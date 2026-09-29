import { en } from './en';
import { ja } from './ja';
import { ko, type MessageKey } from './ko';

export type Locale = 'ko' | 'en' | 'ja';
export type { MessageKey };
export const LOCALES: Locale[] = ['ko', 'en', 'ja'];

const catalogs: Record<Locale, Record<MessageKey, string>> = { ko, en, ja };

// A plain object, so every `t()` call in a template re-runs when the locale changes.
export const i18n = $state<{ locale: Locale }>({ locale: 'ko' });

export function setLocale(locale: Locale): void {
  i18n.locale = locale;
  if (typeof document !== 'undefined') document.documentElement.lang = locale;
}

export function translate(locale: Locale, key: MessageKey, vars: Record<string, string | number> = {}): string {
  const template = catalogs[locale][key] ?? ko[key];
  return template.replace(/\{(\w+)\}/g, (_, name: string) => String(vars[name] ?? `{${name}}`));
}

export function t(key: MessageKey, vars: Record<string, string | number> = {}): string {
  return translate(i18n.locale, key, vars);
}

export function hasMessage(key: string): key is MessageKey {
  return key in ko;
}
