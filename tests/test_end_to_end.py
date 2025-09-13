from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", "-m", "engine.cli.auto_rebase", *args], cwd=ROOT, text=True, capture_output=True, check=True)


def test_e2e_flow(tmp_path: Path):
    art = ROOT / "artifacts" / "run1"
    art.mkdir(parents=True, exist_ok=True)

    run_cli(["init", "--old-base", "data/sample/base-1.0", "--new-base", "data/sample/base-1.1", "--feature", "data/sample/feature-5.0", "--req-map", "data/sample/requirements_map.yaml", "--workdir", str(art)])

    fp = art / "feature_patch"
    bp = art / "base_patch"
    out = art / "feature-5.1"

    run_cli(["extract-feature", "--out", str(fp)])
    run_cli(["extract-base", "--out", str(bp)])

    feature_patch = fp / "feature_patch.json"
    base_patch = bp / "base_patch.json"
    assert feature_patch.exists()
    assert base_patch.exists()

    run_cli(["retarget", "--feature-patch", str(feature_patch), "--base-patch", str(base_patch), "--new-base", "data/sample/base-1.1", "--out", str(out)])

    assert (out / "retarget_results.json").exists()

    # Validate and report
    report_html = out / "../report.html"
    run_cli(["validate", "--path", str(out), "--report", str(report_html)])
    report_json = report_html.with_suffix(".json")
    assert report_html.exists()
    assert report_json.exists()

    # Load and check schema-ish keys
    report = json.loads(report_json.read_text(encoding="utf-8"))
    assert "summary" in report and "files" in report
    # Should have at least one file outcome
    assert len(report["files"]) >= 1

