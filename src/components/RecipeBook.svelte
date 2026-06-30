<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { type Recipe } from '../utils/recipeData';
  import { Search, ChefHat, AlertTriangle, Plus, Link } from '@lucide/svelte';
  import RecipeCard from './RecipeCard.svelte';
  import RecipeDetailsModal from './RecipeDetailsModal.svelte';
  import RecipeImportModal from './RecipeImportModal.svelte';

  // Search and filter state
  let searchQuery = $state('');
  let selectedCategory = $state('All');
  let selectedDifficulty = $state('All');
  let selectedRecipe = $state<any>(null);
  let cookedMessage = $state<string | null>(null);

  // Link Import State
  let isImportingLink = $state(false);
  let importLoading = $state(false);
  let importError = $state<string | null>(null);
  let stagedRecipe = $state<Recipe | null>(null);

  // Dietary filter state
  let activeDietary = $state<string[]>([]);

  const categories = ['All', 'Breakfast', 'Lunch', 'Dinner', 'Snack'];
  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];

  // Add Custom Recipe Form State
  let isAddingCustom = $state(false);
  let showToast = $state(false);
  let toastMsg = $state('');
  let recipeToDelete = $state<Recipe | null>(null);

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
      const q = searchQuery.toLowerCase().trim();
      list = list.filter(r => 
        r.name.toLowerCase().includes(q) || 
        r.ingredients.some(i => i.name.toLowerCase().includes(q))
      );
    }

    // Sort by matching percentage (can cook first, then higher matches)
    return list.sort((a, b) => {
      if (a.stats.canCook && !b.stats.canCook) return -1;
      if (!a.stats.canCook && b.stats.canCook) return 1;
      return b.stats.matchPercentage - a.stats.matchPercentage;
    });
  });

  async function handleImportUrl(url: string) {
    importLoading = true;
    importError = null;
    try {
      const res = await fetch('http://localhost:8000/api/recipes/scrape-external-link', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      const data = await res.json();
      if (data.status === 'success') {
        stagedRecipe = data.recipe;
      } else {
        importError = data.message || 'Failed to import recipe from URL.';
      }
    } catch (err) {
      importError = 'Server connection failed. Make sure the backend is running.';
    } finally {
      importLoading = false;
    }
  }

  function handleSaveStaged() {
    if (stagedRecipe) {
      pantryStore.addCustomRecipe(stagedRecipe);
      stagedRecipe = null;
      isImportingLink = false;
      triggerToast('Recipe imported successfully!');
    }
  }

  function handleCancelStaged() {
    stagedRecipe = null;
  }

  function handleCookRecipe(recipe: Recipe) {
    pantryStore.cookRecipe(recipe.id);
    cookedMessage = "Ingredients successfully deducted from Pantry!";
    triggerToast(`Cooked ${recipe.name}!`);
    setTimeout(() => {
      cookedMessage = null;
    }, 4000);
  }

  function handleAddToShopping(ing: { name: string; quantity: number; unit: string; category: string }) {
    pantryStore.addShoppingItem(ing.name, ing.quantity, ing.unit, ing.category, selectedRecipe?.name);
    triggerToast(`Added ${ing.name} to Shopping List!`);
  }

  function requestDeleteRecipe(recipe: Recipe) {
    recipeToDelete = recipe;
  }

  function confirmDeleteRecipe() {
    if (recipeToDelete) {
      pantryStore.deleteCustomRecipe(recipeToDelete.id);
      recipeToDelete = null;
      selectedRecipe = null;
      triggerToast('Custom recipe deleted.');
    }
  }

  function toggleDietaryTag(tag: string) {
    if (activeDietary.includes(tag)) {
      activeDietary = activeDietary.filter(t => t !== tag);
    } else {
      activeDietary.push(tag);
    }
  }

  function triggerToast(msg: string) {
    toastMsg = msg;
    showToast = true;
    setTimeout(() => {
      showToast = false;
    }, 4000);
  }

  function handleCloseImport() {
    isImportingLink = false;
    isAddingCustom = false;
    stagedRecipe = null;
    importError = null;
  }
</script>

<div class="recipe-container">
  <!-- Toast feedback banner -->
  {#if showToast}
    <div class="alert-toast glass">
      <div class="toast-content">
        <ChefHat size={18} class="toast-icon text-cyan" />
        <span>{toastMsg}</span>
      </div>
    </div>
  {/if}

  <div class="recipe-header">
    <div class="header-titles text-left">
      <h2>Cookbook & Meal Matcher</h2>
      <p class="subtitle">Match recipes with what's currently in your pantry. Missing items can be synced to your shopping checklist.</p>
    </div>
    
    <div class="header-actions">
      <button class="btn btn-secondary btn-sm" onclick={() => isImportingLink = true}>
        <Link size={16} />
        <span>Import Link</span>
      </button>
      <button class="btn btn-cyan btn-sm" onclick={() => isAddingCustom = true}>
        <Plus size={16} />
        <span>Create Recipe</span>
      </button>
    </div>
  </div>

  <!-- Search & Category Filters -->
  <div class="filters-row">
    <div class="search-box">
      <Search size={18} class="search-icon" />
      <input 
        type="text" 
        placeholder="Search recipes or ingredients..." 
        bind:value={searchQuery}
        class="search-input"
      />
    </div>

    <div class="filters-dropdowns">
      <div class="select-wrapper">
        <select bind:value={selectedCategory} class="filter-select">
          {#each categories as cat}
            <option value={cat}>{cat === 'All' ? 'All Categories' : cat}</option>
          {/each}
        </select>
      </div>

      <div class="select-wrapper">
        <select bind:value={selectedDifficulty} class="filter-select">
          {#each difficulties as diff}
            <option value={diff}>{diff === 'All' ? 'All Difficulties' : diff}</option>
          {/each}
        </select>
      </div>
    </div>
  </div>

  <!-- Dietary tag filter buttons -->
  <div class="dietary-tags-row">
    <span class="tags-label">Dietary Filters:</span>
    <div class="tags-list">
      {#each ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto'] as tag}
        <button 
          class="tag-btn {activeDietary.includes(tag) ? 'active' : ''}"
          onclick={() => toggleDietaryTag(tag)}
        >
          {tag}
        </button>
      {/each}
    </div>
  </div>

  <!-- Grid of Recipes -->
  <div class="recipes-content-area">
    {#if filteredRecipes.length > 0}
      <div class="recipes-grid">
        {#each filteredRecipes as recipe (recipe.id)}
          <RecipeCard 
            {recipe} 
            onSelect={() => selectedRecipe = recipe} 
            onDelete={() => requestDeleteRecipe(recipe)}
          />
        {/each}
      </div>
    {:else}
      <div class="empty-state card glass">
        <ChefHat size={40} class="text-slate-500 mb-2" />
        <h3>No Matching Recipes</h3>
        <p>No recipes match your current filters. Try relaxing your dietary filters, searching for a different keyword, or importing a new recipe URL!</p>
      </div>
    {/if}
  </div>
</div>

<!-- Details Modal -->
{#if selectedRecipe}
  <RecipeDetailsModal 
    recipe={selectedRecipe}
    {cookedMessage}
    onClose={() => { selectedRecipe = null; cookedMessage = null; }}
    onCook={() => handleCookRecipe(selectedRecipe!)}
    onAddToShopping={handleAddToShopping}
  />
{/if}

<!-- Import / Custom Forms Modals -->
<RecipeImportModal 
  bind:isImportingLink 
  bind:isAddingCustom 
  {importLoading}
  {importError}
  bind:stagedRecipe
  onImportUrl={handleImportUrl}
  onSaveStaged={handleSaveStaged}
  onCancelStaged={handleCancelStaged}
  onAddCustom={(r) => { pantryStore.addCustomRecipe(r); handleCloseImport(); triggerToast('Custom recipe added!'); }}
  onClose={handleCloseImport}
/>

<!-- Delete custom recipe confirmation modal -->
{#if recipeToDelete}
  <div class="modal-overlay" onclick={() => recipeToDelete = null} role="presentation">
    <div class="modal-content glass confirm-modal" onclick={(e) => e.stopPropagation()} role="presentation">
      <div class="modal-body-form text-center p-6">
        <div class="danger-icon-container">
          <AlertTriangle size={36} />
        </div>
        <h3 class="confirm-title mt-3">Delete Recipe</h3>
        <p class="confirm-message mt-2">Are you sure you want to remove <strong>{recipeToDelete.name}</strong> from your cookbook? This cannot be undone.</p>
        
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
    max-width: 1000px;
    margin: 0 auto;
  }

  .recipe-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .header-titles h2 {
    font-size: 1.5rem;
    font-weight: 800;
  }

  .subtitle {
    font-size: 0.9rem;
    color: var(--color-text-muted);
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  .filters-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  @media (min-width: 768px) {
    .filters-row {
      flex-direction: row;
      align-items: center;
    }
  }

  .search-box {
    position: relative;
    flex-grow: 1;
    min-width: 200px;
  }

  :global(.search-icon) {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--color-text-muted);
  }

  .search-input {
    width: 100%;
    padding: 0.5rem 0.75rem 0.5rem 2.25rem;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .search-input:focus {
    outline: none;
    border-color: var(--color-cyan);
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.15);
  }

  .filters-dropdowns {
    display: flex;
    gap: 0.5rem;
  }

  .filter-select {
    padding: 0.5rem 2rem 0.5rem 0.75rem;
    border-radius: 8px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.85rem;
    cursor: pointer;
    outline: none;
  }

  .filter-select:focus {
    border-color: var(--color-cyan);
  }

  /* Dietary Tags Row */
  .dietary-tags-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    text-align: left;
  }

  .tags-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .tags-list {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .tag-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--color-text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.3rem 0.65rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .tag-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
  }

  .tag-btn.active {
    background: rgba(6, 182, 212, 0.15);
    border-color: var(--color-cyan);
    color: var(--color-cyan);
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
  }

  /* Recipes Grid */
  .recipes-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
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

  /* Empty state card */
  .empty-state {
    text-align: center;
    padding: 4rem 1.5rem;
    color: var(--color-text-muted);
    border: 1px dashed rgba(255, 255, 255, 0.08);
    border-radius: 12px;
  }

  .empty-state h3 {
    font-size: 1.15rem;
    color: var(--color-text-light);
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .empty-state p {
    font-size: 0.85rem;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.4;
  }

  /* Toast Notification */
  .alert-toast {
    position: fixed;
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 2000;
    border-radius: 10px;
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid rgba(6, 182, 212, 0.3);
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

  :global(.toast-icon) {
    flex-shrink: 0;
  }

  @keyframes slideUpFade {
    from { opacity: 0; transform: translate(-50%, 15px); }
    to { opacity: 1; transform: translate(-50%, 0); }
  }

  :global(.text-cyan) {
    color: var(--color-cyan);
  }
</style>
