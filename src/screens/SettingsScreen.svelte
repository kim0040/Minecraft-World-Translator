<script lang="ts">
  import Dialog from '../components/Dialog.svelte';
  import Icon from '../components/Icon.svelte';
  import { app } from '../lib/app.svelte';
  import { credentialStored, type Settings } from '../lib/api';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';
  import type { ThemeChoice } from '../lib/theme';

  const providers = [
    { value: 'openai', label: 'OpenAI' },
    { value: 'gemini', label: 'Gemini' },
    { value: 'anthropic', label: 'Anthropic' },
    { value: 'openrouter', label: 'OpenRouter' },
    { value: 'custom', label: 'settings.provider.custom' as MessageKey }
  ];

  const styles = [
    { value: 'neutral', label: 'settings.style.neutral' as MessageKey },
    { value: 'casual', label: 'settings.style.casual' as MessageKey },
    { value: 'formal', label: 'settings.style.formal' as MessageKey },
    { value: 'polite', label: 'settings.style.polite' as MessageKey },
    { value: 'story', label: 'settings.style.story' as MessageKey },
    { value: 'custom', label: 'settings.style.custom' as MessageKey }
  ];

  const themes: { value: ThemeChoice; label: MessageKey }[] = [
    { value: 'system', label: 'settings.theme.system' },
    { value: 'light', label: 'settings.theme.light' },
    { value: 'dark', label: 'settings.theme.dark' }
  ];

  const providerDefaults: Record<string, { baseUrl: string; wireFormat: string }> = {
    openai: { baseUrl: 'https://api.openai.com/v1', wireFormat: 'openai' },
    gemini: { baseUrl: 'https://generativelanguage.googleapis.com/v1beta', wireFormat: 'gemini' },
    anthropic: { baseUrl: 'https://api.anthropic.com/v1', wireFormat: 'anthropic' },
    openrouter: { baseUrl: 'https://openrouter.ai/api/v1', wireFormat: 'openai' }
  };

  const copySettings = (value: Settings): Settings => ({
    ...value,
    provider: value.provider || 'openai',
    model: value.model ?? '',
    base_url: value.base_url ?? '',
    wire_format: value.wire_format || 'openai',
    target_language: value.target_language || '한국어',
    style_preset: value.style_preset || 'neutral',
    style_prompt: value.style_prompt ?? '',
    custom_system_prompt: value.custom_system_prompt ?? '',
    temperature: Number.isFinite(Number(value.temperature)) ? Number(value.temperature) : 0.3,
    batch_size: Number.isFinite(Number(value.batch_size)) ? Number(value.batch_size) : 40,
    request_timeout: Number.isFinite(Number(value.request_timeout)) ? Number(value.request_timeout) : 120,
    rpm_limit: Number.isFinite(Number(value.rpm_limit)) ? Number(value.rpm_limit) : 0,
    tpm_limit: Number.isFinite(Number(value.tpm_limit)) ? Number(value.tpm_limit) : 0,
    max_batch_retries: Number.isFinite(Number(value.max_batch_retries)) ? Number(value.max_batch_retries) : 3,
    concurrency: Number.isFinite(Number(value.concurrency)) ? Number(value.concurrency) : 4,
    resource_pack_enabled: !!value.resource_pack_enabled,
    skip_target_language_text: value.skip_target_language_text !== false,
    ui_language: value.ui_language || 'ko',
    last_world_dir: value.last_world_dir || ''
  });

  let draft = $state<Settings>(copySettings(app.settings));
  let snapshot = $state<Settings | null>(null);
  let apiKey = $state('');
  let showApiKey = $state(false);
  let showDeleteConfirm = $state(false);
  let credentialProvider = $state('');
  let credentialState = $state<boolean | null>(null);
  let credentialLoading = $state(false);

  // AppState is bootstrapped asynchronously. Capture the comparison copy only after that
  // happens, so the first save compares against persisted settings rather than defaults.
  $effect(() => {
    if (!app.ready || snapshot) return;
    draft = copySettings(app.settings);
    snapshot = copySettings(app.settings);
    credentialProvider = app.settings.provider;
    credentialState = app.apiKeyStored;
    void refreshCredential(app.settings.provider);
  });

  const isCustom = $derived(draft.provider === 'custom');
  const validBaseUrl = (value: string): boolean => {
    try {
      const parsed = new URL(value.trim());
      return (parsed.protocol === 'https:' || parsed.protocol === 'http:') && !!parsed.host;
    } catch {
      return false;
    }
  };
  const baseUrlInvalid = $derived(isCustom && !validBaseUrl(draft.base_url));
  const rangeInvalid = $derived.by(() => ({
    temperature: !inRange(draft.temperature, 0, 2),
    batch: !inRange(draft.batch_size, 1, 200),
    timeout: !inRange(draft.request_timeout, 5, 600),
    rpm: !inRange(draft.rpm_limit, 0, 10000),
    tpm: !inRange(draft.tpm_limit, 0, 10000000),
    retries: !inRange(draft.max_batch_retries, 0, 10),
    concurrency: !inRange(draft.concurrency, 1, 8)
  }));
  const hasRangeError = $derived(Object.values(rangeInvalid).some(Boolean));
  const hasBlockingError = $derived(hasRangeError || (isCustom && !validBaseUrl(draft.base_url)));
  const stored = $derived(credentialProvider === draft.provider ? credentialState : null);
  const providerName = (provider: string): string => {
    const item = providers.find((choice) => choice.value === provider);
    if (!item) return provider;
    return provider === 'custom' ? t('settings.provider.custom') : item.label;
  };

  function inRange(value: unknown, minimum: number, maximum: number): boolean {
    const number = Number(value);
    return Number.isFinite(number) && number >= minimum && number <= maximum;
  }

  async function refreshCredential(provider: string): Promise<void> {
    credentialProvider = provider;
    credentialState = null;
    credentialLoading = true;
    try {
      const value = await credentialStored(provider);
      if (credentialProvider === provider) {
        credentialState = value;
        // This is only a boolean status. The key itself is never read from the store.
        app.apiKeyStored = value;
      }
    } catch {
      if (credentialProvider === provider) credentialState = false;
    } finally {
      if (credentialProvider === provider) credentialLoading = false;
    }
  }

  function providerChanged(event: Event): void {
    draft.provider = (event.currentTarget as HTMLSelectElement).value;
    const defaults = providerDefaults[draft.provider];
    if (defaults) {
      // A custom endpoint can contain credentials controlled by a different operator. Never
      // carry it into a public provider selection where the field is hidden from the user.
      draft.base_url = defaults.baseUrl;
      draft.wire_format = defaults.wireFormat;
    } else if (draft.provider === 'custom' && providerDefaults[snapshot?.provider || '']) {
      draft.base_url = '';
      draft.wire_format = 'openai';
    }
    apiKey = '';
    showApiKey = false;
    app.models = [];
    void refreshCredential(draft.provider);
  }

  function applyDraft(): void {
    app.settings = copySettings(draft);
  }

  async function saveSettings(): Promise<boolean> {
    if (!snapshot || hasBlockingError) return false;

    const previous = copySettings(snapshot);
    applyDraft();
    const saved = await app.saveSettings(previous, apiKey);
    if (!saved) {
      app.settings = previous;
      return false;
    }

    draft = copySettings(app.settings);
    snapshot = copySettings(app.settings);
    apiKey = '';
    showApiKey = false;
    credentialProvider = app.settings.provider;
    credentialState = app.apiKeyStored;
    return true;
  }

  async function submit(event: SubmitEvent): Promise<void> {
    event.preventDefault();
    await saveSettings();
  }

  async function loadModels(): Promise<void> {
    if (hasBlockingError) return;
    if (!snapshot) return;

    // Persist the current draft first so a newly typed credential can be used by the model
    // listing request. loadModels itself persists again through the shared app service.
    const saved = await saveSettings();
    if (!saved) return;
    try {
      const count = await app.loadModels();
      app.notify(count ? t('settings.model.loaded', { count }) : t('settings.model.none'), count ? 'success' : 'info');
    } catch (cause) {
      app.fail(cause);
    }
  }

  async function deleteApiKey(): Promise<void> {
    showDeleteConfirm = false;
    // The singleton method intentionally receives only the provider. It never returns or
    // exposes the stored credential value.
    app.settings = copySettings(draft);
    await app.deleteApiKey();
    if (!app.apiKeyStored) {
      credentialProvider = draft.provider;
      credentialState = false;
      apiKey = '';
      showApiKey = false;
    }
  }

  function setTheme(event: Event): void {
    app.setTheme((event.currentTarget as HTMLSelectElement).value as ThemeChoice);
  }

  function rangeText(label: MessageKey, minimum: string, maximum: string): string {
    return `${t(label)}: ${minimum}–${maximum}`;
  }
