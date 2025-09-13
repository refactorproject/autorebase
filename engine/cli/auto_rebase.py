from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core import config as cfg
from ..core import feature_extract, base_extract, retarget as rt, validate as val, report as rep
from ..core.utils import setup_logging, write_json
from ..adapters import c_cpp, json_cfg, yaml_cfg, dtsi, text_generic
from ..core.vcs import commit_and_tag


def _tools_matrix() -> dict[str, Any]:
    return {
        "c_cpp": c_cpp.detect_env(),
        "json": json_cfg.detect_env(),
        "yaml": yaml_cfg.detect_env(),
        "dtsi": dtsi.detect_env(),
        "text": text_generic.detect_env(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(prog="auto-rebase")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--old-base", required=True)
    p_init.add_argument("--new-base", required=True)
    p_init.add_argument("--feature", required=True)
    p_init.add_argument("--req-map", required=True)
    p_init.add_argument("--workdir", required=True)
    p_init.add_argument("--verbose", action="store_true")

    p_ef = sub.add_parser("extract-feature")
    p_ef.add_argument("--out", required=True)
    p_ef.add_argument("--verbose", action="store_true")

    p_eb = sub.add_parser("extract-base")
    p_eb.add_argument("--out", required=True)
    p_eb.add_argument("--verbose", action="store_true")

    p_rt = sub.add_parser("retarget")
    p_rt.add_argument("--feature-patch", required=True)
    p_rt.add_argument("--base-patch", required=True)
    p_rt.add_argument("--new-base", required=True)
    p_rt.add_argument("--out", required=True)
    p_rt.add_argument("--verbose", action="store_true")

    p_val = sub.add_parser("validate")
    p_val.add_argument("--path", required=True)
    p_val.add_argument("--report", required=True)
    p_val.add_argument("--verbose", action="store_true")

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--path", required=True)
    p_fin.add_argument("--tag", required=True)
    p_fin.add_argument("--trace", required=True)
    p_fin.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    def find_manifest(start_path: Path) -> dict[str, Any]:
        """Walk up from a path to find a run.json manifest and return it."""
        for p in [start_path] + list(start_path.parents):
            cand = p / "run.json"
            if cand.exists():
                return json.loads(cand.read_text(encoding="utf-8"))
        # Also try artifacts parent convention
        cand = Path("artifacts/run1/run.json")
        if cand.exists():
            return json.loads(cand.read_text(encoding="utf-8"))
        raise SystemExit("run.json manifest not found. Run 'init' first or ensure --out is under the workdir.")

    if args.cmd == "init":
        artifacts_dir = Path(args.workdir)
        setup_logging(Path(artifacts_dir) / "logs" / "run.log", args.verbose)
        man = cfg.new_run_manifest(
            old_base=Path(args.old_base),
            new_base=Path(args.new_base),
            feature=Path(args.feature),
            req_map=Path(args.req_map),
            workdir=artifacts_dir,
        )
        cfg.persist_manifest(man, Path(args.workdir))
        print(json.dumps({"run_id": man.run_id, "workdir": args.workdir}))
        return

    # For subsequent steps, derive workdir from provided paths.
    setup_logging(None, getattr(args, "verbose", False))

    if args.cmd == "extract-feature":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        man = find_manifest(out)
        old_base = Path(man["old_base"]).resolve()
        feature = Path(man["feature_old"]).resolve()
        req_map = Path(man["req_map"]).resolve()
        units = feature_extract.extract_feature(old_base, feature, req_map)
        write_json(out / "feature_patch.json", [u for u in units])
        print(str(out / "feature_patch.json"))
        return

    if args.cmd == "extract-base":
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        man = find_manifest(out)
        old_base = Path(man["old_base"]).resolve()
        new_base = Path(man["new_base"]).resolve()
        delta = base_extract.extract_base(old_base, new_base)
        write_json(out / "base_patch.json", delta)
        print(str(out / "base_patch.json"))
        return

    if args.cmd == "retarget":
        feature_patch = json.loads(Path(args.feature_patch).read_text(encoding="utf-8"))
        base_patch = json.loads(Path(args.base_patch).read_text(encoding="utf-8"))
        new_base_root = Path(args.new_base)
        out_dir = Path(args.out)
        results = rt.retarget(feature_patch, base_patch, new_base_root, out_dir)
        write_json(out_dir / "retarget_results.json", results)
        print(str(out_dir / "retarget_results.json"))
        return

    if args.cmd == "validate":
        target = Path(args.path)
        report_html = Path(args.report)
        report_json = report_html.with_suffix(".json")
        outcomes_path = target / "retarget_results.json"
        outcomes = json.loads(outcomes_path.read_text(encoding="utf-8")) if outcomes_path.exists() else {"summary": {}, "files": []}
        validation = val.validate(target)
        tools = _tools_matrix()
        # Load simple report schema
        schema_path = Path("schemas/report.schema.json")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        run_id = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        rep.generate(run_id, outcomes, validation, tools, report_json, report_html, schema)
        print(str(report_html))
        return

    if args.cmd == "finalize":
        target = Path(args.path)
        tag = args.tag
        trace_path = Path(args.trace)
        # Build trace.json from patch req_ids; demo: synthesize from retarget_results
        results_path = target / "retarget_results.json"
        trace = []
        if results_path.exists():
            results = json.loads(results_path.read_text(encoding="utf-8"))
            for f in results.get("files", []):
                if f.get("req_ids"):
                    trace.append({"file": f["file"], "req_ids": f["req_ids"]})
        write_json(trace_path, trace)
        trailers = {
            "Req-Id": ",".join(sorted({rid for t in trace for rid in t.get("req_ids", [])})),
            "Change-Type": "FeatureCustomization",
            "Auto-Rebase-Run": datetime.utcnow().isoformat() + "Z",
        }
        commit_and_tag(target, tag, trailers)
        print(str(trace_path))
        return


if __name__ == "__main__":
    main()
