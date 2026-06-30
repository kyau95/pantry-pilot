<script lang="ts">
  import { X, Clock, ChefHat, Check, ShoppingBag, AlertTriangle } from '@lucide/svelte';
  import { slide } from 'svelte/transition';

  interface Ingredient {
    name: string;
    quantity: number;
    unit: string;
    category: string;
    status: string;
    inStockQty: number;
    missingQty: number;
  }

  interface Recipe {
    id: string;
    name: string;
    description: string;
    prepTime: number;
    cookTime: number;
    difficulty: 'Easy' | 'Medium' | 'Hard';
    category: 'Breakfast' | 'Lunch' | 'Dinner' | 'Snack';
    image: string;
    ingredients: Ingredient[];
    instructions: string[];
    dietaryTags?: string[];
    isCustom?: boolean;
    stats: {
      details: Ingredient[];
      canCook: boolean;
      missingTotal: number;
    };
  }

  interface Props {
    recipe: Recipe;
    cookedMessage: string | null;
    onClose: () => void;
    onCook: () => void;
    onAddToShopping: (ing: Ingredient) => void;
  }

  let { recipe, cookedMessage, onClose, onCook, onAddToShopping }: Props = $props();

  function getStatusBadge(status: string) {
    if (status === 'in-stock') return { class: 'tag-success', label: 'In Stock' };
    if (status === 'insufficient') return { class: 'tag-warning', label: 'Partial' };
    return { class: 'tag-danger', label: 'Missing' };
  }
</script>

