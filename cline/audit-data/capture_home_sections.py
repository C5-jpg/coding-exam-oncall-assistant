from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots" / "reference" / "1440x900" / "home-sections"
OUT.mkdir(parents=True, exist_ok=True)

SECTIONS = [
    ("00-hero", 0),
    ("01-video", 1030),
    ("02-agent-first", 1650),
    ("03-feature-explorer", 2380),
    ("04-use-cases", 3700),
    ("05-pricing-cards", 4820),
    ("06-latest-blogs", 5660),
    ("07-download", 6570),
    ("08-footer", 7420),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = context.new_page()
        page.goto("https://antigravity.google/", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3500)
        for name, y in SECTIONS:
            page.evaluate("(y) => window.scrollTo(0, y)", y)
            page.wait_for_timeout(900)
            page.screenshot(path=str(OUT / f"{name}.png"))
        context.close()
        browser.close()


if __name__ == "__main__":
    main()
