import { SvelteSet } from 'svelte/reactivity';
import { open } from '@tauri-apps/plugin-dialog';
import {
  BackendError,
  callBackend,
  cancelBackend,
  credentialStored,
  onCloseBlocked,
  onProgress,
  type BackupSummary,
  type BootstrapPayload,
  type Estimate,
  type ModelInfo,
  type Notices,
  type ProgressEvent,
  type RecentWorld,
  type ResumeStatus,
  type ScanResult,
  type Settings,
  type TranslationResult,
  type WorldInspection
} from './api';
import { hasMessage, setLocale, t, type Locale, type MessageKey } from './i18n/index.svelte';
import { applyTheme, type ThemeChoice } from './theme';

export type Page = 'workspace' | 'backups' | 'settings' | 'about';
export type Step = 'world' | 'scan' | 'review' | 'run' | 'result';
export type Busy = '' | 'loading' | 'scan' | 'translate' | 'restore' | 'models';
export type Tone = 'info' | 'success' | 'error';

export const STEPS: Step[] = ['world', 'scan', 'review', 'run', 'result'];

export type JobProgress = {
  phase: 'idle' | 'collect' | 'translate' | 'write';
  fileIndex: number;
  fileTotal: number;
  done: number;
  total: number;
  failed: number;
  batch: number;
  batches: number;
  requests: number;
  requestsEstimate: number;
  retry: { attempt: number; max: number } | null;
  startedAt: number;
};

const emptyProgress = (): JobProgress => ({
  phase: 'idle', fileIndex: 0, fileTotal: 0, done: 0, total: 0, failed: 0, batch: 0, batches: 0,
  requests: 0, requestsEstimate: 0, retry: null, startedAt: 0
});

const defaultSettings = (): Settings => ({
  provider: 'openai', model: '', base_url: '', wire_format: 'openai', target_language: '한국어', style_preset: 'neutral',
  style_prompt: '', custom_system_prompt: '', temperature: 0.3, batch_size: 40, request_timeout: 120, rpm_limit: 0,
  tpm_limit: 0, max_batch_retries: 3, concurrency: 4, resource_pack_enabled: false, skip_target_language_text: true,
  ui_language: 'ko', last_world_dir: ''
});

const NOTICE_KEY = 'pomi.notice.v1';
const RESUMABLE = ['cancelled', 'needs_retry', 'failed'];
/** Settings that change which text a scan finds. Changing one makes a reviewed scan stale. */
const SCOPE_KEYS: (keyof Settings)[] = ['target_language', 'resource_pack_enabled', 'skip_target_language_text'];

function numberOr(value: unknown, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) && value !== '' && value !== null && value !== undefined ? parsed : fallback;
}

export class AppState {
  ready = $state(false);
  page = $state<Page>('workspace');
  step = $state<Step>('world');
  busy = $state<Busy>('');
  cancelling = $state(false);
  theme = $state<ThemeChoice>('system');
  notices = $state<Notices | null>(null);
  showNotice = $state(false);
  banner = $state<{ tone: 'error' | 'warning'; message: string } | null>(null);
  toasts = $state<{ id: number; tone: Tone; message: string }[]>([]);
  railCollapsed = $state(false);

  settings = $state<Settings>(defaultSettings());
  apiKeyStored = $state(false);
  models = $state<ModelInfo[]>([]);

  worldDir = $state('');
  inspection = $state<WorldInspection | null>(null);
  recent = $state<RecentWorld[]>([]);
  backups = $state<BackupSummary[]>([]);

  scan = $state<ScanResult | null>(null);
  excluded = new SvelteSet<string>();
  overrides = $state<Record<string, string>>({});
  estimate = $state<Estimate | null>(null);
  failurePolicy = $state<'stop' | 'skip'>('stop');

  progress = $state<JobProgress>(emptyProgress());
  result = $state<TranslationResult | null>(null);
  resume = $state<ResumeStatus | null>(null);
  closeBlocked = $state(false);
  lastRestoreId = $state('');

  private toastSerial = 0;
  private unsubscribe: (() => void)[] = [];

