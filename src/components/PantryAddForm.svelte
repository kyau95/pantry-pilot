<script lang="ts">
  import { Plus } from '@lucide/svelte';

  interface Props {
    categories: string[];
    units: string[];
    onAdd: (name: string, qty: number, unit: string, category: string, useBy: string) => void;
  }

  let { categories, units, onAdd }: Props = $props();

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

    // Reset Form
    formName = '';
    formQty = 1;
    formUnit = 'pieces';
    formUseBy = getDefaultDateString(7);
  }
</script>

<form onsubmit={handleSubmit} class="manual-form card glass">
  <h3>Add Pantry Item</h3>
  <div class="form-grid">
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

  <button type="submit" class="btn btn-cyan w-full mt-3">
    <Plus size={16} />
    <span>Add to Inventory</span>
  </button>
</form>

<style>
  /* Manual Form Styling */
  .manual-form {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .manual-form h3 {
    font-size: 1.125rem;
    font-weight: 700;
    margin-bottom: 1rem;
    color: var(--color-text-light);
  }

  .form-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  @media (min-width: 768px) {
    .form-grid {
      grid-template-columns: 2fr 1.5fr 1.5fr 1.5fr;
    }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    align-items: flex-start;
    width: 100%;
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
    width: 100%;
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
  }

  .flex-1 {
    flex: 1;
  }

  .w-full {
    width: 100%;
  }

  .mt-3 {
    margin-top: 0.75rem;
  }
</style>
