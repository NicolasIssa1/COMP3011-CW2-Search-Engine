"""Tests for storage.py – save_index / load_index."""

import json
import os
import pytest

from src.storage import save_index, load_index


# ── save_index ──────────────────────────────────────────────

def test_save_index_creates_file(tmp_path):
    filepath = tmp_path / "index.json"
    save_index({"hello": {}}, str(filepath))
    assert filepath.exists()


def test_save_index_writes_valid_json(tmp_path):
    filepath = tmp_path / "index.json"
    index = {"word": {"http://example.com": {"frequency": 2, "positions": [0, 5]}}}
    save_index(index, str(filepath))
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == index


def test_save_index_creates_parent_directories(tmp_path):
    filepath = tmp_path / "sub" / "dir" / "index.json"
    save_index({}, str(filepath))
    assert filepath.exists()


def test_save_index_rejects_non_dict():
    with pytest.raises(TypeError):
        save_index(["not", "a", "dict"], "ignored.json")


# ── load_index ──────────────────────────────────────────────

def test_load_index_returns_saved_data(tmp_path):
    filepath = tmp_path / "index.json"
    index = {"python": {"http://a.com": {"frequency": 1, "positions": [3]}}}
    save_index(index, str(filepath))
    loaded = load_index(str(filepath))
    assert loaded == index


def test_load_index_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_index("/non/existent/path.json")


def test_load_index_invalid_json(tmp_path):
    filepath = tmp_path / "bad.json"
    filepath.write_text("{not valid json!!!", encoding="utf-8")
    with pytest.raises(ValueError):
        load_index(str(filepath))


def test_load_index_non_dict_json(tmp_path):
    filepath = tmp_path / "list.json"
    filepath.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(ValueError):
        load_index(str(filepath))


def test_roundtrip_empty_index(tmp_path):
    filepath = tmp_path / "empty.json"
    save_index({}, str(filepath))
    assert load_index(str(filepath)) == {}
