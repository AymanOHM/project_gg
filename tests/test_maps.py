"""Smoke test: the unconverted v1-format maps in data/maps still parse (roadmap task 2.4)."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
MAP_FILES = sorted((ROOT / "data" / "maps").glob("*.json"))


@pytest.mark.parametrize("path", MAP_FILES, ids=lambda p: p.name)
def test_map_file_has_tilemap_and_offgrid(path):
    data = json.loads(path.read_text())
    assert isinstance(data["tilemap"], dict) and data["tilemap"]
    assert isinstance(data["offgrid"], list)
    for key, tile in data["tilemap"].items():
        assert key == f"{tile['pos'][0]};{tile['pos'][1]}"