  // --- derived numbers used across screens ---------------------------------------------------

  get locale(): Locale {
    return (this.settings.ui_language as Locale) || 'ko';
  }

  get candidateCount(): number {
    return this.scan?.candidateCount ?? 0;
  }

  get manualCount(): number {
    return Object.entries(this.overrides).filter(([id, value]) => value.trim() && !this.excluded.has(id)).length;
  }

  get includedCount(): number {
    return Math.max(0, this.candidateCount - this.excluded.size);
  }

  /** Sentences that will go to the provider: included and not written by hand. */
  get outgoingCount(): number {
    return Math.max(0, this.includedCount - this.manualCount);
  }

  get manualOnly(): boolean {
    return this.includedCount > 0 && this.manualCount === this.includedCount;
  }

  get hasModel(): boolean {
    return !!this.settings.model?.trim();
  }

  get canRun(): boolean {
    return !!this.scan && this.scan.status === 'completed' && !this.scan.writeBlockers?.length &&
      this.includedCount > 0 && (this.hasModel || this.manualOnly) && !this.busy;
  }

  get stepReached(): Record<Step, boolean> {
    const scanned = !!this.scan && this.scan.status === 'completed' && !this.scan.writeBlockers?.length;
    return {
      world: true,
      scan: !!this.worldDir && !!this.inspection?.validJavaWorld,
      review: scanned && this.candidateCount > 0,
      run: scanned && this.candidateCount > 0,
      result: !!this.result
    };
  }

  get isBusy(): boolean {
    return this.busy === 'scan' || this.busy === 'translate' || this.busy === 'restore';
  }

  // --- feedback ----------------------------------------------------------------------------

  notify(message: string, tone: Tone = 'info', ms = 5200): void {
    const id = ++this.toastSerial;
    this.toasts = [...this.toasts, { id, tone, message }];
    if (ms > 0) setTimeout(() => this.dismissToast(id), ms);
  }

  dismissToast(id: number): void {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
  }

  /** A readable message for a failed call. Codes the shell or core sent map to catalog text. */
  describe(cause: unknown): string {
    if (cause instanceof BackendError) {
      const key = `error.${cause.code}`;
      if (cause.code === 'BUSY') return t('error.busy');
      if (hasMessage(key)) return t(key as MessageKey);
      return cause.message || t('error.default');
    }
    return cause instanceof Error ? cause.message : t('error.default');
  }

  fail(cause: unknown): void {
    this.banner = { tone: 'error', message: this.describe(cause) };
  }

  // --- start-up ----------------------------------------------------------------------------

  async boot(): Promise<void> {
    this.busy = 'loading';
    try {
      this.unsubscribe.push(await onProgress((event) => this.handleProgress(event)));
      this.unsubscribe.push(await onCloseBlocked(() => { this.closeBlocked = true; }));
    } catch {
      // Outside the desktop shell there are no events. The app still works without live progress.
    }
    try {
      const boot = await callBackend<BootstrapPayload>('app.bootstrap');
      this.notices = boot.notices;
      this.settings = { ...defaultSettings(), ...boot.settings };
      this.settings.batch_size = numberOr(boot.settings.batch_size, 40);
      this.settings.temperature = numberOr(boot.settings.temperature, 0.3);
      this.settings.request_timeout = numberOr(boot.settings.request_timeout, 120);
      this.settings.rpm_limit = numberOr(boot.settings.rpm_limit, 0);
      this.settings.tpm_limit = numberOr(boot.settings.tpm_limit, 0);
      this.settings.max_batch_retries = numberOr(boot.settings.max_batch_retries, 3);
      this.settings.concurrency = numberOr(boot.settings.concurrency, 4);
      this.settings.skip_target_language_text = boot.settings.skip_target_language_text !== false;
      this.settings.resource_pack_enabled = !!boot.settings.resource_pack_enabled;
      setLocale(this.locale);
      this.apiKeyStored = boot.apiKeyStored;
      this.recent = boot.worlds;
      this.worldDir = boot.settings.last_world_dir || '';
      this.inspection = boot.worldInspection;
      this.backups = boot.backups;
      this.showNotice = localStorage.getItem(NOTICE_KEY) !== 'accepted';
      if (this.worldDir && this.inspection?.validJavaWorld) this.step = 'scan';
      this.applyResume(boot.resume);
      void credentialStored(this.settings.provider).then((stored) => { this.apiKeyStored = stored; }).catch(() => {});
    } catch (cause) {
      this.fail(cause);
    } finally {
      this.busy = '';
      this.ready = true;
    }
  }

