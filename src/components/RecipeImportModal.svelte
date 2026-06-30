<script lang="ts">
  import { X, Link, Plus, Trash2, Check, AlertCircle } from '@lucide/svelte';
  import { type Recipe, type RecipeIngredient } from '../utils/recipeData';

  interface Props {
    isImportingLink: boolean;
    isAddingCustom: boolean;
    importLoading: boolean;
    importError: string | null;
    stagedRecipe: Recipe | null;
    onImportUrl: (url: string) => void;
    onSaveStaged: () => void;
    onCancelStaged: () => void;
    onAddCustom: (recipe: Recipe) => void;
    onClose: () => void;
  }

  let { 
    isImportingLink = $bindable(), 
    isAddingCustom = $bindable(), 
    importLoading,
    importError,
    stagedRecipe = $bindable(), 
    onImportUrl,
    onSaveStaged,
    onCancelStaged,
    onAddCustom,
    onClose
  }: Props = $props();

  // Link form state
  let urlInput = $state('');

  // Custom recipe form state
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
  const dietaryPresets = ['Vegetarian', 'Vegan', 'Gluten-Free', 'Dairy-Free', 'Keto', 'Low-Carb'];

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

  function handleImportSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!urlInput.trim()) return;
    onImportUrl(urlInput.trim());
  }

  function handleCustomSubmit(e: SubmitEvent) {
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

    onAddCustom(newRecipe);

    // Reset Custom Form
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
  }
</script>

