# Interaction Specification — antigravity.google Clone

## Particle Field

### Behavior
- **Dots:** Small circles (1.5-2.5px radius) that drift slowly across the canvas
  - Speed: max 0.3px/frame horizontal, 0.2px/frame vertical
  - Opacity: 0.15 - 0.50
  - Colors: 85% gray tones, 15% accent (blue/purple/red/orange)
- **Dashes:** Short line segments (3-9px) that rotate slowly
  - Rotation: 0.002 radians/frame
  - 25% of particles are dashes
- **Wrapping:** Particles wrap around edges with 10px buffer
- **Seeded:** All positions generated with seed=42 for visual consistency

### Responsive Density
- Desktop (≥1024px): Full density (~0.5 per 10,000 sq px)
- Tablet (768-1023px): 70% density
- Mobile (<768px): 40% density, capped

### Performance
- Canvas uses `devicePixelRatio` (capped at 2x) for crisp rendering
- `requestAnimationFrame` loop with cleanup on unmount
- Pointer-events: none (non-interactive)

## Header

### Scroll Behavior
- Fixed position, always visible
- Semi-transparent background with backdrop blur
- No shrink/color change on scroll (stays consistent)

### Navigation Items
- Hover: Background `rgba(0,0,0,0.04)`, text color darkens
- Active/selected: Text color primary, chevron rotates 180°
- Transition: 250ms ease

### Dropdown Panels
- **Trigger:** Click on nav item with dropdown
- **Animation:** Slide down from header + fade in (200ms ease-out)
- **Close:** Click on overlay (transparent backdrop) or click same nav item
- **Content:** Two-column layout with description (left) + menu items (right)
- **Menu item hover:** Background `#f6f7fb`

### Download Button (header)
- Hover: Background goes pure black, shadow appears
- Active: No transform
- Transition: 150ms ease

### Mobile Menu Button
- Visible only below 900px viewport
- Toggles between hamburger (☰) and close (✕) icons
- No slide-out panel implemented (placeholder)

## Hero Section

### Layout
- Full viewport height (`100svh`)
- Content centered with CSS Grid `place-items: center`
- Slight upward offset (`translateY(-8px)`) for visual centering

### CTA Buttons
- **Primary ("Download for Windows"):**
  - Hover: Background `#000`, shadow `0 4px 12px rgba(0,0,0,0.2)`, translateY(-1px)
  - Active: translateY(0)
  - Includes download arrow icon
- **Secondary ("Explore use cases"):**
  - Transparent background with border
  - Hover: Background `#f6f7fb`, border color `#cfd3dc`

### Responsive CTAs
- Desktop: Side by side with 16px gap
- Mobile (<900px): Stacked vertically, max-width 320px, centered

## Video Section

### Player
- Click anywhere to toggle play/pause
- Button overlay shows play/pause icon + text
- 16:9 aspect ratio maintained
- Rounded corners (32px radius)

## Feature Explorer

### Tab Navigation
- Click tab to switch feature
- Active tab: Background `#f6f7fb`, blue dot indicator
- Inactive tab hover: Background `#f6f7fb`
- Video auto-plays and loops for active feature
- Video switches on tab change (via React `key` prop)

## Cards (Use Cases, Blogs)

### Hover Effect
- Transform: `translateY(-4px)`
- Shadow: `0 8px 32px rgba(0,0,0,0.1)`
- Transition: 250ms ease
- All cards are `<a>` tags with `href="#"` (no real navigation)

## Cookie Banner

### Appearance
- Fixed at bottom center of viewport
- Positioned 24px from bottom edge
- Max-width: 680px
- Slide-up animation: `translateY(20px)` → `translateY(0)` + opacity fade, 400ms ease-out

### Dismissal
- Click "Accept" or "Decline" → banner disappears (React state)
- No actual cookie/tracking functionality
- No localStorage persistence (shows again on refresh)

## Pricing Cards

### Particle Background
- Each card contains its own ParticleField instance
- Lower density (0.2) to not overpower card content
- Particles render behind text via z-index layering

## Demo Banner
- Fixed at very bottom of viewport (z-index: 9999)
- Yellow background (`#fff3cd`) with warning text
- Always visible, cannot be dismissed
- Text: "⚠️ Demo only — Unofficial clone for local learning. Not affiliated with Google."