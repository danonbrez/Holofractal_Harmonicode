#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
GUI_ROOT="$ROOT/hhs_gui"

cd "$ROOT"

command -v node >/dev/null || {
  echo "node is required to build the canonical HHS Runtime OS" >&2
  exit 1
}
command -v npm >/dev/null || {
  echo "npm is required to build the canonical HHS Runtime OS" >&2
  exit 1
}
[[ -f "$GUI_ROOT/package.json" ]] || {
  echo "Runtime OS package.json missing: $GUI_ROOT/package.json" >&2
  exit 1
}
[[ -f "$GUI_ROOT/package-lock.json" ]] || {
  echo "Runtime OS package-lock.json missing: $GUI_ROOT/package-lock.json" >&2
  exit 1
}

pushd "$GUI_ROOT" >/dev/null
npm ci --no-audit --no-fund
npm run typecheck
npm run build
popd >/dev/null

[[ -s "$GUI_ROOT/dist/index.html" ]] || {
  echo "Runtime OS build did not produce dist/index.html" >&2
  exit 1
}
[[ -d "$GUI_ROOT/dist/assets" ]] || {
  echo "Runtime OS build did not produce dist/assets" >&2
  exit 1
}
grep -Fq 'HHS Visual Runtime OS Workspace' "$GUI_ROOT/dist/index.html" || {
  echo "Runtime OS build identity missing from dist/index.html" >&2
  exit 1
}
grep -Fq '/assets/index-' "$GUI_ROOT/dist/index.html" || {
  echo "Runtime OS hashed application bundle missing from dist/index.html" >&2
  exit 1
}

printf 'Runtime OS production assets built from %s\n' "$(git -C "$ROOT" rev-parse HEAD)"
