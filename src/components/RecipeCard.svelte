<script lang="ts">
  import { Clock, ChefHat, Check, Trash2 } from '@lucide/svelte';

  interface Recipe {
    id: string;
    name: string;
    description: string;
    prepTime: number;
    cookTime: number;
    difficulty: string;
    category: string;
    image: string;
    isCustom?: boolean;
    stats: {
      matchPercentage: number;
      missingTotal: number;
      canCook: boolean;
    };
  }

  interface Props {
    recipe: Recipe;
    onSelect: () => void;
    onDelete: () => void;
  }

  let { recipe, onSelect, onDelete }: Props = $props();
</script>

<div 
  class="recipe-card glass" 
  onclick={onSelect}
  role="button"
  tabindex="0"
  onkeydown={(e) => e.key === 'Enter' && onSelect()}
>
  <div class="card-image-wrapper">
    <img src={recipe.image} alt={recipe.name} class="card-image" loading="lazy" />
    <div class="category-chip">{recipe.category}</div>
    
    <!-- Matching status badge -->
    <div class="matching-badge-overlay">
      {#if recipe.stats.canCook}
        <span class="match-badge match-full">
          <Check size={12} />
          <span>Ready to Cook</span>
        </span>
      {:else}
        <span class="match-badge match-partial">
          <span>{recipe.stats.matchPercentage}% Matching</span>
        </span>
      {/if}
    </div>

    <!-- Custom delete indicator -->
    {#if recipe.isCustom}
      <button 
        type="button" 
        class="custom-delete-btn"
        onclick={(e) => { e.stopPropagation(); onDelete(); }}
        aria-label="Delete recipe"
      >
        <Trash2 size={14} />
      </button>
    {/if}
  </div>

  <div class="card-info">
    <div class="card-meta">
      <span class="meta-item">
        <Clock size={12} />
        <span>{recipe.prepTime + recipe.cookTime}m</span>
      </span>
      <span class="meta-item">
        <ChefHat size={12} />
        <span>{recipe.difficulty}</span>
      </span>
    </div>
    
    <h3>{recipe.name}</h3>
    <p class="desc">{recipe.description}</p>
    
    <div class="matching-detail-line">
      {#if recipe.stats.canCook}
        <span class="text-emerald font-semibold text-xs">All ingredients in stock</span>
      {:else}
        <span class="text-amber font-semibold text-xs">Missing {recipe.stats.missingTotal} ingredient(s)</span>
      {/if}
    </div>
  </div>
</div>

<style>
  /* Recipe Card */
  .recipe-card {
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    text-align: left;
  }

  .recipe-card:hover {
    transform: translateY(-4px);
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
  }

  .card-image-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 10;
    overflow: hidden;
  }

  .card-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }

  .recipe-card:hover .card-image {
    transform: scale(1.04);
  }

  .category-chip {
    position: absolute;
    top: 0.75rem;
    left: 0.75rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
  }

  .matching-badge-overlay {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
  }

  .match-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
  }

  .match-full {
    background: rgba(16, 185, 129, 0.9);
    color: #fff;
  }

  .match-partial {
    background: rgba(249, 115, 22, 0.9);
    color: #fff;
  }

  .custom-delete-btn {
    position: absolute;
    bottom: 0.75rem;
    right: 0.75rem;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(239, 68, 68, 0.9);
    border: none;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: transform 0.15s;
  }

  .custom-delete-btn:hover {
    transform: scale(1.1);
    background: #ef4444;
  }

  .card-info {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
  }

  .card-meta {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
    color: var(--color-text-muted);
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .recipe-card h3 {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--color-text-light);
    margin: 0 0 0.35rem 0;
    line-height: 1.3;
  }

  .desc {
    font-size: 0.8rem;
    color: var(--color-text-muted);
    line-height: 1.4;
    margin: 0 0 1rem 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-grow: 1;
  }

  .matching-detail-line {
    border-top: 1px solid rgba(255, 255, 255, 0.04);
    padding-top: 0.5rem;
    display: flex;
    justify-content: flex-start;
  }

  .text-emerald {
    color: var(--color-emerald);
  }

  .text-amber {
    color: var(--color-orange);
  }

  .font-semibold {
    font-weight: 600;
  }

  .text-xs {
    font-size: 0.75rem;
  }
</style>
