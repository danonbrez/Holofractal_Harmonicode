# Integrated production native-causal interpreter repair checkpoint — 2026-10-19

- Base and merge target: main. Production promotion remains unverified after main a8f41e0a in latest supplied acceptance evidence.
- Scope: native-chat exit 27, `AutoTokenizer` failure under the actual service identity; preserve pinned `transformers==4.57.6`, native model revision, signed VM81 and native-chat strict acceptance.
- Source `tools/diagnose_native_causal_interpreter.py` commit `3a85f527c277b49704531877ba66c26757ac6a65`: read-only sys.executable, sys.prefix, module spec locations and import error diagnostics. No model downloads, no fallback, no environment secrets.
- Deployment source `.github/workflows/digitalocean-production-main.yml` commit `965f36e3dc0d8e950f4ab36e313fb6dbf9a476ef`: execute diagnostic with `runuser -u hhs` and `/opt/hhs/venv/bin/python` before existing strict import check; fail exit 27 if still broken.
- Test `tests/pass220/test_native_causal_interpreter_diagnostic.py` commit `e2e6a2218ef7fd4d6bf8cf2bc2fde65437e7bb53`.
- Validation outstanding: scoped local/CI test, deployed service interpreter output, package export resolution, pinned model generation with distinct responses, native-chat serialized blocks, HTTPS/Chromium screenshot/browser evidence.
- No live production change has been made; this is diagnostic repair-forward, not accepted delivery.
- Other blockers remain separately tracked: #825 ERS identity/angle/Wolfram verification; Lean Fin81 and divisor gate; parser malformed operators; #826 ordered graph safety; #827 mixed-language cell-wall linker repair. Failed workflow evidence must be repaired in branch and replayed. No warnings silently waived.
