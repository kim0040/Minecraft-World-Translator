import { describe, expect, it, vi } from 'vitest';

const { callBackendMock } = vi.hoisted(() => ({ callBackendMock: vi.fn() }));

vi.mock('../../src/lib/api', async () => {
  const actual = await vi.importActual<typeof import('../../src/lib/api')>('../../src/lib/api');
  return { ...actual, callBackend: callBackendMock };
});

import { CandidateSource, PAGE_SIZE } from '../../src/lib/candidates.svelte';

const page = (overrides: Partial<Parameters<typeof callBackendMock>[1]> = {}) => ({
  candidates: [
    { id: 'shop', source: 'Shop', kind: 'sign', occurrences: 3 },
    { id: 'welcome', source: 'Welcome', kind: 'book', occurrences: 1 }
  ],
  offset: 0,
  total: 2,
  hasMore: false,
  kinds: { sign: 1, book: 1 },
  ...overrides
});

describe('CandidateSource query state', () => {
  it('loads the first page and sends the current query, sort, and state', async () => {
    callBackendMock.mockResolvedValueOnce(page());
    const ids = { excluded: ['excluded-id'], manual: ['manual-id'] };
    const source = new CandidateSource(() => ids);
    source.query = 'shop';
    source.kind = 'sign';
    source.state = 'excluded';
    source.sort = 'source';

    source.reset('scan-1');
    await vi.waitFor(() => expect(callBackendMock).toHaveBeenCalledTimes(1));

    expect(callBackendMock).toHaveBeenCalledWith('candidates.page', {
      scanPlanId: 'scan-1',
      offset: 0,
      limit: PAGE_SIZE,
      query: 'shop',
      kind: 'sign',
      state: 'excluded',
      sort: 'source',
      excludedCandidateIds: ['excluded-id'],
      overrideCandidateIds: []
    });
    expect(source.total).toBe(2);
    expect(source.rowAt(0)?.source).toBe('Shop');
    expect(source.filtered).toBe(true);
  });

  it('keeps include-all unfiltered requests independent of local override lists', async () => {
    callBackendMock.mockResolvedValueOnce(page());
    const source = new CandidateSource(() => ({ excluded: ['excluded-id'], manual: ['manual-id'] }));
    source.reset('scan-2');
    await vi.waitFor(() => expect(callBackendMock).toHaveBeenCalledTimes(1));

    expect(callBackendMock).toHaveBeenCalledWith('candidates.page', expect.objectContaining({
      scanPlanId: 'scan-2',
      query: '',
      kind: '',
      state: 'all',
      sort: 'order',
      excludedCandidateIds: [],
      overrideCandidateIds: []
    }));
  });

  it('passes manual IDs only for the manual filter and loads missing pages once', async () => {
    callBackendMock
      .mockResolvedValueOnce(page({ total: 401, hasMore: true }))
      .mockResolvedValueOnce(page({ offset: PAGE_SIZE, total: 401, hasMore: true }));
    const source = new CandidateSource(() => ({ excluded: ['excluded-id'], manual: ['manual-id'] }));
    source.state = 'manual';
    source.reset('scan-3');
    await vi.waitFor(() => expect(callBackendMock).toHaveBeenCalledTimes(1));
    source.ensure(PAGE_SIZE, PAGE_SIZE + 20);
    await vi.waitFor(() => expect(callBackendMock).toHaveBeenCalledTimes(2));

    expect(callBackendMock).toHaveBeenLastCalledWith('candidates.page', expect.objectContaining({
      scanPlanId: 'scan-3',
      offset: PAGE_SIZE,
      limit: PAGE_SIZE,
      state: 'manual',
      sort: 'order',
      excludedCandidateIds: ['excluded-id'],
      overrideCandidateIds: ['manual-id']
    }));
    source.ensure(PAGE_SIZE, PAGE_SIZE + 20);
    expect(callBackendMock).toHaveBeenCalledTimes(2);
  });

  it('does not create one DOM row per candidate when paging a 100k result', async () => {
    callBackendMock.mockResolvedValueOnce(page({ candidates: [], total: 100_000, hasMore: true }));
    const source = new CandidateSource(() => ({ excluded: [], manual: [] }));
    source.reset('large-scan');
    await vi.waitFor(() => expect(callBackendMock).toHaveBeenCalledTimes(1));

    expect(source.total).toBe(100_000);
    expect(source.rowAt(0)).toBeUndefined();
    source.ensure(99_999, 100_000);
    expect(callBackendMock).toHaveBeenCalledTimes(2);
    expect(callBackendMock).toHaveBeenLastCalledWith('candidates.page', expect.objectContaining({
      offset: 99_800,
      limit: PAGE_SIZE
    }));
  });

  it('awaits a missing page for keyboard navigation across a page boundary', async () => {
    const distant = { id: 'distant', source: 'Page two', kind: 'sign', occurrences: 1 };
    callBackendMock
      .mockResolvedValueOnce(page({ total: 401, hasMore: true }))
      .mockResolvedValueOnce(page({ candidates: [distant], offset: PAGE_SIZE, total: 401, hasMore: true }));
    const source = new CandidateSource(() => ({ excluded: [], manual: [] }));
    source.reset('scan-keyboard');
    await vi.waitFor(() => expect(source.total).toBe(401));

    await expect(source.row(PAGE_SIZE)).resolves.toMatchObject({ id: 'distant' });
    expect(callBackendMock).toHaveBeenCalledTimes(2);
  });
});
