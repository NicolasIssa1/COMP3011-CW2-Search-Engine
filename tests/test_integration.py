"""
test_integration.py – End-to-end tests across multiple modules.

These tests verify that the modules work together correctly:
crawler output → indexer → storage → search.
"""

import pytest

from src.indexer import build_inverted_index
from src.storage import save_index, load_index
from src.search import get_word_entry, find_query


@pytest.fixture
def crawled_pages():
    """Simulated crawler output (two pages, no network call needed)."""
    return [
        {
            "url": "https://quotes.toscrape.com/",
            "title": "Quotes to Scrape",
            "text": "The world as I see it is a remarkable place",
        },
        {
            "url": "https://quotes.toscrape.com/page/2/",
            "title": "Quotes to Scrape",
            "text": "A room without books is like a body without a soul",
        },
    ]


class TestBuildSaveLoadSearch:
    """Full pipeline: build index → save → load → search."""

    def test_pipeline_roundtrip(self, crawled_pages, tmp_path):
        """Index built from pages survives a save/load cycle."""
        index = build_inverted_index(crawled_pages)
        filepath = str(tmp_path / "index.json")

        save_index(index, filepath)
        loaded = load_index(filepath)

        assert loaded == index

    def test_search_after_load(self, crawled_pages, tmp_path):
        """get_word_entry works correctly on a loaded index."""
        index = build_inverted_index(crawled_pages)
        filepath = str(tmp_path / "index.json")
        save_index(index, filepath)
        loaded = load_index(filepath)

        entry = get_word_entry(loaded, "world")
        assert "https://quotes.toscrape.com/" in entry
        assert entry["https://quotes.toscrape.com/"]["frequency"] == 1

    def test_find_query_after_load(self, crawled_pages, tmp_path):
        """find_query returns correct results on a loaded index."""
        index = build_inverted_index(crawled_pages)
        filepath = str(tmp_path / "index.json")
        save_index(index, filepath)
        loaded = load_index(filepath)

        # "a" appears on both pages
        results = find_query(loaded, "a")
        urls = [r["url"] for r in results]
        assert "https://quotes.toscrape.com/" in urls
        assert "https://quotes.toscrape.com/page/2/" in urls

    def test_multi_word_find_after_pipeline(self, crawled_pages, tmp_path):
        """Multi-word query on loaded index returns only intersecting pages."""
        index = build_inverted_index(crawled_pages)
        filepath = str(tmp_path / "index.json")
        save_index(index, filepath)
        loaded = load_index(filepath)

        # "without" and "books" only appear on page 2
        results = find_query(loaded, "without books")
        assert len(results) == 1
        assert results[0]["url"] == "https://quotes.toscrape.com/page/2/"


class TestCLIBehavior:
    """Lightweight tests for the main() command loop logic."""

    def test_main_quit(self, monkeypatch, capsys):
        """The quit command exits the loop cleanly."""
        from src.main import main

        monkeypatch.setattr("builtins.input", lambda _: "quit")
        main()

        output = capsys.readouterr().out
        assert "Goodbye!" in output

    def test_main_unknown_command(self, monkeypatch, capsys):
        """An unknown command prints a helpful error, then quit exits."""
        from src.main import main

        inputs = iter(["xyzzy", "quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main()

        output = capsys.readouterr().out
        assert "Unknown command" in output

    def test_main_print_without_load(self, monkeypatch, capsys):
        """print before loading an index gives a clear error."""
        from src.main import main

        inputs = iter(["print hello", "quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main()

        output = capsys.readouterr().out
        assert "No index loaded" in output

    def test_main_find_without_load(self, monkeypatch, capsys):
        """find before loading an index gives a clear error."""
        from src.main import main

        inputs = iter(["find hello world", "quit"])
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        main()

        output = capsys.readouterr().out
        assert "No index loaded" in output
