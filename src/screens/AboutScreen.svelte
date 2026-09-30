<script lang="ts">
  import Callout from '../components/Callout.svelte';
  import Icon from '../components/Icon.svelte';
  import { t, type MessageKey } from '../lib/i18n/index.svelte';

  // Keep this in sync with package.json and src-tauri/tauri.conf.json until the
  // app exposes a runtime version through a capability-safe API.
  const APP_VERSION = '0.1.0';
  const REPOSITORY_URL = 'https://github.com/kim0040/Minecraft-World-Translator';
  const LICENSE_URL = `${REPOSITORY_URL}/blob/main/LICENSE`;
  const SUPPORT_MATRIX_URL = `${REPOSITORY_URL}/blob/main/docs/support-matrix.md`;
  const EULA_URL = 'https://www.minecraft.net/en-us/eula';
  const USAGE_GUIDELINES_URL = 'https://www.minecraft.net/en-us/usage-guidelines';

  const verifiedScopes: MessageKey[] = [
    'coverage.regions',
    'coverage.entities',
    'coverage.resource_pack'
  ];

  const notScannedScopes: MessageKey[] = [
    'coverage.datapacks',
    'coverage.command_storage',
    'coverage.playerdata'
  ];

  const blockedFormatKeys: MessageKey[] = [
    'world.blocked.bedrock',
    'world.blocked.mcr',
    'world.blocked.linear'
  ];

  const verifiedCompression = ['gzip', 'zlib', 'uncompressed', 'LZ4Block', 'external .mcc'];

  type Diagnostics = {
    platform: string;
    renderer: string;
    storage: string;
  };

  function detectPlatform(): string {
    if (typeof navigator === 'undefined') return t('about.unavailable');
    const userAgent = navigator.userAgent;
    if (/iPhone|iPad|iPod/i.test(userAgent)) return 'iOS';
    if (/Android/i.test(userAgent)) return 'Android';
    if (/Macintosh|Mac OS X/i.test(userAgent)) return 'macOS';
    if (/Windows/i.test(userAgent)) return 'Windows';
    if (/Linux/i.test(userAgent)) return 'Linux';
    return navigator.platform || t('about.unavailable');
  }

  function detectRenderer(): string {
    if (typeof navigator === 'undefined') return t('about.unavailable');
    const userAgent = navigator.userAgent;
    if (/Edg\//i.test(userAgent)) return 'Chromium / WebView2';
    if (/Chrome|Chromium/i.test(userAgent)) return 'Chromium';
    if (/Firefox/i.test(userAgent)) return 'Gecko';
    if (/AppleWebKit/i.test(userAgent)) return 'WebKit';
    return 'WebView';
  }

  function detectStorage(): string {
    if (typeof localStorage === 'undefined') return t('about.unavailable');
    try {
      return localStorage ? t('about.available') : t('about.unavailable');
    } catch {
      return t('about.unavailable');
    }
  }

  const diagnostics: Diagnostics = $derived.by(() => ({
    platform: detectPlatform(),
    renderer: detectRenderer(),
    storage: detectStorage()
  }));
</script>

<div class="page about">
  <header class="page-head">
    <p class="eyebrow">{t('app.tagline')}</p>
    <h1>{t('about.title')}</h1>
    <p class="lead">{t('about.lead')}</p>
  </header>

  <section class="hero card" aria-labelledby="identity-title">
    <div class="identity">
      <img class="mascot" src="/images/pomi.png" alt="Pomi" width="128" height="128" />
      <div class="identity-copy">
        <img class="wordmark" src="/images/wordmark.png" alt="PomiTranslate" width="220" height="64" />
        <h2 id="identity-title">{t('app.tagline')}</h2>
        <p class="muted">{t('about.version', { version: APP_VERSION })}</p>
      </div>
    </div>
    <p class="hero-copy">{t('about.lead')}</p>
  </section>

  <div class="columns">
    <section class="card card-pad" aria-labelledby="coverage-title">
      <div class="section-heading">
        <div>
          <h2 id="coverage-title">{t('coverage.title')}</h2>
          <p class="muted">{t('coverage.lead')}</p>
        </div>
        <span class="pill pill-success"><Icon name="check-circle" size={14} /> {t('coverage.scanned')}</span>
      </div>

      <div class="coverage-group">
        <h3>{t('coverage.scanned')}</h3>
        <ul class="scope-list">
          {#each verifiedScopes as key (key)}
            <li><Icon name="check" size={17} /> <span>{t(key)}</span></li>
          {/each}
        </ul>
      </div>

      <div class="coverage-group">
        <h3><span class="pill pill-accent">{t('about.supportedFormats')}</span></h3>
        <ul class="format-list" aria-label={t('about.supportedFormats')}>
          {#each verifiedCompression as format (format)}
            <li><span class="pill">{format}</span></li>
          {/each}
        </ul>
      </div>

      <div class="coverage-group not-scanned">
        <h3><span class="pill pill-warning"><Icon name="minus" size={14} /> {t('coverage.notScanned')}</span></h3>
        <ul class="scope-list">
          {#each notScannedScopes as key (key)}
            <li><Icon name="minus" size={17} /> <span>{t(key)}</span></li>
          {/each}
        </ul>
      </div>

      <div class="coverage-group blocked">
        <h3><span class="pill pill-danger"><Icon name="alert-triangle" size={14} /> {t('result.unsupported')}</span></h3>
        <ul class="scope-list">
          {#each blockedFormatKeys as key (key)}
            <li><Icon name="alert-triangle" size={17} /> <span>{t(key)}</span></li>
          {/each}
        </ul>
        <p class="hint">{t('about.unsupportedHelp')}</p>
      </div>

      <a class="matrix-link" href={SUPPORT_MATRIX_URL} target="_blank" rel="noreferrer">
        <span>{t('about.supportMatrix')}</span>
        <span class="mono">docs/support-matrix.md</span>
        <Icon name="chevron-right" size={17} />
      </a>
    </section>

    <div class="side-stack">
      <Callout tone="warning" title={t('notice.title')}>
        <p>{t('about.unofficial')}</p>
        <p>{t('notice.item1')}</p>
        <p>{t('notice.item2')}</p>
      </Callout>

      <section class="card card-pad" aria-labelledby="privacy-title">
        <div class="section-heading">
          <div>
            <h2 id="privacy-title">{t('settings.apiKey.label')}</h2>
            <p class="muted">{t('about.local')}</p>
          </div>
          <Icon name="shield" size={24} />
        </div>
        <p class="keychain-note">{t('settings.vault.help')}</p>
      </section>

      <section class="card card-pad" aria-labelledby="links-title">
        <h2 id="links-title">{t('about.source')}</h2>
        <nav class="link-list" aria-label={t('about.source')}>
          <a class="link-row" href={REPOSITORY_URL} target="_blank" rel="noreferrer">
            <Icon name="language" size={19} />
            <span><strong>GitHub</strong><small class="mono">kim0040/Minecraft-World-Translator</small></span>
            <Icon name="chevron-right" size={17} />
          </a>
          <a class="link-row" href={LICENSE_URL} target="_blank" rel="noreferrer">
            <Icon name="shield" size={19} />
            <span><strong>MIT License</strong><small>LICENSE</small></span>
            <Icon name="chevron-right" size={17} />
          </a>
          <a class="link-row" href="mailto:mini0227kim@gmail.com">
            <Icon name="info" size={19} />
            <span><strong>{t('about.contact')}</strong><small>mini0227kim@gmail.com</small></span>
            <Icon name="chevron-right" size={17} />
          </a>
          <a class="link-row" href={EULA_URL} target="_blank" rel="noreferrer">
            <Icon name="info" size={19} />
            <span><strong>Minecraft EULA</strong><small>minecraft.net</small></span>
            <Icon name="chevron-right" size={17} />
          </a>
          <a class="link-row" href={USAGE_GUIDELINES_URL} target="_blank" rel="noreferrer">
            <Icon name="info" size={19} />
            <span><strong>Usage Guidelines</strong><small>minecraft.net</small></span>
            <Icon name="chevron-right" size={17} />
          </a>
        </nav>
      </section>
    </div>
  </div>

  <section class="card card-pad diagnostics" aria-labelledby="diagnostics-title">
    <div class="section-heading">
      <div>
        <h2 id="diagnostics-title">{t('about.diagnostics')}</h2>
        <p class="muted">{t('about.diagnosticsLead')}</p>
      </div>
      <span class="pill">{t('about.version', { version: APP_VERSION })}</span>
    </div>
    <dl>
      <div><dt>{t('about.platform')}</dt><dd>{diagnostics.platform}</dd></div>
      <div><dt>{t('about.renderer')}</dt><dd>{diagnostics.renderer}</dd></div>
      <div><dt>{t('about.storage')}</dt><dd>{diagnostics.storage}</dd></div>
    </dl>
  </section>
</div>

<style>
  .about { max-width: 1040px; }
  .hero { display: grid; grid-template-columns: minmax(0, 1fr) minmax(180px, 0.62fr); align-items: center; gap: var(--space-6); padding: var(--space-6); overflow: hidden; }
  .identity { display: flex; align-items: center; gap: var(--space-5); min-width: 0; }
  .mascot { width: clamp(88px, 13vw, 128px); height: auto; object-fit: contain; flex: none; }
  .identity-copy { display: grid; gap: var(--space-2); min-width: 0; }
  .wordmark { width: min(220px, 100%); height: auto; object-fit: contain; object-position: left center; }
  .identity-copy h2 { font-size: var(--text-lg); color: var(--text-secondary); font-weight: 600; }
  .hero-copy { color: var(--text-secondary); max-width: 34ch; }
  .columns { display: grid; grid-template-columns: minmax(0, 1.15fr) minmax(280px, 0.85fr); gap: var(--space-5); align-items: start; }
  .side-stack { display: grid; gap: var(--space-5); min-width: 0; }
  .section-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--space-4); }
  .section-heading h2 { font-size: var(--text-xl); }
  .section-heading .muted { margin-top: var(--space-1); max-width: 54ch; }
  .coverage-group { display: grid; gap: var(--space-3); margin-top: var(--space-5); }
  .coverage-group h3 { font-size: var(--text-sm); }
  .scope-list, .format-list { list-style: none; display: grid; gap: var(--space-2); margin: 0; padding: 0; }
  .scope-list li { display: flex; align-items: flex-start; gap: var(--space-2); color: var(--text-secondary); font-size: var(--text-sm); }
  .scope-list :global(.icon) { color: var(--success-solid); margin-top: 2px; }
  .not-scanned .scope-list :global(.icon) { color: var(--warning-solid); }
  .blocked .scope-list :global(.icon) { color: var(--danger-solid); }
  .format-list { display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .format-list .pill { font-family: var(--font-mono); font-weight: 500; }
  .blocked .hint { margin-top: var(--space-1); }
  .matrix-link { display: flex; align-items: center; gap: var(--space-2); margin-top: var(--space-5); padding-top: var(--space-4); border-top: 1px solid var(--border); color: var(--accent-text); font-weight: 600; text-decoration: none; }
  .matrix-link:hover { text-decoration: underline; }
  .matrix-link .mono { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text-secondary); font-size: var(--text-xs); font-weight: 400; }
  .matrix-link :global(.icon:last-child) { margin-inline-start: auto; }
  .side-stack :global(.callout) { height: 100%; }
  .side-stack :global(.callout-body) { display: grid; gap: var(--space-2); }
  .keychain-note { margin-top: var(--space-4); padding: var(--space-3); border-radius: var(--radius-md); background: var(--bg-sunken); color: var(--text-secondary); font-size: var(--text-sm); }
  .link-list { display: grid; gap: var(--space-2); margin-top: var(--space-4); }
  .link-row { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: var(--space-3); min-height: 52px; padding: var(--space-2) var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-md); color: var(--text); text-decoration: none; }
  .link-row:hover { background: var(--bg-hover); border-color: var(--border-strong); }
  .link-row > :global(.icon:first-child) { color: var(--accent-text); }
  .link-row > :global(.icon:last-child) { color: var(--text-secondary); }
  .link-row span { display: grid; gap: 1px; min-width: 0; }
  .link-row strong { font-size: var(--text-sm); }
  .link-row small { overflow-wrap: anywhere; color: var(--text-secondary); font-size: var(--text-xs); }
  .diagnostics dl { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--space-3); margin: var(--space-5) 0 0; }
  .diagnostics dl > div { min-width: 0; padding: var(--space-3); border: 1px solid var(--border); border-radius: var(--radius-md); background: var(--bg-sunken); }
  .diagnostics dt { color: var(--text-secondary); font-size: var(--text-xs); font-weight: 600; }
  .diagnostics dd { margin: var(--space-1) 0 0; overflow-wrap: anywhere; font-family: var(--font-mono); font-size: var(--text-sm); }

  @media (max-width: 840px) {
    .hero, .columns { grid-template-columns: 1fr; }
    .hero-copy { max-width: 62ch; }
  }

  @media (max-width: 560px) {
    .hero { padding: var(--space-5); }
    .identity { align-items: flex-start; gap: var(--space-3); }
    .mascot { width: 80px; }
    .diagnostics dl { grid-template-columns: 1fr; }
    .section-heading { flex-direction: column; }
  }

  @media (max-width: 360px) {
    .hero { padding: var(--space-4); }
    .identity { display: grid; grid-template-columns: 64px minmax(0, 1fr); }
    .mascot { width: 64px; }
    .wordmark { width: 100%; }
    .identity-copy h2 { font-size: var(--text-md); }
    .card-pad { padding: var(--space-4); }
  }
</style>
