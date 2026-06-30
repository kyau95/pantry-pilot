<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { Plus, Trash2, ShoppingCart, AlertTriangle } from '@lucide/svelte';
  import ShoppingProgressPanel from './ShoppingProgressPanel.svelte';
  import ShoppingAddForm from './ShoppingAddForm.svelte';
  import ShoppingCategorySection from './ShoppingCategorySection.svelte';

  // Manual Add Form State
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

  function handleAdd(name: string, quantity: number, unit: string, category: string) {
    pantryStore.addShoppingItem(name, quantity, unit, category);
    triggerToast(`Added ${name} to shopping list!`);
    showAddForm = false;
  }

  function handlePurchase() {
    if (checkedCount === 0) return;
    
    const count = checkedCount;
    pantryStore.purchaseCheckedItems();
    triggerToast(`Moved ${count} item(s) to your Pantry!`);
  }

  let showClearConfirm = $state(false);

  function handleClearConfirm() {
    pantryStore.clearShoppingList();
    showClearConfirm = false;
    triggerToast("Shopping list cleared!");
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

    <div class="header-actions">
      {#if totalCount > 0}
        <button class="btn btn-danger btn-sm" onclick={() => showClearConfirm = true} aria-label="Clear shopping list">
          <Trash2 size={16} />
          <span>Clear List</span>
        </button>
      {/if}
      <button class="btn btn-cyan btn-sm" onclick={() => showAddForm = !showAddForm}>
        <Plus size={16} />
        <span>{showAddForm ? 'Close Form' : 'Add Item'}</span>
      </button>
    </div>
  </div>

  <!-- Progress and Bulk Purchase Area -->
  {#if totalCount > 0}
    <ShoppingProgressPanel 
      {checkedCount} 
      {totalCount} 
      onPurchase={handlePurchase} 
    />
  {/if}

  <!-- Manual Add Form (Collapsible) -->
  {#if showAddForm}
    <ShoppingAddForm 
      {categories} 
      {units} 
      onAdd={handleAdd} 
    />
  {/if}

  <!-- Shopping List Groups -->
  {#if groupedItems.length > 0}
    <div class="shopping-groups">
      {#each groupedItems as [category, items] (category)}
        <ShoppingCategorySection 
          {category} 
          {items} 
          onToggle={(id) => pantryStore.toggleShoppingItem(id)}
          onUpdateQuantity={(id, qty) => pantryStore.updateShoppingQuantity(id, qty)}
          onDelete={(id) => pantryStore.deleteShoppingItem(id)}
        />
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

{#if showClearConfirm}
  <div class="modal-overlay" onclick={() => showClearConfirm = false} role="presentation">
    <div class="modal-content glass confirm-modal" onclick={(e) => e.stopPropagation()} role="presentation">
      <div class="modal-body-form text-center p-6">
        <div class="danger-icon-container">
          <AlertTriangle size={36} />
        </div>
        <h3 class="confirm-title mt-3">Clear Shopping List</h3>
        <p class="confirm-message mt-2">Are you sure you want to delete all <strong>{totalCount}</strong> item(s) from your shopping list? This cannot be undone.</p>
        
        <div class="confirm-actions mt-4">
          <button class="btn btn-danger mr-2" onclick={handleClearConfirm}>Clear All</button>
          <button class="btn btn-secondary" onclick={() => showClearConfirm = false}>Cancel</button>
        </div>
      </div>
    </div>
  </div>
{/if}

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

  .header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .header-titles h2 {
    font-size: 1.75rem;
    font-weight: 800;
    margin-bottom: 0.25rem;
    text-align: left;
  }

  .subtitle {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    text-align: left;
  }

  /* Category groups wrapper styles */
  .shopping-groups {
    display: flex;
    flex-direction: column;
    gap: 1rem;
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

  @keyframes slideUpFade {
    from { opacity: 0; transform: translate(-50%, 15px); }
    to { opacity: 1; transform: translate(-50%, 0); }
  }
</style>
