<script lang="ts">
  import { Camera, RefreshCw } from '@lucide/svelte';

  interface PresetItem {
    name: string;
    quantity: number;
    unit: string;
    category: string;
    confidence: number;
    box: { x: number; y: number; w: number; h: number };
  }

  interface PresetBasket {
    name: string;
    description: string;
    items: PresetItem[];
  }

  interface Props {
    cameraActive: boolean;
    cameraError: string | null;
    scanning: boolean;
    scanStep: 'idle' | 'capturing' | 'analyzing' | 'results';
    capturedImageData: string | null;
    presetBaskets: PresetBasket[];
    videoEl: HTMLVideoElement | null;
    canvasEl: HTMLCanvasElement | null;
    onStartCamera: () => void;
    onStopCamera: () => void;
    onCapture: () => void;
    onLoadPreset: (basket: PresetBasket) => void;
    onFileUpload: (e: Event) => void;
  }

  let { 
    cameraActive, 
    cameraError, 
    scanning, 
    scanStep, 
    capturedImageData, 
    presetBaskets,
    videoEl = $bindable(),
    canvasEl = $bindable(),
    onStartCamera,
    onStopCamera,
    onCapture,
    onLoadPreset,
    onFileUpload
  }: Props = $props();

  let fileInput: HTMLInputElement | null = $state(null);
</script>

