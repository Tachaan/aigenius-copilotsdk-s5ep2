---
name: brand-guidelines
description: "Guides AI agents when generating branded aviation and loyalty program websites. Use this skill when building marketing pages, product catalogs, hero sections, loyalty points displays, or any customer-facing UI for airline and frequent flyer contexts. Provides a complete visual design system with colors, typography, spacing, components, and layout patterns."
license: MIT
---

# Brand Guidelines — Aviation & Loyalty Program Design System

A cohesive visual design system for generating polished, professional aviation and loyalty program websites. Every section includes actionable CSS so an agent can produce an on-brand site immediately.

## When to Use

- Generating a new branded website or landing page
- Building product/reward catalog pages with points pricing
- Creating hero sections, navigation, or footers for airline contexts
- Styling loyalty tier indicators, points badges, or earn/redeem UIs
- Reviewing existing UI for brand compliance

---

## 1. Color Palette

Define all colors as CSS custom properties for consistency and easy theming.

| Role | Token | Hex | Usage |
|------|-------|-----|-------|
| Primary | `--color-primary` | `#E0003E` | CTAs, active states, brand accent |
| Primary contrast | `--color-primary-contrast` | `#FFFFFF` | Text on primary backgrounds |
| Secondary dark | `--color-secondary-dark` | `#1A1A2E` | Footer, dark sections |
| Secondary light | `--color-secondary-light` | `#F5F5F5` | Page background, card fills |
| Accent gold | `--color-accent-gold` | `#C9A84C` | Loyalty/premium highlights |
| Success | `--color-success` | `#2E7D32` | Confirmations, positive indicators |
| Text primary | `--color-text` | `#1A1A1A` | Body copy |
| Text muted | `--color-text-muted` | `#6B7280` | Captions, secondary info |

```css
:root {
  /* Primary */
  --color-primary: #E0003E;
  --color-primary-hover: #B80032;
  --color-primary-contrast: #FFFFFF;

  /* Secondary */
  --color-secondary-dark: #1A1A2E;
  --color-secondary-light: #F5F5F5;

  /* Accent */
  --color-accent-gold: #C9A84C;
  --color-accent-gold-light: #F5E6C8;
  --color-success: #2E7D32;

  /* Text */
  --color-text: #1A1A1A;
  --color-text-muted: #6B7280;
  --color-text-inverse: #FFFFFF;

  /* Borders & Surfaces */
  --color-border: #E5E7EB;
  --color-surface: #FFFFFF;
}
```

---

## 2. Typography

Use a system font stack for fast rendering with professional appearance. No external font dependencies.

```css
:root {
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  --font-family-mono: "SF Mono", "Fira Code", "Fira Mono", "Roboto Mono",
    monospace;

  --font-size-xs: 0.75rem;   /* 12px */
  --font-size-sm: 0.875rem;  /* 14px */
  --font-size-base: 1rem;    /* 16px */
  --font-size-lg: 1.125rem;  /* 18px */
  --font-size-xl: 1.25rem;   /* 20px */
  --font-size-2xl: 1.5rem;   /* 24px */
  --font-size-3xl: 2rem;     /* 32px */
  --font-size-4xl: 2.5rem;   /* 40px */

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-body: 1.6;
  --line-height-heading: 1.2;

  --letter-spacing-tight: -0.025em;
  --letter-spacing-normal: 0;
  --letter-spacing-wide: 0.05em;
  --letter-spacing-uppercase: 0.1em;
}

body {
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  line-height: var(--line-height-body);
  color: var(--color-text);
}

h1 {
  font-size: var(--font-size-4xl); /* 2.5rem */
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-heading);
  letter-spacing: var(--letter-spacing-tight);
}

h2 {
  font-size: var(--font-size-3xl); /* 2rem */
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-heading);
}

h3 {
  font-size: var(--font-size-2xl); /* 1.5rem */
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-heading);
}

.label-uppercase {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  letter-spacing: var(--letter-spacing-uppercase);
  text-transform: uppercase;
}
```

---

## 3. Spacing System

Based on a **4px base unit**. Use the scale consistently for padding, margin, and gap.

| Token | Value |
|-------|-------|
| `--space-xs` | 4px |
| `--space-sm` | 8px |
| `--space-md` | 12px |
| `--space-base` | 16px |
| `--space-lg` | 24px |
| `--space-xl` | 32px |
| `--space-2xl` | 48px |
| `--space-3xl` | 64px |
| `--space-4xl` | 96px |

```css
:root {
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-base: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;
  --space-4xl: 96px;
}
```

---

## 4. Card & Product Layout

Product cards are the primary content unit for reward catalogs and destination pages.

