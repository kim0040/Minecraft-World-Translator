import { describe, expect, it } from 'vitest';
import { defaultReasoningLabel, effortLabel, reasoningMode, reasoningSummary, supportedEfforts } from '../../src/lib/reasoning';
import { setLocale } from '../../src/lib/i18n/index.svelte';

describe('reasoning presentation', () => {
  it('sorts only supported efforts and translates their labels', () => {
    setLocale('ko');
    expect(supportedEfforts({ id: 'fixture', reasoning: { supported_efforts: ['max', 'high', 'low'] } })).toEqual(['low', 'high', 'max']);
    expect(effortLabel('high')).toBe('강하게 (high)');
    expect(supportedEfforts()).toEqual([]);
  });
  it('keeps the legacy enabled option in custom mode', () => {
    expect(reasoningMode('enabled')).toBe('custom');
    expect(reasoningMode('high')).toBe('custom');
    expect(reasoningMode('disabled')).toBe('disabled');
    expect(reasoningMode('default')).toBe('default');
  });
  it('does not infer activation from a default effort alone', () => {
    setLocale('ko');
    expect(defaultReasoningLabel({ id: 'fixture', reasoning: { default_effort: 'high' } })).toContain('활성화 여부 미확인');
    expect(defaultReasoningLabel({ id: 'fixture', reasoning: { default_effort: 'high', default_enabled: true } })).toBe('모델 기본값: 켜짐 · 강하게 (high)');
    expect(defaultReasoningLabel({ id: 'fixture', reasoning: { default_enabled: false } })).toBe('모델 기본값: 꺼짐');
    expect(defaultReasoningLabel()).toContain('아직 확인하지 못했습니다');
  });
  it('summarizes selected settings without inventing model defaults', () => {
    setLocale('ko');
    expect(reasoningSummary('max')).toBe('직접 설정 · 최대 (max)');
    expect(reasoningSummary('enabled')).toContain('강도 미지정');
    expect(reasoningSummary('default')).toContain('아직 확인하지 못했습니다');
    expect(defaultReasoningLabel({ id: 'no-support' })).toContain('지원하지 않습니다');
  });
});
