(() => {
  const callbacks = new Map();
  const listeners = new Map();
  let callbackId = 0;
  let eventId = 0;

  const candidates = [
    { id: 'welcome', source: 'Welcome to Roguefire', kind: 'sign', kinds: { sign: 3 }, occurrences: 3, locations: [{ holder: 'minecraft:oak_sign', pos: [12, 64, -8], chunk: [0, -1], detail: 'front:1' }] },
    { id: 'shop', source: 'The Lost Key Shop', kind: 'text_display', kinds: { text_display: 1 }, occurrences: 1, locations: [{ holder: 'minecraft:text_display', pos: [24, 70, 11], chunk: [1, 0], detail: 'base' }] },
    { id: 'book', source: 'Find the keeper beyond the old bridge.', kind: 'book_page', kinds: { book_page: 2 }, occurrences: 2, locations: [{ holder: 'minecraft:written_book', pos: [30, 65, 9], chunk: [1, 0], detail: 'page:3' }] },
    { id: 'lore', source: 'A blade that remembers every battle', kind: 'item_lore', kinds: { item_lore: 8 }, occurrences: 8, locations: [{ holder: 'minecraft:diamond_sword', pos: [8, 63, 20], chunk: [0, 1], detail: 'line:1' }] },
    { id: 'tellraw', source: 'You are not ready yet.', kind: 'command', kinds: { command: 1 }, occurrences: 1, locations: [{ holder: 'minecraft:command_block', pos: [-4, 58, 42], chunk: [-1, 2], detail: 'base' }] },
    { id: 'merchant', source: 'Merchant of the Northern Gate', kind: 'entity_name', kinds: { entity_name: 2 }, occurrences: 2, locations: [{ holder: 'minecraft:villager', pos: [101, 67, -33], chunk: [6, -3], detail: 'custom' }] }
  ];
  const worldDir = '/private/tmp/pomi-eval/Roguefire — a deliberately long translated world folder name';
  const inspection = {
    validJavaWorld: true,
    kind: 'java_world',
    childWorlds: [],
    regionDirs: ['region', 'entities', 'DIM-1/region', 'DIM1/region', 'dimensions/roguefire/sky/region'],
    resourcePacks: [`${worldDir}/resources.zip`],
    dataVersions: [{ world: 'Roguefire', dataVersion: 4189 }],
    writeBlockers: []
  };
  const backups = [
    { backupSetId: '2026-09-29T16-24-18Z-translation', createdAt: '2026-09-29T16:24:18+09:00', fileCount: 69, verified: true, kind: 'translation', sizeBytes: 1843200, inWorldFolder: false },
    { backupSetId: 'legacy-2026-09-28T12-10-00', createdAt: '2026-09-28T12:10:00+09:00', fileCount: 12, verified: false, kind: 'recovery', sizeBytes: 512000, inWorldFolder: true }
  ];
  const settings = {
    provider: 'openrouter', model: 'xiaomi/mimo-v2.6-flash', base_url: '', wire_format: 'openai',
    target_language: '한국어', style_preset: 'neutral', style_prompt: '', custom_system_prompt: '',
    temperature: 0.3, batch_size: 40, request_timeout: 120, rpm_limit: 0, tpm_limit: 0,
    max_batch_retries: 3, concurrency: 4, resource_pack_enabled: false,
    skip_target_language_text: true, ui_language: 'ko', last_world_dir: worldDir
  };
  const estimate = {
    candidateCount: candidates.length, requests: 1, sourceChars: 180, inputTokens: 720,
    outputTokens: 240, price: { input: 0.00000015, output: 0.0000006, perMillionInput: 0.15, perMillionOutput: 0.6 },
    cost: { low: 0.000252, high: 0.000504 }
  };
  const scan = {
    status: 'completed', candidateCount: candidates.length, occurrenceCount: 17,
    kinds: { sign: 1, text_display: 1, book_page: 1, item_lore: 1, command: 1, entity_name: 1 },
    providerRequests: 0, fingerprint: 'fixture-world-fingerprint', scanPlanId: 'fixture-scan-plan', dryRun: true,
    writeBlockers: [], errors: [], warnings: [], requestEstimate: 1, estimate, candidates,
    coverage: [
      { id: 'regions', scanned: true, present: true, count: 6 },
      { id: 'entities', scanned: true, present: true, count: 2 },
      { id: 'resource_pack', scanned: false, present: true, count: 84 },
      { id: 'datapacks', scanned: false, present: true, count: 427 },
      { id: 'command_storage', scanned: false, present: true, count: 31 },
      { id: 'playerdata', scanned: false, present: true, count: 4 }
    ]
  };

  function scenario() {
    return new URLSearchParams(location.search).get('scenario') || 'selected';
  }
  function emit(name, message) {
    for (const listener of listeners.values()) {
      if (listener.event === name) callbacks.get(listener.handler)?.({ event: name, id: listener.id, payload: message });
    }
  }
  function ok(request, payload) {
    return { v: 1, id: request.id, type: 'response.ok', payload };
  }
  function resumePayload() {
    return {
      available: true, scanPlanId: scan.scanPlanId, fingerprint: scan.fingerprint,
      candidateCount: candidates.length, candidates, excludedCandidateIds: ['tellraw'],
      candidateOverrides: { shop: '잃어버린 열쇠 상점' }, savedAt: 1790672400,
      status: 'needs_retry', translatedCount: 2
    };
  }
  function filteredPage(body) {
    let rows = [...candidates];
    const query = String(body.query || '').trim().toLocaleLowerCase();
    if (query) rows = rows.filter((item) => item.source.toLocaleLowerCase().includes(query));
    if (body.kind) rows = rows.filter((item) => item.kind === body.kind);
    const excluded = new Set(body.excludedCandidateIds || []);
    const manual = new Set(body.overrideCandidateIds || []);
    if (body.state === 'included') rows = rows.filter((item) => !excluded.has(item.id));
    if (body.state === 'excluded') rows = rows.filter((item) => excluded.has(item.id));
    if (body.state === 'manual') rows = rows.filter((item) => manual.has(item.id));
    if (body.sort === 'source') rows.sort((a, b) => a.source.localeCompare(b.source));
    if (body.sort === 'count') rows.sort((a, b) => b.occurrences - a.occurrences);
    if (body.sort === 'kind') rows.sort((a, b) => a.kind.localeCompare(b.kind));
    const offset = Number(body.offset || 0);
    const limit = Number(body.limit || 200);
    return { candidates: rows.slice(offset, offset + limit), offset, total: rows.length, hasMore: offset + limit < rows.length, kinds: scan.kinds };
  }
  function resultPayload(failed) {
    return failed ? {
      status: 'needs_retry', candidateCount: candidates.length, changedFileCount: 0, providerRequests: 3,
      backupSetId: backups[0].backupSetId,
      errors: [{ code: 'PROVIDER_OUTAGE', message: 'Provider requests failed repeatedly.' }],
      translation: { unique: 6, translated: 2, failed: 4, kept_original: 4, unchanged: 0 },
      translationFailures: [{ source: 'Welcome to Roguefire', reason: 'Provider unavailable' }],
      keptOriginalSamples: ['Welcome to Roguefire'],
      usage: { prompt_tokens: 680, completion_tokens: 118, cost: 0.0002, cost_reported: true }
    } : {
      status: 'completed', candidateCount: candidates.length, changedFileCount: 8, providerRequests: 1,
      backupSetId: backups[0].backupSetId,
      translation: { unique: 6, translated: 5, failed: 0, kept_original: 0, unchanged: 1 },
      translationSamples: [
        { source: 'Welcome to Roguefire', translated: '로그파이어에 오신 것을 환영합니다' },
        { source: 'The Lost Key Shop', translated: '잃어버린 열쇠 상점' }
      ],
      usage: { prompt_tokens: 712, completion_tokens: 231, cost: 0.00025, cost_reported: true }
    };
  }

  async function sidecar(request) {
    const type = request.type;
    const body = request.payload || {};
    const current = scenario();
    if (type === 'app.bootstrap') {
      const empty = current === 'empty';
      const resumed = ['scanned', 'review', 'run', 'run-progress', 'result-success', 'result-failed', 'dark-review'].includes(current);
      return ok(request, {
        notices: { firstLaunch: '', about: '', backupWarning: '', apiWarning: '' }, settings: { ...settings, last_world_dir: empty ? '' : worldDir },
        apiKeyStored: true, worlds: empty ? [] : [{ path: worldDir, name: 'Roguefire', lastOpened: 1790672400, available: true }],
        worldInspection: empty ? null : inspection, backups: empty ? [] : backups,
        resume: resumed ? resumePayload() : { available: false }
      });
    }
    if (type === 'settings.set') return ok(request, { settings: { ...settings, ...body }, apiKeyStored: true });
    if (type === 'world.inspect') return ok(request, inspection);
    if (type === 'worlds.remember') return ok(request, { worlds: [{ path: worldDir, name: 'Roguefire', lastOpened: 1790672400, available: true }] });
    if (type === 'worlds.forget') return ok(request, { worlds: [] });
    if (type === 'resume.status') return ok(request, { available: false });
    if (type === 'backups.list') return ok(request, { backups });
    if (type === 'estimate.get') return ok(request, estimate);
    if (type === 'candidates.page') return ok(request, filteredPage(body));
    if (type === 'models.list') return ok(request, { models: [{ id: 'xiaomi/mimo-v2.6-flash', display_name: 'MiMo V2.6 Flash' }] });
    if (type === 'scan.start') {
      if (current === 'scan-running') {
        setTimeout(() => emit('pomi-progress', { v: 1, id: request.id, type: 'scan.progress', payload: { event: 'scan_start', total_files: 96 } }), 50);
        setTimeout(() => emit('pomi-progress', { v: 1, id: request.id, type: 'scan.progress', payload: { event: 'file_start', phase: 'collect', index: 37, total: 96 } }), 120);
        return new Promise((resolve) => setTimeout(() => resolve(ok(request, scan)), 60000));
      }
      return ok(request, scan);
    }
    if (type === 'translate.start' || type === 'translate.resume') {
      if (current === 'run-progress') {
        setTimeout(() => emit('pomi-progress', { v: 1, id: request.id, type: 'translate.progress', payload: { event: 'phase_start', phase: 'translate', total: 6, requests_estimate: 1 } }), 50);
        setTimeout(() => emit('pomi-progress', { v: 1, id: request.id, type: 'translate.progress', payload: { event: 'translation_progress', completed: 4, total: 6, failed: 0, batch: 1, batches: 2, requests: 1 } }), 120);
        return new Promise((resolve) => setTimeout(() => resolve(ok(request, resultPayload(false))), 60000));
      }
      return ok(request, resultPayload(current === 'result-failed'));
    }
    if (type === 'restore.start') return ok(request, { status: 'completed', recoverySetId: 'recovery-before-restore' });
    if (type === 'credentials.delete') return ok(request, { deleted: true });
    return ok(request, {});
  }

  window.__TAURI_INTERNALS__ = {
    metadata: { currentWindow: { label: 'main' }, currentWebview: { label: 'main' } },
    plugins: { path: { sep: '/', delimiter: ':' } },
    transformCallback(callback) { const id = ++callbackId; callbacks.set(id, callback); return id; },
    unregisterCallback(id) { callbacks.delete(id); },
    runCallback(id, data) { callbacks.get(id)?.(data); },
    convertFileSrc(path) { return path; },
    async invoke(command, args = {}) {
      if (command === 'plugin:event|listen') { const id = ++eventId; listeners.set(id, { id, event: args.event, handler: args.handler }); return id; }
      if (command === 'plugin:event|unlisten') { listeners.delete(args.eventId); return null; }
      if (command === 'plugin:dialog|open') return null;
      if (command === 'credential_status') return true;
      if (command === 'operation_active') return false;
      if (command === 'cancel_active') return true;
      if (command === 'sidecar_request') return sidecar(args.request);
      throw new Error(`Unsupported fixture command: ${command}`);
    }
  };
  localStorage.setItem('pomi.notice.v1', 'accepted');
  localStorage.setItem('pomi.theme.v1', scenario() === 'dark-review' ? 'dark' : 'light');
})();
