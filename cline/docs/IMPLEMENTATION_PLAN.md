# Antigravity Clone Implementation Plan

> Phase 1 audit is complete enough to plan implementation, but this file intentionally does not implement the page. The next phase should begin only after confirmation to proceed.

## 1. Objective

Build a local, browser-runnable, high-fidelity learning clone of `https://antigravity.google/` under:

```text
D:\reps\26H1_kimi\coding-exam\cline
```

The clone must:

- Use Vite + React + TypeScript.
- Recreate the long scrolling homepage, not just the hero.
- Include header, nav, dropdowns, hero, video/media sections, feature explorer, use cases, pricing, blogs, download, cookie banner, footer.
- Implement self-authored Canvas particle systems.
- Use screenshot and pixel diff feedback to iterate.
- Remain clearly labeled as an unofficial demo.
- Avoid real Google download/login/tracking flows.

## 2. Proposed Directory

```text
cline/
├── code/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── styles/
│   │   │   ├── base.css
│   │   │   ├── layout.css
│   │   │   └── components.css
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── DropdownPanel.tsx
│   │   │   ├── Hero.tsx
│   │   │   ├── FeatureExplorer.tsx
│   │   │   ├── UseCases.tsx
│   │   │   ├── Pricing.tsx
│   │   │   ├── BlogGrid.tsx
│   │   │   ├── DownloadSection.tsx
│   │   │   ├── CookieBanner.tsx
│   │   │   └── Footer.tsx
│   │   ├── particles/
│   │   │   ├── CanvasLayer.tsx
│   │   │   ├── ParticleField.ts
│   │   │   ├── DottedRibbon.ts
│   │   │   ├── CardParticleField.ts
│   │   │   ├── config.ts
│   │   │   └── pointer.ts
│   │   ├── data/
│   │   │   ├── nav.ts
│   │   │   ├── sections.ts
│   │   │   └── cards.ts
│   │   └── utils/
│   │       ├── math.ts
│   │       ├── seededRandom.ts
│   │       └── viewport.ts
│   └── scripts/
│       ├── capture-reference.ts
│       ├── capture-local.ts
│       └── pixel-diff.ts
├── docs/
├── screenshots/
│   ├── reference/
│   ├── local/
│   └── diff/
└── audit-data/
```

## 3. Technical Stack

| Area | Choice | Reason |
| --- | --- | --- |
| Build | Vite | Lightweight, fast dev server, simple static build |
| UI | React + TypeScript | Clear component structure and typed props/data |
| Styling | Plain CSS modules or organized global CSS | Maximum control for pixel matching |
| Animation | Canvas 2D + requestAnimationFrame | Source target uses canvas-like particles; Canvas 2D is enough for sparse dots and easier to tune |
| Screenshot | Playwright | Same tool family used for reference capture |
| Pixel diff | `pixelmatch` + `pngjs` | Common deterministic image comparison pipeline |
| Randomness | Seeded PRNG | Stable particle distribution across refreshes |

## 4. Implementation Phases

### Phase 2.1 Scaffold

Tasks:

- Create Vite React TypeScript project under `cline/code`.
- Add scripts:
  - `npm run dev`
  - `npm run build`
  - `npm run preview`
  - `npm run screenshot`
  - `npm run diff`
- Add basic lint/typecheck if practical.
- Do not touch `question-1` or any files outside `cline`.

Commit suggestion:

```text
feat(question-2): scaffold antigravity clone app
```

### Phase 2.2 Layout Shell

Tasks:

- Header with desktop nav and mobile menu.
- Hero shell matching observed title/CTA placement.
- All major homepage sections in correct order.
- Footer.
- Placeholder media/cards with correct dimensions and spacing.
- Demo-only disclaimer.

Validation:

- Compare `1440x900` and `390x844` screenshots for layout.
- Header height should be close to `52px`.
- Hero title top should be close to observed reference.

Commit suggestion:

```text
feat(question-2): recreate antigravity page structure
```

### Phase 2.3 Canvas Particle Systems

Tasks:

- Implement reusable Canvas layer component.
- Implement `ParticleField` for homepage hero sparse dots/short dashes.
- Implement `DottedRibbon` for Product page/right arc visual.
- Implement `CardParticleField` for pricing/download panels.
- Add seeded random and DPR-aware resizing.
- Add mobile density reduction.
- Add pointer move, pointer leave, hover intensity, and click pulse.

Particle data shape:

```ts
type Particle = {
  baseX: number;
  baseY: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  opacity: number;
  color: string;
  phase: number;
  seed: number;
  rotation: number;
  angularVelocity: number;
  mode: "dot" | "dash";
  layer: 0 | 1 | 2;
};
```

Validation:

- Particles must appear as dots or very short dashes.
- No vertical streaks.
- Text remains readable.
- Motion is subtle and stable.

Commit suggestion:

```text
feat(question-2): implement seeded canvas particle fields
```

### Phase 2.4 Navigation and Interactions

Tasks:

- Use Cases top-sheet dropdown.
- Resources top-sheet dropdown.
- Product route/state.
- Pricing and Blog local scroll/route behavior.
- Smooth card hover states.
- Cookie banner with local state.
- Keyboard support: Escape, focus, aria-expanded.

Validation:

- Browser inspect: dropdown matches observed full-width white top sheet.
- No real external/official actions.

