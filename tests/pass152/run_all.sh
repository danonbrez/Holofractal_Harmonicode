#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
python3 -m py_compile hhs_runtime/pass152/*.py hhs_backend/api/pass152_elastic_closure_routes.py hhs_backend/server.py tools/hhs152.py
cc -std=c11 -Wall -Wextra -Werror -pedantic hhs_runtime/pass152/hhs152_native.c tests/pass152/test_native.c -o /tmp/hhs152_native_test
/tmp/hhs152_native_test
python3 tests/pass152/run_pass152_tests.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q tests/test_hhs_pass152_universal_elastic_closure_v1.py
node --check hhs_gui/spatial_environment/src/runtime-bridge.js
node --check hhs_gui/spatial_environment/src/application-registry.js
node --check hhs_gui/spatial_environment/src/ui-shell.js
