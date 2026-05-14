# Design Specification — antigravity.google Clone

## Color System

| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg` | `#ffffff` | Page background |
| `--color-bg-off` | `#fbfbfa` | Alternate bg |
| `--color-text-primary` | `#121317` | Main text |
| `--color-text-secondary` | `#3c4043` | Nav items, descriptions |
| `--color-text-muted` | `#6b7280` | Metadata, captions |
| `--color-border` | `#e6e8ee` | Card borders |
| `--color-border-light` | `#f0f1f5` | Subtle borders |
| `--cta-primary-bg` | `#111217` | Primary buttons |
| `--cta-secondary-bg` | `#f6f7fb` | Secondary buttons |
| `--particle-blue` | `#3f63ff` | Links, accents |

## Particle Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Blue | `#3f63ff`, `#5c6ff0` | Accent particles |
| Purple | `#8a58d6` | Accent particles |
| Red | `#ea4335` | Accent particles |
| Orange | `#fbbc04` | Accent particles |
| Gray | `#9aa0a6`, `#c4c9d0` | Background particles (majority) |

## Typography

| Element | Size | Weight | Line-height | Letter-spacing |
|---------|------|--------|-------------|----------------|
| Hero title (desktop) | 80px | 450 | 88px | -0.5px |
| Hero title (tablet) | 64px | 450 | 72px | -0.5px |
| Hero title (mobile) | 48px | 450 | 56px | -0.5px |
| Hero title (small) | 40px | 450 | 48px | -0.5px |
| Section heading | 48px | 400 | 1.2 | 0 |
| Card title | 20px | 500 | 1.3 | 0 |
| Nav items | 14.5px | 450 | 21.02px | 0.11px |
| Body text | 16px | 400 | 1.5 | 0 |
| Small text | 14px | 400 | 1.5 | 0 |
| Caption | 12px | 400 | 1.5 | 0 |

**Font Stack:** `"Google Sans Flex", "Google Sans", Inter, system-ui, -apple-system, sans-serif`

## Layout

| Property | Desktop | Tablet | Mobile | Small |
|----------|---------|--------|--------|-------|
| Header padding-x | 72px | 48px | 24px | 16px |
| Section padding-x | 108px | 64px | 32px | 20px |
| Section padding-y | 120px | 120px | 80px | 64px |
| Max content width | 1224px | 1224px | 1224px | 1224px |
| Header height | 52px | 52px | 52px | 52px |

## Buttons

| Property | Primary | Secondary |
|----------|---------|-----------|
| Height | 48-52px | 48-52px |
| Padding-x | 32-36px | 32-36px |
| Border-radius | 999px | 999px |
| Background | `#111217` | `#f6f7fb` |
| Color | `#ffffff` | `#121317` |
| Border | none | 1px solid `#e6e8ee` |
| Hover bg | `#000` | `#eef0f7` |
| Font size | 16px | 16px |
| Font weight | 500 | 500 |

## Cards

| Property | Value |
|----------|-------|
| Border-radius | 24px (small), 32px (large) |
| Border | 1px solid `#f0f1f5` |
| Shadow | `0 4px 24px rgba(0,0,0,0.06)` |
| Hover shadow | `0 8px 32px rgba(0,0,0,0.1)` |
| Hover transform | `translateY(-4px)` |

## Responsive Breakpoints

| Breakpoint | Width | Changes |
|------------|-------|---------|
| Desktop | ≥1200px | Full layout |
| Tablet | 900-1199px | Reduced padding/text |
| Mobile | 480-899px | Stacked nav, hidden nav items |
| Small | <480px | Maximum compression |

## Animations

| Element | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Dropdown panel | Slide down + fade in | 200ms | ease-out |
| Cookie banner | Slide up + fade in | 400ms | ease-out |
| Card hover | Lift + shadow | 250ms | ease |
| Button hover | Background + shadow + translateY(-1px) | 150ms | ease |
| Particles | Slow drift (0.3px/frame max) | Continuous | linear |
| Dashes | Slow rotation (0.002rad/frame) | Continuous | linear |