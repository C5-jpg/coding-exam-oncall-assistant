# Antigravity Site Audit

> Scope: first-phase audit for a local learning clone of `https://antigravity.google/`.
> This document records observed layout, DOM structure, page sections, screenshots, and known capture limits. It is not an implementation file.

## 1. Audit Boundary

- Target URL: `https://antigravity.google/`
- Audit date: 2026-05-14
- Output root: `D:\reps\26H1_kimi\coding-exam\cline`
- Allowed use: local UI recreation study only.
- Prohibited use: impersonating Google, implementing real Google login/download/tracking, collecting user data, or presenting the clone as an official site.

## 2. Tool Capability Mapping

The user requested Browser / Playwright / Puppeteer-like tools and MCP visual inspection. The current environment was mapped as follows:

| Requested capability | Actual tool used | Audit role |
| --- | --- | --- |
| Browser / Playwright visual inspection | Browser plugin through the in-app browser, plus Python Playwright scripts | Open target page, inspect DOM, display screenshots, click dropdowns |
| Multi-viewport screenshot capture | Playwright CLI and Python Playwright | Capture initial, 1s, 3s, full-page, and section screenshots |
| DOM and computed styles | Python Playwright audit script | Extract header/nav/hero/section/canvas/media/style data |
| Resource manifest | Python Playwright network listeners and performance entries | List CSS, JS, fonts, images, videos, third-party resources |
| File system | Workspace file tools | Store audit data only under `cline/` |

Full mapping file: [`TOOL_CAPABILITY_MAP.md`](./TOOL_CAPABILITY_MAP.md)

## 3. Screenshot Dataset

Reference screenshots were collected for the requested viewport matrix:

| Viewport | Initial | +1s | +3s | Full page |
| --- | --- | --- | --- | --- |
| 1440x900 | `../screenshots/reference/1440x900/initial.png` | `../screenshots/reference/1440x900/after-1s.png` | `../screenshots/reference/1440x900/after-3s.png` | `../screenshots/reference/1440x900/full-page-after-3s.png` |
| 1366x768 | `../screenshots/reference/1366x768/initial.png` | `../screenshots/reference/1366x768/after-1s.png` | `../screenshots/reference/1366x768/after-3s.png` | `../screenshots/reference/1366x768/full-page-after-3s.png` |
| 1024x768 | `../screenshots/reference/1024x768/initial.png` | `../screenshots/reference/1024x768/after-1s.png` | `../screenshots/reference/1024x768/after-3s.png` | `../screenshots/reference/1024x768/full-page-after-3s.png` |
| 768x1024 | `../screenshots/reference/768x1024/initial.png` | `../screenshots/reference/768x1024/after-1s.png` | `../screenshots/reference/768x1024/after-3s.png` | `../screenshots/reference/768x1024/full-page-after-3s.png` |
| 390x844 | `../screenshots/reference/390x844/initial.png` | `../screenshots/reference/390x844/after-1s.png` | `../screenshots/reference/390x844/after-3s.png` | `../screenshots/reference/390x844/full-page-after-3s.png` |
| 375x812 | `../screenshots/reference/375x812/initial.png` | `../screenshots/reference/375x812/after-1s.png` | `../screenshots/reference/375x812/after-3s.png` | `../screenshots/reference/375x812/full-page-after-3s.png` |

Primary 1440x900 section captures:

| Section | Screenshot |
| --- | --- |
| Hero | `../screenshots/reference/1440x900/home-sections/00-hero.png` |
| Intro video | `../screenshots/reference/1440x900/home-sections/01-video.png` |
| Agent-first icon field | `../screenshots/reference/1440x900/home-sections/02-agent-first.png` |
| Feature explorer | `../screenshots/reference/1440x900/home-sections/03-feature-explorer.png` |
| Use cases | `../screenshots/reference/1440x900/home-sections/04-use-cases.png` |
| Pricing cards | `../screenshots/reference/1440x900/home-sections/05-pricing-cards.png` |
| Latest blogs | `../screenshots/reference/1440x900/home-sections/06-latest-blogs.png` |
| Download | `../screenshots/reference/1440x900/home-sections/07-download.png` |
| Footer | `../screenshots/reference/1440x900/home-sections/08-footer.png` |

Dropdown captures:

