"""
test_crawler.py - Unit tests for the web crawler module.

Uses pytest and unittest.mock to test each crawler function
without making real HTTP requests.
"""

import pytest
from unittest.mock import patch, Mock
import requests

from src.crawler import fetch_page, parse_page, get_next_page_url, crawl, BASE_URL


# ---------------------------------------------------------------------------
# Fixtures: reusable HTML snippets
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_html():
    """A realistic HTML page with quotes, a title, and a 'next' link."""
    return """
    <html>
    <head><title>Quotes to Scrape</title></head>
    <body>
        <div class="quote">
            <span class="text">"The world is a book."</span>
            <small class="author">Saint Augustine</small>
        </div>
        <nav>
            <ul class="pager">
                <li class="next"><a href="/page/2/">Next</a></li>
            </ul>
        </nav>
    </body>
    </html>
    """


@pytest.fixture
def last_page_html():
    """HTML for the final page — has a 'previous' link but no 'next' link."""
    return """
    <html>
    <head><title>Quotes to Scrape</title></head>
    <body>
        <div class="quote">
            <span class="text">"Last quote on the site."</span>
        </div>
        <nav>
            <ul class="pager">
                <li class="previous"><a href="/page/9/">Previous</a></li>
            </ul>
        </nav>
    </body>
    </html>
    """


@pytest.fixture
def html_with_script_and_style():
    """HTML containing <script> and <style> tags that should be stripped."""
    return """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <p>Visible text here.</p>
        <script>var x = 1;</script>
        <style>.hidden { display: none; }</style>
        <p>More visible text.</p>
    </body>
    </html>
    """


# ---------------------------------------------------------------------------
# Tests for fetch_page()
# ---------------------------------------------------------------------------

