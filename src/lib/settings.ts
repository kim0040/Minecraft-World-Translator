import type { ScanOptions, Settings } from './api';
import { resourcePackOptions } from './resource-pack';

export function defaultScanOptions(): ScanOptions {
  return {
    translate_signs: true, translate_books: true, translate_custom_names: true, translate_item_names: true,
    translate_lore: true, translate_titles: true, translate_filtered_titles: true, translate_command_output: true,
    translate_text_displays: true, skip_command_like_text: true,
    region_dirs: ['region', 'entities', 'DIM-1/region', 'DIM-1/entities', 'DIM1/region', 'DIM1/entities'],
    skip_patterns: ['*.bak_translate'], component_translate_key_prefixes: []
  };
}

/** Presets change categories only; custom file rules stay intact. */
export function applyScanPreset(options: ScanOptions, preset: 'recommended' | 'story' | 'all'): ScanOptions {
  const defaults = defaultScanOptions();
  return {
    ...options,
    ...Object.fromEntries(Object.entries(defaults).filter(([, value]) => typeof value === 'boolean')),
    translate_text_displays: options.translate_text_displays,
    translate_item_names: preset !== 'story',
    translate_lore: preset !== 'story'
  };
}

export function normalizedScanOptions(options?: Partial<ScanOptions>): ScanOptions {
  const defaults = defaultScanOptions();
  return {
    ...Object.fromEntries(Object.entries(defaults).map(([key, value]) => [key, options?.[key as keyof ScanOptions] ?? value])) as ScanOptions,
    region_dirs: [...(options?.region_dirs ?? defaults.region_dirs)],
    skip_patterns: [...(options?.skip_patterns ?? defaults.skip_patterns)],
    component_translate_key_prefixes: [...(options?.component_translate_key_prefixes ?? defaults.component_translate_key_prefixes)]
  };
}

/** Explicit public fields prevent unknown backend preferences from entering an export. */
export function publicSettingsForExport(settings: Settings): Settings {
  return {
    provider: settings.provider, model: settings.model, base_url: settings.base_url, wire_format: settings.wire_format,
    target_language: settings.target_language, style_preset: settings.style_preset,
    style_prompt: settings.style_prompt, custom_system_prompt: settings.custom_system_prompt,
    temperature: settings.temperature, batch_size: settings.batch_size, request_timeout: settings.request_timeout,
    rpm_limit: settings.rpm_limit, tpm_limit: settings.tpm_limit, max_batch_retries: settings.max_batch_retries,
    max_file_write_retries: settings.max_file_write_retries, continue_on_file_error: settings.continue_on_file_error,
    source_overrides: { ...settings.source_overrides },
    concurrency: settings.concurrency, resource_pack_enabled: settings.resource_pack_enabled, resource_pack_options: resourcePackOptions(settings.resource_pack_options),
    skip_target_language_text: settings.skip_target_language_text, scan_options: normalizedScanOptions(settings.scan_options),
    ui_language: settings.ui_language, last_world_dir: settings.last_world_dir
  };
}

/** Stable comparison uses values, including list order, rather than object identity. */
export function scanOptionsSignature(options?: Partial<ScanOptions>): string {
  const normalized = normalizedScanOptions(options);
  return JSON.stringify(Object.fromEntries(Object.entries(normalized).sort(([a], [b]) => a.localeCompare(b))));
}
