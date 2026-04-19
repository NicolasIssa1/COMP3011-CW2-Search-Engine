"""
search.py – Query functions for the inverted index.

Provides two functions:
    get_word_entry(index, word) – look up a single word in the index.
    find_query(index, query)    – find pages that contain every word in a query.
"""


def get_word_entry(index, word):
    """Look up a single word in the inverted index.

    The search is case-insensitive: the word is lowercased before lookup.

    Args:
        index (dict): The inverted index.
        word (str): The word to search for.

    Returns:
        dict: A dict mapping page URLs to their frequency/positions data
              for that word, or an empty dict if the word is not found.
    """
    word = word.strip().lower()
    if not word:
        return {}

    return index.get(word, {})


def find_query(index, query):
    """Find pages that contain every word in a query phrase.

    The query is split on whitespace, each word is lowercased, and
    only pages that appear in the index entry for *every* query word
    are returned.

    Args:
        index (dict): The inverted index.
        query (str): A single- or multi-word search query.

    Returns:
        list[dict]: A list of result dicts, one per matching page, e.g.
            [
                {
                    "url": "http://example.com",
                    "words": {
                        "python": {"frequency": 3, "positions": [0, 4, 9]},
                        "code":   {"frequency": 1, "positions": [5]}
                    }
                },
                ...
            ]
            Returns an empty list when the query is blank or no pages match.
    """
    # Normalise the query: lowercase and split on whitespace
    words = query.strip().lower().split()
    if not words:
        return []

    # Gather the set of page URLs for each query word
    sets_of_urls = []
    for word in words:
        entries = index.get(word, {})
        sets_of_urls.append(set(entries.keys()))

    # Pages must contain ALL query words
    matching_urls = set.intersection(*sets_of_urls) if sets_of_urls else set()

    # Build a result list with per-word details for each matching page
    results = []
    for url in sorted(matching_urls):
        word_details = {}
        for word in words:
            word_details[word] = index[word][url]
        results.append({"url": url, "words": word_details})

    return results
