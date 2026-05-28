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

NT_BOOKS = [
    ("MATTHEW", "matthew"), ("MARK", "mark"), ("LUKE", "luke"), ("JOHN", "john"),
    ("ACTS", "acts"), ("ROMANS", "romans"),
    ("1 CORINTHIANS", "1-corinthians"), ("2 CORINTHIANS", "2-corinthians"),
    ("GALATIANS", "galatians"), ("EPHESIANS", "ephesians"),
    ("PHILIPPIANS", "philippians"), ("COLOSSIANS", "colossians"),
    ("1 THESSALONIANS", "1-thessalonians"), ("2 THESSALONIANS", "2-thessalonians"),
    ("1 TIMOTHY", "1-timothy"), ("2 TIMOTHY", "2-timothy"),
    ("TITUS", "titus"), ("PHILEMON", "philemon"), ("HEBREWS", "hebrews"),
    ("JAMES", "james"), ("1 PETER", "1-peter"), ("2 PETER", "2-peter"),
    ("1 JOHN", "1-john"), ("2 JOHN", "2-john"), ("3 JOHN", "3-john"),
    ("JUDE", "jude"), ("REVELATION", "revelation"),
]

ALL_BOOKS = OT_BOOKS + NT_BOOKS

BOOK_NAME_TO_SLUG = {name: slug for name, slug in ALL_BOOKS}
DISPLAY_NAME = {name: name.title().replace("Of", "of") for name, _ in ALL_BOOKS}
DISPLAY_NAME["SONG OF SOLOMON"] = "Song of Solomon"
DISPLAY_NAME["1 SAMUEL"] = "1 Samuel"
DISPLAY_NAME["2 SAMUEL"] = "2 Samuel"
DISPLAY_NAME["1 KINGS"] = "1 Kings"
DISPLAY_NAME["2 KINGS"] = "2 Kings"
DISPLAY_NAME["1 CHRONICLES"] = "1 Chronicles"
DISPLAY_NAME["2 CHRONICLES"] = "2 Chronicles"
DISPLAY_NAME["1 CORINTHIANS"] = "1 Corinthians"
DISPLAY_NAME["2 CORINTHIANS"] = "2 Corinthians"
DISPLAY_NAME["1 THESSALONIANS"] = "1 Thessalonians"
DISPLAY_NAME["2 THESSALONIANS"] = "2 Thessalonians"
DISPLAY_NAME["1 TIMOTHY"] = "1 Timothy"
DISPLAY_NAME["2 TIMOTHY"] = "2 Timothy"
DISPLAY_NAME["1 PETER"] = "1 Peter"
DISPLAY_NAME["2 PETER"] = "2 Peter"
DISPLAY_NAME["1 JOHN"] = "1 John"
DISPLAY_NAME["2 JOHN"] = "2 John"
DISPLAY_NAME["3 JOHN"] = "3 John"


def clean_text(text: str) -> str:
    """Remove footnote lines, inline markers, and normalize whitespace."""
    # Remove entire footnote reference lines (e.g. "[1] 1:6 Or a canopy...")
    # These must be stripped before whitespace collapsing so they don't bleed
    # into surrounding verse text as spurious chapter:verse markers.
    text = re.sub(r'(?m)^\[\d+\][^\n]*\n?', '', text)
    # Remove wrapped footnote continuation lines (e.g. "30; 2:1" or "28, 30; 2:1")
    # These contain only digits, spaces, commas, semicolons, and colons — no letters.
    text = re.sub(r'(?m)^[0-9 ,;:]+$\n?', '', text)
    # Remove any remaining inline footnote markers (e.g. word[2])
    text = re.sub(r'\[\d+\]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def _parse_verses(chapter_text: str, start_verse: int = 1) -> list:
    """Parse inline verse numbers out of a chapter's text block."""
    # Match inline verse numbers: a bare integer immediately followed by a letter
    # or opening quote (no space). Lowercase included — many verses start lowercase
    # e.g. “3your anointing oils are fragrant”.
    verse_split = re.compile(r'(?<=\s)(\d+)(?=[A-Za-z"\u201c\u2018\u2019\'])')
    verse_splits = list(verse_split.finditer(chapter_text))

    verses = []
    v1_end = verse_splits[0].start() if verse_splits else len(chapter_text)
    v1_text = chapter_text[:v1_end].strip()
    if v1_text:
        verses.append({"verse": start_verse, "text": v1_text})

    for j, vs in enumerate(verse_splits):
        verse_num = int(vs.group(1))
        vs_start = vs.end()
        vs_end = verse_splits[j + 1].start() if j + 1 < len(verse_splits) else len(chapter_text)
        verse_text = chapter_text[vs_start:vs_end].strip()
        if verse_text:
            verses.append({"verse": verse_num, "text": verse_text})

    return verses


def parse_book_content(book_name: str, content: str) -> dict:
    """Parse a single book's raw text into the shared JSON schema."""
    content = clean_text(content)

    # Split on chapter:verse markers (e.g. "1:1 " or "2:1 ")
    # These always mark verse 1 of a new chapter.
    chapter_pattern = re.compile(r'(\d+):1\s')
    chapter_splits = list(chapter_pattern.finditer(content))

    if not chapter_splits:
        # Single-chapter book with bare inline verse numbers only (e.g. Obadiah).
        # Treat the entire content as chapter 1.
        chapters = [{"chapter": 1, "verses": _parse_verses(content, start_verse=1)}]
    else:
        chapters = []
        for i, match in enumerate(chapter_splits):
            chapter_num = int(match.group(1))
            text_start = match.end()
            text_end = chapter_splits[i + 1].start() if i + 1 < len(chapter_splits) else len(content)
            chapter_text = content[text_start:text_end].strip()
            chapters.append({"chapter": chapter_num, "verses": _parse_verses(chapter_text)})

    slug = BOOK_NAME_TO_SLUG.get(book_name.upper(), book_name.lower())
    display = DISPLAY_NAME.get(book_name.upper(), book_name.title())
    return {"book": display, "slug": slug, "chapters": chapters}


def parse_esv(source_path: str, output_dir: str) -> None:
    text = Path(source_path).read_text(encoding='utf-8')

    # Find the last occurrence of each book header (ALL CAPS on its own line).
    # The last occurrence is the actual content section, not the ToC entry.
    book_positions = {}
    for book_name, _ in ALL_BOOKS:
        pattern = re.compile(rf'(?m)^\s*{re.escape(book_name)}\s*$')
        matches = list(pattern.finditer(text))
        if matches:
            book_positions[book_name] = matches[-1].end()

    sorted_books = sorted(book_positions.items(), key=lambda x: x[1])
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for i, (book_name, start) in enumerate(sorted_books):
        end = sorted_books[i + 1][1] if i + 1 < len(sorted_books) else len(text)
        book_content = text[start:end]
        # Truncate at the footnote block before any text processing.
        footnote_block = re.search(r'\n\[1\] ', book_content)
        if footnote_block:
            book_content = book_content[:footnote_block.start()]
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
