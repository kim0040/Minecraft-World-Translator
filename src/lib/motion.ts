/**
 * Script-driven transitions (Svelte's fly/fade/flip) run on the Web Animations API, which the
 * reduced-motion rule in base.css cannot reach. They take their duration from here instead.
 */
export function reducedMotion(): boolean {
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

export function motion(ms: number): number {
  return reducedMotion() ? 0 : ms;
}
