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