<div class="modal-overlay" onclick={onClose} role="presentation">
  <div class="modal-content glass" onclick={(e) => e.stopPropagation()} role="presentation">
    <button class="close-btn" onclick={onClose} aria-label="Close modal">
      <X size={16} />
    </button>

    <div class="modal-scroll-body">
      <!-- Recipe Hero Image banner -->
      <div class="modal-hero">
        <img src={recipe.image} alt={recipe.name} class="hero-image" />
        <div class="hero-gradient-overlay"></div>
        <div class="hero-text-content">
          <span class="hero-category">{recipe.category}</span>
          <h2>{recipe.name}</h2>
          <p>{recipe.description}</p>
        </div>
      </div>

      <!-- Recipe Content Specs Grid -->
      <div class="modal-details-grid">
        <!-- Left Column: Specs, Stats, Ingredients Checklist -->
        <div class="details-left">
          <div class="spec-cards-row">
            <div class="spec-card">
              <span class="label">Prep Time</span>
              <span class="value">{recipe.prepTime} mins</span>
            </div>
            <div class="spec-card">
              <span class="label">Cook Time</span>
              <span class="value">{recipe.cookTime} mins</span>
            </div>
            <div class="spec-card">
              <span class="label">Difficulty</span>
              <span class="value">{recipe.difficulty}</span>
            </div>
          </div>

          <!-- Ingredients Matching Checklist section -->
          <div class="ingredients-list-section mt-4">
            <h3 class="section-title">Ingredients Checklist</h3>
            <p class="section-desc">Pantry Pilot automatically aligns recipe requirements with your active kitchen stock.</p>

            <div class="ingredients-list">
              {#each recipe.stats.details as ing}
                <div class="ing-detail-row {ing.status}">
                  <div class="ing-left">
                    <span class="ing-name">{ing.name}</span>
                    <span class="ing-qty">{ing.quantity} {ing.unit}</span>
                  </div>
                  
                  <div class="ing-right">
                    {#if ing.status !== 'in-stock'}
                      <button 
                        type="button" 
                        class="btn-shopping-add" 
                        onclick={() => onAddToShopping(ing)}
                        aria-label="Add missing item to shopping list"
                      >
                        <ShoppingBag size={12} />
                        <span>Add Missing</span>
                      </button>
                    {/if}
                    
                    <span class="status-indicator-badge {getStatusBadge(ing.status).class}">
                      {getStatusBadge(ing.status).label}
                    </span>
                  </div>
                </div>
              {/each}
            </div>
          </div>
        </div>

        <!-- Right Column: Preparation Steps / Instructions -->
        <div class="details-right">
          <div class="instructions-section">
            <h3 class="section-title">Preparation Steps</h3>
            
            <div class="steps-list">
              {#each recipe.instructions as step, i}
                <div class="step-card-row">
                  <div class="step-number">{i + 1}</div>
                  <div class="step-body">{step}</div>
                </div>
              {/each}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Footer Actions (Cook / Shopping sync) -->
    <div class="modal-footer-sticky glass">
      {#if cookedMessage}
        <div class="cook-success-alert" transition:slide>
          <Check size={16} />
          <span>{cookedMessage}</span>
        </div>
      {/if}

      <div class="footer-actions-row">
        {#if recipe.stats.canCook}
          <button class="btn btn-emerald w-full" onclick={onCook}>
            <Check size={18} />
            <span>Cook this Recipe (Deduct Ingredients)</span>
          </button>
        {:else}
          <div class="missing-ingredients-alert-footer">
            <AlertTriangle size={18} class="text-orange" />
            <div class="alert-text">
              <strong>Insufficient Stock!</strong>
              <span>You are missing {recipe.stats.missingTotal} ingredients. Sync to shopping list to acquire.</span>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(6px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal-content {
    width: 100%;
    max-width: 900px;
    max-height: 90vh;
    background: rgba(25, 30, 45, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  }

  .close-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--color-text-light);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    z-index: 10;
  }

  .close-btn:hover {
    background: rgba(255, 255, 255, 0.1);
  }

  .modal-scroll-body {
    flex-grow: 1;
    overflow-y: auto;
    padding-bottom: 2rem;
  }

  .modal-hero {
    position: relative;
    width: 100%;
    height: 250px;
    overflow: hidden;
    text-align: left;
  }

  .hero-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .hero-gradient-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(15, 23, 42, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%);
  }

  .hero-text-content {
    position: absolute;
    bottom: 1.5rem;
    left: 1.5rem;
    right: 1.5rem;
  }

  .hero-category {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--color-cyan);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .hero-text-content h2 {
    font-size: 1.75rem;
    font-weight: 800;
    color: #fff;
    margin: 0.25rem 0 0.5rem 0;
  }

  .hero-text-content p {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    margin: 0;
    max-width: 600px;
    line-height: 1.4;
  }

  .modal-details-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
    padding: 1.5rem;
    text-align: left;
  }

  @media (min-width: 768px) {
    .modal-details-grid {
      grid-template-columns: 1fr 1.2fr;
    }
  }

  .spec-cards-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }

  .spec-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 0.5rem;
    text-align: center;
    display: flex;
    flex-direction: column;
  }

  .spec-card .label {
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--color-text-muted);
    text-transform: uppercase;
  }

  .spec-card .value {
    font-size: 0.85rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin-top: 0.25rem;
  }

  .section-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0 0 0.25rem 0;
  }

  .section-desc {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin: 0 0 1rem 0;
    line-height: 1.4;
  }

  .ingredients-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .ing-detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  .ing-left {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }

  .ing-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--color-text-light);
  }

  .ing-qty {
    font-size: 0.75rem;
    color: var(--color-text-muted);
  }

  .ing-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .btn-shopping-add {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(6, 182, 212, 0.2);
    color: var(--color-cyan);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-shopping-add:hover {
    background: rgba(6, 182, 212, 0.2);
    color: #fff;
  }

  .status-indicator-badge {
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  .tag-success {
    background: rgba(16, 185, 129, 0.1);
    color: var(--color-emerald);
  }

  .tag-warning {
    background: rgba(249, 115, 22, 0.1);
    color: var(--color-orange);
  }

  .tag-danger {
    background: rgba(239, 68, 68, 0.1);
    color: #f87171;
  }

  /* Instructions Column */
  .steps-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .step-card-row {
    display: flex;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.04);
  }

  .step-number {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--color-cyan);
    color: #000;
    font-size: 0.75rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .step-body {
    font-size: 0.85rem;
    color: var(--color-text-light);
    line-height: 1.45;
  }

  /* Sticky Footer Actions */
  .modal-footer-sticky {
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.9);
    padding: 1rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .cook-success-alert {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--color-emerald);
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
    justify-content: center;
  }

  .footer-actions-row {
    display: flex;
    justify-content: center;
  }

  .missing-ingredients-alert-footer {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    background: rgba(249, 115, 22, 0.05);
    border: 1px solid rgba(249, 115, 22, 0.15);
    width: 100%;
  }

  .alert-text {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    line-height: 1.35;
    font-size: 0.8rem;
  }

  .alert-text strong {
    color: var(--color-orange);
    font-weight: 700;
  }

  .alert-text span {
    color: var(--color-text-muted);
  }

  .w-full {
    width: 100%;
  }

  .mt-4 {
    margin-top: 1rem;
  }

  .text-orange {
    color: var(--color-orange);
  }
</style>
