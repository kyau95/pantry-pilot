<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { recipes, type Recipe } from '../utils/recipeData';
  import { Search, Clock, ChefHat, Check, AlertTriangle, Plus, X, ShoppingBag } from '@lucide/svelte';

  // Search and filter state
  let searchQuery = $state('');
  let selectedCategory = $state('All');
  let selectedDifficulty = $state('All');
  let selectedRecipe = $state<Recipe | null>(null);
  let cookedMessage = $state<string | null>(null);

  const categories = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];

  // Check ingredient status in pantry
  // Returns: { status: 'in-stock' | 'insufficient' | 'missing', inStockQty: number, missingQty: number }
  function getIngredientStatus(reqIng: { name: string; quantity: number }) {
    // Find matching items in pantry (case insensitive)
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
    return recipes.map(recipe => {
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
      // Refresh modal data if open
      selectedRecipe = recipes.find(r => r.id === recipeId) || null;
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
</div>

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
      grid-template-columns: 1fr 1fr;
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

  @keyframes slideUpFade {
    from { opacity: 0; transform: translate(-50%, 15px); }
    to { opacity: 1; transform: translate(-50%, 0); }
  }
</style>
