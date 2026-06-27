<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { type Recipe } from '../utils/recipeData';
  import { Search, Clock, ChefHat, Check, AlertTriangle, Plus, X, ShoppingBag, Trash2, Link } from '@lucide/svelte';

  // Search and filter state
  let searchQuery = $state('');
  let selectedCategory = $state('All');
  let selectedDifficulty = $state('All');
  let selectedRecipe = $state<Recipe | null>(null);
  let cookedMessage = $state<string | null>(null);

  // Link Import State
  let isImportingLink = $state(false);
  let importUrl = $state('');
  let importLoading = $state(false);
  let importError = $state<string | null>(null);
  let stagedRecipe = $state<Recipe | null>(null);

  // Dietary filter state
  let activeDietary = $state<string[]>([]);

  const categories = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];

  // Add Custom Recipe Form State
  let isAddingCustom = $state(false);
  let customName = $state('');
  let customDesc = $state('');
  let customPrep = $state(10);
  let customCook = $state(15);
  let customDifficulty = $state<'Easy' | 'Medium' | 'Hard'>('Easy');
  let customCategory = $state<'Breakfast' | 'Lunch' | 'Dinner' | 'Snack'>('Dinner');
  let customImage = $state('');
  
  let customIngredients = $state<Array<{ name: string; quantity: number; unit: string; category: string }>>([
    { name: '', quantity: 1, unit: 'pieces', category: 'Vegetables' }
  ]);
  let customInstructions = $state<string[]>(['']);
  let customDietary = $state<string[]>([]);

  const availableCategories = ['Vegetables', 'Fruits', 'Dairy', 'Meats & Proteins', 'Grains', 'Pantry Staples'];
  const availableUnits = ['pieces', 'g', 'ml', 'slices', 'tbsp', 'cups', 'pack', 'bottle', 'bunch'];

  function addIngredientRow() {
    customIngredients.push({ name: '', quantity: 1, unit: 'pieces', category: 'Vegetables' });
  }

  function removeIngredientRow(index: number) {
    customIngredients = customIngredients.filter((_, i) => i !== index);
  }

  function addInstructionRow() {
    customInstructions.push('');
  }

  function removeInstructionRow(index: number) {
    customInstructions = customInstructions.filter((_, i) => i !== index);
  }

  function toggleCustomDietary(tag: string) {
    if (customDietary.includes(tag)) {
      customDietary = customDietary.filter(t => t !== tag);
    } else {
      customDietary.push(tag);
    }
  }

  function resetCustomForm() {
    customName = '';
    customDesc = '';
    customPrep = 10;
    customCook = 15;
    customDifficulty = 'Easy';
    customCategory = 'Dinner';
    customImage = '';
    customIngredients = [{ name: '', quantity: 1, unit: 'pieces', category: 'Vegetables' }];
    customInstructions = [''];
    customDietary = [];
    isAddingCustom = false;
  }

  function handleAddCustomSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!customName.trim()) return;

    const validIngredients = customIngredients.filter(ing => ing.name.trim() !== '');
    const validInstructions = customInstructions.filter(step => step.trim() !== '');

    if (validIngredients.length === 0) {
      alert('Please add at least one valid ingredient');
      return;
    }
    if (validInstructions.length === 0) {
      alert('Please add at least one instruction step');
      return;
    }

    const newRecipe: Recipe = {
      id: 'custom-' + Math.random().toString(36).substring(2, 9),
      name: customName.trim(),
      description: customDesc.trim(),
      prepTime: customPrep,
      cookTime: customCook,
      difficulty: customDifficulty,
      category: customCategory,
      image: customImage.trim() || 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=600&auto=format&fit=crop&q=60',
      ingredients: validIngredients,
      instructions: validInstructions,
      dietaryTags: customDietary,
      isCustom: true
    };

    pantryStore.addCustomRecipe(newRecipe);
    resetCustomForm();
  }

  function toggleDietaryTag(tag: string) {
    if (activeDietary.includes(tag)) {
      activeDietary = activeDietary.filter(t => t !== tag);
    } else {
      activeDietary.push(tag);
    }
  }

  // Check ingredient status in pantry
  function getIngredientStatus(reqIng: { name: string; quantity: number }) {
    const pantryItems = pantryStore.pantryItems.filter(
      p => p.name.toLowerCase() === reqIng.name.toLowerCase()
    );
    
    const totalInStock = pantryItems.reduce((sum, p) => sum + p.quantity, 0);
    
    if (totalInStock >= reqIng.quantity) {
      return { status: 'in-stock', inStockQty: totalInStock, missingQty: 0 };
    } else if (totalInStock > 0) {
      return { status: 'insufficient', inStockQty: totalInStock, missingQty: reqIng.quantity - totalInStock };
    } else {
      return { status: 'missing', inStockQty: 0, missingQty: reqIng.quantity };
    }
  }

  // Get matching stats for a recipe
  function getRecipeMatchStats(recipe: Recipe) {
    let inStockCount = 0;
    let insufficientCount = 0;
    let missingCount = 0;
    
    const details = recipe.ingredients.map(ing => {
      const status = getIngredientStatus(ing);
      if (status.status === 'in-stock') inStockCount++;
      else if (status.status === 'insufficient') insufficientCount++;
      else missingCount++;
      
      return {
        ...ing,
        ...status
      };
    });

    const totalIng = recipe.ingredients.length;
    const matchPercentage = Math.round((inStockCount / totalIng) * 100);
    const missingTotal = insufficientCount + missingCount;

    return {
      details,
      inStockCount,
      missingTotal,
      matchPercentage,
      canCook: missingTotal === 0
    };
  }

  // Derived recipes list with calculated match stats
  let recipesWithStats = $derived.by(() => {
    return pantryStore.recipes.map(recipe => {
      const stats = getRecipeMatchStats(recipe);
      return {
        ...recipe,
        stats
      };
    });
  });

  // Filtered and sorted recipes
  let filteredRecipes = $derived.by(() => {
    let list = recipesWithStats;

    if (selectedCategory !== 'All') {
      list = list.filter(r => r.category === selectedCategory);
    }

    if (selectedDifficulty !== 'All') {
      list = list.filter(r => r.difficulty === selectedDifficulty);
    }

    // Filter by active dietary tags
    if (activeDietary.length > 0) {
      list = list.filter(r => 
        activeDietary.every(tag => r.dietaryTags && r.dietaryTags.includes(tag))
      );
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      list = list.filter(r => r.name.toLowerCase().includes(query) || r.description.toLowerCase().includes(query));
    }

    // Sort by match percentage (highest first), then by name
    return [...list].sort((a, b) => {
      if (b.stats.matchPercentage !== a.stats.matchPercentage) {
        return b.stats.matchPercentage - a.stats.matchPercentage;
      }
      return a.name.localeCompare(b.name);
    });
  });

  // Cook recipe action
  function handleCook(recipeId: string, recipeName: string) {
    pantryStore.cookRecipe(recipeId);
    cookedMessage = `Successfully cooked ${recipeName}! Ingredients deducted from pantry.`;
    if (selectedRecipe && selectedRecipe.id === recipeId) {
      selectedRecipe = pantryStore.recipes.find(r => r.id === recipeId) || null;
    }
    setTimeout(() => {
      cookedMessage = null;
    }, 4000);
  }

  // Add missing items to shopping list
  function handleAddMissingToShopping(recipe: Recipe) {
    const stats = getRecipeMatchStats(recipe);
    let addedCount = 0;
    
    stats.details.forEach(ing => {
      if (ing.missingQty > 0) {
        pantryStore.addShoppingItem(ing.name, ing.missingQty, ing.unit, ing.category, recipe.name);
        addedCount++;
      }
    });

    if (addedCount > 0) {
      cookedMessage = `Added ${addedCount} missing ingredient(s) to your Shopping List!`;
      setTimeout(() => {
        cookedMessage = null;
      }, 4000);
    }
  }

  let recipeToDelete = $state<{ id: string; name: string; closeDetails: boolean } | null>(null);

  function requestDeleteRecipe(id: string, name: string, closeDetails: boolean = false) {
    recipeToDelete = { id, name, closeDetails };
  }

  function confirmDeleteRecipe() {
    if (recipeToDelete) {
      pantryStore.deleteCustomRecipe(recipeToDelete.id);
      if (recipeToDelete.closeDetails) {
        selectedRecipe = null;
      }
      recipeToDelete = null;
    }
  }

  function getMatchClass(percentage: number) {
    if (percentage === 100) return 'match-perfect';
    if (percentage >= 50) return 'match-partial';
    return 'match-poor';
  }

  // Check how many items are missing/insufficient
  function getMatchLabel(stats: any) {
    if (stats.canCook) return 'Ready to Cook';
    if (stats.missingTotal <= 2) return `Missing ${stats.missingTotal} Item${stats.missingTotal > 1 ? 's' : ''}`;
    return 'Missing 3+ Items';
  }

  async function handleImportSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!importUrl.trim()) return;

    importLoading = true;
    importError = null;

    try {
      const imported = await pantryStore.importRecipeFromLink(importUrl.trim());
      stagedRecipe = imported;
    } catch (err: any) {
      importError = err.message || 'Failed to parse recipe from URL.';
    } finally {
      importLoading = false;
    }
  }

  function addStagedIngredientRow() {
    if (stagedRecipe) {
      stagedRecipe.ingredients = [
        ...stagedRecipe.ingredients,
        { name: '', quantity: 1, unit: 'pieces', category: 'Vegetables' }
      ];
    }
  }

  function removeStagedIngredientRow(index: number) {
    if (stagedRecipe) {
      stagedRecipe.ingredients = stagedRecipe.ingredients.filter((_, i) => i !== index);
    }
  }

  function addStagedInstructionRow() {
    if (stagedRecipe) {
      stagedRecipe.instructions = [
        ...stagedRecipe.instructions,
        ''
      ];
    }
  }

  function removeStagedInstructionRow(index: number) {
    if (stagedRecipe) {
      stagedRecipe.instructions = stagedRecipe.instructions.filter((_, i) => i !== index);
    }
  }

  function handleSaveStagedRecipe(e: SubmitEvent) {
    e.preventDefault();
    if (!stagedRecipe) return;

    const validIngredients = stagedRecipe.ingredients.filter(ing => ing.name.trim() !== '');
    const validInstructions = stagedRecipe.instructions.filter(step => step.trim() !== '');

    if (validIngredients.length === 0) {
      alert('Please add at least one valid ingredient');
      return;
    }
    if (validInstructions.length === 0) {
      alert('Please add at least one instruction step');
      return;
    }

    const finalizedRecipe: Recipe = {
      ...stagedRecipe,
      name: stagedRecipe.name.trim(),
      description: stagedRecipe.description.trim(),
      ingredients: validIngredients,
      instructions: validInstructions
    };

    pantryStore.addCustomRecipe(finalizedRecipe);
    cookedMessage = `Successfully saved "${finalizedRecipe.name}" to Cookbook!`;
    
    // Reset staged import state
    stagedRecipe = null;
    importUrl = '';
    isImportingLink = false;
    
    setTimeout(() => {
      cookedMessage = null;
    }, 4000);
  }

  function handleCancelStaged() {
    stagedRecipe = null;
  }

  function handleFormSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!stagedRecipe) {
      handleImportSubmit(e);
    } else {
      handleSaveStagedRecipe(e);
    }
  }
