"""
indexer.py - Inverted index builder for the search engine.

Takes crawled page data and builds an inverted index that maps every
word to the pages it appears in, along with frequency and position
statistics.  All text is lowercased so searches are case-insensitive.
"""

import re


def tokenize_text(text):
    """Split text into a list of lowercase word tokens.

    Uses a regular expression to extract sequences of alphanumeric
    characters (including apostrophes within words like "don't").
    Punctuation, symbols, and whitespace are discarded.

    Args:
        text (str): A string of raw page text.

    Returns:
        list[str]: A list of lowercase token strings, preserving their order.
    """
    # Match word characters and internal apostrophes (e.g. "it's", "don't")
    tokens = re.findall(r"[a-zA-Z0-9]+(?:'[a-zA-Z]+)?", text)
    return [token.lower() for token in tokens]


def build_inverted_index(pages):
    """Build an inverted index from a list of crawled pages.

    For each word found across all pages, the index records which pages
    contain it, how many times it appears on each page (frequency), and
    at which token positions it occurs.

    Args:
        pages (list[dict]): A list of dicts, each with keys 'url', 'title',
            and 'text', as returned by crawler.crawl().

    Returns:
        dict: The inverted index, structured as:
            {
                "word": {
                    "page_url": {
                        "frequency": int,
                        "positions": [int, ...]
                    }
                }
            }
    """
    index = {}

    for page in pages:
        url = page["url"]
        tokens = tokenize_text(page["text"])

        for position, token in enumerate(tokens):
            # Create the word entry if it doesn't exist yet
            if token not in index:
                index[token] = {}

            # Create the page entry for this word if it doesn't exist yet
            if url not in index[token]:
                index[token][url] = {"frequency": 0, "positions": []}

            # Record this occurrence
            index[token][url]["frequency"] += 1
            index[token][url]["positions"].append(position)

    return index
