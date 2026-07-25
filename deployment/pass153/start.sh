#!/bin/sh
set -eu
exec python -m uvicorn hhs_backend.pass153_server:app --host "${HHS_HOST:-0.0.0.0}" --port "${PORT:-8000}"