Commit suggestion:

```text
feat(question-2): add nav dropdowns and safe local interactions
```

### Phase 2.5 Screenshot and Diff Tooling

Tasks:

- Add `scripts/capture-reference.ts`.
- Add `scripts/capture-local.ts`.
- Add `scripts/pixel-diff.ts`.
- Output:
  - `cline/screenshots/reference/`
  - `cline/screenshots/local/`
  - `cline/screenshots/diff/`
  - `cline/docs/PIXEL_AUDIT.md`

Commands:

```bash
cd cline/code
npm run screenshot
npm run diff
```

Validation:

- `PIXEL_AUDIT.md` lists mismatch ratio per viewport.
- Diff images are generated.

Commit suggestion:

```text
test(question-2): add screenshot and pixel diff audit scripts
```

### Phase 2.6 Three Visual Correction Rounds

Round 1: layout position

- Header horizontal alignment.
- Hero vertical/horizontal placement.
- Section order and section spacing.
- Mobile hero wrapping.

Round 2: typography, color, button, spacing

- Hero font size/weight/line-height.
- CTA size, radius, icon position.
- Dropdown typography and top-sheet proportions.
- Card radius/border/shadow.

Round 3: motion, particles, responsive details

- Particle density and shape.
- Product dotted ribbon.
- Pointer/click effects.
- Reduced motion.
- Mobile performance.

Commit suggestion after all corrections:

```text
refactor(question-2): tune antigravity visual fidelity
```

## 5. Screenshot / Diff Scripts Design

### 5.1 `capture-reference.ts`

Responsibilities:

- Open `https://antigravity.google/`.
- Capture viewports:
  - `1440x900`
  - `1366x768`
  - `1024x768`
  - `768x1024`
  - `390x844`
  - `375x812`
- Save to `cline/screenshots/reference`.
- Capture initial, 1s, 3s, and full-page states.

### 5.2 `capture-local.ts`

Responsibilities:

- Open `http://localhost:5173/` or configured local URL.
- Capture the same viewport matrix and timing states.
- Save to `cline/screenshots/local`.

### 5.3 `pixel-diff.ts`

Responsibilities:

- Match reference/local files by viewport and state.
- Resize/crop only when explicitly documented.
- Use `pixelmatch`.
- Write diff PNGs to `cline/screenshots/diff`.
- Generate `cline/docs/PIXEL_AUDIT.md` with:
  - mismatch ratio
  - diff pixels
  - likely divergent regions
  - fixed items
  - unresolved items
  - next optimization steps

## 6. Initial Pixel-Matching Priorities

1. Header height and nav spacing.
2. Hero title placement and line wrapping.
3. White background and sparse particles.
4. CTA size/radius/spacing.
5. Full-width dropdown layout.
6. Major section vertical positions.
7. Pricing/download card proportions.
8. Mobile nav and hero wrap.

## 7. Particle Implementation Detail

### Homepage `ParticleField`

- Seed particles in viewport space.
- Add left-weighted swirl/wave distribution.
- Use low-alpha colors.
- Mix dots and tiny dashes:
  - dots: `r=0.7-1.6`
  - dashes: length `2-5px`, width `1-1.6px`
- Clamp max velocity.
- Use local field function:
  - sine/cosine drift
  - pointer displacement
  - spring return to base

### Product `DottedRibbon`

- Generate points in parametric bands:
  - loop/ribbon center curve
  - width falloff
  - blue dot opacity falloff
- Draw as uniform tiny dots.
- Animate with slight wave offset.

### Card `CardParticleField`

- Clip to rounded card bounds.
- Lower density.
- Slow drift.
- Higher opacity only near card accent areas.

## 8. Performance Plan

- Cap DPR to `2`, mobile to `1.5` if needed.
- Reduce particles on mobile.
- Avoid shadows per particle where expensive.
- Batch canvas state changes by color/layer where possible.
- No per-frame DOM layout reads.
- Pause or reduce offscreen section canvases with `IntersectionObserver`.
- Respect `prefers-reduced-motion`.

## 9. Legal and Brand Safety Plan

Required UI copy:

```text
Demo only / Unofficial clone. This local recreation is for UI study and does not provide official Google downloads or services.
```

Required behavior:

- All download links are local placeholders.
- No Google analytics or GTM.
- No sign-in, telemetry, forms, or data collection.
- No official claim in README or UI.

## 10. Definition of Done

The implementation can be considered ready for review when:

- `npm install` works under `cline/code`.
- `npm run dev` starts the local app.
- `npm run build` succeeds.
- `npm run screenshot` captures local screenshots.
- `npm run diff` generates diff images and `docs/PIXEL_AUDIT.md`.
- All major sections from this audit exist in the clone.
- Use Cases and Resources dropdowns are interactive.
- Product view/section includes dotted blue ribbon particle system.
- Particle effect is dot/short-dash based and no longer resembles vertical streaks.
- README explains clone scope, implementation, differences, legal disclaimer, and run steps.

## 11. Do Not Do

- Do not write outside `D:\reps\26H1_kimi\coding-exam\cline`.
- Do not modify `question-1`.
- Do not copy/minify/use the production JS bundle.
- Do not include real tracking scripts.
- Do not implement real download/login flows.
- Do not claim pixel-perfect completion before diff reports exist.
