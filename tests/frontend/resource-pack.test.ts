import { expect, it } from 'vitest';
import { defaultResourcePackOptions, validateResourcePackOptions } from '../../src/lib/resource-pack';
import { parseSettingsImport } from '../../src/lib/settings-import';
import { defaultSettings } from '../../src/lib/app.svelte';

it('imports public and legacy locale options without external ZIP paths', () => {
  const options = { source_lang_files: ['en_gb.json'], target_lang_file: 'ja_jp.json', skip_if_target_exists: true };
  const legacy = parseSettingsImport(JSON.stringify({ resource_pack: { ...options, zip_paths: ['/private/file.zip'], enabled: true } }), defaultSettings());
  expect(legacy.resource_pack_options).toEqual(options);
  expect(legacy).not.toHaveProperty('zip_paths');
});

it('rejects unsafe names, duplicates, source collision and invalid policy', () => {
  for (const patch of [{ target_lang_file: '../out.json' }, { source_lang_files: ['a.json', 'a.json'] }, { target_lang_file: 'en_us.json' }, { source_lang_files: [] }, { skip_if_target_exists: 'true' }, { secret: 'unused' }]) {
    expect(() => validateResourcePackOptions(patch)).toThrow();
  }
  expect(validateResourcePackOptions({})).toEqual(defaultResourcePackOptions());
});
