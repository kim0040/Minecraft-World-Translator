<script lang="ts">
  let { value = null, max = 100, label }: { value?: number | null; max?: number; label: string } = $props();
  const percent = $derived(value === null || max <= 0 ? null : Math.max(0, Math.min(100, (value / max) * 100)));
</script>

<div
  class="bar"
  role="progressbar"
  aria-label={label}
  aria-valuemin="0"
  aria-valuemax="100"
  aria-valuenow={percent === null ? undefined : Math.round(percent)}
>
  <div class="fill" class:indeterminate={percent === null} style:width={percent === null ? undefined : `${percent}%`}></div>
</div>

<style>
  .bar { height: 10px; border-radius: var(--radius-full); background: var(--bg-sunken); overflow: hidden; border: 1px solid var(--border); }
  .fill { height: 100%; border-radius: var(--radius-full); background: var(--accent); transition: width 240ms var(--ease); }
  .indeterminate { width: 32%; animation: slide 1.3s var(--ease) infinite; }
  @keyframes slide { from { translate: -100% 0; } to { translate: 320% 0; } }
</style>
