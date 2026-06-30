<script lang="ts">
  import { Plus } from '@lucide/svelte';

  interface Props {
    categories: string[];
    units: string[];
    onAdd: (name: string, quantity: number, unit: string, category: string) => void;
  }

  let { categories, units, onAdd }: Props = $props();

  let formName = $state('');
  let formQty = $state(1);
  let formUnit = $state('pieces');
  let formCategory = $state('Vegetables');

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!formName.trim()) return;

    onAdd(formName.trim(), formQty, formUnit, formCategory);
    
    // Reset form fields
    formName = '';
    formQty = 1;
    formUnit = 'pieces';
  }
</script>

<form onsubmit={handleSubmit} class="manual-form card glass">
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

  @media (min-width: 640px) {
    .form-grid {
      grid-template-columns: 2fr 1fr 1.5fr;
    }
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    align-items: flex-start;
  }

  .form-group label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
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
