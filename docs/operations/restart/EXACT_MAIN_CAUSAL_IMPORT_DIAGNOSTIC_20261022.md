# Exact-main causal import diagnostic checkpoint — 2026-10-22

- Base main SHA: `3aa0cd4415e5970abd518fcbca547d0dc2c322e3`.
- Working branch: `fix/production-causal-import-diagnostics-20261022`; merge target: `main`.
- Source inspection: `tools/provision_native_causal_model.py` and `.github/workflows/digitalocean-production-main.yml`.
- Observed workflow already runs pinned preflight and --install under `/opt/hhs/venv/bin/python`; next checks transformers AutoTokenizer, AutoModelForCausalLM and torch under service identity `hhs`.
- Exact October 21 failed deployment job logs were **not retrievable** with available connected GitHub workflow tooling. Root cause is **not established**. No extra install, model/version changes or package speculation introduced.
- Commit `beb1d0484c8a0eea593a49b1b10fa8228a7addd3`: added `tools/diagnose_native_causal_import.py`, fail-closed, prints executable, effective UID, selected installed package versions and complete traceback on error, no environment contents or secrets.
- Commit `05e79532d8c462d3718e0a12b131dc909f6158ee`: deployment switches **only** the existing service-identity import command to diagnostic script; keeps identical import obligations and exit 27 on failure.
- Commit `5bc8780f6852acd0e1dd67f27175f9f74f3bcd64`: dependency-scoped contract tests `tests/production/test_native_causal_import_diagnostics.py`.
- Validation: static source inspected. Run `python -m pytest -q tests/production/test_native_causal_import_diagnostics.py` and `python -m py_compile tools/diagnose_native_causal_import.py` before integration; neither command executed in connected repository environment in this conversation. No production deployment verified.
- Next action: execute scoped validation, open PR, obtain failed production import trace from next controlled deployment run, then repair only the confirmed root cause. Preserve pinned versions, model SHA, VM81/Hash72/Hash216 authority, exact-main acceptance and fail-closed behavior.
- Changed files: `tools/diagnose_native_causal_import.py`, `.github/workflows/digitalocean-production-main.yml`, `tests/production/test_native_causal_import_diagnostics.py`, this checkpoint.