<div class="visual-scanner-container card glass">
  <div class="scanner-viewport">
    <!-- Camera stream / video element -->
    {#if cameraActive}
      <!-- svelte-ignore a11y_media_has_caption -->
      <video 
        bind:this={videoEl} 
        class="video-feed" 
        autoplay 
        playsinline
      ></video>
      
      <!-- Retro scan line overlays -->
      <div class="scan-laser-overlay"></div>
      <div class="corners-overlay"></div>
    {:else}
      <div class="scanner-placeholder">
        {#if capturedImageData}
          <img src={capturedImageData} alt="Captured snapshot" class="captured-snapshot-preview" />
        {:else}
          <div class="placeholder-icon">
            <Camera size={48} class="text-cyan animate-pulse-slow" />
          </div>
          <h3>Simulated Vision Scanner</h3>
          <p class="placeholder-desc">Use preset demo baskets, upload a receipt, or activate your webcam to start scanning.</p>
        {/if}
      </div>
    {/if}

    <!-- Shutter flash animation -->
    {#if scanStep === 'capturing'}
      <div class="shutter-flash"></div>
    {/if}

    <!-- Analyzing loading overlay -->
    {#if scanStep === 'analyzing'}
      <div class="analyzing-overlay">
        <div class="spinner-container">
          <div class="scanner-spinner"></div>
          <span class="loading-text">Analyzing Grocery Items...</span>
        </div>
      </div>
    {/if}
  </div>

  <!-- Camera Controls -->
  <div class="viewport-controls">
    <div class="camera-actions-row">
      {#if cameraActive}
        <button class="btn btn-secondary" onclick={onStopCamera} disabled={scanning}>
          <span>Turn Off Camera</span>
        </button>
        <button class="btn btn-cyan capture-action-btn" onclick={onCapture} disabled={scanning}>
          <Camera size={18} />
          <span>Snap & Scan</span>
        </button>
      {:else}
        <button class="btn btn-cyan btn-sm" onclick={onStartCamera} disabled={scanning}>
          <RefreshCw size={14} />
          <span>Activate Webcam</span>
        </button>
        
        <button class="btn btn-secondary btn-sm" onclick={() => fileInput?.click()} disabled={scanning}>
          <span>Upload Image</span>
        </button>
        <input 
          type="file" 
          bind:this={fileInput} 
          onchange={onFileUpload} 
          accept="image/*" 
          style="display: none;" 
        />
      {/if}
    </div>

    {#if cameraError}
      <p class="camera-alert">{cameraError}</p>
    {/if}
  </div>

  <!-- Presets Panel -->
  <div class="presets-panel">
    <h4>Demo Preset Groceries</h4>
    <p class="section-desc">Instantly populate items to test the expiration dashboards, multi-batch grouping, and cookbook matches without webcam access.</p>
    
    <div class="presets-grid">
      {#each presetBaskets as basket}
        <button 
          class="preset-card card" 
          onclick={() => onLoadPreset(basket)} 
          disabled={scanning}
        >
          <h5>{basket.name}</h5>
          <p>{basket.description}</p>
        </button>
      {/each}
    </div>
  </div>
</div>

<style>
  .visual-scanner-container {
    padding: 1.25rem;
    background: rgba(30, 41, 59, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.05);
  }

  .scanner-viewport {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    border-radius: 12px;
    overflow: hidden;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .video-feed {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .scan-laser-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: linear-gradient(
      to bottom,
      transparent 0%,
      rgba(6, 182, 212, 0) 45%,
      rgba(6, 182, 212, 0.15) 50%,
      rgba(6, 182, 212, 0) 55%,
      transparent 100%
    );
    background-size: 100% 200%;
    animation: scanLineMove 4s linear infinite;
  }

  .corners-overlay {
    position: absolute;
    inset: 1.5rem;
    border: 2px solid transparent;
    pointer-events: none;
  }

  .corners-overlay::before, .corners-overlay::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border-color: var(--color-cyan);
    border-style: solid;
  }

  .corners-overlay::before {
    top: 0; left: 0; border-width: 2px 0 0 2px;
  }

  .corners-overlay::after {
    bottom: 0; right: 0; border-width: 0 2px 2px 0;
  }

  .scanner-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding: 2rem;
    color: var(--color-text-muted);
  }

  .captured-snapshot-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .placeholder-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: rgba(6, 182, 212, 0.05);
    border: 1px solid rgba(6, 182, 212, 0.15);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
  }

  :global(.animate-pulse-slow) {
    animation: pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: .4; }
  }

  .scanner-placeholder h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-bottom: 0.5rem;
  }

  .placeholder-desc {
    font-size: 0.85rem;
    max-width: 420px;
    line-height: 1.4;
    margin: 0;
  }

  .shutter-flash {
    position: absolute;
    inset: 0;
    background: #fff;
    z-index: 50;
    animation: flashShutter 0.25s ease-out forwards;
  }

  .analyzing-overlay {
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 40;
    backdrop-filter: blur(4px);
  }

  .spinner-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }

  .scanner-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(6, 182, 212, 0.1);
    border-top-color: var(--color-cyan);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  .loading-text {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--color-cyan);
    letter-spacing: 0.02em;
  }

  .viewport-controls {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .camera-actions-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    flex-wrap: wrap;
  }

  .capture-action-btn {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }

  .camera-alert {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin: 0.25rem 0 0 0;
  }

  .presets-panel {
    margin-top: 1.5rem;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 1.25rem;
    text-align: left;
  }

  .presets-panel h4 {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-bottom: 0.25rem;
  }

  .section-desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    margin-bottom: 1rem;
    line-height: 1.4;
  }

  .presets-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  @media (min-width: 640px) {
    .presets-grid {
      grid-template-columns: repeat(3, 1fr);
    }
  }

  .preset-card {
    padding: 0.75rem 1rem;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.04);
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
    height: 100%;
  }

  .preset-card:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.08);
    transform: translateY(-2px);
  }

  .preset-card h5 {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-cyan);
    margin: 0 0 0.25rem 0;
  }

  .preset-card p {
    font-size: 0.7rem;
    color: var(--color-text-muted);
    line-height: 1.35;
    margin: 0;
  }

  @keyframes scanLineMove {
    0% { background-position: 0% 0%; }
    100% { background-position: 0% 200%; }
  }

  @keyframes flashShutter {
    0% { opacity: 0.95; }
    100% { opacity: 0; }
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
