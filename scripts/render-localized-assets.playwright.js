// First: node scripts/generate-localized-assets.mjs
// Run with playwright-cli run-code --filename scripts/render-localized-assets.playwright.js.
// Vite must be serving this repository on 127.0.0.1:5199.
async (page) => {
  const results = [];
  for (const locale of ['en', 'ko', 'ja', 'zh']) {
    const paths = [
      { path: `assets/brand/social/og_default_${locale}_v1`, height: 630 },
      ...['scan_first', 'backup_first', 'api_notice', 'unsupported'].map((id) => ({ path: `assets/illustrations/docs/doc_${id}_${locale}_v1`, height: 720 })),
    ];
    for (const { path, height } of paths) {
      await page.setViewportSize({ width: 1200, height });
      await page.goto(`http://127.0.0.1:5199/${path}.svg`);
      const bounds = await page.evaluate(async () => {
        await document.fonts.ready;
        await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        return [...document.querySelectorAll('text')].map((text) => {
          const box = text.getBBox();
          return { text: text.textContent, x: box.x, y: box.y, right: box.x + box.width, bottom: box.y + box.height };
        });
      });
      for (const box of bounds) {
        if (box.x < 0 || box.y < 0 || box.right > 1200 || box.bottom > height) throw new Error(`Clipped text in ${path}: ${box.text}`);
      }
      await page.screenshot({ path: `${path}.png` });
      results.push({ path: `${path}.png`, width: 1200, height, textBoxes: bounds });
    }
  }
  return results;
}
