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

NT_SLUGS = [
    "matthew", "mark", "luke", "john", "acts",
    "romans", "1-corinthians", "2-corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1-thessalonians", "2-thessalonians",
    "1-timothy", "2-timothy", "titus", "philemon", "hebrews",
    "james", "1-peter", "2-peter", "1-john", "2-john", "3-john",
    "jude", "revelation",
]

ALL_SLUGS = OT_SLUGS + NT_SLUGS

BASE_URL = "https://raw.githubusercontent.com/aruljohn/Bible-kjv/master"


def kjv_github_filename(slug: str) -> str:
    """Convert our slug to the GitHub repo's filename convention."""
    parts = slug.split('-')
    # Title-case each part, but keep short prepositions like "of" lowercase
    return ''.join(p if p == 'of' else p.title() for p in parts)


def transform_book(raw: dict, slug: str) -> dict:
    """Add slug field and normalize chapter/verse to int (raw data uses strings)."""
    return {
        "book": raw["book"],
        "slug": slug,
        "chapters": [
            {
                "chapter": int(ch["chapter"]),
                "verses": [
                    {"verse": int(v["verse"]), "text": v["text"]}
                    for v in ch["verses"]
                ],
            }
            for ch in raw["chapters"]
        ],
    }


def fetch_kjv(output_dir: str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    for slug in ALL_SLUGS:
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
