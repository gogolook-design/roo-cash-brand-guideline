# Roo.Cash Brand Guideline — Project Notes

A single-page brand guideline for Roo.Cash 2026 rebrand. The deliverable is `index.html` plus the
locally-bundled assets it depends on. Kept self-contained so it can be opened from disk, zipped,
or hosted statically without a build step.

## Working principles

- **Language**: every word on the page is 繁體中文 (Taiwanese Mandarin). Only exceptions: the
  wordmark "Roo.Cash", color hex codes, font names, CSS token names, chapter eyebrow `CHAPTER 0X`
  labels. No 簡體, no 大陸用語 (`用户` → `使用者/你`; `贷款` → `貸款`; `合作伙伴` → `合作夥伴`).
- **Voice**: "剛好很懂錢的好朋友". Specific, neighborly, numeric. Never deck-speak. Banned:
  賦能、閉環、打造、全方位、一站式、極致體驗、智能（用「聰明」或「AI」）、用戶（用「你」or「使用者」）.
- **Punctuation**: full-width inside Chinese sentences (，。：、！？「」（）). Half-width
  only in pure-English fragments and code.
- **Numbers**: never drop trailing zeros. `2.05%` not `2.5%`. Numbers get the orange highlight,
  surrounding text stays navy — never recolor whole sentences.

## File layout

```
index.html                       # the guideline itself (single page, 10 chapters)
styles/colors_and_type.css       # design system tokens — copied verbatim from the handoff bundle
fonts/NotoSansTC-VariableFont_wght.ttf
assets/logos/                    # roo-cash-horizontal-{dark,white}.png, gogolook-white.png
CLAUDE.md                        # this file
MEMORY.md                        # project memory (auto-created)
```

`styles/colors_and_type.css` is the **single source of truth for tokens**. Don't redefine colors
or type sizes inline — pull from `--nroo-*` variables and `.h1` / `.b1` / `.num-md` semantic
classes. The only inline hex values allowed are inside the SVG mascot in chapter 08, because
those need stroke colors that survive being copied out into Figma/illustrator.

The font `@font-face` was repointed from `url("fonts/...")` (project-root layout in the original
bundle) to `url("../fonts/...")` because we moved the CSS into `styles/`. If you ever flatten the
directory, undo that change.

## Design tokens (the locked decisions)

| Token | Value | Used for |
|---|---|---|
| Trust `#021C26` | `--nroo-blue-100` | Logo, primary text, dark surfaces, H1/H2 |
| Pulse `#25C9BA` | `--nroo-green-100` | All primary CTAs. Hover → `#14A571` |
| Spark `#FF601A` | `--nroo-orange-120` | Numeric highlights only. Almost never a fill. |
| Clear `#F2F6F8` | `--nroo-grey-10` | Page canvas. White is reserved for cards. |

**Do not introduce a 5th brand color.** The framework draft proposed mint `#4ECDC4` — explicitly
rejected by the user; the live design system palette wins.

Type stack: Noto Sans TC (CJK, primary), Roboto Condensed Light (large numerics), IBM Plex Sans
(input chrome), PingFang TC (Apple fallback). Body line-height is **1.75** — that's a brand
fingerprint, not a default; preserve it.

Radii: 30 (hero/style cards), 16–24 (product cards), 12 (panels), 8 (chips), 6 (inputs).
Primary CTA radius is **16** (wider than typical fintech — keep it).

## Layout system

- Max content width 1200 px (style sheets stretch to 1280).
- Section vertical rhythm: **120 px desktop / 80 px mobile** between chapters.
- Hero overlapping stat strip pulls up `-64px` on desktop, `-48px` on mobile.
- Sticky header is 72 px tall; `scroll-padding-top: 88px` accounts for it on TOC anchor jumps.
- Mobile breakpoint is 960 px (single-column grids, hidden top-nav, stat-strip 2-up).

## Mascot rules

The original design system says the kangaroo is **Logo-only**. The 2026 brand expands this. The
4 SVG poses in chapter 08 (idle / pointing / cheering / thinking) are **v1 placeholder direction**
drawn from geometric primitives — clearly labeled as such in copy. When the real illustrator
delivers, swap the SVGs but keep the same 4 poses, same 48–240 px size range, same Do/Don't list.

## What lives where (sources)

- New brand copy (story, personality, values, tone): pulled verbatim from
  `/Users/jasonlin/Downloads/roo_brand_framework_zh.html`. Update there first, then port across.
- Visual rules (logo, color, type, layout, motion, iconography): authoritative source is the
  design system handoff bundle at `/tmp/design_extract/roo-cash-design-system/` (extracted from
  the gzip at `https://api.anthropic.com/v1/design/h/jlN7FSRJsPAAPmhgPegreQ`). The bundle is
  ephemeral — if `/tmp` is wiped, refetch and re-extract.
- Live product reference: `https://roo.cash/`. WebFetch returns 403; use the bundle's
  `ui_kits/roo-cash-web/HomePage.jsx` as the canonical layout reference instead.

## Verification

When changing the page:
1. Open `file://.../index.html` directly — must work without a server.
2. Resize to 375 / 960 / 1440 — single column at <960, 2-up stat strip, gutter relaxes.
3. DevTools color-picker any element — should resolve to a `--nroo-*` token, not a raw hex.
4. Tab through TOC links — anchor offsets clear the sticky header.
5. Print preview — must read cleanly (brand guidelines get printed).

## Stale info to ignore

The global memory entry `~/.claude/memory/domain/brand-tokens.md` lists Roo.Cash as
`#FF6B35 / Inter`. **That's stale** — it predates the 2026 design system. Don't propagate it.
The user has been told; pending their go-ahead to update.

## Global Memory

Read `~/.claude/CLAUDE.md` for memory rules and topic files.
