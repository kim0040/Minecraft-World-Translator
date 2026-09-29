<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import { baseName, formatDuration, formatNumber, formatCompact, formatUsd, middleEllipsis } from '../lib/format';
  import Icon from '../components/Icon.svelte';
  import Callout from '../components/Callout.svelte';
  import ProgressBar from '../components/ProgressBar.svelte';

  const providerLabels: Record<string, string> = { openai: 'OpenAI', gemini: 'Gemini', anthropic: 'Anthropic', openrouter: 'OpenRouter', custom: 'Custom' };
  const running = $derived(app.busy === 'translate');
  const estimate = $derived(app.estimate);
  const modelText = $derived(
    app.manualOnly ? t('run.manualOnly') : app.hasModel ? `${providerLabels[app.settings.provider] ?? app.settings.provider} · ${app.settings.model}` : t('run.noModel')
  );

  let now = $state(Date.now());
  $effect(() => {
    if (!running) return;
    const timer = setInterval(() => { now = Date.now(); }, 500);
    return () => clearInterval(timer);
  });

  const p = $derived(app.progress);
  const phases: { id: 'collect' | 'translate' | 'write'; key: MessageKey }[] = [
    { id: 'collect', key: 'run.phase.collect' },
    { id: 'translate', key: 'run.phase.translate' },
    { id: 'write', key: 'run.phase.write' }
  ];
  const order = { idle: -1, collect: 0, translate: 1, write: 2 } as const;
  const phaseIndex = $derived(order[p.phase]);
  const barValue = $derived(
    p.phase === 'translate' ? (p.total ? p.done : null) : p.fileTotal ? p.fileIndex : null
  );
  const barMax = $derived(p.phase === 'translate' ? p.total || 100 : p.fileTotal || 100);
  const detail = $derived(
    p.phase === 'translate'
      ? t('run.progress.translate', { done: formatNumber(p.done, app.locale), total: formatNumber(p.total, app.locale) })
      : p.phase === 'write'
        ? t('run.progress.write', { index: p.fileIndex, total: p.fileTotal })
        : p.fileTotal
          ? t('run.progress.collect', { index: p.fileIndex, total: p.fileTotal })
          : t('common.loading')
  );
  const costText = $derived.by(() => {
    if (!estimate || estimate.requests === 0) return t('run.cost.free');
    if (!estimate.cost) return t('run.cost.unknown');
    return t('run.cost.band', { low: formatUsd(estimate.cost.low, app.locale), high: formatUsd(estimate.cost.high, app.locale) });
  });
  const resumeText = $derived(
    app.resume
      ? (app.resume.status === 'cancelled'
          ? t('run.resumeInfoCancelled', { count: app.resume.translatedCount ?? 0 })
          : t('run.resumeInfo', { count: app.resume.translatedCount ?? 0 }))
      : ''
  );
</script>

