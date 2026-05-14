# Asset Manifest — antigravity.google Clone

## Local Assets (included in project)

### Videos (from resources/)
| File | Location | Usage |
|------|----------|-------|
| `an-agent-first-experience.mp4` | `public/videos/` | Hero video section |
| `cross-surface-agents.mp4` | `public/videos/` | Feature explorer - Cross-surface tab |
| `higher-level-abstractions.mp4` | `public/videos/` | Feature explorer - Abstractions tab |
| `pinball_optmized.mp4` | `public/videos/` | Feature explorer - IDE tab |
| `user-feedback.mp4` | `public/videos/` | Feature explorer - Feedback tab |

### Icons (inline SVG)
All icons are rendered as inline SVG in React components:
- Logo icon (4-color triangle) — `Header.tsx`, `Hero.tsx`
- Navigation chevron — `Header.tsx`
- Download arrow — `Header.tsx`, `Hero.tsx`, `DownloadSection.tsx`
- Mobile menu (hamburger/close) — `Header.tsx`
- Agent-first section icons (13 items) — `AgentFirst.tsx`
- Use case card icons — `UseCases.tsx`
- Blog arrow — `Blogs.tsx`
- Dropdown item icons — `Dropdown.tsx`

### Favicon
- `public/favicon.svg` — Simplified 4-color triangle

## External Dependencies

### Font
- **Google Sans Flex** loaded via Google Fonts CDN
- URL: `https://fonts.googleapis.com/css2?family=Google+Sans+Flex:opsz,slnt,wdth,wght,ROND@8..144,-10..0,25..150,400..500,0..100&display=swap`
- Fallback stack: Inter, system-ui, -apple-system, sans-serif
- **Note:** If offline, the fallback fonts will be used

### JS/CSS Frameworks
- React 19 — UI framework
- Vite 7 — Build tool
- TypeScript 5.8 — Type safety

## Assets NOT Downloaded (replaced with local alternatives)

| Original | Replacement | Reason |
|----------|-------------|--------|
| Google Antigravity actual logo SVG | Simplified 4-color triangle SVG | Brand asset, not freely available |
| Original particle system JS | Custom Canvas implementation | Original is bundled/obfuscated |
| Original hero animation | Static hero with canvas particles | Complex original animation |
| Blog post thumbnail images | Empty colored div placeholders | No access to original images |
| Use case card images | Icon + colored background | No access to original images |
| Footer social icons | Not included | Secondary priority |

## Particle System
- **Implementation:** HTML5 Canvas
- **File:** `src/particles/ParticleField.tsx`
- **PRNG:** `src/particles/seededRandom.ts`
- **Rendering:** requestAnimationFrame loop
- **Colors:** Blue, purple, red, orange, gray (matching original palette)
- **Shapes:** Dots (circles) + Dashes (short lines with slow rotation)
- **Mobile optimization:** Reduced particle count on smaller screens