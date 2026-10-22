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

## 2026-10-22 scoped validation follow-up
- PR #842 checks at original commit 21392c3b: Source Text Integrity, I073–I077 successful; DigitalOcean Production Exact Main parent workflow successful but actual `deploy-exact-main` job **SKIPPED**, therefore production repair not verified.
- Commit `083d63916e134d3a7a19f3ac9cf610673df7bd77` adds synthetic import-error regression, checking failing traceback, stderr, and no ready marker.
- Commit `39d826585b036f172eaef49b1bb47552f59e6094` creates dedicated GitHub Actions workflow for scoped `py_compile` and `pytest` on PR; this executes only diagnostics and does not deploy production or install model weights.
- CI execution on this update is pending until observed. If green, retain draft until actual host service-identity failure traceback is captured and real root cause is repaired. Do not infer production-ready from a skipped deployment.

## 2026-10-22 CI acceptance update
- Exact branch-head CI run 39765751273 (`Production Native Causal Import Diagnostic`): SUCCESS, including Python compile and isolated failure-path regression.
- `HHS Source Text Integrity` run 39765751060 SUCCESS.
- `DigitalOcean Production Exact Main` run 39765751300 parent SUCCESS: `validate-production-backend-closure` SUCCESS, `validate-deployment-contract` SUCCESS, **`deploy-exact-main` SKIPPED**. No live service-identity import or production deployment occurred in this run.
- Diagnostic-only PR #842 remains draft; maintain exact dependency/model pins and fail-closed acceptance. Root cause of original import failure is not yet evidenced by a live failing traceback. Next: controlled exact-main production run under authorized deployment path; inspect diagnostic traceback; repair-forward only demonstrated defect. No unverified production-ready claim.

## CI acceptance receipt — 2026-10-22
- PR #842 head `ea21bc13fcc6d00d217ec7959a67cdf23c3c7841`; targeted diagnostic workflow run `39765751273`, job `119780648659` SUCCESS: `3 passed, 1 warning in 0.25s`. Warning is unknown pytest config `asyncio_mode`, not a diagnostic failure. Compile step succeeded.
- HHS Source Text Integrity `39765751060` SUCCESS.
- DigitalOcean Production Exact Main run `39765751300` overall SUCCESS because `validate-production-backend-closure` and `validate-deployment-contract` succeeded; `deploy-exact-main` job `119786477893` SKIPPED. No production-host service-identity import evidence exists from this check.
- The diagnostic PR is test-validated but the October 21 AutoTokenizer root cause is not established; keep draft and no merge/deploy claim. Next obtain actual exact-main deployment traceback or host evidence, then repair confirmed cause and validate against current main. No additional CI reruns necessary for already green dependency-scoped diagnostic tests.
