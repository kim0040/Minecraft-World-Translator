<script lang="ts">
  import type { Snippet } from 'svelte';
  import Icon, { type IconName } from './Icon.svelte';

  let {
    tone = 'info',
    title,
    children,
    actions,
    role
  }: { tone?: 'info' | 'success' | 'warning' | 'danger'; title: string; children?: Snippet; actions?: Snippet; role?: 'alert' | 'status' } = $props();

  const icons: Record<string, IconName> = { info: 'info', success: 'check-circle', warning: 'alert-triangle', danger: 'alert-circle' };
</script>

<div class="callout callout-{tone}" {role}>
  <span class="callout-icon"><Icon name={icons[tone]} size={20} /></span>
  <div class="inner">
    <div class="callout-title">{title}</div>
    {#if children}<div class="callout-body">{@render children()}</div>{/if}
    {#if actions}<div class="acts">{@render actions()}</div>{/if}
  </div>
</div>

<style>
  .inner { min-width: 0; }
  .acts { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-top: var(--space-3); }
</style>
