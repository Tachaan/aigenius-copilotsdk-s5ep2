---
mode: 'agent'
description: 'Audit code for accessibility issues and WCAG compliance'
tools: ['read', 'search']
agents: ['accessibility-auditor']
---

Review the following code for accessibility issues and WCAG 2.1 Level AA compliance.

## Instructions

1. **Scan** the provided code or files for accessibility violations
2. **Categorize** issues by severity: Critical, Major, Minor
3. **Provide fixes** with specific code examples for each issue
4. **Summarize** overall WCAG compliance level

## Focus Areas

- Semantic HTML and heading hierarchy
- ARIA roles, attributes, and labels
- Keyboard navigation and focus management
- Color contrast ratios (4.5:1 text, 3:1 UI)
- Alt text and media accessibility
- Form labels and error messaging

## Output

For each issue found, include:
- **Location**: File and line reference
- **Severity**: Critical / Major / Minor
- **WCAG Criterion**: The specific guideline violated (e.g., 1.1.1 Non-text Content)
- **Impact**: Who is affected and how
- **Fix**: Code example showing the corrected implementation

End with a compliance summary and any positive accessibility patterns observed.
