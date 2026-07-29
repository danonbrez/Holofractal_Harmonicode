#!/usr/bin/env sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
PYTHON_BIN=${PYTHON_BIN:-python3}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  printf '%s\n' 'P172_PYTHON_NOT_FOUND: install Python 3.11 or use a verified offline bundle containing it' >&2
  exit 2
fi

exec "$PYTHON_BIN" "$ROOT/hhs-bootstrap.py" install "$@"