</script>

<div class="page settings">
  <header class="page-head">
    <p class="eyebrow">PomiTranslate</p>
    <h1>{t('settings.title')}</h1>
    <p class="lead">{t('settings.lead')}</p>
  </header>

  <form class="settings-form" onsubmit={submit} novalidate>
    <section class="card settings-section" aria-labelledby="translation-title">
      <div class="section-head">
        <div class="section-icon" aria-hidden="true"><Icon name="language" size={20} /></div>
        <div><h2 id="translation-title">{t('settings.language.title')}</h2><p>{t('settings.style.extraPlaceholder')}</p></div>
      </div>
      <div class="fields two">
        <div class="field">
          <label class="label" for="target-language">{t('settings.language.target')}</label>
          <input id="target-language" class="input" type="text" bind:value={draft.target_language} autocomplete="off" aria-describedby="target-language-help" />
          <span id="target-language-help" class="hint">{t('settings.language.targetHelp')}</span>
        </div>
        <div class="field">
          <label class="label" for="style-preset">{t('settings.style.label')}</label>
          <select id="style-preset" class="select" bind:value={draft.style_preset}>
            {#each styles as style (style.value)}<option value={style.value}>{t(style.label)}</option>{/each}
          </select>
        </div>
        <div class="field full">
          <label class="label" for="style-prompt">{t('settings.style.extra')} <span class="optional">{t('common.optional')}</span></label>
          <textarea id="style-prompt" class="textarea" rows="3" bind:value={draft.style_prompt} placeholder={t('settings.style.extraPlaceholder')}></textarea>
        </div>
        {#if draft.style_preset === 'custom'}
          <div class="field full">
            <label class="label" for="custom-prompt">{t('settings.style.system')}</label>
            <textarea id="custom-prompt" class="textarea" rows="5" bind:value={draft.custom_system_prompt} placeholder={t('settings.style.system')}></textarea>
          </div>
        {/if}
      </div>
    </section>

    <section class="card settings-section" aria-labelledby="provider-title">
      <div class="section-head">
        <div class="section-icon" aria-hidden="true"><Icon name="shield" size={20} /></div>
        <div><h2 id="provider-title">{t('settings.provider.title')}</h2><p>{t('settings.apiKey.help')}</p></div>
      </div>
      <div class="fields two">
        <div class="field">
          <label class="label" for="provider">{t('settings.provider.label')}</label>
          <select id="provider" class="select" value={draft.provider} onchange={providerChanged}>
            {#each providers as provider (provider.value)}<option value={provider.value}>{providerName(provider.value)}</option>{/each}
          </select>
        </div>
        <div class="field">
          <label class="label" for="model">{t('settings.model.label')}</label>
          <input
            id="model"
            class="input"
            type="text"
            bind:value={draft.model}
            list="model-list"
            autocomplete="off"
            placeholder={t('settings.model.placeholder')}
          />
          {#if app.models.length}<span class="hint">{t('settings.model.loaded', { count: app.models.length })}</span>{/if}
          <datalist id="model-list">{#each app.models as model (model.id)}<option value={model.id}>{model.display_name || model.id}</option>{/each}</datalist>
        </div>
        {#if isCustom}
          <div class="field full">
            <label class="label" for="base-url">{t('settings.baseUrl.label')}</label>
            <input
              id="base-url"
              class="input"
              class:invalid={baseUrlInvalid}
              type="url"
              bind:value={draft.base_url}
              placeholder="https://example.com/v1"
              autocomplete="url"
              aria-invalid={baseUrlInvalid}
              aria-describedby={baseUrlInvalid ? 'base-url-error' : undefined}
            />
            {#if baseUrlInvalid}<span id="base-url-error" class="field-error" role="alert">{t('settings.baseUrl.label')}: https://example.com/v1</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="wire-format">{t('settings.wire.label')}</label>
            <select id="wire-format" class="select" bind:value={draft.wire_format}>
              <option value="openai">OpenAI Chat</option>
              <option value="anthropic">Anthropic Messages</option>
            </select>
          </div>
        {/if}
        <div class="field full credential-field">
          <div class="label-row">
            <label class="label" for="api-key">{t('settings.apiKey.label')}</label>
            {#if credentialLoading}<span class="hint" role="status">{t('common.loading')}</span>
            {:else if stored === true}<span class="pill pill-success"><Icon name="check" size={13} /> {t('settings.apiKey.stored')}</span>
            {:else if stored === false}<span class="pill">{t('settings.apiKey.missing')}</span>{/if}
          </div>
          <div class="secret-input">
            <input id="api-key" class="input" type={showApiKey ? 'text' : 'password'} bind:value={apiKey} autocomplete="new-password" placeholder={t('settings.apiKey.placeholder')} spellcheck="false" />
            <button type="button" class="btn btn-secondary btn-icon" aria-label={showApiKey ? t('settings.apiKey.hide') : t('settings.apiKey.show')} title={showApiKey ? t('settings.apiKey.hide') : t('settings.apiKey.show')} onclick={() => (showApiKey = !showApiKey)}>
              <Icon name={showApiKey ? 'eye-off' : 'eye'} size={18} />
            </button>
          </div>
          <span class="hint">{t('settings.apiKey.help')}</span>
        </div>
      </div>
      <div class="section-actions">
        <button type="button" class="btn btn-secondary" disabled={!!app.busy || hasBlockingError} onclick={loadModels}>
          <Icon name="refresh" size={17} /> {app.busy === 'models' ? t('settings.model.listing') : t('settings.model.list')}
        </button>
      </div>
    </section>

    <section class="card settings-section" aria-labelledby="scope-title">
      <div class="section-head">
        <div class="section-icon" aria-hidden="true"><Icon name="search" size={20} /></div>
        <div><h2 id="scope-title">{t('settings.scope.title')}</h2><p>{t('coverage.lead')}</p></div>
      </div>
      <div class="checks">
        <label class="check">
          <input type="checkbox" bind:checked={draft.resource_pack_enabled} />
          <span><strong>{t('settings.scope.pack')}</strong><small>{t('settings.scope.packHelp')}</small></span>
        </label>
        <label class="check">
          <input type="checkbox" bind:checked={draft.skip_target_language_text} />
          <span><strong>{t('settings.scope.skipTarget')}</strong><small>{t('settings.scope.skipTargetHelp')}</small></span>
        </label>
      </div>
    </section>

    <section class="card settings-section" aria-labelledby="performance-title">
        <details class="advanced">
        <summary>
          <span class="section-head compact">
            <span class="section-icon" aria-hidden="true"><Icon name="sliders" size={20} /></span>
            <span><strong id="performance-title">{t('settings.speed.title')}</strong><small>{t('settings.advanced')}</small></span>
          </span>
          <Icon name="chevron-down" size={18} />
        </summary>
        <div class="fields three">
          <div class="field">
            <label class="label" for="concurrency">{t('settings.speed.concurrency')}</label>
            <input id="concurrency" class="input" class:invalid={rangeInvalid.concurrency} type="number" min="1" max="8" step="1" bind:value={draft.concurrency} aria-invalid={rangeInvalid.concurrency} aria-describedby={rangeInvalid.concurrency ? 'concurrency-error' : 'concurrency-help'} />
            <span id="concurrency-help" class="hint">{t('settings.speed.concurrencyHelp')}</span>
            {#if rangeInvalid.concurrency}<span id="concurrency-error" class="field-error" role="alert">{rangeText('settings.speed.concurrency', '1', '8')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="batch-size">{t('settings.speed.batch')}</label>
            <input id="batch-size" class="input" class:invalid={rangeInvalid.batch} type="number" min="1" max="200" step="1" bind:value={draft.batch_size} aria-invalid={rangeInvalid.batch} aria-describedby={rangeInvalid.batch ? 'batch-error' : undefined} />
            {#if rangeInvalid.batch}<span id="batch-error" class="field-error" role="alert">{rangeText('settings.speed.batch', '1', '200')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="temperature">{t('settings.speed.temperature')}</label>
            <input id="temperature" class="input" class:invalid={rangeInvalid.temperature} type="number" min="0" max="2" step="0.1" bind:value={draft.temperature} aria-invalid={rangeInvalid.temperature} aria-describedby={rangeInvalid.temperature ? 'temperature-error' : undefined} />
            {#if rangeInvalid.temperature}<span id="temperature-error" class="field-error" role="alert">{rangeText('settings.speed.temperature', '0', '2')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="timeout">{t('settings.speed.timeout')}</label>
            <input id="timeout" class="input" class:invalid={rangeInvalid.timeout} type="number" min="5" max="600" step="1" bind:value={draft.request_timeout} aria-invalid={rangeInvalid.timeout} aria-describedby={rangeInvalid.timeout ? 'timeout-error' : undefined} />
            {#if rangeInvalid.timeout}<span id="timeout-error" class="field-error" role="alert">{rangeText('settings.speed.timeout', '5', '600')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="retries">{t('settings.speed.retries')}</label>
            <input id="retries" class="input" class:invalid={rangeInvalid.retries} type="number" min="0" max="10" step="1" bind:value={draft.max_batch_retries} aria-invalid={rangeInvalid.retries} aria-describedby={rangeInvalid.retries ? 'retries-error' : undefined} />
            {#if rangeInvalid.retries}<span id="retries-error" class="field-error" role="alert">{rangeText('settings.speed.retries', '0', '10')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="rpm">{t('settings.speed.rpm')}</label>
            <input id="rpm" class="input" class:invalid={rangeInvalid.rpm} type="number" min="0" max="10000" step="1" bind:value={draft.rpm_limit} aria-invalid={rangeInvalid.rpm} aria-describedby={rangeInvalid.rpm ? 'rpm-error' : 'rpm-help'} />
            <span id="rpm-help" class="hint">{t('settings.speed.limitHelp')}</span>
            {#if rangeInvalid.rpm}<span id="rpm-error" class="field-error" role="alert">{rangeText('settings.speed.rpm', '0', '10,000')}</span>{/if}
          </div>
          <div class="field">
            <label class="label" for="tpm">{t('settings.speed.tpm')}</label>
            <input id="tpm" class="input" class:invalid={rangeInvalid.tpm} type="number" min="0" max="10000000" step="100" bind:value={draft.tpm_limit} aria-invalid={rangeInvalid.tpm} aria-describedby={rangeInvalid.tpm ? 'tpm-error' : 'tpm-help'} />
            <span id="tpm-help" class="hint">{t('settings.speed.limitHelp')}</span>
            {#if rangeInvalid.tpm}<span id="tpm-error" class="field-error" role="alert">{rangeText('settings.speed.tpm', '0', '10,000,000')}</span>{/if}
          </div>
        </div>
      </details>
    </section>

    <section class="card settings-section" aria-labelledby="app-title">
      <div class="section-head">
        <div class="section-icon" aria-hidden="true"><Icon name="sliders" size={20} /></div>
        <div><h2 id="app-title">{t('settings.app.title')}</h2><p>{t('settings.app.theme')}</p></div>
      </div>
      <div class="fields two">
        <div class="field">
          <label class="label" for="ui-language">{t('settings.app.language')}</label>
          <select id="ui-language" class="select" bind:value={draft.ui_language}>
            <option value="ko">{t('lang.ko')}</option>
            <option value="en">{t('lang.en')}</option>
            <option value="ja">{t('lang.ja')}</option>
          </select>
        </div>
        <div class="field">
          <label class="label" for="theme">{t('settings.app.theme')}</label>
          <select id="theme" class="select" value={app.theme} onchange={setTheme}>
            {#each themes as theme (theme.value)}<option value={theme.value}>{t(theme.label)}</option>{/each}
          </select>
        </div>
      </div>
    </section>

    <footer class="actions">
      {#if stored === true}
        <button type="button" class="btn btn-danger" disabled={!!app.busy} onclick={() => (showDeleteConfirm = true)}><Icon name="trash" size={17} /> {t('settings.apiKey.delete')}</button>
      {/if}
      <span class="spacer"></span>
      <button type="submit" class="btn btn-primary btn-lg" disabled={!!app.busy || hasBlockingError}>
        <Icon name="check" size={18} /> {t('common.save')}
      </button>
    </footer>
  </form>
</div>

{#if showDeleteConfirm}
  <Dialog title={t('settings.apiKey.deleteTitle', { provider: providerName(draft.provider) })} onClose={() => (showDeleteConfirm = false)}>
    <p>{t('settings.apiKey.deleteBody')}</p>
    {#snippet actions()}
      <button type="button" class="btn btn-secondary" onclick={() => (showDeleteConfirm = false)}>{t('common.cancel')}</button>
      <button type="button" class="btn btn-danger-solid" onclick={deleteApiKey}>{t('settings.apiKey.delete')}</button>
    {/snippet}
  </Dialog>
{/if}

<style>
  .settings { max-width: 920px; }
  .settings-form { display: grid; gap: var(--space-4); }
  .settings-section { padding: var(--space-5); display: grid; gap: var(--space-5); }
  .section-head { display: flex; align-items: flex-start; gap: var(--space-3); min-width: 0; }
  .section-head h2 { font-size: var(--text-lg); }
  .section-head p { color: var(--text-secondary); font-size: var(--text-sm); margin-top: var(--space-1); }
  .section-icon { display: grid; place-items: center; flex: none; width: 36px; height: 36px; border-radius: var(--radius-md); background: var(--accent-soft); color: var(--accent-soft-text); }
  .fields { display: grid; gap: var(--space-4); min-width: 0; }
  .fields.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .fields.three { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .field { display: grid; gap: var(--space-2); min-width: 0; align-content: start; }
  .field.full { grid-column: 1 / -1; }
  .label { color: var(--text); font-size: var(--text-sm); font-weight: 700; }
  .label-row { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); flex-wrap: wrap; }
  .optional { color: var(--text-secondary); font-size: var(--text-xs); font-weight: 400; }
  .hint { color: var(--text-secondary); font-size: var(--text-xs); line-height: 1.45; }
  .input, .select, .textarea { min-width: 0; }
  .input.invalid { border-color: var(--danger-solid); box-shadow: 0 0 0 2px color-mix(in srgb, var(--danger-solid) 18%, transparent); }
  .field-error { color: var(--danger-text); font-size: var(--text-xs); line-height: 1.4; }
  .secret-input { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: var(--space-2); min-width: 0; }
  .secret-input .btn { min-height: 40px; }
  .credential-field { padding-top: var(--space-1); }
  .check { display: grid; grid-template-columns: auto minmax(0, 1fr); align-items: start; gap: var(--space-3); padding: var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-lg); cursor: pointer; }
  .check input { width: 20px; height: 20px; margin: 1px 0 0; accent-color: var(--accent); }
  .check span { display: grid; gap: var(--space-1); min-width: 0; }
  .check strong { font-size: var(--text-sm); }
  .check small { color: var(--text-secondary); font-size: var(--text-xs); font-weight: 400; }
  .checks { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--space-3); }
  .section-actions { display: flex; justify-content: flex-start; padding-top: var(--space-1); }
  .advanced { display: grid; gap: var(--space-5); }
  .advanced summary { display: flex; align-items: center; justify-content: space-between; gap: var(--space-4); cursor: pointer; list-style: none; }
  .advanced summary::-webkit-details-marker { display: none; }
  .advanced summary > .section-head { align-items: center; }
  .advanced summary strong { display: block; font-size: var(--text-lg); }
  .advanced summary small { display: block; color: var(--text-secondary); font-size: var(--text-sm); margin-top: 2px; }
  .advanced[open] summary > :global(.icon) { rotate: 180deg; }
  .actions { display: flex; align-items: center; flex-wrap: wrap; gap: var(--space-3); padding-top: var(--space-2); }
  .spacer { flex: 1; min-width: var(--space-3); }
  @media (max-width: 760px) {
    .fields.two, .fields.three, .checks { grid-template-columns: 1fr; }
    .field.full { grid-column: auto; }
    .settings-section { padding: var(--space-4); }
    .actions .btn-primary { width: 100%; }
  }
  @media (max-width: 420px) {
    .settings-section { padding-inline: var(--space-3); }
    .section-head { gap: var(--space-2); }
    .section-icon { width: 32px; height: 32px; }
    .actions { display: grid; grid-template-columns: 1fr; }
    .actions .spacer { display: none; }
    .actions .btn-danger, .actions .btn-primary { width: 100%; }
  }
  @media (min-width: 1500px) {
    .settings-form { grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; }
    .settings-form > .settings-section:first-child, .settings-form > .settings-section:nth-child(2) { grid-column: span 1; }
    .settings-form > .settings-section:nth-child(3), .settings-form > .settings-section:nth-child(4), .settings-form > .settings-section:nth-child(5), .settings-form > .actions { grid-column: 1 / -1; }
  }
</style>
