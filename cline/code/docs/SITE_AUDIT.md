# Site Audit — antigravity.google

Audited: 2026-05-14

## Overview
Google Antigravity is an agentic development platform landing page. Clean white design with sparse animated particles (dots and dashes) in blue/gray/purple/red/orange colors.

## Page Structure

### Header
- Fixed, height: 52px
- Background: rgba(255,255,255,0.86) with backdrop-filter blur(16px)
- Left: Logo icon (4-color triangle) + "Google Antigravity" text
- Center: Nav items — Product, Use Cases (dropdown), Pricing, Blog, Resources (dropdown)
- Right: "Download" button (black pill, 36px height)
- Mobile: Hamburger menu icon replaces nav + download

### Hero Section
- Full viewport height, centered content
- Background: White with particle field overlay (Canvas)
- Brand icon: Larger 4-color triangle (48px)
- Title: "Experience liftoff with the next-gen agent platform" — 80px, weight 450
- CTAs: "Download for Windows" (primary) + "Explore use cases" (secondary)
- Particle field: Sparse dots/dashes, blue/gray/purple, slow drift

### Video Section
- 16:9 video player with rounded corners (32px radius)
- Play/pause button overlay at bottom-right

### Agent-First Section
- Heading: 48px, "agentic development platform" in blue (#3f63ff)
- Icon grid: 13 items with labels (Code, Agent, Build, Deploy, Debug, Test, Ship, Monitor, Iterate, Scale, Secure, Analyze, Connect)

### Feature Explorer Section
- Two-column layout: feature tabs (left) + video preview (right)
- 5 features with tab navigation: Agent-First, IDE, Higher-level Abstractions, Cross-surface Agents, User Feedback
- Each feature has looping video preview

### Use Cases Section
- Heading: "Built for developers in the agent-first era"
- 3-card grid: Frontend, Full stack, Enterprise
- Card: Image area + title + description, hover lift effect

### Pricing Section
- 2-card grid with particle backgrounds
- "For developers" (free, green badge) + "For organizations" (coming soon, blue badge)
- Each card has particle field and CTA button

### Blog Section
- Header: "Latest from the blog" + "View blog" link
- 3-card grid with image placeholders
- Tags: Blog, Engineering, Update

### Download Section
- Large rounded card with particle background
- Heading: "Ready to experience liftoff?"
- Two download buttons + platform tag

### Footer
- 5-column link grid: Product, Use Cases, Resources, Company, Legal
- Bottom: Copyright + Privacy/Terms/Cookies links

### Cookie Banner
- Fixed bottom-center, rounded card
- Text + Decline/Accept buttons
- Slide-up animation on load

## Responsive Breakpoints
- Desktop: ≥1200px — full nav, large hero text
- Tablet: 900-1199px — reduced padding, smaller text
- Mobile: <900px — hidden nav, hamburger, stacked CTAs
- Small mobile: <480px — further reduced sizes

## Navigation Dropdowns
- Use Cases: 3 items (Professional, Frontend, Fullstack) with icons
- Resources: 5 items (Documentation, Changelog, Support, Press, Releases)
- Panel slides down with animation (200ms ease-out)
- Click-outside closes dropdown