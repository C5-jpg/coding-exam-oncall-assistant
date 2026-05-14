# Antigravity Design Spec

> This design specification is derived from reference screenshots, DOM snapshots, computed style extraction, and Browser visual inspection. It is the implementation target for the local clone, not a claim of official Google design guidance.

## 1. Visual Direction

The target is a clean Google-style product landing page:

- White background.
- Very dark neutral text.
- Minimal chrome.
- Rounded pill CTAs.
- Full-width header with translucent white surface.
- Sparse blue/gray/red/orange particle fields that feel technical, restrained, and lightweight.
- Large typography with generous line height and centered hero composition.
- Content sections built from large full-width bands and rounded media/card surfaces.

The local clone must display a clear `Demo only / Unofficial clone` note and must avoid real Google download/login/tracking behavior.

## 2. Color System

Observed values:

| Token | Source observation | Suggested clone token |
| --- | --- | --- |
| Page background | White screenshot background | `#ffffff` |
| Primary text | `rgb(18, 19, 23)` | `#121317` |
| Secondary text | Google-style dark gray, observed around body copy | `#3c4043` / `#4b4f58` |
| Muted text | Footer and helper text | `#6b7280` |
| Hairline border | Button/card edges | `#e6e8ee` |
| Header surface | `rgba(255, 255, 255, 0.85)` | `rgba(255,255,255,.86)` with blur |
| Primary CTA bg | Near black | `#111217` |
| Primary CTA text | White | `#ffffff` |
| Secondary CTA bg | Light gray/off-white | `#f6f7fb` |
| Secondary CTA text | Near black | `#121317` |
| Particle blue | Hero/product dots | `#3f63ff`, `#5c6ff0` |
| Particle purple | Hero accent | `#8a58d6` |
| Particle red | Hero accent | `#ea4335`-like |
| Particle orange | Hero accent | `#fbbc04`-like |

The clone should avoid dark or saturated “space” palettes. This target is a white product site with technical micro-motion.

## 3. Typography

Observed body font stack:

```css
font-family: "Google Sans Flex", "Google Sans", sans-serif;
```

Local clone recommendation:

```css
font-family:
  "Google Sans Flex",
  "Google Sans",
  Inter,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

Do not depend on external Google font loading for offline viability. Use local fallback stack first, with optional CSS variables approximating the original.

Observed desktop values:

| Element | Font size | Weight | Line height | Letter spacing |
| --- | ---: | ---: | ---: | ---: |
| Body | `16px` | regular | `24px` | default |
| Header nav | `14.5px` | `450` | `21.02px` | `0.11px` |
| Hero title | `80px` | `450` | `88px` | visually tight, no negative tracking |
| Hero label | about `24px` visual brand mark row | medium | tight |
| Button text | about `16px` | `600` on primary | `20-24px` | default |

Responsive type targets:

| Breakpoint | Hero title target |
| --- | --- |
| `>= 1280px` | `72-80px`, line-height `1.08-1.1` |
| `1024px` | `60-68px`, keep two-line structure |
| `768px` | `48-56px`, centered |
| `390px` / `375px` | `42-48px`, allow 3-4 lines, no overflow |

## 4. Header Layout

Observed desktop header:

- Height: `52px`.
- Full width.
- Background: translucent white.
- Logo starts around `72px` from the left at 1440 width.
- Nav starts around `269px`, vertically centered.
- Download CTA is top-right, black rounded pill.
- Items are horizontally spaced, no boxed nav background.

Desktop clone target:

```css
.site-header {
  height: 52px;
  padding: 0 72px;
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(16px);
}
```

Mobile clone target:

- Preserve logo and Download button if space allows.
- Collapse nav into a menu button at `<= 900px`.
- Use full-screen or top-sheet mobile menu.
- Keep CTA local/no-op with `href="#"`.

## 5. Hero Layout

Observed desktop hero:

- Full viewport section: `900px` high at `1440x900`.
- Hero title rect: `x=170`, `y=342.28`, `w=1100`, `h=149.05`.
- Centered brand label above title.
- CTA row below title around lower center.
- Hero canvas fills the viewport behind content.

Implementation target:

```css
.hero {
  min-height: 100svh;
  display: grid;
  place-items: center;
  position: relative;
  overflow: hidden;
}

