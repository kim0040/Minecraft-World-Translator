import type { ResourcePackOptions } from './api';

export function defaultResourcePackOptions(): ResourcePackOptions {
  return { source_lang_files: ['en_us.json', 'zh_cn.json'], target_lang_file: 'ko_kr.json', skip_if_target_exists: false };
}

export function resourcePackOptions(value?: Partial<ResourcePackOptions>): ResourcePackOptions {
  const defaults = defaultResourcePackOptions();
  return { ...defaults, ...value, source_lang_files: [...(value?.source_lang_files ?? defaults.source_lang_files)] };
}

export function validateResourcePackOptions(value: unknown, base?: ResourcePackOptions): ResourcePackOptions {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('resource_pack_options must be an object');
  const input = value as Record<string, unknown>;
  if (Object.keys(input).some((key) => !['source_lang_files', 'target_lang_file', 'skip_if_target_exists'].includes(key))) throw new Error('Unknown resource pack option');
  const merged = { ...resourcePackOptions(base), ...input };
  const filename = (name: unknown): name is string => typeof name === 'string' && name.length <= 64 && /^[A-Za-z0-9_.-]+\.json$/.test(name) && !name.includes('..');
  const sources = merged.source_lang_files;
  if (!Array.isArray(sources) || !sources.length || sources.length > 16 || !sources.every(filename) || new Set(sources).size !== sources.length) throw new Error('Invalid source locale files');
  if (!filename(merged.target_lang_file) || sources.includes(merged.target_lang_file)) throw new Error('Invalid target locale file');
  if (typeof merged.skip_if_target_exists !== 'boolean') throw new Error('Invalid existing locale policy');
  return { source_lang_files: [...sources], target_lang_file: merged.target_lang_file, skip_if_target_exists: merged.skip_if_target_exists };
}
