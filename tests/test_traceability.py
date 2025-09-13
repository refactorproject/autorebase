from __future__ import annotations

from pathlib import Path

from engine.core.traceability import load_requirements_map, req_ids_for_file


ROOT = Path(__file__).resolve().parents[1]


def test_mapping_globs_to_ids():
    mappings = load_requirements_map(ROOT / "data/sample/requirements_map.yaml")
    ids = req_ids_for_file("src/foo.cpp", mappings)
    assert "AD-REQ-201" in ids and "AD-REQ-318" in ids
    ids2 = req_ids_for_file("configs/config.json", mappings)
    assert "AD-REQ-411" in ids2