  destroy(): void {
    for (const stop of this.unsubscribe) stop();
    this.unsubscribe = [];
  }

  acceptNotice(): void {
    localStorage.setItem(NOTICE_KEY, 'accepted');
    this.showNotice = false;
  }

  setTheme(choice: ThemeChoice): void {
    this.theme = choice;
    applyTheme(choice);
  }

  // --- navigation --------------------------------------------------------------------------

  goto(page: Page): void {
    this.page = page;
  }

  goStep(step: Step): void {
    if (!this.stepReached[step] || this.isBusy) return;
    this.page = 'workspace';
    this.step = step;
  }

  // --- worlds ------------------------------------------------------------------------------

  private resetJob(): void {
    this.scan = null;
    this.excluded.clear();
    this.overrides = {};
    this.estimate = null;
    this.result = null;
    this.progress = emptyProgress();
    this.resume = null;
  }

  async chooseWorld(): Promise<void> {
    this.banner = null;
    try {
      const chosen = await open({ directory: true, multiple: false, title: t('world.open') });
      if (typeof chosen === 'string') await this.useWorld(chosen);
    } catch (cause) {
      this.fail(cause);
    }
  }

  async useWorld(path: string): Promise<void> {
    if (this.isBusy) return;
    this.banner = null;
    try {
      const inspected = await callBackend<WorldInspection>('world.inspect', { worldDir: path });
      if (!inspected.validJavaWorld) {
        this.banner = { tone: 'error', message: t('world.invalid') };
        return;
      }
      const changed = path !== this.worldDir;
      this.worldDir = path;
      this.inspection = inspected;
      if (changed) this.resetJob();
      this.recent = (await callBackend<{ worlds: RecentWorld[] }>('worlds.remember', { worldDir: path })).worlds;
      await this.loadBackups();
      if (changed) this.applyResume(await callBackend<ResumeStatus>('resume.status', { worldDir: path }));
      this.step = 'world';
    } catch (cause) {
      this.fail(cause);
    }
  }

  async forgetWorld(path: string): Promise<void> {
    try {
      this.recent = (await callBackend<{ worlds: RecentWorld[] }>('worlds.forget', { worldDir: path })).worlds;
      if (this.worldDir === path) {
        this.worldDir = '';
        this.inspection = null;
        this.backups = [];
        this.resetJob();
        this.step = 'world';
      }
    } catch (cause) {
      this.fail(cause);
    }
  }

  async loadBackups(): Promise<void> {
    if (!this.worldDir) {
      this.backups = [];
      return;
    }
    this.backups = (await callBackend<{ backups: BackupSummary[] }>('backups.list', { worldDir: this.worldDir })).backups;
  }

  // --- resume ------------------------------------------------------------------------------

  private applyResume(resumable: ResumeStatus): void {
    if (!resumable?.available || !resumable.scanPlanId || !resumable.fingerprint) {
      this.resume = null;
      return;
    }
    this.scan = {
      status: 'completed',
      candidateCount: resumable.candidateCount || 0,
      providerRequests: 0,
      fingerprint: resumable.fingerprint,
      scanPlanId: resumable.scanPlanId,
      dryRun: true,
      candidates: resumable.candidates || []
    };
    this.excluded.clear();
    for (const id of resumable.excludedCandidateIds || []) this.excluded.add(id);
    this.overrides = { ...(resumable.candidateOverrides || {}) };
    this.resume = resumable;
    void this.loadEstimate();
  }

  // --- scan --------------------------------------------------------------------------------