| Menu | Screenshot | Notes |
| --- | --- | --- |
| Use Cases | Browser-confirmed visual; also captured by script | Full-width white dropdown below header |
| Resources | Browser-confirmed visual | Full-width white dropdown below header |
| Product | Browser-confirmed route/page transition | Product is a top-level product page, not a compact dropdown |
| Pricing | Script captured route state | Route/page content, not dropdown |
| Blog | Script captured route state | Route/page content, not dropdown |

## 4. High-Level Page Structure

The homepage is a long, scrollable marketing site with a white product-site aesthetic and a restrained particle/dot animation system. At `1440x900`, the page height is about `8183px`.

Observed section order:

1. Sticky header and navigation.
2. Hero section with full-viewport canvas background.
3. Intro video block.
4. Agent-first icon/constellation section.
5. Feature explorer with tab-like labels and video/media panel.
6. Use cases carousel/cards.
7. Pricing / plan cards.
8. Latest blogs cards.
9. Download section.
10. Footer with Google-style legal/navigation links.

## 5. Header / Navbar DOM Structure

Observed DOM snapshot:

```text
main
  link "Google Antigravity" -> /
  navigation
    button "Product"
    button "Use Cases" + keyboard_arrow_down
    button "Pricing"
    button "Blog"
    button "Resources" + keyboard_arrow_down
  button "Download" + download icon
```

Header measurements at `1440x900`:

| Element | Observed value |
| --- | --- |
| Header height | `52px` |
| Header background | `rgba(255, 255, 255, 0.85)` |
| Header position | fixed/sticky visual behavior at top |
| Header width | full viewport |
| Nav rect | `x=269.48`, `y=8`, `w=487.03`, `h=36` |
| Nav item font size | `14.5px` |
| Nav font weight | `450` |
| Nav line height | `21.02px` |
| Nav letter spacing | `0.11px` |
| Download button position | top-right, black pill |

## 6. Hero Section

Observed hero content:

```text
Google Antigravity
Experience liftoff with the next-gen agent platform
Download for Windows
Explore use cases
```

Hero measurements at `1440x900`:

| Element | Observed value |
| --- | --- |
| Hero section class | `welcome-wrapper` |
| Section rect | `x=0`, `y=0`, `w=1440`, `h=900` |
| Hero title rect | `x=170`, `y=342.28`, `w=1100`, `h=149.05` |
| Hero title font size | `80px` |
| Hero title weight | `450` |
| Hero title line height | `88px` |
| Hero title color | `rgb(18, 19, 23)` |
| CTA alignment | centered below title |
| Background | white with sparse animated dots/short colored particles |

The hero title text is split into individual text nodes/spans for animation control. There is a branded icon/cursor image above the main title.

## 7. Background Particle / Dot System

Observed visible behavior:

- White background, not a dark “space” effect.
- Sparse dot and short-dash particles in blue, gray, purple, orange, and red tones.
- Particles are small, most appearing as dots or tiny rotated dashes rather than long vertical streaks.
- Density is asymmetric: more activity appears on the left and in wave/arc clusters; the center text area remains readable.
- The product page shows a large arcing blue dotted shape on the right, built from a regular dot matrix warped into a ribbon/loop.
- The homepage hero has fine low-opacity particles across the viewport plus clustered colored motion on the left.
- Motion is subtle and product-site-like; it should not look like a generic starfield.

Observed canvas elements:

| Canvas context | Rect / role |
| --- | --- |
| Hero background | `1440x900`, full viewport |
| Pricing cards | Two canvases around `648x728`, used inside card backgrounds |
| Download section | Canvas around `1213.8x724.2` inside large rounded download panel |

## 8. Main Sections

### 8.1 Intro Video

Observed:

- Section class: `landing-video-section`
- Y position at desktop: about `1100.81px`
- Media rectangle: about `720x401.63`
- Visible control text: `Play intro`
- Visual: rounded video/thumbnail block with centered play affordance.

### 8.2 Agent-First Section

Observed:

- Section class: `agent-first-section`
- Y position: about `1703.25px`
- Height: about `726.47px`
- Visual: icon constellation/list of developer workflow symbols.
- Text conveys transition to an agent-first development model.

### 8.3 Feature Explorer

Observed:

- Section class: `feature-explorer-section`
- Y position: about `2429.72px`
- Height: about `1318.75px`
- Left-side title/content and right-side rounded media card.
- Feature labels observed:
  - `An Agent-First Experience`
  - `An IDE Experience`
  - `Higher-level Abstractions`
  - `Cross-surface Agents`
  - `User Feedback`
- Videos are used for each feature tab/content state.

### 8.4 Use Cases

Observed:

- Section class: `landing-use-case-section`
- Y position: about `3748.47px`
- Height: about `1128.75px`
- Section title: `Built for developers for the agent-first era`
- Cards:
  - `Frontend developer`
  - `Full stack developer`
  - `Enterprise developer`
- Includes carousel/slider arrows.

### 8.5 Pricing

Observed:

- Section class: `try-solutions-section`
- Y position: about `4877.22px`
- Height: about `839.25px`
- Cards:
  - `Available at no charge`
  - `For developers`
  - `Achieve new heights`
  - `Download`
  - `Coming soon`
  - `For organizations`
  - `Level up your entire team`
  - `Notify me`
- Visual: two large rounded plan cards with internal particle/canvas accents.

### 8.6 Latest Blogs

Observed:

- Section class: `landing-latest-blogs`
- Y position: about `5716.47px`
- Height: about `725.86px`
- Contains blog card grid and `View blog` CTA.
- Uses square image thumbnails.

### 8.7 Download

Observed:

- Section class: `download-section-container`
- Rect at desktop: `x=108`, `y=6630.42`, `w=1224`, `h=771.67`
- Includes large rounded container, product copy, platform download affordances.
- Download options mention Windows, x64, and ARM64.
- Uses a large canvas/media background.

### 8.8 Footer

Observed:

- Footer y position: about `7506.17px`
- Footer height: about `676.48px`
- Includes product tagline, navigation links, Google links/legal links.

## 9. Navigation and Routes

Observed navigation items:

| Item | Behavior |
| --- | --- |
| Product | Opens/navigates to product page content with hero `Agents that help you achieve liftoff` |
| Use Cases | Opens full-width dropdown with Professional, Frontend, Fullstack and `See overview` |
| Pricing | Opens/navigates to pricing route/content |
| Blog | Opens/navigates to blog route/content |
| Resources | Opens full-width dropdown with Documentation, Changelog, Support, Press, Releases |
| Download | Leads to download section/route; clone must use local placeholder only |

Browser-confirmed Resources dropdown text:

```text
Everything you need to stay up-to-date and get help
Documentation
Changelog
Support
Press
Releases
```

Browser-confirmed Use Cases dropdown text:

```text
Built for developers in the agent-first era
Explore how Google Antigravity helps you build
See overview
Professional
Frontend
Fullstack
```

## 10. Cookie Banner

Cookie resources are loaded from Google Glue:

- CSS: `https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.css`
- JS: `https://www.gstatic.com/glue/cookienotificationbar/cookienotificationbar.min.js`

During reference capture, the cookie banner was not persistently visible in the primary screenshots. The local clone should still include a non-tracking local cookie notice because the source site loads a cookie notification system. The clone banner must not connect to Google services.

## 11. Capture Limits and Known Ambiguities

- One scripted Resources dropdown capture timed out, but later Browser inspection confirmed the Resources dropdown content and visual layout.
- Product, Pricing, and Blog are better treated as route/page interactions rather than compact dropdown menus.
- Some video assets were discovered through DOM/network/performance entries, but not fully downloaded during phase 1.
- Exact internal particle implementation is compiled/minified in the production JS bundle; the clone must recreate behavior independently using observed output, not copied proprietary source.
- Pixel-level reproduction cannot be claimed until the local implementation exists and `pixel-diff` reports are generated.

## 12. Evidence Files

Raw audit outputs:

- `../audit-data/computed-styles.json`
- `../audit-data/dom-metrics.json`
- `../audit-data/dropdowns.json`
- `../audit-data/network-requests.json`
- `../audit-data/network-responses.json`
- `../audit-data/performance-assets.json`
- `../audit-data/scroll-audit.json`

Capture scripts:

- `../audit-data/capture_reference_screenshots.ps1`
- `../audit-data/audit_antigravity.py`
- `../audit-data/capture_home_sections.py`
