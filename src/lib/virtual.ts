/** Which rows of a long fixed-height list to draw. Pure, so it can be tested without a browser. */
export type Window = { start: number; end: number; padTop: number; padBottom: number };

export function visibleWindow(opts: {
  scrollTop: number;
  viewportHeight: number;
  rowHeight: number;
  total: number;
  overscan?: number;
}): Window {
  const { rowHeight, total } = opts;
  const overscan = opts.overscan ?? 6;
  if (total <= 0 || rowHeight <= 0) return { start: 0, end: 0, padTop: 0, padBottom: 0 };
  const scrollTop = Math.max(0, Math.min(opts.scrollTop, Math.max(0, total * rowHeight - opts.viewportHeight)));
  const first = Math.floor(scrollTop / rowHeight);
  const last = Math.ceil((scrollTop + Math.max(0, opts.viewportHeight)) / rowHeight);
  const start = Math.max(0, first - overscan);
  const end = Math.min(total, last + overscan);
  return { start, end, padTop: start * rowHeight, padBottom: (total - end) * rowHeight };
}

/** Which pages of a server-paged list cover rows start..end. */
export function pagesFor(start: number, end: number, pageSize: number): number[] {
  if (end <= start) return [];
  const pages: number[] = [];
  for (let page = Math.floor(start / pageSize); page <= Math.floor((end - 1) / pageSize); page += 1) pages.push(page);
  return pages;
}
