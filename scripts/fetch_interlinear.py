# scripts/fetch_interlinear.py
"""Download OSHB Hebrew interlinear XML + English glosses from vektor8891/interlinear-bible."""
import json
import re
import sqlite3
import sys
import tempfile
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

# Our slugs use hyphens; vektor8891 uses underscores (and "songs" for Song of Solomon)
SLUG_TO_VEKTOR = {slug: slug.replace('-', '_') for slug, _ in OT_BOOKS}
SLUG_TO_VEKTOR["song-of-solomon"] = "songs"

OSHB_BASE = "https://raw.githubusercontent.com/openscriptures/morphhb/master/wlc"
VEKTOR_DB_URL = "https://github.com/vektor8891/interlinear-bible/raw/master/data/bible.db"


def normalize_strongs(number_str: str) -> str:
    n = number_str.lstrip('0') or '0'
    return f"H{n}"


def extract_first_strongs(lemma: str) -> str | None:
    if not lemma:
        return None
    last = lemma.split('/')[-1]
    m = re.match(r'^(\d+)', last.strip())
    if not m:
        return None
    return normalize_strongs(m.group(1))


def fetch_vektor_glosses(db_path: str) -> tuple[dict, dict]:
    """Load English translations from vektor8891 interlinear DB.

    Returns:
        positional: {(vektor_book, chapter_int, verse_int, word_order_int): word_eng}
        strongs:    {H1234: definition}  — fallback when positional lookup misses
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Positional: word_eng per book/chapter/verse/position
    c.execute('''
        SELECT ch.book, ch.chapter, i.verse, i.word_order, i.word_eng
        FROM interlinear i
        JOIN chapters ch ON i.chapter_ind = ch.ind
    ''')
    positional = {}
    for book, chapter, verse, word_order, word_eng in c.fetchall():
        try:
            key = (book, int(chapter), int(verse), int(word_order))
            positional[key] = word_eng or ""
        except (ValueError, TypeError):
            pass

    # Strongs fallback: definition per Strong's number
    c.execute('SELECT strong_id, definition FROM words')
    strongs = {}
    for strong_id, definition in c.fetchall():
        n = strong_id[1:].lstrip('0') or '0'
        strongs[f"H{n}"] = definition or ""

    conn.close()
    print(f"    Loaded {len(positional)} positional translations, {len(strongs)} Strong's entries")
    return positional, strongs


def parse_word_element(elem, word_order: int, vektor_book: str, chapter: int, verse: int,
                       positional: dict, strongs: dict) -> dict:
    lemma = elem.get("lemma", "")
    strongs_id = extract_first_strongs(lemma) or ""
    gloss = positional.get((vektor_book, chapter, verse, word_order), None)
    if gloss is None:
        gloss = strongs.get(strongs_id, "")
    return {
        "hebrew": elem.text or "",
        "strongs": strongs_id,
        "gloss": gloss,
    }


def fetch_book(slug: str, osis_id: str, positional: dict, strongs: dict) -> dict:
    url = f"{OSHB_BASE}/{osis_id}.xml"
    with urllib.request.urlopen(url) as resp:
        xml_bytes = resp.read()

    root = ET.fromstring(xml_bytes)
    vektor_book = SLUG_TO_VEKTOR[slug]

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
            word_order = 1
            for child in elem:
                ctag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                if ctag == 'w' and child.text:
                    words.append(parse_word_element(
                        child, word_order, vektor_book, ch_num, v_num, positional, strongs
                    ))
                    word_order += 1
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

    print("  Downloading vektor8891/interlinear-bible DB...")
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    urllib.request.urlretrieve(VEKTOR_DB_URL, db_path)

    positional, strongs = fetch_vektor_glosses(db_path)

    for slug, osis_id in OT_BOOKS:
        print(f"  Fetching interlinear {slug}...")
        try:
            book_data = fetch_book(slug, osis_id, positional, strongs)
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

    Path(db_path).unlink(missing_ok=True)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python fetch_interlinear.py <output_dir>")
        sys.exit(1)
    fetch_interlinear(sys.argv[1])
