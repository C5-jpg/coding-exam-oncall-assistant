# Antigravity Interaction Spec

> This document records observed and required interactions for the local clone. It separates reference behavior from clone-safe behavior.

## 1. Interaction Goals

The clone should feel like a polished product website, not a static mock:

- Header navigation should open matching dropdowns or route-like sections.
- Buttons and cards should have smooth hover states.
- Background particles should animate continuously but subtly.
- Pointer movement should influence particles lightly without turning the site into a game.
- The page should scroll through all major sections.
- Download/login-like actions must remain local placeholders.

## 2. Header Navigation

Observed header items:

```text
Product
Use Cases
Pricing
Blog
Resources
Download
```

### 2.1 Product

Observed:

- Product behaves like a route/page transition.
- Visible product hero: `Agents that help you achieve liftoff`.
- Product page uses a large right-side dotted blue ribbon/arc particle system.
- CTA buttons: `Download for x64`, `Download for ARM64`.

Clone-safe behavior:

- Either implement as a local section route/state (`/#product`) or a local view in React state.
- Do not link to real download endpoints.
- Product CTA links should be `href="#"` and marked demo-only.

### 2.2 Use Cases Dropdown

Observed DOM:

```text
Built for developers in the agent-first era
Explore how Google Antigravity helps you build
See overview
Professional
Frontend
Fullstack
```

Observed visual behavior:

- Full-width white top sheet opens below header.
- Header remains visible.
- Dropdown has rounded lower corners.
- Left copy block and right menu column.
- Menu items include small icons and arrow glyphs.

Clone behavior:

- Open on click and hover/focus for desktop.
- Close on outside click, Escape, nav item switch, or route click.
- On mobile, render as accordion items inside the mobile menu.

### 2.3 Resources Dropdown

Observed DOM:

```text
Everything you need to stay up-to-date and get help
Documentation
Changelog
Support
Press
Releases
```

Clone behavior:

- Same top-sheet pattern as Use Cases.
- Items are local placeholders.
- Use consistent right-arrow icon treatment.

### 2.4 Pricing and Blog

Observed:

- Pricing and Blog act as route/page interactions.
- They also appear in footer/global links.

Clone behavior:

- Provide local scroll targets or React route-like states.
- Links remain local placeholders.
- If separate pages are not implemented in Phase 2, clicking should scroll to homepage Pricing/Blog sections.

### 2.5 Download

Observed:

- Header download button is a black pill with download icon.
- Hero primary CTA is also black.
- Download section appears near bottom.

Clone-safe behavior:

- Header Download should scroll to local download section or use `href="#download"`.
- The download section should clearly state demo-only.
- No binary downloads, installers, tracking, or external redirects.

## 3. Particle Interaction

The target site is restrained. Particle response should not be exaggerated.

### 3.1 Base Motion

Required clone behavior:

- Continuous `requestAnimationFrame` loop.
- Delta-time normalized updates.
- DPR-aware canvas resolution.
- Seeded random layout.
- Stable visual distribution after refresh.
- Resize rebuild/reprojection.

Visual constraints:

- Particles are dots or very short dashes.
- Avoid vertical streaks.
- Avoid dense starfield.
- Keep text center readable.

### 3.2 Pointer Move

Expected behavior:

- Nearby particles shift slightly.
- Tiny velocity/rotation changes can occur.
- Influence radius should be broad but low strength.
- No sudden explosions during normal hover.

Implementation target:

```text
radius: 120-220px desktop, 80-140px mobile
strength: subtle, capped
response: spring + damping
```

### 3.3 Hover Over CTAs and Cards

Expected behavior:

- CTA hover increases local particle activity very slightly.
- Card hover lifts card and may increase contained-canvas opacity/speed.
- Hover should be smooth and reversible.

Implementation target:

- Add a global interaction intensity variable when `.interactive` elements are hovered.
- Keep animation below the readability threshold.

### 3.4 Click / Tap

Expected behavior for clone:

- Small local pulse/ripple is acceptable.
- Particles can brighten or shift outward briefly.
- Restore to base field with spring/damping.

Implementation target:

```text
duration: 500-900ms
radius expansion: 24px -> 260px
strength: low-medium
opacity pulse: +0.08 to +0.2 max
```

### 3.5 Scroll

Observed:

- The page is long and scrollable with major sections.
- Feature/section content appears as the user scrolls.

Clone behavior:

- Smooth reveal animations for sections.
- Parallax should be subtle.
- Particle speed/intensity can respond slightly to scroll velocity.
- Avoid scroll-jank; no expensive layout reads per frame.

## 4. Button and Card States

### 4.1 Primary Buttons

Base:

- Black pill.
- White text.
- Icon on the left/right depending context.
- Height around `44-48px`.

Hover:

- Slight translateY `-1px` or `-2px`.
- Soft shadow increase.
- Background remains near black.

Active:

- Translate down to original position.

### 4.2 Secondary Buttons

Base:

- Very light gray/off-white.
- Dark text.
- Subtle border.
- Pill radius.

Hover:

- Slight gray darkening.
- Border becomes more visible.

### 4.3 Cards

Use case, blog, pricing, and media cards:

- Rounded surfaces.
- Smooth `transform` hover.
- Slight shadow/border response.
- Image/media should not jump or resize.

Target timing:

```css
transition:
  transform 220ms cubic-bezier(.2,.8,.2,1),
  box-shadow 220ms cubic-bezier(.2,.8,.2,1),
  border-color 220ms ease,
  background-color 220ms ease;
```

## 5. Dropdown Animation

Target behavior:

- Open under header in about `180-240ms`.
- Opacity from `0` to `1`.
- TranslateY from `-8px` to `0`.
- Bottom corners rounded.
- Header remains at top.
- Close on Escape and outside click.

Accessibility requirements:

- Use `aria-expanded`.
- Use `aria-controls` for dropdown panels.
- Menu items should be keyboard reachable.
- Escape closes the open dropdown.
- Focus should not disappear behind the overlay.

## 6. Mobile Interaction

Observed mobile references were captured at:

- `390x844`
- `375x812`
- `768x1024`

Clone target:

- Full nav collapses under about `900px`.
- Use a menu button or compressed menu.
- CTA buttons stack or wrap without clipping.
- Particle count is reduced.
- Dropdown panels become accordion sections.
- Touch targets should be at least `44px` high.

## 7. Cookie Banner

Reference:

- Target loads Google Glue cookie notification assets.
- The banner was not always visible in primary captures.

Clone target:

- Local-only cookie notice.
- No network calls.
- Buttons:
  - `Accept demo notice`
  - `Dismiss`
- Store dismissal in `localStorage`.
- Include clone disclaimer.

## 8. Reduced Motion

If `prefers-reduced-motion: reduce`:

- Freeze or heavily slow background particles.
- Disable section reveal transforms.
- Keep hover color states but remove large motion.
- No click ripple expansion.

## 9. Console and Performance Requirements

Expected implementation checks:

- No console errors.
- Canvas animation should sustain 60fps on common hardware.
- Mobile particle count should be reduced.
- DPR should be capped, likely `Math.min(window.devicePixelRatio, 2)`.
- Avoid per-particle DOM operations.
- Use object arrays or typed arrays if needed.
- The animation must not require a discrete GPU to be usable, though testing on a discrete GPU is acceptable.

## 10. Local Legal / Brand Interaction Rules

All interactive clone actions must be safe:

- `Download` does not download software.
- `Pricing` does not purchase anything.
- `Blog` links do not impersonate official posts.
- `Docs/Support/Press/Releases` are local placeholders.
- Show “Demo only / Unofficial clone” visibly.
- No tracking or data collection.
