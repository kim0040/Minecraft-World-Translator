import type { ModelInfo } from './api';
import { t, type MessageKey } from './i18n/index.svelte';

const effortKeys: Record<string, MessageKey> = {
  minimal: 'settings.reasoning.minimal', low: 'settings.reasoning.low', medium: 'settings.reasoning.medium',
  high: 'settings.reasoning.high', xhigh: 'settings.reasoning.xhigh', max: 'settings.reasoning.max'
};

export function effortLabel(effort: string): string {
  return effortKeys[effort] ? `${t(effortKeys[effort])} (${effort})` : effort;
}

export function supportedEfforts(model?: ModelInfo): string[] {
  const supported = model?.reasoning?.supported_efforts;
  return Object.keys(effortKeys).filter((effort) => supported === null || supported?.includes(effort));
}

export function supportsReasoning(model?: ModelInfo): boolean {
  return !!model?.reasoning || !!model?.supported_parameters?.includes('reasoning');
}

export function reasoningMode(choice: string): 'default' | 'disabled' | 'custom' {
  return choice === 'default' || choice === 'disabled' ? choice : 'custom';
}

export function defaultReasoningLabel(model?: ModelInfo): string {
  if (!model) return t('settings.reasoning.unknownDefault');
  if (!supportsReasoning(model)) return t('settings.reasoning.notSupported');
  const metadata = model.reasoning;
  if (metadata?.default_enabled === false && !metadata.mandatory) return t('settings.reasoning.defaultOff');
  const strength = metadata?.default_effort && metadata.default_effort !== 'none'
    ? effortLabel(metadata.default_effort) : t('settings.reasoning.unknownStrength');
  if (metadata?.mandatory || metadata?.default_enabled === true) return t('settings.reasoning.defaultOn', { strength });
  return t('settings.reasoning.defaultUnconfirmed', { strength });
}

export function reasoningSummary(choice: string, model?: ModelInfo): string {
  if (choice === 'default') return `${t('settings.reasoning.default')} · ${defaultReasoningLabel(model)}`;
  if (choice === 'disabled') return t('settings.reasoning.disabled');
  return `${t('settings.reasoning.custom')} · ${choice === 'enabled' ? t('settings.reasoning.unspecified') : effortLabel(choice)}`;
}