<!-- Link Import Stage Overlay -->
{#if isImportingLink}
  <div class="modal-overlay" onclick={onClose} role="presentation">
    <div class="modal-content glass confirm-modal" onclick={(e) => e.stopPropagation()} role="presentation">
      <button class="close-btn" onclick={onClose} aria-label="Close modal">
        <X size={16} />
      </button>

      <div class="modal-body-form text-left p-6">
        <div class="modal-title-header">
          <Link size={24} class="text-cyan mb-1" />
          <h3 class="modal-h3 mt-1">Import External Recipe Link</h3>
          <p class="modal-p mt-1">Provide a recipe webpage URL (e.g. from AllRecipes, FoodNetwork) to parse the instructions and ingredient list dynamically.</p>
        </div>

        {#if stagedRecipe}
          <!-- Stage 2: Staged Scraped Recipe review and normalize -->
          <div class="staged-recipe-review mt-4">
            <h4 class="staged-review-title">Review Scraped Recipe</h4>
            <p class="modal-p mb-3">Please verify the parsed parameters. Binders will automatically normalize fractional quantities.</p>

            <div class="staged-form-grid">
              <div class="form-group">
                <label for="stage-name">Recipe Name</label>
                <input type="text" id="stage-name" bind:value={stagedRecipe.name} class="form-input w-full" />
              </div>
              <div class="form-group-row">
                <div class="form-group flex-1">
                  <label for="stage-prep">Prep Time</label>
                  <input type="number" id="stage-prep" bind:value={stagedRecipe.prepTime} class="form-input w-full" />
                </div>
                <div class="form-group flex-1">
                  <label for="stage-cook">Cook Time</label>
                  <input type="number" id="stage-cook" bind:value={stagedRecipe.cookTime} class="form-input w-full" />
                </div>
              </div>
            </div>

            <!-- Staged Ingredients review lists -->
            <div class="staged-ingredients mt-4">
              <h5 class="staged-sub-title">Normalized Ingredient Quantities</h5>
              <div class="staged-ingredients-list mt-2">
                {#each stagedRecipe.ingredients as ing, index}
                  <div class="staged-ing-row">
                    <input type="text" bind:value={ing.name} class="staged-ing-name-input flex-2" />
                    <input type="number" bind:value={ing.quantity} class="staged-ing-qty-input flex-1" step="any" />
                    <select bind:value={ing.unit} class="staged-ing-unit-select flex-1">
                      {#each availableUnits as u}
                        <option value={u}>{u}</option>
                      {/each}
                    </select>
                  </div>
                {/each}
              </div>
            </div>

            <div class="staged-actions mt-4">
              <button class="btn btn-secondary mr-2" onclick={onCancelStaged}>Discard</button>
              <button class="btn btn-emerald" onclick={onSaveStaged}>
                <Check size={16} />
                <span>Save to Recipe Book</span>
              </button>
            </div>
          </div>
        {:else}
          <!-- Stage 1: URL input form -->
          <form onsubmit={handleImportSubmit} class="link-import-form mt-4">
            <div class="form-group">
              <label for="import-url">Webpage URL</label>
              <input 
                type="url" 
                id="import-url" 
                placeholder="https://www.allrecipes.com/recipe/..." 
                bind:value={urlInput}
                required
                class="form-input w-full"
                disabled={importLoading}
              />
            </div>

            {#if importError}
              <div class="import-error-msg mt-2">
                <AlertCircle size={14} />
                <span>{importError}</span>
              </div>
            {/if}

            <div class="import-actions mt-4">
              <button 
                type="button" 
                class="btn btn-secondary mr-2" 
                onclick={onClose}
                disabled={importLoading}
              >Cancel</button>
              <button 
                type="submit" 
                class="btn btn-cyan" 
                disabled={importLoading}
              >
                {#if importLoading}
                  <span>Importing...</span>
                {:else}
                  <span>Fetch Recipe</span>
                {/if}
              </button>
            </div>
          </form>
        {/if}
      </div>
    </div>
  </div>
{/if}

<!-- Add Custom Recipe Overlay -->
{#if isAddingCustom}
  <div class="modal-overlay" onclick={onClose} role="presentation">
    <div class="modal-content glass" onclick={(e) => e.stopPropagation()} role="presentation">
      <button class="close-btn" onclick={onClose} aria-label="Close modal">
        <X size={16} />
      </button>

      <div class="modal-scroll-body p-6">
        <div class="modal-title-header text-left">
          <Plus size={24} class="text-cyan mb-1" />
          <h3 class="modal-h3 mt-1">Create Custom Recipe</h3>
          <p class="modal-p mt-1">Construct your cookbook recipes manually with custom ingredients, prep instructions, and dietary tags.</p>
        </div>

        <form onsubmit={handleCustomSubmit} class="custom-recipe-form mt-4 text-left">
          <div class="form-grid-2">
            <div class="form-group">
              <label for="custom-name">Recipe Title</label>
              <input type="text" id="custom-name" bind:value={customName} required class="form-input w-full" placeholder="e.g., Grandma's Lasagna" />
            </div>

            <div class="form-group">
              <label for="custom-desc">Short Description</label>
              <input type="text" id="custom-desc" bind:value={customDesc} class="form-input w-full" placeholder="e.g., A classic beef lasagna baked to golden perfection" />
            </div>

            <div class="form-group-row">
              <div class="form-group flex-1">
                <label for="custom-prep">Prep Time (mins)</label>
                <input type="number" id="custom-prep" bind:value={customPrep} required min="1" class="form-input w-full" />
              </div>
              <div class="form-group flex-1">
                <label for="custom-cook">Cook Time (mins)</label>
                <input type="number" id="custom-cook" bind:value={customCook} required min="0" class="form-input w-full" />
              </div>
            </div>

            <div class="form-group-row">
              <div class="form-group flex-1">
                <label for="custom-difficulty">Difficulty</label>
                <select id="custom-difficulty" bind:value={customDifficulty} class="form-select w-full">
                  <option value="Easy">Easy</option>
                  <option value="Medium">Medium</option>
                  <option value="Hard">Hard</option>
                </select>
              </div>
              <div class="form-group flex-1">
                <label for="custom-category">Category</label>
                <select id="custom-category" bind:value={customCategory} class="form-select w-full">
                  <option value="Breakfast">Breakfast</option>
                  <option value="Lunch">Lunch</option>
                  <option value="Dinner">Dinner</option>
                  <option value="Snack">Snack</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label for="custom-image">Image URL (Optional)</label>
              <input type="text" id="custom-image" bind:value={customImage} class="form-input w-full" placeholder="https://images.unsplash.com/..." />
            </div>
          </div>

          <!-- Ingredients Rows dynamic builder -->
          <div class="ingredients-builder-section mt-4">
            <div class="builder-header">
              <h4>Required Ingredients</h4>
              <button type="button" class="btn btn-cyan btn-xs" onclick={addIngredientRow}>+ Add Ingredient</button>
            </div>
            
            <div class="builder-list mt-2">
              {#each customIngredients as ing, index}
                <div class="builder-row">
                  <input type="text" placeholder="Ingredient name (e.g. Flour)" bind:value={ing.name} required class="form-input builder-input-name flex-2" />
                  <input type="number" step="any" min="0.01" bind:value={ing.quantity} required class="form-input builder-input-qty flex-1" />
                  <select bind:value={ing.unit} class="form-select builder-select-unit flex-1">
                    {#each availableUnits as u}
                      <option value={u}>{u}</option>
                    {/each}
                  </select>
                  <select bind:value={ing.category} class="form-select builder-select-cat flex-1">
                    {#each availableCategories as cat}
                      <option value={cat}>{cat}</option>
                    {/each}
                  </select>
                  {#if customIngredients.length > 1}
                    <button type="button" class="btn-delete-row" onclick={() => removeIngredientRow(index)} aria-label="Delete row">
                      <Trash2 size={14} />
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Instructions steps builder -->
          <div class="instructions-builder-section mt-4">
            <div class="builder-header">
              <h4>Preparation Steps</h4>
              <button type="button" class="btn btn-cyan btn-xs" onclick={addInstructionRow}>+ Add Step</button>
            </div>

            <div class="builder-list mt-2">
              {#each customInstructions as step, index}
                <div class="builder-row">
                  <span class="step-num-label">{index + 1}</span>
                  <input type="text" placeholder="Step description (e.g. Preheat oven to 375F)" bind:value={customInstructions[index]} required class="form-input builder-input-step flex-grow" />
                  {#if customInstructions.length > 1}
                    <button type="button" class="btn-delete-row" onclick={() => removeInstructionRow(index)} aria-label="Delete row">
                      <Trash2 size={14} />
                    </button>
                  {/if}
                </div>
              {/each}
            </div>
          </div>

          <!-- Dietary Tags presets selector -->
          <div class="dietary-tags-section mt-4">
            <h4>Dietary Tags (Optional)</h4>
            <div class="dietary-tags-list mt-2">
              {#each dietaryPresets as tag}
                <button 
                  type="button"
                  class="dietary-tag-btn {customDietary.includes(tag) ? 'active' : ''}"
                  onclick={() => toggleCustomDietary(tag)}
                >
                  {tag}
                </button>
              {/each}
            </div>
          </div>

          <div class="form-actions mt-4">
            <button type="button" class="btn btn-secondary mr-2" onclick={onClose}>Cancel</button>
            <button type="submit" class="btn btn-cyan">Save Custom Recipe</button>
          </div>
        </form>
      </div>
    </div>
  </div>
{/if}

<style>
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
  }

  .modal-content {
    width: 100%;
    max-width: 600px;
    background: rgba(25, 30, 45, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  }

  .modal-content.confirm-modal {
    max-width: 500px;
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
    z-index: 10;
  }

  .close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .modal-scroll-body {
    max-height: 90vh;
    overflow-y: auto;
  }

  .p-6 {
    padding: 1.5rem;
  }

  .modal-title-header {
    margin-bottom: 1rem;
  }

  .modal-h3 {
    font-size: 1.2rem;
    font-weight: 800;
    color: var(--color-text-light);
    margin: 0;
  }

  .modal-p {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    line-height: 1.4;
    margin: 0;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    margin-bottom: 1rem;
    align-items: flex-start;
  }

  .form-group label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .form-input, .form-select {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.85rem;
    text-align: left;
    box-sizing: border-box;
  }

  .form-input:focus, .form-select:focus {
    outline: none;
    border-color: var(--color-cyan);
  }

  .form-group-row {
    display: flex;
    gap: 1rem;
    width: 100%;
    margin-bottom: 1rem;
  }

  .form-grid-2 {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  /* Staged Scrape Review Styles */
  .staged-review-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-cyan);
    margin-bottom: 0.25rem;
    text-transform: uppercase;
  }

  .staged-sub-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
  }

  .staged-ingredients-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-height: 200px;
    overflow-y: auto;
    background: rgba(0, 0, 0, 0.2);
    padding: 0.5rem;
    border-radius: 6px;
  }

  .staged-ing-row {
    display: flex;
    gap: 0.5rem;
  }

  .staged-ing-name-input {
    background: transparent;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    color: #fff;
    font-family: inherit;
    font-size: 0.8rem;
    padding: 0.25rem;
  }

  .staged-ing-qty-input {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #fff;
    font-family: inherit;
    font-size: 0.8rem;
    border-radius: 4px;
    padding: 0.25rem;
    text-align: center;
  }

  .staged-ing-unit-select {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--color-text-muted);
    font-family: inherit;
    font-size: 0.8rem;
    border-radius: 4px;
    padding: 0.25rem;
  }

  .import-error-msg {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #f87171;
    font-size: 0.75rem;
    font-weight: 600;
  }

  /* Dynamic Custom Recipe Builder */
  .builder-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 0.5rem;
  }

  .builder-header h4 {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0;
    text-transform: uppercase;
  }

  .builder-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .builder-row {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .builder-input-name {
    font-size: 0.8rem;
  }

  .builder-input-qty {
    font-size: 0.8rem;
    text-align: center;
  }

  .builder-select-unit, .builder-select-cat {
    font-size: 0.8rem;
    padding: 0.4rem 0.5rem;
  }

  .builder-input-step {
    font-size: 0.8rem;
  }

  .step-num-label {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-muted);
    font-size: 0.7rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .btn-delete-row {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.2);
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .btn-delete-row:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  /* Dietary Preset selectors */
  .dietary-tags-section h4 {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0;
    text-transform: uppercase;
  }

  .dietary-tags-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .dietary-tag-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--color-text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .dietary-tag-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
  }

  .dietary-tag-btn.active {
    background: rgba(6, 182, 212, 0.15);
    border-color: var(--color-cyan);
    color: var(--color-cyan);
  }

  /* Form actions */
  .form-actions {
    display: flex;
    justify-content: flex-end;
  }

  .flex-1 { flex: 1; }
  .flex-2 { flex: 2; }
  .flex-grow { flex-grow: 1; }
  .w-full { width: 100%; }
  .mt-1 { margin-top: 0.25rem; }
  .mt-2 { margin-top: 0.5rem; }
  .mt-4 { margin-top: 1rem; }
  .mb-3 { margin-bottom: 0.75rem; }
  .mr-2 { margin-right: 0.5rem; }
</style>
