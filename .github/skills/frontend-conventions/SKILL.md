---
name: frontend-conventions
description: "Guides AI agents when generating frontend websites from scratch. Use this skill when creating HTML pages, styling with CSS, adding JavaScript interactivity, or building static sites. Covers semantic HTML5, modern CSS patterns, accessibility, performance, and component patterns for production-ready frontends."
license: MIT
model: gpt-5.4
---

# Frontend Conventions

Enforce consistent, accessible, and performant patterns when generating frontend websites from scratch.

## When to Use

- Creating a new website or landing page from scratch
- Writing HTML templates or page layouts
- Styling with CSS (Grid, Flexbox, custom properties)
- Adding vanilla JavaScript interactivity
- When asked: "build a website", "create a landing page", "generate frontend code"
- Reviewing frontend code for accessibility or performance

## Semantic HTML5 Structure

### 1. Page Skeleton

Every page MUST use semantic landmark elements — never use `<div>` as a structural substitute.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Page description for SEO">
  <meta property="og:title" content="Page Title">
  <meta property="og:description" content="Share description">
  <meta property="og:image" content="/assets/og-image.jpg">
  <title>Page Title</title>
  <link rel="stylesheet" href="styles/main.css">
</head>
<body>
  <a href="#main" class="skip-link">Skip to content</a>
  <header>...</header>
  <nav aria-label="Main">...</nav>
  <main id="main">...</main>
  <footer>...</footer>
</body>
</html>
```

### 2. Heading Hierarchy

Use one `<h1>` per page. Never skip heading levels.

```html
<!-- ✅ Good -->
<h1>Company Name</h1>
  <h2>Products</h2>
    <h3>Product A</h3>
  <h2>About</h2>

<!-- ❌ Bad: skips h2, multiple h1s -->
<h1>Title</h1>
<h1>Subtitle</h1>
  <h3>Section</h3>
```

## Modern CSS Patterns

### 3. Custom Properties for Theming

Define design tokens as CSS custom properties on `:root`.

```css
:root {
  --color-primary: #2563eb;
  --color-text: #1f2937;
  --color-bg: #ffffff;
  --font-base: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;
  --radius: 0.375rem;
}
```

### 4. CSS Grid for Layouts

Use Grid for page-level and multi-column layouts.

```css
.page-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
}
@media (min-width: 768px) {
  .page-grid { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
}
```

### 5. Flexbox for Component Alignment

Use Flexbox for single-axis alignment within components.

```css
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-md);
}
```

### 6. Responsive Typography

Use `clamp()` for fluid type sizing — no media queries needed.

```css
h1 { font-size: clamp(1.75rem, 4vw + 0.5rem, 3rem); }
h2 { font-size: clamp(1.25rem, 3vw + 0.25rem, 2rem); }
body { font-size: clamp(1rem, 1vw + 0.75rem, 1.125rem); }
```

### 7. Mobile-First Breakpoints

Always write base styles for mobile, then layer on with `min-width`.

```css
/* Base: mobile */
.container { padding: var(--space-md); }

/* Tablet */
@media (min-width: 768px) {
  .container { max-width: 720px; margin-inline: auto; }
}
/* Desktop */
@media (min-width: 1024px) {
  .container { max-width: 960px; }
}
```

## Component Patterns

### 8. Hero Section with CTA

```html
<section class="hero">
  <h1>Build Better Products</h1>
  <p>Concise value proposition in one sentence.</p>
  <a href="#signup" class="btn btn-primary">Get Started</a>
</section>
```

```css
.hero {
  display: grid;
  place-content: center;
  text-align: center;
  min-height: 60vh;
  padding: var(--space-lg);
}
.btn-primary {
  display: inline-block;
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-primary);
  color: #fff;
  border-radius: var(--radius);
  text-decoration: none;
}
```

### 9. Product/Card Grid

```html
<section aria-labelledby="products-heading">
  <h2 id="products-heading">Products</h2>
  <div class="card-grid">
    <article class="card">
      <img src="assets/product.jpg" alt="Product name" loading="lazy" width="400" height="300">
      <h3>Product Name</h3>
      <p>Short description.</p>
    </article>
  </div>
</section>
```

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-lg);
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: var(--radius);
  overflow: hidden;
}
.card img { width: 100%; height: auto; display: block; }
```

### 10. Navigation with Mobile Hamburger

```html
<nav aria-label="Main">
  <a href="/" class="nav-logo">Logo</a>
  <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu" aria-label="Toggle menu">
    <span class="hamburger"></span>
  </button>
  <ul id="nav-menu" class="nav-links" role="list">
    <li><a href="#features">Features</a></li>
    <li><a href="#pricing">Pricing</a></li>
  </ul>
</nav>
```

```css
.nav-toggle { display: none; }
@media (max-width: 767px) {
  .nav-toggle { display: block; }
  .nav-links { display: none; }
  .nav-links.open { display: flex; flex-direction: column; }
}
```

### 11. Footer with Columns

```html
<footer>
  <div class="footer-grid">
    <div><h4>Product</h4><ul role="list">...</ul></div>
    <div><h4>Company</h4><ul role="list">...</ul></div>
    <div><h4>Legal</h4><ul role="list">...</ul></div>
  </div>
  <p class="footer-copy">&copy; 2025 Company. All rights reserved.</p>
</footer>
```

