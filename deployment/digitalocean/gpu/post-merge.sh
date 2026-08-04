#!/usr/bin/env bash
set -Eeuo pipefail
umask 027

REPO_ROOT=${HHS_REPO_ROOT:-${HHS_REPOSITORY_ROOT:-/opt/hhs/app}}
PYTHON=${HHS_PASS208_PYTHON:-/opt/hhs/venv/bin/python}

cd "$REPO_ROOT"

if [[ -f bin/post_compile ]]; then
  bash bin/post_compile
fi

PYTHONPATH="$REPO_ROOT${PYTHONPATH:+:$PYTHONPATH}" \
"$PYTHON" -c \
  'from hhs_python.runtime.hhs_pass207_gpu_driver_native import build_native_library; print(build_native_library(force=True))'

[[ -s hhs_runtime/builds/libhhs_pass207_gpu_driver.so ]] || {
  echo "Pass 207 GPU driver library was not produced" >&2
  exit 1
}

/usr/local/lib/hhs-gpu/hhs-gpu-preflight.sh
