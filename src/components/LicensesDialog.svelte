<script lang="ts">
  import { onMount } from 'svelte';
  import { t } from '../lib/i18n/index.svelte';
  import Dialog from './Dialog.svelte';

  let { onClose }: { onClose: () => void } = $props();

  // Both files ship inside the app (public/licenses/, written by scripts/generate-licenses.mjs).
  let own = $state('');
  let thirdParty = $state('');
  let failed = $state(false);
  let tab = $state<'third' | 'own'>('third');

  onMount(() => {
    void Promise.all([
      fetch('/licenses/LICENSE.txt').then((response) => (response.ok ? response.text() : Promise.reject())),
      fetch('/licenses/THIRD_PARTY_LICENSES.txt').then((response) => (response.ok ? response.text() : Promise.reject()))
    ]).then(([mine, theirs]) => { own = mine; thirdParty = theirs; }).catch(() => { failed = true; });
  });
</script>

<Dialog title={t('licenses.title')} size="wide" {onClose}>
  <p>{t('licenses.lead')}</p>
  <div class="segmented" role="group" aria-label={t('licenses.title')}>
    <button type="button" aria-pressed={tab === 'third'} onclick={() => (tab = 'third')}>{t('licenses.thirdParty')}</button>
    <button type="button" aria-pressed={tab === 'own'} onclick={() => (tab = 'own')}>{t('licenses.app')}</button>
  </div>
  {#if failed}
    <p role="alert">{t('licenses.failed')}</p>
  {:else if !thirdParty}
    <p role="status">{t('licenses.loading')}</p>
  {:else}
    <!-- A scrolling text must take keyboard focus to scroll without a mouse (WCAG 2.1.1). -->
    <!-- svelte-ignore a11y_no_noninteractive_tabindex -->
    <pre class="text selectable" tabindex="0" aria-label={tab === 'own' ? t('licenses.app') : t('licenses.thirdParty')}>{tab === 'own' ? own : thirdParty}</pre>
  {/if}
  {#snippet actions()}
    <button type="button" class="btn btn-primary" data-autofocus onclick={onClose}>{t('common.close')}</button>
  {/snippet}
</Dialog>

<style>
  .segmented { justify-self: start; }
  .text { margin: 0; padding: var(--space-3); min-height: 0; max-height: 100%; overflow: auto; white-space: pre-wrap; overflow-wrap: anywhere; font-family: var(--font-mono); font-size: var(--text-xs); line-height: 1.5;
    color: var(--text); background: var(--bg-sunken); border: 1px solid var(--border); border-radius: var(--radius-md); }
</style>
