import { callBackend, type Candidate, type CandidatePage } from './api';
import { pagesFor } from './virtual';

export const PAGE_SIZE = 200;
export type StateFilter = 'all' | 'included' | 'excluded' | 'manual';
export type SortMode = 'order' | 'source' | 'count' | 'kind';

/**
 * The candidate list as the review screen sees it: filtered, sorted and paged by the sidecar so
 * the total and the rows can never disagree, and only the pages in view are ever loaded.
 */
export class CandidateSource {
  query = $state('');
  kind = $state('');
  state = $state<StateFilter>('all');
  sort = $state<SortMode>('order');
  total = $state(0);
  kinds = $state<Record<string, number>>({});
  loading = $state(false);
  error = $state('');
  /** Bumped when rows arrive, so a row read inside an effect re-runs. */
  version = $state(0);

  private pages = new Map<number, Candidate[]>();
  private inflight = new Set<number>();
  private token = 0;
  private timer: ReturnType<typeof setTimeout> | undefined;
  private scanPlanId = '';
  private ids: () => { excluded: string[]; manual: string[] };

  constructor(ids: () => { excluded: string[]; manual: string[] }) {
    this.ids = ids;
  }

  get filtered(): boolean {
    return !!this.query.trim() || !!this.kind || this.state !== 'all';
  }

  /** Start over for a scan plan, or after any filter changed. */
  reset(scanPlanId = this.scanPlanId, seed?: Candidate[], seedTotal?: number): void {
    this.scanPlanId = scanPlanId;
    this.token += 1;
    this.pages.clear();
    this.inflight.clear();
    this.error = '';
    if (seed && !this.filtered && this.sort === 'order') {
      this.pages.set(0, seed.slice(0, PAGE_SIZE));
      this.total = seedTotal ?? seed.length;
      this.version += 1;
    } else {
      this.total = 0;
    }
    this.ensure(0, Math.min(PAGE_SIZE, Math.max(this.total, 1)));
  }

  /** Re-run the query after a short pause, so typing does not send a request per key. */
  refetchSoon(delay = 200): void {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.reset(), delay);
  }

  rowAt(index: number): Candidate | undefined {
    void this.version;
    return this.pages.get(Math.floor(index / PAGE_SIZE))?.[index % PAGE_SIZE];
  }

  /** Load whichever pages cover rows start..end that are not here yet. */
  ensure(start: number, end: number): void {
    if (!this.scanPlanId) return;
    for (const page of pagesFor(start, Math.max(end, start + 1), PAGE_SIZE)) {
      if (!this.pages.has(page) && !this.inflight.has(page)) void this.load(page);
    }
  }

  private async load(page: number): Promise<void> {
    const token = this.token;
    this.inflight.add(page);
    this.loading = true;
    const { excluded, manual } = this.ids();
    try {
      const response = await callBackend<CandidatePage>('candidates.page', {
        scanPlanId: this.scanPlanId,
        offset: page * PAGE_SIZE,
        limit: PAGE_SIZE,
        query: this.query,
        kind: this.kind,
        state: this.state,
        sort: this.sort,
        excludedCandidateIds: this.state === 'all' ? [] : excluded,
        overrideCandidateIds: this.state === 'manual' ? manual : []
      });
      if (token !== this.token) return; // the filters changed while this was in flight
      this.pages.set(page, response.candidates);
      this.total = response.total;
      this.kinds = response.kinds;
      this.version += 1;
    } catch (cause) {
      if (token === this.token) this.error = cause instanceof Error ? cause.message : String(cause);
    } finally {
      if (token === this.token) {
        this.inflight.delete(page);
        this.loading = this.inflight.size > 0;
      }
    }
  }

  /** Every id matching the current filters, to include or exclude them all at once. */
  async allIds(): Promise<string[]> {
    const { excluded, manual } = this.ids();
    const ids: string[] = [];
    for (let offset = 0; ; offset += 500) {
      const response = await callBackend<CandidatePage>('candidates.page', {
        scanPlanId: this.scanPlanId,
        offset,
        limit: 500,
        query: this.query,
        kind: this.kind,
        state: this.state,
        sort: 'order',
        excludedCandidateIds: this.state === 'all' ? [] : excluded,
        overrideCandidateIds: this.state === 'manual' ? manual : []
      });
      ids.push(...response.candidates.map((candidate) => candidate.id));
      if (!response.hasMore) return ids;
    }
  }
}
