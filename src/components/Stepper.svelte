<script lang="ts">
  import { app, STEPS, type Step } from '../lib/app.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import Icon from './Icon.svelte';

  const order = $derived(STEPS.indexOf(app.step));
  const isDone = (step: Step) => STEPS.indexOf(step) < order && app.stepReached[step];
  const label = (step: Step) => t(`step.${step}` as MessageKey);
</script>

<nav class="stepper" aria-label={t('step.list')}>
  <ol>
    {#each STEPS as step, index (step)}
      {@const current = app.step === step}
      {@const reachable = app.stepReached[step] && !app.isBusy}
      <li class:current class:done={isDone(step)}>
        <button
          type="button"
          class="step"
          disabled={!reachable && !current}
          aria-current={current ? 'step' : undefined}
          onclick={() => app.goStep(step)}
        >
          <span class="marker" aria-hidden="true">
            {#if isDone(step)}<Icon name="check" size={14} />{:else}{index + 1}{/if}
          </span>
          <span class="name">{label(step)}</span>
          {#if isDone(step)}<span class="sr-only"> ({t('step.done')})</span>{/if}
          {#if current}<span class="sr-only"> ({t('step.current')})</span>{/if}
        </button>
      </li>
    {/each}
  </ol>
</nav>

<style>
  ol { display: flex; align-items: center; gap: 0; margin: 0; padding: 0; list-style: none; }
  li { display: flex; align-items: center; }
  li + li::before { content: ''; width: clamp(12px, 3vw, 36px); height: 2px; background: var(--border-strong); margin-inline: var(--space-1); border-radius: 2px; }
  li.done + li::before, li.current::before { background: var(--accent); }
  .step { display: inline-flex; align-items: center; gap: var(--space-2); min-height: 40px; padding: 0 var(--space-3) 0 var(--space-2); border: 0; background: transparent; border-radius: var(--radius-full); color: var(--text-secondary); font-weight: 600; font-size: var(--text-sm); transition: background-color 120ms var(--ease), color 120ms var(--ease); }
  .step:disabled { cursor: default; opacity: 0.6; }
  .marker { display: grid; place-items: center; width: 24px; height: 24px; border-radius: 50%; font-size: var(--text-xs); font-weight: 700; border: 1.5px solid var(--border-control); color: var(--text-secondary); background: var(--bg-surface); font-variant-numeric: tabular-nums; }
  li.done .marker { background: var(--accent); border-color: var(--accent); color: var(--text-on-accent); }
  li.current .marker { border-color: var(--accent); color: var(--accent-text); box-shadow: 0 0 0 3px var(--accent-soft); }
  li.current .step { color: var(--text); }
  @media (hover: hover) { .step:not(:disabled):hover { background: var(--bg-hover); color: var(--text); } }
  @media (max-width: 1080px) { li:not(.current) .name { display: none; } li:not(.current) .step { padding-inline: var(--space-1); } }
</style>
