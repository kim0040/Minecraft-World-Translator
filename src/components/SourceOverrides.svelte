<script lang="ts">
  import { validateSourceOverrides } from '../lib/settings-import';
  import { t } from '../lib/i18n/index.svelte';

  let { overrides = $bindable({}), invalid = $bindable(false) }: { overrides?: Record<string, string>; invalid?: boolean } = $props();
  let text = $state('');
  let expanded = $state(false);
  let lastSerialized = '';
  $effect(() => { if (invalid) expanded = true; });
  $effect(() => {
    const next = JSON.stringify(overrides, null, 2);
    if (next !== lastSerialized) { text = next; lastSerialized = next; invalid = false; }
  });
  function update(value: string): void {
    text = value;
    try {
      const parsed = validateSourceOverrides(JSON.parse(value || '{}'));
      lastSerialized = JSON.stringify(parsed, null, 2);
      overrides = parsed; invalid = false;
    }
    catch { invalid = true; }
  }
</script>

<details bind:open={expanded}>
  <summary>{t('settings.overrides.title')}</summary>
  <div class="field">
    <label for="source-overrides" class="label">{t('settings.overrides.label')}</label>
    <textarea id="source-overrides" class="textarea mono" rows="7" value={text} oninput={(event) => update(event.currentTarget.value)} aria-invalid={invalid} aria-describedby="source-overrides-help" spellcheck="false"></textarea>
    <p id="source-overrides-help" class="hint">{t('settings.overrides.help')}</p>
    <code>{'{"Shop": "상점"}'}</code>
    {#if invalid}<p class="field-error" role="alert">{t('settings.overrides.invalid')}</p>{/if}
  </div>
</details>

<style>
  summary { cursor: pointer; font-weight: 600; min-height: 32px; }
  .field { display: grid; gap: var(--space-2); padding-top: var(--space-3); }
  textarea { min-width: 0; width: 100%; resize: vertical; }
  code { overflow-wrap: anywhere; }
</style>
