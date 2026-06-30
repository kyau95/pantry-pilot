<script lang="ts">
  import { pantryStore } from '../stores/pantryStore.svelte';
  import { slide } from 'svelte/transition';
  import { Search, Plus, ClipboardList, Filter, AlertTriangle } from '@lucide/svelte';
  import PantryDashboard from './PantryDashboard.svelte';
  import PantryAddForm from './PantryAddForm.svelte';
  import PantryGroupCard from './PantryGroupCard.svelte';

  // State
  let searchQuery = $state('');
  let selectedCategory = $state('All');
  let isAddingManual = $state(false);

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

  function handleAdd(name: string, qty: number, unit: string, category: string, useBy: string) {
    pantryStore.addPantryItem(name, qty, unit, category, useBy);
    isAddingManual = false;
  }
</script>

<div class="pantry-container">
  <!-- Dynamic Alert Dashboard Banner -->
  <PantryDashboard 
    {expiredCount} 
    {expiringSoonCount} 
    bind:expiryFilter 
  />

  <div class="inventory-header">
    <div class="header-titles">
      <h2>Pantry Inventory</h2>
      <p class="subtitle">Check your current stock, track expiration dates, and update quantities.</p>
    </div>
    
    <button class="btn btn-emerald btn-sm" onclick={() => isAddingManual = !isAddingManual}>
      <Plus size={16} />
      <span>{isAddingManual ? 'Close Form' : 'Add Item'}</span>
    </button>
  </div>

  <!-- Manual Add Form -->
  {#if isAddingManual}
    <PantryAddForm 
      {categories} 
      {units} 
      onAdd={handleAdd} 
    />
  {/if}

  <!-- Filters Row -->
  <div class="filters-row">
    <div class="search-box">
      <Search size={18} class="search-icon" />
      <input 
        type="text" 
        placeholder="Search ingredients..." 
        bind:value={searchQuery}
        class="search-input"
      />
    </div>

    <!-- Category Pills selection -->
    <div class="category-pills">
      {#each categories as cat}
        <button 
          class="pill-btn {selectedCategory === cat ? 'active' : ''}"
          onclick={() => selectedCategory = cat}
        >
          {cat}
        </button>
      {/each}
    </div>
  </div>

  <!-- Inventory List (Grouped Collapsible Batches) -->
  <div class="inventory-content-area">
    {#if groupedItems.length > 0}
      <div class="inventory-grid">
        {#each groupedItems as g (g.name.toLowerCase().trim())}
          {@const key = g.name.toLowerCase().trim()}
          {@const isExpanded = expandedGroups[key]}
          <PantryGroupCard 
            {g} 
            {isExpanded} 
            onToggle={() => toggleGroup(key)}
            onDeleteBatch={requestDeleteBatch}
            onUpdateQuantity={(id, qty) => pantryStore.updatePantryQuantity(id, qty)}
          />
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

  .subtitle {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    text-align: left;
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
    border-color: var(--color-emerald);
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
  }

  .category-pills {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
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

  .inventory-grid {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  /* Empty state */
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
</style>
