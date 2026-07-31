#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
make -C native_projects/hhs_pass183_probability_hydration clean test
python3 -m py_compile hhs_runtime/pass183/*.py hhs_backend/api/probability_hydration_routes.py
python3 -m pytest -q tests/test_pass183_probability_hydration.py tests/test_pass183_api_and_studio.py
python3 tests/pass183_acceptance_harness.py --output native_projects/hhs_pass183_probability_hydration/evidence/PASS_183_COMPLETION.json
test -s applications/probability_hydration_studio/index.html
test -s applications/probability_hydration_studio/app.js
test -s applications/probability_hydration_studio/styles.css
grep -q "Probability Equation Hydration" applications/probability_hydration_studio/index.html
grep -q "api/v1/probability" hhs_backend/api/probability_hydration_routes.py
echo HHS_PASS_183_PROBABILITY_EQUATION_HYDRATION_MEMBRANE_RUNTIME_VERIFIED