```css
.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--space-lg);
}
```

### 12. Modal/Overlay

```html
<dialog id="modal" aria-labelledby="modal-title">
  <h2 id="modal-title">Confirm Action</h2>
  <p>Are you sure?</p>
  <button data-close-modal>Close</button>
</dialog>
```

```javascript
const modal = document.getElementById("modal");
document.querySelector("[data-open-modal]").addEventListener("click", () => modal.showModal());
document.querySelector("[data-close-modal]").addEventListener("click", () => modal.close());
```

### 13. Form with Validation States

```html
<form novalidate>
  <label for="email">Email</label>
  <input type="email" id="email" required aria-describedby="email-error">
  <span id="email-error" class="error" role="alert" hidden>Enter a valid email.</span>
  <button type="submit">Submit</button>
</form>
```

```css
input:user-invalid { border-color: #dc2626; }
input:user-valid { border-color: #16a34a; }
.error { color: #dc2626; font-size: 0.875rem; }
```

## Accessibility Fundamentals

### 14. ARIA & Landmarks

- Use `<header>`, `<nav>`, `<main>`, `<footer>` — they provide implicit ARIA roles
- Add `aria-label` to distinguish multiple `<nav>` elements
- Use `aria-expanded`, `aria-controls` on toggle buttons
- Add `role="alert"` for dynamic error messages

### 15. Skip Navigation

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  padding: var(--space-sm) var(--space-md);
  background: var(--color-primary);
  color: #fff;
  z-index: 100;
}
.skip-link:focus { top: 0; }
```

### 16. Focus & Keyboard

```css
/* Visible focus for keyboard, hidden for mouse */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

All interactive elements (`<a>`, `<button>`, `<input>`) MUST be keyboard-navigable. Never attach click handlers to `<div>` or `<span>`.

### 17. Images

```html
<!-- Informative image: descriptive alt -->
<img src="chart.png" alt="Sales grew 40% in Q3 2025" width="600" height="400">

<!-- Decorative image: empty alt -->
<img src="divider.svg" alt="" role="presentation">
```

### 18. Color Contrast

Minimum contrast ratios (WCAG AA):
- Normal text: **4.5:1**
- Large text (18px+ bold or 24px+): **3:1**
- UI components: **3:1**

Never rely on color alone to convey information.

## Performance

### 19. Image Loading

```html
<!-- Lazy load below-fold images -->
<img src="photo.jpg" alt="Description" loading="lazy" width="800" height="600" decoding="async">

<!-- Eager load hero/above-fold images -->
<link rel="preload" as="image" href="hero.jpg">
```

### 20. Critical Resources

```html
<head>
  <!-- Inline critical CSS or preload -->
  <link rel="preload" href="styles/main.css" as="style">
  <!-- Defer non-critical JS -->
  <script src="scripts/main.js" type="module" defer></script>
</head>
```

### 21. System Font Stack

Use system fonts as the default — no font file downloads needed.

```css
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}
```

## File Organization

### 22. Directory Structure

```
project/
├── index.html
├── styles/
│   ├── main.css          # Single file for small sites
│   ├── base.css           # Reset, tokens, typography (larger sites)
│   ├── components.css     # Component-specific styles
│   └── utilities.css      # Utility classes
├── scripts/
│   └── main.js
└── assets/
    ├── logo.svg
    └── og-image.jpg
```

For single-page sites, one `main.css` and one `main.js` is sufficient. Split only when files exceed ~300 lines.

## JavaScript Patterns

### 23. ES Modules

```html
<script type="module" src="scripts/main.js"></script>
```

```javascript
// scripts/main.js
import { initNav } from "./nav.js";
initNav();
```

### 24. Event Delegation

```javascript
document.querySelector(".card-grid").addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (card) handleCardClick(card);
});
```

### 25. IntersectionObserver for Scroll Effects

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) entry.target.classList.add("visible");
  });
}, { threshold: 0.1 });

document.querySelectorAll(".animate-in").forEach((el) => observer.observe(el));
```

### 26. Template Literals for Dynamic Content

```javascript
function renderCard({ title, description, image }) {
  return `<article class="card">
    <img src="${image}" alt="${title}" loading="lazy" width="400" height="300">
    <h3>${title}</h3>
    <p>${description}</p>
  </article>`;
}
```

## Review Checklist

When reviewing generated frontend code, verify:

- [ ] Semantic HTML used (`header`, `nav`, `main`, `section`, `footer`) — no structural `<div>` soup
- [ ] Page has valid heading hierarchy (`h1` → `h2` → `h3`, no skipped levels)
- [ ] All images have appropriate `alt` text and explicit `width`/`height`
- [ ] Interactive elements are keyboard-accessible with visible `:focus-visible` styles
- [ ] Responsive layout works mobile-first using `min-width` breakpoints
- [ ] CSS custom properties define a consistent design token system
- [ ] JavaScript is vanilla ES modules with `defer` or `type="module"` — no framework dependencies
- [ ] Performance basics met: lazy-loaded images, preloaded critical resources, system font fallback
- [ ] Create everything in docs/loyalty-store folder, create the folder if it doesn't exist
