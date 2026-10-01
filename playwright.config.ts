import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/browser',
  timeout: 30000,
  workers: 1,
  outputDir: 'output/playwright/results',
  reporter: 'list',
  use: { channel: 'chrome', baseURL: 'http://127.0.0.1:5197', viewport: { width: 1440, height: 900 }, trace: 'retain-on-failure',
    // Screens fade in; tests read them settled. tests/browser/motion.spec.ts covers the motion itself.
    contextOptions: { reducedMotion: 'reduce' } },
  webServer: {
    command: 'node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 5197 --strictPort',
    url: 'http://127.0.0.1:5197',
    reuseExistingServer: false,
  },
});
