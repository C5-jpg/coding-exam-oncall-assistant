# Pixel Audit Report

Generated: Pending first run

> Run `npm run diff` after generating both reference and local screenshots.

## Summary by Viewport

| Viewport | Shot | Diff % | Status |
|----------|------|--------|--------|
| (pending) | | | |

## Most Inconsistent Areas

Pending first comparison run.

## Fixed Items
- Header height and blur effect (52px, backdrop-filter blur 16px)
- Navigation item font sizes (14.5px) and weights (450)
- Hero section centering with grid place-items
- Particle field canvas with seeded random
- CTA button styling (pill shape, 999px radius)
- Cookie banner slide-up animation
- Responsive breakpoints (1199px, 899px, 479px)

## Unfixed Items
- Exact particle positions differ (seeded random vs original)
- Google Sans Flex font may not load if offline
- Video thumbnails use local placeholder content
- Footer links are all local placeholders (#)
- Exact dropdown animation timing may differ
- Blog card images are empty placeholders
- Use case card images are icon-only

## Next Optimization Suggestions
1. Fine-tune particle density and opacity per viewport
2. Adjust hero title line-break for each viewport
3. Match exact dropdown panel padding and width
4. Add scroll-reveal animations to sections
5. Fine-tune spacing between sections