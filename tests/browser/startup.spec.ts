import { test, expect } from '@playwright/test';
import { resolve } from 'node:path';

for (const scenario of ['startup-handshake', 'startup-bootstrap', 'startup-stopped']) {
  test(`${scenario} shows recovery and retries bootstrap once`, async ({ page }) => {
    await page.addInitScript({ path: resolve('tests/frontend/tauri-fixture-init.js') });
    await page.goto(`/?scenario=${scenario}`);
    const alert = page.getByRole('alert');
    await expect(alert).toContainText('앱을 준비하지 못했습니다');
    if (scenario !== 'startup-stopped') {
      await expect(alert).not.toContainText(/CORE_HANDSHAKE_TIMEOUT|BOOTSTRAP_TIMEOUT/);
    }
    await expect(page.getByRole('button', { name: '환경 설정', exact: true })).toBeDisabled();
    await page.getByRole('button', { name: '다시 시도', exact: true }).click();
    await expect(alert).toHaveCount(0);
    await expect(page.getByRole('button', { name: '환경 설정', exact: true })).toBeEnabled();
    await expect(page.getByRole('heading', { name: '월드 스캔', exact: true })).toBeVisible();
    expect(await page.evaluate(() => (window as unknown as { __pomiRequests: { type: string }[] }).__pomiRequests
      .filter((request) => request.type === 'app.bootstrap').length)).toBe(2);
  });
}

for (const scenario of ['startup-delay', 'startup-listeners']) {
  test(`${scenario} reaches the initial screen`, async ({ page }) => {
    await page.addInitScript({ path: resolve('tests/frontend/tauri-fixture-init.js') });
    await page.goto(`/?scenario=${scenario}`);
    await expect(page.getByRole('heading', { name: '월드 스캔', exact: true })).toBeVisible();
    await expect(page.getByRole('alert')).toHaveCount(0);
  });
}
