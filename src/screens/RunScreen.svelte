<script lang="ts">
  import { app } from '../lib/app.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import { baseName, formatDuration, formatNumber, formatCompact, formatUsd, middleEllipsis } from '../lib/format';
  import Icon from '../components/Icon.svelte';
  import Callout from '../components/Callout.svelte';
  import ProgressBar from '../components/ProgressBar.svelte';
  import SetupNotice from '../components/SetupNotice.svelte';
  import { REASONING_PROVIDERS, reasoningSummary } from '../lib/reasoning';

  const providerLabels: Record<string, string> = { openai: 'OpenAI', gemini: 'Gemini', anthropic: 'Anthropic', openrouter: 'OpenRouter', comet: 'Comet API', custom: 'Custom' };
  const running = $derived(app.busy === 'translate');
  const reasoningModel = $derived(app.modelsFor(app.settings).find((model) => model.id === app.settings.model.trim()));
  const reasoning = $derived(reasoningSummary(app.settings.openrouter_reasoning ?? 'default', reasoningModel));
  let attemptedMetadata = false;
  $effect(() => {
    if (app.settings.provider !== 'openrouter' || app.manualOnly || app.busy || attemptedMetadata) return;
    const timer = setTimeout(() => {
      attemptedMetadata = true;
      void app.loadModels().catch(() => {}); // The summary explicitly keeps unknown metadata unknown.
    }, 0);
    return () => clearTimeout(timer);
  });
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
    if (app.manualOnly || estimate?.requests === 0) return t('run.cost.free');
    if (!estimate) return app.estimateLoading ? t('run.cost.calculating') : t('run.cost.unknown');
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

      <!-- Always laid out, so the cancel button does not move when translation starts. -->
      <dl class="facts">
        <div><dt>{t('run.progress.requestsLabel')}</dt><dd class="num">{p.phase === 'translate' ? t('run.progress.requests', { done: p.requests, total: p.requestsEstimate || estimate?.requests || 0 }) : '–'}</dd></div>
        <div><dt>{t('result.stat.failed')}</dt><dd class="num" class:bad={p.failed > 0}>{p.phase === 'translate' ? p.failed : '–'}</dd></div>
      </dl>

      {#if p.retry}
        <Callout tone="warning" title={t('run.progress.retry', { attempt: p.retry.attempt, max: p.retry.max })} role="status" />
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

    {#if !app.manualOnly}<SetupNotice blocking />{/if}

    <section aria-labelledby="summary-title">
      <h2 id="summary-title" class="group-title">{t('run.summaryTitle')}</h2>
      <dl class="group">
        <div class="row-item"><dt class="k">{t('run.summary.world')}</dt><dd class="v" title={app.worldDir}>{baseName(app.worldDir)}<span class="sub mono">{middleEllipsis(app.worldDir, 56)}</span></dd></div>
        <div class="row-item"><dt class="k">{t('run.summary.language')}</dt><dd class="v">{app.settings.target_language}</dd></div>
        <div class="row-item"><dt class="k">{t('run.summary.model')}</dt><dd class="v" class:warn={!app.hasModel && !app.manualOnly}>{modelText}</dd></div>
        {#if REASONING_PROVIDERS.includes(app.settings.provider) && !app.manualOnly}
          <div class="row-item"><dt class="k">{t('settings.reasoning.label')}</dt><dd class="v inline"><span class="text">{reasoning}</span><button type="button" class="btn btn-quiet btn-sm edit-settings" disabled={!!app.busy} onclick={() => app.openSettingsFor('run')}>{t('run.reasoning.edit')}</button></dd></div>
        {/if}
      </dl>
    </section>

    <section aria-labelledby="work-title">
      <h2 id="work-title" class="group-title">{t('run.workTitle')}</h2>
      <dl class="group">
        <div class="row-item"><dt class="k">{t('run.summary.texts')}</dt><dd class="v num">{formatNumber(app.outgoingCount, app.locale)}</dd></div>
        <div class="row-item"><dt class="k">{t('run.summary.manual')}</dt><dd class="v num">{formatNumber(app.manualCount, app.locale)}</dd></div>
        <div class="row-item"><dt class="k">{t('run.summary.requests')}</dt><dd class="v num">{app.manualOnly ? '0' : estimate ? formatNumber(estimate.requests, app.locale) : app.estimateLoading ? t('run.cost.calculating') : t('common.unknown')}</dd></div>
        <div class="row-item">
          <dt class="k">{t('run.summary.cost')}</dt>
          <dd class="v num">{costText}
            <!-- While a new estimate is on its way its lines keep their place, so nothing below jumps. -->
            {#if (estimate && estimate.requests > 0) || (!estimate && app.estimateLoading && !app.manualOnly)}
              <span class="sub">{estimate ? t('run.summary.tokens', { input: formatCompact(estimate.inputTokens, app.locale), output: formatCompact(estimate.outputTokens, app.locale) }) : '\u00a0'}</span>
              <span class="sub">{estimate ? (estimate.cost ? t('run.cost.note') : t('run.cost.unknownWhy')) : '\u00a0'}</span>
              {#if REASONING_PROVIDERS.includes(app.settings.provider) && app.settings.openrouter_reasoning !== 'disabled'}<span class="sub">{t('run.reasoning.cost')}</span>{/if}
            {/if}
          </dd>
        </div>
        <div class="row-item"><dt class="k">{t('run.summary.backup')}</dt><dd class="v backup"><Icon name="shield" size={14} /> {t('run.summary.backupValue')}</dd></div>
        {#if app.settings.resource_pack_enabled && app.settings.external_resource_pack_paths?.length}
          <div class="row-item"><dt class="k">{t('settings.pack.externalTitle')}</dt><dd class="v"><ul class="external-paths">{#each app.settings.external_resource_pack_paths as path}<li class="mono">{path}</li>{/each}</ul><span class="sub">{t('settings.pack.externalHelp')}</span></dd></div>
        {/if}
      </dl>
    </section>

    <fieldset class="group policy">
      <legend class="group-title">{t('run.failurePolicy')}</legend>
      <label class="row-item check"><input type="radio" name="policy" value="stop" bind:group={app.failurePolicy} /><span>{t('run.failure.stop')}</span></label>
      <label class="row-item check"><input type="radio" name="policy" value="skip" bind:group={app.failurePolicy} /><span>{t('run.failure.skip')}</span></label>
    </fieldset>

    <div class="action-bar">
      <p class="note">{t('run.confirm.body')}</p>
      <div class="buttons">
        <button type="button" class="btn btn-secondary btn-lg" disabled={app.isBusy} onclick={() => app.goStep('review')}>
          <Icon name="chevron-left" size={16} /> {t('step.review')}
        </button>
        <button type="button" class="btn btn-primary btn-lg" disabled={!app.canRun} onclick={() => app.startTranslate({ resume: !!app.resume })}>
          <Icon name="play" size={16} /> {app.resume ? t('run.resume') : t('run.start')}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .external-paths { padding-inline-start: 1em; margin: 0; overflow-wrap: anywhere; }
  /* The edit button keeps its line when the summary text changes length, so the rows below stay put. */
  .inline { display: flex; align-items: center; gap: var(--space-2); }
  .inline > .text { flex: 1 1 auto; min-width: 0; }
  .edit-settings { flex: none; }
  .live { padding: var(--space-5); display: grid; gap: var(--space-5); }
  .phases { display: flex; gap: var(--space-5); margin: 0; padding: 0; list-style: none; flex-wrap: wrap; }
  .phases li { display: flex; align-items: center; gap: var(--space-2); color: var(--text-secondary); font-weight: 600; }
  .phases li.current { color: var(--text); }
  .phases li.done { color: var(--success-text); }
  .dot { position: relative; display: grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; border: 1.5px solid var(--border-control); font-size: var(--text-xs); font-variant-numeric: tabular-nums; background: var(--bg-surface); }
  li.done .dot { background: var(--success-solid); border-color: var(--success-solid); color: #fff; }
  li.current .dot { border-color: var(--accent); }
  .ping { width: 8px; height: 8px; border-radius: 50%; background: var(--accent); animation: pomi-pulse 1.2s ease-in-out infinite; }
  @keyframes pomi-pulse { 50% { opacity: 0.3; scale: 0.8; } }
  .bar { display: grid; gap: var(--space-2); }
  .line { display: flex; align-items: baseline; gap: var(--space-3); }
  .strong { font-weight: 700; }
  .facts { display: flex; gap: var(--space-6); margin: 0; }
  .facts dt { font-size: var(--text-sm); color: var(--text-secondary); font-weight: 500; }
  .facts dd { margin: 0; font-size: var(--text-xl); font-weight: 700; }
  .bad { color: var(--danger-text); }
  dd.warn { color: var(--warning-text); }
  .backup { display: flex; align-items: center; gap: 6px; }
  .backup :global(.icon) { color: var(--success-text); flex: none; }
  .sub { display: block; font-weight: 400; font-size: var(--text-sm); color: var(--text-secondary); margin-top: 2px; }
  .policy { min-width: 0; }
  .policy legend { float: left; width: 100%; padding: 10px var(--space-4) 0; margin: 0; }
  .policy legend + .row-item { clear: both; }
  .policy .row-item { display: flex; align-items: center; gap: var(--space-2); }
  .policy .row-item:first-of-type { border-top: 0; }
  .check span { font-weight: 500; }
  .check input[type='radio'] { width: 16px; height: 16px; margin: 0; }
</style>
