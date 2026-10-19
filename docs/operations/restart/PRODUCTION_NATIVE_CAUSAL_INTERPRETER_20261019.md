# Integrated production native-causal interpreter repair checkpoint — 2026-10-19

- Base and merge target: main. Production promotion remains unverified after main a8f41e0a in latest supplied acceptance evidence.
- Scope: native-chat exit 27, `AutoTokenizer` failure under the actual service identity; preserve pinned `transformers==4.57.6`, native model revision, signed VM81 and native-chat strict acceptance.
- Source `tools/diagnose_native_causal_interpreter.py` commit `3a85f527c277b49704531877ba66c26757ac6a65`: read-only sys.executable, sys.prefix, module spec locations and import error diagnostics. No model downloads, no fallback, no environment secrets.
- Deployment source `.github/workflows/digitalocean-production-main.yml` commit `965f36e3dc0d8e950f4ab36e313fb6dbf9a476ef`: execute diagnostic with `runuser -u hhs` and `/opt/hhs/venv/bin/python` before existing strict import check; fail exit 27 if still broken.
- Test `tests/pass220/test_native_causal_interpreter_diagnostic.py` commit `e2e6a2218ef7fd4d6bf8cf2bc2fde65437e7bb53`.
- Validation outstanding: scoped local/CI test, deployed service interpreter output, package export resolution, pinned model generation with distinct responses, native-chat serialized blocks, HTTPS/Chromium screenshot/browser evidence.
- No live production change has been made; this is diagnostic repair-forward, not accepted delivery.
- Other blockers remain separately tracked: #825 ERS identity/angle/Wolfram verification; Lean Fin81 and divisor gate; parser malformed operators; #826 ordered graph safety; #827 mixed-language cell-wall linker repair. Failed workflow evidence must be repaired in branch and replayed. No warnings silently waived.

## Mandatory deployed interface-to-native end-to-end acceptance

Production acceptance is conjunctive across **all required user-visible services and workflows**, not a collection of disconnected green service checks. For every exposed workflow, execute the actual deployed Chromium/HTTPS interface with the deployed frontend assets and route a real request through browser action → frontend handler → external HTTPS ingress → API route → service dispatcher → native VM81/Hash72/Hash216 or other contractually authorized execution → receipt/output decode → UI-visible result. Capture a per-workflow trace containing source/target SHA, deployed asset identity, HTTP request/response and route, service identity, native execution/receipt evidence, output type/ABI, UI rendered result, and browser artifact. Do not claim native admission on routes that are explicitly read-only.

**First upstream contract violation rule:** Compare each boundary's observed input/output to the authoritative versioned contract and commit ancestry in order. If backend first violates API, native proof, identity or output contract, repair backend; if backend satisfies its contract but UI sends the wrong endpoint/schema or renders incorrectly, repair interface. For host-only dependency, reverse proxy, TLS, permissions, asset drift, or deployment bundle issues, repair the relevant deployment boundary. If contracts conflict, reconcile the highest-authority source before any weakening. Negative/bypass tests must be applied to the boundary changed.

**Acceptance gate:** no release acceptance unless all required routes work in the real deployed UI with meaningful outputs, no silent fallback/mock/static shell substitutes, integrity/typed decoding proven, and HTTPS+Chromium evidence plus native receipts preserved. Fail closed for missing screenshots/browser artifact or any unresolved material warning. Local/unit and detached endpoint checks are supplementary only.

**Existing partial evidence is insufficient:** PR #831 diagnoses production interpreter imports, but does not prove repaired chat, visual interface integration, or deployment. Run required contract inventory to identify all user-visible services and wire tests before claiming complete acceptance.
