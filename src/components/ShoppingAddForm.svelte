<script lang="ts">
  import { Plus, X } from '@lucide/svelte';

  interface Props {
    categories: string[];
    units: string[];
    onAdd: (name: string, quantity: number, unit: string, category: string) => void;
    onClose: () => void;
  }

  let { categories, units, onAdd, onClose }: Props = $props();

  let formName = $state('');
  let formQty = $state(1);
  let formUnit = $state('pieces');
  let formCategory = $state('Vegetables');

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    onAdd(formName.trim(), formQty, formUnit, formCategory);
    
    formName = '';
    formQty = 1;
    formUnit = 'pieces';
    onClose();
  }
</script>

<div class="modal-overlay" onclick={onClose} role="presentation">
  <div class="modal-content glass" onclick={(e) => e.stopPropagation()} role="presentation">
    <button type="button" class="close-btn" onclick={onClose} aria-label="Close modal">
      <X size={18} />
    </button>

    <div class="modal-title-header">
      <h3 class="modal-h3">Add Shopping Item</h3>
      <p class="modal-p">Add a new grocery item to your interactive shopping list.</p>
    </div>

    <form onsubmit={handleSubmit} class="modal-body-form">
      <div class="form-group">
        <label for="shop-name">Item Name</label>
        <input 
          type="text" 
          id="shop-name" 
          placeholder="e.g., Bread, Milk, Cheese" 
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
          <label for="shop-qty">Quantity</label>
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

      <div class="modal-actions mt-2">
        <button type="button" class="btn btn-secondary" onclick={onClose}>
          Cancel
        </button>
        <button type="submit" class="btn btn-cyan">
          <Plus size={16} />
          <span>Add Item</span>
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .flex-1 {
    flex: 1;
  }
  .mt-2 {
    margin-top: 0.5rem;
  }
</style>
