import { beforeEach, describe, expect, it, vi } from 'vitest';

const { invokeMock } = vi.hoisted(() => ({ invokeMock: vi.fn() }));

vi.mock('@tauri-apps/api/core', () => ({ invoke: invokeMock }));
vi.mock('@tauri-apps/api/event', () => ({ listen: vi.fn() }));

import { callBackend } from '../../src/lib/api';

describe('sidecar request queue', () => {
  beforeEach(() => invokeMock.mockReset());

  it('waits for the active sidecar response before starting candidate paging', async () => {
    let finishEstimate!: (value: unknown) => void;
    invokeMock
      .mockImplementationOnce((_command, args) => new Promise((resolve) => {
        finishEstimate = (payload) => resolve({ v: 1, id: args.request.id, type: 'response.ok', payload });
      }))
      .mockImplementationOnce((_command, args) => Promise.resolve({
        v: 1,
        id: args.request.id,
        type: 'response.ok',
        payload: { candidates: [], total: 0 }
      }));

    const estimate = callBackend('estimate.get', { scanPlanId: 'scan-1' });
    const page = callBackend('candidates.page', { scanPlanId: 'scan-1', offset: 0, limit: 200 });
    await vi.waitFor(() => expect(invokeMock).toHaveBeenCalledTimes(1));

    finishEstimate({ requests: 1 });
    await expect(estimate).resolves.toEqual({ requests: 1 });
    await expect(page).resolves.toMatchObject({ total: 0 });
    expect(invokeMock).toHaveBeenCalledTimes(2);
  });
});
