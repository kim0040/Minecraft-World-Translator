import { test, expect, type Page } from '@playwright/test';
import { resolve } from 'node:path';
import AxeBuilder from '@axe-core/playwright';

async function open(page: Page, query: string) {
  await page.addInitScript({ path: resolve('tests/frontend/tauri-fixture-init.js') });
  await page.goto(`/?${query}`);
  await expect(page.locator('main')).not.toContainText('불러오는 중');
}

test('a fresh install learns what is missing before scanning and returns to the run step after setup', async ({ page }) => {
  await open(page, 'scenario=selected&fresh=1');
  // Scanning works without a key, but the missing setup is said up front, not at step 4.
  const early = page.locator('.callout').filter({ hasText: 'AI 번역 설정이 아직 남아 있습니다' });
  await expect(early).toContainText('사용할 AI 모델을 아직 고르지 않았습니다.');
  await expect(early).toContainText('OpenAI API 키가 저장되어 있지 않습니다.');
  await page.getByRole('button', { name: '스캔 시작', exact: true }).click();
  await page.getByRole('button', { name: /후보 검토/ }).last().click();
  await page.getByRole('button', { name: '번역 준비 단계로 이동' }).click();

  // One notice lists everything that blocks the run.
  const blocking = page.getByRole('alert').filter({ hasText: '번역을 시작하려면 설정을 마쳐 주세요' });
  await expect(blocking).toHaveCount(1);
  await expect(page.getByRole('button', { name: '번역 시작', exact: true })).toBeDisabled();
  await blocking.getByRole('button', { name: '환경 설정에서 설정하기' }).click();

  await page.locator('#api-key').fill('sk-fixture');
  await page.locator('#model').fill('fixture-model');
  await page.getByRole('button', { name: '저장하고 돌아가기', exact: true }).click();
  await expect(page.getByRole('heading', { level: 1, name: '번역 준비 및 실행' })).toBeVisible();
  await expect(page.locator('main')).toContainText('OpenAI · fixture-model');
  await expect(page.getByRole('alert').filter({ hasText: '번역을 시작하려면' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: '번역 시작', exact: true })).toBeEnabled();
});

test('settings opened from a step offer the way back without unsaved changes', async ({ page }) => {
  await open(page, 'scenario=run');
  await page.getByRole('navigation', { name: '작업 단계' }).getByRole('button', { name: /^번역 진행/ }).click();
  await page.getByRole('button', { name: '추론 설정 수정' }).click();
  await page.getByRole('button', { name: '"번역 진행" 단계로 돌아가기' }).click();
  await expect(page.getByRole('heading', { level: 1, name: '번역 준비 및 실행' })).toBeVisible();
});

test('leaving settings with unsaved changes asks before dropping them', async ({ page }) => {
  await open(page, 'scenario=selected&missingKey=1');
  await page.getByRole('button', { name: '환경 설정', exact: true }).click();
  await page.locator('#api-key').fill('sk-unsaved');
  await page.getByRole('button', { name: '백업 관리', exact: true }).click();

  const dialog = page.getByRole('dialog', { name: '저장하지 않은 설정이 있습니다' });
  await expect(dialog).toBeVisible();
  expect((await new AxeBuilder({ page }).analyze()).violations).toEqual([]);
  await dialog.getByRole('button', { name: '계속 편집' }).click();
  await expect(page.locator('#api-key')).toHaveValue('sk-unsaved');
  await expect(page.getByRole('heading', { level: 1, name: '환경 설정' })).toBeVisible();

  await page.getByRole('button', { name: '번역 작업', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: '저장하지 않고 이동' }).click();
  await expect(page.getByRole('heading', { level: 1, name: '월드 스캔' })).toBeVisible();
  await page.getByRole('button', { name: '환경 설정', exact: true }).click();
  await expect(page.locator('#api-key')).toHaveValue('');

  // Saving from the question moves on as asked.
  await page.locator('#model').fill('saved-on-leave');
  await page.getByRole('button', { name: '도움말', exact: true }).click();
  await page.getByRole('dialog').getByRole('button', { name: '저장하고 이동' }).click();
  await expect(page.getByRole('heading', { level: 1, name: '도움말' })).toBeVisible();
  await page.getByRole('button', { name: '환경 설정', exact: true }).click();
  await expect(page.locator('#model')).toHaveValue('saved-on-leave');
  await page.getByRole('button', { name: '정보', exact: true }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
});

test('keyboard moves through a narrow review list without opening the detail sheet', async ({ page }) => {
  await page.setViewportSize({ width: 1024, height: 700 });
  await open(page, 'scenario=review');
  await page.getByRole('button', { name: /^후보 검토/ }).click();
  const first = page.locator('tr[data-index="0"]');
  await first.focus();
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Space');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.locator('tr[data-index="1"] input[type="checkbox"]')).not.toBeChecked();
  await expect(page.locator('tr[data-index="1"]')).toBeFocused();
  await page.keyboard.press('Space');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await page.keyboard.press('Enter');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.locator('#manual-translation')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await expect(page.locator('tr[data-index="1"]')).toBeFocused();
});

test('a toast never covers the action bar', async ({ page }) => {
  await open(page, 'scenario=run');
  await page.getByRole('button', { name: '환경 설정', exact: true }).click();
  await page.locator('#model').fill('toast-fixture');
  await page.getByRole('button', { name: '저장', exact: true }).click();
  await page.getByRole('button', { name: '번역 작업', exact: true }).click();
  await page.getByRole('navigation', { name: '작업 단계' }).getByRole('button', { name: /^번역 진행/ }).click();
  const toast = page.locator('.toast').first();
  await expect(toast).toBeVisible();
  const toastBox = (await toast.boundingBox())!;
  const barBox = (await page.locator('.action-bar').boundingBox())!;
  expect(toastBox.y + toastBox.height).toBeLessThan(barBox.y);
});
