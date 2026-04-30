# Roo.Cash 2026 Brand Guideline · Issue 01

A single-page brand guideline for Roo.Cash (袋鼠金融 — Gogolook's Taiwan personal-finance comparison product). Self-contained static HTML, no build step.

## Live preview

Hosted on GitHub Pages. Open the site URL and enter the access password to view.

> **Soft gate, not real protection.** This is a public repo with a client-side password check. Both passwords (`1234` and `roocash2026`) are visible in `index.html`. Treat the gate as a polite "internal preview" notice, not authentication.

## Local preview

```bash
open index.html
# or
python3 -m http.server 8000
# then visit http://localhost:8000
```

No build step. Open the file directly from disk and it works.

## What's inside

```
index.html                       # the guideline (10 chapters, 繁體中文)
styles/colors_and_type.css       # design system tokens (navy/green/orange/cream)
fonts/NotoSansTC-VariableFont_wght.ttf
assets/logos/                    # roo-cash dark/white, gogolook white
CLAUDE.md                        # project conventions for AI collaborators
MEMORY.md                        # project memory
```

## Brand at a glance

| Token | Value | Use |
|---|---|---|
| Navy | `#112858` | Primary text, logo, dark surfaces |
| Green | `#00E0A0` | All primary CTAs |
| Orange | `#D84421` | Numeric highlights only |
| Cream | `#F8F8F8` / `#FBFAF6` | Page canvas |

Type stack:
- **Noto Serif TC (思源宋體)** — display: hero, chapter titles, pull quotes
- **Noto Sans TC (思源黑體)** — body, UI, card titles
- **Newsreader Italic** — English display italic
- **Roboto Condensed Light** — large numerics
- **IBM Plex Mono** — micro-labels, eyebrows, IDs, folios

See chapter 07 of the guideline for the full type spec, pairing rules, and the alternatives that were considered.

## Issue / status

`v1.0 · 2026 Spring · Internal Draft`. See `CLAUDE.md` for working principles, voice rules, and locked decisions.

## Contact

Brand questions → Slack `#brand-roocash`
