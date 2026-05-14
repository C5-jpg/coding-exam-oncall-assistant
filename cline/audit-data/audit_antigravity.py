from __future__ import annotations

import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "audit-data"
SHOT = ROOT / "screenshots" / "reference"
URL = "https://antigravity.google/"


def save_json(name: str, payload) -> None:
    (DATA / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = context.new_page()

        requests: list[dict] = []
        responses: list[dict] = []
        page.on("request", lambda req: requests.append({
            "url": req.url,
            "method": req.method,
            "resourceType": req.resource_type,
        }))
        page.on("response", lambda res: responses.append({
            "url": res.url,
            "status": res.status,
            "resourceType": res.request.resource_type,
            "contentType": res.headers.get("content-type", ""),
        }))

        page.goto(URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        metrics = page.evaluate(
            """() => ({
                title: document.title,
                url: location.href,
                viewport: { width: innerWidth, height: innerHeight },
                scrollHeight: document.documentElement.scrollHeight,
                bodyHeight: document.body.scrollHeight,
                bodyText: document.body.innerText,
                links: Array.from(document.querySelectorAll('a')).map((a) => ({
                    text: a.innerText.trim(),
                    href: a.getAttribute('href'),
                    aria: a.getAttribute('aria-label'),
                    className: a.className
                })),
                buttons: Array.from(document.querySelectorAll('button')).map((b) => ({
                    text: b.innerText.trim(),
                    aria: b.getAttribute('aria-label'),
                    expanded: b.getAttribute('aria-expanded'),
                    className: b.className
                })),
                headings: Array.from(document.querySelectorAll('h1,h2,h3')).map((h) => ({
                    tag: h.tagName,
                    text: h.innerText.trim(),
                    className: h.className
                })),
                sections: Array.from(document.querySelectorAll('main,section,footer,header,nav,[role=\"dialog\"],[popover]')).map((el) => {
                    const rect = el.getBoundingClientRect();
                    return {
                        tag: el.tagName,
                        role: el.getAttribute('role'),
                        aria: el.getAttribute('aria-label'),
                        className: String(el.className),
                        text: (el.innerText || '').trim().slice(0, 500),
                        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                    };
                }),
                canvases: Array.from(document.querySelectorAll('canvas')).map((c) => {
                    const rect = c.getBoundingClientRect();
                    return { width: c.width, height: c.height, rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height }, className: c.className };
                }),
                videos: Array.from(document.querySelectorAll('video, source')).map((v) => ({
                    tag: v.tagName,
                    src: v.getAttribute('src'),
                    poster: v.getAttribute('poster'),
                    className: v.className
                })),
                images: Array.from(document.querySelectorAll('img')).map((img) => ({
                    alt: img.alt,
                    src: img.currentSrc || img.src,
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    className: img.className
                })),
                styleSheets: Array.from(document.styleSheets).map((s) => s.href).filter(Boolean),
                scripts: Array.from(document.scripts).map((s) => s.src).filter(Boolean),
            })"""
        )
        save_json("dom-metrics.json", metrics)
        save_json("network-requests.json", requests)
        save_json("network-responses.json", responses)

        # Computed style samples for design spec.
        style_samples = page.evaluate(
            """() => {
                function sample(selector) {
                  const el = document.querySelector(selector);
                  if (!el) return null;
                  const cs = getComputedStyle(el);
                  const rect = el.getBoundingClientRect();
                  return {
                    selector,
                    text: (el.innerText || el.textContent || '').trim().slice(0, 200),
                    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                    fontFamily: cs.fontFamily,
                    fontSize: cs.fontSize,
                    fontWeight: cs.fontWeight,
                    lineHeight: cs.lineHeight,
                    letterSpacing: cs.letterSpacing,
                    color: cs.color,
                    backgroundColor: cs.backgroundColor,
                    borderRadius: cs.borderRadius,
                    boxShadow: cs.boxShadow,
                    padding: cs.padding,
                    margin: cs.margin,
                    display: cs.display,
                    gap: cs.gap,
                  };
                }
                return {
                  body: sample('body'),
                  header: sample('header'),
                  nav: sample('nav'),
                  h1: sample('h1'),
                  primaryButton: sample('button, a[href*=\"download\"], a'),
                  main: sample('main'),
                };
            }"""
        )
        save_json("computed-styles.json", style_samples)

        # Dropdown audits.
        dropdowns = {}
        for name in ["Product", "Use Cases", "Resources", "Pricing", "Blog"]:
            try:
                target = page.get_by_text(name, exact=True).first
                target.click(timeout=3000)
                page.wait_for_timeout(500)
                dropdowns[name] = page.evaluate(
                    """(label) => ({
                        label,
                        bodyText: document.body.innerText,
                        openButtons: Array.from(document.querySelectorAll('button')).map((b) => ({
                            text: b.innerText.trim(),
                            expanded: b.getAttribute('aria-expanded')
                        })),
                        visibleLinks: Array.from(document.querySelectorAll('a')).filter((a) => {
                            const r = a.getBoundingClientRect();
                            return r.width > 0 && r.height > 0;
                        }).map((a) => ({ text: a.innerText.trim(), href: a.getAttribute('href') })).slice(0, 80)
                    })""",
                    name,
                )
                page.screenshot(path=str(SHOT / "1440x900" / f"dropdown-{name.lower().replace(' ', '-')}.png"))
                page.keyboard.press("Escape")
                page.wait_for_timeout(250)
            except Exception as exc:
                dropdowns[name] = {"error": str(exc)}
        save_json("dropdowns.json", dropdowns)

        # Scroll viewport screenshots at fixed y positions to validate blank/sections.
        scroll_positions = [0, 600, 1200, 1800, 2400, 3200, 4200]
        scroll_audit = []
        scroll_dir = SHOT / "1440x900" / "scroll"
        scroll_dir.mkdir(parents=True, exist_ok=True)
        for y in scroll_positions:
            page.evaluate("(y) => window.scrollTo(0, y)", y)
            page.wait_for_timeout(500)
            page.screenshot(path=str(scroll_dir / f"y-{y}.png"))
            scroll_audit.append(page.evaluate(
                """(y) => {
                    const center = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
                    return {
                      y,
                      scrollY: window.scrollY,
                      centerTag: center?.tagName,
                      centerText: (center?.innerText || center?.textContent || '').trim().slice(0, 250),
                      visibleText: document.body.innerText.slice(0, 1500),
                    };
                }""",
                y,
            ))
        save_json("scroll-audit.json", scroll_audit)

        # Asset URLs from performance entries.
        assets = page.evaluate(
            """() => performance.getEntriesByType('resource').map((entry) => ({
                name: entry.name,
                initiatorType: entry.initiatorType,
                duration: Math.round(entry.duration),
                transferSize: entry.transferSize || 0,
                encodedBodySize: entry.encodedBodySize || 0,
                decodedBodySize: entry.decodedBodySize || 0,
            }))"""
        )
        save_json("performance-assets.json", assets)

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
