"""
crawler.py - Web crawler for quotes.toscrape.com

Crawls all pages of the target website, following pagination links,
and extracts the URL, title, and visible text content from each page.
Respects a politeness window of at least 6 seconds between requests.
"""

import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
POLITENESS_DELAY = 6  # seconds between successive requests


def fetch_page(url):
    """Send a GET request to the given URL and return the Response object.

    Args:
        url: The full URL to fetch.

    Returns:
        A requests.Response object if successful, None otherwise.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None


def parse_page(url, html):
    """Parse a page's HTML and extract its URL, title, and visible text.

    Args:
        url: The URL of the page (stored as-is in the result).
        html: The raw HTML string of the page.

    Returns:
        A dictionary with keys 'url', 'title', and 'text'.
    """
    soup = BeautifulSoup(html, "lxml")

    # Extract the <title> tag text, falling back to empty string
    title = soup.title.string.strip() if soup.title and soup.title.string else ""

    # Extract visible text from the page body
    body = soup.body
    if body:
        # Remove script and style elements that aren't visible content
        for tag in body.find_all(["script", "style"]):
            tag.decompose()
        text = body.get_text(separator=" ", strip=True)
    else:
        text = ""

    return {"url": url, "title": title, "text": text}


def get_next_page_url(html):
    """Find the 'next' pagination link in the page HTML.

    Args:
        html: The raw HTML string of the page.

    Returns:
        The full URL of the next page, or None if there is no next page.
    """
    soup = BeautifulSoup(html, "lxml")
    next_li = soup.find("li", class_="next")
    if next_li:
        anchor = next_li.find("a")
        if anchor and anchor.get("href"):
            return BASE_URL + anchor["href"]
    return None


def crawl(start_url=None):
    """Crawl all pages starting from start_url, following pagination.

    Respects the politeness window between successive requests.

    Args:
        start_url: The URL to begin crawling from. Defaults to BASE_URL + "/".

    Returns:
        A list of dictionaries, each with 'url', 'title', and 'text' keys.
    """
    if start_url is None:
        start_url = BASE_URL + "/"

    pages = []
    current_url = start_url
    page_number = 1

    while current_url:
        # Politeness delay before every request except the first
        if page_number > 1:
            print(f"[INFO] Waiting {POLITENESS_DELAY}s (politeness window)...")
            time.sleep(POLITENESS_DELAY)

        print(f"[INFO] Crawling page {page_number}: {current_url}")
        response = fetch_page(current_url)

        if response is None:
            print(f"[WARN] Skipping page {page_number} due to fetch error.")
            break

        page_data = parse_page(current_url, response.text)
        pages.append(page_data)
        print(f"[INFO] Extracted {len(page_data['text'])} chars from page {page_number}")

        # Follow pagination
        current_url = get_next_page_url(response.text)
        page_number += 1

    print(f"[INFO] Crawling complete. {len(pages)} page(s) collected.")
    return pages
