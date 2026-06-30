<script lang="ts">
  import { Check, Eye, Trash2 } from '@lucide/svelte';

  interface DetectedItem {
    name: string;
    quantity: number;
    unit: string;
    category: string;
    confidence: number;
    box: { x: number; y: number; w: number; h: number };
  }

  interface Props {
    detectedItems: DetectedItem[];
    capturedImageData: string | null;
    categories: string[];
    units: string[];
    onSaveAll: () => void;
    onCancel: () => void;
  }

  let { detectedItems = $bindable(), capturedImageData, categories, units, onSaveAll, onCancel }: Props = $props();

  let hoveredIndex = $state<number | null>(null);

  function removeItem(index: number) {
    detectedItems = detectedItems.filter((_, i) => i !== index);
  }

  function adjustQty(index: number, amt: number) {
    if (detectedItems[index]) {
      const unit = detectedItems[index].unit;
      const step = unit === 'g' || unit === 'ml' ? 50 : 1;
      const val = Math.max(0.1, detectedItems[index].quantity + amt * step);
      detectedItems[index].quantity = Math.round(val * 100) / 100;
    }
  }
</script>

<div class="review-panel card glass">
  <div class="review-header">
    <div class="review-title-desc">
      <h3>Review Scanned Groceries</h3>
      <p class="section-desc">We've parsed the scanner feed using our local AI. Verify the names, quantities, and categories before committing to your Pantry.</p>
    </div>
    
    <div class="review-actions">
      <button class="btn btn-secondary" onclick={onCancel}>Discard Scan</button>
      <button class="btn btn-emerald" onclick={onSaveAll} disabled={detectedItems.length === 0}>
        <Check size={18} />
        <span>Add {detectedItems.length} Item(s) to Pantry</span>
      </button>
    </div>
  </div>

  <div class="review-layout">
    <!-- Visual feed bounding box visualization -->
    <div class="image-visualization-card card">
      <div class="image-wrapper-container">
        {#if capturedImageData}
          <img src={capturedImageData} alt="Captured snap" class="snapshot-img" />
        {:else}
          <div class="no-visual-overlay">
            <Eye size={36} class="text-slate-600 mb-2" />
            <span>Visual Bounding Box Unavailable</span>
            <span class="subtext">Barcode scanned products do not generate camera frame bounding coordinates.</span>
          </div>
        {/if}

        <!-- Bounding Box Overlays -->
        {#each detectedItems as item, index}
          <div 
            class="bounding-box-rect {hoveredIndex === index ? 'active' : ''}"
            style="left: {item.box.x}%; top: {item.box.y}%; width: {item.box.w}%; height: {item.box.h}%;"
          >
            <span class="box-label">{item.name}</span>
          </div>
        {/each}
      </div>
    </div>

    <!-- Editable Queue Table -->
    <div class="detected-items-table-wrapper card">
      {#if detectedItems.length > 0}
        <div class="detected-table">
          <div class="table-header-row">
            <span>Item Name</span>
            <span>Category</span>
            <span>Quantity</span>
            <span class="text-center">Remove</span>
          </div>

          <div class="table-body">
            {#each detectedItems as item, index (index)}
              <div 
                class="table-row {hoveredIndex === index ? 'hovered' : ''}"
                onmouseenter={() => hoveredIndex = index}
                onmouseleave={() => hoveredIndex = null}
                role="presentation"
              >
                <!-- Name -->
                <div class="cell-name">
                  <input 
                    type="text" 
                    bind:value={item.name}
                    class="cell-input text-bold"
                    placeholder="Item Name"
                  />
                  <span class="confidence-badge">
                    {Math.round(item.confidence * 100)}% Match
                  </span>
                </div>

                <!-- Category -->
                <div class="cell-category">
                  <select bind:value={item.category} class="cell-select">
                    {#each categories.filter(c => c !== 'All') as cat}
                      <option value={cat}>{cat}</option>
                    {/each}
                  </select>
                </div>

                <!-- Qty + Unit adjusters -->
                <div class="cell-qty">
                  <div class="qty-adjuster">
                    <button type="button" class="qty-btn" onclick={() => adjustQty(index, -1)}>-</button>
                    <input 
                      type="number"
                      bind:value={item.quantity}
                      class="qty-input"
                      min="0.1"
                      step="any"
                    />
                    <select bind:value={item.unit} class="unit-select">
                      {#each units as u}
                        <option value={u}>{u}</option>
                      {/each}
                    </select>
                    <button type="button" class="qty-btn" onclick={() => adjustQty(index, 1)}>+</button>
                  </div>
                </div>

                <!-- Actions -->
                <div class="cell-action text-center">
                  <button 
                    type="button" 
                    class="delete-btn" 
                    onclick={() => removeItem(index)}
                    aria-label="Delete item"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {:else}
        <div class="empty-items-alert">
          <span>All items cleared. Snap another photo or scan a barcode to continue!</span>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .review-panel {
    padding: 1.5rem;
    margin-bottom: 1.5rem;
  }

  .review-header {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
    text-align: left;
  }

  @media (min-width: 768px) {
    .review-header {
      flex-direction: row;
      justify-content: space-between;
      align-items: flex-start;
    }
  }

  .review-title-desc h3 {
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--color-text-light);
    margin: 0 0 0.25rem 0;
  }

  .section-desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin: 0;
    line-height: 1.4;
  }

  .review-actions {
    display: flex;
    gap: 0.75rem;
    flex-shrink: 0;
  }

  .review-layout {
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }

  @media (min-width: 1024px) {
    .review-layout {
      grid-template-columns: 1.2fr 2fr;
    }
  }

  .image-visualization-card {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    overflow: hidden;
    height: fit-content;
  }

  .image-wrapper-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    background: #090d16;
  }

  .snapshot-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .no-visual-overlay {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 2rem;
    color: var(--color-text-muted);
    text-align: center;
  }

  .no-visual-overlay span {
    font-weight: 700;
    font-size: 0.85rem;
    color: var(--color-text-light);
  }

  .no-visual-overlay .subtext {
    font-size: 0.7rem;
    font-weight: 400;
    color: var(--color-text-muted);
    margin-top: 0.25rem;
    max-width: 250px;
    line-height: 1.35;
  }

  .bounding-box-rect {
    position: absolute;
    border: 2px solid var(--color-cyan);
    background: rgba(6, 182, 212, 0.08);
    border-radius: 4px;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
    transition: all 0.2s ease;
    pointer-events: none;
  }

  .bounding-box-rect.active {
    border-color: var(--color-emerald);
    background: rgba(16, 185, 129, 0.15);
    box-shadow: 0 0 15px rgba(16, 185, 129, 0.5);
    z-index: 10;
  }

  .box-label {
    position: absolute;
    top: -20px;
    left: -2px;
    background: var(--color-cyan);
    color: #000;
    font-size: 0.6rem;
    font-weight: 800;
    padding: 1px 4px;
    border-radius: 3px;
    white-space: nowrap;
    text-transform: uppercase;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  }

  .bounding-box-rect.active .box-label {
    background: var(--color-emerald);
    color: #fff;
  }

  /* Table styling */
  .detected-items-table-wrapper {
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.05);
    overflow-x: auto;
  }

  .detected-table {
    min-width: 600px;
    text-align: left;
  }

  .table-header-row {
    display: grid;
    grid-template-columns: 2.2fr 1.8fr 2.5fr 0.8fr;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--color-text-muted);
    letter-spacing: 0.05em;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  }

  .table-row {
    display: grid;
    grid-template-columns: 2.2fr 1.8fr 2.5fr 0.8fr;
    align-items: center;
    padding: 0.65rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    transition: all 0.2s ease;
  }

  .table-row.hovered {
    background: rgba(255, 255, 255, 0.03);
  }

  .cell-name {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .cell-input {
    background: transparent;
    border: none;
    border-bottom: 1px solid transparent;
    color: var(--color-text-light);
    font-family: inherit;
    font-size: 0.9rem;
    padding: 1px 0;
    width: 90%;
  }

  .cell-input:focus {
    outline: none;
    border-color: var(--color-cyan);
  }

  .text-bold {
    font-weight: 600;
  }

  .confidence-badge {
    font-size: 0.65rem;
    color: var(--color-cyan);
    font-weight: 700;
  }

  .cell-category {
    padding-right: 0.5rem;
  }

  .cell-select {
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    border-radius: 4px;
    padding: 0.3rem 0.5rem;
    font-size: 0.8rem;
    font-family: inherit;
    width: 100%;
    outline: none;
  }

  .cell-select:focus {
    border-color: var(--color-cyan);
  }

  .cell-qty {
    display: flex;
    align-items: center;
  }

  .qty-adjuster {
    display: flex;
    align-items: center;
    background: rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    overflow: hidden;
  }

  .qty-btn {
    background: transparent;
    border: none;
    color: var(--color-text-light);
    width: 24px;
    height: 24px;
    cursor: pointer;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
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
    outline: none;
    -moz-appearance: textfield;
    appearance: textfield;
  }

  .qty-input::-webkit-outer-spin-button,
  .qty-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .unit-select {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    font-family: inherit;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0 0.25rem;
    outline: none;
    cursor: pointer;
  }

  .cell-action {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .text-center {
    text-align: center;
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

  .empty-items-alert {
    padding: 3rem 1.5rem;
    color: var(--color-text-muted);
    font-size: 0.85rem;
    text-align: center;
  }
</style>
