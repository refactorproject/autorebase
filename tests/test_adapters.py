from __future__ import annotations

from pathlib import Path

from engine.adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic


ROOT = Path(__file__).resolve().parents[1]


def test_detect_env_smoke():
    envs = [c_cpp.detect_env(), json_cfg.detect_env(), yaml_cfg.detect_env(), dtsi.detect_env(), text_generic.detect_env()]
    assert all(isinstance(e, dict) for e in envs)


def test_extractors_smoke():
    ob = ROOT / "data/sample/base-1.0"
    fb = ROOT / "data/sample/feature-5.0"
    assert len(c_cpp.extract_feature(ob, fb)) >= 1
    assert len(json_cfg.extract_feature(ob, fb)) >= 1
    assert len(yaml_cfg.extract_feature(ob, fb)) >= 1
    assert len(dtsi.extract_feature(ob, fb)) >= 1

