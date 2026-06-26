<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { slide } from 'svelte/transition';
  import { Search, Plus, Trash2, Calendar, ClipboardList, Filter } from '@lucide/svelte';

  // State
  let searchQuery = $state('');
  let selectedCategory = $state('All');
  let isAddingManual = $state(false);

  // Manual Item Form State
  let formName = $state('');
  let formQty = $state(1);
  let formUnit = $state('pieces');
  let formCategory = $state('Vegetables');

  // Helper to format default dates
  function getDefaultDateString(daysAhead: number) {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    return d.toISOString().split('T')[0];
  }

  let formUseBy = $state(getDefaultDateString(7));

  const categories = [
    'All',
    'Vegetables',
    'Fruits',
    'Dairy',
    'Meats & Proteins',
    'Grains',
    'Pantry Staples'
  ];

  const units = ['pieces', 'g', 'ml', 'slices', 'tbsp', 'cups', 'pack', 'bottle', 'bunch'];

  // Filtered items computed reactively, sorted by expiration (earliest first)
  let filteredItems = $derived.by(() => {
    let items = pantryStore.pantryItems;
    
    if (selectedCategory !== 'All') {
      items = items.filter(item => item.category === selectedCategory);
    }
    
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim();
      items = items.filter(item => item.name.toLowerCase().includes(query));
    }
    
    // Sort by useByDate ascending, then by name
    return [...items].sort((a, b) => {
      const timeA = new Date(a.useByDate).getTime();
      const timeB = new Date(b.useByDate).getTime();
      if (timeA !== timeB) return timeA - timeB;
      return a.name.localeCompare(b.name);
    });
  });

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    // Convert date string from input to ISO Date
    const isoDate = new Date(formUseBy).toISOString();
    pantryStore.addPantryItem(formName, formQty, formUnit, formCategory, isoDate);
    
    // Reset Form
    formName = '';
    formQty = 1;
    formUnit = 'pieces';
    formUseBy = getDefaultDateString(7);
    isAddingManual = false;
  }

  function formatDate(isoString: string) {
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  }

  function getDaysRemaining(isoString: string) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const expiry = new Date(isoString);
    expiry.setHours(0,0,0,0);
    
    const diffTime = expiry.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  // Quick helper to suggest stock levels and expiration
  function getStockStatus(item: typeof pantryStore.pantryItems[0]) {
    const daysRemaining = getDaysRemaining(item.useByDate);
    if (daysRemaining < 0) {
      return { label: `Expired (${Math.abs(daysRemaining)}d ago)`, class: 'status-expired' };
    }
    if (daysRemaining === 0) {
      return { label: 'Expires Today', class: 'status-expired' };
    }
    if (daysRemaining <= 3) {
      return { label: `Expires in ${daysRemaining}d`, class: 'status-expiring' };
    }
    if (item.quantity <= 2 && (item.unit === 'pieces' || item.unit === 'slices')) {
      return { label: 'Low Stock', class: 'status-low' };
    }
    return { label: 'Fresh', class: 'status-fresh' };
  }
</script>

