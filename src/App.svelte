<script lang="ts">
  import CameraScanner from './components/CameraScanner.svelte';
  import PantryList from './components/PantryList.svelte';
  import RecipeBook from './components/RecipeBook.svelte';
  import ShoppingList from './components/ShoppingList.svelte';
  import { pantryStore } from './stores/pantryStore.svelte';
  import { Camera, ClipboardList, ChefHat, ShoppingCart } from '@lucide/svelte';

  // Navigation tab state
  let activeTab = $state<'scanner' | 'pantry' | 'cookbook' | 'shopping'>('scanner');

  // Derived counts for dynamic badges
  let shoppingCount = $derived(pantryStore.shoppingList.length);
  let pantryCount = $derived(pantryStore.pantryItems.length);
</script>

<div class="app-wrapper">
  <!-- Desktop & Tablet Header Shell -->
  <header class="app-header glass">
    <div class="logo-area">
      <div class="logo-icon">
        <ChefHat size={24} class="text-cyan" />
      </div>
      <div class="logo-text">
        <h1>Pantry Pilot</h1>
        <span class="tagline">Smart Kitchen Companion</span>
      </div>
    </div>

    <!-- Desktop Navigation Tabs -->
    <nav class="desktop-nav">
      <button 
        class="nav-item {activeTab === 'scanner' ? 'active' : ''}" 
        onclick={() => activeTab = 'scanner'}
      >
        <Camera size={16} />
        <span>Scan Groceries</span>
      </button>

      <button 
        class="nav-item {activeTab === 'pantry' ? 'active' : ''}" 
        onclick={() => activeTab = 'pantry'}
      >
        <ClipboardList size={16} />
        <span>My Pantry</span>
        {#if pantryCount > 0}
          <span class="badge badge-emerald">{pantryCount}</span>
        {/if}
      </button>

      <button 
        class="nav-item {activeTab === 'cookbook' ? 'active' : ''}" 
        onclick={() => activeTab = 'cookbook'}
      >
        <ChefHat size={16} />
        <span>Recipe Book</span>
      </button>

      <button 
        class="nav-item {activeTab === 'shopping' ? 'active' : ''}" 
        onclick={() => activeTab = 'shopping'}
      >
        <ShoppingCart size={16} />
        <span>Shopping List</span>
        {#if shoppingCount > 0}
          <span class="badge badge-cyan">{shoppingCount}</span>
        {/if}
      </button>
    </nav>
  </header>

  <!-- Router Core View Area -->
  <main class="main-content">
    {#if activeTab === 'scanner'}
      <CameraScanner />
    {:else if activeTab === 'pantry'}
      <PantryList />
    {:else if activeTab === 'cookbook'}
      <RecipeBook />
    {:else if activeTab === 'shopping'}
      <ShoppingList />
    {/if}
  </main>

  <!-- Mobile Sticky Bottom Navigation -->
  <nav class="mobile-nav glass">
    <button 
      class="mobile-nav-item {activeTab === 'scanner' ? 'active' : ''}" 
      onclick={() => activeTab = 'scanner'}
    >
      <Camera size={20} />
      <span>Scanner</span>
    </button>

    <button 
      class="mobile-nav-item {activeTab === 'pantry' ? 'active' : ''}" 
      onclick={() => activeTab = 'pantry'}
    >
      <div class="icon-badge-wrapper">
        <ClipboardList size={20} />
        {#if pantryCount > 0}
          <span class="mobile-badge badge-emerald">{pantryCount}</span>
        {/if}
      </div>
      <span>Pantry</span>
    </button>

    <button 
      class="mobile-nav-item {activeTab === 'cookbook' ? 'active' : ''}" 
      onclick={() => activeTab = 'cookbook'}
    >
      <ChefHat size={20} />
      <span>Recipes</span>
    </button>

    <button 
      class="mobile-nav-item {activeTab === 'shopping' ? 'active' : ''}" 
      onclick={() => activeTab = 'shopping'}
    >
      <div class="icon-badge-wrapper">
        <ShoppingCart size={20} />
        {#if shoppingCount > 0}
          <span class="mobile-badge badge-cyan">{shoppingCount}</span>
        {/if}
      </div>
      <span>Shopping</span>
    </button>
  </nav>
</div>

<style>
  .app-wrapper {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    padding-bottom: 80px; /* Account for bottom sticky nav */
  }

  @media (min-width: 768px) {
    .app-wrapper {
      padding-bottom: 2rem;
    }
  }

  .app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 1.25rem;
    margin: 1rem auto;
    width: 95%;
    max-width: 1200px;
    border-radius: 14px;
    z-index: 100;
  }

  .logo-area {
    display: flex;
    align-items: center;
    gap: 0.65rem;
  }

  .logo-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(6, 182, 212, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(6, 182, 212, 0.15);
  }

  .logo-text h1 {
    font-size: 1.15rem;
    font-weight: 800;
    color: #fff;
    line-height: 1;
    letter-spacing: -0.02em;
  }

  .tagline {
    font-size: 0.65rem;
    color: var(--color-text-muted);
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }

  .desktop-nav {
    display: none;
    gap: 0.4rem;
  }

  @media (min-width: 768px) {
    .desktop-nav {
      display: flex;
    }
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0.9rem;
    border-radius: 8px;
    background: transparent;
    border: 1px solid transparent;
    color: var(--color-text-muted);
    font-family: inherit;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .nav-item:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.02);
  }

  .nav-item.active {
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }

  .badge {
    font-size: 0.65rem;
    font-weight: 800;
    padding: 1px 5px;
    border-radius: 9999px;
    color: #fff;
    margin-left: 0.25rem;
  }

  .badge-emerald {
    background: var(--color-emerald);
    box-shadow: 0 0 8px var(--color-emerald-glow);
  }

  .badge-cyan {
    background: var(--color-cyan);
    box-shadow: 0 0 8px var(--color-cyan-glow);
  }

  .main-content {
    flex-grow: 1;
    width: 95%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.5rem 0;
  }

  /* Mobile bottom sticky menu bar */
  .mobile-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 64px;
    background: rgba(7, 11, 22, 0.9);
    border-top: 1px solid rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    z-index: 999;
  }

  @media (min-width: 768px) {
    .mobile-nav {
      display: none;
    }
  }

  .mobile-nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.15rem;
    flex-grow: 1;
    height: 100%;
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    font-family: inherit;
    font-size: 0.65rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .mobile-nav-item.active {
    color: var(--color-cyan);
  }

  .icon-badge-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mobile-badge {
    position: absolute;
    top: -5px;
    right: -8px;
    font-size: 0.55rem;
    padding: 1px 4px;
    margin: 0;
  }
</style>
