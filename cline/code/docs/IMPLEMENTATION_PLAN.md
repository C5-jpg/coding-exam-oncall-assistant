# Implementation Plan — antigravity.google Clone

## Status: ✅ Phase 2 Complete (Initial Implementation)

## Architecture

```
cline/code/
├── public/
│   ├── favicon.svg
│   └── videos/           # Local video assets
├── src/
│   ├── components/
│   │   ├── AgentFirst/   # Icon grid section
│   │   ├── Blogs/        # Blog cards section
│   │   ├── CookieBanner/ # Cookie consent banner
│   │   ├── DownloadSection/ # Final CTA section
│   │   ├── Dropdown/     # Navigation dropdown panels
│   │   ├── FeatureExplorer/ # Tab + video feature showcase
│   │   ├── Footer/       # Site footer
│   │   ├── Header/       # Fixed navigation header
│   │   ├── Hero/         # Hero with particles + CTAs
│   │   ├── Pricing/      # Pricing cards section
│   │   ├── UseCases/     # Use case cards section
│   │   └── VideoSection/ # Main video player
│   ├── particles/
│   │   ├── ParticleField.tsx  # Canvas particle renderer
│   │   └── seededRandom.ts    # Deterministic PRNG
│   ├── styles/
│   │   ├── global.css    # Reset, utilities, buttons
│   │   └── variables.css # Design tokens
│   ├── App.tsx           # Page composition
│   └── main.tsx          # React entry point
├── scripts/
│   ├── capture-reference.ts  # Screenshot original site
│   ├── capture-local.ts      # Screenshot local clone
│   └── pixel-diff.ts         # Compare + generate report
├── docs/                     # Audit & specification docs
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Phases

### Phase 1: Audit ✅
- [x] Explore antigravity.google via web reader
- [x] Analyze reference video from resources/
- [x] Document page structure, design system, interactions
- [x] Generate SITE_AUDIT.md, DESIGN_SPEC.md, ASSET_MANIFEST.md, INTERACTION_SPEC.md

### Phase 2: Implementation ✅
- [x] Scaffold Vite + React + TypeScript project
- [x] Create CSS design tokens (variables.css)
- [x] Implement particle field (Canvas + seeded random)
- [x] Build all page sections (Header, Hero, Video, AgentFirst, FeatureExplorer, UseCases, Pricing, Blogs, Download, Footer, CookieBanner)
- [x] Responsive breakpoints (desktop/tablet/mobile/small)
- [x] Demo banner and safety measures
- [x] Build passes (`tsc -b && vite build`)

### Phase 3: Pixel Comparison ⏳
- [ ] Install Playwright Chromium (requires network access)
- [ ] Run `npm run screenshot:ref` on antigravity.google
- [ ] Run `npm run screenshot:local` on localhost:5173
- [ ] Run `npm run diff` to generate PIXEL_AUDIT.md
- [ ] Review diff results

### Phase 4: Visual Corrections (3 Rounds)
- [ ] Round 1: Layout positions (header, hero centering, section spacing)
- [ ] Round 2: Typography, colors, buttons, spacing
- [ ] Round 3: Animations, particles, responsive details

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | React 19 + TypeScript | Task requirement |
| Build tool | Vite 7 | Fast HMR, modern defaults |
| CSS approach | Plain CSS with custom properties | Simple, no build overhead |
| Particle system | HTML5 Canvas | Performant, controllable |
| PRNG | Seeded (Lehmer) | Deterministic visual output |
| Font loading | Google Fonts CDN | Matches original |
| Video assets | Local copies from resources/ | No network dependency |
| Icons | Inline SVG | No icon library needed |

## Safety Measures

1. **Demo banner** fixed at bottom of every page
2. **All links** use `href="#"` with `preventDefault()`
3. **No real downloads** — buttons are visual only
4. **No tracking** — no analytics, cookies, or external requests
5. **No authentication** — no login/signup flows
6. **Title** includes "Demo Clone (Unofficial)"

## How to Run

```bash
cd cline/code
npm install
npm run dev        # Start dev server at http://127.0.0.1:5173
npm run build      # Production build
npm run preview    # Preview production build
```

## How to Compare (requires Playwright)

```bash
npx playwright install chromium   # One-time browser install
npm run screenshot:ref            # Capture reference screenshots
npm run screenshot:local          # Capture local screenshots (dev server must be running)
npm run diff                      # Generate pixel comparison report
```

## Known Limitations

1. Particle positions will not match original exactly (different implementation)
2. Google Sans Flex font requires internet connection
3. Video content may differ from current live site
4. Mobile menu slide-out panel not implemented (button only)
5. Blog/use-case card images are placeholders
6. No scroll-reveal animations (potential improvement)