<div class="pantry-container">
  <!-- Left Column: Pantry Inventory list -->
  <div class="inventory-section card glass">
    <div class="inventory-header">
      <h2>Pantry Inventory</h2>
      <button class="btn btn-emerald btn-sm" onclick={() => isAddingManual = !isAddingManual}>
        <Plus size={16} />
        <span>{isAddingManual ? 'Close Form' : 'Add Item'}</span>
      </button>
    </div>

    <!-- Filters and Search Bar -->
    <div class="filters-row">
      <div class="search-box">
        <Search size={16} class="search-icon" />
        <input 
          type="text" 
          placeholder="Search items..." 
          bind:value={searchQuery}
          class="search-input"
        />
      </div>

      <!-- Categories filter pills -->
      <div class="category-pills">
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

    <!-- Manual Adding Form (Collapsible) -->
    {#if isAddingManual}
      <form onsubmit={handleSubmit} class="manual-form card glass">
        <h3>Add Ingredient Manually</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="item-name">Item Name</label>
            <input 
              type="text" 
              id="item-name" 
              placeholder="e.g., Avocado, Tomatoes" 
              bind:value={formName}
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="item-cat">Category</label>
            <select id="item-cat" bind:value={formCategory} class="form-select">
              {#each categories.filter(c => c !== 'All') as cat}
                <option value={cat}>{cat}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label for="item-expiry">Use By Date</label>
            <input 
              type="date" 
              id="item-expiry" 
              bind:value={formUseBy}
              required
              class="form-input"
            />
          </div>

          <div class="form-group-row">
            <div class="form-group flex-1">
              <label for="item-qty">Qty</label>
              <input 
                type="number" 
                id="item-qty" 
                min="0.1" 
                step="any" 
                bind:value={formQty}
                required
                class="form-input"
              />
            </div>
            
            <div class="form-group flex-1">
              <label for="item-unit">Unit</label>
              <select id="item-unit" bind:value={formUnit} class="form-select">
                {#each units as u}
                  <option value={u}>{u}</option>
                {/each}
              </select>
            </div>
          </div>
        </div>

        <button type="submit" class="btn btn-emerald w-full mt-3">
          <Plus size={16} />
          <span>Add to Inventory</span>
        </button>
      </form>
    {/if}

    <!-- Inventory List -->
    {#if filteredItems.length > 0}
      <div class="inventory-grid">
        {#each filteredItems as item (item.id)}
          <div class="pantry-card glass" transition:slide>
            <div class="card-left">
              <div class="pantry-details">
                <span class="pantry-name">{item.name}</span>
                <span class="pantry-cat">{item.category}</span>
              </div>
              <div class="pantry-meta">
                <div class="meta-item">
                  <Calendar size={12} />
                  <span>Added {formatDate(item.createdAt)}</span>
                </div>
                <span class="stock-badge {getStockStatus(item).class}">
                  {getStockStatus(item).label}
                </span>
              </div>
            </div>

            <!-- Quantity adjusters and delete -->
            <div class="card-right">
              <div class="qty-adjuster">
                <button 
                  onclick={() => pantryStore.updatePantryQuantity(item.id, item.quantity - (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
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
                      pantryStore.updatePantryQuantity(item.id, val);
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
                  onclick={() => pantryStore.updatePantryQuantity(item.id, item.quantity + (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
                  class="qty-btn"
                  aria-label="Increase quantity"
                >+</button>
              </div>
              <button 
                class="delete-btn" 
                onclick={() => pantryStore.deletePantryItem(item.id)} 
                aria-label="Delete item"
              >
                <Trash2 size={16} />
              </button>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="empty-state">
        <ClipboardList size={40} class="text-slate-500 mb-2" />
        <h3>Pantry is Empty</h3>
        <p>No items match your filters, or you haven't scanned any groceries yet. Use the Scanner tab or click "Add Item" above to stock your pantry!</p>
      </div>
    {/if}
  </div>
</div>

<style>
  .pantry-container {
    max-width: 900px;
    margin: 0 auto;
  }

  .inventory-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .inventory-header h2 {
    font-size: 1.5rem;
    font-weight: 800;
  }

  .filters-row {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
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

  .search-icon {
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
    border-color: var(--color-emerald);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
  }

  .category-pills {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    /* scrollbar styling */
    scrollbar-width: none;
  }

  .category-pills::-webkit-scrollbar {
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
    background: var(--color-emerald);
    border-color: var(--color-emerald);
    color: #fff;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
  }

  /* Manual Add Form */
  .manual-form {
    padding: 1.25rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px dashed rgba(16, 185, 129, 0.3);
    border-radius: 12px;
    margin-bottom: 1.5rem;
    animation: slideDown 0.25s ease-out;
  }

  .manual-form h3 {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--color-emerald);
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
  }

  .form-input, .form-select {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.85rem;
  }

  .form-input:focus, .form-select:focus {
    outline: none;
    border-color: var(--color-emerald);
  }

  /* Inventory grid list */
  .inventory-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .pantry-card {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.875rem 1.25rem;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    transition: all 0.2s ease;
  }

  .pantry-card:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.08);
    transform: translateX(2px);
  }

  .card-left {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .pantry-details {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .pantry-name {
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--color-text-light);
  }

  .pantry-cat {
    font-size: 0.65rem;
    padding: 1px 6px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    color: var(--color-text-muted);
  }

  .pantry-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }

  .stock-badge {
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
  }

  .status-fresh {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-emerald);
    border: 1px solid rgba(16, 185, 129, 0.2);
  }

  .status-low {
    background: rgba(249, 115, 22, 0.1);
    color: var(--color-orange);
    border: 1px solid rgba(249, 115, 22, 0.2);
  }

  .status-expired {
    background: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  .status-expiring {
    background: rgba(249, 115, 22, 0.1);
    color: var(--color-orange);
    border: 1px solid rgba(249, 115, 22, 0.2);
  }

  /* Card Right: adjustment / delete */
  .card-right {
    display: flex;
    align-items: center;
    gap: 1rem;
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
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .delete-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }

  /* Empty / seed states */
  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 4rem 1.5rem;
    color: var(--color-text-muted);
    border: 1px dashed rgba(255, 255, 255, 0.08);
    border-radius: 12px;
  }

  .empty-state h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: var(--color-text-light);
    margin-top: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .empty-state p {
    font-size: 0.85rem;
    line-height: 1.4;
    max-width: 400px;
  }

  .btn-sm {
    padding: 0.35rem 0.75rem;
    font-size: 0.8rem;
  }

  .flex-1 { flex: 1; }
  .w-full { width: 100%; }
  .mt-3 { margin-top: 0.75rem; }

  @keyframes slideDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
