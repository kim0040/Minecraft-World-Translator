<script lang="ts">
  import { tick } from 'svelte';
  import { app } from '../lib/app.svelte';
  import type { Candidate } from '../lib/api';
  import type { SortMode, StateFilter } from '../lib/candidates.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import { formatNumber } from '../lib/format';
  import CandidateTable from '../components/CandidateTable.svelte';
  import CandidateDetail from '../components/CandidateDetail.svelte';
  import Dialog from '../components/Dialog.svelte';
  import Icon from '../components/Icon.svelte';

  const source = app.candidates;
  let selected = $state<Candidate | null>(null);
  let wide = $state(true);
  let busyBulk = $state(false);
  let query = $state(source.query);

  $effect(() => {
    const media = matchMedia('(min-width: 1100px)');
    wide = media.matches;
    const listener = async () => {
      const focus = document.activeElement;
      const editing = focus instanceof HTMLElement && focus.id === 'manual-translation';
      const inDetail = focus instanceof HTMLElement && !!focus.closest('.detail, dialog');
      wide = media.matches;
      await tick();
      if (editing) document.getElementById('manual-translation')?.focus();
      else if (inDetail && wide) document.querySelector<HTMLElement>('tr[aria-selected="true"]')?.focus();
    };
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  });

  // Changes to who is included only change what a state filter shows. Reload it after a pause.
  $effect(() => {
    void app.excluded.size;
    void Object.keys(app.overrides).length;
    if (source.state !== 'all') source.refetchSoon(350);
    void app.loadEstimate();
  });

  const states: { value: StateFilter; key: MessageKey }[] = [
    { value: 'all', key: 'review.state.all' },
    { value: 'included', key: 'review.state.included' },
    { value: 'excluded', key: 'review.state.excluded' },
    { value: 'manual', key: 'review.state.manual' }
  ];
  const kindEntries = $derived(Object.entries(source.kinds).sort((a, b) => b[1] - a[1]));

  function setQuery(value: string): void {
    query = value;
    source.query = value;
    source.refetchSoon();
  }
  function setKind(kind: string): void {
    source.kind = source.kind === kind ? '' : kind;
    source.reset();
  }
  function setState(value: StateFilter): void {
    source.state = value;
    source.reset();
  }
  function setSort(value: SortMode): void {
    source.sort = value;
    source.reset();
  }
  function clearFilters(): void {
    query = '';
    source.query = '';
    source.kind = '';
    source.state = 'all';
    source.reset();
  }
  async function bulk(include: boolean): Promise<void> {
    busyBulk = true;
    try {
      for (const id of await source.allIds()) app.setIncluded(id, include);
    } catch (cause) {
      app.fail(cause);
    } finally {
      busyBulk = false;
    }
  }
</script>

