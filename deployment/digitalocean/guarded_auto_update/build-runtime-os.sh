#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
GUI_ROOT="$ROOT/hhs_gui"
if [[ -n "${HHS_RUNTIME_OS_BUILD_ROOT:-}" ]]; then
  OUTPUT_ROOT=$HHS_RUNTIME_OS_BUILD_ROOT
elif [[ "$(realpath -m "$ROOT")" == "/opt/hhs/app" ]]; then
  OUTPUT_ROOT=/var/lib/hhs/runtime-os/dist
else
  OUTPUT_ROOT="$GUI_ROOT/dist"
fi

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

if [[ "$OUTPUT_ROOT" != "$GUI_ROOT/dist" ]]; then
  install -d -m 0755 "$(dirname "$OUTPUT_ROOT")" "$OUTPUT_ROOT"
fi

pushd "$GUI_ROOT" >/dev/null
npm ci --no-audit --no-fund
npm run typecheck
npm run build -- --outDir "$OUTPUT_ROOT" --emptyOutDir
popd >/dev/null

[[ -s "$OUTPUT_ROOT/index.html" ]] || {
  echo "Runtime OS build did not produce $OUTPUT_ROOT/index.html" >&2
  exit 1
}
[[ -d "$OUTPUT_ROOT/assets" ]] || {
  echo "Runtime OS build did not produce $OUTPUT_ROOT/assets" >&2
  exit 1
}
grep -Fq 'HHS Visual Runtime OS Workspace' "$OUTPUT_ROOT/index.html" || {
  echo "Runtime OS build identity missing from $OUTPUT_ROOT/index.html" >&2
  exit 1
}
grep -Fq '/assets/index-' "$OUTPUT_ROOT/index.html" || {
  echo "Runtime OS hashed application bundle missing from $OUTPUT_ROOT/index.html" >&2
  exit 1
}

# Generated browser assets are public read-only deployment material. Keep the
# source checkout immutable while allowing the unprivileged HHS service to read
# the external DigitalOcean asset tree.
chmod -R a+rX "$OUTPUT_ROOT"

printf 'Runtime OS production assets built from %s into %s\n' \
  "$(git -C "$ROOT" rev-parse HEAD)" "$OUTPUT_ROOT"
