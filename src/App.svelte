<script lang="ts">
  import { onMount } from 'svelte';
  import { listen } from '@tauri-apps/api/event';
  import { open } from '@tauri-apps/plugin-dialog';
  import { callBackend, cancelBackend, credentialStored, type BackupSummary, type RecentWorld, type ScanResult, type Settings, type TranslationResult, type WorldInspection } from './lib/backend';
  import { translate, type UiLocale } from './lib/i18n';

  type Page = 'world' | 'settings' | 'about';
  type Notice = { firstLaunch: string; about: string; backupWarning: string; apiWarning: string };
  type ResumeStatus = {
    available: boolean;
    scanPlanId?: string;
    fingerprint?: string;
    candidateCount?: number;
    candidates?: NonNullable<ScanResult['candidates']>;
    excludedCandidateIds?: string[];
    candidateOverrides?: Record<string, string>;
    savedAt?: number;
    status?: string;
    translatedCount?: number;
    reason?: string;
  };
  type BootstrapPayload = {
    notices: Notice;
    settings: Settings;
    apiKeyStored: boolean;
    worlds: RecentWorld[];
    worldInspection: WorldInspection | null;
    backups: BackupSummary[];
    resume: ResumeStatus;
  };

  let page = $state<Page>('world');
  let uiLanguage = $state<UiLocale>('ko');
  let busy = $state<'loading' | 'scan' | 'translate' | 'restore' | 'models' | ''>('loading');
  let error = $state('');
  let info = $state('');
  let worldDir = $state('');
  let provider = $state('openai');
  let model = $state('');
  let baseUrl = $state('');
  let wireFormat = $state('openai');
  let targetLanguage = $state('한국어');
  let stylePreset = $state('neutral');
  let stylePrompt = $state('');
  let customSystemPrompt = $state('');
  let temperature = $state(0.3);
  let batchSize = $state(40);
  let requestTimeout = $state(120);
  let rpmLimit = $state(0);
  let tpmLimit = $state(0);
  let maxBatchRetries = $state(3);
  let resourcePackEnabled = $state(false);
  let apiKey = $state('');
  let apiKeyStored = $state(false);
  let models = $state<{ id: string; display_name?: string }[]>([]);
  let scan = $state<ScanResult | null>(null);
  let result = $state<TranslationResult | null>(null);
  let backups = $state<BackupSummary[]>([]);
  let selectedBackupId = $state('');
  let excludedCandidateIds = $state<string[]>([]);
  let candidateOverrides = $state<Record<string, string>>({});
  let recentWorlds = $state<RecentWorld[]>([]);
  let worldInspection = $state<WorldInspection | null>(null);
  let candidateQuery = $state('');
  let candidateViewTotal = $state(0);
  let candidateFilter = $state<'all' | 'included' | 'excluded' | 'manual'>('all');
  let candidateOffset = $state(0);
  let notices = $state<Notice | null>(null);
  let showNotice = $state(false);
  let showTranslateConfirm = $state(false);
  let showRestoreConfirm = $state(false);
  let showDeleteKeyConfirm = $state(false);
  let progressText = $state('');
  let resumeAvailable = $state(false);
  let resumeSavedAt = $state(0);
  let resumeRequested = $state(false);
  let resumeStatus = $state('cancelled');
  let resumeTranslated = $state(0);

  const providerChoices = [
    { id: 'openai', label: 'OpenAI' },
    { id: 'gemini', label: 'Gemini' },
    { id: 'anthropic', label: 'Anthropic' },
    { id: 'openrouter', label: 'OpenRouter' },
    { id: 'custom', label: 'Custom' }
  ];

  const includedCandidateCount = $derived((scan?.candidateCount ?? 0) - excludedCandidateIds.length);
  const manualOverrideCount = $derived(
    Object.entries(candidateOverrides).filter(([id, value]) => value.trim() && !excludedCandidateIds.includes(id)).length
  );
  const externalCandidateCount = $derived(Math.max(0, includedCandidateCount - manualOverrideCount));
  const estimatedRequestCount = $derived(
    externalCandidateCount === 0 ? 0 : Math.ceil(externalCandidateCount / Math.max(1, Number(batchSize) || 1))
  );
  const manualOnly = $derived(includedCandidateCount > 0 && manualOverrideCount === includedCandidateCount);
  const visibleCandidates = $derived(
    (scan?.candidates ?? []).filter((candidate) => {
      if (candidateFilter === 'included') return !excludedCandidateIds.includes(candidate.id);
      if (candidateFilter === 'excluded') return excludedCandidateIds.includes(candidate.id);
      if (candidateFilter === 'manual') return !!candidateOverrides[candidate.id]?.trim();
      return true;
    })
  );
  const canTranslate = $derived(
    !!worldDir && scan?.status === 'completed' && !!scan?.fingerprint &&
    !scan?.writeBlockers?.length && includedCandidateCount > 0 && (!!model.trim() || manualOnly) && !busy
  );

  onMount(() => {
    let unlisten: (() => void) | undefined;
    void listen<{ payload?: { event?: string; phase?: string; index?: number; total?: number; completed?: number; candidate_text_count?: number } }>('pomi-progress', ({ payload: message }) => {
      const progress = message.payload || {};
      if (progress.index && progress.total) {
        progressText = progress.phase === 'write'
          ? t('월드에 쓰는 중 · 파일 {index} / {total}', { index: progress.index, total: progress.total })
          : t('텍스트 찾는 중 · 파일 {index} / {total}', { index: progress.index, total: progress.total });
      } else if (progress.event === 'done') {
        progressText = '';
      } else if (progress.event === 'translation_progress') {
        progressText = t('번역 중 · {done} / {total}', { done: progress.completed ?? 0, total: progress.total ?? 0 });
      } else if (progress.event === 'phase_start' && progress.phase === 'translate') {
        progressText = t('번역 요청 준비 중');
      } else if (progress.event === 'translation_batch_error') {
        progressText = t('제공사 응답 오류 · 다시 시도합니다');
      }
    }).then((stop) => { unlisten = stop; });
    void (async () => {
      try {
        const bootstrap = await callBackend<BootstrapPayload>('app.bootstrap');
        notices = bootstrap.notices;
        uiLanguage = bootstrap.settings.ui_language || 'ko';
        document.documentElement.lang = uiLanguage;
        provider = bootstrap.settings.provider || 'openai';
        model = bootstrap.settings.model || '';
        baseUrl = bootstrap.settings.base_url || '';
        wireFormat = bootstrap.settings.wire_format || 'openai';
        targetLanguage = bootstrap.settings.target_language || '한국어';
        stylePreset = bootstrap.settings.style_preset || 'neutral';
        stylePrompt = bootstrap.settings.style_prompt || '';
        customSystemPrompt = bootstrap.settings.custom_system_prompt || '';
        temperature = numberOr(bootstrap.settings.temperature, 0.3);
        batchSize = numberOr(bootstrap.settings.batch_size, 40);
        requestTimeout = numberOr(bootstrap.settings.request_timeout, 120);
        rpmLimit = numberOr(bootstrap.settings.rpm_limit, 0);
        tpmLimit = numberOr(bootstrap.settings.tpm_limit, 0);
        maxBatchRetries = numberOr(bootstrap.settings.max_batch_retries, 3);
        resourcePackEnabled = !!bootstrap.settings.resource_pack_enabled;
        worldDir = bootstrap.settings.last_world_dir || '';
        apiKeyStored = bootstrap.apiKeyStored;
        showNotice = localStorage.getItem('pomi.notice.v1') !== 'accepted';
        recentWorlds = bootstrap.worlds;
        worldInspection = bootstrap.worldInspection;
        backups = bootstrap.backups;
        selectedBackupId = backups[0]?.backupSetId || '';
        if (worldDir) {
          applyResume(bootstrap.resume);
        }
        void credentialStored(provider).then((stored) => { apiKeyStored = stored; }).catch(() => {});
      } catch (cause) {
        error = describe(cause);
      } finally {
        busy = '';
      }
    })();
    return () => unlisten?.();
  });

  function describe(cause: unknown): string {
    return cause instanceof Error ? cause.message : String(cause);
  }

  function t(key: string, variables: Record<string, string | number> = {}): string {
    return translate(uiLanguage, key, variables);
  }

  function updateUiLanguage(): void {
    document.documentElement.lang = uiLanguage;
  }

  function requestEstimate(): string {
    if (resumeAvailable) return t('재개 시 남은 요청 확인 불가');
    if (estimatedRequestCount === 0) return t('API 요청 없음');
    return t('최소 {count}회 · 파일 경계·재시도 제외', { count: estimatedRequestCount });
  }

  function numberOr(value: unknown, fallback: number): number {
    const parsed = Number(value);
    return Number.isFinite(parsed) && value !== '' && value !== null && value !== undefined ? parsed : fallback;
  }

  function compatibilityStatus(): { tone: 'verified' | 'warning' | 'unsupported'; label: string; detail: string } {
    const blockers = [...(worldInspection?.writeBlockers || []), ...(scan?.writeBlockers || [])];
    if (blockers.length || (scan && scan.status !== 'completed')) {
      return {
        tone: 'unsupported',
        label: t('현재 쓰기 중단'),
        detail: t('감지된 형식에는 쓰지 않습니다. 검사 결과에서 원인을 확인하세요.')
      };
    }
    if (!scan) {
      return {
        tone: 'warning',
        label: t('스캔 필요'),
        detail: t('DataVersion은 참고 정보입니다. 실제 리전 압축과 텍스트 구조를 스캔해야 합니다.')
      };
    }
    if (scan.errors?.length) {
      return {
        tone: 'warning',
        label: t('일부 구조 경고'),
        detail: t('읽지 못한 항목이 있어 전체 결과를 확인해야 합니다.')
      };
    }
    return {
      tone: 'verified',
      label: t('검사한 구조 쓰기 가능'),
      detail: t('현재 월드에서 발견한 압축·텍스트 구조가 픽스처로 검증된 범위에 있습니다.')
    };
  }

  function statusLabel(status: string): string {
    const labels: Record<string, string> = {
      completed: '완료',
      partial: '일부만 번역',
      needs_retry: '중단됨 · 월드 그대로',
      failed: '실패',
      cancelled: '취소됨',
      locked: '월드 사용 중',
      invalidated: '월드가 바뀜',
      unsupported: '지원하지 않는 형식'
    };
    return t(labels[status] || status);
  }

  function blockerLabel(blocker: string): string {
    const labels: Record<string, string> = {
      bedrock: 'Bedrock 월드는 현재 쓰기를 지원하지 않습니다.',
      mcr: 'pre-Anvil .mcr 파일은 현재 쓰기를 지원하지 않습니다.',
      linear: '.linear 리전 파일은 현재 쓰기를 지원하지 않습니다.',
      world_in_use: 'Minecraft 또는 서버가 이 월드를 사용 중입니다. 월드를 닫고 다시 스캔하세요.',
      not_writable: '선택한 폴더에 쓸 권한이 없습니다.',
      not_readable: '선택한 폴더를 읽을 권한이 없습니다.',
      missing: '선택한 폴더를 찾을 수 없습니다.'
    };
    return t(labels[blocker] || blocker);
  }

  function resetScan(): void {
    scan = null;
    result = null;
    excludedCandidateIds = [];
    candidateOverrides = {};
    candidateQuery = '';
    candidateViewTotal = 0;
    candidateFilter = 'all';
    candidateOffset = 0;
    progressText = '';
    resumeAvailable = false;
    resumeSavedAt = 0;
    resumeRequested = false;
  }

  function applyResume(resumable: ResumeStatus): void {
    if (!resumable.available || !resumable.scanPlanId || !resumable.fingerprint) return;
    scan = {
      status: 'completed',
      candidateCount: resumable.candidateCount || 0,
      providerRequests: 0,
      fingerprint: resumable.fingerprint,
      scanPlanId: resumable.scanPlanId,
      dryRun: true,
      candidates: resumable.candidates || []
    };
    candidateViewTotal = resumable.candidateCount || 0;
    excludedCandidateIds = resumable.excludedCandidateIds || [];
    candidateOverrides = resumable.candidateOverrides || {};
    resumeAvailable = true;
    resumeSavedAt = resumable.savedAt || 0;
    resumeStatus = resumable.status || 'cancelled';
    resumeTranslated = resumable.translatedCount || 0;
    info = resumeStatus === 'cancelled'
      ? t('안전하게 취소된 이전 작업이 있습니다. 월드와 설정이 일치해 이어서 실행할 수 있습니다.')
      : t('번역이 중단됐지만 월드는 바뀌지 않았습니다. 이미 번역한 {count}개는 저장돼 있어 이어서 실행하면 남은 부분만 요청합니다.', { count: resumeTranslated });
  }

  function failureMessage(outcome: TranslationResult): string {
    const first = outcome.errors?.[0];
    const codes: Record<string, string> = {
      RATE_LIMITED: '제공사가 요청 한도로 응답을 거절했습니다.',
      AUTH_FAILED: 'API 키가 거부됐습니다. 설정에서 키를 확인해 주세요.',
      NO_CREDIT: '제공사 계정의 잔액이 부족합니다.',
      MODEL_NOT_FOUND: '제공사가 이 모델을 찾지 못했습니다. 모델 ID를 확인해 주세요.',
      PROVIDER_ERROR: '제공사 서버에 오류가 있습니다.',
      NETWORK_ERROR: '제공사에 연결하지 못했습니다.',
      TRANSLATION_INCOMPLETE: '일부 문자열을 번역하지 못했습니다.'
    };
    const reason = t(codes[first?.code || ''] || '번역을 끝내지 못했습니다.');
    const kept = outcome.status === 'failed' ? '' : ` ${t('월드는 바뀌지 않았습니다. 잠시 후 이어서 실행하세요.')}`;
    return `${reason}${kept}`;
  }

  async function loadResume(): Promise<void> {
    if (!worldDir) return;
    applyResume(await callBackend<ResumeStatus>('resume.status', { worldDir }));
  }

  function setCandidateIncluded(candidateId: string, included: boolean): void {
    excludedCandidateIds = included
      ? excludedCandidateIds.filter((id) => id !== candidateId)
      : [...excludedCandidateIds, candidateId];
  }

  function setCandidateOverride(candidateId: string, value: string): void {
    const next = { ...candidateOverrides };
    if (value) next[candidateId] = value;
    else delete next[candidateId];
    candidateOverrides = next;
  }

  async function loadBackups(): Promise<void> {
    if (!worldDir) {
      backups = [];
      selectedBackupId = '';
      return;
    }
    const listed = await callBackend<{ backups: BackupSummary[] }>('backups.list', { worldDir });
    backups = listed.backups;
    if (!backups.some((item) => item.backupSetId === selectedBackupId)) {
      selectedBackupId = backups[0]?.backupSetId || '';
    }
  }

  async function chooseWorld(): Promise<void> {
    error = '';
    try {
      const chosen = await open({ directory: true, multiple: false, title: t('Minecraft Java 월드 폴더 선택') });
      if (typeof chosen === 'string' && chosen !== worldDir) {
        const inspected = await callBackend<WorldInspection>('world.inspect', { worldDir: chosen });
        if (!inspected.validJavaWorld) {
          error = t('Minecraft Java 월드 폴더 또는 Java 월드가 들어 있는 서버 루트를 선택해 주세요.');
          return;
        }
        worldDir = chosen;
        worldInspection = inspected;
        resetScan();
        recentWorlds = (await callBackend<{ worlds: RecentWorld[] }>('worlds.remember', { worldDir })).worlds;
        await loadBackups();
        info = t('월드를 선택했습니다. 호환성과 번역 후보를 스캔해 주세요.');
      }
    } catch (cause) {
      error = describe(cause);
    }
  }

  async function selectRecentWorld(item: RecentWorld): Promise<void> {
    if (!item.available || busy) return;
    error = '';
    try {
      const inspected = await callBackend<WorldInspection>('world.inspect', { worldDir: item.path });
      if (!inspected.validJavaWorld) {
        error = t('이 경로에서 지원 가능한 Minecraft Java 월드를 확인하지 못했습니다.');
        return;
      }
      worldDir = item.path;
      worldInspection = inspected;
      resetScan();
      recentWorlds = (await callBackend<{ worlds: RecentWorld[] }>('worlds.remember', { worldDir })).worlds;
      await loadBackups();
      info = t('최근 월드를 선택했습니다. 안전 검사를 위해 다시 스캔해 주세요.');
    } catch (cause) {
      error = describe(cause);
    }
  }

  async function forgetWorld(path: string): Promise<void> {
    if (busy) return;
    error = '';
    try {
      recentWorlds = (await callBackend<{ worlds: RecentWorld[] }>('worlds.forget', { worldDir: path })).worlds;
      if (worldDir === path) {
        worldDir = '';
        worldInspection = null;
        backups = [];
        resetScan();
      }
    } catch (cause) {
      error = describe(cause);
    }
  }

  async function saveSettings(): Promise<void> {
    const saved = await callBackend<{ settings: Settings; apiKeyStored: boolean }>('settings.set', {
      worldDir, provider, model, baseUrl, wireFormat, targetLanguage, stylePreset, stylePrompt, customSystemPrompt, uiLanguage,
      temperature, batchSize, requestTimeout, rpmLimit, tpmLimit, maxBatchRetries, resourcePackEnabled,
      ...(apiKey ? { apiKey } : {})
    });
    apiKeyStored = saved.apiKeyStored;
    apiKey = '';
  }

  async function saveSettingsFromButton(): Promise<void> {
    busy = 'loading';
    error = '';
    try {
      await saveSettings();
      resetScan();
      info = t('설정을 저장했습니다. 번역 전 스캔을 다시 실행해 주세요.');
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
      progressText = '';
    }
  }

  async function loadModels(): Promise<void> {
    busy = 'models';
    error = '';
    try {
      await saveSettings();
      const listed = await callBackend<{ models: { id: string; display_name?: string }[] }>('models.list', {
        provider, baseUrl
      });
      models = listed.models;
      info = models.length ? (uiLanguage === 'ko' ? `${models.length}개 모델을 불러왔습니다.` : uiLanguage === 'ja' ? `${models.length}件のモデルを読み込みました。` : `Loaded ${models.length} models.`) : t('제공된 모델 목록이 없습니다. 모델 ID를 직접 입력할 수 있습니다.');
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
      progressText = '';
    }
  }

  async function deleteApiKey(): Promise<void> {
    showDeleteKeyConfirm = false;
    busy = 'loading';
    error = '';
    try {
      await callBackend<{ deleted: boolean }>('credentials.delete', { provider });
      apiKey = '';
      apiKeyStored = false;
      info = uiLanguage === 'ko' ? `${provider} API 키를 운영체제 키체인에서 삭제했습니다.` : uiLanguage === 'ja' ? `${provider}のAPIキーを資格情報ストアから削除しました。` : `Deleted the ${provider} API key from the operating system credential store.`;
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
    }
  }

  async function startScan(): Promise<void> {
    if (!worldDir || busy) return;
    busy = 'scan';
    error = '';
    info = '';
    resetScan();
    try {
      await saveSettings();
      scan = await callBackend<ScanResult>('scan.start', { worldDir });
      candidateViewTotal = scan.candidateCount;
      candidateOffset = 0;
      if (scan.status === 'completed' && !scan.writeBlockers?.length) {
        info = uiLanguage === 'ko' ? `스캔 완료 · 번역 후보 ${scan.candidateCount.toLocaleString()}개 · 번역 API 요청 ${scan.providerRequests}회` : uiLanguage === 'ja' ? `スキャン完了 · 翻訳候補 ${scan.candidateCount.toLocaleString()}件 · APIリクエスト ${scan.providerRequests}回` : `Scan complete · ${scan.candidateCount.toLocaleString()} candidates · ${scan.providerRequests} translation API requests`;
      } else {
        error = t('이 월드는 현재 안전하게 번역할 수 없습니다. 아래 검사 결과를 확인해 주세요.');
      }
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
      progressText = '';
    }
  }

  async function loadCandidatePage(offset: number): Promise<void> {
    if (!scan || busy) return;
    busy = 'loading';
    error = '';
    try {
      const page = await callBackend<{
        candidates: NonNullable<ScanResult['candidates']>;
        hasMore: boolean;
        total: number;
      }>('candidates.page', {
        scanPlanId: scan.scanPlanId,
        offset: Math.max(0, offset),
        limit: 200,
        query: candidateQuery
      });
      scan.candidates = page.candidates;
      candidateViewTotal = page.total ?? candidateViewTotal;
      candidateOffset = Math.max(0, offset);
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
    }
  }

  async function searchCandidates(): Promise<void> {
    if (!scan || busy) return;
    busy = 'loading';
    error = '';
    try {
      const page = await callBackend<{
        candidates: NonNullable<ScanResult['candidates']>;
        total: number;
      }>('candidates.page', {
        scanPlanId: scan.scanPlanId,
        offset: 0,
        limit: 200,
        query: candidateQuery
      });
      scan.candidates = page.candidates;
      candidateViewTotal = page.total;
      candidateOffset = 0;
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
    }
  }

  async function cancelOperation(): Promise<void> {
    try {
      if (await cancelBackend()) info = t('취소를 요청했습니다. 현재 안전한 처리 지점에서 중단합니다.');
    } catch (cause) {
      error = describe(cause);
    }
  }

  async function startTranslation(): Promise<void> {
    showTranslateConfirm = false;
    if (!canTranslate || !scan) return;
    busy = 'translate';
    error = '';
    info = t('번역 중입니다. 이 창은 작업이 끝날 때까지 닫히지 않습니다.');
    try {
      await saveSettings();
      result = await callBackend<TranslationResult>(resumeRequested ? 'translate.resume' : 'translate.start', {
        worldDir,
        fingerprint: scan.fingerprint,
        scanPlanId: scan.scanPlanId,
        excludedCandidateIds,
        candidateOverrides,
        provider
      });
      if (result.status === 'completed' || result.status === 'partial') {
        resumeAvailable = false;
        resumeSavedAt = 0;
        await loadBackups();
        if (result.backupSetId) selectedBackupId = result.backupSetId;
        if (result.status === 'partial') error = t('일부만 번역했습니다. 번역하지 못한 문자열은 원문 그대로입니다.');
        info = uiLanguage === 'ko' ? `번역 완료 · 변경 파일 ${result.changedFileCount}개. 복원에 사용할 검증된 백업이 생성됐는지 결과를 확인하세요.` : uiLanguage === 'ja' ? `翻訳完了 · ${result.changedFileCount}件のファイルを変更しました。復元用の検証済みバックアップを確認してください。` : `Translation complete · ${result.changedFileCount} files changed. Confirm the verified backup in the result.`;
      } else if (result.status === 'cancelled') {
        info = t('취소했습니다. 이미 번역한 부분은 저장돼 있어 이어서 실행할 수 있습니다.');
      } else {
        error = failureMessage(result);
      }
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
      progressText = '';
      if (result && ['cancelled', 'needs_retry', 'failed'].includes(result.status)) {
        try {
          await loadResume();
        } catch (cause) {
          error = describe(cause);
        }
      }
    }
  }

  async function restoreSelected(): Promise<void> {
    showRestoreConfirm = false;
    if (!worldDir || !selectedBackupId || busy) return;
    busy = 'restore';
    error = '';
    try {
      const restored = await callBackend<{ status: string; recoverySetId: string }>('restore.start', {
        worldDir, backupSetId: selectedBackupId
      });
      resetScan();
      await loadBackups();
      info = uiLanguage === 'ko' ? `백업 복원 완료. 복원 직전 상태도 ${restored.recoverySetId} 백업으로 보존했습니다.` : uiLanguage === 'ja' ? `バックアップを復元しました。復元直前の状態は ${restored.recoverySetId} に保存しました。` : `Backup restored. The pre-restore state was saved as ${restored.recoverySetId}.`;
    } catch (cause) {
      error = describe(cause);
    } finally {
      busy = '';
    }
  }

  function acceptNotice(): void {
    localStorage.setItem('pomi.notice.v1', 'accepted');
    showNotice = false;
  }

  function modal(
    node: HTMLDialogElement,
    options: { dismissible: boolean; onDismiss: () => void }
  ): { destroy: () => void } {
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const cancel = (event: Event) => {
      event.preventDefault();
      if (options.dismissible) options.onDismiss();
    };
    node.addEventListener('cancel', cancel);
    node.showModal();
    queueMicrotask(() => node.querySelector<HTMLElement>('button, input, select, textarea')?.focus());
    return {
      destroy: () => {
        node.removeEventListener('cancel', cancel);
        if (node.open) node.close();
        previous?.focus();
      }
    };
  }
