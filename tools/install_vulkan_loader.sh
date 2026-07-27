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
  local manager="$1"
  shift
  local packages=("$@")
  case "$manager" in
    apt)
      if [[ "${HHS_VULKAN_SKIP_PACKAGE_INDEX_UPDATE:-0}" != "1" ]]; then
        run_privileged apt-get update
      fi
      run_privileged env DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends "${packages[@]}"
      ;;
    dnf) run_privileged dnf install -y "${packages[@]}" ;;
    yum) run_privileged yum install -y "${packages[@]}" ;;
    pacman) run_privileged pacman -Sy --noconfirm --needed "${packages[@]}" ;;
    apk) run_privileged apk add --no-cache "${packages[@]}" ;;
    zypper) run_privileged zypper --non-interactive install "${packages[@]}" ;;
    *) echo "[HHS] Unsupported Vulkan package manager adapter: $manager" >&2; return 69 ;;
  esac
}

install_distribution_loader() {
  local manager=""
  local packages=()

  if command -v apt-get >/dev/null 2>&1; then
    manager="apt"
    packages=(libvulkan1)
  elif command -v dnf >/dev/null 2>&1; then
    manager="dnf"
    packages=(vulkan-loader)
  elif command -v yum >/dev/null 2>&1; then
    manager="yum"
    packages=(vulkan-loader)
  elif command -v pacman >/dev/null 2>&1; then
    manager="pacman"
    packages=(vulkan-icd-loader)
  elif command -v apk >/dev/null 2>&1; then
    manager="apk"
    packages=(vulkan-loader)
  elif command -v zypper >/dev/null 2>&1; then
    manager="zypper"
    packages=(libvulkan1)
  else
    echo "[HHS] No supported Linux package manager found for Vulkan loader installation" >&2
    return 69
  fi

  if [[ "$INSTALL_TOOLS" == "1" ]]; then
    packages+=(vulkan-tools)
  fi
  install_packages "$manager" "${packages[@]}"

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
  install_distribution_loader
fi

mkdir -p "$RUNTIME_ROOT"
"$PYTHON_BIN" -m hhs_backend.runtime.hhs_vulkan_loader_runtime_v1 \
  --stage \
  --require-loader

echo "[HHS] Vulkan loader staged under ${RUNTIME_ROOT}"
