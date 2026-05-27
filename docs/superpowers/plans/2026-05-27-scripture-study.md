# Scripture Study Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained static scripture study website with three parallel Bible translations (KJV, ESV, Hebrew interlinear) synchronized by verse, hosted on Cloudflare Pages.

**Architecture:** All Bible data is pre-bundled as per-book JSON files under `data/`. A Python data-prep pipeline (run once locally) downloads KJV, converts the user's ESV .txt, and converts the OSHB Hebrew interlinear XML into the shared JSON schema. The frontend is vanilla HTML/CSS/ES-module JS — no framework, no build step on Cloudflare.

**Tech Stack:** Python 3 + pytest (data prep), Vanilla JS ES modules, CSS Flexbox, Cloudflare Pages (static hosting)

---

## File Map

```
ScriptureReading/
├── index.html
├── style.css
├── js/
│   ├── app.js               # state, routing, wires components
│   ├── sidebar.js           # book list panel
│   ├── header.js            # fixed top bar + chapter nav
│   ├── prose-renderer.js    # KJV + ESV column renderer (shared)
│   └── interlinear-renderer.js  # Hebrew word-block renderer
├── data/
│   ├── books.json           # 39 OT book metadata
│   ├── kjv/                 # genesis.json … malachi.json
│   ├── esv/                 # genesis.json … malachi.json
│   └── interlinear/         # genesis.json … malachi.json
├── scripts/
│   ├── convert_esv.py       # parse ESV .txt → per-book JSON
│   ├── fetch_kjv.py         # download KJV from GitHub → per-book JSON
│   ├── fetch_interlinear.py # download OSHB XML + Strong's → per-book JSON
│   └── tests/
│       ├── test_convert_esv.py
│       ├── test_fetch_kjv.py
│       └── test_fetch_interlinear.py
├── stitch.md
└── docs/
    └── superpowers/
        ├── specs/2026-05-27-scripture-study-design.md
        └── plans/2026-05-27-scripture-study.md
```

---

## JSON Schemas (shared across all tasks)

**KJV / ESV per-book:**
```json
{
  "book": "Genesis",
  "slug": "genesis",
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

**Interlinear per-book:**
```json
{
  "book": "Genesis",
  "slug": "genesis",
  "chapters": [
    {
      "chapter": 1,
      "verses": [
        {
          "verse": 1,
          "words": [
            { "hebrew": "בְּרֵאשִׁ֖ית", "strongs": "H7225", "gloss": "beginning" }
          ]
        }
      ]
    }
  ]
}
```

---

## Task 1: Project Scaffold + Git Init

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Verify working directory exists and is empty**

```bash
ls "/home/ryan/Documents/Shared Work/Projects/ScriptureReading/"
```
Expected: Only the `docs/` directory.

- [ ] **Step 2: Create directory structure**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
mkdir -p js data/kjv data/esv data/interlinear scripts/tests
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.env
node_modules/
.DS_Store
```