</script>

<svelte:head>
  <title>PomiTranslate — World Translator for Minecraft</title>
</svelte:head>

<a class="skip-link" href="#main-content">{t('본문으로 건너뛰기')}</a>
<div class="app-shell">
  <aside class="sidebar">
    <div class="brand">
      <img src="/images/wordmark.png" alt="PomiTranslate" class="wordmark" />
      <span>World Translator for Minecraft</span>
    </div>
    <nav aria-label={t('주 메뉴')}>
      <button class:active={page === 'world'} aria-current={page === 'world' ? 'page' : undefined} onclick={() => page = 'world'}>{t('월드 작업')}</button>
      <button class:active={page === 'settings'} aria-current={page === 'settings' ? 'page' : undefined} onclick={() => page = 'settings'}>{t('번역 설정')}</button>
      <button class:active={page === 'about'} aria-current={page === 'about' ? 'page' : undefined} onclick={() => page = 'about'}>{t('앱 정보')}</button>
    </nav>
    <div class="sidebar-note">
      <img src="/images/pomi.png" alt="" />
      <p>{t('스캔은 API를 호출하거나 월드 파일을 바꾸지 않습니다.')}</p>
    </div>
  </aside>

  <main id="main-content">
    <header class="topbar">
      <div>
        <p class="eyebrow">POMITRANSLATE</p>
        <h1>{page === 'world' ? t('월드 번역') : page === 'settings' ? t('번역 설정') : t('PomiTranslate 소개')}</h1>
      </div>
      <div class="operation-status">
        {#if busy === 'scan' || busy === 'translate'}<button class="secondary compact" onclick={cancelOperation}>{t('취소')}</button>{/if}
        <span class="phase">{busy ? t('작업 중') : t('준비됨')}</span>
      </div>
    </header>

    <div class="message error" role="alert" aria-atomic="true">{error}</div>
    <div class="message info" role="status" aria-live="polite" aria-atomic="true">{progressText || info}</div>

    {#if page === 'world'}
      <section class="panel world-panel" aria-labelledby="world-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{t('01 · 월드 선택')}</p>
            <h2 id="world-title">{t('번역할 Java 월드')}</h2>
            <p>{t('원본 폴더를 선택합니다. 월드를 앱 안으로 복사하지 않습니다.')}</p>
          </div>
          <button class="primary" onclick={chooseWorld} disabled={!!busy}>{t('월드 폴더 열기')}</button>
        </div>
        {#if worldDir}
          <div class="selected-world"><span>{worldInspection?.kind === 'server_root' ? t('서버 루트') : t('선택한 Java 월드')}</span><strong title={worldDir}>{worldDir}</strong>{#if worldInspection?.resourcePacks?.length}<small>resources.zip: {worldInspection.resourcePacks.length} · {resourcePackEnabled ? t('번역 대상에 포함') : t('설정에서 포함 가능')}</small>{/if}</div>
        {:else}
          <div class="empty-world">{t('아직 선택한 월드가 없습니다.')}</div>
        {/if}
        {#if recentWorlds.length}
          <div class="recent-worlds">
            <h3>{t('최근 월드')}</h3>
            {#each recentWorlds as item (item.path)}
              <div class="recent-world-row">
                <button class="recent-world" onclick={() => selectRecentWorld(item)} disabled={!item.available || !!busy}>
                  <strong>{item.name}</strong><span>{item.path}</span>{#if !item.available}<small>{t('폴더를 찾을 수 없음')}</small>{/if}
                </button>
                <button class="forget-world" aria-label={`${item.name} ${t('최근 목록에서 지우기')}`} onclick={() => forgetWorld(item.path)} disabled={!!busy}>{t('지우기')}</button>
              </div>
            {/each}
          </div>
        {/if}
      </section>

      <section class="panel" aria-labelledby="scan-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{t('02 · 호환성 및 범위 확인')}</p>
            <h2 id="scan-title">{t('먼저 스캔')}</h2>
            <p>{t('번역 후보 수와 쓰기 차단 형식을 확인합니다. API 키 없이 실행할 수 있습니다.')}</p>
          </div>
          <button class="primary" onclick={startScan} disabled={!worldDir || !!busy}>{busy === 'scan' ? t('스캔 중…') : t('Scan Only 실행')}</button>
        </div>
        {#if worldInspection}
          {@const compatibility = compatibilityStatus()}
          <div class:verified={compatibility.tone === 'verified'} class:warning={compatibility.tone === 'warning'} class:unsupported={compatibility.tone === 'unsupported'} class="compatibility-state">
            <div><span>{t('호환성 상태')}</span><strong>{compatibility.label}</strong></div>
            <p>{compatibility.detail}</p>
            {#if worldInspection.dataVersions?.length}
              <ul aria-label={t('월드 DataVersion 정보')}>
                {#each worldInspection.dataVersions as item}<li><span>{item.world}</span><strong>{item.dataVersion ?? t('읽을 수 없음')}</strong></li>{/each}
              </ul>
            {/if}
          </div>
        {/if}
        {#if scan}
          <div class="scan-summary">
            <div><span>{t('스캔 상태')}</span><strong>{scan.status === 'completed' ? t('완료') : scan.status}</strong></div>
            <div><span>{t('고유 번역 후보')}</span><strong>{scan.candidateCount.toLocaleString()}</strong></div>
            <div><span>{t('API 요청')}</span><strong>{scan.providerRequests}</strong></div>
          </div>
          {#if scan.writeBlockers?.length}
            <div class="compatibility-warning"><strong>{t('쓰기 차단')}</strong><ul>{#each scan.writeBlockers as blocker}<li>{blockerLabel(blocker)}</li>{/each}</ul></div>
          {/if}
          {#if scan.errors?.length}
            <div class="compatibility-warning"><strong>{t('검사 오류')}</strong><ul>{#each scan.errors as issue}<li>{issue.message || issue.scope}</li>{/each}</ul></div>
          {/if}
          {#if scan.candidates?.length}
            <div class="candidate-list">
              <div class="candidate-heading"><h3>{t('번역 후보 검토')}</h3><span>{t('포함')} {includedCandidateCount} · {t('제외')} {excludedCandidateIds.length} · {t('직접 번역')} {manualOverrideCount}</span></div>
              <div class="candidate-search">
                <input bind:value={candidateQuery} onkeydown={(event) => event.key === 'Enter' && searchCandidates()} placeholder={t('원문 검색')} aria-label={t('번역 후보 원문 검색')} />
                <select bind:value={candidateFilter} aria-label={t('번역 후보 필터')}><option value="all">{t('전체')}</option><option value="included">{t('포함')}</option><option value="excluded">{t('제외')}</option><option value="manual">{t('직접 번역')}</option></select>
                <button class="secondary" onclick={searchCandidates} disabled={!!busy}>{t('검색')}</button>
              </div>
              {#if candidateQuery}<p class="candidate-result-count">{t('검색 결과')} {candidateViewTotal.toLocaleString()}</p>{/if}
              <div class="candidate-scroll">
                {#each visibleCandidates as candidate (candidate.id)}
                  <div class="candidate-row">
                    <input
                      type="checkbox"
                      aria-label={`${candidate.source} ${t('번역에 포함')}`}
                      checked={!excludedCandidateIds.includes(candidate.id)}
                      onchange={(event) => setCandidateIncluded(candidate.id, event.currentTarget.checked)}
                    />
                    <div class="candidate-content">
                      <span>{candidate.source}</span>
                      {#if candidate.location || (candidate.kind && candidate.kind !== 'world.text')}<small>{candidate.kind && candidate.kind !== 'world.text' ? candidate.kind : ''}{candidate.location ? ` · ${candidate.location}` : ''}</small>{/if}
                      <input
                        class="manual-translation"
                        type="text"
                        value={candidateOverrides[candidate.id] || ''}
                        oninput={(event) => setCandidateOverride(candidate.id, event.currentTarget.value)}
                        placeholder={t('직접 번역 입력 (입력하면 API 대신 사용)')}
                        disabled={excludedCandidateIds.includes(candidate.id)}
                        aria-label={`${candidate.source} ${t('직접 번역')}`}
                      />
                    </div>
                  </div>
                {/each}
              </div>
              {#if candidateViewTotal > 200}
                <div class="candidate-pages">
                  <button class="secondary" onclick={() => loadCandidatePage(candidateOffset - 200)} disabled={!!busy || candidateOffset === 0}>{t('이전')}</button>
                  <span>{(candidateOffset + 1).toLocaleString()}–{Math.min(candidateOffset + scan.candidates.length, candidateViewTotal).toLocaleString()} / {candidateViewTotal.toLocaleString()}</span>
                  <button class="secondary" onclick={() => loadCandidatePage(candidateOffset + 200)} disabled={!!busy || candidateOffset + scan.candidates.length >= candidateViewTotal}>{t('다음')}</button>
                </div>
              {/if}
            </div>
          {/if}
        {:else}
          <div class="empty-state">{t('스캔을 실행하면 검사 결과가 이곳에 표시됩니다.')}</div>
        {/if}
      </section>

      <section class="panel" aria-labelledby="translate-title">
        <div class="section-heading">
          <div>
            <p class="eyebrow">{t('03 · 번역 및 복원')}</p>
            <h2 id="translate-title">{t('검토 후 번역')}</h2>
            <p>{t('선택한 제공사로 후보 텍스트를 전송합니다. API 사용료가 발생할 수 있습니다.')}</p>
          </div>
          <button class="primary dark" onclick={() => { resumeRequested = resumeAvailable; showTranslateConfirm = true; }} disabled={!canTranslate}>{resumeAvailable ? t('중단 작업 이어서') : t('번역 실행')}</button>
        </div>
        <div class="run-detail">
          <div><span>{t('대상 언어')}</span><strong>{targetLanguage}</strong></div>
          <div><span>{t('제공사 · 모델')}</span><strong>{manualOnly ? t('직접 번역만 적용') : `${provider} · ${model || t('모델 미설정')}`}</strong></div>
          <div><span>{t('최소 번역 요청')}</span><strong>{requestEstimate()}</strong></div>
          <div><span>{t('백업')}</span><strong>{t('변경 전 파일 검증')}</strong></div>
        </div>
        {#if resumeAvailable}<div class="resume-notice"><strong>{t('이어 할 작업 있음')}</strong><span>{resumeSavedAt ? new Date(resumeSavedAt * 1000).toLocaleString(uiLanguage) : t('안전하게 취소된 작업')}{resumeTranslated ? ` · ${t('번역 완료 {count}개 저장됨', { count: resumeTranslated })}` : ''}</span><small>{t('월드 파일이나 번역 설정이 바뀌면 재개되지 않습니다.')}</small></div>{/if}
        {#if result}
          <div class="result-box"><strong>{t('최근 작업')}: {statusLabel(result.status)}</strong><span>{t('변경 파일')} {result.changedFileCount} · {t('후보')} {result.candidateCount}</span>{#if result.translation?.failed}<span>{t('번역하지 못한 문자열')} {result.translation.failed}</span>{/if}{#if result.translation?.kept_original}<span>{t('서식 기호 보호로 원문 유지')} {result.translation.kept_original}</span>{/if}{#if result.warnings?.length}<span>{t('경고')} {result.warnings.length}</span>{/if}</div>
        {/if}
        {#if backups.length}
          <div class="backup-history">
            <h3>{t('백업 기록')}</h3>
            <label>{t('복원할 백업')}
              <select bind:value={selectedBackupId}>
                {#each backups as backup}
                  <option value={backup.backupSetId}>
                    {new Date(backup.createdAt).toLocaleString(uiLanguage)} · {backup.fileCount} {t('변경 파일')}{backup.verified ? ` · ${t('검증됨')}` : ''}
                  </option>
                {/each}
              </select>
            </label>
            <button class="secondary danger" onclick={() => showRestoreConfirm = true} disabled={!!busy || !selectedBackupId}>{t('선택한 백업 복원')}</button>
          </div>
        {/if}
      </section>
    {:else if page === 'settings'}
      <section class="panel settings-panel" aria-labelledby="settings-title">
        <div class="section-heading"><div><p class="eyebrow">{t('모델 및 언어')}</p><h2 id="settings-title">{t('번역 설정')}</h2><p>{t('API 키는 운영체제 키체인에 저장됩니다.')}</p></div></div>
        <div class="form-grid">
          <label>{t('화면 언어')}<select bind:value={uiLanguage} onchange={updateUiLanguage}><option value="ko">{t('한국어')}</option><option value="en">{t('영어')}</option><option value="ja">{t('일본어')}</option></select></label>
          <label>{t('API 제공사')}<select bind:value={provider} onchange={resetScan}>{#each providerChoices as choice}<option value={choice.id}>{choice.label}</option>{/each}</select></label>
          <label>{t('모델 ID')}<input bind:value={model} oninput={resetScan} list="model-list" placeholder={t('모델 ID 입력')} /></label>
          <datalist id="model-list">{#each models as item}<option value={item.id}>{item.display_name || item.id}</option>{/each}</datalist>
          <label>{t('대상 언어')}<input bind:value={targetLanguage} oninput={resetScan} /></label>
          <label>{t('스타일')}<select bind:value={stylePreset} onchange={resetScan}><option value="neutral">{t('중립')}</option><option value="casual">{t('친근하게')}</option><option value="formal">{t('격식 있게')}</option><option value="polite">{t('정중하게')}</option><option value="story">{t('이야기풍')}</option><option value="custom">{t('사용자 시스템 프롬프트')}</option></select></label>
          {#if provider === 'custom'}<label>{t('사용자 지정 API URL')}<input bind:value={baseUrl} oninput={resetScan} placeholder="https://example.com/v1" /></label><label>{t('호환 형식')}<select bind:value={wireFormat} onchange={resetScan}><option value="openai">OpenAI Chat</option><option value="anthropic">Anthropic Messages</option></select></label>{/if}
          <label class="full">{t('API 키')} <span class="field-hint">{apiKeyStored ? t('키체인에 저장된 키가 있습니다.') : t('저장된 키가 없습니다.')}</span><input type="password" bind:value={apiKey} autocomplete="off" placeholder={t('새 키를 입력할 때만 작성')} /></label>
        </div>
        <details class="advanced-settings">
          <summary>{t('고급 번역 설정')}</summary>
          <div class="form-grid">
            <label class="full">{t('추가 스타일 지시')}<textarea bind:value={stylePrompt} oninput={resetScan} rows="3" placeholder={t('기본 스타일에 덧붙일 지시')}></textarea></label>
            {#if stylePreset === 'custom'}<label class="full">{t('사용자 시스템 프롬프트')}<textarea bind:value={customSystemPrompt} oninput={resetScan} rows="5" placeholder={t('번역에 사용할 전체 시스템 프롬프트')}></textarea></label>{/if}
            <label>{t('온도')} <span class="field-hint">0–2</span><input type="number" min="0" max="2" step="0.1" bind:value={temperature} oninput={resetScan} /></label>
            <label>{t('배치 크기')} <span class="field-hint">1–200</span><input type="number" min="1" max="200" step="1" bind:value={batchSize} oninput={resetScan} /></label>
            <label>{t('분당 요청 제한')} <span class="field-hint">{t('0은 제한 없음')}</span><input type="number" min="0" max="10000" step="1" bind:value={rpmLimit} oninput={resetScan} /></label>
            <label>{t('분당 토큰 제한')} <span class="field-hint">{t('0은 제한 없음')}</span><input type="number" min="0" max="10000000" step="100" bind:value={tpmLimit} oninput={resetScan} /></label>
            <label>{t('요청 제한 시간(초)')} <span class="field-hint">5–600</span><input type="number" min="5" max="600" step="1" bind:value={requestTimeout} oninput={resetScan} /></label>
            <label>{t('배치 재시도')} <span class="field-hint">0–10</span><input type="number" min="0" max="10" step="1" bind:value={maxBatchRetries} oninput={resetScan} /></label>
            <label class="check-field full"><input type="checkbox" bind:checked={resourcePackEnabled} onchange={resetScan} /><span>{t('월드 안의 resources.zip 언어 파일도 번역')}</span></label>
            <p class="field-note full">{t('리소스팩 ZIP은 월드 폴더 안에 있을 때만 포함됩니다. 변경 전 같은 백업 세트에 보존됩니다.')}</p>
          </div>
        </details>
        <div class="settings-actions"><button class="secondary danger" onclick={() => showDeleteKeyConfirm = true} disabled={!!busy || !apiKeyStored}>{t('저장된 키 삭제')}</button><button class="secondary" onclick={loadModels} disabled={!!busy}>{busy === 'models' ? t('조회 중…') : t('모델 목록 조회')}</button><button class="primary" onclick={saveSettingsFromButton} disabled={!!busy}>{t('설정 저장')}</button></div>
      </section>
    {:else}
      <section class="panel about-panel">
        <img src="/images/pomi.png" alt={t('Pomi 마스코트')} />
        <div><p class="eyebrow">WORLD TRANSLATOR FOR MINECRAFT</p><h2>PomiTranslate</h2><p>{t('Java Edition 월드의 플레이어 표시 텍스트를 찾아 번역하는 무료 오픈소스 도구입니다.')}</p><p>{t('비공식 제품이며 Mojang/Microsoft와 관련이 없습니다. 번역한 맵의 재배포에는 원작자의 허락이 필요합니다.')}</p><p>{t('월드는 로컬에서 처리되지만, 번역할 텍스트는 선택한 API 제공사로 전송됩니다.')}</p><p class="small">0.1.0 · GitHub: kim0040/Minecraft-World-Translator</p></div>
      </section>
    {/if}
  </main>
</div>

{#if showNotice}
  <dialog class="modal" use:modal={{ dismissible: false, onDismiss: () => {} }} aria-labelledby="notice-title"><p class="eyebrow">{t('처음 시작하기 전에')}</p><h2 id="notice-title">{t('PomiTranslate 사용 안내')}</h2><p>{t('비공식 오픈소스 도구이며 Mojang/Microsoft와 관련이 없습니다.')}</p><p>{t('월드 파일을 수정하므로 중요한 월드는 별도로 백업해 주세요. 번역할 텍스트는 선택한 AI API 제공사로 전송되며 요금이 발생할 수 있습니다.')}</p><button class="primary" onclick={acceptNotice}>{t('확인하고 시작')}</button></dialog>
{/if}

{#if showTranslateConfirm}
  <dialog class="modal" use:modal={{ dismissible: true, onDismiss: () => showTranslateConfirm = false }} aria-labelledby="confirm-title"><p class="eyebrow">{resumeRequested ? t('중단 작업 재개 확인') : t('번역 실행 확인')}</p><h2 id="confirm-title">{resumeRequested ? t('안전한 지점부터 이어서 번역할까요?') : t('이 월드를 번역할까요?')}</h2><dl><dt>{t('월드')}</dt><dd>{worldDir}</dd><dt>{t('대상 언어')}</dt><dd>{targetLanguage}</dd><dt>{t('제공사 · 모델')}</dt><dd>{manualOnly ? t('직접 번역만 적용') : `${provider} · ${model}`}</dd><dt>{t('외부로 전송될 고유 텍스트')}</dt><dd>{resumeRequested ? t('재개 시 남은 수 확인 불가') : externalCandidateCount}</dd><dt>{t('예상 요청·비용')}</dt><dd>{resumeRequested ? `${t('재개 시 남은 요청 확인 불가')} · ${t('비용 확인 불가 · 제공사 정책에 따라 청구')}` : estimatedRequestCount === 0 ? t('API 요청 없음') : `${t('최소 {count}회 · 파일 경계·재시도 제외', { count: estimatedRequestCount })} · ${t('비용 확인 불가 · 제공사 정책에 따라 청구')}`}</dd><dt>{t('백업')}</dt><dd>{resumeRequested ? t('기존 검증 백업 세트를 이어서 사용') : t('쓰기 전 변경 파일을 백업하고 검증')}</dd></dl><p class="small">{t('이미 전송된 API 요청에는 요금이 발생했을 수 있습니다. 원작자의 허락 없이 번역본을 재배포하지 마세요.')}</p><div class="modal-actions"><button class="secondary" onclick={() => showTranslateConfirm = false}>{t('취소')}</button><button class="primary dark" onclick={startTranslation}>{resumeRequested ? t('이어서 번역') : t('번역 시작')}</button></div></dialog>
{/if}

{#if showRestoreConfirm}
  <dialog class="modal" use:modal={{ dismissible: true, onDismiss: () => showRestoreConfirm = false }} aria-labelledby="restore-title"><p class="eyebrow">{t('백업 복원')}</p><h2 id="restore-title">{t('선택한 백업으로 되돌릴까요?')}</h2><p>{t('현재 월드의 변경 파일을 복원 전 recovery 백업으로 먼저 보존한 뒤, 선택한 시점의 파일로 교체합니다.')}</p><p class="small">{t('백업 ID')}: {selectedBackupId}</p><div class="modal-actions"><button class="secondary" onclick={() => showRestoreConfirm = false}>{t('취소')}</button><button class="primary danger-fill" onclick={restoreSelected}>{t('복원')}</button></div></dialog>
{/if}

{#if showDeleteKeyConfirm}
  <dialog class="modal" use:modal={{ dismissible: true, onDismiss: () => showDeleteKeyConfirm = false }} aria-labelledby="delete-key-title"><p class="eyebrow">{t('자격 증명 삭제')}</p><h2 id="delete-key-title">{provider} {t('API 키를 삭제할까요?')}</h2><p>{t('운영체제 키체인에 저장된 현재 제공사의 키를 삭제합니다. 다시 사용하려면 새 키를 입력해야 합니다.')}</p><div class="modal-actions"><button class="secondary" onclick={() => showDeleteKeyConfirm = false}>{t('취소')}</button><button class="primary danger-fill" onclick={deleteApiKey}>{t('키 삭제')}</button></div></dialog>
{/if}