  async startScan(): Promise<void> {
    if (!this.worldDir || this.isBusy) return;
    this.busy = 'scan';
    this.banner = null;
    this.resetJob();
    this.progress = { ...emptyProgress(), phase: 'collect', startedAt: Date.now() };
    try {
      await this.persistSettings();
      this.scan = await callBackend<ScanResult>('scan.start', { worldDir: this.worldDir });
      this.estimate = this.scan.estimate ?? null;
    } catch (cause) {
      this.fail(cause);
    } finally {
      this.busy = '';
      this.progress = emptyProgress();
    }
  }

  async loadEstimate(): Promise<void> {
    if (!this.scan) return;
    try {
      this.estimate = await callBackend<Estimate>('estimate.get', {
        scanPlanId: this.scan.scanPlanId,
        excludedCandidateIds: [...this.excluded],
        overrideCandidateIds: Object.entries(this.overrides).filter(([, value]) => value.trim()).map(([id]) => id)
      });
    } catch {
      // The estimate is a convenience. A failure leaves the last known one in place.
    }
  }

  setIncluded(id: string, included: boolean): void {
    if (included) this.excluded.delete(id);
    else this.excluded.add(id);
  }

  setOverride(id: string, value: string): void {
    const next = { ...this.overrides };
    if (value) next[id] = value;
    else delete next[id];
    this.overrides = next;
  }

  // --- translate ---------------------------------------------------------------------------

  private handleProgress(event: ProgressEvent): void {
    const p = { ...this.progress };
    switch (event.event) {
      case 'scan_start':
        p.phase = 'collect';
        p.fileTotal = event.total_files ?? p.fileTotal;
        break;
      case 'file_start':
      case 'file_done':
        if (event.phase === 'write') p.phase = 'write';
        else if (p.phase === 'idle') p.phase = 'collect';
        p.fileIndex = event.index ?? p.fileIndex;
        p.fileTotal = event.total ?? p.fileTotal;
        break;
      case 'phase_start':
        if (event.phase === 'translate') {
          p.phase = 'translate';
          p.total = event.total ?? 0;
          p.done = 0;
          p.requestsEstimate = event.requests_estimate ?? 0;
        } else if (event.phase === 'write') {
          p.phase = 'write';
          p.fileIndex = 0;
          p.fileTotal = event.total ?? 0;
        }
        break;
      case 'translation_progress':
        p.phase = 'translate';
        p.done = event.completed ?? p.done;
        p.total = event.total ?? p.total;
        p.failed = event.failed ?? p.failed;
        p.batch = event.batch ?? p.batch;
        p.batches = event.batches ?? p.batches;
        p.requests = event.requests ?? p.requests;
        p.retry = null;
        break;
      case 'translation_batch_error':
        p.retry = { attempt: event.attempt ?? 1, max: event.max_attempts ?? 1 };
        break;
      case 'translation_batch_done':
        p.retry = null;
        break;
      default:
        return;
    }
    this.progress = p;
  }

  async startTranslate(options: { resume?: boolean } = {}): Promise<void> {
    if (!this.scan || this.isBusy) return;
    this.busy = 'translate';
    this.cancelling = false;
    this.banner = null;
    this.result = null;
    this.step = 'run';
    this.progress = { ...emptyProgress(), phase: 'collect', startedAt: Date.now() };
    let outcome: TranslationResult | null = null;
    try {
      await this.persistSettings();
      outcome = await callBackend<TranslationResult>(options.resume ? 'translate.resume' : 'translate.start', {
        worldDir: this.worldDir,
        fingerprint: this.scan.fingerprint,
        scanPlanId: this.scan.scanPlanId,
        excludedCandidateIds: [...this.excluded],
        candidateOverrides: this.overrides,
        provider: this.settings.provider,
        failurePolicy: this.failurePolicy
      });
      this.result = outcome;
      this.step = 'result';
      await this.loadBackups();
      if (RESUMABLE.includes(outcome.status)) {
        this.applyResume(await callBackend<ResumeStatus>('resume.status', { worldDir: this.worldDir }));
        // A resumed job keeps its reviewed choices: applyResume rebuilds them from the checkpoint.
      } else {
        this.resume = null;
      }
    } catch (cause) {
      this.fail(cause);
      this.step = this.scan ? 'run' : 'scan';
    } finally {
      this.busy = '';
      this.cancelling = false;
      this.progress = emptyProgress();
    }
  }

