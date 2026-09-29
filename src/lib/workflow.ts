import type { ProgressEvent } from './api';

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

export function emptyProgress(): JobProgress {
  return {
    phase: 'idle', fileIndex: 0, fileTotal: 0, done: 0, total: 0, failed: 0, batch: 0, batches: 0,
    requests: 0, requestsEstimate: 0, retry: null, startedAt: 0
  };
}

/** Convert sidecar event names into the small set of phases the interface explains to people. */
export function reduceProgress(current: JobProgress, event: ProgressEvent): JobProgress {
  const next = { ...current };
  switch (event.event) {
    case 'scan_start':
      next.phase = 'collect';
      next.fileTotal = event.total_files ?? next.fileTotal;
      break;
    case 'file_start':
    case 'file_done':
      if (event.phase === 'write') next.phase = 'write';
      else if (next.phase === 'idle') next.phase = 'collect';
      next.fileIndex = event.index ?? next.fileIndex;
      next.fileTotal = event.total ?? next.fileTotal;
      break;
    case 'phase_start':
      if (event.phase === 'translate') {
        next.phase = 'translate';
        next.total = event.total ?? 0;
        next.done = 0;
        next.requestsEstimate = event.requests_estimate ?? 0;
      } else if (event.phase === 'write') {
        next.phase = 'write';
        next.fileIndex = 0;
        next.fileTotal = event.total ?? 0;
      }
      break;
    case 'translation_progress':
      next.phase = 'translate';
      next.done = event.completed ?? next.done;
      next.total = event.total ?? next.total;
      next.failed = event.failed ?? next.failed;
      next.batch = event.batch ?? next.batch;
      next.batches = event.batches ?? next.batches;
      next.requests = event.requests ?? next.requests;
      next.retry = null;
      break;
    case 'translation_batch_error':
      next.retry = { attempt: event.attempt ?? 1, max: event.max_attempts ?? 1 };
      break;
    case 'translation_batch_done':
      next.retry = null;
      break;
    default:
      return current;
  }
  return next;
}

export type ResultTone = 'success' | 'warning' | 'danger' | 'info';
export type ResultPresentation = {
  status: 'completed' | 'partial' | 'needs_retry' | 'failed' | 'cancelled' | 'locked' | 'invalidated' | 'unsupported';
  tone: ResultTone;
  showReason: boolean;
};

/** Unknown backend statuses use the safe failure copy instead of appearing as raw identifiers. */
export function resultPresentation(status: string): ResultPresentation {
  switch (status) {
    case 'completed': return { status, tone: 'success', showReason: false };
    case 'partial': return { status, tone: 'warning', showReason: true };
    case 'needs_retry': return { status, tone: 'warning', showReason: true };
    case 'cancelled': return { status, tone: 'info', showReason: false };
    case 'invalidated': return { status, tone: 'warning', showReason: false };
    case 'unsupported': return { status, tone: 'danger', showReason: false };
    case 'locked': return { status, tone: 'warning', showReason: true };
    case 'failed':
    default:
      return { status: 'failed', tone: 'danger', showReason: true };
  }
}
