#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

ROOT=${1:-$(pwd)}
GUI_ROOT="$ROOT/hhs_gui"
LIVE_ROOT=$(realpath -m "$ROOT")
if [[ -n "${HHS_RUNTIME_OS_BUILD_ROOT:-}" ]]; then
  OUTPUT_ROOT=$HHS_RUNTIME_OS_BUILD_ROOT
elif [[ "$LIVE_ROOT" == "/opt/hhs/app" ]]; then
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

if [[ "$LIVE_ROOT" == "/opt/hhs/app" ]]; then
  [[ $EUID -eq 0 ]] || {
    echo "DigitalOcean production Runtime OS build must run as root" >&2
    exit 1
  }
  CANONICAL_SERVICE="$ROOT/deploy/digitalocean/hhs-pass196-integrated-environment.service"
  [[ -f "$CANONICAL_SERVICE" ]] || {
    echo "Canonical HHS service missing: $CANONICAL_SERVICE" >&2
    exit 1
  }
  install -m 0644 "$CANONICAL_SERVICE" /etc/systemd/system/hhs.service
fi

if [[ "$OUTPUT_ROOT" != "$GUI_ROOT/dist" ]]; then
  install -d -m 0755 "$(dirname "$OUTPUT_ROOT")" "$OUTPUT_ROOT"
fi

pushd "$GUI_ROOT" >/dev/null
# This frontend currently has no committed lockfile. Match the already-proven
# Runtime OS CI path instead of pretending npm ci has a lockfile authority that
# does not exist. If a lockfile is deliberately added later, that can become a
# separately reviewed reproducibility contract.
npm install --no-audit --no-fund
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
