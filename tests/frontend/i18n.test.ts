import { describe, expect, it } from 'vitest';

import { en } from '../../src/lib/i18n/en';
import { ja } from '../../src/lib/i18n/ja';
import { ko } from '../../src/lib/i18n/ko';
import { LOCALES, translate } from '../../src/lib/i18n/index.svelte';

describe('translation catalogs', () => {
  it('have exactly the same semantic key set', () => {
    const sourceKeys = Object.keys(ko).sort();
    expect(Object.keys(en).sort()).toEqual(sourceKeys);
    expect(Object.keys(ja).sort()).toEqual(sourceKeys);
  });

  it('has a non-empty localized value for every key and locale', () => {
    for (const locale of LOCALES) {
      for (const key of Object.keys(ko)) {
        const value = translate(locale, key as keyof typeof ko);
        expect(value, `${locale}.${key}`).not.toBe('');
        expect(value, `${locale}.${key}`).not.toContain('{missing');
      }
    }
  });

  it('interpolates variables without exposing template placeholders', () => {
    expect(translate('en', 'common.of', { done: 2, total: 5 })).toBe('2 / 5');
    expect(translate('ko', 'detail.chunk', { x: 3, z: -2 })).toBe('청크 (3, -2)');
  });
});
