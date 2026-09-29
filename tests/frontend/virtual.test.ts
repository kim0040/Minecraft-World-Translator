import { describe, expect, it } from 'vitest';

import { pagesFor, visibleWindow } from '../../src/lib/virtual';

describe('virtual list helpers', () => {
  it('returns an empty window for empty or invalid dimensions', () => {
    expect(visibleWindow({ scrollTop: 0, viewportHeight: 400, rowHeight: 40, total: 0 })).toEqual({
      start: 0,
      end: 0,
      padTop: 0,
      padBottom: 0
    });
    expect(visibleWindow({ scrollTop: 0, viewportHeight: 400, rowHeight: 0, total: 10 })).toEqual({
      start: 0,
      end: 0,
      padTop: 0,
      padBottom: 0
    });
  });

  it('clamps scrolling and adds overscan without exceeding the total', () => {
    expect(visibleWindow({ scrollTop: 0, viewportHeight: 100, rowHeight: 20, total: 10, overscan: 1 })).toEqual({
      start: 0,
      end: 6,
      padTop: 0,
      padBottom: 80
    });
    expect(visibleWindow({ scrollTop: 60, viewportHeight: 100, rowHeight: 20, total: 10, overscan: 1 })).toEqual({
      start: 2,
      end: 9,
      padTop: 40,
      padBottom: 20
    });
    expect(visibleWindow({ scrollTop: 9999, viewportHeight: 100, rowHeight: 20, total: 10, overscan: 1 })).toEqual({
      start: 4,
      end: 10,
      padTop: 80,
      padBottom: 0
    });
  });

  it('keeps a 10k or 100k row list bounded to a small rendered window', () => {
    const tenThousand = visibleWindow({ scrollTop: 123_456, viewportHeight: 520, rowHeight: 52, total: 10_000 });
    const oneHundredThousand = visibleWindow({ scrollTop: 4_999_999, viewportHeight: 520, rowHeight: 52, total: 100_000 });
    for (const window of [tenThousand, oneHundredThousand]) {
      expect(window.start).toBeGreaterThanOrEqual(0);
      expect(window.end).toBeGreaterThan(window.start);
      expect(window.end - window.start).toBeLessThanOrEqual(30);
      expect(window.padTop).toBeGreaterThanOrEqual(0);
      expect(window.padBottom).toBeGreaterThanOrEqual(0);
    }
    expect(tenThousand.end).toBeLessThanOrEqual(10_000);
    expect(oneHundredThousand.end).toBeLessThanOrEqual(100_000);
  });

  it('maps row ranges to inclusive page indexes', () => {
    expect(pagesFor(0, 0, 200)).toEqual([]);
    expect(pagesFor(0, 1, 200)).toEqual([0]);
    expect(pagesFor(199, 200, 200)).toEqual([0]);
    expect(pagesFor(199, 201, 200)).toEqual([0, 1]);
    expect(pagesFor(400, 801, 200)).toEqual([2, 3, 4]);
    expect(pagesFor(9_999, 10_000, 200)).toEqual([49]);
    expect(pagesFor(99_999, 100_000, 200)).toEqual([499]);
  });
});
