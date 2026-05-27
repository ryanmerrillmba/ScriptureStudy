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
