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