```css
.product-card {
  background: var(--color-surface);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12), 0 4px 10px rgba(0, 0, 0, 0.08);
}

.product-card__image {
  width: 100%;
  aspect-ratio: 3 / 2;
  object-fit: cover;
}

.product-card__body {
  padding: var(--space-lg);
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.product-card__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.product-card__price {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-primary);
}

.product-card__price--original {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-decoration: line-through;
  margin-right: var(--space-sm);
}

/* Product grid — responsive columns */
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-lg);
  padding: var(--space-lg);
}

@media (max-width: 1024px) {
  .product-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .product-grid {
    grid-template-columns: 1fr;
  }
}
```

---

## 5. Loyalty Points Display

Style points as a premium, instantly-recognizable element. Use locale-aware formatting for numbers.

### Points Badge

```css
.points-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--color-accent-gold-light);
  color: #7A6420;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  padding: var(--space-xs) var(--space-md);
  border-radius: 999px; /* pill shape */
  white-space: nowrap;
}

.points-badge__icon {
  width: 16px;
  height: 16px;
}
```

### Number Formatting

Always format points with locale-aware thousand separators:

```js
function formatPoints(points) {
  return new Intl.NumberFormat().format(points) + ' points';
}
// → "12,500 points"
```

### Earn / Redeem Toggle

```css
.points-toggle {
  display: inline-flex;
  border-radius: 999px;
  overflow: hidden;
  border: 2px solid var(--color-primary);
}

.points-toggle__option {
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  border: none;
  background: transparent;
  color: var(--color-primary);
  transition: background 0.2s ease, color 0.2s ease;
}

.points-toggle__option--active {
  background: var(--color-primary);
  color: var(--color-primary-contrast);
}
```

### Tier Indicators

| Tier | Color | Token |
|------|-------|-------|
| Bronze | `#CD7F32` | `--tier-bronze` |
| Silver | `#A0A0A0` | `--tier-silver` |
| Gold | `#C9A84C` | `--tier-gold` |
| Platinum | `#5A5A6E` | `--tier-platinum` |

```css
:root {
  --tier-bronze: #CD7F32;
  --tier-silver: #A0A0A0;
  --tier-gold: #C9A84C;
  --tier-platinum: #5A5A6E;
}

.tier-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-md);
  border-radius: 4px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-uppercase);
  color: var(--color-text-inverse);
}

.tier-badge--bronze   { background: var(--tier-bronze); }
.tier-badge--silver   { background: var(--tier-silver); }
.tier-badge--gold     { background: var(--tier-gold); color: #1A1A1A; }
.tier-badge--platinum { background: var(--tier-platinum); }
```

---

## 6. Navigation

Sticky header with clear hierarchy: logo left, nav center, CTA right.

```css
.site-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--space-lg);
}

.site-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  height: 64px;
}

.site-header__logo img {
  height: 32px;
  width: auto;
}

.site-nav {
  display: flex;
  gap: var(--space-xl);
  list-style: none;
  margin: 0;
  padding: 0;
}

.site-nav__link {
  text-decoration: none;
  color: var(--color-text);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: var(--space-sm) 0;
  border-bottom: 2px solid transparent;
  transition: border-color 0.2s ease, color 0.2s ease;
}

.site-nav__link:hover,
.site-nav__link--active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* Mobile hamburger menu */
.mobile-menu-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-sm);
}

@media (max-width: 768px) {
  .site-nav {
    display: none;
  }

  .mobile-menu-toggle {
    display: block;
  }

  .mobile-nav-panel {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: var(--color-surface);
    box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
    transition: right 0.3s ease;
    z-index: 200;
    padding: var(--space-2xl) var(--space-lg);
  }

  .mobile-nav-panel--open {
    right: 0;
  }

  .mobile-nav-panel .site-nav {
    display: flex;
    flex-direction: column;
    gap: var(--space-lg);
  }

  .mobile-nav-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 199;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }

  .mobile-nav-overlay--visible {
    opacity: 1;
    pointer-events: auto;
  }
}
```

---

## 7. CTA Buttons

Three tiers of call-to-action with clear visual hierarchy.