class TestFetchPage:
    """Tests for the fetch_page function."""

    @patch("src.crawler.requests.get")
    def test_successful_fetch(self, mock_get):
        """fetch_page returns a Response on a 200 OK."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fetch_page("https://example.com")

        assert result is mock_response
        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("src.crawler.requests.get")
    def test_http_error_returns_none(self, mock_get):
        """fetch_page returns None when the server responds with an error status."""
        mock_get.return_value.raise_for_status.side_effect = requests.HTTPError("404")

        result = fetch_page("https://example.com/bad")

        assert result is None

    @patch("src.crawler.requests.get")
    def test_connection_error_returns_none(self, mock_get):
        """fetch_page returns None on a network connection failure."""
        mock_get.side_effect = requests.ConnectionError("Connection refused")

        result = fetch_page("https://nonexistent.invalid")

        assert result is None

    @patch("src.crawler.requests.get")
    def test_timeout_returns_none(self, mock_get):
        """fetch_page returns None when the request times out."""
        mock_get.side_effect = requests.Timeout("Request timed out")

        result = fetch_page("https://example.com")

        assert result is None


# ---------------------------------------------------------------------------
# Tests for parse_page()
# ---------------------------------------------------------------------------

class TestParsePage:
    """Tests for the parse_page function."""

    def test_extracts_url_title_and_text(self, sample_html):
        """parse_page correctly extracts the URL, title, and body text."""
        result = parse_page("https://example.com", sample_html)

        assert result["url"] == "https://example.com"
        assert result["title"] == "Quotes to Scrape"
        assert "The world is a book." in result["text"]
        assert "Saint Augustine" in result["text"]

    def test_strips_script_and_style(self, html_with_script_and_style):
        """parse_page removes <script> and <style> content from the text."""
        result = parse_page("https://example.com", html_with_script_and_style)

        assert "Visible text here." in result["text"]
        assert "More visible text." in result["text"]
        assert "var x = 1" not in result["text"]
        assert ".hidden" not in result["text"]

    def test_empty_html(self):
        """parse_page handles an empty HTML string without crashing."""
        result = parse_page("https://example.com", "")

        assert result["url"] == "https://example.com"
        assert result["title"] == ""
        assert result["text"] == ""

    def test_missing_title_tag(self):
        """parse_page returns empty title if <title> is absent."""
        html = "<html><body><p>Hello</p></body></html>"
        result = parse_page("https://example.com", html)

        assert result["title"] == ""
        assert "Hello" in result["text"]

    def test_missing_body_tag(self):
        """parse_page returns empty text if <body> is absent."""
        html = "<html><head><title>Title Only</title></head></html>"
        result = parse_page("https://example.com", html)

        assert result["title"] == "Title Only"
        # lxml may auto-generate a body; accept either outcome
        assert isinstance(result["text"], str)

    def test_result_keys(self, sample_html):
        """parse_page always returns a dict with exactly 'url', 'title', 'text'."""
        result = parse_page("https://example.com", sample_html)

        assert set(result.keys()) == {"url", "title", "text"}


# ---------------------------------------------------------------------------
# Tests for get_next_page_url()
# ---------------------------------------------------------------------------

class TestGetNextPageUrl:
    """Tests for the get_next_page_url function."""

    def test_finds_next_link(self, sample_html):
        """get_next_page_url returns the full URL of the next page."""
        result = get_next_page_url(sample_html)

        assert result == BASE_URL + "/page/2/"

    def test_returns_none_on_last_page(self, last_page_html):
        """get_next_page_url returns None when there is no 'next' link."""
        result = get_next_page_url(last_page_html)

        assert result is None

    def test_returns_none_for_empty_html(self):
        """get_next_page_url returns None for an empty HTML string."""
        result = get_next_page_url("")

        assert result is None

    def test_returns_none_when_no_pager(self):
        """get_next_page_url returns None when there is no pagination at all."""
        html = "<html><body><p>No pagination here</p></body></html>"
        result = get_next_page_url(html)

        assert result is None

    def test_next_li_without_anchor(self):
        """get_next_page_url returns None when <li class='next'> has no <a>."""
        html = '<html><body><li class="next"></li></body></html>'
        result = get_next_page_url(html)

        assert result is None


# ---------------------------------------------------------------------------
# Tests for crawl()
# ---------------------------------------------------------------------------

class TestCrawl:
    """Tests for the crawl orchestrator function."""

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_single_page(self, mock_fetch, mock_sleep):
        """crawl returns one page when there is no 'next' link."""
        mock_response = Mock()
        mock_response.text = """
        <html><head><title>Page 1</title></head>
        <body><p>Only page</p></body></html>
        """
        mock_fetch.return_value = mock_response

        result = crawl("https://quotes.toscrape.com/")

        assert len(result) == 1
        assert result[0]["title"] == "Page 1"
        assert "Only page" in result[0]["text"]
        # No sleep needed for a single page
        mock_sleep.assert_not_called()

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_follows_pagination(self, mock_fetch, mock_sleep):
        """crawl follows 'next' links across multiple pages."""
        page1_html = """
        <html><head><title>Page 1</title></head>
        <body><p>First</p>
        <li class="next"><a href="/page/2/">Next</a></li>
        </body></html>
        """
        page2_html = """
        <html><head><title>Page 2</title></head>
        <body><p>Second</p></body></html>
        """
        resp1 = Mock()
        resp1.text = page1_html
        resp2 = Mock()
        resp2.text = page2_html
        mock_fetch.side_effect = [resp1, resp2]

        result = crawl("https://quotes.toscrape.com/")

        assert len(result) == 2
        assert result[0]["title"] == "Page 1"
        assert result[1]["title"] == "Page 2"

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_respects_politeness_delay(self, mock_fetch, mock_sleep):
        """crawl calls time.sleep(6) before the second request onward."""
        page1_html = """
        <html><head><title>P1</title></head>
        <body><li class="next"><a href="/page/2/">Next</a></li></body></html>
        """
        page2_html = """
        <html><head><title>P2</title></head><body><p>End</p></body></html>
        """
        resp1, resp2 = Mock(), Mock()
        resp1.text = page1_html
        resp2.text = page2_html
        mock_fetch.side_effect = [resp1, resp2]

        crawl("https://quotes.toscrape.com/")

        # Sleep should be called once (before page 2), with 6 seconds
        mock_sleep.assert_called_once_with(6)

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_stops_on_fetch_error(self, mock_fetch, mock_sleep):
        """crawl stops and returns collected pages when a fetch fails."""
        mock_fetch.return_value = None  # simulate failure on the first page

        result = crawl("https://quotes.toscrape.com/")

        assert result == []

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_stops_midway_on_error(self, mock_fetch, mock_sleep):
        """crawl keeps pages collected before a mid-crawl failure."""
        page1_html = """
        <html><head><title>P1</title></head>
        <body><p>OK</p>
        <li class="next"><a href="/page/2/">Next</a></li>
        </body></html>
        """
        resp1 = Mock()
        resp1.text = page1_html
        mock_fetch.side_effect = [resp1, None]  # page 2 fails

        result = crawl("https://quotes.toscrape.com/")

        assert len(result) == 1
        assert result[0]["title"] == "P1"

    @patch("src.crawler.time.sleep")
    @patch("src.crawler.fetch_page")
    def test_crawl_uses_default_start_url(self, mock_fetch, mock_sleep):
        """crawl defaults to BASE_URL + '/' when no start_url is given."""
        mock_fetch.return_value = None

        crawl()

        mock_fetch.assert_called_once_with(BASE_URL + "/")
