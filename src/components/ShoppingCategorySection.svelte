<script lang="ts">
  import { CheckSquare, Square, Trash2 } from '@lucide/svelte';

  interface ShoppingItem {
    id: string;
    name: string;
    quantity: number;
    unit: string;
    category: string;
    checked: boolean;
    recipeName?: string;
  }

  interface Props {
    category: string;
    items: ShoppingItem[];
    onToggle: (id: string) => void;
    onUpdateQuantity: (id: string, qty: number) => void;
    onDelete: (id: string) => void;
  }

  let { category, items, onToggle, onUpdateQuantity, onDelete }: Props = $props();
</script>

<div class="category-group card glass">
  <h3 class="group-title">{category}</h3>
  
  <div class="items-list">
    {#each items as item (item.id)}
      <div class="shop-item-row {item.checked ? 'checked' : ''}">
        <!-- Checkbox and Name -->
        <button 
          class="checkbox-wrapper" 
          onclick={() => onToggle(item.id)}
          aria-label={item.checked ? "Uncheck item" : "Check item"}
        >
          {#if item.checked}
            <CheckSquare size={20} class="text-cyan fill-cyan-icon" />
          {:else}
            <Square size={20} class="text-muted" />
          {/if}
        </button>

        <div class="item-details" onclick={() => onToggle(item.id)} role="presentation">
          <span class="item-name">{item.name}</span>
          {#if item.recipeName}
            <span class="recipe-context">Required for {item.recipeName}</span>
          {/if}
        </div>

        <!-- Quantity & Actions -->
        <div class="item-actions">
          <div class="qty-adjuster">
            <button 
              onclick={() => onUpdateQuantity(item.id, item.quantity - (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
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
                  onUpdateQuantity(item.id, val);
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
              onclick={() => onUpdateQuantity(item.id, item.quantity + (item.unit === 'g' || item.unit === 'ml' ? 50 : 1))} 
              class="qty-btn"
              aria-label="Increase quantity"
            >+</button>
          </div>
          <button 
            class="delete-btn" 
            onclick={() => onDelete(item.id)}
            aria-label="Delete item"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    {/each}
  </div>
</div>

<style>
  /* Shopping Checklist Items styles */
  .category-group {
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    background: rgba(30, 41, 59, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
  }

  .group-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-cyan);
    margin-bottom: 1rem;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .items-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .shop-item-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.03);
    transition: all 0.2s ease;
  }

  .shop-item-row:hover {
    background: rgba(255, 255, 255, 0.03);
    border-color: rgba(255, 255, 255, 0.06);
  }

  .shop-item-row.checked {
    opacity: 0.65;
    background: rgba(255, 255, 255, 0.005);
  }

  .shop-item-row.checked .item-name {
    text-decoration: line-through;
    color: var(--color-text-muted);
  }

  .checkbox-wrapper {
    background: transparent;
    border: none;
    padding: 0;
    margin-right: 0.75rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    color: inherit;
  }

  :global(.fill-cyan-icon) {
    fill: rgba(6, 182, 212, 0.15);
  }

  .item-details {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    cursor: pointer;
  }

  .item-name {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--color-text-light);
    text-align: left;
  }

  .recipe-context {
    font-size: 0.7rem;
    color: var(--color-cyan);
    margin-top: 0.15rem;
    opacity: 0.85;
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
    width: 26px;
    height: 26px;
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
    width: 38px;
    background: transparent;
    border: none;
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.8rem;
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
    border-radius: 3px;
  }

  .qty-unit {
    color: var(--color-text-muted);
    font-size: 0.7rem;
    margin-right: 0.4rem;
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
    display: flex;
    align-items: center;
  }

  .delete-btn:hover {
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
  }
</style>
