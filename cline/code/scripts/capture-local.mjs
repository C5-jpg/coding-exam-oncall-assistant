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

const baseUrl = process.env.LOCAL_URL ?? 'http://127.0.0.1:5173/';
const outRoot = path.resolve('../screenshots/local');
await fs.mkdir(outRoot, { recursive: true });

const browser = await launchBrowser();
for (const [width, height] of viewports) {
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await page.addInitScript(() => {
    window.localStorage.setItem('antigravity-demo-cookie', 'dismissed');
  });
  const dir = path.join(outRoot, `${width}x${height}`);
  await fs.mkdir(dir, { recursive: true });
  await page.goto(baseUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.screenshot({ path: path.join(dir, 'initial.png') });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(dir, 'after-1s.png') });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(dir, 'after-3s.png') });
  await page.screenshot({ path: path.join(dir, 'full-page-after-3s.png'), fullPage: true });
  await page.close();
}

const interactionPage = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await interactionPage.addInitScript(() => {
  window.localStorage.setItem('antigravity-demo-cookie', 'dismissed');
});
const desktopDir = path.join(outRoot, '1440x900');
await interactionPage.goto(baseUrl, { waitUntil: 'load', timeout: 60000 });
await interactionPage.locator('header a[href="#use-cases"]').click();
await interactionPage.screenshot({ path: path.join(desktopDir, 'dropdown-use-cases.png') });
await interactionPage.goto(baseUrl, { waitUntil: 'load', timeout: 60000 });
await interactionPage.locator('header a[href="#resources"]').click();
await interactionPage.screenshot({ path: path.join(desktopDir, 'dropdown-resources.png') });
await interactionPage.close();
await browser.close();

async function launchBrowser() {
  try {
    return await chromium.launch({ channel: 'chrome', headless: true });
  } catch {
    return chromium.launch({ headless: true });
  }
}
