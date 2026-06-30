<script lang="ts">
  import { AlertTriangle, Clock, Filter } from '@lucide/svelte';

  interface Props {
    expiredCount: number;
    expiringSoonCount: number;
    expiryFilter: 'All' | 'Expired' | 'ExpiringSoon';
  }

  let { expiredCount, expiringSoonCount, expiryFilter = $bindable() }: Props = $props();
</script>

<div class="expiry-dashboard-banner">
  {#if expiredCount > 0}
    <div class="alert-box expired-alert">
      <AlertTriangle size={18} />
      <div class="alert-content">
        <strong>{expiredCount} Item(s) Expired!</strong>
        <span>Spoiled stock detected. Please review and discard.</span>
      </div>
      <button 
        type="button" 
        class="alert-action-btn"
        onclick={() => expiryFilter = expiryFilter === 'Expired' ? 'All' : 'Expired'}
      >
        {expiryFilter === 'Expired' ? 'Show All' : 'Filter Expired'}
      </button>
    </div>
  {/if}

  {#if expiringSoonCount > 0}
    <div class="alert-box expiring-alert">
      <Clock size={18} />
      <div class="alert-content">
        <strong>{expiringSoonCount} Item(s) Expiring Soon!</strong>
        <span>Items are nearing their use-by date (2 days or less).</span>
      </div>
      <button 
        type="button" 
        class="alert-action-btn"
        onclick={() => expiryFilter = expiryFilter === 'ExpiringSoon' ? 'All' : 'ExpiringSoon'}
      >
        {expiryFilter === 'ExpiringSoon' ? 'Show All' : 'Filter Expiring'}
      </button>
    </div>
  {/if}
</div>

<style>
  /* Dashboard alert banners */
  .expiry-dashboard-banner {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    width: 100%;
    margin-bottom: 1.25rem;
  }

  .alert-box {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    backdrop-filter: blur(8px);
    transition: all 0.2s ease;
    text-align: left;
  }

  .expired-alert {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #f87171;
  }

  .expiring-alert {
    background: rgba(249, 115, 22, 0.08);
    border: 1px solid rgba(249, 115, 22, 0.25);
    color: #fb923c;
  }

  .alert-content {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    line-height: 1.35;
  }

  .alert-content strong {
    font-weight: 700;
  }

  .alert-content span {
    opacity: 0.85;
    font-size: 0.8rem;
  }

  .alert-action-btn {
    padding: 0.35rem 0.75rem;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: inherit;
    font-size: 0.75rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.15s ease;
    white-space: nowrap;
  }

  .alert-action-btn:hover {
    background: rgba(255, 255, 255, 0.12);
  }
</style>
