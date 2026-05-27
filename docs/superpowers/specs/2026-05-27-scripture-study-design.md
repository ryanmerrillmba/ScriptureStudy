# Scripture Study Website — Design Spec
**Date:** 2026-05-27  
**Status:** Approved

---

## Overview

A static, self-contained scripture study website hosted on Cloudflare Pages and accessed privately via Tailscale. Displays three parallel Bible translations side-by-side with synchronized verse alignment, focused on the Old Testament.

---

## Layout

Four columns, desktop browser only:

| Column | Width | Content |
|--------|-------|---------|
| Book navigation | ~180px fixed | All 39 OT books, grouped by category |
| KJV | flex 1 | King James Version text |
| ESV | flex 1 | English Standard Version text |
| Interlinear | flex 1.5 | Hebrew word blocks (Hebrew → transliteration → gloss) |

**Verse alignment mechanism:** Each verse is a single `div.verse-row` containing three side-by-side flex cells. The row height automatically expands to match the tallest cell (always the interlinear column). No JavaScript required for alignment.

**Fixed header bar:** Displays current book + chapter number + total chapters, with prev/next chapter arrows and a chapter-jump dropdown. Does not scroll.

**Left sidebar:** Fixed. Books grouped by category (Law, History, Poetry, Major Prophets, Minor Prophets) with subtle category labels. Active book highlighted.

**Scroll container:** Single scrollable area beneath the header containing all verse rows. Sidebar and header remain fixed.

---

## Data Layer

All data is bundled into the Cloudflare Pages deployment — no runtime external dependencies. Files are loaded lazily (on book selection only).

### Sources

| Translation | Source | License |
|-------------|--------|---------|
| KJV | `aruljohn/Bible-kjv` (GitHub) | Public domain |
| ESV | User-provided `.txt` file → converted via Python script | Personal use |
| Hebrew Interlinear | `openscriptures/morphhb` (GitHub) | CC BY 4.0 |

### File Structure

```
/data/
  kjv/genesis.json, exodus.json, ... (39 files)
  esv/genesis.json, exodus.json, ... (39 files)
  interlinear/genesis.json, exodus.json, ... (39 files)
```

### JSON Schemas

**KJV / ESV:**
```json
{
  "book": "Genesis",
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        { "verse": 1, "text": "In the beginning..." }
      ]
    }
  ]
}
```

**Interlinear:**
```json
{
  "book": "Genesis",
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "words": [
            {
              "hebrew": "בְּרֵאשִׁית",
              "transliteration": "bə-rê-šîṯ",
              "strongs": "H7225",
              "gloss": "In the beginning"
            }
          ]
        }
      ]
    }
  ]
}
```

### Estimated Sizes

| Dataset | Estimated Size |
|---------|---------------|
| KJV OT | ~2MB |
| ESV OT | ~2MB |
| Hebrew Interlinear OT | ~15–20MB |

---

## Navigation & Interactions

**Book selection:** Click any book in the left sidebar → loads Chapter 1 of that book. Active book is highlighted.

**Chapter navigation:** Prev/next arrows in the fixed header. Clicking the chapter number opens a dropdown to jump to any chapter directly.

**Verse display:**
- Verse number appears at the left edge of each translation cell
- KJV and ESV: plain prose text
- Interlinear: stacked word blocks — Hebrew script (large) on top, transliteration (small italic) in middle, English gloss (small) below
- Alternating row background or subtle divider lines between verses for readability

**Scrolling:** Single scroll container covers all three translation columns together. Sidebar and header fixed.

---

## Deployment

- **Host:** Cloudflare Pages (free tier)
- **Access:** Private via Tailscale network
- **Data prep (one-time, local):** Run Python scripts to generate all 117 JSON data files, then commit them to the repo
- **Cloudflare build:** No build step — pure static HTML/CSS/JS + pre-generated JSON data files
- **New Testament:** Not in scope for v1. Same architecture supports it — add NT data files and book list entries when ready.

---

## Deliverables

1. **`index.html` + `style.css` + `app.js`** — the website
2. **`scripts/convert_esv.py`** — Python script to parse user's ESV `.txt` into per-book JSON
3. **`scripts/fetch_data.py`** — Python script to download and convert KJV and interlinear source data into the required JSON schema
4. **`data/`** — all 117 JSON files (39 books × 3 translations)
5. **`stitch.md`** — Google Stitch prompt to build the interface

---

## Deferred

- Verse highlighting and annotation
- New Testament support
- Mobile/tablet layout
