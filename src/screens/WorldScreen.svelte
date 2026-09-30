<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import { baseName, formatDate, middleEllipsis } from '../lib/format';
  import Icon from '../components/Icon.svelte';
  import Callout from '../components/Callout.svelte';

  const dimensions = $derived.by(() => {
    const dirs = app.inspection?.regionDirs ?? [];
    const found = new Set<string>();
    for (const dir of dirs) {
      if (/^DIM-1\//.test(dir)) found.add('nether');
      else if (/^DIM1\//.test(dir)) found.add('end');
      else if (/^(region|entities)$/.test(dir)) found.add('overworld');
      else found.add('other');
    }
    return ['overworld', 'nether', 'end', 'other'].filter((name) => found.has(name));
  });
  const dataVersion = $derived(app.inspection?.dataVersions?.find((item) => item.dataVersion)?.dataVersion ?? null);
  const blockers = $derived(app.inspection?.writeBlockers ?? []);
  const blockerText = (code: string) => {
    const key = `world.blocked.${code}` as MessageKey;
    try { return t(key); } catch { return t('world.blocked.unknown'); }
  };
  const knownBlockers = ['bedrock', 'mcr', 'linear', 'world_in_use', 'not_writable', 'not_readable', 'missing', 'unsafe_path'];
  const name = $derived(app.worldDir ? baseName(app.worldDir) : '');
  const kind = $derived((app.inspection?.kind ?? 'unknown') as 'java_world' | 'server_root' | 'unknown');
</script>

<div class="page">
  <header class="page-head">
    <h1>{t('world.title')}</h1>
    <p class="lead">{t('world.lead')}</p>
  </header>

  {#if app.worldDir && app.inspection?.validJavaWorld}
    <section class="card selected" aria-labelledby="selected-title">
      <div class="head">
        <div class="thumb" aria-hidden="true"><Icon name="folder" size={28} /></div>
        <div class="who">
          <p class="eyebrow" id="selected-title">{t('world.selected')}</p>
          <h2 class="name">{name}</h2>
          <p class="path mono truncate" title={app.worldDir}>{middleEllipsis(app.worldDir, 72)}</p>
        </div>
      </div>

      <ul class="facts">
        <li><span class="pill pill-accent">{t(`world.kind.${kind}` as MessageKey)}</span></li>
        {#each dimensions as dim (dim)}<li><span class="pill">{t(`world.dim.${dim}` as MessageKey)}</span></li>{/each}
        {#if app.inspection?.resourcePacks?.length}<li><span class="pill">{t('world.resourcePack')}</span></li>{/if}
        <li><span class="pill">{t('world.backupsCount', { count: app.backups.length })}</span></li>
        {#if dataVersion}<li><span class="pill num">{t('world.gameData', { version: dataVersion })}</span></li>{/if}
      </ul>

      {#if blockers.length}
        <Callout tone="danger" title={t('scan.blocked')} role="alert">
          <ul class="plain">
            {#each blockers as code (code)}<li>{knownBlockers.includes(code) ? blockerText(code) : t('world.blocked.unknown')}</li>{/each}
          </ul>
        </Callout>
      {/if}

      {#if app.resume}
        <Callout tone="info" title={t('world.resumeFound')}>
          {app.resume.status === 'cancelled'
            ? t('run.resumeInfoCancelled', { count: app.resume.translatedCount ?? 0 })
            : t('run.resumeInfo', { count: app.resume.translatedCount ?? 0 })}
          {#snippet actions()}
            <button type="button" class="btn btn-secondary btn-sm" onclick={() => app.goStep('run')}>{t('run.resume')}</button>
          {/snippet}
        </Callout>
      {/if}

      <div class="cta">
        <button type="button" class="btn btn-primary btn-lg" disabled={blockers.length > 0} onclick={() => app.goStep('scan')}>
          {t('world.continue')} <Icon name="chevron-right" size={20} />
        </button>
        <button type="button" class="btn btn-secondary" disabled={app.isBusy} onclick={() => app.chooseWorld()}>
          <Icon name="folder" size={18} /> {t('world.open')}
        </button>
      </div>
    </section>
  {:else}
    <section class="card empty">
      <div class="art" aria-hidden="true"><img src="/images/pomi.png" alt="" width="96" height="96" /></div>
      <div class="copy">
        <h2>{t('world.open')}</h2>
        <p class="muted">{t('world.openHint')}</p>
      </div>
      <button type="button" class="btn btn-primary btn-lg" onclick={() => app.chooseWorld()}>
        <Icon name="folder" size={20} /> {t('world.open')}
      </button>
    </section>
  {/if}

  <section class="recent" aria-labelledby="recent-title">
    <h2 id="recent-title" class="section-title">{t('world.recent')}</h2>
    {#if app.recent.length === 0}
      <p class="muted">{t('world.recentEmpty')}</p>
    {:else}
      <ul class="worlds">
        {#each app.recent as world (world.path)}
          <li class="world" class:current={world.path === app.worldDir}>
            <button
              type="button"
              class="open"
              disabled={!world.available || app.isBusy}
              aria-current={world.path === app.worldDir ? 'true' : undefined}
              onclick={() => app.useWorld(world.path)}
            >
              <span class="ico" aria-hidden="true"><Icon name="folder" size={20} /></span>
              <span class="txt">
                <span class="n">{world.name || baseName(world.path)}</span>
                {#if world.path !== app.worldDir}<span class="p mono truncate" title={world.path}>{middleEllipsis(world.path, 64)}</span>{/if}
              </span>
              <span class="meta">
                {#if !world.available}<span class="pill pill-warning">{t('world.missing')}</span>
                {:else if world.lastOpened}<span class="when">{formatDate(world.lastOpened, app.locale)}</span>{/if}
              </span>
            </button>
            <button type="button" class="btn btn-quiet btn-icon btn-sm" disabled={app.isBusy} aria-label={t('world.forgetNamed', { name: world.name || baseName(world.path) })} title={t('world.forget')} onclick={() => app.forgetWorld(world.path)}>
              <Icon name="x" size={16} />
            </button>
          </li>
        {/each}
      </ul>
    {/if}
  </section>
</div>

<style>
  .selected { padding: var(--space-5); display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-4); }
  .head { display: flex; gap: var(--space-4); align-items: center; min-width: 0; }
  .thumb { flex: none; display: grid; place-items: center; width: 56px; height: 56px; border-radius: var(--radius-lg); background: var(--accent-soft); color: var(--accent-soft-text); }
  .who { min-width: 0; }
  .name { font-size: var(--text-xl); margin-top: 2px; overflow-wrap: anywhere; }
  .path { font-size: var(--text-sm); color: var(--text-secondary); margin-top: 2px; }
  .facts { display: flex; flex-wrap: wrap; gap: var(--space-2); margin: 0; padding: 0; list-style: none; }
  .plain { margin: 0; padding-inline-start: 18px; }
  .cta { display: flex; flex-wrap: wrap; gap: var(--space-3); padding-top: var(--space-2); border-top: 1px solid var(--border); margin-top: var(--space-1); padding-top: var(--space-4); }
  .empty { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: var(--space-5); padding: var(--space-6) var(--space-5); border-style: dashed; border-color: var(--border-strong); box-shadow: none; }
  .art img { width: 96px; height: 96px; object-fit: contain; }
  .copy h2 { font-size: var(--text-xl); }
  .copy p { margin-top: var(--space-1); }
  .section-title { font-size: var(--text-lg); margin-bottom: var(--space-3); }
  .worlds { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-2); min-width: 0; }
  .world { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: var(--space-2); min-width: 0; }
  .open { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: var(--space-3); min-height: 56px; padding: var(--space-2) var(--space-4) var(--space-2) var(--space-3);
    min-width: 0; width: 100%; text-align: start; background: var(--bg-surface); border: 1px solid var(--border); border-radius: var(--radius-lg); transition: border-color 120ms var(--ease), background-color 120ms var(--ease); }
  .world.current .open { border-color: var(--accent); background: var(--bg-selected); }
  .open:disabled { opacity: 0.6; }
  .ico { display: grid; place-items: center; width: 36px; height: 36px; border-radius: var(--radius-md); background: var(--bg-sunken); color: var(--text-secondary); }
  .txt { display: grid; min-width: 0; }
  .n { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .p { font-size: var(--text-xs); color: var(--text-secondary); }
  .when { font-size: var(--text-xs); color: var(--text-secondary); white-space: nowrap; }
  @media (hover: hover) { .open:not(:disabled):hover { border-color: var(--border-control); } }
  @media (max-width: 760px) { .empty { grid-template-columns: 1fr; justify-items: start; } .meta { display: none; } }
  @media (max-width: 420px) {
    .selected { padding: var(--space-4); }
    .head { align-items: flex-start; gap: var(--space-3); }
    .thumb { width: 48px; height: 48px; }
    .cta .btn { width: 100%; }
    .open { padding-inline: var(--space-2); gap: var(--space-2); }
  }
</style>
