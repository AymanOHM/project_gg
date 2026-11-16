"""Smoke test: every shipped map file parses and has the expected top-level shape."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAP_FILES = [ROOT / "map.json", *sorted((ROOT / "data" / "maps").glob("*.json"))]


@pytest.mark.parametrize("path", MAP_FILES, ids=lambda p: p.name)
def test_map_file_has_tilemap_and_offgrid(path):
    data = json.loads(path.read_text())
    assert isinstance(data["tilemap"], dict) and data["tilemap"]
    assert isinstance(data["offgrid"], list)
    for key, tile in data["tilemap"].items():
        assert key == f"{tile['pos'][0]};{tile['pos'][1]}"
