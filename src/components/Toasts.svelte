<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { t } from '../lib/i18n/index.svelte';
  import Icon from './Icon.svelte';
</script>

<div class="toasts" class:settings-page={app.page === 'settings'} role="region" aria-label={t('error.title')}>
  {#each app.toasts as toast (toast.id)}
    <div class="toast {toast.tone}" role={toast.tone === 'error' ? 'alert' : 'status'}>
      <Icon name={toast.tone === 'error' ? 'alert-circle' : toast.tone === 'success' ? 'check-circle' : 'info'} size={18} />
      <span class="msg">{toast.message}</span>
      <button type="button" class="btn btn-quiet btn-icon btn-sm" aria-label={t('error.dismiss')} onclick={() => app.dismissToast(toast.id)}>
        <Icon name="x" size={16} />
      </button>
    </div>
  {/each}
</div>

<style>
  .toasts { position: fixed; inset-block-end: var(--space-4); inset-inline-end: var(--space-4); z-index: 50; display: grid; gap: var(--space-2); width: min(420px, calc(100vw - 32px)); pointer-events: none; }
  .toasts.settings-page { inset-block-start: var(--space-4); inset-block-end: auto; }
  @media (max-width: 640px) { .toasts.settings-page { inset-block-start: calc(40px + 2 * var(--space-2) + 1px + var(--space-3)); } }
  .toast { pointer-events: auto; display: grid; grid-template-columns: auto 1fr auto; align-items: start; gap: var(--space-3); padding: var(--space-3) var(--space-3) var(--space-3) var(--space-4);
    border-radius: var(--radius-lg); background: var(--bg-surface); color: var(--text); border: 1px solid var(--border-strong); box-shadow: var(--shadow-pop); animation: in 180ms var(--ease); }
  .toast :global(.icon) { margin-top: 2px; }
  .toast.success :global(.icon:first-child) { color: var(--success-solid); }
  .toast.error :global(.icon:first-child) { color: var(--danger-solid); }
  .toast.info :global(.icon:first-child) { color: var(--accent-text); }
  .msg { font-size: var(--text-sm); padding-top: 2px; }
  @keyframes in { from { opacity: 0; translate: 0 8px; } to { opacity: 1; translate: 0 0; } }
</style>
