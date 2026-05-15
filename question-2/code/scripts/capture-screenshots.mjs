/**
 * Playwright screenshot capture script for Antigravity recreation.
 *
 * Prerequisites:
 *   npm install --save-dev playwright
 *   npx playwright install chromium
 *
 * Usage:
 *   node scripts/capture-screenshots.mjs
 *
 * The script expects a dev server running at http://127.0.0.1:5173/
 */

import { chromium } from "playwright";
import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const screenshotDir = path.resolve(__dirname, "../../screenshot");

if (!fs.existsSync(screenshotDir)) {
  fs.mkdirSync(screenshotDir, { recursive: true });
}

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:5173";

async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const browser = await chromium.launch();
  const context = await browser.newContext();

  console.log("📸 Capturing screenshots...\n");

  // ---- 1. Desktop Home ----
  const page1 = await context.newPage();
  await page1.setViewportSize({ width: 1440, height: 900 });
  await page1.goto(BASE_URL, { waitUntil: "networkidle" });
  await sleep(2000);
  await page1.screenshot({
    path: path.join(screenshotDir, "01-home-desktop.png"),
    fullPage: false,
  });
  console.log("✅ 01-home-desktop.png");

  // ---- 2. Resources Menu Open ----
  const resourcesTrigger = page1.locator('.nav-item[data-dropdown="resources"] .nav-trigger');
  await resourcesTrigger.hover();
  await sleep(600);
  await page1.screenshot({
    path: path.join(screenshotDir, "02-resources-menu.png"),
    fullPage: false,
  });
  console.log("✅ 02-resources-menu.png");

  // ---- 3. Use Cases Section ----
  await page1.locator('.nav-item[data-dropdown="resources"]').dispatchEvent("mouseleave");
  await sleep(300);
  await page1.locator("#use-cases").scrollIntoViewIfNeeded();
  await sleep(800);
  await page1.screenshot({
    path: path.join(screenshotDir, "03-use-cases-section.png"),
    fullPage: false,
  });
  console.log("✅ 03-use-cases-section.png");

  // ---- 4. Video Playing ----
  await page1.locator("#hero").scrollIntoViewIfNeeded();
  await sleep(500);
  await page1.locator("#hero-play-btn").click();
  await sleep(1500);
  await page1.screenshot({
    path: path.join(screenshotDir, "04-video-playing.png"),
    fullPage: false,
  });
  console.log("✅ 04-video-playing.png");

  // ---- 5. Mobile ----
  const page2 = await context.newPage();
  await page2.setViewportSize({ width: 390, height: 844 });
  await page2.goto(BASE_URL, { waitUntil: "networkidle" });
  await sleep(2000);
  await page2.screenshot({
    path: path.join(screenshotDir, "05-mobile.png"),
    fullPage: false,
  });
  console.log("✅ 05-mobile.png");

  // ---- 6. Pricing Section ----
  await page1.bringToFront();
  await page1.locator("#pricing").scrollIntoViewIfNeeded();
  await sleep(800);
  await page1.screenshot({
    path: path.join(screenshotDir, "06-pricing.png"),
    fullPage: false,
  });
  console.log("✅ 06-pricing.png");

  // ---- 7. Blog Section ----
  await page1.locator("#blog").scrollIntoViewIfNeeded();
  await sleep(800);
  await page1.screenshot({
    path: path.join(screenshotDir, "07-blog.png"),
    fullPage: false,
  });
  console.log("✅ 07-blog.png");

  await browser.close();
  console.log("\n🎉 All screenshots captured!");
}

main().catch((err) => {
  console.error("❌ Screenshot capture failed:", err);
  process.exit(1);
});