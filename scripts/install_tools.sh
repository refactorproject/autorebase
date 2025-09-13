#!/usr/bin/env bash
set -euo pipefail

echo "[auto-rebase] Tool installer (best-effort)." 
OS="$(uname -s || echo unknown)"
echo "Detected OS: $OS"

need() { command -v "$1" >/dev/null 2>&1 || return 0; echo "$1 present"; }

echo "Checking optional tools..."
for t in git difftastic gumtree clang-tidy coccinelle spatch dtc yq comby; do
  if command -v "$t" >/dev/null 2>&1; then
    echo " - $t: present"
  else
    echo " - $t: missing (will fallback at runtime)"
  fi
done

echo "Done."

