<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { slide } from 'svelte/transition';
  import { Search, Plus, Trash2, Calendar, ClipboardList, Filter, AlertTriangle, Clock } from '@lucide/svelte';

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

  interface PantryGroup {
    name: string;
    category: string;
    totalQtyLabel: string;
    statusClass: string;
    statusLabel: string;
    batches: Array<typeof pantryStore.pantryItems[0]>;
  }

  let expiryFilter = $state<'All' | 'Expired' | 'ExpiringSoon'>('All');
  let expandedGroups = $state<Record<string, boolean>>({});
  let itemToDelete = $state<{ id: string; name: string } | null>(null);

  function requestDeleteBatch(id: string, name: string) {
    itemToDelete = { id, name };
  }

  function confirmDeleteBatch() {
    if (itemToDelete) {
      pantryStore.deletePantryItem(itemToDelete.id);
      itemToDelete = null;
    }
  }

  function toggleGroup(key: string) {
    expandedGroups = {
      ...expandedGroups,
      [key]: !expandedGroups[key]
    };
  }

  function getDaysRemaining(isoString: string) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const expiry = new Date(isoString);
    expiry.setHours(0,0,0,0);
    
    const diffTime = expiry.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  let expiredCount = $derived.by(() => {
    return pantryStore.pantryItems.filter(item => getDaysRemaining(item.useByDate) < 0).length;
  });

  let expiringSoonCount = $derived.by(() => {
    return pantryStore.pantryItems.filter(item => {
      const days = getDaysRemaining(item.useByDate);
      return days >= 0 && days <= 2;
    }).length;
  });

  let groupedItems = $derived.by(() => {
    const rawItems = pantryStore.pantryItems;
    const groupsMap = new Map<string, PantryGroup>();
    
    for (const item of rawItems) {
      const key = item.name.toLowerCase().trim();
      if (!groupsMap.has(key)) {
        groupsMap.set(key, {
          name: item.name,
          category: item.category,
          totalQtyLabel: '',
          statusClass: 'status-fresh',
          statusLabel: 'Fresh',
          batches: []
        });
      }
      
      const g = groupsMap.get(key)!;
      g.batches.push(item);
    }
    
    const groupsList: PantryGroup[] = [];
    for (const g of groupsMap.values()) {
      g.batches.sort((a, b) => new Date(a.useByDate).getTime() - new Date(b.useByDate).getTime());
      
      // Sum quantities per unit
      const qtyByUnit: Record<string, number> = {};
      for (const b of g.batches) {
        qtyByUnit[b.unit] = (qtyByUnit[b.unit] || 0) + b.quantity;
      }
      
      // Build visual roll-up label (e.g. "2 pack" or "1 pack + 2 pieces")
      g.totalQtyLabel = Object.entries(qtyByUnit)
        .map(([unit, qty]) => `${qty} ${unit}`)
        .join(' + ');
      
      let hasExpired = false;
      let hasExpiring = false;
      let minDaysRemaining = Infinity;
      
      for (const b of g.batches) {
        const days = getDaysRemaining(b.useByDate);
        if (days < minDaysRemaining) {
          minDaysRemaining = days;
        }
        if (days < 0) {
          hasExpired = true;
        } else if (days <= 2) {
          hasExpiring = true;
        }
      }
      
      if (hasExpired) {
        g.statusClass = 'status-expired';
        g.statusLabel = minDaysRemaining < 0 
          ? `Expired (${Math.abs(minDaysRemaining)}d ago)` 
          : 'Expired';
      } else if (hasExpiring) {
        g.statusClass = 'status-expiring';
        g.statusLabel = minDaysRemaining === 0 
          ? 'Expires Today' 
          : `Expires in ${minDaysRemaining}d`;
      } else {
        g.statusClass = 'status-fresh';
        g.statusLabel = 'Fresh';
      }
      
      groupsList.push(g);
    }
    
    let filtered = groupsList;
    
    if (selectedCategory !== 'All') {
      filtered = filtered.filter(g => g.category === selectedCategory);
    }
    
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(g => g.name.toLowerCase().includes(q));
    }
    
    if (expiryFilter === 'Expired') {
      filtered = filtered.filter(g => g.statusClass === 'status-expired');
    } else if (expiryFilter === 'ExpiringSoon') {
      filtered = filtered.filter(g => g.statusClass === 'status-expiring');
    }
    
    const priority = {
      'status-expired': 0,
      'status-expiring': 1,
      'status-fresh': 2
    };
    
    return filtered.sort((a, b) => {
      const prioA = priority[a.statusClass as keyof typeof priority] ?? 2;
      const prioB = priority[b.statusClass as keyof typeof priority] ?? 2;
      if (prioA !== prioB) return prioA - prioB;
      return a.name.localeCompare(b.name);
    });
  });

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    const isoDate = new Date(formUseBy).toISOString();
    pantryStore.addPantryItem(formName, formQty, formUnit, formCategory, isoDate);
    
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

  function getStockStatus(item: typeof pantryStore.pantryItems[0]) {
    const daysRemaining = getDaysRemaining(item.useByDate);
    if (daysRemaining < 0) {
      return { label: `Expired (${Math.abs(daysRemaining)}d ago)`, class: 'status-expired' };
    }
    if (daysRemaining === 0) {
      return { label: 'Expires Today', class: 'status-expired' };
    }
    if (daysRemaining <= 2) {
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

    <!-- Expiry Alert Dashboard Banner -->
    {#if expiredCount > 0 || expiringSoonCount > 0}
      <div class="expiry-dashboard-banner mt-3 mb-1">
        {#if expiredCount > 0}
          <div class="alert-box expired-alert">
            <AlertTriangle size={18} />
            <div class="alert-content">
              <strong>{expiredCount} Item(s) Expired!</strong>
              <span>Discard spoiled items to keep your pantry fresh.</span>
            </div>
            <button 
              type="button" 
              class="alert-action-btn" 
              onclick={() => expiryFilter = expiryFilter === 'Expired' ? 'All' : 'Expired'}
            >
              {expiryFilter === 'Expired' ? 'Show All' : 'Filter Expired'}
            </button>
          </div>
        {/if}
        {#if expiringSoonCount > 0}
          <div class="alert-box expiring-alert">
            <Clock size={18} />
            <div class="alert-content">
              <strong>{expiringSoonCount} Item(s) Expiring Soon!</strong>
              <span>Use them in recipes soon to prevent food waste.</span>
            </div>
            <button 
              type="button" 
              class="alert-action-btn" 
              onclick={() => expiryFilter = expiryFilter === 'ExpiringSoon' ? 'All' : 'ExpiringSoon'}
            >
              {expiryFilter === 'ExpiringSoon' ? 'Show All' : 'Filter Expiring'}
            </button>
          </div>
        {/if}
      </div>
    {/if}

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

    <!-- Inventory List (Grouped Collapsible Batches) -->
    {#if groupedItems.length > 0}
      <div class="inventory-grid">
        {#each groupedItems as g (g.name.toLowerCase().trim())}
          {@const key = g.name.toLowerCase().trim()}
          {@const isExpanded = expandedGroups[key]}
          <div class="pantry-group-card glass {isExpanded ? 'expanded' : ''}" transition:slide>
            <div class="group-header" onclick={() => toggleGroup(key)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && toggleGroup(key)}>
              <div class="group-header-left">
                <div class="chevron-icon {isExpanded ? 'open' : ''}">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
                </div>
                <div class="pantry-details">
                  <span class="pantry-name">{g.name}</span>
                  <span class="pantry-cat">{g.category}</span>
                </div>
              </div>

              <div class="group-header-right">
                <span class="stock-badge {g.statusClass}">{g.statusLabel}</span>
                <span class="total-qty-badge">
                  {g.totalQtyLabel}
                </span>
              </div>
            </div>

            {#if isExpanded}
              <div class="batches-section" transition:slide>
                <div class="batches-table-wrapper">
                  <div class="batches-header-row">
                    <span>Batch Expiration</span>
                    <span>Added On</span>
                    <span>Quantity</span>
                    <span class="text-center">Actions</span>
                  </div>
                  <div class="batches-list">
                    {#each g.batches as batch (batch.id)}
                      <div class="batch-row">
                        <div class="batch-date-col">
                          <span class="batch-expiry-date">{formatDate(batch.useByDate)}</span>
                          <span class="batch-badge {getStockStatus(batch).class}">
                            {getStockStatus(batch).label}
                          </span>
                        </div>
                        
                        <div class="batch-added-col">
                          <span class="batch-added-date">{formatDate(batch.createdAt)}</span>
                        </div>
                        
                        <div class="batch-qty-col">
                          <div class="qty-adjuster">
                            <button 
                              type="button"
                              onclick={() => pantryStore.updatePantryQuantity(batch.id, batch.quantity - (batch.unit === 'g' || batch.unit === 'ml' ? 50 : 1))} 
                              class="qty-btn"
                              aria-label="Decrease quantity"
                            >-</button>
                            <input 
                              type="number"
                              value={batch.quantity}
                              oninput={(e) => {
                                const target = e.target as HTMLInputElement;
                                if (target.value === '') return;
                                const val = parseFloat(target.value);
                                if (!isNaN(val) && val >= 0) {
                                  pantryStore.updatePantryQuantity(batch.id, val);
                                }
                              }}
                              onblur={(e) => {
                                (e.target as HTMLInputElement).value = String(batch.quantity);
                              }}
                              class="qty-input"
                              min="0"
                              step="any"
                            />
                            <span class="qty-unit">{batch.unit}</span>
                            <button 
                              type="button"
                              onclick={() => pantryStore.updatePantryQuantity(batch.id, batch.quantity + (batch.unit === 'g' || batch.unit === 'ml' ? 50 : 1))} 
                              class="qty-btn"
                              aria-label="Increase quantity"
                            >+</button>
                          </div>
                        </div>
                        
                        <div class="batch-actions-col text-center">
                          <button 
                            type="button"
                            class="delete-btn" 
                            onclick={() => requestDeleteBatch(batch.id, g.name)} 
                            aria-label="Delete batch"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </div>
                    {/each}
                  </div>
                </div>
              </div>
            {/if}
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

{#if itemToDelete}
  <div class="modal-overlay" onclick={() => itemToDelete = null} role="presentation">
    <div class="modal-content glass confirm-modal" onclick={(e) => e.stopPropagation()} role="presentation">
      <div class="modal-body-form text-center p-6">
        <div class="danger-icon-container">
          <AlertTriangle size={36} />
        </div>
        <h3 class="confirm-title mt-3">Delete Pantry Batch</h3>
        <p class="confirm-message mt-2">Are you sure you want to delete this batch of <strong>{itemToDelete.name}</strong> from your inventory? This cannot be undone.</p>
        
        <div class="confirm-actions mt-4">
          <button class="btn btn-danger mr-2" onclick={confirmDeleteBatch}>Delete Batch</button>
          <button class="btn btn-secondary" onclick={() => itemToDelete = null}>Cancel</button>
        </div>
      </div>
    </div>
  </div>
{/if}

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

  /* Group Card */
  .pantry-group-card {
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.25s ease;
  }

  .pantry-group-card:hover {
    border-color: rgba(255, 255, 255, 0.08);
  }

  .pantry-group-card.expanded {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }

  .group-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    cursor: pointer;
    user-select: none;
    transition: background-color 0.2s ease;
  }

  .group-header:hover {
    background: rgba(255, 255, 255, 0.03);
  }

  .group-header-left {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .chevron-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--color-text-muted);
    transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1), color 0.2s;
  }

  .chevron-icon.open {
    transform: rotate(90deg);
    color: var(--color-emerald);
  }

  .group-header-right {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .total-qty-badge {
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    font-size: 0.8rem;
    font-weight: 700;
    text-align: center;
    white-space: nowrap;
  }

  /* Batches Section */
  .batches-section {
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    background: rgba(0, 0, 0, 0.15);
    padding: 0.75rem 1.25rem 1rem 1.25rem;
    overflow-x: auto;
  }

  .batches-table-wrapper {
    min-width: 550px;
  }

  .batches-header-row {
    display: grid;
    grid-template-columns: 2fr 1.5fr 2.5fr 1fr;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-text-muted);
    letter-spacing: 0.05em;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    margin-bottom: 0.5rem;
  }

  .batches-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .batch-row {
    display: grid;
    grid-template-columns: 2fr 1.5fr 2.5fr 1fr;
    align-items: center;
    font-size: 0.85rem;
    padding: 0.35rem 0;
  }

  .batch-date-col {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    align-items: flex-start;
  }

  .batch-expiry-date {
    font-weight: 600;
    color: var(--color-text-light);
  }

  .batch-badge {
    padding: 0px 4px;
    border-radius: 3px;
    font-size: 0.6rem;
    font-weight: 700;
  }

  .batch-added-col {
    color: var(--color-text-muted);
  }

  .batch-qty-col {
    display: flex;
    align-items: center;
  }

  .batch-actions-col {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .text-center {
    text-align: center;
  }

  /* Expiry Dashboard alert banners */
  .expiry-dashboard-banner {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
  }

  .alert-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    backdrop-filter: blur(8px);
    transition: all 0.2s ease;
  }

  .expired-alert {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #f87171;
  }

  .expiring-alert {
    background: rgba(249, 115, 22, 0.08);
    border: 1px solid rgba(249, 115, 22, 0.25);
    color: #fb923c;
  }

  .alert-content {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    line-height: 1.35;
  }

  .alert-content strong {
    font-weight: 700;
  }

  .alert-content span {
    opacity: 0.85;
    font-size: 0.8rem;
  }

  .alert-action-btn {
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: inherit;
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .alert-action-btn:hover {
    background: rgba(255, 255, 255, 0.12);
  }

  .card-left {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  .pantry-details {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.15rem;
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
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.02em;
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
