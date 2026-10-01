import { beforeEach, describe, expect, it, vi } from 'vitest';

const { backend, listen } = vi.hoisted(() => ({ backend: vi.fn(), listen: vi.fn() }));
vi.mock('../../src/lib/api', async () => ({
  ...await vi.importActual<typeof import('../../src/lib/api')>('../../src/lib/api'),
  callBackend: backend, onProgress: listen, onCloseBlocked: listen, onZoomFailed: listen
}));
import { AppState, defaultSettings } from '../../src/lib/app.svelte';
import { BackendError } from '../../src/lib/api';

const payload = () => ({
  notices: { firstLaunch: '', about: '', backupWarning: '', apiWarning: '' },
  settings: defaultSettings(), apiKeyStored: false, worlds: [], worldInspection: null,
  backups: [], resume: { available: false }
});

beforeEach(() => {
  backend.mockReset();
  listen.mockReset().mockResolvedValue(() => {});
  vi.stubGlobal('localStorage', { getItem: () => 'accepted' });
});

describe('startup recovery', () => {
  it('starts bootstrap even if event registration never responds', async () => {
    listen.mockReturnValue(new Promise(() => {}));
    backend.mockResolvedValue(payload());
    const app = new AppState();
    await app.boot();
    expect(backend).toHaveBeenCalledExactlyOnceWith('app.bootstrap');
    expect(app.ready).toBe(true);
    expect(app.startupFailed).toBe(false);
    app.destroy();
  });

  it('a timed-out startup can retry without duplicate subscriptions or lost queue state', async () => {
    backend.mockRejectedValueOnce(new BackendError('BOOTSTRAP_TIMEOUT', 'BOOTSTRAP_TIMEOUT'));
    backend.mockResolvedValueOnce(payload());
    const app = new AppState();
    await app.boot();
    expect(app.startupFailed).toBe(true);
    expect(app.busy).toBe('');
    expect(app.banner?.message).not.toContain('BOOTSTRAP_TIMEOUT');
    await app.boot();
    expect(app.startupFailed).toBe(false);
    expect(app.banner).toBeNull();
    expect(app.ready).toBe(true);
    expect(backend).toHaveBeenCalledTimes(2);
    expect(listen).toHaveBeenCalledTimes(3);
    app.destroy();
  });

  it('refuses a duplicate boot while bootstrap is pending', async () => {
    let resolve!: (value: ReturnType<typeof payload>) => void;
    backend.mockReturnValue(new Promise((done) => { resolve = done; }));
    const app = new AppState();
    const first = app.boot();
    await app.boot();
    expect(backend).toHaveBeenCalledTimes(1);
    expect(app.ready).toBe(false);
    resolve(payload());
    await first;
    app.destroy();
  });

  it('removes late event subscriptions after the app was destroyed', async () => {
    const stop = vi.fn();
    let resolve!: (value: () => void) => void;
    listen.mockReturnValue(new Promise<() => void>((done) => { resolve = done; }));
    backend.mockResolvedValue(payload());
    const app = new AppState();
    await app.boot();
    app.destroy();
    resolve(stop);
    await Promise.resolve();
    expect(stop).toHaveBeenCalledTimes(3);
  });
});
