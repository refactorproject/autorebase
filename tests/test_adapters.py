from __future__ import annotations

from pathlib import Path

from engine.core import feature_extract, base_extract


ROOT = Path(__file__).resolve().parents[1]


def test_feature_extract_smoke():
    """Test feature extraction using git patches."""
    old_base = ROOT / "data/sample-base-sw_1.0"
    feature = ROOT / "data/sample-feature-sw_5.0"
    req_map = ROOT / "data/sample/requirements_map.yaml"
    
    units = feature_extract.extract_feature(old_base, feature, req_map)
    assert isinstance(units, list)
    assert len(units) >= 1
    
    # Check that each unit has the expected structure
    for unit in units:
        assert "file_path" in unit
        assert "patch_content" in unit
        assert "req_ids" in unit
        assert "requirements" in unit


def test_base_extract_smoke():
    """Test base extraction using git patches."""
    old_base = ROOT / "data/sample-base-sw_1.0"
    new_base = ROOT / "data/sample-base-sw_1.1"
    
    delta = base_extract.extract_base(old_base, new_base)
    assert isinstance(delta, dict)
    assert "git_patches" in delta
    assert isinstance(delta["git_patches"], dict)

