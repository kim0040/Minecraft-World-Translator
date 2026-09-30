import { beforeEach, describe, expect, it, vi } from 'vitest';

const { backend } = vi.hoisted(() => ({ backend: vi.fn() }));
vi.mock('../../src/lib/api', async () => ({
  ...await vi.importActual<typeof import('../../src/lib/api')>('../../src/lib/api'),
  callBackend: backend
}));
import { AppState } from '../../src/lib/app.svelte';
import { BackendError } from '../../src/lib/api';
import { publicSettingsForExport } from '../../src/lib/settings';

beforeEach(() => backend.mockReset());
describe('settings recovery', () => {
  it('external ZIP selection invalidates the reviewed scan and stays out of portable settings export', async () => {
    const app = new AppState();
    const before = { ...app.settings, external_resource_pack_paths: [] };
    app.scan = { status: 'completed', candidateCount: 1, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    app.settings = { ...before, external_resource_pack_paths: ['/private/tmp/synthetic-pack.zip'] };
    backend.mockResolvedValueOnce({ settings: app.settings, apiKeyStored: true, credentialMode: 'local' });
    expect(await app.saveSettings(before)).toBe(true);
    expect(app.scan).toBeNull();
    expect(backend).toHaveBeenCalledWith('settings.set', expect.objectContaining({ externalResourcePackPaths: ['/private/tmp/synthetic-pack.zip'] }));
    expect(publicSettingsForExport(app.settings)).not.toHaveProperty('external_resource_pack_paths');
  });
  it('deleting a draft provider credential does not apply draft preferences or alter another provider status', async () => {
    const app = new AppState();
    app.apiKeyStored = true;
    const before = { ...app.settings };
    backend.mockResolvedValueOnce({ deleted: true });
    expect(await app.deleteApiKey('custom')).toBe(true);
    expect(backend).toHaveBeenCalledWith('credentials.delete', { provider: 'custom' });
    expect(app.settings).toEqual(before);
    expect(app.apiKeyStored).toBe(true);
    backend.mockRejectedValueOnce(new BackendError('delete failed', 'TRANSPORT'));
    expect(await app.deleteApiKey()).toBe(false);
    expect(app.apiKeyStored).toBe(true);
  });

  it('requires a stored credential for API translation while allowing manual-only work', () => {
    const app = new AppState();
    app.settings.model = 'fixture';
    app.scan = { status: 'completed', candidateCount: 1, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    expect(app.canRun).toBe(false);
    app.overrides = { first: '직접 번역' };
    expect(app.canRun).toBe(true);
  });
  it('ignores out-of-order estimates and keeps unavailable prices unknown', async () => {
    const app = new AppState();
    app.scan = { status: 'completed', candidateCount: 2, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    let oldReply!: (value: unknown) => void;
    backend.mockImplementationOnce(() => new Promise((resolve) => { oldReply = resolve; }));
    const oldRequest = app.loadEstimate();
    app.setIncluded('first', false);
    backend.mockResolvedValueOnce({ requests: 1, cost: { low: 1, high: 2 } });
    await app.loadEstimate();
    oldReply({ requests: 2, cost: { low: 5, high: 10 } });
    await oldRequest;
    expect(app.estimate?.requests).toBe(1);
    backend.mockRejectedValueOnce(new BackendError('unavailable', 'TRANSPORT'));
    await app.loadEstimate();
    expect(app.estimate).toBeNull();
  });
  it('exports only public settings even when backend objects contain unknown secret fields', () => {
    const app = new AppState();
    const unsafe = { ...app.settings, apiKey: 'synthetic-secret', masterKey: 'synthetic-master', credentialMode: 'local',
      scan_options: { ...app.settings.scan_options, api_key: 'synthetic-nested-secret' } };
    const exported = publicSettingsForExport(unsafe);
    expect(JSON.stringify(exported)).not.toMatch(/synthetic|apiKey|api_key|masterKey|credentialMode/);
    expect(exported.scan_options.translate_signs).toBe(true);
    expect(exported.scan_options.region_dirs).not.toBe(unsafe.scan_options.region_dirs);
  });
  it('restores verified previous preferences and keeps the reviewed scan on vault failure', async () => {
    const app = new AppState();
    const before = { ...app.settings, model: 'old' };
    const scan = { status: 'completed', candidateCount: 1, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    app.scan = scan;
    app.settings = { ...before, model: 'new' };
    app.credentialMode = 'session';
    backend.mockRejectedValueOnce(new BackendError('fixture failure', 'CREDENTIAL_SAVE_FAILED'));
    expect(await app.saveSettings(before, '', 'local')).toBe(false);
    expect(app.settings.model).toBe('old');
    expect(app.credentialMode).toBe('local');
    expect(app.scan?.scanPlanId).toBe('fixture');
    expect(backend).toHaveBeenCalledTimes(1);
  });

  it('reloads authoritative preferences after uncertain recovery and invalidates the scan', async () => {
    const app = new AppState();
    const before = { ...app.settings, model: 'old' };
    app.scan = { status: 'completed', candidateCount: 1, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    app.settings = { ...before, model: 'draft' };
    backend.mockRejectedValueOnce(new BackendError('unknown write', 'SETTINGS_RECONCILIATION_REQUIRED'));
    backend.mockResolvedValueOnce({ settings: { ...before, model: 'actual' }, apiKeyStored: false, credentialMode: 'local' });
    expect(await app.saveSettings(before)).toBe(false);
    expect(app.settings.model).toBe('actual');
    expect(app.scan).toBeNull();
    expect(app.settingsRecoveryRequired).toBe(false);
    expect(backend).toHaveBeenLastCalledWith('settings.get');
  });

  it('blocks translation when neither rollback nor authoritative reload can be verified', async () => {
    const app = new AppState();
    const before = { ...app.settings };
    backend.mockRejectedValueOnce(new BackendError('unknown write', 'SETTINGS_RECONCILIATION_REQUIRED'));
    backend.mockRejectedValueOnce(new BackendError('reload failed', 'TRANSPORT'));
    expect(await app.saveSettings(before)).toBe(false);
    expect(app.settingsRecoveryRequired).toBe(true);
    expect(app.canRun).toBe(false);
    await app.startTranslate();
    expect(backend).toHaveBeenCalledTimes(2);
  });

  it('applies the settings acknowledged by the core rather than the unnormalized draft', async () => {
    const app = new AppState();
    const before = { ...app.settings };
    app.settings = { ...before, model: 'draft' };
    backend.mockResolvedValueOnce({ settings: { ...before, model: 'actual' }, apiKeyStored: true, credentialMode: 'local' });
    expect(await app.saveSettings(before)).toBe(true);
    expect(app.settings.model).toBe('actual');
    expect(app.apiKeyStored).toBe(true);
  });

  it('requires a new key after uncertain OS recovery even when public settings reload succeeds', async () => {
    const app = new AppState();
    const before = { ...app.settings };
    backend.mockRejectedValueOnce(new BackendError('unknown OS write', 'CREDENTIAL_SAVE_UNCERTAIN'));
    backend.mockResolvedValueOnce({ settings: before, apiKeyStored: true, credentialMode: 'keychain' });
    expect(await app.saveSettings(before)).toBe(false);
    expect(app.credentialRecovery.has(before.provider)).toBe(true);
    expect(app.canRun).toBe(false);
    expect(await app.saveSettings(before)).toBe(false);
    expect(backend).toHaveBeenCalledTimes(2);
    backend.mockResolvedValueOnce({ settings: before, apiKeyStored: true, credentialMode: 'local' });
    expect(await app.saveSettings(before, 'synthetic-new-key')).toBe(true);
    expect(app.credentialRecovery.has(before.provider)).toBe(false);
  });

  it('compares category scope by values and invalidates only when one flag changes', async () => {
    const app = new AppState();
    const before = { ...app.settings };
    app.scan = { status: 'completed', candidateCount: 1, providerRequests: 0, fingerprint: 'fixture', scanPlanId: 'fixture', dryRun: true };
    backend.mockResolvedValueOnce({ settings: { ...before, scan_options: { ...before.scan_options } }, apiKeyStored: true, credentialMode: 'local' });
    backend.mockResolvedValueOnce({ requests: 1 }); // estimate after a preserved scan
    expect(await app.saveSettings(before)).toBe(true);
    expect(app.scan?.scanPlanId).toBe('fixture');
    backend.mockResolvedValueOnce({ settings: { ...before, scan_options: { ...before.scan_options, translate_signs: false } }, apiKeyStored: true, credentialMode: 'local' });
    expect(await app.saveSettings(before)).toBe(true);
    expect(app.scan).toBeNull();
  });
});
