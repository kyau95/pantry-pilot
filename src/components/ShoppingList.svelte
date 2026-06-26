<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { Plus, Trash2, CheckSquare, Square, ShoppingCart, ShoppingBag, ArrowRight } from '@lucide/svelte';

  // Manual Add Form State
  let formName = $state('');
  let formQty = $state(1);
  let formUnit = $state('pieces');
  let formCategory = $state('Vegetables');
  let showAddForm = $state(false);
  let showToast = $state(false);
  let toastMsg = $state('');

  const categories = [
    'Vegetables',
    'Fruits',
    'Dairy',
    'Meats & Proteins',
    'Grains',
    'Pantry Staples'
  ];

  const units = ['pieces', 'g', 'ml', 'slices', 'tbsp', 'cups', 'pack', 'bottle', 'bunch'];

  // Derived: group shopping list by category
  let groupedItems = $derived.by(() => {
    const groups: Record<string, typeof pantryStore.shoppingList> = {};
    
    // Initialize groups
    categories.forEach(cat => {
      groups[cat] = [];
    });
    groups['Other'] = [];

    pantryStore.shoppingList.forEach(item => {
      if (groups[item.category]) {
        groups[item.category].push(item);
      } else {
        groups['Other'].push(item);
      }
    });

    // Remove empty groups
    return Object.entries(groups).filter(([_, items]) => items.length > 0);
  });

  // Derived counts
  let checkedCount = $derived(pantryStore.shoppingList.filter(i => i.checked).length);
  let totalCount = $derived(pantryStore.shoppingList.length);

  function handleAdd(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    pantryStore.addShoppingItem(formName, formQty, formUnit, formCategory);
    
    triggerToast(`Added ${formName} to shopping list!`);

    // Reset Form
    formName = '';
    formQty = 1;
    formUnit = 'pieces';
    showAddForm = false;
  }

  function handlePurchase() {
    if (checkedCount === 0) return;
    
    const count = checkedCount;
    pantryStore.purchaseCheckedItems();
    triggerToast(`Moved ${count} item(s) to your Pantry!`);
  }

  function triggerToast(msg: string) {
    toastMsg = msg;
    showToast = true;
    setTimeout(() => {
      showToast = false;
    }, 4000);
  }
</script>

