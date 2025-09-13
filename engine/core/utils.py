from __future__ import annotations

import json
import logging
import os
import subprocess
from dataclasses import asdict
import shutil
from pathlib import Path
from typing import Any, Iterable, Optional


LOG = logging.getLogger("auto_rebase")


def setup_logging(log_path: Optional[Path] = None, verbose: bool = False) -> None:
    """Configure logging. If log_path is provided, also log to file.

    Avoid secrets in logs; INFO default, DEBUG if verbose.
    """

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(log_path)
        fh.setLevel(level)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logging.getLogger().addHandler(fh)


def which(cmd: str) -> Optional[str]:
    """Return full path if command exists in PATH, else None."""

    from shutil import which as _which

    return _which(cmd)


def run_cmd(args: list[str], cwd: Optional[Path] = None, check: bool = True) -> tuple[int, str, str]:
    """Run a subprocess and capture output. Returns (code, stdout, stderr)."""

    LOG.debug("Running: %s", " ".join(args))
    proc = subprocess.Popen(args, cwd=str(cwd) if cwd else None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\n{err}")
    return proc.returncode, out, err


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def list_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file()]


def rel_to(path: Path, base: Path) -> str:
    return str(path.relative_to(base))


def safe_copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dump_dataclass_json(path: Path, obj: Any) -> None:
    write_json(path, asdict(obj))


def copy_tree(src: Path, dst: Path) -> None:
    """Copy a directory tree from src to dst (overwrite)."""
    if dst.exists():
        # remove existing to avoid stale files; best-effort
        for p in list(dst.rglob("*")):
            try:
                if p.is_file() or p.is_symlink():
                    p.unlink()
            except Exception:
                pass
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        out = dst / rel
        if p.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, out)
