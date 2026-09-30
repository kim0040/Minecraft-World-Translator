<script lang="ts">
  import { open } from '@tauri-apps/plugin-dialog';
  import { app } from '../lib/app.svelte';
  import { t } from '../lib/i18n/index.svelte';
  let { paths = $bindable([]) }: { paths?: string[] } = $props();
  let picking = $state(false);
  async function choose(): Promise<void> {
    if (picking) return;
    picking = true;
    try {
      const selected = await open({ directory: false, multiple: true, title: t('settings.pack.externalChoose'), filters: [{ name: 'ZIP', extensions: ['zip'] }] });
      const chosen = typeof selected === 'string' ? [selected] : selected ?? [];
      const next = [...new Set([...paths, ...chosen])];
      if (next.length > 16) app.notify(t('settings.pack.externalLimit'), 'info');
      else paths = next;
    } catch { app.notify(t('settings.pack.externalFailed'), 'error'); }
    finally { picking = false; }
  }
</script>

<section aria-labelledby="external-packs-title" class="external-packs">
  <div class="heading"><h3 id="external-packs-title">{t('settings.pack.externalTitle')}</h3><button type="button" class="btn btn-secondary" disabled={picking} onclick={choose}>{t('settings.pack.externalChoose')}</button></div>
  <p class="hint">{t('settings.pack.externalHelp')}</p>
  {#if paths.length}
    <ul>
      {#each paths as path (path)}
        <li><span class="mono">{path}</span><button type="button" class="btn btn-quiet" aria-label={t('settings.pack.externalRemove', { path })} onclick={() => paths = paths.filter((item) => item !== path)}>{t('settings.pack.externalRemoveButton')}</button></li>
      {/each}
    </ul>
  {:else}<p class="hint">{t('settings.pack.externalEmpty')}</p>{/if}
</section>

<style>
  .external-packs { display: grid; gap: var(--space-3); }
  .heading { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: var(--space-3); }
  ul { list-style: none; padding: 0; display: grid; gap: var(--space-2); }
  li { display: flex; align-items: center; gap: var(--space-3); min-width: 0; }
  li span { overflow-wrap: anywhere; min-width: 0; flex: 1; font-size: var(--text-sm); }
  li button { flex: none; }
</style>