<div class="page">
  {#if running}
    <header class="page-head">
      <h1>{t('run.busy')}</h1>
      <p class="lead">{t('run.busyHelp')}</p>
    </header>

    <section class="card live" aria-live="polite">
      <ol class="phases" aria-label={t('step.list')}>
        {#each phases as phase, index (phase.id)}
          <li class:done={phaseIndex > index} class:current={phaseIndex === index}>
            <span class="dot" aria-hidden="true">
              {#if phaseIndex > index}<Icon name="check" size={14} />{:else if phaseIndex === index}<span class="ping"></span>{:else}{index + 1}{/if}
            </span>
            <span>{t(phase.key)}</span>
          </li>
        {/each}
      </ol>

      <div class="bar">
        <ProgressBar label={detail} value={barValue} max={barMax} />
        <div class="line">
          <span class="num strong">{detail}</span>
          <span class="spacer"></span>
          <span class="num muted">{t('run.progress.elapsed', { time: formatDuration((now - p.startedAt) / 1000, app.locale) })}</span>
        </div>
      </div>

      <dl class="facts">
        {#if p.phase === 'translate'}
          <div><dt>{t('run.summary.requests')}</dt><dd class="num">{t('run.progress.requests', { done: p.requests, total: p.requestsEstimate || estimate?.requests || 0 })}</dd></div>
          <div><dt>{t('run.progress.failed', { count: '' }).trim()}</dt><dd class="num" class:bad={p.failed > 0}>{p.failed}</dd></div>
        {/if}
      </dl>

      {#if p.retry}
        <Callout tone="warning" title={t('run.progress.retry', { attempt: p.retry.attempt, max: p.retry.max })} role="status" />
      {/if}
      {#if app.closeBlocked}
        <Callout tone="info" title={t('run.closeBlocked')} role="status" />
      {/if}

      <div>
        <button type="button" class="btn btn-secondary" disabled={app.cancelling} onclick={() => app.cancel()}>
          <Icon name="stop" size={18} /> {app.cancelling ? t('run.cancelling') : t('run.cancel')}
        </button>
      </div>
    </section>
  {:else}
    <header class="page-head">
      <h1>{t('run.title')}</h1>
      <p class="lead">{t('run.lead')}</p>
    </header>

    {#if app.resume}
      <Callout tone="info" title={t('world.resumeFound')}>
        {resumeText}
        {#if app.resume.reason}<br /><strong>{t('run.resumeReason')}:</strong> {app.resume.reason}{/if}
      </Callout>
    {/if}

    {#if !app.hasModel && !app.manualOnly}
      <Callout tone="warning" title={t('run.noModel')} role="alert">
        {t('run.noModelHelp')}
        {#snippet actions()}<button type="button" class="btn btn-secondary btn-sm" onclick={() => app.goto('settings')}>{t('run.goSettings')}</button>{/snippet}
      </Callout>
    {/if}

    <section class="card summary" aria-labelledby="summary-title">
      <h2 id="summary-title" class="sr-only">{t('run.title')}</h2>
      <dl class="grid">
        <div><dt>{t('run.summary.world')}</dt><dd title={app.worldDir}>{baseName(app.worldDir)}<span class="sub mono">{middleEllipsis(app.worldDir, 44)}</span></dd></div>
        <div><dt>{t('run.summary.language')}</dt><dd>{app.settings.target_language}</dd></div>
        <div><dt>{t('run.summary.model')}</dt><dd class:warn={!app.hasModel && !app.manualOnly}>{modelText}</dd></div>
        <div><dt>{t('run.summary.texts')}</dt><dd class="num">{formatNumber(app.outgoingCount, app.locale)}</dd></div>
        <div><dt>{t('run.summary.manual')}</dt><dd class="num">{formatNumber(app.manualCount, app.locale)}</dd></div>
        <div><dt>{t('run.summary.requests')}</dt><dd class="num">{formatNumber(estimate?.requests ?? 0, app.locale)}</dd></div>
        <div class="wide">
          <dt>{t('run.summary.cost')}</dt>
          <dd class="num">{costText}
            {#if estimate && estimate.requests > 0}
              <span class="sub">{t('run.summary.tokens', { input: formatCompact(estimate.inputTokens, app.locale), output: formatCompact(estimate.outputTokens, app.locale) })}</span>
              <span class="sub">{estimate.cost ? t('run.cost.note') : t('run.cost.unknownWhy')}</span>
            {/if}
          </dd>
        </div>
        <div class="wide"><dt>{t('run.summary.backup')}</dt><dd><Icon name="shield" size={16} /> {t('run.summary.backupValue')}</dd></div>
      </dl>
    </section>

    <fieldset class="policy">
      <legend>{t('run.failurePolicy')}</legend>
      <label class="check"><input type="radio" name="policy" value="stop" bind:group={app.failurePolicy} /><span>{t('run.failure.stop')}</span></label>
      <label class="check"><input type="radio" name="policy" value="skip" bind:group={app.failurePolicy} /><span>{t('run.failure.skip')}</span></label>
    </fieldset>

    <p class="confirm muted">{t('run.confirm.body')}</p>

    <div class="cta">
      <button type="button" class="btn btn-primary btn-lg" disabled={!app.canRun} onclick={() => app.startTranslate({ resume: !!app.resume })}>
        <Icon name="play" size={18} /> {app.resume ? t('run.resume') : t('run.start')}
      </button>
      <button type="button" class="btn btn-secondary" disabled={app.isBusy} onclick={() => app.goStep('review')}>
        <Icon name="chevron-left" size={18} /> {t('step.review')}
      </button>
    </div>
  {/if}
</div>

<style>
  .live { padding: var(--space-5); display: grid; gap: var(--space-5); }
  .phases { display: flex; gap: var(--space-5); margin: 0; padding: 0; list-style: none; flex-wrap: wrap; }
  .phases li { display: flex; align-items: center; gap: var(--space-2); color: var(--text-secondary); font-weight: 600; }
  .phases li.current { color: var(--text); }
  .phases li.done { color: var(--success-text); }
  .dot { position: relative; display: grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; border: 1.5px solid var(--border-control); font-size: var(--text-xs); font-variant-numeric: tabular-nums; background: var(--bg-surface); }
  li.done .dot { background: var(--success-solid); border-color: var(--success-solid); color: #fff; }
  li.current .dot { border-color: var(--accent); }
  .ping { width: 10px; height: 10px; border-radius: 50%; background: var(--accent); animation: pulse 1.2s ease-in-out infinite; }
  @keyframes pulse { 50% { opacity: 0.3; scale: 0.8; } }
  .bar { display: grid; gap: var(--space-2); }
  .line { display: flex; align-items: baseline; gap: var(--space-3); }
  .strong { font-weight: 700; }
  .facts { display: flex; gap: var(--space-6); margin: 0; }
  .facts dt { font-size: var(--text-xs); color: var(--text-secondary); font-weight: 600; }
  .facts dd { margin: 0; font-size: var(--text-xl); font-weight: 700; }
  .bad { color: var(--danger-text); }
  .summary { padding: var(--space-5); }
  .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-5) var(--space-5); margin: 0; }
  .grid > div { min-width: 0; }
  .grid .wide { grid-column: span 3; padding-top: var(--space-4); border-top: 1px solid var(--border); }
  dt { font-size: var(--text-xs); font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-secondary); margin-bottom: var(--space-1); }
  dd { margin: 0; font-weight: 600; overflow-wrap: anywhere; }
  dd.warn { color: var(--warning-text); }
  .sub { display: block; font-weight: 400; font-size: var(--text-sm); color: var(--text-secondary); margin-top: 2px; }
  .policy { border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4); display: grid; gap: var(--space-3); background: var(--bg-surface); margin: 0; }
  .policy legend { padding: 0 var(--space-2); font-size: var(--text-sm); font-weight: 700; }
  .check span { font-weight: 500; }
  .check input[type='radio'] { width: 18px; height: 18px; }
  .confirm { font-size: var(--text-sm); max-width: 70ch; }
  .cta { display: flex; flex-wrap: wrap; gap: var(--space-3); align-items: center; }
  @media (max-width: 900px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .grid .wide { grid-column: span 2; } }
</style>
