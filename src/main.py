"""
main.py – Command-line interface for the search engine.

Commands:
    build           Crawl the website, build the index, and save it.
    load            Load a previously saved index from disk.
    print <word>    Show the index entry for a single word.
    find <query>    Find pages matching a query (all words must appear).
    quit            Exit the program.
"""

from src.crawler import crawl
from src.indexer import build_inverted_index
from src.storage import save_index, load_index
from src.search import get_word_entry, find_query

INDEX_PATH = "data/index.json"


def handle_build():
    """Crawl the site, build the inverted index, and save it."""
    print("Crawling website...")
    pages = crawl()

    print("Building inverted index...")
    index = build_inverted_index(pages)

    print(f"Saving index to {INDEX_PATH}...")
    save_index(index, INDEX_PATH)

    print(f"Done. {len(index)} unique words indexed from {len(pages)} page(s).")
    return index


def handle_load():
    """Load the inverted index from disk."""
    try:
        index = load_index(INDEX_PATH)
        print(f"Index loaded from {INDEX_PATH} ({len(index)} words).")
        return index
    except FileNotFoundError:
        print(f"Error: {INDEX_PATH} not found. Run 'build' first.")
    except ValueError as e:
        print(f"Error: {e}")
    return None


def handle_print(index, word):
    """Display the index entry for a single word."""
    entry = get_word_entry(index, word)
    if not entry:
        print(f"Word '{word.strip()}' not found in the index.")
        return

    # Use the normalised (lowercase, stripped) form for display
    normalised = word.strip().lower()
    print(f"Entry for '{normalised}':")
    for url, data in entry.items():
        print(f"  {url}")
        print(f"    Frequency : {data['frequency']}")
        print(f"    Positions : {data['positions']}")


def handle_find(index, query):
    """Display pages matching a multi-word query."""
    results = find_query(index, query)
    if not results:
        print(f"No pages found for '{query.strip()}'.")
        return

    print(f"Found {len(results)} page(s) matching '{query.strip()}':\n")
    for result in results:
        print(f"  {result['url']}")
        for word, data in result["words"].items():
            print(f"    '{word}' — frequency: {data['frequency']}, positions: {data['positions']}")
        print()


def main():
    """Run the interactive command loop."""
    index = None

    print("COMP3011 Search Engine")
    print("Commands: build | load | print <word> | find <query> | quit\n")

    while True:
        try:
            user_input = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Split into command and argument(s)
        parts = user_input.split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        if command == "quit":
            print("Goodbye!")
            break

        elif command == "build":
            index = handle_build()

        elif command == "load":
            loaded = handle_load()
            if loaded is not None:
                index = loaded

        elif command == "print":
            if index is None:
                print("No index loaded. Run 'build' or 'load' first.")
            elif not argument:
                print("Usage: print <word>")
            else:
                handle_print(index, argument)

        elif command == "find":
            if index is None:
                print("No index loaded. Run 'build' or 'load' first.")
            elif not argument:
                print("Usage: find <query>")
            else:
                handle_find(index, argument)

        else:
            print(f"Unknown command: '{command}'")
            print("Commands: build | load | print <word> | find <query> | quit")


if __name__ == "__main__":
    main()