```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-md) var(--space-lg);
  font-family: var(--font-family);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease,
    box-shadow 0.2s ease;
  text-decoration: none;
  border: 2px solid transparent;
  line-height: 1;
}

/* Primary — solid red */
.btn--primary {
  background: var(--color-primary);
  color: var(--color-primary-contrast);
  border-color: var(--color-primary);
}

.btn--primary:hover {
  background: var(--color-primary-hover);
  border-color: var(--color-primary-hover);
}

/* Secondary — outlined red */
.btn--secondary {
  background: transparent;
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn--secondary:hover {
  background: var(--color-primary);
  color: var(--color-primary-contrast);
}

/* Tertiary — text link with arrow */
.btn--tertiary {
  background: transparent;
  color: var(--color-primary);
  border: none;
  padding: var(--space-xs) 0;
}

.btn--tertiary::after {
  content: "→";
  margin-left: var(--space-xs);
  transition: transform 0.2s ease;
}

.btn--tertiary:hover::after {
  transform: translateX(4px);
}

/* Disabled state — all variants */
.btn:disabled,
.btn--disabled {
  background: var(--color-border);
  color: var(--color-text-muted);
  border-color: var(--color-border);
  cursor: not-allowed;
  pointer-events: none;
}
```

---

## 8. Hero Section

Full-width banner with dark overlay for text legibility. Use destination or aircraft imagery.

```css
.hero {
  position: relative;
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
}

.hero__background {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  z-index: 0;
}

/* Dark gradient overlay for text contrast */
.hero__background::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(26, 26, 46, 0.6) 0%,
    rgba(26, 26, 46, 0.8) 100%
  );
}

.hero__content {
  position: relative;
  z-index: 1;
  max-width: 720px;
  padding: var(--space-2xl) var(--space-lg);
}

.hero__headline {
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-inverse);
  line-height: var(--line-height-heading);
  margin-bottom: var(--space-base);
}

.hero__subheadline {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: var(--space-xl);
  line-height: var(--line-height-body);
}

/* Use kangaroo silhouette or destination photography as background-image */
/* Example: background-image: url('/images/hero-destination.jpg'); */
```

---

## 9. Footer

Dark-themed footer with a 4-column layout, social links, and copyright bar.

```css
.site-footer {
  background: var(--color-secondary-dark);
  color: var(--color-text-inverse);
  padding: var(--space-3xl) var(--space-lg) 0;
}

.site-footer__grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-xl);
  max-width: 1280px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .site-footer__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .site-footer__grid {
    grid-template-columns: 1fr;
  }
}

.site-footer__heading {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  text-transform: uppercase;
  letter-spacing: var(--letter-spacing-uppercase);
  margin-bottom: var(--space-base);
  color: var(--color-accent-gold);
}

.site-footer__links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.site-footer__links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: color 0.2s ease;
}

.site-footer__links a:hover {
  color: var(--color-text-inverse);
}

/* Newsletter signup */
.footer-newsletter__input-group {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
}

.footer-newsletter__input {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text-inverse);
  font-size: var(--font-size-sm);
}

.footer-newsletter__input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

/* Social icons row */
.site-footer__social {
  display: flex;
  gap: var(--space-base);
  margin-top: var(--space-lg);
}

.site-footer__social a {
  color: rgba(255, 255, 255, 0.7);
  transition: color 0.2s ease;
}

.site-footer__social a:hover {
  color: var(--color-accent-gold);
}

/* Copyright bar */
.site-footer__copyright {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin-top: var(--space-2xl);
  padding: var(--space-lg) 0;
  text-align: center;
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.5);
}
```

### Recommended Footer Columns

| Column | Contents |
|--------|----------|
| **About** | Brand tagline, brief description, social icons |
| **Quick Links** | Destinations, Earn Points, Redeem, Flight Status |
| **Support** | Help Centre, Contact Us, FAQs, Accessibility |
| **Newsletter** | Heading, brief copy, email input + subscribe button |

---

## Brand Compliance Review Checklist

Before delivering any branded page, verify the following:

- [ ] **Color tokens** — All colors reference CSS custom properties from Section 1; no hardcoded hex values outside `:root`.
- [ ] **Typography** — Headings use the correct size/weight hierarchy (h1 2.5rem bold → h3 1.5rem medium). Body text uses system font stack.
- [ ] **Spacing consistency** — All padding, margin, and gap values use `--space-*` tokens on the 4px scale.
- [ ] **Responsive layout** — Product grid collapses from 3 → 2 → 1 columns. Navigation switches to hamburger menu at 768px.
- [ ] **Points formatting** — All point values use `Intl.NumberFormat()` with comma separators. Points badges use gold pill styling.
- [ ] **Button hierarchy** — Page has one clear primary CTA. Secondary and tertiary buttons are visually distinct. Disabled states are implemented.
- [ ] **Hero section** — Has dark overlay gradient, white text, minimum 60vh height, and a centered call-to-action.
- [ ] **Accessibility** — Color contrast meets WCAG AA (4.5:1 for text). Interactive elements have focus-visible outlines. Images have alt text.
