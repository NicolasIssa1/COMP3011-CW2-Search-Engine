"""
test_indexer.py - Unit tests for the indexer module.

Tests tokenization and inverted index construction, verifying
correct frequency counts, token positions, and case-insensitivity.
"""

import pytest
from src.indexer import tokenize_text, build_inverted_index


# ---------------------------------------------------------------------------
# Fixtures: reusable page data
# ---------------------------------------------------------------------------

@pytest.fixture
def single_page():
    """A single crawled page with a short sentence."""
    return [{"url": "https://example.com/page/1/", "title": "P1",
             "text": "Good friends are hard to find"}]


@pytest.fixture
def two_pages():
    """Two crawled pages with overlapping words."""
    return [
        {"url": "https://example.com/page/1/", "title": "P1",
         "text": "Good friends are hard to find"},
        {"url": "https://example.com/page/2/", "title": "P2",
         "text": "A good book is a good friend"},
    ]


# ---------------------------------------------------------------------------
# Tests for tokenize_text()
# ---------------------------------------------------------------------------

class TestTokenizeText:
    """Tests for the tokenize_text function."""

    def test_lowercases_all_tokens(self):
        """All tokens are converted to lowercase."""
        tokens = tokenize_text("Hello World PYTHON")
        assert tokens == ["hello", "world", "python"]

    def test_strips_punctuation(self):
        """Commas, periods, exclamation marks etc. are removed."""
        tokens = tokenize_text("Hello, world! How are you?")
        assert tokens == ["hello", "world", "how", "are", "you"]

    def test_preserves_contractions(self):
        """Apostrophes inside contractions are kept (e.g. don't, it's)."""
        tokens = tokenize_text("I don't think it's fair")
        assert "don't" in tokens
        assert "it's" in tokens

    def test_handles_numbers(self):
        """Numeric tokens are preserved."""
        tokens = tokenize_text("There are 100 quotes on page 1")
        assert "100" in tokens
        assert "1" in tokens

    def test_empty_string(self):
        """An empty string produces an empty token list."""
        assert tokenize_text("") == []

    def test_whitespace_only(self):
        """A string of only whitespace produces an empty token list."""
        assert tokenize_text("   \n\t  ") == []

    def test_preserves_token_order(self):
        """Tokens appear in the same order as in the original text."""
        tokens = tokenize_text("one two three")
        assert tokens == ["one", "two", "three"]

    def test_mixed_case_same_token(self):
        """Different casings of the same word produce identical tokens."""
        tokens = tokenize_text("Good GOOD good")
        assert tokens == ["good", "good", "good"]

    def test_special_characters_ignored(self):
        """Symbols like @, #, $, etc. are discarded."""
        tokens = tokenize_text("email@test #hashtag $100")
        assert "email" in tokens
        assert "test" in tokens
        assert "hashtag" in tokens
        assert "100" in tokens


# ---------------------------------------------------------------------------
# Tests for build_inverted_index()
# ---------------------------------------------------------------------------

class TestBuildInvertedIndex:
    """Tests for the build_inverted_index function."""

    def test_single_page_indexes_all_words(self, single_page):
        """Every word in a single page appears in the index."""
        index = build_inverted_index(single_page)
        for word in ["good", "friends", "are", "hard", "to", "find"]:
            assert word in index

    def test_url_is_page_key(self, single_page):
        """The page URL is used as the key under each word entry."""
        index = build_inverted_index(single_page)
        url = "https://example.com/page/1/"
        assert url in index["good"]

    def test_frequency_matches_occurrences(self, two_pages):
        """Frequency count matches the actual number of word occurrences."""
        index = build_inverted_index(two_pages)
        # "good" appears twice on page 2
        page2 = index["good"]["https://example.com/page/2/"]
        assert page2["frequency"] == 2

    def test_frequency_equals_len_positions(self, two_pages):
        """Frequency always equals the length of the positions list."""
        index = build_inverted_index(two_pages)
        for word, pages in index.items():
            for url, stats in pages.items():
                assert stats["frequency"] == len(stats["positions"]), (
                    f"Mismatch for '{word}' on {url}"
                )

    def test_positions_are_token_indexes(self, two_pages):
        """Positions reflect token index, not character offset."""
        index = build_inverted_index(two_pages)
        # Page 2 text: "A good book is a good friend"
        # Tokens:       0    1    2   3  4    5     6
        page2_good = index["good"]["https://example.com/page/2/"]
        assert page2_good["positions"] == [1, 5]

    def test_word_appears_across_multiple_pages(self, two_pages):
        """A word found on two pages has entries for both URLs."""
        index = build_inverted_index(two_pages)
        assert "https://example.com/page/1/" in index["good"]
        assert "https://example.com/page/2/" in index["good"]

    def test_single_occurrence_frequency_is_one(self, single_page):
        """A word appearing once has frequency 1 and a single position."""
        index = build_inverted_index(single_page)
        entry = index["find"]["https://example.com/page/1/"]
        assert entry["frequency"] == 1
        assert len(entry["positions"]) == 1

    def test_empty_pages_list(self):
        """An empty page list produces an empty index."""
        index = build_inverted_index([])
        assert index == {}

    def test_page_with_empty_text(self):
        """A page with empty text adds nothing to the index."""
        pages = [{"url": "https://example.com/empty/", "title": "E", "text": ""}]
        index = build_inverted_index(pages)
        assert index == {}

    def test_case_insensitive_indexing(self):
        """'Good' and 'good' are indexed under the same key."""
        pages = [{"url": "https://example.com/", "title": "T",
                  "text": "Good good GOOD"}]
        index = build_inverted_index(pages)
        assert "good" in index
        assert "Good" not in index
        assert "GOOD" not in index
        assert index["good"]["https://example.com/"]["frequency"] == 3

    def test_index_entry_structure(self, single_page):
        """Each index entry has exactly the 'frequency' and 'positions' keys."""
        index = build_inverted_index(single_page)
        for word, pages in index.items():
            for url, stats in pages.items():
                assert set(stats.keys()) == {"frequency", "positions"}
                assert isinstance(stats["frequency"], int)
                assert isinstance(stats["positions"], list)