- [ ] **Step 4: Git init and first commit**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
git init && \
git add .gitignore docs/ && \
git commit -m "chore: init project with spec and plan"
```

---

## Task 2: books.json Metadata

**Files:**
- Create: `data/books.json`

- [ ] **Step 1: Create books.json**

```json
[
  { "name": "Genesis",        "slug": "genesis",        "chapters": 50,  "category": "Law" },
  { "name": "Exodus",         "slug": "exodus",         "chapters": 40,  "category": "Law" },
  { "name": "Leviticus",      "slug": "leviticus",      "chapters": 27,  "category": "Law" },
  { "name": "Numbers",        "slug": "numbers",        "chapters": 36,  "category": "Law" },
  { "name": "Deuteronomy",    "slug": "deuteronomy",    "chapters": 34,  "category": "Law" },
  { "name": "Joshua",         "slug": "joshua",         "chapters": 24,  "category": "History" },
  { "name": "Judges",         "slug": "judges",         "chapters": 21,  "category": "History" },
  { "name": "Ruth",           "slug": "ruth",           "chapters": 4,   "category": "History" },
  { "name": "1 Samuel",       "slug": "1-samuel",       "chapters": 31,  "category": "History" },
  { "name": "2 Samuel",       "slug": "2-samuel",       "chapters": 24,  "category": "History" },
  { "name": "1 Kings",        "slug": "1-kings",        "chapters": 22,  "category": "History" },
  { "name": "2 Kings",        "slug": "2-kings",        "chapters": 25,  "category": "History" },
  { "name": "1 Chronicles",   "slug": "1-chronicles",   "chapters": 29,  "category": "History" },
  { "name": "2 Chronicles",   "slug": "2-chronicles",   "chapters": 36,  "category": "History" },
  { "name": "Ezra",           "slug": "ezra",           "chapters": 10,  "category": "History" },
  { "name": "Nehemiah",       "slug": "nehemiah",       "chapters": 13,  "category": "History" },
  { "name": "Esther",         "slug": "esther",         "chapters": 10,  "category": "History" },
  { "name": "Job",            "slug": "job",            "chapters": 42,  "category": "Poetry" },
  { "name": "Psalms",         "slug": "psalms",         "chapters": 150, "category": "Poetry" },
  { "name": "Proverbs",       "slug": "proverbs",       "chapters": 31,  "category": "Poetry" },
  { "name": "Ecclesiastes",   "slug": "ecclesiastes",   "chapters": 12,  "category": "Poetry" },
  { "name": "Song of Solomon","slug": "song-of-solomon","chapters": 8,   "category": "Poetry" },
  { "name": "Isaiah",         "slug": "isaiah",         "chapters": 66,  "category": "Major Prophets" },
  { "name": "Jeremiah",       "slug": "jeremiah",       "chapters": 52,  "category": "Major Prophets" },
  { "name": "Lamentations",   "slug": "lamentations",   "chapters": 5,   "category": "Major Prophets" },
  { "name": "Ezekiel",        "slug": "ezekiel",        "chapters": 48,  "category": "Major Prophets" },
  { "name": "Daniel",         "slug": "daniel",         "chapters": 12,  "category": "Major Prophets" },
  { "name": "Hosea",          "slug": "hosea",          "chapters": 14,  "category": "Minor Prophets" },
  { "name": "Joel",           "slug": "joel",           "chapters": 3,   "category": "Minor Prophets" },
  { "name": "Amos",           "slug": "amos",           "chapters": 9,   "category": "Minor Prophets" },
  { "name": "Obadiah",        "slug": "obadiah",        "chapters": 1,   "category": "Minor Prophets" },
  { "name": "Jonah",          "slug": "jonah",          "chapters": 4,   "category": "Minor Prophets" },
  { "name": "Micah",          "slug": "micah",          "chapters": 7,   "category": "Minor Prophets" },
  { "name": "Nahum",          "slug": "nahum",          "chapters": 3,   "category": "Minor Prophets" },
  { "name": "Habakkuk",       "slug": "habakkuk",       "chapters": 3,   "category": "Minor Prophets" },
  { "name": "Zephaniah",      "slug": "zephaniah",      "chapters": 3,   "category": "Minor Prophets" },
  { "name": "Haggai",         "slug": "haggai",         "chapters": 2,   "category": "Minor Prophets" },
  { "name": "Zechariah",      "slug": "zechariah",      "chapters": 14,  "category": "Minor Prophets" },
  { "name": "Malachi",        "slug": "malachi",        "chapters": 4,   "category": "Minor Prophets" }
]
```

- [ ] **Step 2: Commit**

```bash
git add data/books.json && git commit -m "data: add OT book metadata"
```

---

## Task 3: ESV Converter Script

**Files:**
- Create: `scripts/convert_esv.py`
- Create: `scripts/tests/test_convert_esv.py`

The ESV .txt format (observed): chapter 1 verse 1 is marked `1:1 <text>`, subsequent chapters with `N:1 <text>`. Verses 2+ within a chapter appear inline — the verse number immediately precedes the text with no space (e.g. `3And God said`). Footnotes appear as `[N]`. Section headings are lines without verse numbers (indented or standalone).

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_convert_esv.py
import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from convert_esv import parse_book_content, clean_text

def test_clean_text_removes_footnotes():
    assert clean_text("the earth.[1] And God") == "the earth. And God"

def test_clean_text_normalizes_whitespace():
    assert clean_text("  too   many   spaces  ") == "too many spaces"

def test_parse_book_content_returns_correct_chapter_count():
    sample = """
          The Creation of the World
1:1 In the beginning God created the heavens and the earth. 2The earth was formless.
3And God said.
2:1 Thus the heavens were finished. 2And on the seventh day God rested.
"""
    result = parse_book_content("Genesis", sample)
    assert len(result["chapters"]) == 2

def test_parse_book_content_verse_1_chapter_1():
    sample = """
1:1 In the beginning God created the heavens and the earth. 2The earth was formless.
"""
    result = parse_book_content("Genesis", sample)
    v1 = result["chapters"][0]["verses"][0]
    assert v1["verse"] == 1
    assert "In the beginning" in v1["text"]

def test_parse_book_content_verse_2_chapter_1():
    sample = """
1:1 In the beginning God created the heavens and the earth. 2The earth was formless.
"""
    result = parse_book_content("Genesis", sample)
    v2 = result["chapters"][0]["verses"][1]
    assert v2["verse"] == 2
    assert "formless" in v2["text"]

def test_parse_book_content_chapter_2_verse_1():
    sample = """
1:1 First verse. 2Second verse.
2:1 Chapter two opens here. 2Another verse.
"""
    result = parse_book_content("Genesis", sample)
    ch2 = result["chapters"][1]
    assert ch2["chapter"] == 2
    assert ch2["verses"][0]["verse"] == 1
    assert "Chapter two" in ch2["verses"][0]["text"]
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_convert_esv.py -v 2>&1 | head -30
```
Expected: ImportError or ModuleNotFoundError for `convert_esv`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/convert_esv.py
"""Parse the ESV .txt file into per-book JSON files matching the shared schema."""
import re
import json
import sys
from pathlib import Path

OT_BOOKS = [
    ("GENESIS", "genesis"), ("EXODUS", "exodus"), ("LEVITICUS", "leviticus"),
    ("NUMBERS", "numbers"), ("DEUTERONOMY", "deuteronomy"), ("JOSHUA", "joshua"),
    ("JUDGES", "judges"), ("RUTH", "ruth"), ("1 SAMUEL", "1-samuel"),
    ("2 SAMUEL", "2-samuel"), ("1 KINGS", "1-kings"), ("2 KINGS", "2-kings"),
    ("1 CHRONICLES", "1-chronicles"), ("2 CHRONICLES", "2-chronicles"),
    ("EZRA", "ezra"), ("NEHEMIAH", "nehemiah"), ("ESTHER", "esther"),
    ("JOB", "job"), ("PSALMS", "psalms"), ("PROVERBS", "proverbs"),
    ("ECCLESIASTES", "ecclesiastes"), ("SONG OF SOLOMON", "song-of-solomon"),
    ("ISAIAH", "isaiah"), ("JEREMIAH", "jeremiah"), ("LAMENTATIONS", "lamentations"),
    ("EZEKIEL", "ezekiel"), ("DANIEL", "daniel"), ("HOSEA", "hosea"),
    ("JOEL", "joel"), ("AMOS", "amos"), ("OBADIAH", "obadiah"),
    ("JONAH", "jonah"), ("MICAH", "micah"), ("NAHUM", "nahum"),
    ("HABAKKUK", "habakkuk"), ("ZEPHANIAH", "zephaniah"), ("HAGGAI", "haggai"),
    ("ZECHARIAH", "zechariah"), ("MALACHI", "malachi"),
]
BOOK_NAME_TO_SLUG = {name: slug for name, slug in OT_BOOKS}
DISPLAY_NAME = {name: name.title().replace("Of", "of") for name, _ in OT_BOOKS}
DISPLAY_NAME["SONG OF SOLOMON"] = "Song of Solomon"
DISPLAY_NAME["1 SAMUEL"] = "1 Samuel"
DISPLAY_NAME["2 SAMUEL"] = "2 Samuel"
DISPLAY_NAME["1 KINGS"] = "1 Kings"
DISPLAY_NAME["2 KINGS"] = "2 Kings"
DISPLAY_NAME["1 CHRONICLES"] = "1 Chronicles"
DISPLAY_NAME["2 CHRONICLES"] = "2 Chronicles"


