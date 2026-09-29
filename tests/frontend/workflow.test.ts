import { describe, expect, it } from 'vitest';

import { resultPresentation, emptyProgress, reduceProgress } from '../../src/lib/workflow';
import { LOCALES, translate, type MessageKey } from '../../src/lib/i18n/index.svelte';

describe('workflow progress mapping', () => {
  it('maps collect, translate, and write events to the user-facing phases', () => {
    const initial = { ...emptyProgress(), startedAt: 123 };
    const collecting = reduceProgress(initial, { event: 'scan_start', total_files: 18 });
    expect(collecting).toMatchObject({ phase: 'collect', fileTotal: 18, startedAt: 123 });

    const translating = reduceProgress(collecting, {
      event: 'phase_start',
      phase: 'translate',
      total: 42,
      requests_estimate: 7
    });
    expect(translating).toMatchObject({ phase: 'translate', total: 42, done: 0, requestsEstimate: 7 });

    const writing = reduceProgress(translating, { event: 'phase_start', phase: 'write', total: 5 });
    expect(writing).toMatchObject({ phase: 'write', fileIndex: 0, fileTotal: 5 });

    const writingFile = reduceProgress(writing, { event: 'file_start', phase: 'write', index: 3, total: 5 });
    expect(writingFile).toMatchObject({ phase: 'write', fileIndex: 3, fileTotal: 5 });
  });

  it('clears a retry indicator after progress or a completed batch', () => {
    const initial = emptyProgress();
    const retrying = reduceProgress(initial, {
      event: 'translation_batch_error',
      attempt: 2,
      max_attempts: 4
    });
    expect(retrying.retry).toEqual({ attempt: 2, max: 4 });

    const progressed = reduceProgress(retrying, {
      event: 'translation_progress',
      completed: 3,
      total: 10,
      failed: 1,
      batch: 2,
      batches: 4,
      requests: 2
    });
    expect(progressed.retry).toBeNull();
    expect(progressed).toMatchObject({ phase: 'translate', done: 3, total: 10, failed: 1, batch: 2, batches: 4, requests: 2 });

    const retryingAgain = reduceProgress(progressed, { event: 'translation_batch_error', attempt: 1, max_attempts: 4 });
    const batchDone = reduceProgress(retryingAgain, { event: 'translation_batch_done' });
    expect(batchDone.retry).toBeNull();
  });

  it('returns the same state for unknown raw events', () => {
    const current = { ...emptyProgress(), phase: 'translate' as const, done: 8, retry: { attempt: 1, max: 3 } };
    const next = reduceProgress(current, { event: 'translation_batch_start' });
    expect(next).toBe(current);
    expect(next).toEqual(current);
  });
});

describe('result status presentation', () => {
  it('maps every backend status to a localized known status', () => {
    const statuses = ['completed', 'partial', 'needs_retry', 'failed', 'cancelled', 'invalidated', 'unsupported', 'locked', 'unknown'];
    const knownStatuses = new Set(['completed', 'partial', 'needs_retry', 'failed', 'cancelled', 'locked', 'invalidated', 'unsupported']);

    for (const status of statuses) {
      const presentation = resultPresentation(status);
      expect(knownStatuses.has(presentation.status), status).toBe(true);
      expect(presentation.status, status).not.toBe('unknown');

      for (const locale of LOCALES) {
        const title = translate(locale, `result.${presentation.status}` as MessageKey);
        expect(title, `${locale}.${status}`).not.toBe(status);
        expect(title, `${locale}.${status}`).not.toBe('');
      }
    }
  });
});
