<script lang="ts">
  import { app, type Page } from '../lib/app.svelte';
  import { t } from '../lib/i18n/index.svelte';
  import { formatDuration } from '../lib/format';
  import Icon, { type IconName } from './Icon.svelte';

  const items: { page: Page; icon: IconName; label: 'nav.workspace' | 'nav.backups' | 'nav.settings' | 'nav.about' }[] = [
    { page: 'workspace', icon: 'language', label: 'nav.workspace' },
    { page: 'backups', icon: 'archive', label: 'nav.backups' },
    { page: 'settings', icon: 'sliders', label: 'nav.settings' },
    { page: 'about', icon: 'info', label: 'nav.about' }
  ];

  const status = $derived(
    app.cancelling ? t('status.cancelling')
      : app.busy === 'scan' ? t('status.scanning')
      : app.busy === 'translate' ? t('status.translating')
      : app.busy === 'restore' ? t('status.restoring')
      : app.busy ? t('status.working')
      : app.startupFailed ? t('startup.failed')
      : t('status.ready')
  );
  let now = $state(Date.now());
  $effect(() => {
    if (!app.isBusy) return;
    now = Date.now();
    const timer = setInterval(() => { now = Date.now(); }, 1000);
    return () => clearInterval(timer);
  });

  const percent = $derived(
    app.busy === 'translate' && app.progress.phase === 'translate' && app.progress.total > 0
      ? Math.round((app.progress.done / app.progress.total) * 100)
      : null
  );
</script>

<aside class="sidebar" class:rail={app.railCollapsed}>
  <div class="brand">
    <img class="wordmark" src="/images/wordmark.png" alt="PomiTranslate" width="176" />
    <span class="dark-wordmark" role="img" aria-label="PomiTranslate">Pomi<span>Translate</span></span>
  </div>

  <nav aria-label={t('nav.main')}>
    {#each items as item (item.page)}
      <button
        type="button"
        class="nav"
        class:active={app.page === item.page}
        disabled={app.busy === 'settings' || !app.ready || app.startupFailed}
        aria-label={t(item.label)}
        aria-current={app.page === item.page ? 'page' : undefined}
        title={app.railCollapsed ? t(item.label) : undefined}
        onclick={() => app.goto(item.page)}
      >
        <Icon name={item.icon} size={20} />
        <span class="label">{t(item.label)}</span>
      </button>
    {/each}
  </nav>

  <div class="foot">
    <div class="state" role="status" aria-live="polite">
      <img class="pomi" src="/images/pomi.png" alt="" width="44" height="44" />
      <div class="text">
        <span class="dot" class:busy={app.isBusy} aria-hidden="true"></span>
        <span class="status-text">{status}{percent !== null ? ` ${percent}%` : ''}</span>
        {#if app.isBusy && app.progress.startedAt}
          <span class="sub num">{formatDuration((now - app.progress.startedAt) / 1000, app.locale)}</span>
        {/if}
      </div>
    </div>
    <button type="button" class="collapse btn btn-quiet btn-sm" aria-label={t('nav.collapse')} aria-pressed={app.railCollapsed} onclick={() => (app.railCollapsed = !app.railCollapsed)}>
      <Icon name="sidebar" size={18} />
    </button>
  </div>
</aside>

<style>
  .sidebar {
    position: fixed; inset-block: 0; inset-inline-start: 0; z-index: 30; height: 100vh; height: 100dvh; overflow-y: auto; overscroll-behavior-y: contain; display: flex; flex-direction: column; gap: var(--space-5);
    padding: var(--space-5) var(--space-4) var(--space-4); background: var(--bg-surface); border-inline-end: 1px solid var(--border);
    width: var(--sidebar-width);
  }
  .sidebar.rail { width: var(--sidebar-rail); padding-inline: var(--space-3); }
  .brand { padding-inline: var(--space-2); min-height: 56px; display: flex; align-items: center; }
  .wordmark { width: 156px; height: auto; margin-top: -6px; }
  .dark-wordmark { display: none; font-size: var(--text-xl); font-weight: 800; letter-spacing: -0.04em; color: var(--text); white-space: nowrap; }
  .dark-wordmark span { color: var(--accent-text); }
  :global([data-theme='dark']) .wordmark { display: none; }
  :global([data-theme='dark']) .sidebar:not(.rail) .dark-wordmark { display: inline; }
  @media (max-width: 1000px) { :global([data-theme='dark']) .sidebar:not(.rail) .dark-wordmark { display: none; } }
  .rail .brand { justify-content: center; padding: 0; }
  .rail .wordmark { display: none; }
  .rail .brand::before { content: ''; width: 28px; height: 28px; border-radius: 8px; background: var(--accent); mask: url('/images/pomi.png') center / contain no-repeat; }
  nav { display: grid; gap: var(--space-1); }
  .nav {
    display: flex; align-items: center; gap: var(--space-3); min-height: 44px; padding: 0 var(--space-3);
    border: 0; border-radius: var(--radius-md); background: transparent; color: var(--text-secondary);
    font-size: var(--text-md); font-weight: 600; text-align: start;
    transition: background-color 120ms var(--ease), color 120ms var(--ease);
  }
  .nav.active { background: var(--accent-soft); color: var(--accent-soft-text); }
  .rail .nav { justify-content: center; padding: 0; }
  .rail .label { display: none; }
  @media (hover: hover) { .nav:not(.active):hover { background: var(--bg-hover); color: var(--text); } }
  .foot { margin-top: auto; display: grid; gap: var(--space-3); }
  .state { display: flex; align-items: center; gap: var(--space-3); padding: var(--space-3); border-radius: var(--radius-lg); background: var(--bg-sunken); }
  .pomi { width: 44px; height: 44px; object-fit: contain; flex: none; }
  .text { display: grid; grid-template-columns: auto 1fr; column-gap: var(--space-2); align-items: center; min-width: 0; font-size: var(--text-sm); font-weight: 600; }
  .status-text { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .sub { grid-column: 2; font-weight: 400; color: var(--text-secondary); font-size: var(--text-xs); }
  .dot { width: 8px; height: 8px; border-radius: var(--radius-full); background: var(--success-solid); }
  .dot.busy { background: var(--accent); animation: pulse 1.4s ease-in-out infinite; }
  @keyframes pulse { 50% { opacity: 0.35; } }
  .rail .state { justify-content: center; padding: var(--space-2); }
  .rail .text, .rail .pomi { display: none; }
  .rail .state::before { content: ''; width: 10px; height: 10px; border-radius: 50%; background: var(--success-solid); }
  .collapse { justify-self: start; }
  .rail .collapse { justify-self: center; }
  @media (max-width: 1000px) { .sidebar { width: var(--sidebar-rail); padding-inline: var(--space-3); } .sidebar .label, .sidebar .wordmark, .sidebar .text, .sidebar .pomi, .sidebar .collapse { display: none; } .sidebar .nav { justify-content: center; padding: 0; } .sidebar .brand { justify-content: center; padding: 0; } .sidebar .brand::before { content: ''; width: 28px; height: 28px; border-radius: 8px; background: var(--accent); mask: url('/images/pomi.png') center / contain no-repeat; } .sidebar .state { justify-content: center; } .sidebar .state::before { content: ''; width: 10px; height: 10px; border-radius: 50%; background: var(--success-solid); } }
</style>
