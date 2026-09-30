import { invoke, isTauri } from '@tauri-apps/api/core';

export type DocumentKind = 'settings' | 'scan_report' | 'translation_report';

/** Native builds use a save dialog; browser fixtures use an ordinary download. */
export async function exportDocument(kind: DocumentKind, payload?: unknown): Promise<boolean> {
  if (isTauri()) return invoke<boolean>('export_document', { kind, document: payload ?? null });
  const filename = kind === 'settings' ? 'pomi-settings.json' : kind === 'scan_report' ? 'scan-report.json' : 'translate-report.json';
  const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  return true;
}
