#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
INSTALL_MODE="${HHS_VULKAN_INSTALL_MODE:-install}"
INSTALL_TOOLS="${HHS_VULKAN_INSTALL_TOOLS:-1}"
RUNTIME_ROOT="${HHS_VULKAN_RUNTIME_ROOT:-${ROOT_DIR}/.hhs/runtime/graphics/vulkan}"
export HHS_VULKAN_RUNTIME_ROOT="$RUNTIME_ROOT"
export PYTHONPATH="${ROOT_DIR}${PYTHONPATH:+:${PYTHONPATH}}"

usage() {
  cat <<'EOF'
Usage: tools/install_vulkan_loader.sh [--verify-only] [--no-tools]

Installs the platform Vulkan loader package when required, stages the resolved
libvulkan.so.1 into the HHS runtime graphics tree, and writes a receipt plus an
environment file. GPU vendor drivers and device access remain host concerns.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --verify-only) INSTALL_MODE="verify-only" ;;
    --no-tools) INSTALL_TOOLS="0" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "[HHS] Unknown Vulkan installer argument: $1" >&2; usage >&2; exit 64 ;;
  esac
  shift
done

run_privileged() {
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo "$@"
  else
    echo "[HHS] Installing the Vulkan loader requires root or sudo: $*" >&2
    return 77
  fi
}

loader_ready() {
  "$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 \
    --require-loader >/dev/null 2>&1
}

install_packages() {
  local loader_packages=()
  local tools_packages=()

  if command -v apt-get >/dev/null 2>&1; then
    loader_packages=(libvulkan1)
    tools_packages=(vulkan-tools)
    if [[ "${HHS_VULKAN_SKIP_PACKAGE_INDEX_UPDATE:-0}" != "1" ]]; then
      run_privileged apt-get update
    fi
    run_privileged env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      "${loader_packages[@]}" $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  elif command -v dnf >/dev/null 2>&1; then
    loader_packages=(vulkan-loader)
    tools_packages=(vulkan-tools)
    run_privileged dnf install -y "${loader_packages[@]}" \
      $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  elif command -v yum >/dev/null 2>&1; then
    loader_packages=(vulkan-loader)
    tools_packages=(vulkan-tools)
    run_privileged yum install -y "${loader_packages[@]}" \
      $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  elif command -v pacman >/dev/null 2>&1; then
    loader_packages=(vulkan-icd-loader)
    tools_packages=(vulkan-tools)
    run_privileged pacman -Sy --noconfirm --needed "${loader_packages[@]}" \
      $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  elif command -v apk >/dev/null 2>&1; then
    loader_packages=(vulkan-loader)
    tools_packages=(vulkan-tools)
    run_privileged apk add --no-cache "${loader_packages[@]}" \
      $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  elif command -v zypper >/dev/null 2>&1; then
    loader_packages=(libvulkan1)
    tools_packages=(vulkan-tools)
    run_privileged zypper --non-interactive install "${loader_packages[@]}" \
      $([[ "$INSTALL_TOOLS" == "1" ]] && printf '%s ' "${tools_packages[@]}")
  else
    echo "[HHS] No supported Linux package manager found for Vulkan loader installation" >&2
    return 69
  fi

  if command -v ldconfig >/dev/null 2>&1; then
    run_privileged ldconfig || true
  fi
}

system_name="$(uname -s 2>/dev/null || printf unknown)"
case "$system_name" in
  Linux) ;;
  Android)
    echo "[HHS] Android supplies its Vulkan loader through the OS"
    exec "$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 --require-loader
    ;;
  Darwin)
    echo "[HHS] macOS LiteRT-LM GPU execution uses Metal; no Linux Vulkan loader installed"
    exec "$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1
    ;;
  *)
    echo "[HHS] This installer provisions the Linux Vulkan loader; detected ${system_name}" >&2
    exit 69
    ;;
esac

if loader_ready; then
  echo "[HHS] Vulkan loader already available"
elif [[ "$INSTALL_MODE" == "verify-only" ]]; then
  echo "[HHS] Vulkan loader verification failed and installation is disabled" >&2
  exit 1
else
  echo "[HHS] Installing Vulkan loader packages for the native graphics runtime"
  install_packages
fi

mkdir -p "$RUNTIME_ROOT"
"$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 \
  --stage \
  --require-loader

echo "[HHS] Vulkan loader staged under ${RUNTIME_ROOT}"
