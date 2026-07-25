<script lang="ts">
  import { Plus, X } from '@lucide/svelte';

  interface Props {
    categories: string[];
    units: string[];
    onAdd: (name: string, qty: number, unit: string, category: string, useBy: string) => void;
    onClose: () => void;
  }

  let { categories, units, onAdd, onClose }: Props = $props();

  let formName = $state('');
  let formQty = $state(1);
  let formUnit = $state('pieces');
  let formCategory = $state('Vegetables');

  function getDefaultDateString(daysAhead: number) {
    const d = new Date();
    d.setDate(d.getDate() + daysAhead);
    return d.toISOString().split('T')[0];
  }

  let formUseBy = $state(getDefaultDateString(7));

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    const isoDate = new Date(formUseBy).toISOString();
    onAdd(formName.trim(), formQty, formUnit, formCategory, isoDate);

    formName = '';
    formQty = 1;
    formUnit = 'pieces';
    formUseBy = getDefaultDateString(7);
    onClose();
  }
</script>

<div class="modal-overlay" onclick={onClose} role="presentation">
  <div class="modal-content glass" onclick={(e) => e.stopPropagation()} role="presentation">
    <button type="button" class="close-btn" onclick={onClose} aria-label="Close modal">
      <X size={18} />
    </button>

    <div class="modal-title-header">
      <h3 class="modal-h3">Add Pantry Item</h3>
      <p class="modal-p">Stock a new batch of ingredients into your pantry inventory.</p>
    </div>

    <form onsubmit={handleSubmit} class="modal-body-form">
      <div class="form-group">
        <label for="item-name">Item Name</label>
        <input 
          type="text" 
          id="item-name" 
          placeholder="e.g., Spinach, Garlic" 
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
          <label for="item-qty">Quantity</label>
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

      <div class="modal-actions mt-2">
        <button type="button" class="btn btn-secondary" onclick={onClose}>
          Cancel
        </button>
        <button type="submit" class="btn btn-cyan">
          <Plus size={16} />
          <span>Add to Inventory</span>
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
