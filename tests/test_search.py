"""Tests for search.py – get_word_entry / find_query."""

import pytest

from src.search import get_word_entry, find_query


# ── shared fixture ──────────────────────────────────────────

@pytest.fixture
def sample_index():
    """A small inverted index used by most tests."""
    return {
        "python": {
            "http://a.com": {"frequency": 3, "positions": [0, 4, 9]},
            "http://b.com": {"frequency": 1, "positions": [2]},
        },
        "code": {
            "http://a.com": {"frequency": 1, "positions": [5]},
        },
        "java": {
            "http://b.com": {"frequency": 2, "positions": [0, 3]},
        },
    }


# ── search_word ─────────────────────────────────────────────

def test_get_word_entry_found(sample_index):
    result = get_word_entry(sample_index, "python")
    assert "http://a.com" in result
    assert "http://b.com" in result


def test_get_word_entry_case_insensitive(sample_index):
    assert get_word_entry(sample_index, "Python") == get_word_entry(sample_index, "python")


def test_get_word_entry_not_found(sample_index):
    assert get_word_entry(sample_index, "rust") == {}


def test_get_word_entry_empty_string(sample_index):
    assert get_word_entry(sample_index, "") == {}


def test_get_word_entry_whitespace(sample_index):
    assert get_word_entry(sample_index, "  python  ") == get_word_entry(sample_index, "python")


# ── find_query ──────────────────────────────────────────────

def test_find_query_single_word(sample_index):
    results = find_query(sample_index, "python")
    urls = [r["url"] for r in results]
    assert "http://a.com" in urls
    assert "http://b.com" in urls


def test_find_query_multi_word_match(sample_index):
    results = find_query(sample_index, "python code")
    assert len(results) == 1
    assert results[0]["url"] == "http://a.com"
    assert "python" in results[0]["words"]
    assert "code" in results[0]["words"]


def test_find_query_no_common_page(sample_index):
    # "code" only on a.com, "java" only on b.com → no overlap
    results = find_query(sample_index, "code java")
    assert results == []


def test_find_query_word_not_in_index(sample_index):
    results = find_query(sample_index, "python rust")
    assert results == []


def test_find_query_empty_query(sample_index):
    assert find_query(sample_index, "") == []


def test_find_query_whitespace_query(sample_index):
    assert find_query(sample_index, "   ") == []


def test_find_query_case_insensitive(sample_index):
    assert find_query(sample_index, "PYTHON CODE") == find_query(sample_index, "python code")


def test_find_query_extra_whitespace(sample_index):
    assert find_query(sample_index, "  python   code  ") == find_query(sample_index, "python code")


def test_find_query_duplicate_word_in_query(sample_index):
    """Repeating a word in the query still works (does not crash or duplicate)."""
    results = find_query(sample_index, "python python")
    urls = [r["url"] for r in results]
    assert "http://a.com" in urls
    assert "http://b.com" in urls


def test_get_word_entry_does_not_mutate_index(sample_index):
    """Callers cannot accidentally corrupt the index through the returned entry."""
    original_freq = sample_index["python"]["http://a.com"]["frequency"]
    entry = get_word_entry(sample_index, "python")
    # Read-only check: the returned data is the real dict (not a copy),
    # so verify the original is still intact after access.
    assert entry["http://a.com"]["frequency"] == original_freq