</script>

<div class="recipe-container">
  <!-- Toast message / alert notification -->
  {#if cookedMessage}
    <div class="alert-toast glass">
      <div class="toast-content">
        <Check size={18} class="toast-icon text-emerald" />
        <span>{cookedMessage}</span>
      </div>
    </div>
  {/if}

  <div class="recipe-header">
    <div class="header-titles">
      <h2>Gourmet Recipe Book</h2>
      <p class="subtitle">Match your scanned pantry items automatically with chef-curated recipes.</p>
    </div>
    <div class="header-actions">
      <button class="btn btn-cyan" onclick={() => { isImportingLink = true; importError = null; }}>
        <Link size={16} />
        <span>Import from Link</span>
      </button>
      <button class="btn btn-emerald" onclick={() => isAddingCustom = true}>
        <Plus size={16} />
        <span>Add Custom Recipe</span>
      </button>
    </div>
  </div>

  <!-- Search and Filters Section -->
  <div class="filters-panel card glass">
    <div class="search-box">
      <Search size={18} class="search-icon" />
      <input 
        type="text" 
        placeholder="Search recipe name or ingredients..." 
        bind:value={searchQuery}
        class="search-input"
      />
    </div>

    <div class="filter-controls">
      <!-- Category Filter -->
      <div class="filter-group">
        <span class="filter-label">Meal Type</span>
        <div class="pills-container">
          {#each categories as category}
            <button 
              class="pill-btn {selectedCategory === category ? 'active' : ''}"
              onclick={() => selectedCategory = category}
            >
              {category}
            </button>
          {/each}
        </div>
      </div>

      <!-- Difficulty Filter -->
      <div class="filter-group">
        <span class="filter-label">Difficulty</span>
        <div class="pills-container">
          {#each difficulties as difficulty}
            <button 
              class="pill-btn {selectedDifficulty === difficulty ? 'active' : ''}"
              onclick={() => selectedDifficulty = difficulty}
            >
              {difficulty}
            </button>
          {/each}
        </div>
      </div>

      <!-- Dietary Filters -->
      <div class="filter-group">
        <span class="filter-label">Dietary Filters</span>
        <div class="pills-container">
          {#each ['Vegetarian', 'Gluten-Free', 'Dairy-Free'] as tag}
            <button 
              class="pill-btn {activeDietary.includes(tag) ? 'active-dietary' : ''}"
              onclick={() => toggleDietaryTag(tag)}
            >
              {tag}
            </button>
          {/each}
        </div>
      </div>
    </div>
  </div>

  <!-- Recipes Grid -->
  {#if filteredRecipes.length > 0}
    <div class="recipes-grid">
      {#each filteredRecipes as recipe (recipe.id)}
        <div class="recipe-card glass" onclick={() => selectedRecipe = recipe} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && (selectedRecipe = recipe)}>
          <!-- Image header -->
          <div class="card-image-wrapper">
            <img src={recipe.image} alt={recipe.name} class="recipe-img" loading="lazy" />
            <div class="card-badges">
              <span class="badge badge-difficulty {recipe.difficulty.toLowerCase()}">{recipe.difficulty}</span>
              <span class="badge badge-time">
                <Clock size={12} />
                <span>{recipe.prepTime + recipe.cookTime} mins</span>
              </span>
              {#if recipe.isCustom}
                <button 
                  class="badge badge-delete" 
                  onclick={(e) => { e.stopPropagation(); requestDeleteRecipe(recipe.id, recipe.name); }}
                  title="Delete recipe"
                  aria-label="Delete recipe"
                >
                  <Trash2 size={12} style="color: #ef4444;" />
                </button>
              {/if}
            </div>
            
            <!-- Match Glow Overlay -->
            <div class="match-badge {getMatchClass(recipe.stats.matchPercentage)}">
              <span>{recipe.stats.matchPercentage}% Match</span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="card-body">
            <span class="recipe-cat">{recipe.category}</span>
            <h3 class="recipe-title">{recipe.name}</h3>
            <p class="recipe-desc">{recipe.description}</p>
            
            <!-- Matching inventory breakdown -->
            <div class="inventory-status-bar">
              <div class="progress-track">
                <div class="progress-fill {getMatchClass(recipe.stats.matchPercentage)}" style="width: {recipe.stats.matchPercentage}%"></div>
              </div>
              <div class="status-labels">
                <span class="status-msg {recipe.stats.canCook ? 'text-emerald' : 'text-orange'}">
                  {#if recipe.stats.canCook}
                    <Check size={12} />
                  {:else}
                    <AlertTriangle size={12} />
                  {/if}
                  {getMatchLabel(recipe.stats)}
                </span>
                <span class="ing-count">{recipe.stats.inStockCount} / {recipe.ingredients.length} in stock</span>
              </div>
            </div>
          </div>

          <!-- Card Actions -->
          <div class="card-footer" onclick={(e) => e.stopPropagation()} role="presentation">
            {#if recipe.stats.canCook}
              <button class="btn btn-emerald btn-full" onclick={() => handleCook(recipe.id, recipe.name)}>
                <ChefHat size={16} />
                <span>Cook Recipe</span>
              </button>
            {:else}
              <button class="btn btn-orange btn-full" onclick={() => handleAddMissingToShopping(recipe)}>
                <Plus size={16} />
                <span>Add Missing to List</span>
              </button>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="empty-state card glass">
      <ChefHat size={48} class="text-muted" />
      <h3>No Recipes Found</h3>
      <p>Try adjusting your search filters or scan more items to match with our premium recipes.</p>
    </div>
  {/if}

  <!-- Recipe Details Modal -->
  {#if selectedRecipe}
    {@const stats = getRecipeMatchStats(selectedRecipe)}
    <div class="modal-overlay" onclick={() => selectedRecipe = null} role="presentation">
      <div class="modal-content glass" onclick={(e) => e.stopPropagation()} role="presentation">
        <button class="close-btn" onclick={() => selectedRecipe = null} aria-label="Close details">
          <X size={20} />
        </button>

        <!-- Modal Hero Image -->
        <div class="modal-hero">
          <img src={selectedRecipe.image} alt={selectedRecipe.name} class="modal-hero-img" />
          <div class="modal-hero-overlay">
            <span class="modal-cat">{selectedRecipe.category}</span>
            <h2>{selectedRecipe.name}</h2>
          </div>
        </div>

        <div class="modal-body-scroll">
          <div class="modal-meta-row">
            <div class="meta-item">
              <span class="meta-label">Prep Time</span>
              <span class="meta-val">{selectedRecipe.prepTime} mins</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Cook Time</span>
              <span class="meta-val">{selectedRecipe.cookTime} mins</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Difficulty</span>
              <span class="meta-val badge badge-difficulty {selectedRecipe.difficulty.toLowerCase()}">{selectedRecipe.difficulty}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Match Rating</span>
              <span class="meta-val text-emerald font-bold">{stats.matchPercentage}% Match</span>
            </div>
          </div>

          <p class="modal-desc">{selectedRecipe.description}</p>

          <div class="modal-grid">
            <!-- Left Side: Ingredient Check List -->
            <div class="modal-section">
              <h3>Ingredients Checklist</h3>
              <p class="section-sub">Drawn from scanner analysis and current inventory.</p>
              
              <div class="ingredient-list">
                {#each stats.details as ing}
                  <div class="ingredient-row {ing.status}">
                    <div class="ing-left">
                      <div class="checkbox-mock">
                        {#if ing.status === 'in-stock'}
                          <Check size={12} class="text-white" />
                        {:else if ing.status === 'insufficient'}
                          <AlertTriangle size={12} class="text-orange" />
                        {:else}
                          <X size={12} class="text-red" />
                        {/if}
                      </div>
                      <span class="ing-name">{ing.name}</span>
                    </div>

                    <div class="ing-right">
                      <span class="ing-req">{ing.quantity} {ing.unit} required</span>
                      
                      {#if ing.status === 'in-stock'}
                        <span class="ing-stock-info text-emerald">({ing.inStockQty} in stock)</span>
                      {:else if ing.status === 'insufficient'}
                        <span class="ing-stock-info text-orange">({ing.inStockQty} in stock, need {ing.missingQty} more)</span>
                      {:else}
                        <span class="ing-stock-info text-red">(Missing)</span>
                      {/if}
                    </div>
                  </div>
                {/each}
              </div>

              <!-- Quick action to fill list -->
              {#if !stats.canCook}
                <button class="btn btn-outline-orange mt-4 w-full" onclick={() => handleAddMissingToShopping(selectedRecipe!)}>
                  <Plus size={16} />
                  <span>Add {stats.missingTotal} Missing Ingredient(s) to Shopping List</span>
                </button>
              {/if}
            </div>

            <!-- Right Side: Step-by-Step Instructions -->
            <div class="modal-section">
              <h3>Cooking Instructions</h3>
              <p class="section-sub">Follow these detailed steps to prepare the meal.</p>
              
              <ol class="instructions-list">
                {#each selectedRecipe.instructions as step, idx}
                  <li>
                    <span class="step-num">{idx + 1}</span>
                    <p class="step-text">{step}</p>
                  </li>
                {/each}
              </ol>
            </div>
          </div>
        </div>

        <!-- Modal Action Footer -->
        <div class="modal-footer">
          {#if selectedRecipe.isCustom}
            <button class="btn btn-danger" onclick={() => requestDeleteRecipe(selectedRecipe!.id, selectedRecipe!.name, true)}>
              <Trash2 size={16} />
              <span>Delete Recipe</span>
            </button>
          {/if}
          {#if stats.canCook}
            <button class="btn btn-emerald" onclick={() => handleCook(selectedRecipe!.id, selectedRecipe!.name)}>
              <ChefHat size={18} />
              <span>I'm Cooking This! Deduct Ingredients</span>
            </button>
          {:else}
            <div class="disabled-notice">
              <AlertTriangle size={16} />
              <span>You are missing ingredients to cook this recipe. Complete them using the Shopping List first.</span>
            </div>
          {/if}
          <button class="btn btn-secondary" onclick={() => selectedRecipe = null}>Close</button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Add Custom Recipe Modal -->
  {#if isAddingCustom}
    <div class="modal-overlay" onclick={resetCustomForm} role="presentation">
      <div class="modal-content glass custom-recipe-modal" onclick={(e) => e.stopPropagation()} role="presentation">
        <button class="close-btn" onclick={resetCustomForm} aria-label="Close form">
          <X size={20} />
        </button>

        <div class="modal-header-simple">
          <h2>Create Custom Recipe</h2>
          <p class="section-sub">Add your own culinary creations to your personal cookbook.</p>
        </div>

        <form onsubmit={handleAddCustomSubmit} class="modal-body-scroll">
          <div class="form-grid-three">
            <div class="form-group flex-2">
              <label for="recipe-name">Recipe Name</label>
              <input 
                type="text" 
                id="recipe-name" 
                placeholder="e.g., Mom's Lasagna" 
                bind:value={customName}
                required
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label for="recipe-img">Image URL (Optional)</label>
              <input 
                type="url" 
                id="recipe-img" 
                placeholder="https://images.unsplash.com/..." 
                bind:value={customImage}
                class="form-input"
              />
            </div>
          </div>

          <div class="form-group mt-3">
            <label for="recipe-desc">Short Description</label>
            <textarea 
              id="recipe-desc" 
              placeholder="Briefly describe your gourmet recipe..." 
              bind:value={customDesc}
              required
              rows="2"
              class="form-textarea"
            ></textarea>
          </div>

          <div class="form-grid-four mt-3">
            <div class="form-group">
              <label for="recipe-category">Meal Type</label>
              <select id="recipe-category" bind:value={customCategory} class="form-select">
                <option value="Breakfast">Breakfast</option>
                <option value="Lunch">Lunch</option>
                <option value="Dinner">Dinner</option>
                <option value="Snack">Snack</option>
              </select>
            </div>

            <div class="form-group">
              <label for="recipe-difficulty">Difficulty</label>
              <select id="recipe-difficulty" bind:value={customDifficulty} class="form-select">
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>

            <div class="form-group">
              <label for="recipe-prep">Prep Time (mins)</label>
              <input 
                type="number" 
                id="recipe-prep" 
                min="0" 
                bind:value={customPrep}
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="recipe-cook">Cook Time (mins)</label>
              <input 
                type="number" 
                id="recipe-cook" 
                min="0" 
                bind:value={customCook}
                required
                class="form-input"
              />
            </div>
          </div>

          <!-- Dietary tags selectors -->
          <div class="form-group mt-4">
            <span class="filter-label">Dietary Tags</span>
            <div class="pills-container mt-1">
              {#each ['Vegetarian', 'Gluten-Free', 'Dairy-Free'] as tag}
                <button 
                  type="button"
                  class="pill-btn {customDietary.includes(tag) ? 'active-dietary' : ''}"
                  onclick={() => toggleCustomDietary(tag)}
                >
                  {tag}
                </button>
              {/each}
            </div>
          </div>

          <!-- Dynamic Ingredients List -->
          <div class="ingredients-form-section mt-4">
            <div class="section-title-row">
              <h3>Required Ingredients</h3>
              <button type="button" class="btn btn-outline-cyan btn-sm" onclick={addIngredientRow}>
                <Plus size={14} />
                <span>Add Ingredient</span>
              </button>
            </div>
            
            <div class="dynamic-rows-container mt-2">
              {#each customIngredients as ing, idx}
                <div class="dynamic-row">
                  <input 
                    type="text" 
                    placeholder="Ingredient name (e.g. Pasta)" 
                    bind:value={ing.name}
                    required
                    class="form-input flex-2"
                  />
                  <input 
                    type="number" 
                    placeholder="Qty" 
                    min="0.1" 
                    step="any" 
                    bind:value={ing.quantity}
                    required
                    class="form-input flex-05"
                  />
                  <select bind:value={ing.unit} class="form-select flex-1">
                    {#each availableUnits as unit}
                      <option value={unit}>{unit}</option>
                    {/each}
                  </select>
                  <select bind:value={ing.category} class="form-select flex-1">
                    {#each availableCategories as cat}
                      <option value={cat}>{cat}</option>
                    {/each}
                  </select>
                  {#if customIngredients.length > 1}
                    <button type="button" class="btn-delete-row" onclick={() => removeIngredientRow(idx)} aria-label="Remove ingredient">
                      <X size={16} />
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Dynamic Cooking Steps -->
          <div class="instructions-form-section mt-4">
            <div class="section-title-row">
              <h3>Step-by-Step Instructions</h3>
              <button type="button" class="btn btn-outline-cyan btn-sm" onclick={addInstructionRow}>
                <Plus size={14} />
                <span>Add Step</span>
              </button>
            </div>

            <div class="dynamic-rows-container mt-2">
              {#each customInstructions as step, idx}
                <div class="dynamic-row">
                  <span class="step-label">Step {idx + 1}</span>
                  <input 
                    type="text" 
                    placeholder="e.g. Boil water and add salt." 
                    bind:value={customInstructions[idx]}
                    required
                    class="form-input flex-2"
                  />
                  {#if customInstructions.length > 1}
                    <button type="button" class="btn-delete-row" onclick={() => removeInstructionRow(idx)} aria-label="Remove step">
                      <X size={16} />
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Modal Footer Actions -->
          <div class="modal-footer mt-4">
            <button type="submit" class="btn btn-emerald">Save Recipe</button>
            <button type="button" class="btn btn-secondary" onclick={resetCustomForm}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  {/if}

  <!-- Import Recipe Link Modal -->
  {#if isImportingLink}
    <div class="modal-overlay" onclick={() => { if (!importLoading && !stagedRecipe) isImportingLink = false; }} role="presentation">
      <form onsubmit={handleFormSubmit} class="modal-content glass {stagedRecipe ? 'custom-recipe-modal' : 'import-link-modal'}" onclick={(e) => e.stopPropagation()} role="presentation">
        <button type="button" class="close-btn" onclick={() => { stagedRecipe = null; isImportingLink = false; }} disabled={importLoading} aria-label="Close form">
          <X size={20} />
        </button>

        {#if !stagedRecipe}
          <div class="modal-header-simple">
            <h2>Import Recipe from Link</h2>
            <p class="section-sub">Paste a recipe URL from any culinary site to automatically extract ingredients and steps.</p>
          </div>

          <div class="modal-body-form">
            <div class="form-group">
              <label for="import-url">Recipe Link / URL</label>
              <input 
                type="url" 
                id="import-url" 
                placeholder="e.g. https://www.allrecipes.com/recipe/..." 
                bind:value={importUrl}
                required
                disabled={importLoading}
                class="form-input"
              />
            </div>

            {#if importError}
              <div class="error-banner">
                <AlertTriangle size={16} />
                <span>{importError}</span>
              </div>
            {/if}
          </div>

          <!-- Modal Footer Actions -->
          <div class="modal-footer">
            <button type="submit" class="btn btn-cyan" disabled={importLoading}>
              {#if importLoading}
                <span>Importing...</span>
              {:else}
                <span>Import Recipe</span>
              {/if}
            </button>
            <button type="button" class="btn btn-secondary" onclick={() => isImportingLink = false} disabled={importLoading}>Cancel</button>
          </div>
        {:else}
          <div class="modal-header-simple">
            <h2>Verify & Normalize Recipe</h2>
            <p class="section-sub">Adjust parsed ingredients and steps. Original author comments are shown as reference guides.</p>
          </div>

          <div class="modal-body-scroll">
            <!-- Basic Details -->
            <div class="form-grid-three">
              <div class="form-group flex-2">
                <label for="staged-name">Recipe Name</label>
                <input 
                  type="text" 
                  id="staged-name" 
                  bind:value={stagedRecipe.name}
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="staged-img">Image URL</label>
                <input 
                  type="text" 
                  id="staged-img" 
                  bind:value={stagedRecipe.image}
                  class="form-input"
                />
              </div>
            </div>

            <div class="form-grid-four mt-3">
              <div class="form-group">
                <label for="staged-prep">Prep Time (mins)</label>
                <input 
                  type="number" 
                  id="staged-prep" 
                  min="0" 
                  bind:value={stagedRecipe.prepTime}
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="staged-cook">Cook Time (mins)</label>
                <input 
                  type="number" 
                  id="staged-cook" 
                  min="0" 
                  bind:value={stagedRecipe.cookTime}
                  required
                  class="form-input"
                />
              </div>
              <div class="form-group">
                <label for="staged-difficulty">Difficulty</label>
                <select id="staged-difficulty" bind:value={stagedRecipe.difficulty} class="form-select">
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
              <div class="form-group">
                <label for="staged-category">Category</label>
                <select id="staged-category" bind:value={stagedRecipe.category} class="form-select">
                  <option value="Breakfast">Breakfast</option>
                  <option value="Lunch">Lunch</option>
                  <option value="Dinner">Dinner</option>
                  <option value="Snack">Snack</option>
                </select>
              </div>
            </div>

            <div class="form-group mt-3">
              <label for="staged-desc">Description</label>
              <textarea 
                id="staged-desc" 
                rows="2"
                bind:value={stagedRecipe.description}
                class="form-textarea"
              ></textarea>
            </div>

            <!-- Ingredients Section -->
            <div class="ingredients-form-section mt-4">
              <div class="section-title-row">
                <h3>Staged Ingredients</h3>
                <button type="button" class="btn btn-outline-cyan btn-sm" onclick={addStagedIngredientRow}>
                  <Plus size={14} />
                  <span>Add Ingredient</span>
                </button>
              </div>

              <div class="dynamic-rows-container mt-2">
                {#each stagedRecipe.ingredients as ing, idx}
                  <div class="staged-row-wrapper mt-2">
                    <div class="dynamic-row">
                      <input 
                        type="text" 
                        placeholder="Ingredient name (e.g. Mushrooms)" 
                        bind:value={ing.name}
                        required
                        class="form-input flex-2"
                      />
                      <input 
                        type="number" 
                        placeholder="Qty" 
                        min="0.01" 
                        step="any" 
                        bind:value={ing.quantity}
                        required
                        class="form-input flex-05"
                      />
                      <select bind:value={ing.unit} class="form-select flex-1">
                        {#each availableUnits as unit}
                          <option value={unit}>{unit}</option>
                        {/each}
                      </select>
                      <select bind:value={ing.category} class="form-select flex-1">
                        {#each availableCategories as cat}
                          <option value={cat}>{cat}</option>
                        {/each}
                      </select>
                      {#if stagedRecipe.ingredients.length > 1}
                        <button type="button" class="btn-delete-row" onclick={() => removeStagedIngredientRow(idx)} aria-label="Remove ingredient">
                          <X size={16} />
                        </button>
                      {/if}
                    </div>
                    {#if ing.originalText}
                      <div class="original-text-helper">
                        <span class="helper-label">Original:</span>
                        <span class="helper-content">"{ing.originalText}"</span>
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>

            <!-- Instructions Section -->
            <div class="instructions-form-section mt-4">
              <div class="section-title-row">
                <h3>Cooking Instructions</h3>
                <button type="button" class="btn btn-outline-cyan btn-sm" onclick={addStagedInstructionRow}>
                  <Plus size={14} />
                  <span>Add Step</span>
                </button>
              </div>

              <div class="dynamic-rows-container mt-2">
                {#each stagedRecipe.instructions as step, idx}
                  <div class="dynamic-row">
                    <span class="step-label">Step {idx + 1}</span>
                    <input 
                      type="text" 
                      placeholder="e.g. Boil water and add salt." 
                      bind:value={stagedRecipe.instructions[idx]}
                      required
                      class="form-input flex-2"
                    />
                    {#if stagedRecipe.instructions.length > 1}
                      <button type="button" class="btn-delete-row" onclick={() => removeStagedInstructionRow(idx)} aria-label="Remove step">
                        <X size={16} />
                      </button>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          </div>

          <!-- Modal Footer Actions -->
          <div class="modal-footer">
            <button type="submit" class="btn btn-cyan">Save to Cookbook</button>
            <button type="button" class="btn btn-secondary" onclick={handleCancelStaged}>Back</button>
          </div>
        {/if}
      </form>
    </div>
  {/if}
</div>

{#if recipeToDelete}
  <div class="modal-overlay" onclick={() => recipeToDelete = null} role="presentation">
    <div class="modal-content glass confirm-modal" onclick={(e) => e.stopPropagation()} role="presentation">
      <div class="modal-body-form text-center p-6">
        <div class="danger-icon-container">
          <AlertTriangle size={36} />
        </div>
        <h3 class="confirm-title mt-3">Delete Recipe</h3>
        <p class="confirm-message mt-2">Are you sure you want to delete the recipe <strong>{recipeToDelete.name}</strong>? This action will permanently remove it from your Cookbook.</p>
        
        <div class="confirm-actions mt-4">
          <button class="btn btn-danger mr-2" onclick={confirmDeleteRecipe}>Delete Recipe</button>
          <button class="btn btn-secondary" onclick={() => recipeToDelete = null}>Cancel</button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .recipe-container {
    max-width: 1100px;
    margin: 0 auto;
    position: relative;
  }

  .recipe-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .header-titles h2 {
    font-size: 1.75rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
  }

  .subtitle {
    font-size: 0.9rem;
    color: var(--color-text-muted);
  }

  /* Filters Panel */
  .filters-panel {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    margin-bottom: 2rem;
  }

  .search-box {
    position: relative;
    width: 100%;
  }

  .search-icon {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
  }

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border-radius: 10px;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.95rem;
    transition: all 0.25s;
  }

  .search-input:focus {
    outline: none;
    border-color: var(--color-cyan);
    box-shadow: 0 0 12px rgba(6, 182, 212, 0.15);
  }

  .filter-controls {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 768px) {
    .filter-controls {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .filter-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-text-muted);
    letter-spacing: 0.05em;
  }

  .pills-container {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    scrollbar-width: none;
  }

  .pills-container::-webkit-scrollbar {
    display: none;
  }

  .pill-btn {
    white-space: nowrap;
    padding: 0.4rem 0.85rem;
    border-radius: 9999px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--color-text-muted);
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .pill-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
  }

  .pill-btn.active {
    background: var(--color-cyan);
    border-color: var(--color-cyan);
    color: #fff;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
  }

  .pill-btn.active-dietary {
    background: var(--color-emerald);
    border-color: var(--color-emerald);
    color: #fff;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
  }

  /* Recipes Grid */
  .recipes-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  @media (min-width: 640px) {
    .recipes-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (min-width: 1024px) {
    .recipes-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  /* Recipe Card */
  .recipe-card {
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .recipe-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
  }

  .card-image-wrapper {
    position: relative;
    height: 180px;
    width: 100%;
    background: rgba(0, 0, 0, 0.2);
    overflow: hidden;
  }

  .recipe-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }

  .recipe-card:hover .recipe-img {
    transform: scale(1.05);
  }

  .card-badges {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    display: flex;
    gap: 0.5rem;
    z-index: 2;
  }

  .badge {
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
  }

  .badge-difficulty.easy {
    background: rgba(16, 185, 129, 0.75);
    color: #fff;
  }

  .badge-difficulty.medium {
    background: rgba(249, 115, 22, 0.75);
    color: #fff;
  }

  .badge-difficulty.hard {
    background: rgba(239, 68, 68, 0.75);
    color: #fff;
  }

  .badge-time {
    background: rgba(15, 23, 42, 0.75);
    color: #f1f5f9;
  }

  .match-badge {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 800;
    backdrop-filter: blur(8px);
    z-index: 2;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }

  .match-perfect {
    background: rgba(16, 185, 129, 0.2);
    color: var(--color-emerald);
    border-color: rgba(16, 185, 129, 0.3);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
  }

  .match-partial {
    background: rgba(6, 182, 212, 0.2);
    color: var(--color-cyan);
    border-color: rgba(6, 182, 212, 0.3);
  }

  .match-poor {
    background: rgba(249, 115, 22, 0.2);
    color: var(--color-orange);
    border-color: rgba(249, 115, 22, 0.3);
  }

  /* Card Body */
  .card-body {
    padding: 1.25rem;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
  }

  .recipe-cat {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-cyan);
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
  }

  .recipe-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-bottom: 0.5rem;
    line-height: 1.3;
  }

  .recipe-desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    line-height: 1.4;
    margin-bottom: 1.25rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .inventory-status-bar {
    margin-top: auto;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .progress-track {
    height: 4px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 999px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.3s ease;
  }

  .progress-fill.match-perfect { background: var(--color-emerald); }
  .progress-fill.match-partial { background: var(--color-cyan); }
  .progress-fill.match-poor { background: var(--color-orange); }

  .status-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
  }

  .status-msg {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-weight: 600;
  }

  .ing-count {
    color: var(--color-text-muted);
  }

  .card-footer {
    padding: 0 1.25rem 1.25rem 1.25rem;
  }

  .btn-full {
    width: 100%;
    justify-content: center;
  }

  /* Empty / error state */
  .empty-state {
    text-align: center;
    padding: 4rem 1.5rem;
    color: var(--color-text-muted);
  }

  .empty-state h3 {
    font-size: 1.15rem;
    color: var(--color-text-light);
    margin-top: 0.75rem;
    margin-bottom: 0.25rem;
  }

  .empty-state p {
    font-size: 0.85rem;
    max-width: 400px;
    margin: 0 auto;
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(6px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
    animation: fadeIn 0.25s ease-out;
  }

  .modal-content {
    width: 100%;
    max-width: 900px;
    max-height: 90vh;
    background: rgba(25, 30, 45, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
    animation: modalScale 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    z-index: 10;
  }

  .close-btn:hover {
    background: rgba(0, 0, 0, 0.6);
    color: var(--color-cyan);
    transform: scale(1.05);
  }

  .modal-hero {
    position: relative;
    height: 200px;
    width: 100%;
  }

  .modal-hero-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .modal-hero-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(15, 23, 42, 0.95) 20%, rgba(15, 23, 42, 0.2));
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 1.5rem;
  }

  .modal-cat {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-cyan);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.25rem;
  }

  .modal-hero-overlay h2 {
    font-size: 1.75rem;
    font-weight: 800;
    color: var(--color-text-light);
    line-height: 1.2;
  }

  .modal-body-scroll {
    padding: 1.5rem;
    overflow-y: auto;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .modal-meta-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 1rem;
  }

  @media (min-width: 640px) {
    .modal-meta-row {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .modal-meta-row .meta-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.25rem;
  }

  .meta-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    font-weight: 600;
    text-transform: uppercase;
  }

  .meta-val {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text-light);
  }

  .modal-desc {
    font-size: 0.95rem;
    color: var(--color-text-muted);
    line-height: 1.5;
  }

  .modal-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  @media (min-width: 768px) {
    .modal-grid {
      grid-template-columns: 1.1fr 1fr;
    }
  }

  .modal-section h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-bottom: 0.15rem;
  }

  .section-sub {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin-bottom: 1rem;
  }

  /* Ingredient checklist in modal */
  .ingredient-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .ingredient-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  .ing-left {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .checkbox-mock {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }

  .ingredient-row.in-stock .checkbox-mock {
    background: var(--color-emerald);
    border-color: var(--color-emerald);
  }

  .ingredient-row.insufficient .checkbox-mock {
    background: rgba(249, 115, 22, 0.1);
    border-color: var(--color-orange);
  }

  .ingredient-row.missing .checkbox-mock {
    background: rgba(239, 68, 68, 0.1);
    border-color: #ef4444;
  }

  .ing-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-light);
  }

  .ing-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    font-size: 0.75rem;
  }

  .ing-req {
    color: var(--color-text-light);
    font-weight: 500;
  }

  .ing-stock-info {
    font-size: 0.65rem;
    font-weight: 600;
  }

  /* Instructions list */
  .instructions-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .instructions-list li {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
  }

  .step-num {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: var(--color-cyan);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
    box-shadow: 0 0 8px rgba(6, 182, 212, 0.3);
  }

  .step-text {
    font-size: 0.85rem;
    line-height: 1.45;
    color: var(--color-text-muted);
    margin: 0;
  }

  /* Modal Action Footer */
  .modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.75rem;
    padding: 1.25rem 1.5rem;
    background: rgba(15, 23, 42, 0.95);
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }

  .disabled-notice {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    color: var(--color-orange);
    margin-right: auto;
    max-width: 500px;
    text-align: left;
  }

  /* Toast Notification */
  .alert-toast {
    position: fixed;
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2000;
    border-radius: 10px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 0.75rem 1.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    animation: slideUpFade 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .toast-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-text-light);
    font-size: 0.9rem;
    font-weight: 600;
  }

  .toast-icon {
    flex-shrink: 0;
  }

  /* Animations */
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes modalScale {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
  }

  /* Delete Badge on Card */
  .badge-delete {
    background: rgba(239, 68, 68, 0.25);
    border-color: rgba(239, 68, 68, 0.35);
    cursor: pointer;
    transition: all 0.2s;
  }

  .badge-delete:hover {
    background: rgba(239, 68, 68, 0.45);
    border-color: rgba(239, 68, 68, 0.65);
    transform: scale(1.05);
  }

  /* Custom Recipe Modal Styling */
  .custom-recipe-modal {
    max-width: 750px !important;
  }

  .modal-header-simple {
    padding: 1.5rem 1.5rem 0.5rem 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .modal-header-simple h2 {
    font-size: 1.35rem;
    font-weight: 800;
    margin: 0;
    color: var(--color-cyan);
  }

  .form-grid-three {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 640px) {
    .form-grid-three {
      grid-template-columns: 2fr 1fr;
    }
  }

  .form-grid-four {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  @media (min-width: 640px) {
    .form-grid-four {
      grid-template-columns: repeat(4, 1fr);
    }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    text-align: left;
  }

  .form-group label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-text-muted);
    letter-spacing: 0.05em;
  }

  .form-input, .form-select, .form-textarea {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.85rem;
    transition: all 0.2s;
  }

  .form-input:focus, .form-select:focus, .form-textarea:focus {
    outline: none;
    border-color: var(--color-cyan);
  }

  .form-textarea {
    resize: vertical;
  }

  /* Dynamic Sub-forms */
  .ingredients-form-section, .instructions-form-section {
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 1.25rem;
    text-align: left;
  }

  .section-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .section-title-row h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0;
  }

  .dynamic-rows-container {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .dynamic-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .step-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-cyan);
    min-width: 55px;
    flex-shrink: 0;
  }

  .btn-delete-row {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.2);
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 6px;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .btn-delete-row:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  .btn-outline-cyan {
    background: transparent;
    border: 1px solid rgba(6, 182, 212, 0.25);
    color: var(--color-cyan);
  }

  .btn-outline-cyan:hover {
    background: rgba(6, 182, 212, 0.08);
    border-color: rgba(6, 182, 212, 0.5);
  }

  /* Utility sizing classes */
  .flex-2 { flex: 2; }
  .flex-1 { flex: 1; }
  .flex-05 { flex: 0.5; }
  .mt-1 { margin-top: 0.25rem; }
  .mt-2 { margin-top: 0.5rem; }
  .mt-3 { margin-top: 0.75rem; }
  .mt-4 { margin-top: 1rem; }

  .header-actions {
    display: flex;
    gap: 0.75rem;
    align-items: center;
  }

  .import-link-modal {
    max-width: 500px !important;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border-radius: 6px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    color: #ef4444;
    font-size: 0.85rem;
  }

  .modal-body-form {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .original-text-helper {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin-top: 0.25rem;
    padding-left: 0.5rem;
  }

  .helper-label {
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.65rem;
    color: var(--color-cyan);
    letter-spacing: 0.05em;
  }

  .helper-content {
    font-style: italic;
  }

  .staged-row-wrapper {
    display: flex;
    flex-direction: column;
    width: 100%;
  }
</style>
