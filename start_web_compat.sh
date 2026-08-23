#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[HHS] DEPRECATED: browser frontend is compatibility/remote projection only." >&2
echo "[HHS] Preferred local entrypoint: bash start_vm.sh" >&2
echo "[HHS] Primary machine/API entrypoint: bash start_api.sh" >&2
exec bash "${ROOT_DIR}/start.sh" "$@"