def clean_text(text: str) -> str:
    """Remove footnote markers and normalize whitespace."""
    text = re.sub(r'\[\d+\]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def parse_book_content(book_name: str, content: str) -> dict:
    """Parse a single book's raw text into the shared JSON schema."""
    content = clean_text(content)

    # Split on chapter:verse markers (e.g. "1:1 " or "2:1 ")
    # These always mark verse 1 of a new chapter
    chapter_pattern = re.compile(r'(\d+):1\s')
    chapter_splits = list(chapter_pattern.finditer(content))

    chapters = []
    for i, match in enumerate(chapter_splits):
        chapter_num = int(match.group(1))
        text_start = match.end()
        text_end = chapter_splits[i + 1].start() if i + 1 < len(chapter_splits) else len(content)
        chapter_text = content[text_start:text_end].strip()

        # First verse text runs until the next inline verse number
        # Inline verse numbers: a bare integer immediately followed by a capital letter or quote
        # Pattern: preceded by whitespace (or start), digit(s), then uppercase/quote (no space)
        verse_split = re.compile(r'(?<=\s)(\d+)(?=[A-Z"‘“])')
        verse_splits = list(verse_split.finditer(chapter_text))

        verses = []
        # Verse 1: everything before the first inline verse number
        v1_end = verse_splits[0].start() if verse_splits else len(chapter_text)
        v1_text = chapter_text[:v1_end].strip()
        if v1_text:
            verses.append({"verse": 1, "text": v1_text})

        # Remaining verses
        for j, vs in enumerate(verse_splits):
            verse_num = int(vs.group(1))
            vs_start = vs.end()
            vs_end = verse_splits[j + 1].start() if j + 1 < len(verse_splits) else len(chapter_text)
            verse_text = chapter_text[vs_start:vs_end].strip()
            if verse_text:
                verses.append({"verse": verse_num, "text": verse_text})

        chapters.append({"chapter": chapter_num, "verses": verses})

    slug = BOOK_NAME_TO_SLUG.get(book_name.upper(), book_name.lower())
    display = DISPLAY_NAME.get(book_name.upper(), book_name.title())
    return {"book": display, "slug": slug, "chapters": chapters}


def parse_esv(source_path: str, output_dir: str) -> None:
    text = Path(source_path).read_text(encoding='utf-8')

    # Find the last occurrence of each OT book header (ALL CAPS on its own line)
    # The last occurrence is the actual content section, not the ToC entry
    book_positions = {}
    for book_name, _ in OT_BOOKS:
        pattern = re.compile(rf'(?m)^{re.escape(book_name)}\s*$')
        matches = list(pattern.finditer(text))
        if matches:
            book_positions[book_name] = matches[-1].end()

    sorted_books = sorted(book_positions.items(), key=lambda x: x[1])
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i, (book_name, start) in enumerate(sorted_books):
        end = sorted_books[i + 1][1] if i + 1 < len(sorted_books) else len(text)
        book_content = text[start:end]
        book_data = parse_book_content(book_name, book_content)
        slug = BOOK_NAME_TO_SLUG[book_name]
        (out / f'{slug}.json').write_text(
            json.dumps(book_data, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        print(f"  {slug}: {len(book_data['chapters'])} chapters, "
              f"{sum(len(c['verses']) for c in book_data['chapters'])} verses")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_esv.py <source.txt> <output_dir>")
        sys.exit(1)
    parse_esv(sys.argv[1], sys.argv[2])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_convert_esv.py -v
```
Expected: 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/convert_esv.py scripts/tests/test_convert_esv.py && \
git commit -m "feat: add ESV text converter script"
```

---

## Task 4: KJV Fetch Script

**Files:**
- Create: `scripts/fetch_kjv.py`
- Create: `scripts/tests/test_fetch_kjv.py`

Source: `aruljohn/Bible-kjv` on GitHub. Each OT book is a JSON file at:
`https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/{BookName}.json`
where `BookName` is title-cased (e.g. `Genesis.json`, `1Samuel.json`).

The source schema is already: `{ book, chapters: [{ chapter, verses: [{ verse, text }] }] }`.
Our script adds the `slug` field and downloads only the 39 OT books.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_fetch_kjv.py
import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))
from fetch_kjv import transform_book, kjv_github_filename

def test_kjv_github_filename_simple():
    assert kjv_github_filename("genesis") == "Genesis"

def test_kjv_github_filename_numbered():
    assert kjv_github_filename("1-samuel") == "1Samuel"

def test_kjv_github_filename_song():
    assert kjv_github_filename("song-of-solomon") == "SongofSolomon"

def test_transform_book_adds_slug():
    raw = {
        "book": "Genesis",
        "chapters": [
            {"chapter": 1, "verses": [{"verse": 1, "text": "In the beginning..."}]}
        ]
    }
    result = transform_book(raw, "genesis")
    assert result["slug"] == "genesis"
    assert result["book"] == "Genesis"
    assert result["chapters"][0]["verses"][0]["verse"] == 1

def test_transform_book_preserves_all_chapters():
    raw = {
        "book": "Ruth",
        "chapters": [
            {"chapter": i, "verses": [{"verse": 1, "text": "verse"}]}
            for i in range(1, 5)
        ]
    }
    result = transform_book(raw, "ruth")
    assert len(result["chapters"]) == 4
```

- [ ] **Step 2: Run to verify failure**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_fetch_kjv.py -v 2>&1 | head -20
```
Expected: ImportError for `fetch_kjv`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/fetch_kjv.py
"""Download KJV per-book JSON from GitHub and convert to shared schema."""
import json
import sys
import urllib.request
from pathlib import Path

OT_SLUGS = [
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth", "1-samuel", "2-samuel",
    "1-kings", "2-kings", "1-chronicles", "2-chronicles",
    "ezra", "nehemiah", "esther", "job", "psalms", "proverbs",
    "ecclesiastes", "song-of-solomon", "isaiah", "jeremiah",
    "lamentations", "ezekiel", "daniel", "hosea", "joel", "amos",
    "obadiah", "jonah", "micah", "nahum", "habakkuk", "zephaniah",
    "haggai", "zechariah", "malachi",
]

BASE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master"


def kjv_github_filename(slug: str) -> str:
    """Convert our slug to the GitHub repo's filename convention."""
    parts = slug.split('-')
    # Remove leading number prefix for the join, keep it at front
    return ''.join(p.title() for p in parts).replace('Of', 'of').replace('of', 'of')


def transform_book(raw: dict, slug: str) -> dict:
    """Add slug field to the raw KJV JSON (schema already matches ours)."""
    return {
        "book": raw["book"],
        "slug": slug,
        "chapters": raw["chapters"],
    }


def fetch_kjv(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for slug in OT_SLUGS:
        filename = kjv_github_filename(slug)
        url = f"{BASE_URL}/{filename}.json"
        print(f"  Fetching {url}...")
        try:
            with urllib.request.urlopen(url) as resp:
                raw = json.loads(resp.read().decode('utf-8'))
            book_data = transform_book(raw, slug)
            (out / f'{slug}.json').write_text(
                json.dumps(book_data, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            print(f"    OK: {len(book_data['chapters'])} chapters")
        except Exception as e:
            print(f"    ERROR fetching {slug}: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fetch_kjv.py <output_dir>")
        sys.exit(1)
    fetch_kjv(sys.argv[1])
```

- [ ] **Step 4: Run tests**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_fetch_kjv.py -v
```
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_kjv.py scripts/tests/test_fetch_kjv.py && \
git commit -m "feat: add KJV fetch script"
```

---

## Task 5: Interlinear Fetch Script

**Files:**
- Create: `scripts/fetch_interlinear.py`
- Create: `scripts/tests/test_fetch_interlinear.py`

Sources:
- OSHB XML (one file per book): `https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc/{OSIS_ID}.xml`
- Strong's Hebrew lexicon JSON: `https://raw.githubusercontent.com/openscriptures/strongs/master/hebrew/strongs-hebrew-dictionary.js` (strip `module.exports = ` prefix, parse as JSON)

OSHB OSIS IDs: `Gen Exod Lev Num Deut Josh Judg Ruth 1Sam 2Sam 1Kgs 2Kgs 1Chr 2Chr Ezra Neh Esth Job Ps Prov Eccl Song Isa Jer Lam Ezek Dan Hos Joel Amos Obad Jonah Mic Nah Hab Zeph Hag Zech Mal`

The lemma attribute in OSHB looks like `strong:H07225` or `strong:H01254 strong:H07225`. We extract the first H-number, normalize it (strip leading zeros: `H07225` → `H7225`), and look up the `kjv_def` field in the Strong's dictionary for the English gloss.

- [ ] **Step 1: Write the failing test**

```python
# scripts/tests/test_fetch_interlinear.py
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from fetch_interlinear import normalize_strongs, extract_first_strongs, parse_word_element
from unittest.mock import MagicMock

def test_normalize_strongs_strips_leading_zeros():
    assert normalize_strongs("H07225") == "H7225"
    assert normalize_strongs("H01254") == "H1254"

def test_normalize_strongs_no_leading_zeros():
    assert normalize_strongs("H430") == "H430"

def test_extract_first_strongs_single():
    assert extract_first_strongs("strong:H07225") == "H7225"

def test_extract_first_strongs_multiple():
    assert extract_first_strongs("strong:H01254 strong:H07225") == "H1254"

def test_extract_first_strongs_none():
    assert extract_first_strongs("") is None

def test_parse_word_element_returns_word_dict():
    glosses = {"H7225": "beginning"}
    mock_elem = MagicMock()
    mock_elem.text = "בְּרֵאשִׁ֖ית"
    mock_elem.get = lambda attr, default="": "strong:H07225" if attr == "lemma" else default
    result = parse_word_element(mock_elem, glosses)
    assert result["hebrew"] == "בְּרֵאשִׁ֖ית"
    assert result["strongs"] == "H7225"
    assert result["gloss"] == "beginning"

def test_parse_word_element_unknown_strongs():
    glosses = {}
    mock_elem = MagicMock()
    mock_elem.text = "someword"
    mock_elem.get = lambda attr, default="": "strong:H99999" if attr == "lemma" else default
    result = parse_word_element(mock_elem, glosses)
    assert result["strongs"] == "H99999"
    assert result["gloss"] == ""
```

- [ ] **Step 2: Run to verify failure**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_fetch_interlinear.py -v 2>&1 | head -20
```
Expected: ImportError for `fetch_interlinear`.

- [ ] **Step 3: Write the implementation**

```python
# scripts/fetch_interlinear.py
"""Download OSHB Hebrew interlinear XML + Strong's lexicon, output per-book JSON."""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

OSIS_NS = "http://www.bibletex.org/schema/osisCore.2.1.1"

OT_BOOKS = [
    ("genesis", "Gen"), ("exodus", "Exod"), ("leviticus", "Lev"),
    ("numbers", "Num"), ("deuteronomy", "Deut"), ("joshua", "Josh"),
    ("judges", "Judg"), ("ruth", "Ruth"), ("1-samuel", "1Sam"),
    ("2-samuel", "2Sam"), ("1-kings", "1Kgs"), ("2-kings", "2Kgs"),
    ("1-chronicles", "1Chr"), ("2-chronicles", "2Chr"), ("ezra", "Ezra"),
    ("nehemiah", "Neh"), ("esther", "Esth"), ("job", "Job"),
    ("psalms", "Ps"), ("proverbs", "Prov"), ("ecclesiastes", "Eccl"),
    ("song-of-solomon", "Song"), ("isaiah", "Isa"), ("jeremiah", "Jer"),
    ("lamentations", "Lam"), ("ezekiel", "Ezek"), ("daniel", "Dan"),
    ("hosea", "Hos"), ("joel", "Joel"), ("amos", "Amos"),
    ("obadiah", "Obad"), ("jonah", "Jonah"), ("micah", "Mic"),
    ("nahum", "Nah"), ("habakkuk", "Hab"), ("zephaniah", "Zeph"),
    ("haggai", "Hag"), ("zechariah", "Zech"), ("malachi", "Mal"),
]

SLUG_TO_DISPLAY = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy", "joshua": "Joshua",
    "judges": "Judges", "ruth": "Ruth", "1-samuel": "1 Samuel",
    "2-samuel": "2 Samuel", "1-kings": "1 Kings", "2-kings": "2 Kings",
    "1-chronicles": "1 Chronicles", "2-chronicles": "2 Chronicles",
    "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther",
    "job": "Job", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song-of-solomon": "Song of Solomon",
    "isaiah": "Isaiah", "jeremiah": "Jeremiah", "lamentations": "Lamentations",
    "ezekiel": "Ezekiel", "daniel": "Daniel", "hosea": "Hosea",
    "joel": "Joel", "amos": "Amos", "obadiah": "Obadiah",
    "jonah": "Jonah", "micah": "Micah", "nahum": "Nahum",
    "habakkuk": "Habakkuk", "zephaniah": "Zephaniah", "haggai": "Haggai",
    "zechariah": "Zechariah", "malachi": "Malachi",
}

OSHB_BASE = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc"
STRONGS_URL = "https://raw.githubusercontent.com/openscriptures/strongs/master/hebrew/strongs-hebrew-dictionary.js"


def normalize_strongs(code: str) -> str:
    """Strip leading zeros from a Strong's number: H07225 -> H7225."""
    if not code:
        return code
    letter = code[0]
    number = code[1:].lstrip('0') or '0'
    return f"{letter}{number}"


def extract_first_strongs(lemma: str) -> str | None:
    """Extract and normalize the first Strong's number from a lemma attribute."""
    match = re.search(r'strong:(H\d+)', lemma)
    if not match:
        return None
    return normalize_strongs(match.group(1))


def parse_word_element(elem, glosses: dict) -> dict:
    """Convert an OSHB <w> element to our word dict."""
    lemma = elem.get("lemma", "")
    strongs = extract_first_strongs(lemma) or ""
    return {
        "hebrew": elem.text or "",
        "strongs": strongs,
        "gloss": glosses.get(strongs, ""),
    }


def fetch_strongs_glosses() -> dict:
    """Download Strong's Hebrew dictionary, return {H1234: 'gloss string'} map."""
    print("  Fetching Strong's Hebrew lexicon...")
    with urllib.request.urlopen(STRONGS_URL) as resp:
        raw = resp.read().decode('utf-8')
    # Strip JS module wrapper: "module.exports = {...}"
    raw = re.sub(r'^.*?=\s*', '', raw, count=1, flags=re.DOTALL).strip().rstrip(';')
    data = json.loads(raw)
    glosses = {}
    for key, entry in data.items():
        normalized = normalize_strongs(key)
        gloss = entry.get("kjv_def", entry.get("strongs_def", "")).split(',')[0].strip()
        glosses[normalized] = gloss
    print(f"    Loaded {len(glosses)} Strong's entries")
    return glosses


def fetch_book(slug: str, osis_id: str, glosses: dict) -> dict:
    """Download and parse one OSHB XML book."""
    url = f"{OSHB_BASE}/{osis_id}.xml"
    with urllib.request.urlopen(url) as resp:
        xml_bytes = resp.read()

    root = ET.fromstring(xml_bytes)

    # OSHB uses a default namespace; find all verse elements
    # osisID format: "Gen.1.1"
    chapters = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'verse':
            osisID = elem.get('osisID', '')
            parts = osisID.split('.')
            if len(parts) < 3:
                continue
            ch_num = int(parts[1])
            v_num = int(parts[2])
            words = []
            for child in elem:
                ctag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if ctag == 'w' and child.text:
                    words.append(parse_word_element(child, glosses))
            chapters.setdefault(ch_num, []).append({
                "verse": v_num,
                "words": words,
            })

    return {
        "book": SLUG_TO_DISPLAY[slug],
        "slug": slug,
        "chapters": [
            {"chapter": ch, "verses": verses}
            for ch, verses in sorted(chapters.items())
        ],
    }


def fetch_interlinear(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    glosses = fetch_strongs_glosses()

    for slug, osis_id in OT_BOOKS:
        print(f"  Fetching interlinear {slug}...")
        try:
            book_data = fetch_book(slug, osis_id, glosses)
            (out / f'{slug}.json').write_text(
                json.dumps(book_data, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            total_words = sum(
                len(v["words"])
                for ch in book_data["chapters"]
                for v in ch["verses"]
            )
            print(f"    OK: {len(book_data['chapters'])} chapters, {total_words} words")
        except Exception as e:
            print(f"    ERROR: {e}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fetch_interlinear.py <output_dir>")
        sys.exit(1)
    fetch_interlinear(sys.argv[1])
```

- [ ] **Step 4: Run tests**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python -m pytest scripts/tests/test_fetch_interlinear.py -v
```
Expected: 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/fetch_interlinear.py scripts/tests/test_fetch_interlinear.py && \
git commit -m "feat: add Hebrew interlinear fetch script"
```

---

## Task 6: Generate All Data Files

**Files:**
- Populates: `data/kjv/`, `data/esv/`, `data/interlinear/`

The ESV source file path is: `/home/ryan/.claude/uploads/f18962da-f9e6-4fc6-af50-037fc802274d/cf4007d3-ESVBible.txt`
Copy it into the project first so it's available locally.

- [ ] **Step 1: Copy ESV source into project**

```bash
cp "/home/ryan/.claude/uploads/f18962da-f9e6-4fc6-af50-037fc802274d/cf4007d3-ESVBible.txt" \
   "/home/ryan/Documents/Shared Work/Projects/ScriptureReading/scripts/ESVBible.txt"
```

Note: `scripts/ESVBible.txt` is in `.gitignore` — do NOT commit this file.

Add to `.gitignore`:
```
scripts/ESVBible.txt
```

- [ ] **Step 2: Run ESV converter**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python scripts/convert_esv.py scripts/ESVBible.txt data/esv/
```
Expected: 39 lines printed, each showing book slug + chapter count + verse count. Spot-check:
- genesis: 50 chapters
- psalms: 150 chapters
- obadiah: 1 chapter

- [ ] **Step 3: Fix any parsing errors**

If chapter counts don't match books.json, inspect the problem book's raw text in the ESV file and adjust the regex in `convert_esv.py`. Common issues:
- Book header not found (check capitalization)
- Chapter marker format differs (check for `N:1` vs other patterns)

Re-run until all 39 books show correct chapter counts.

- [ ] **Step 4: Run KJV fetcher**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python scripts/fetch_kjv.py data/kjv/
```
Expected: 39 lines, each `OK: N chapters`. If a 404 occurs, the GitHub filename mapping is wrong — check `kjv_github_filename()` for that slug.

- [ ] **Step 5: Run interlinear fetcher** (takes several minutes — ~40 network requests + Strong's download)

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python scripts/fetch_interlinear.py data/interlinear/
```
Expected: Strong's loaded, then 39 book lines. Verify Genesis has 50 chapters and Psalms has 150.

- [ ] **Step 6: Verify file counts**

```bash
ls data/kjv/ | wc -l && ls data/esv/ | wc -l && ls data/interlinear/ | wc -l
```
Expected: `39` for each.

- [ ] **Step 7: Quick sanity check — Genesis 1:1 across all three**

```bash
python3 -c "
import json
for d in ['kjv','esv']:
    g = json.load(open(f'data/{d}/genesis.json'))
    print(d.upper(), ':', g['chapters'][0]['verses'][0]['text'][:60])
i = json.load(open('data/interlinear/genesis.json'))
w = i['chapters'][0]['verses'][0]['words']
print('INTERLINEAR:', ' '.join(x['gloss'] for x in w[:4]))
"
```
Expected: KJV and ESV show Genesis 1:1 text. Interlinear shows glosses for first few words.

- [ ] **Step 8: Commit data files**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
git add data/ && \
git commit -m "data: add generated KJV, ESV, and interlinear JSON files"
```

---

## Task 7: HTML Skeleton

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Scripture Study</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div id="app">
    <nav id="sidebar">
      <div id="book-list"></div>
    </nav>

    <div id="main">
      <header id="top-bar">
        <button id="btn-prev" aria-label="Previous chapter">&#8592;</button>
        <div id="chapter-label">
          <span id="book-title"></span>
          <span id="chapter-display"></span>
        </div>
        <button id="btn-next" aria-label="Next chapter">&#8594;</button>
      </header>

      <div id="columns-header">
        <div class="col-label">King James Version</div>
        <div class="col-label">English Standard Version</div>
        <div class="col-label">Hebrew Interlinear</div>
      </div>

      <div id="scroll-container">
        <div id="verse-rows"></div>
      </div>
    </div>
  </div>

  <script type="module" src="js/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Open in browser to confirm it loads without errors**

Open `index.html` in a browser (file:// URL is fine at this stage). DevTools console should show only a 404 for `app.js` — no syntax errors.

- [ ] **Step 3: Commit**

```bash
git add index.html && git commit -m "feat: add HTML skeleton"
```

---

## Task 8: CSS Layout

**Files:**
- Create: `style.css`

- [ ] **Step 1: Create style.css**

```css
:root {
  --sidebar-width: 180px;
  --header-height: 48px;
  --col-label-height: 32px;
  --bg: #1a1a1a;
  --bg-sidebar: #111;
  --bg-header: #222;
  --bg-row-alt: #1e1e1e;
  --text: #e8e8e0;
  --text-muted: #888;
  --accent: #7a9fcb;
  --verse-num-color: #5a7fa0;
  --border: #333;
  --hebrew-color: #d4c5a0;
  --strongs-color: #888;
  --gloss-color: #bbb;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: Georgia, 'Times New Roman', serif;
  height: 100vh;
  overflow: hidden;
}

#app {
  display: flex;
  height: 100vh;
}

/* ── Sidebar ── */
#sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 8px 0;
  padding-top: calc(var(--header-height) + var(--col-label-height) + 8px);
}

.category-label {
  font-size: 10px;
  font-family: sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  padding: 12px 12px 4px;
}

.book-item {
  display: block;
  padding: 5px 12px;
  font-size: 13px;
  cursor: pointer;
  color: var(--text);
  border-left: 3px solid transparent;
  transition: background 0.1s;
}

.book-item:hover { background: #1f1f1f; }
.book-item.active {
  color: var(--accent);
  border-left-color: var(--accent);
  background: #1f2a36;
}

/* ── Main area ── */
#main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

/* ── Fixed header ── */
#top-bar {
  height: var(--header-height);
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 10;
  flex-shrink: 0;
}

#top-bar button {
  background: none;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 4px 10px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
}
#top-bar button:hover { background: #333; }
#top-bar button:disabled { opacity: 0.3; cursor: default; }

#chapter-label {
  flex: 1;
  font-family: sans-serif;
  font-size: 14px;
  text-align: center;
}

#book-title { font-weight: 600; margin-right: 8px; }
#chapter-display { color: var(--text-muted); }

/* ── Column labels ── */
#columns-header {
  display: flex;
  height: var(--col-label-height);
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.col-label {
  flex: 1;
  font-family: sans-serif;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-right: 1px solid var(--border);
}
.col-label:last-child { border-right: none; flex: 1.4; }

/* ── Scroll container ── */
#scroll-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* ── Verse rows ── */
.verse-row {
  display: flex;
  border-bottom: 1px solid var(--border);
}
.verse-row:nth-child(even) { background: var(--bg-row-alt); }

.col-kjv, .col-esv {
  flex: 1;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.7;
  border-right: 1px solid var(--border);
}

.col-interlinear {
  flex: 1.4;
  padding: 10px 12px;
  display: flex;
  flex-wrap: wrap;
  align-content: flex-start;
  gap: 6px 8px;
}

.verse-num {
  font-size: 10px;
  font-family: sans-serif;
  color: var(--verse-num-color);
  font-weight: 600;
  margin-right: 4px;
  vertical-align: super;
}

/* ── Interlinear word blocks ── */
.word-block {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 4px 6px;
  border: 1px solid #2a2a2a;
  border-radius: 4px;
  min-width: 40px;
  background: #161616;
}

.word-hebrew {
  font-size: 18px;
  color: var(--hebrew-color);
  font-family: 'SBL Hebrew', 'Ezra SIL', 'Cardo', serif;
  direction: rtl;
  line-height: 1.4;
}

.word-strongs {
  font-size: 9px;
  font-family: sans-serif;
  color: var(--strongs-color);
  margin-top: 1px;
}

.word-gloss {
  font-size: 11px;
  color: var(--gloss-color);
  font-family: sans-serif;
  text-align: center;
  margin-top: 2px;
  font-style: italic;
}

/* ── Loading state ── */
#verse-rows:empty::after {
  content: 'Select a book to begin.';
  display: block;
  padding: 40px;
  color: var(--text-muted);
  font-family: sans-serif;
  font-size: 14px;
  text-align: center;
}
```

- [ ] **Step 2: Reload in browser**

Hard-refresh. The app layout should show: dark sidebar on left, header bar at top, three column labels beneath the header. No content yet (just the "Select a book" placeholder). No console errors.

- [ ] **Step 3: Commit**

```bash
git add style.css && git commit -m "feat: add 4-column CSS layout"
```

---

## Task 9: Sidebar Component

**Files:**
- Create: `js/sidebar.js`

- [ ] **Step 1: Create sidebar.js**

```js
// js/sidebar.js
const CATEGORIES = ['Law', 'History', 'Poetry', 'Major Prophets', 'Minor Prophets'];

export function initSidebar(books, onSelect) {
  const container = document.getElementById('book-list');

  const byCategory = {};
  for (const book of books) {
    (byCategory[book.category] ||= []).push(book);
  }

  for (const cat of CATEGORIES) {
    const catBooks = byCategory[cat] || [];
    if (!catBooks.length) continue;

    const label = document.createElement('div');
    label.className = 'category-label';
    label.textContent = cat;
    container.appendChild(label);

    for (const book of catBooks) {
      const item = document.createElement('div');
      item.className = 'book-item';
      item.textContent = book.name;
      item.dataset.slug = book.slug;
      item.addEventListener('click', () => onSelect(book.slug));
      container.appendChild(item);
    }
  }
}

export function setSidebarActive(slug) {
  document.querySelectorAll('.book-item').forEach(el => {
    el.classList.toggle('active', el.dataset.slug === slug);
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add js/sidebar.js && git commit -m "feat: add sidebar book list component"
```

---

## Task 10: Header Component

**Files:**
- Create: `js/header.js`

- [ ] **Step 1: Create header.js**

```js
// js/header.js
export function initHeader(onPrev, onNext) {
  document.getElementById('btn-prev').addEventListener('click', onPrev);
  document.getElementById('btn-next').addEventListener('click', onNext);
}

export function updateHeader(bookName, chapter, totalChapters) {
  document.getElementById('book-title').textContent = bookName;
  document.getElementById('chapter-display').textContent =
    `Chapter ${chapter} of ${totalChapters}`;
  document.getElementById('btn-prev').disabled = chapter <= 1;
  document.getElementById('btn-next').disabled = chapter >= totalChapters;
}
```

- [ ] **Step 2: Commit**

```bash
git add js/header.js && git commit -m "feat: add header chapter navigation component"
```

---

## Task 11: Prose Column Renderer (KJV + ESV)

**Files:**
- Create: `js/prose-renderer.js`

- [ ] **Step 1: Create prose-renderer.js**

```js
// js/prose-renderer.js

/**
 * Render a single prose translation column's verse cell.
 * @param {number} verseNum
 * @param {string} text
 * @returns {HTMLElement}
 */
export function buildProseCell(verseNum, text, cssClass) {
  const cell = document.createElement('div');
  cell.className = cssClass;

  const num = document.createElement('sup');
  num.className = 'verse-num';
  num.textContent = verseNum;

  const content = document.createTextNode(text);

  cell.appendChild(num);
  cell.appendChild(content);
  return cell;
}
```

- [ ] **Step 2: Commit**

```bash
git add js/prose-renderer.js && git commit -m "feat: add prose column renderer"
```

---

## Task 12: Interlinear Column Renderer

**Files:**
- Create: `js/interlinear-renderer.js`

- [ ] **Step 1: Create interlinear-renderer.js**

```js
// js/interlinear-renderer.js

/**
 * Build a single Hebrew word block element.
 * @param {{ hebrew: string, strongs: string, gloss: string }} word
 * @returns {HTMLElement}
 */
function buildWordBlock(word) {
  const block = document.createElement('div');
  block.className = 'word-block';

  const heb = document.createElement('span');
  heb.className = 'word-hebrew';
  heb.textContent = word.hebrew;

  const strongs = document.createElement('span');
  strongs.className = 'word-strongs';
  strongs.textContent = word.strongs;

  const gloss = document.createElement('span');
  gloss.className = 'word-gloss';
  gloss.textContent = word.gloss;

  block.appendChild(heb);
  block.appendChild(strongs);
  block.appendChild(gloss);
  return block;
}

/**
 * Build the interlinear column cell for one verse.
 * @param {number} verseNum
 * @param {{ hebrew: string, strongs: string, gloss: string }[]} words
 * @returns {HTMLElement}
 */
export function buildInterlinearCell(verseNum, words) {
  const cell = document.createElement('div');
  cell.className = 'col-interlinear';

  const num = document.createElement('sup');
  num.className = 'verse-num';
  num.textContent = verseNum;
  cell.appendChild(num);

  for (const word of words) {
    if (word.hebrew && word.hebrew.trim()) {
      cell.appendChild(buildWordBlock(word));
    }
  }
  return cell;
}
```

- [ ] **Step 2: Commit**

```bash
git add js/interlinear-renderer.js && git commit -m "feat: add interlinear Hebrew word-block renderer"
```

---

## Task 13: App.js — State Management and Wiring

**Files:**
- Create: `js/app.js`

- [ ] **Step 1: Create app.js**

```js
// js/app.js
import { initSidebar, setSidebarActive } from './sidebar.js';
import { initHeader, updateHeader } from './header.js';
import { buildProseCell } from './prose-renderer.js';
import { buildInterlinearCell } from './interlinear-renderer.js';

const state = {
  books: [],
  currentSlug: null,
  currentChapter: 1,
};

async function loadJSON(path) {
  const resp = await fetch(path);
  if (!resp.ok) throw new Error(`Failed to load ${path}: ${resp.status}`);
  return resp.json();
}

function getBook() {
  return state.books.find(b => b.slug === state.currentSlug);
}

async function renderChapter() {
  const book = getBook();
  if (!book) return;

  const [kjvData, esvData, ilData] = await Promise.all([
    loadJSON(`data/kjv/${book.slug}.json`),
    loadJSON(`data/esv/${book.slug}.json`),
    loadJSON(`data/interlinear/${book.slug}.json`),
  ]);

  const ch = state.currentChapter - 1; // 0-indexed
  const kjvVerses = kjvData.chapters[ch]?.verses || [];
  const esvVerses = esvData.chapters[ch]?.verses || [];
  const ilVerses  = ilData.chapters[ch]?.verses  || [];

  const maxVerses = Math.max(kjvVerses.length, esvVerses.length, ilVerses.length);

  const container = document.getElementById('verse-rows');
  container.innerHTML = '';

  for (let i = 0; i < maxVerses; i++) {
    const kjvV = kjvVerses[i];
    const esvV = esvVerses[i];
    const ilV  = ilVerses[i];
    const verseNum = (kjvV || esvV || ilV).verse;

    const row = document.createElement('div');
    row.className = 'verse-row';
    row.dataset.verse = verseNum;

    row.appendChild(buildProseCell(verseNum, kjvV?.text ?? '', 'col-kjv'));
    row.appendChild(buildProseCell(verseNum, esvV?.text ?? '', 'col-esv'));
    row.appendChild(buildInterlinearCell(verseNum, ilV?.words ?? []));

    container.appendChild(row);
  }

  updateHeader(book.name, state.currentChapter, book.chapters);
  setSidebarActive(book.slug);

  // Sync URL hash for bookmarking
  history.replaceState(null, '', `#${book.slug}/${state.currentChapter}`);

  // Scroll to top of content
  document.getElementById('scroll-container').scrollTop = 0;
}

function selectBook(slug, chapter = 1) {
  state.currentSlug = slug;
  state.currentChapter = chapter;
  renderChapter();
}

function prevChapter() {
  if (state.currentChapter > 1) {
    state.currentChapter--;
    renderChapter();
  }
}

function nextChapter() {
  const book = getBook();
  if (book && state.currentChapter < book.chapters) {
    state.currentChapter++;
    renderChapter();
  }
}

async function init() {
  state.books = await loadJSON('data/books.json');

  initSidebar(state.books, slug => selectBook(slug, 1));
  initHeader(prevChapter, nextChapter);

  // Restore from URL hash if present
  const hash = window.location.hash.slice(1); // e.g. "genesis/3"
  if (hash) {
    const [slug, chStr] = hash.split('/');
    const ch = parseInt(chStr, 10) || 1;
    const book = state.books.find(b => b.slug === slug);
    if (book) {
      selectBook(slug, ch);
      return;
    }
  }

  // Default: open Genesis chapter 1
  selectBook('genesis', 1);
}

init();
```

- [ ] **Step 2: Serve the site locally and test**

A static file server is needed because ES modules require HTTP (not file://). Run:

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
python3 -m http.server 8080
```

Open `http://localhost:8080` in a browser.

Expected behavior:
- Genesis chapter 1 loads automatically
- All three columns show verse content, rows aligned
- Prev button is disabled (chapter 1)
- Clicking a book in the sidebar loads that book
- Prev/Next arrows navigate chapters
- URL hash updates on navigation (e.g. `#genesis/1`)
- Refresh restores the same book/chapter

- [ ] **Step 3: Check console for errors**

DevTools console should be clean. Common issues:
- 404 on a data file → check the slug mapping in scripts matches the file names
- Blank interlinear column → OSHB parsing issue, check interlinear JSON manually

- [ ] **Step 4: Commit**

```bash
git add js/app.js && git commit -m "feat: wire up app state, rendering, and navigation"
```

---

## Task 14: stitch.md — Google Stitch UI Prompt

**Files:**
- Create: `stitch.md`

- [ ] **Step 1: Create stitch.md**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add stitch.md && git commit -m "docs: add Google Stitch UI prompt"
```

---

## Task 15: Cloudflare Pages Deployment

**Files:**
- No code changes needed — the site is already static

- [ ] **Step 1: Create a GitHub repository**

Go to github.com, create a new repository named `scripture-reading` (private). Copy the remote URL.

- [ ] **Step 2: Push to GitHub**

```bash
cd "/home/ryan/Documents/Shared Work/Projects/ScriptureReading" && \
git remote add origin <YOUR_GITHUB_REPO_URL> && \
git push -u origin main
```

- [ ] **Step 3: Connect to Cloudflare Pages**

1. Go to dash.cloudflare.com → Pages → Create a project
2. Connect to Git → select the `scripture-reading` repository
3. Build settings:
   - Build command: *(leave empty)*
   - Build output directory: `/` (the root)
4. Click Save and Deploy

- [ ] **Step 4: Verify deployment**

Cloudflare will provide a URL like `scripture-reading-xxx.pages.dev`. Open it. Verify:
- Genesis chapter 1 loads
- All three columns render
- Navigation works
- URL hash updates

- [ ] **Step 5: Note the Tailscale access**

The Cloudflare Pages URL is publicly accessible by default. If you want to restrict it to Tailscale only, use Cloudflare Access (under Zero Trust) to add an email-based policy. Otherwise the public URL works fine for personal use.

---

## Self-Review Checklist

- [x] **Spec coverage:**
  - 4-column layout (sidebar + KJV + ESV + interlinear) ✓ Tasks 7, 8
  - Verse-row grid with auto height sync ✓ Task 13 (flex rows)
  - Synchronized scrolling ✓ Task 13 (single scroll container)
  - Book navigation with category grouping ✓ Task 9
  - Chapter prev/next navigation ✓ Task 10, 13
  - URL hash bookmarking ✓ Task 13
  - Hebrew word blocks (Hebrew + Strong's + gloss) ✓ Task 12
  - Data bundled on Cloudflare ✓ Task 6, 15
  - ESV from .txt file ✓ Task 3, 6
  - KJV from GitHub ✓ Task 4, 6
  - Interlinear from OSHB ✓ Task 5, 6
  - stitch.md ✓ Task 14
  - Cloudflare Pages deployment ✓ Task 15

- [x] **No placeholders** — all steps contain actual code or exact commands
- [x] **Type consistency** — `buildProseCell`, `buildInterlinearCell`, `initSidebar`, `setSidebarActive`, `initHeader`, `updateHeader` are consistent across Tasks 9–13
- [x] **Slug consistency** — `books.json` slugs, Python script output filenames, and JS `loadJSON` paths all use the same slug format (e.g. `1-samuel`, `song-of-solomon`)