<div class="review">
  <header class="head">
    <div class="titles">
      <h1>{t('review.title')}</h1>
      <p class="lead">{t('review.lead')}</p>
    </div>
    <div class="counts" role="status" aria-live="polite">
      <span class="pill pill-success num">{t('review.included', { count: formatNumber(app.includedCount, app.locale) })}</span>
      <span class="pill num">{t('review.excluded', { count: formatNumber(app.excluded.size, app.locale) })}</span>
      <span class="pill pill-accent num">{t('review.manual', { count: formatNumber(app.manualCount, app.locale) })}</span>
    </div>
  </header>

  <div class="toolbar">
    <div class="search">
      <Icon name="search" size={15} />
      <input
        id="review-search"
        class="input"
        type="search"
        value={query}
        placeholder={t('review.search')}
        aria-label={t('review.searchLabel')}
        oninput={(event) => setQuery(event.currentTarget.value)}
      />
    </div>
    <div class="segmented" role="group" aria-label={t('review.state')}>
      {#each states as item (item.value)}
        <button type="button" aria-pressed={source.state === item.value} onclick={() => setState(item.value)}>{t(item.key)}</button>
      {/each}
    </div>
    <label class="sort">
      <span class="sr-only">{t('review.sort')}</span>
      <select class="select" value={source.sort} onchange={(event) => setSort(event.currentTarget.value as SortMode)}>
        <option value="order">{t('review.sort')}: {t('review.sort.order')}</option>
        <option value="source">{t('review.sort')}: {t('review.sort.source')}</option>
        <option value="count">{t('review.sort')}: {t('review.sort.count')}</option>
        <option value="kind">{t('review.sort')}: {t('review.sort.kind')}</option>
      </select>
    </label>
  </div>

  <div class="chips" role="group" aria-label={t('scan.summary.kinds')}>
    <button type="button" class="chip" aria-pressed={!source.kind} onclick={() => setKind('')}>
      {t('review.allKinds')}
    </button>
    {#each kindEntries as [kind, count] (kind)}
      <button type="button" class="chip" aria-pressed={source.kind === kind} onclick={() => setKind(kind)}>
        {t(`kind.${kind}` as MessageKey)} <span class="num n">{formatNumber(count, app.locale)}</span>
      </button>
    {/each}
  </div>

  <div class="workarea" class:wide>
    <div class="tablewrap"><CandidateTable selectedId={selected?.id ?? ''} onSelect={(candidate) => (selected = candidate)} /></div>
    {#if wide}<div class="detailwrap"><CandidateDetail candidate={selected} /></div>{/if}
  </div>

  <footer class="foot">
    <div class="meta">
      <span class="num muted">{t('review.rows', { total: formatNumber(source.total, app.locale) })}</span>
      {#if source.filtered}<button type="button" class="btn btn-quiet btn-sm" onclick={clearFilters}>{t('review.clearFilters')}</button>{/if}
      <button type="button" class="btn btn-secondary btn-sm" disabled={busyBulk || source.total === 0} onclick={() => bulk(false)}>{t('review.excludeVisible')}</button>
      <button type="button" class="btn btn-secondary btn-sm" disabled={busyBulk || source.total === 0} onclick={() => bulk(true)}>{t('review.includeVisible')}</button>
      <span class="hint">{t('review.bulkNote', { count: formatNumber(source.total, app.locale) })}</span>
    </div>
    <div class="next">
      {#if app.includedCount === 0}<span class="hint" role="alert">{t('review.nothingIncluded')}</span>{/if}
      <button type="button" class="btn btn-primary btn-lg" disabled={app.includedCount === 0} onclick={() => app.goStep('run')}>
        {t('review.toRun')} <Icon name="chevron-right" size={16} />
      </button>
    </div>
  </footer>
</div>

{#if !wide && selected}
  <Dialog title={t('review.detail.title')} onClose={() => (selected = null)}>
    <CandidateDetail candidate={selected} showHeading={false} />
    {#snippet actions()}<button type="button" class="btn btn-primary" onclick={() => (selected = null)}>{t('common.close')}</button>{/snippet}
  </Dialog>
{/if}

<style>
  .review { animation: pomi-enter var(--dur-base) var(--ease-out) backwards; display: grid; grid-template-rows: auto auto auto minmax(0, 1fr) auto; gap: var(--space-3); height: 100%; min-height: 460px; }
  .head { display: flex; align-items: flex-end; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; }
  h1 { font-size: var(--text-2xl); }
  .lead { color: var(--text-secondary); margin-top: var(--space-1); }
  .counts { display: flex; gap: var(--space-2); flex-wrap: wrap; }
  .toolbar { display: flex; gap: var(--space-3); align-items: center; flex-wrap: wrap; }
  .search { position: relative; flex: 1 1 260px; min-width: 200px; }
  .search :global(.icon) { position: absolute; inset-inline-start: 9px; top: 50%; translate: 0 -50%; color: var(--text-secondary); pointer-events: none; }
  .search .input { padding-inline-start: 32px; }
  .sort { flex: 0 0 auto; }
  .sort .select { width: auto; min-width: 200px; }
  .chips { display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .chip { display: inline-flex; align-items: center; gap: 6px; min-height: 26px; padding: 0 10px; border-radius: var(--radius-full); border: 1px solid var(--border-control); background: var(--bg-surface); color: var(--text); font-size: var(--text-sm); font-weight: 600; transition: background-color var(--dur-fast) var(--ease), border-color var(--dur-fast) var(--ease); }
  .chip .n { color: var(--text-secondary); font-weight: 500; }
  .chip[aria-pressed='true'] { background: var(--accent-soft); border-color: var(--accent); color: var(--accent-soft-text); }
  .chip[aria-pressed='true'] .n { color: inherit; }
  @media (hover: hover) { .chip[aria-pressed='false']:hover { background: var(--bg-hover); } }
  .workarea { display: grid; grid-template-columns: minmax(0, 1fr); gap: var(--space-3); min-height: 0; }
  .workarea.wide { grid-template-columns: minmax(0, 1fr) 340px; }
  .tablewrap, .detailwrap { min-height: 0; height: 100%; }
  .foot { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); flex-wrap: wrap; padding-top: var(--space-3); border-top: 1px solid var(--border); }
  .meta { display: flex; align-items: center; gap: var(--space-3); flex-wrap: wrap; }
  .next { display: flex; align-items: center; gap: var(--space-3); margin-inline-start: auto; }
  @media (max-width: 1100px) { .hint { display: none; } }
  @media (max-width: 640px), (max-height: 650px) {
    .review { height: auto; min-height: 0; grid-template-rows: auto auto auto minmax(300px, 1fr) auto; }
    .workarea { min-height: 300px; }
  }
</style>
