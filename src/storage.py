"""
storage.py – Save and load the inverted index as JSON.

Provides two functions:
    save_index(index, filepath)  – serialise the index dict to a JSON file.
    load_index(filepath)         – read a JSON file back into a dict.
"""

import json
import os


def save_index(index, filepath):
    """Write the inverted index to a JSON file.

    Args:
        index (dict): The inverted index to save.
        filepath (str): Path to the output JSON file.

    Raises:
        TypeError: If `index` is not a dict.
        IOError: If the file cannot be written.
    """
    if not isinstance(index, dict):
        raise TypeError("Index must be a dictionary.")

    # Create parent directories if they don't already exist
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def load_index(filepath):
    """Load an inverted index from a JSON file.

    Args:
        filepath (str): Path to the JSON file.

    Returns:
        dict: The inverted index.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file contains invalid or corrupted JSON.
        IOError: If the file cannot be read.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Index file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in index file: {e}")

    if not isinstance(data, dict):
        raise ValueError("Index file does not contain a valid index (expected a JSON object).")

    return data
