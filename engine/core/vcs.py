from __future__ import annotations

from pathlib import Path
from typing import Optional
import os
import tempfile
import difflib

from .utils import which, run_cmd, list_files, rel_to, ensure_dir


def commit_and_tag(path: Path, tag: str, trailers: dict[str, str]) -> None:
    """Create a git commit with trailers and tag it. Best-effort if git present."""

    if not which("git"):
        return
    try:
        run_cmd(["git", "init"], cwd=path)
        run_cmd(["git", "add", "."], cwd=path)
        message = "Auto-Rebase finalize\n\n" + "\n".join(f"{k}: {v}" for k, v in trailers.items())
        run_cmd(["git", "commit", "-m", message], cwd=path)
        run_cmd(["git", "tag", tag], cwd=path)
    except Exception:
        # Best-effort only
        pass


def git_diff_no_index(old: Path, new: Path, out_patch: Path) -> None:
    """Create a unified diff between two directories using git --no-index.

    To get stable, relative paths that apply with -p1, we symlink both trees
    into a temp dir as 'a' and 'b' and diff those.
    """
    if not which("git"):
        raise RuntimeError("git not available for diff generation")
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        a = tdp / "a"
        b = tdp / "b"
        try:
            os.symlink(old.resolve(), a)
            os.symlink(new.resolve(), b)
        except Exception:
            # Fallback: create directories and copy minimal structure
            a.mkdir()
            b.mkdir()
        code, out, err = run_cmd(["git", "diff", "--no-index", "a", "b"], cwd=tdp, check=False)
        # git diff exits 1 when there are differences; treat 0/1 as success
        if code not in (0, 1):
            raise RuntimeError(f"git diff failed: {err}")
        out_patch.parent.mkdir(parents=True, exist_ok=True)
        out_patch.write_text(out, encoding="utf-8")


def git_apply_reject(patch_path: Path, target_dir: Path, strip: int = 1) -> None:
    """Apply a patch to target_dir using git apply with --reject.

    strip controls -pN path stripping (defaults to 1 for a/ and b/).
    Generates .rej files for rejected hunks.
    """
    if not which("git"):
        raise RuntimeError("git not available for patch apply")
    args = ["git", "apply", f"-p{strip}", "--reject", "--no-3way", str(patch_path)]
    code, out, err = run_cmd(args, cwd=target_dir, check=False)
    if code != 0:
        # Even with rejects, git apply may return non-zero; continue but surface stderr in logs
        pass


def unified_diff_text(a_path: Path, b_path: Path, rel: str | None = None) -> str:
    """Return unified diff between two files using `diff -u` if available, else difflib.

    Returns empty string if files are identical. If one side is missing, uses /dev/null when shelling
    out, or difflib with empty content.
    """
    has_diff = bool(which("diff"))
    a_exists = a_path.exists()
    b_exists = b_path.exists()
    if has_diff and (a_exists or b_exists):
        a_arg = str(a_path) if a_exists else "/dev/null"
        b_arg = str(b_path) if b_exists else "/dev/null"
        code, out, err = run_cmd(["diff", "-u", a_arg, b_arg], check=False)
        if code == 0:
            return ""
        if code in (1,):
            # Replace absolute paths with relative paths in the diff output
            if rel:
                out = out.replace(str(a_path), f"a/{rel}")
                out = out.replace(str(b_path), f"b/{rel}")
            return out
        # On other failures, fall back to difflib
    a_txt = a_path.read_text(encoding="utf-8") if a_exists else ""
    b_txt = b_path.read_text(encoding="utf-8") if b_exists else ""
    fromfile = f"a/{rel or a_path.name}"
    tofile = f"b/{rel or b_path.name}"
    return "".join(difflib.unified_diff(a_txt.splitlines(True), b_txt.splitlines(True), fromfile=fromfile, tofile=tofile))


def generate_per_file_patches(old_root: Path, new_root: Path, out_dir: Path) -> list[Path]:
    """Generate per-file unified diff patches under out_dir mirroring the tree structure.

    - For files only in new_root, diff /dev/null vs new file (additions)
    - For files only in old_root, diff old vs /dev/null (deletions)
    - For files in both, diff their contents
    Writes each patch as `<out_dir>/<rel>.patch` if there is a difference.
    Returns list of written patch paths.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    old_files = {rel_to(p, old_root): p for p in list_files(old_root)}
    new_files = {rel_to(p, new_root): p for p in list_files(new_root)}
    rels = sorted(set(old_files.keys()) | set(new_files.keys()))
    written: list[Path] = []
    for rel in rels:
        a = old_files.get(rel, old_root / rel)
        b = new_files.get(rel, new_root / rel)
        diff_txt = unified_diff_text(a, b, rel=rel)
        if not diff_txt.strip():
            continue
        patch_path = out_dir / f"{rel}.patch"
        ensure_dir(patch_path.parent)
        patch_path.write_text(diff_txt, encoding="utf-8")
        written.append(patch_path)
    return written


def apply_patch_dir_with_reject(patch_dir: Path, target_dir: Path, strip: int = 1) -> list[Path]:
    """Apply all .patch files under patch_dir (recursively) using git apply --reject.

    Returns a list of .rej files produced. Continues on errors to accumulate rejects.
    """
    if not which("git"):
        raise RuntimeError("git not available for patch apply")
    patches = sorted(patch_dir.rglob("*.patch"))
    for p in patches:
        code, out, err = run_cmd(["git", "apply", f"-p{strip}", "--reject", "--no-3way", str(p)], cwd=target_dir, check=False)
        # proceed regardless; .rej will indicate failures
    return list(target_dir.rglob("*.rej"))
