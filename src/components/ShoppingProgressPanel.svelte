<script lang="ts">
  import { ShoppingBag, ArrowRight } from '@lucide/svelte';

  interface Props {
    checkedCount: number;
    totalCount: number;
    onPurchase: () => void;
  }

  let { checkedCount, totalCount, onPurchase }: Props = $props();
</script>

<div class="progress-panel card glass">
  <div class="progress-details">
    <span class="progress-text">
      <strong>{checkedCount}</strong> of <strong>{totalCount}</strong> items checked off
    </span>
    <div class="progress-bar-container">
      <div class="progress-bar-fill" style="width: {(checkedCount / totalCount) * 100}%"></div>
    </div>
  </div>

  <button 
    class="btn btn-emerald purchase-btn" 
    disabled={checkedCount === 0}
    onclick={onPurchase}
  >
    <ShoppingBag size={16} />
    <span>Move Checked to Pantry</span>
    <ArrowRight size={14} />
  </button>
</div>

<style>
  .progress-panel {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1.25rem;
    margin-bottom: 1.5rem;
  }

  @media (min-width: 640px) {
    .progress-panel {
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
    }
  }

  .progress-details {
    flex-grow: 1;
    margin-right: 1.5rem;
  }

  .progress-text {
    display: block;
    font-size: 0.9rem;
    color: var(--color-text-light);
    margin-bottom: 0.5rem;
  }

  .progress-bar-container {
    height: 6px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
    overflow: hidden;
  }

  .progress-bar-fill {
    height: 100%;
    background: var(--color-emerald);
    border-radius: 3px;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .purchase-btn {
    align-self: flex-start;
  }

  @media (min-width: 640px) {
    .purchase-btn {
      align-self: auto;
    }
  }
</style>