.hero-inner {
  max-width: 1100px;
  text-align: center;
  transform: translateY(-8px);
}
```

CTA target:

| Button | Background | Size | Radius | Behavior |
| --- | --- | --- | --- | --- |
| Download for Windows | black | about `270x48px` desktop | `999px` | hover lifts/darkens subtly; local `href="#"` |
| Explore use cases | off-white | about `200x48px` desktop | `999px` | hover border/gray surface |

## 6. Particle Design Spec

The most important correction from the previous failed implementation: the target particles are mostly points or very short dashes, not tall vertical streaks.

### 6.1 Homepage Hero Particle Target

- Background: white.
- Particle unit: tiny circle or 1-3px short dash.
- Color: low-opacity blue/gray plus sparse red/orange/purple accents.
- Distribution:
  - Low-density across the full viewport.
  - Higher density on left curved wave/cluster.
  - Keep text legibility high in the title center.
- Motion:
  - Slow drift.
  - Subtle swirl/field movement.
  - Short dash rotation follows local velocity.
  - No loud trails.
  - No long vertical lines.

### 6.2 Product Page Particle Target

The product page shows a large blue dotted ribbon/arc on the right:

- Dot grid warped into a loop/arch.
- Dots are uniform, tiny, and blue.
- Large shape occupies much of the right side.
- Left side has sparse freestanding particles.

The clone should implement this as a separate canvas mode or reusable `ParticleField` variant:

- `heroMode = "sparse-flow"`
- `productMode = "dotted-ribbon"`
- `cardMode = "contained-card-field"`

### 6.3 Pricing / Download Particle Target

- Particles stay inside large rounded cards.
- Motion is decorative and subtle.
- Card layers must remain visually dominant over motion.

## 7. Cards and Section Layout

Observed design language:

- Use large rounded media panels/cards.
- Cards are not deeply nested.
- Border radius usually medium-large for product hero/media surfaces; buttons use full pill radius.
- Shadows are soft or absent; emphasis comes from whitespace, rounded masks, and media.
- Section spacing is generous, about one viewport section per major concept.

Implementation guidance:

| Component | Shape | Shadow | Border |
| --- | --- | --- | --- |
| Dropdown sheet | Full-width top sheet, rounded bottom corners | very soft | none or subtle |
| Feature media panel | Large rounded rectangle | soft | light border |
| Use-case card | Rounded image card | light | subtle |
| Pricing card | Large rounded plan card | soft layered | light border |
| Download panel | Very large rounded container | soft | light border |

## 8. Dropdown Menus

Use Cases dropdown:

- Full width below header.
- White background.
- Rounded bottom corners.
- Left column:
  - `Built for developers in the agent-first era`
  - `Explore how Google Antigravity helps you build`
  - `See overview`
- Right column menu:
  - Professional
  - Frontend
  - Fullstack
- Menu items include small icons and right arrows.

Resources dropdown:

- Full width below header.
- White background.
- Rounded bottom corners.
- Left title:
  - `Everything you need to stay up-to-date and get help`
- Right menu:
  - Documentation
  - Changelog
  - Support
  - Press
  - Releases

Dropdown animation target:

- Opens quickly under header.
- White top sheet pushes visually over hero, not a tiny floating popover.
- Header remains visible.
- Slight opacity/translate reveal is acceptable.

## 9. Responsive Behavior

Observed requested viewports:

- `1440x900`
- `1366x768`
- `1024x768`
- `768x1024`
- `390x844`
- `375x812`

Implementation breakpoints:

| Breakpoint | Behavior |
| --- | --- |
| `>= 1200px` | Full nav, centered hero, large typography |
| `900-1199px` | Full or compressed nav, reduced hero width |
| `<= 899px` | Mobile menu, compressed header padding |
| `<= 480px` | Vertical CTA stack, reduced particles, no text overflow |

Particle density targets:

| Viewport | Density strategy |
| --- | --- |
| Desktop | Full density, around 450-900 dots depending mode |
| Tablet | 65-75% density |
| Mobile | 35-50% density, simpler animation, lower DPR cap |

## 10. Interaction Visual States

Buttons:

- Primary hover: subtle lift, black remains black, tiny shadow increase.
- Secondary hover: background becomes slightly darker gray, border more visible.
- Active: press down 1px.

Cards:

- Hover: smooth elevation, media/card transform `translateY(-4px)` or subtle scale.
- Use case cards should feel interactive but not game-like.

Navbar:

- Hover: text darkens or underline/active tone appears.
- Dropdown arrow rotates 180 degrees on open.

Cookie banner:

- Local-only banner.
- Bottom sheet/card style.
- Accept/dismiss stores local preference if implemented.

## 11. Implementation Acceptance Targets

The local implementation should be judged against the captured reference:

- Header height and nav spacing should match within about `8-12px` on desktop.
- Hero title vertical position should match within about `24px` after font fallback differences.
- Hero text width and line breaks should stay close at all requested viewports.
- Particles must be tiny dots/short dashes and sparse, not vertical streaks.
- Dropdowns must be full-width top sheets matching the observed structure.
- Page must include all major homepage sections, not just first-screen particle animation.
- No real tracking, login, or official download links.

## 12. Visual References

Use these first when implementing:

```text
../screenshots/reference/1440x900/after-3s.png
../screenshots/reference/1440x900/home-sections/00-hero.png
../screenshots/reference/1440x900/home-sections/03-feature-explorer.png
../screenshots/reference/1440x900/home-sections/05-pricing-cards.png
../screenshots/reference/1440x900/home-sections/07-download.png
../screenshots/reference/390x844/after-3s.png
../screenshots/reference/375x812/after-3s.png
```