  async cancel(): Promise<void> {
    if (!this.isBusy || this.cancelling) return;
    try {
      if (await cancelBackend()) this.cancelling = true;
    } catch (cause) {
      this.fail(cause);
    }
  }

  // --- backups -----------------------------------------------------------------------------

  async restore(backupSetId: string): Promise<boolean> {
    if (!this.worldDir || this.isBusy) return false;
    this.busy = 'restore';
    this.banner = null;
    try {
      const restored = await callBackend<{ status: string; recoverySetId: string }>('restore.start', {
        worldDir: this.worldDir,
        backupSetId
      });
      this.lastRestoreId = restored.recoverySetId;
      this.resetJob();
      await this.loadBackups();
      this.notify(t('backups.restoreDone', { id: restored.recoverySetId || backupSetId }), 'success', 9000);
      return true;
    } catch (cause) {
      this.fail(cause);
      return false;
    } finally {
      this.busy = '';
    }
  }

  // --- settings ----------------------------------------------------------------------------

  /** Write the current settings, and a new API key when one was typed. Never keeps the key. */
  async persistSettings(apiKey = ''): Promise<void> {
    const s = this.settings;
    const saved = await callBackend<{ settings: Settings; apiKeyStored: boolean }>('settings.set', {
      worldDir: this.worldDir,
      provider: s.provider,
      model: s.model,
      baseUrl: s.base_url,
      wireFormat: s.wire_format,
      targetLanguage: s.target_language,
      stylePreset: s.style_preset,
      stylePrompt: s.style_prompt,
      customSystemPrompt: s.custom_system_prompt,
      uiLanguage: s.ui_language,
      temperature: s.temperature,
      batchSize: s.batch_size,
      requestTimeout: s.request_timeout,
      rpmLimit: s.rpm_limit,
      tpmLimit: s.tpm_limit,
      maxBatchRetries: s.max_batch_retries,
      concurrency: s.concurrency,
      resourcePackEnabled: s.resource_pack_enabled,
      skipTargetLanguageText: s.skip_target_language_text,
      ...(apiKey ? { apiKey } : {})
    });
    this.apiKeyStored = saved.apiKeyStored;
  }

  /** Save from the settings screen. A change that alters what a scan finds makes the scan stale. */
  async saveSettings(before: Settings, apiKey = ''): Promise<boolean> {
    try {
      await this.persistSettings(apiKey);
      const scopeChanged = SCOPE_KEYS.some((key) => before[key] !== this.settings[key]);
      if (scopeChanged && this.scan) {
        this.resetJob();
        if (this.step !== 'world') this.step = 'scan';
        this.notify(t('settings.changedScan'), 'info', 8000);
      }
      if (before.ui_language !== this.settings.ui_language) setLocale(this.locale);
      if (this.scan) void this.loadEstimate();
      this.notify(t('settings.saved'), 'success', 2600);
      return true;
    } catch (cause) {
      this.banner = { tone: 'error', message: `${t('settings.saveError')}: ${this.describe(cause)}` };
      return false;
    }
  }

  async loadModels(): Promise<number> {
    this.busy = 'models';
    try {
      await this.persistSettings();
      const listed = await callBackend<{ models: ModelInfo[] }>('models.list', {
        provider: this.settings.provider,
        baseUrl: this.settings.base_url
      });
      this.models = listed.models;
      return listed.models.length;
    } finally {
      this.busy = '';
    }
  }

  async deleteApiKey(): Promise<void> {
    try {
      await callBackend<{ deleted: boolean }>('credentials.delete', { provider: this.settings.provider });
      this.apiKeyStored = false;
      this.notify(t('settings.apiKey.deleted'), 'success');
    } catch (cause) {
      this.fail(cause);
    }
  }

  isResumeStatus(status: string): boolean {
    return RESUMABLE.includes(status);
  }
}

export const app = new AppState();
