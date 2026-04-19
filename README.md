# COMP3011 CW2 – Search Engine

## Overview

A Python command-line search engine built for COMP3011 Coursework 2. The tool crawls [quotes.toscrape.com](https://quotes.toscrape.com/), builds an inverted index from the page content, saves it to disk, and provides interactive commands to search for words and phrases across the crawled pages.

## Features

- **Web crawling** – automatically follows pagination across all pages of the target site.
- **Politeness delay** – waits 6 seconds between HTTP requests to respect the server.
- **Inverted index** – maps every word to the pages it appears on, recording frequency and token positions.
- **Case-insensitive search** – all text is lowercased at index time, so queries match regardless of case.
- **Single-word lookup** (`print`) – displays every page a word appears on, with frequency and positions.
- **Multi-word search** (`find`) – returns only pages containing *all* query words.
- **Persistent storage** – the index is saved as JSON and can be reloaded without re-crawling.

## Project Structure

```
COMP3011-CW2-Search-Engine/
├── src/
│   ├── crawler.py          Web crawler (fetch, parse, paginate)
│   ├── indexer.py           Tokeniser and inverted index builder
│   ├── storage.py           Save / load index as JSON
│   ├── search.py            Word lookup and phrase query functions
│   └── main.py              Interactive command-line interface
├── tests/
│   ├── test_crawler.py      Unit tests for the crawler
│   ├── test_indexer.py       Unit tests for the indexer
│   ├── test_storage.py       Unit tests for storage
│   ├── test_search.py        Unit tests for search
│   └── test_integration.py   Integration and CLI tests
├── data/
│   └── index.json           Generated index (created by `build`)
├── requirements.txt
└── pytest.ini
```

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `requests`, `beautifulsoup4`, `lxml`, `pytest`.

## How to Run the Application

```bash
python -m src.main
```

This starts an interactive prompt with the following commands:

| Command | Description |
|---|---|
| `build` | Crawl the website, build the inverted index, and save it to `data/index.json`. |
| `load` | Load a previously saved index from `data/index.json`. |
| `print <word>` | Display the index entry for a single word. |
| `find <query>` | Find pages that contain all words in the query. |
| `quit` | Exit the program. |

## Example Commands and Outputs

```
COMP3011 Search Engine
Commands: build | load | print <word> | find <query> | quit

>> build
Crawling website...
[INFO] Crawling page 1: https://quotes.toscrape.com/
[INFO] Extracted 985 chars from page 1
[INFO] Waiting 6s (politeness window)...
[INFO] Crawling page 2: https://quotes.toscrape.com/page/2/
...
[INFO] Crawling complete. 10 page(s) collected.
Building inverted index...
Saving index to data/index.json...
Done. 1487 unique words indexed from 10 page(s).

>> print world
Entry for 'world':
  https://quotes.toscrape.com/
    Frequency : 3
    Positions : [42, 118, 205]

>> find good friends
Found 1 page(s) matching 'good friends':

  https://quotes.toscrape.com/page/2/
    'good' — frequency: 2, positions: [31, 85]
    'friends' — frequency: 1, positions: [86]

>> quit
Goodbye!
```

## Running Tests

```bash
pytest -v
```

The project has **73 passing tests**:

- **21** crawler tests (fetch, parse, pagination, crawl orchestration)
- **20** indexer tests (tokenisation, index structure, frequencies, positions)
- **9** storage tests (save, load, error handling, round-trip)
- **15** search tests (word lookup, phrase query, edge cases)
- **8** integration and CLI tests (full pipeline, command loop)

## Design Overview

| Module | Responsibility |
|---|---|
| **crawler.py** | Fetches pages with `requests`, parses HTML with BeautifulSoup, strips `<script>` and `<style>` tags, extracts visible text, and follows "next" pagination links. |
| **indexer.py** | Splits page text into tokens using a regex, lowercases every token, and builds the inverted index mapping words → pages → frequency and positions. |
| **storage.py** | `save_index()` writes the index to a JSON file (creating directories if needed). `load_index()` reads it back, with error handling for missing files and corrupt JSON. |
| **search.py** | `get_word_entry(index, word)` returns the index entry for one word. `find_query(index, query)` returns pages matching all query words (set intersection). |
| **main.py** | Runs an interactive input loop that delegates to the four modules above. Handles missing index, empty input, and unknown commands gracefully. |

## Notes

### Case-Insensitive Search

All text is lowercased during indexing (`indexer.py`), and all queries are lowercased before lookup (`search.py`). This means `print World`, `print WORLD`, and `print world` all return the same result.

### Inverted Index Format

The index is stored as a nested JSON object:

```json
{
  "word": {
    "page_url": {
      "frequency": 3,
      "positions": [0, 14, 27]
    }
  }
}
```

- **frequency** – the number of times the word appears on that page.
- **positions** – a list of zero-based token positions for each occurrence.