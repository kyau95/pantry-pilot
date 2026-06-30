<script lang="ts">
  import { slide } from 'svelte/transition';
  import { Trash2 } from '@lucide/svelte';

  interface PantryItem {
    id: string;
    name: string;
    quantity: number;
    unit: string;
    category: string;
    createdAt: string;
    useByDate: string;
  }

  interface PantryGroup {
    name: string;
    category: string;
    totalQtyLabel: string;
    statusClass: string;
    statusLabel: string;
    batches: PantryItem[];
  }

  interface Props {
    g: PantryGroup;
    isExpanded: boolean;
    onToggle: () => void;
    onDeleteBatch: (id: string, name: string) => void;
    onUpdateQuantity: (id: string, qty: number) => void;
  }

  let { g, isExpanded, onToggle, onDeleteBatch, onUpdateQuantity }: Props = $props();

  function getDaysRemaining(isoString: string) {
    const today = new Date();
    today.setHours(0,0,0,0);
    const expiry = new Date(isoString);
    expiry.setHours(0,0,0,0);
    
    const diffTime = expiry.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  function getStockStatus(item: PantryItem) {
    const days = getDaysRemaining(item.useByDate);
    if (days < 0) {
      return { class: 'status-expired', label: days === -1 ? 'Expired yesterday' : `Expired ${Math.abs(days)}d ago` };
    }
    if (days === 0) {
      return { class: 'status-expiring', label: 'Expires today' };
    }
    if (days === 1) {
      return { class: 'status-expiring', label: 'Expires tomorrow' };
    }
    if (days <= 2) {
      return { class: 'status-expiring', label: `Expires in ${days}d` };
    }
    return { class: 'status-fresh', label: 'Fresh' };
  }

  function formatDate(isoString: string) {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  }
</script>

<div class="pantry-group-card glass {isExpanded ? 'expanded' : ''}" transition:slide>
  <div class="group-header" onclick={onToggle} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && onToggle()}>
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
                    onclick={() => onUpdateQuantity(batch.id, batch.quantity - (batch.unit === 'g' || batch.unit === 'ml' ? 50 : 1))} 
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
                        onUpdateQuantity(batch.id, val);
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
                    onclick={() => onUpdateQuantity(batch.id, batch.quantity + (batch.unit === 'g' || batch.unit === 'ml' ? 50 : 1))} 
                    class="qty-btn"
                    aria-label="Increase quantity"
                  >+</button>
                </div>
              </div>
              
              <div class="batch-actions-col text-center">
                <button 
                  type="button"
                  class="delete-btn" 
                  onclick={() => onDeleteBatch(batch.id, g.name)} 
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

<style>
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
    background: rgba(255, 255, 255, 0.04);
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
    display: flex;
    align-items: center;
  }

  .delete-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
</style>
