<script lang="ts">
  import { onMount } from 'svelte';
  import { app } from './lib/app.svelte';
  import { t } from './lib/i18n/index.svelte';
  import { applyTheme, storedTheme, watchSystemTheme } from './lib/theme';
  import Sidebar from './components/Sidebar.svelte';
  import Stepper from './components/Stepper.svelte';
  import Dialog from './components/Dialog.svelte';
  import Callout from './components/Callout.svelte';
  import Toasts from './components/Toasts.svelte';
  import Icon from './components/Icon.svelte';
  import WorldScreen from './screens/WorldScreen.svelte';
  import ScanScreen from './screens/ScanScreen.svelte';
  import ReviewScreen from './screens/ReviewScreen.svelte';
  import RunScreen from './screens/RunScreen.svelte';
  import ResultScreen from './screens/ResultScreen.svelte';
  import BackupsScreen from './screens/BackupsScreen.svelte';
  import SettingsScreen from './screens/SettingsScreen.svelte';
  import AboutScreen from './screens/AboutScreen.svelte';

  onMount(() => {
    app.theme = storedTheme();
    applyTheme(app.theme);
    const stopTheme = watchSystemTheme(() => app.theme);
    void app.boot();
    return () => {
      stopTheme();
      app.destroy();
    };
  });
</script>

<a class="skip" href="#main-content">{t('app.skip')}</a>

<div class="shell" class:rail={app.railCollapsed}>
  <Sidebar />

  <div class="workspace">
    {#if app.page === 'workspace'}
      <header class="workflow-head">
        <Stepper />
      </header>
    {/if}

    <main id="main-content" tabindex="-1" class:review-page={app.page === 'workspace' && app.step === 'review'}>
      {#if !app.ready}
        <div class="boot" role="status" aria-live="polite">
          <span class="spin" aria-hidden="true"><Icon name="refresh" size={24} /></span>
          <span>{t('common.loading')}</span>
        </div>
      {:else if app.startupFailed}
        <Callout tone="danger" title={t('startup.failed')} role="alert">
          <p>{app.banner?.message}</p>
          <p>{t('startup.help')}</p>
          {#snippet actions()}
            <button type="button" class="btn btn-primary" onclick={() => app.boot()}>{t('common.retry')}</button>
          {/snippet}
        </Callout>
      {:else}
        {#if app.banner}
          <div class="banner">
            <Callout tone={app.banner.tone === 'error' ? 'danger' : 'warning'} title={t('error.title')} role="alert">
              {app.banner.message}
              {#snippet actions()}
                <button type="button" class="btn btn-quiet btn-sm" onclick={() => (app.banner = null)}>{t('error.dismiss')}</button>
              {/snippet}
            </Callout>
          </div>
        {/if}

        {#if app.page === 'workspace'}
          {#if app.step === 'world'}<WorldScreen />
          {:else if app.step === 'scan'}<ScanScreen />
          {:else if app.step === 'review'}<ReviewScreen />
          {:else if app.step === 'run'}<RunScreen />
          {:else}<ResultScreen />{/if}
        {:else if app.page === 'backups'}
          <BackupsScreen />
        {:else if app.page === 'settings'}
          <SettingsScreen />
        {:else}
          <AboutScreen />
        {/if}
      {/if}
    </main>
  </div>
</div>

{#if app.showNotice && app.notices}
  <Dialog title={t('notice.title')} dismissible={false} onClose={() => {}}>
    <div class="notice-brand" aria-hidden="true"><img src="/images/pomi.png" alt="" width="72" height="72" /></div>
    <ul class="notice-list">
      <li><Icon name="shield" size={19} /> <span>{t('notice.item1')}</span></li>
      <li><Icon name="language" size={19} /> <span>{t('notice.item2')}</span></li>
      <li><Icon name="info" size={19} /> <span>{t('notice.item3')}</span></li>
    </ul>
    {#snippet actions()}
      <button type="button" class="btn btn-primary btn-lg" data-autofocus onclick={() => app.acceptNotice()}>{t('notice.accept')}</button>
    {/snippet}
  </Dialog>
{/if}

<Toasts />

<style>
  .skip {
    position: fixed; z-index: 100; inset-block-start: var(--space-2); inset-inline-start: var(--space-2);
    translate: 0 -160%; padding: var(--space-2) var(--space-3); border-radius: var(--radius-md);
    background: var(--accent); color: var(--text-on-accent); font-weight: 700;
  }
  .skip:focus { translate: 0; }
  .shell { min-height: 100vh; display: grid; grid-template-columns: var(--sidebar-width) minmax(0, 1fr); }
  .shell.rail { grid-template-columns: var(--sidebar-rail) minmax(0, 1fr); }
  .workspace { grid-column: 2; min-width: 0; display: grid; grid-template-rows: auto minmax(0, 1fr); }
  .workflow-head {
    position: sticky; inset-block-start: 0; z-index: 20; min-width: 0; overflow-x: auto;
    padding: var(--space-3) clamp(var(--space-4), 3vw, var(--space-6));
    background: color-mix(in srgb, var(--bg-page) 92%, transparent); border-block-end: 1px solid var(--border);
    backdrop-filter: blur(12px);
  }
  main { min-width: 0; padding: var(--space-5) clamp(var(--space-4), 3vw, var(--space-6)) var(--space-7); }
  main.review-page { padding-block-end: var(--space-4); }
  .boot { min-height: 50vh; display: flex; align-items: center; justify-content: center; gap: var(--space-3); color: var(--text-secondary); }
  .banner { margin-block-end: var(--space-4); }
  .notice-brand { display: grid; place-items: center; }
  .notice-brand img { width: 72px; height: 72px; object-fit: contain; outline: 1px solid var(--image-outline); outline-offset: -1px; border-radius: var(--radius-xl); }
  .notice-list { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--space-3); }
  .notice-list li { display: grid; grid-template-columns: auto 1fr; align-items: start; gap: var(--space-3); }
  .notice-list :global(.icon) { color: var(--accent-text); margin-top: 2px; }

  @media (max-width: 1000px) {
    .shell, .shell.rail { grid-template-columns: var(--sidebar-rail) minmax(0, 1fr); }
  }
  @media (max-width: 640px) {
    .shell, .shell.rail { --mobile-nav-height: calc(40px + 2 * var(--space-2) + 1px); grid-template-columns: minmax(0, 1fr); padding-block-start: var(--mobile-nav-height); }
    .workspace { grid-column: 1; grid-row: 1; }
    main { padding: var(--space-4) var(--space-3) var(--space-6); }
    .workflow-head { top: var(--mobile-nav-height); padding-inline: var(--space-2); }
    :global(.sidebar) {
      position: fixed !important; inset-block-end: auto; width: 100% !important; height: var(--mobile-nav-height) !important; padding: var(--space-2) !important;
      display: grid !important; grid-template-columns: auto minmax(0, 1fr) !important; align-items: center !important;
      border-inline-end: 0 !important; border-block-end: 1px solid var(--border); gap: var(--space-2) !important;
    }
    :global(.sidebar .brand) { min-height: 40px !important; }
    :global(.sidebar nav) { display: grid !important; grid-template-columns: repeat(4, minmax(40px, 1fr)); }
    :global(.sidebar .foot) { display: none !important; }
  }
</style>
