<script lang="ts">
  import { AlertCircle } from '@lucide/svelte';
  import { slide } from 'svelte/transition';

  interface Props {
    barcodeInput: string;
    barcodeError: string | null;
    onScanBarcode: (code: string) => void;
  }

  let { barcodeInput = $bindable(), barcodeError = $bindable(), onScanBarcode }: Props = $props();

  const presets = [
    { code: '800223', name: 'Pasta (800223)' },
    { code: '501004', name: 'Cheese (501004)' },
    { code: '401120', name: 'Avocado (401120)' },
    { code: '326082', name: 'Olive Oil (326082)' },
    { code: '123456', name: 'Eggs (123456)' }
  ];

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (!barcodeInput.trim()) return;
    onScanBarcode(barcodeInput.trim());
  }

  function handleSelectPreset(code: string) {
    barcodeInput = code;
    onScanBarcode(code);
  }
</script>

<div class="barcode-scanner-card card glass">
  <div class="card-header">
    <h3>Simulated Barcode Scanner</h3>
    <p class="section-desc">Pantry Pilot supports physical barcode scanners. Scan or select a code below to simulate a barcode event.</p>
  </div>

  <form onsubmit={handleSubmit} class="barcode-form">
    <div class="form-row">
      <input 
        type="text" 
        placeholder="Enter barcode or scan..." 
        bind:value={barcodeInput}
        class="form-input barcode-input-field"
      />
      <button type="submit" class="btn btn-cyan">Scan Code</button>
    </div>

    {#if barcodeError}
      <div class="barcode-error-alert" transition:slide>
        <AlertCircle size={16} />
        <span>{barcodeError}</span>
      </div>
    {/if}
  </form>

  <div class="barcode-presets">
    <span class="presets-title">Simulated Products:</span>
    <div class="presets-list">
      {#each presets as p}
        <button 
          type="button" 
          class="badge-preset-btn"
          onclick={() => handleSelectPreset(p.code)}
        >
          {p.name}
        </button>
      {/each}
    </div>
  </div>
</div>

<style>
  .barcode-scanner-card {
    padding: 1.25rem;
    background: rgba(30, 41, 59, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.05);
    text-align: left;
  }

  .card-header h3 {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0 0 0.25rem 0;
  }

  .section-desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .barcode-form {
    margin-bottom: 1.25rem;
  }

  .form-row {
    display: flex;
    gap: 0.5rem;
  }

  .barcode-input-field {
    flex-grow: 1;
    font-family: monospace;
    letter-spacing: 0.05em;
    font-size: 0.9rem;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
  }

  .barcode-input-field:focus {
    outline: none;
    border-color: var(--color-cyan);
  }

  .barcode-error-alert {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
    color: #f87171;
    font-size: 0.75rem;
    font-weight: 600;
  }

  .barcode-presets {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 1rem;
  }

  .presets-title {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .presets-list {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .badge-preset-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--color-text-muted);
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.25rem 0.6rem;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.15s;
  }

  .badge-preset-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    border-color: rgba(255, 255, 255, 0.12);
  }
</style>
