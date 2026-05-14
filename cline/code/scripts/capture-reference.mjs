import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const viewports = [
  [1440, 900],
  [1366, 768],
  [1024, 768],
  [768, 1024],
  [390, 844],
  [375, 812],
];

const outRoot = path.resolve('../screenshots/reference');
await fs.mkdir(outRoot, { recursive: true });

const browser = await launchBrowser();
for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  const dir = path.join(outRoot, `${width}x${height}`);
  await fs.mkdir(dir, { recursive: true });
  await page.goto('https://antigravity.google/', { waitUntil: 'load', timeout: 60000 });
  await page.screenshot({ path: path.join(dir, 'initial.png') });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(dir, 'after-1s.png') });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(dir, 'after-3s.png') });
  await page.screenshot({ path: path.join(dir, 'full-page-after-3s.png'), fullPage: true });
  await page.close();
}
await browser.close();

async function launchBrowser() {
  try {
    return await chromium.launch({ channel: 'chrome', headless: true });
  } catch {
    return chromium.launch({ headless: true });
  }
}