<div class="shopping-container">
  <!-- Toast message / alert notification -->
  {#if showToast}
    <div class="alert-toast glass">
      <div class="toast-content">
        <ShoppingCart size={18} class="toast-icon text-cyan" />
        <span>{toastMsg}</span>
      </div>
    </div>
  {/if}

  <div class="shopping-header">
    <div class="header-titles">
      <h2>Interactive Shopping List</h2>
      <p class="subtitle">Compile needed groceries manually or automatically from recipe requirements.</p>
    </div>

    <button class="btn btn-cyan btn-sm" onclick={() => showAddForm = !showAddForm}>
      <Plus size={16} />
      <span>{showAddForm ? 'Close Form' : 'Add Item'}</span>
    </button>
  </div>

  <!-- Progress and Bulk Purchase Area -->
  {#if totalCount > 0}
    <div class="progress-panel card glass">
      <div class="progress-details">
        <span class="progress-text">
          <strong>{checkedCount}</strong> of <strong>{totalCount}</strong> items checked off
        </span>
        <div class="progress-bar-container">
          <div class="progress-bar-fill" style="width: {(checkedCount / totalCount) * 100}%"></div>
        </div>
      </div>

      <button 
        class="btn btn-emerald purchase-btn" 
        disabled={checkedCount === 0}
        onclick={handlePurchase}
      >
        <ShoppingBag size={16} />
        <span>Move Checked to Pantry</span>
        <ArrowRight size={14} />
      </button>
    </div>
  {/if}

  <!-- Manual Add Form (Collapsible) -->
  {#if showAddForm}
    <form onsubmit={handleAdd} class="manual-form card glass">
      <h3>Add Shopping Item</h3>
      <div class="form-grid">
        <div class="form-group">
          <label for="shop-name">Item Name</label>
          <input 
            type="text" 
            id="shop-name" 
            placeholder="e.g., Bread, Cheese" 
            bind:value={formName}
            required
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="shop-cat">Category</label>
          <select id="shop-cat" bind:value={formCategory} class="form-select">
            {#each categories as cat}
              <option value={cat}>{cat}</option>
            {/each}
          </select>
        </div>

        <div class="form-group-row">
          <div class="form-group flex-1">
            <label for="shop-qty">Qty</label>
            <input 
              type="number" 
              id="shop-qty" 
              min="0.1" 
              step="any" 
              bind:value={formQty}
              required
              class="form-input"
            />
          </div>
          
          <div class="form-group flex-1">
            <label for="shop-unit">Unit</label>
            <select id="shop-unit" bind:value={formUnit} class="form-select">
              {#each units as u}
                <option value={u}>{u}</option>
              {/each}
            </select>
          </div>
        </div>
      </div>

      <button type="submit" class="btn btn-cyan w-full mt-3">
        <Plus size={16} />
        <span>Add to List</span>
      </button>
    </form>
  {/if}

  <!-- Shopping List Groups -->
  {#if groupedItems.length > 0}
    <div class="shopping-groups">
      {#each groupedItems as [category, items] (category)}
        <div class="category-group card glass">
          <h3 class="group-title">{category}</h3>
          
          <div class="items-list">
            {#each items as item (item.id)}
              <div class="shop-item-row {item.checked ? 'checked' : ''}">
                <!-- Checkbox and Name -->
                <button 
                  class="checkbox-wrapper" 
                  onclick={() => pantryStore.toggleShoppingItem(item.id)}
                  aria-label={item.checked ? "Uncheck item" : "Check item"}
                >
                  {#if item.checked}
                    <CheckSquare size={20} class="text-cyan fill-cyan-icon" />
                  {:else}
                    <Square size={20} class="text-muted" />
                  {/if}
                </button>

                <div class="item-details" onclick={() => pantryStore.toggleShoppingItem(item.id)} role="presentation">
                  <span class="item-name">{item.name}</span>
                  {#if item.recipeName}
                    <span class="recipe-context">Required for {item.recipeName}</span>
                  {/if}
                </div>

                <!-- Quantity & Actions -->
                <div class="item-actions">
                  <div class="qty-adjuster">
                    <button 
                      onclick={() => pantryStore.updateShoppingQuantity(item.id, item.quantity - (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
                      class="qty-btn"
                      aria-label="Decrease quantity"
                    >-</button>
                    <input 
                      type="number"
                      value={item.quantity}
                      oninput={(e) => {
                        const target = e.target as HTMLInputElement;
                        if (target.value === '') return;
                        const val = parseFloat(target.value);
                        if (!isNaN(val) && val >= 0) {
                          pantryStore.updateShoppingQuantity(item.id, val);
                        }
                      }}
                      onblur={(e) => {
                        (e.target as HTMLInputElement).value = String(item.quantity);
                      }}
                      class="qty-input"
                      min="0"
                      step="any"
                    />
                    <span class="qty-unit">{item.unit}</span>
                    <button 
                      onclick={() => pantryStore.updateShoppingQuantity(item.id, item.quantity + (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
                      class="qty-btn"
                      aria-label="Increase quantity"
                    >+</button>
                  </div>
                  <button 
                    class="delete-btn" 
                    onclick={() => pantryStore.deleteShoppingItem(item.id)}
                    aria-label="Delete item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="empty-state card glass">
      <ShoppingCart size={48} class="text-muted" />
      <h3>Your Shopping List is Empty</h3>
      <p>Need groceries? Add items manually or use the Recipe Book to automatically populate missing ingredients.</p>
    </div>
  {/if}
</div>

<style>
  .shopping-container {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
  }

  .shopping-header {
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

  /* Progress & Purchase Panel */
  .progress-panel {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
    align-items: center;
  }

  @media (min-width: 640px) {
    .progress-panel {
      flex-direction: row;
      justify-content: space-between;
    }
  }

  .progress-details {
    flex-grow: 1;
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .progress-text {
    font-size: 0.85rem;
    color: var(--color-text-muted);
    text-align: left;
  }

  .progress-bar-container {
    height: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 999px;
    overflow: hidden;
    width: 100%;
  }

  .progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--color-cyan) 0%, var(--color-emerald) 100%);
    border-radius: 999px;
    transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .purchase-btn {
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .purchase-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-muted);
    border-color: rgba(255, 255, 255, 0.05);
    box-shadow: none;
  }

  /* Manual Add Form */
  .manual-form {
    padding: 1.25rem;
    background: rgba(255, 255, 255, 0.01);
    border: 1px dashed rgba(6, 182, 212, 0.3);
    border-radius: 12px;
    margin-bottom: 1.5rem;
    animation: slideDown 0.25s ease-out;
  }

  .manual-form h3 {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--color-cyan);
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 640px) {
    .form-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .form-group-row {
    display: flex;
    gap: 0.5rem;
  }

  .form-group label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--color-text-muted);
    letter-spacing: 0.05em;
    text-align: left;
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
  }

  .form-input:focus, .form-select:focus {
    outline: none;
    border-color: var(--color-cyan);
  }

  /* Category groups styling */
  .shopping-groups {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .category-group {
    padding: 1.25rem;
    text-align: left;
  }

  .group-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-bottom: 0.75rem;
    border-left: 3px solid var(--color-cyan);
    padding-left: 0.5rem;
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .shop-item-row {
    display: flex;
    align-items: center;
    padding: 0.65rem 0.75rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.04);
    transition: all 0.2s;
  }

  .shop-item-row:hover {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.06);
  }

  .shop-item-row.checked {
    opacity: 0.6;
  }

  .checkbox-wrapper {
    background: transparent;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    margin-right: 0.75rem;
    border-radius: 4px;
    color: inherit;
  }

  :global(.fill-cyan-icon) {
    fill: rgba(6, 182, 212, 0.1);
  }

  .item-details {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    cursor: pointer;
  }

  .item-name {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-text-light);
    transition: text-decoration 0.2s;
  }

  .shop-item-row.checked .item-name {
    text-decoration: line-through;
    color: var(--color-text-muted);
  }

  .recipe-context {
    font-size: 0.7rem;
    color: var(--color-cyan);
    font-weight: 500;
    margin-top: 0.1rem;
  }

  .item-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .qty-adjuster {
    display: flex;
    align-items: center;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    overflow: hidden;
  }

  .qty-btn {
    background: transparent;
    border: none;
    color: var(--color-text-light);
    width: 28px;
    height: 28px;
    cursor: pointer;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s;
  }

  .qty-btn:hover {
    background: rgba(255, 255, 255, 0.05);
  }

  .qty-input {
    width: 45px;
    background: transparent;
    border: none;
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
    padding: 0;
    -moz-appearance: textfield;
    appearance: textfield;
  }

  .qty-input::-webkit-outer-spin-button,
  .qty-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .qty-input:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
  }

  .qty-unit {
    color: var(--color-text-muted);
    font-size: 0.7rem;
    margin-right: 0.5rem;
    user-select: none;
  }

  .delete-btn {
    background: transparent;
    border: none;
    color: rgba(255, 255, 255, 0.2);
    cursor: pointer;
    padding: 0.4rem;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .delete-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  /* Empty state */
  .empty-state {
    text-align: center;
    padding: 4.5rem 1.5rem;
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

  /* Animations */
  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes slideUpFade {
    from { opacity: 0; transform: translate(-50%, 15px); }
    to { opacity: 1; transform: translate(-50%, 0); }
  }

  .flex-1 { flex: 1; }
  .w-full { width: 100%; }
  .mt-3 { margin-top: 0.75rem; }
</style>
