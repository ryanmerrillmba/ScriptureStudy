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
