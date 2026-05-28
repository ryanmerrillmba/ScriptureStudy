# scripts/fetch_greek_interlinear.py
"""Download MorphGNT SBLGNT Greek NT + English glosses from vektor8891/interlinear-bible."""
import json
import re
import sqlite3
import sys
import tempfile
import urllib.request
from pathlib import Path

MORPHGNT_BASE = "https://raw.githubusercontent.com/morphgnt/sblgnt/master"
VEKTOR_DB_URL = "https://github.com/vektor8891/interlinear-bible/raw/master/data/bible.db"

# (slug, display_name, morphgnt_file, nt_book_num, vektor_book)
NT_BOOKS = [
    ("matthew",         "Matthew",         "61-Mt",  1,  "matthew"),
    ("mark",            "Mark",            "62-Mk",  2,  "mark"),
    ("luke",            "Luke",            "63-Lk",  3,  "luke"),
    ("john",            "John",            "64-Jn",  4,  "john"),
    ("acts",            "Acts",            "65-Ac",  5,  "acts"),
    ("romans",          "Romans",          "66-Ro",  6,  "romans"),
    ("1-corinthians",   "1 Corinthians",   "67-1Co", 7,  "1_corinthians"),
    ("2-corinthians",   "2 Corinthians",   "68-2Co", 8,  "2_corinthians"),
    ("galatians",       "Galatians",       "69-Ga",  9,  "galatians"),
    ("ephesians",       "Ephesians",       "70-Eph", 10, "ephesians"),
    ("philippians",     "Philippians",     "71-Php", 11, "philippians"),
    ("colossians",      "Colossians",      "72-Col", 12, "colossians"),
    ("1-thessalonians", "1 Thessalonians", "73-1Th", 13, "1_thessalonians"),
    ("2-thessalonians", "2 Thessalonians", "74-2Th", 14, "2_thessalonians"),
    ("1-timothy",       "1 Timothy",       "75-1Ti", 15, "1_timothy"),
    ("2-timothy",       "2 Timothy",       "76-2Ti", 16, "2_timothy"),
    ("titus",           "Titus",           "77-Tit", 17, "titus"),
    ("philemon",        "Philemon",        "78-Phm", 18, "philemon"),
    ("hebrews",         "Hebrews",         "79-Heb", 19, "hebrews"),
    ("james",           "James",           "80-Jas", 20, "james"),
    ("1-peter",         "1 Peter",         "81-1Pe", 21, "1_peter"),
    ("2-peter",         "2 Peter",         "82-2Pe", 22, "2_peter"),
    ("1-john",          "1 John",          "83-1Jn", 23, "1_john"),
    ("2-john",          "2 John",          "84-2Jn", 24, "2_john"),
    ("3-john",          "3 John",          "85-3Jn", 25, "3_john"),
    ("jude",            "Jude",            "86-Jud", 26, "jude"),
    ("revelation",      "Revelation",      "87-Re",  27, "revelation"),
]


def fetch_vektor_glosses_nt(db_path: str) -> tuple[dict, dict]:
    """Load NT English translations from vektor8891 DB.

    Returns:
        positional: {(vektor_book, chapter_int, verse_int, word_order_int): word_eng}
        strongs:    {G1234: definition}
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute('''
        SELECT ch.book, ch.chapter, i.verse, i.word_order, i.word_eng
        FROM interlinear i
        JOIN chapters ch ON i.chapter_ind = ch.ind
        WHERE ch.book NOT IN (
            'genesis','exodus','leviticus','numbers','deuteronomy','joshua',
            'judges','ruth','1_samuel','2_samuel','1_kings','2_kings',
            '1_chronicles','2_chronicles','ezra','nehemiah','esther','job',
            'psalms','proverbs','ecclesiastes','songs','isaiah','jeremiah',
            'lamentations','ezekiel','daniel','hosea','joel','amos','obadiah',
            'jonah','micah','nahum','habakkuk','zephaniah','haggai','zechariah','malachi'
        )
    ''')
    positional = {}
    for book, chapter, verse, word_order, word_eng in c.fetchall():
        try:
            key = (book, int(chapter), int(verse), int(word_order))
            positional[key] = word_eng or ""
        except (ValueError, TypeError):
            pass

    c.execute('SELECT strong_id, definition FROM words')
    strongs = {}
    for strong_id, definition in c.fetchall():
        n = strong_id[1:].lstrip('0') or '0'
        strongs[f"{strong_id[0]}{n}"] = definition or ""

    conn.close()
    print(f"    Loaded {len(positional)} NT positional translations, {len(strongs)} Strong's entries")
    return positional, strongs


def parse_morphgnt(raw_text: str, book_num: int, vektor_book: str,
                   positional: dict, strongs: dict) -> dict:
    """Parse a MorphGNT file into our chapter/verse/word structure.

    MorphGNT line format (8 space-separated fields):
      BBCCVV  POS  Parsing  cited-form  word-form  normalized  lemma
    We use the word-form (col 5, 0-indexed col 4) for display — clean, no punctuation.
    """
    prefix = f"{book_num:02d}"
    chapters: dict[int, dict[int, list]] = {}

    verse_word_order: dict[tuple, int] = {}

    for line in raw_text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        bcv = parts[0]
        if not bcv.startswith(prefix):
            continue

        ch_num = int(bcv[2:4])
        v_num  = int(bcv[4:6])
        word_form = parts[4]  # clean word, no trailing punctuation

        vkey = (ch_num, v_num)
        verse_word_order[vkey] = verse_word_order.get(vkey, 0) + 1
        word_order = verse_word_order[vkey]

        gloss = positional.get((vektor_book, ch_num, v_num, word_order), None)
        if gloss is None:
            gloss = ""

        chapters.setdefault(ch_num, {}).setdefault(v_num, []).append({
            "greek": word_form,
            "gloss": gloss,
        })

    return [
        {
            "chapter": ch,
            "verses": [
                {"verse": v, "words": words}
                for v, words in sorted(verses.items())
            ]
        }
        for ch, verses in sorted(chapters.items())
    ]


def fetch_greek(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("  Downloading vektor8891/interlinear-bible DB...")
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    urllib.request.urlretrieve(VEKTOR_DB_URL, db_path)

    positional, strongs = fetch_vektor_glosses_nt(db_path)

    for slug, display, morphgnt_file, book_num, vektor_book in NT_BOOKS:
        url = f"{MORPHGNT_BASE}/{morphgnt_file}-morphgnt.txt"
        print(f"  Fetching Greek {slug}...")
        try:
            with urllib.request.urlopen(url) as resp:
                raw = resp.read().decode('utf-8')
            chapters = parse_morphgnt(raw, book_num, vektor_book, positional, strongs)
            book_data = {"book": display, "slug": slug, "chapters": chapters}
            (out / f'{slug}.json').write_text(
                json.dumps(book_data, ensure_ascii=False, indent=2), encoding='utf-8'
            )
            total_words = sum(len(v["words"]) for ch in chapters for v in ch["verses"])
            print(f"    OK: {len(chapters)} chapters, {total_words} words")
        except Exception as e:
            print(f"    ERROR: {e}")

    Path(db_path).unlink(missing_ok=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fetch_greek_interlinear.py <output_dir>")
        sys.exit(1)
    fetch_greek(sys.argv[1])
