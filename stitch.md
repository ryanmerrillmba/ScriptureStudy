# Scripture Study App — Google Stitch Prompt

Build a desktop-only scripture study web application with the following exact specifications.

## Layout

The app fills the full viewport with no scrollbars on the body. It is divided into two main sections side-by-side using flexbox:

1. **Left Sidebar** (fixed width 180px, full height, dark background #111, right border #333)
2. **Main Content Area** (flex: 1, all remaining space)

The Main Content Area is a vertical flex column containing:
- A fixed **Top Bar** (height 48px, background #222, bottom border #333)
- A fixed **Column Labels Bar** (height 32px, background #222, bottom border #333)
- A **Scroll Container** (flex: 1, overflow-y: auto) that holds all verse rows

## Left Sidebar

Contains a scrollable list of 39 Old Testament books grouped by category. Each category group starts with a small uppercase label (font-size 10px, color #888, letter-spacing 0.08em) followed by the book names. Categories in order: Law, History, Poetry, Major Prophets, Minor Prophets.

Each book is a clickable div (class `book-item`): padding 5px 12px, font-size 13px, Georgia serif. On hover: background #1f1f1f. When active (selected): color #7a9fcb, left border 3px solid #7a9fcb, background #1f2a36.

## Top Bar

Horizontally centered content with three elements in a flex row:
- Left arrow button (←) — navigates to previous chapter, disabled on chapter 1
- Center: book name (bold, sans-serif 14px) + chapter info (color #888, e.g. "Chapter 3 of 50")
- Right arrow button (→) — navigates to next chapter, disabled on last chapter

Buttons: no background, border 1px solid #333, color #e8e8e0, padding 4px 10px, border-radius 4px. Hover: background #333. Disabled: opacity 0.3.

## Column Labels Bar

Three labels side-by-side, same flex proportions as the three translation columns below:
- "King James Version" (flex: 1)
- "English Standard Version" (flex: 1)
- "Hebrew Interlinear" (flex: 1.4)

Labels: font-family sans-serif, font-size 11px, uppercase, letter-spacing 0.06em, color #888, padding 0 12px. Right border #333 between labels.

## Verse Rows

Each verse is ONE flex row (class `verse-row`) containing exactly three cells side-by-side. The row expands in height to fit its tallest cell — this is what keeps verses aligned across all three translations.

Every even row has background #1e1e1e. All rows have a bottom border #333.

### KJV Cell (class `col-kjv`, flex: 1)
- Padding 10px 12px, font-size 14px, Georgia serif, line-height 1.7, right border #333
- Starts with a superscript verse number (font-size 10px, color #5a7fa0, font-family sans-serif, bold) followed immediately by the verse text

### ESV Cell (class `col-esv`, flex: 1)
- Same styling as KJV cell, right border #333

### Hebrew Interlinear Cell (class `col-interlinear`, flex: 1.4)
- Padding 10px 12px
- Starts with a superscript verse number (same style as above)
- Then a flex-wrap container of **word blocks**

**Word Block** (class `word-block`):
- Inline-flex column, align-items center
- Padding 4px 6px, border 1px solid #2a2a2a, border-radius 4px, background #161616
- Contains three stacked spans:
  1. Hebrew text (class `word-hebrew`): font-size 18px, color #d4c5a0, font-family 'SBL Hebrew' or serif fallback, direction rtl
  2. Strong's number (class `word-strongs`): font-size 9px, color #888, sans-serif
  3. English gloss (class `word-gloss`): font-size 11px, color #bbb, sans-serif, italic, text-align center

## Data Loading

On startup, fetch `data/books.json` (array of 39 book objects: `{name, slug, chapters, category}`). Default to Genesis chapter 1.

When a book/chapter is selected, fetch three JSON files in parallel:
- `data/kjv/{slug}.json`
- `data/esv/{slug}.json`
- `data/interlinear/{slug}.json`

Each has schema: `{book, slug, chapters: [{chapter, verses: [{verse, text}]}]}` for prose, and `{book, slug, chapters: [{chapter, verses: [{verse, words: [{hebrew, strongs, gloss}]}]}]}` for interlinear.

After loading, clear `#verse-rows` and render one `.verse-row` div per verse, with the three cells built from the loaded data. Scroll the container to the top.

## URL Hash Routing

On navigation, update `window.location.hash` to `#{slug}/{chapter}` (e.g. `#genesis/3`). On page load, parse the hash to restore the previous position.

## Color Theme

```
--bg: #1a1a1a
--bg-sidebar: #111
--bg-header: #222
--bg-row-alt: #1e1e1e
--text: #e8e8e0
--text-muted: #888
--accent: #7a9fcb
--verse-num-color: #5a7fa0
--border: #333
--hebrew-color: #d4c5a0
--strongs-color: #888
--gloss-color: #bbb
```

## Empty State

When no book is selected (before first load), show centered text "Select a book to begin." in color #888, sans-serif 14px, inside the scroll container.
