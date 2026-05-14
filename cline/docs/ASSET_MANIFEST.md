# Antigravity Asset Manifest

> This manifest lists observed assets from `https://antigravity.google/` during audit. The local clone should not hotlink official Google assets unless explicitly allowed. Use local placeholders, self-authored Canvas/SVG, and clearly marked demo content where needed.

## 1. Summary

Observed asset classes:

- CSS bundles.
- JS bundles.
- Google/Google Symbols font CSS and WOFF2 files.
- Cookie notification assets.
- Product images and blog thumbnails.
- Multiple MP4 videos.
- Canvas-rendered particle/background layers.
- Google Tag Manager / analytics scripts.

Clone policy:

- Do not include real analytics/tracking scripts.
- Do not implement real download/login actions.
- Avoid copying proprietary bundle code.
- Prefer self-authored Canvas, CSS, local SVG, and locally generated visual placeholders.
- Include `Demo only / Unofficial clone` in the local UI and README.

## 2. CSS Assets

| URL | Purpose | Clone handling |
| --- | --- | --- |
| `https://antigravity.google/styles-7KLEMMT6.css` | Main production stylesheet | Do not copy wholesale; use observed computed styles and screenshots to author local CSS |
| `https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.css` | Google cookie banner style | Replace with local cookie banner CSS |

## 3. JS Assets

| URL | Purpose | Clone handling |
| --- | --- | --- |
| `https://antigravity.google/main-5LR4F4TY.js` | Production app bundle | Do not copy; recreate behavior independently |
| `https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.js` | Cookie banner runtime | Replace with local, no-tracking banner |
| `https://www.googletagmanager.com/gtag/js?id=G-47V54ZJ3EV&cx=c&gtm=4e65c0` | Analytics | Exclude |
| `https://www.googletagmanager.com/gtm.js?id=GTM-M4N2ZKXQ` | Google Tag Manager | Exclude |

## 4. Fonts

Observed font CSS:

```text
https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,wght@6..144,1..1000&display=block
https://fonts.googleapis.com/css2?family=Google+Symbols:opsz,wght,FILL,GRAD@24,400,0,0&display=block
```

Observed font families:

- `Google Sans Flex`
- `Google Sans`
- `Google Symbols`

Clone handling:

- Use local/system fallback stack for offline stability.
- Use CSS and text/icon approximations instead of depending on Google-hosted icon font.
- If icon library is introduced later, use open-source icons and keep styling close.

## 5. Image Assets

Observed image URLs:

| URL | Observed use | Clone handling |
| --- | --- | --- |
| `https://antigravity.google/assets/image/antigravity-cursor.png` | Brand/cursor image in hero | Replace with local geometric logo/cursor approximation; do not present as official |
| `https://antigravity.google/assets/image/landing/landing-thumbnail-frontend.jpg` | Use case card thumbnail | Replace with local placeholder or generated non-official thumbnail |
| `https://antigravity.google/assets/image/landing/landing-thumbnail-fullstack.jpg` | Use case card thumbnail | Replace with local placeholder or generated non-official thumbnail |
| `https://antigravity.google/assets/image/landing/landing-thumbnail-enterprise.jpg` | Use case card thumbnail | Replace with local placeholder or generated non-official thumbnail |
| `https://antigravity.google/assets/image/blog/blog-gemini-3-1-pro-square.png` | Blog card image | Replace with local demo thumbnail |
| `https://antigravity.google/assets/image/blog/blog-gemini-3-flash-square.png` | Blog card image | Replace with local demo thumbnail |
| `https://antigravity.google/assets/image/blog/blog-nano-banana-pro-square.png` | Blog card image | Replace with local demo thumbnail |
| `https://antigravity.google/assets/image/blog/blog-feature-introducing-google-antigravity.png` | Blog card image | Replace with local demo thumbnail |

## 6. Texture / Icon Assets

Observed:

```text
https://antigravity.google/assets/textures/icons/individual.png
https://antigravity.google/assets/textures/icons/cube.png
```

Clone handling:

- Recreate as local CSS/SVG/icon components.
- Keep icon weight and geometry close enough for layout fidelity.
- Do not use official icon textures if licensing is unclear.

## 7. Video Assets

Observed MP4 entries:

| URL | Observed use | Clone handling |
| --- | --- | --- |
| `https://antigravity.google/assets/video/hero_video.mp4` | Intro / hero video content | Optional local placeholder video surface; do not require asset for layout |
| `https://antigravity.google/assets/video/landing/an-agent-first-experience.mp4` | Feature explorer panel | Use local mock video placeholder or CSS/canvas animated panel |
| `https://antigravity.google/assets/video/landing/an-ai-ide-core.mp4` | Feature explorer panel | Use local mock video placeholder or CSS/canvas animated panel |
| `https://antigravity.google/assets/video/landing/higher-level-abstractions.mp4` | Feature explorer panel | Use local mock video placeholder or CSS/canvas animated panel |
| `https://antigravity.google/assets/video/landing/cross-surface-agents.mp4` | Feature explorer panel | Use local mock video placeholder or CSS/canvas animated panel |
| `https://antigravity.google/assets/video/landing/user-feedback.mp4` | Feature explorer panel | Use local mock video placeholder or CSS/canvas animated panel |

Phase-1 note:

- The audit discovered video URLs but did not copy them into the repository.
- If later implementation chooses to download public video references for analysis, store them only under `cline/`, document source, and avoid redistributing proprietary assets in the final clone unless legally safe.
- A robust local clone should not depend on remote videos to render the page.

## 8. Canvas / Generated Visual Assets

The most important visual assets are generated at runtime:

| Canvas | Observed role | Clone implementation |
| --- | --- | --- |
| Hero canvas | Sparse particle/dot field behind hero | Self-authored Canvas 2D particle field |
| Product page canvas | Large blue dotted ribbon/arc | Self-authored deterministic dotted ribbon field |
| Pricing card canvases | Decorative particle layers inside plan cards | Self-authored contained card particle fields |
| Download canvas | Decorative motion/background inside large download panel | Self-authored contained canvas layer |

Canvas implementation requirements for Phase 2:

- Seeded random for stable refreshes.
- DPR-aware sizing with DPR cap for performance.
- Resize handling.
- Low-density mobile mode.
- Tiny dots/short dashes only; avoid vertical streak artifacts.

## 9. Network / Third-Party Resources to Exclude

Exclude in local clone:

- Google Tag Manager.
- Google Analytics / gtag.
- Remote cookie notification JS.
- Any real auth, login, telemetry, or conversion tracking.

Local substitutes:

- Static/no-op links with `href="#"`.
- Local cookie banner state in `localStorage`.
- Demo-only download CTA text and local disclaimer.

## 10. Asset Risk Register

| Asset type | Risk | Mitigation |
| --- | --- | --- |
| Google logo/brand | Brand impersonation risk | Use “Unofficial clone / Demo only” notice and do not claim official status |
| Official download buttons | User confusion / unsafe impersonation | Use local placeholder links and disabled/no-op actions |
| Production JS/CSS | Proprietary code copying | Do not copy bundle source; use independent implementation |
| Remote videos/images | Copyright/licensing uncertainty | Use generated/local placeholders unless explicitly authorized |
| Analytics scripts | Privacy/tracking risk | Exclude entirely |

## 11. Raw Evidence

Raw files:

```text
../audit-data/network-requests.json
../audit-data/network-responses.json
../audit-data/performance-assets.json
../audit-data/dom-metrics.json
```
