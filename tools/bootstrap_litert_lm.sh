#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${HHS_LITERT_LM_VENV_DIR:-${ROOT_DIR}/.hhs/litert-lm/venv}"
REQ_FILE="${HHS_LITERT_LM_REQUIREMENTS:-${ROOT_DIR}/requirements-litert-lm.txt}"
LOCAL_BIN="${VENV_DIR}/bin/litert-lm"
MODE="${1:---install}"

log() {
  printf '%s\n' "[HHS] $*" >&2
}

check_python() {
  "$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 10):
    raise SystemExit(
        f"LiteRT-LM requires Python 3.10 or newer; found {sys.version.split()[0]}"
    )
PY
}

resolve_existing() {
  if [[ -n "${HHS_LITERT_LM_BIN:-}" ]]; then
    if [[ ! -x "${HHS_LITERT_LM_BIN}" ]]; then
      log "HHS_LITERT_LM_BIN is not executable: ${HHS_LITERT_LM_BIN}"
      return 1
    fi
    printf '%s\n' "${HHS_LITERT_LM_BIN}"
    return 0
  fi

  if [[ -x "$LOCAL_BIN" ]]; then
    printf '%s\n' "$LOCAL_BIN"
    return 0
  fi

  if command -v litert-lm >/dev/null 2>&1; then
    command -v litert-lm
    return 0
  fi

  return 1
}

install_local() {
  check_python
  if [[ ! -f "$REQ_FILE" ]]; then
    log "missing LiteRT-LM requirements file: $REQ_FILE"
    return 1
  fi

  log "Installing repository-local LiteRT-LM runtime"
  log "Environment: $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --upgrade pip
  "$VENV_DIR/bin/python" -m pip install --requirement "$REQ_FILE"

  if [[ ! -x "$LOCAL_BIN" ]]; then
    log "installation completed without creating $LOCAL_BIN"
    return 1
  fi

  "$LOCAL_BIN" --version >&2
  printf '%s\n' "$LOCAL_BIN"
}

case "$MODE" in
  --print-bin)
    if resolve_existing; then
      exit 0
    fi
    install_local
    ;;
  --verify)
    BIN="$(resolve_existing)" || {
      log "LiteRT-LM is not installed"
      exit 127
    }
    "$BIN" --version
    ;;
  --install)
    if BIN="$(resolve_existing)"; then
      log "Using LiteRT-LM executable: $BIN"
      "$BIN" --version >&2
      printf '%s\n' "$BIN"
    else
      install_local
    fi
    ;;
  *)
    log "usage: $0 [--install|--verify|--print-bin]"
    exit 64
    ;;
esac
