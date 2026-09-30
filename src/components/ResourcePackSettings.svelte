<script lang="ts">
  import type { ResourcePackOptions } from '../lib/api';
  import { resourcePackOptions, validateResourcePackOptions } from '../lib/resource-pack';
  import { t } from '../lib/i18n/index.svelte';
  let { options = $bindable(resourcePackOptions()), invalid = $bindable(false) }: { options?: ResourcePackOptions; invalid?: boolean } = $props();
  let sources = $state(options.source_lang_files.join(', '));
  let target = $state(options.target_lang_file);
  let previous = JSON.stringify(options);
  $effect(() => {
    const signature = JSON.stringify(options);
    if (signature !== previous) {
      previous = signature;
      sources = options.source_lang_files.join(', ');
      target = options.target_lang_file;
      invalid = false;
    }
  });
  function update(event: Event, field: 'sources' | 'target'): void {
    const value = (event.currentTarget as HTMLInputElement).value;
    if (field === 'sources') sources = value;
    else target = value;
    try {
      options = validateResourcePackOptions({ ...options, source_lang_files: sources.split(',').map((value) => value.trim()), target_lang_file: target.trim() });
      previous = JSON.stringify(options);
      invalid = false;
    } catch { invalid = true; }
  }
</script>

<div class="pack-fields">
  <div class="field"><label class="label" for="pack-sources">{t('settings.pack.sources')}</label><input id="pack-sources" class="input" value={sources} oninput={(event) => update(event, 'sources')} aria-invalid={invalid} aria-describedby="pack-help" /></div>
  <div class="field"><label class="label" for="pack-target">{t('settings.pack.target')}</label><input id="pack-target" class="input" value={target} oninput={(event) => update(event, 'target')} aria-invalid={invalid} aria-describedby="pack-help" /></div>
  <p id="pack-help" class="hint full">{t('settings.pack.help')}</p>
  <label class="check full"><input type="checkbox" bind:checked={options.skip_if_target_exists} /><span>{t('settings.pack.skip')}</span></label>
  {#if invalid}<p class="field-error full" role="alert">{t('settings.pack.invalid')}</p>{/if}
  {#if !options.skip_if_target_exists}<p class="hint full">{t('settings.pack.overwrite')}</p>{/if}
</div>

<style>
  .pack-fields { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: var(--space-3); }
  .field { min-width: 0; display: grid; gap: var(--space-2); }
  .full { grid-column: 1 / -1; }
  .check { display: flex; align-items: start; gap: var(--space-2); }
  @media (max-width: 640px) { .pack-fields { grid-template-columns: minmax(0, 1fr); } }
</style>
