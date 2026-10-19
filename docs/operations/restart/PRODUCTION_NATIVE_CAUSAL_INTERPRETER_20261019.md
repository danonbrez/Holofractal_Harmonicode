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

## Concurrent production validation, hydration and optimizer priority invariant

Production validation, inherited Hash216 hydration, parallel/racing candidate search and optimizer execution are **one integrated delivery graph**, not mutually exclusive projects or independent authority lanes.

1. **Authority before speed:** All racing and optimization workers are candidate-only. They may derive and rank hydrated constructors concurrently, but canonical commit/mint/persistence passes only through the inherited signed VM81/Hash72/Hash216 execution path. Never bypass a failed native/ethical/security gate to improve latency or make UI acceptance appear green.
2. **Hydration before recomputation:** Resolve admitted reusable state and proof relationships from inherited Lane 1–4/Hash216 ancestry before expensive recomputation. Preserve phase and ordered operator provenance. A cache hit must reproduce the same externally observable typed result and receipt lineage; stale/incomplete hydration is an explicit failure, not fallback authorization.
3. **Nonblocking parallel validation:** Run dependency-independent scoped proofs, performance calibration and browser checks concurrently where safe; serialize only operations sharing canonical state, production mutation, promotion locks or a receipt clock. Racing candidate completion order cannot change the deterministic selected/committed result unless an existing native selection contract explicitly permits it.
4. **First upstream violation repair:** Missing bindings, service paths, model packages, encoder/decoder fidelity or deployment assets are implementation gaps. Trace against contracts and commit ancestry, fix at the responsible boundary, replay impacted dependency-scoped checks and the final deployed UI-to-native-to-UI acceptance. Do not reinterpret missing wiring as missing mathematics.
5. **Acceptance evidence:** Pair optimized/racing measurements with nonoptimized baseline parity for exact result, source/receipt ancestry, negative bypass tests and deployed Chrome HTTPS result. Report performance separately from correctness. A faster path is inadmissible if any output type, gate, lineage or UI behavior differs.
6. **Scheduling:** Production incident/blocker repairs, hydration fidelity, and optimization regression each remain tracked and executable in parallel when their dependencies permit. A queued external CI job does not prevent a restartable commit; it also does not count as passing acceptance. Promotion remains blocked until every required path is verified.
7. **All warnings/errors:** Determine whether each is an actionable contract, build, environment, provenance, security or performance issue; log cause, affected dependency and remedy. Do not silently waive failures or warnings solely to unblock racing/deployment.

A green backend, microbenchmark or service registry cannot stand in for the fully wired deployed interface. Optimization never overrides native authority or the required production acceptance predicate.

## Native-first production service selection and verified-gap imports

**Default:** Route every production capability through the already available, contract-admitted native HARMONICODE service and inherited hydrated constructors before considering external packages, remote providers, libraries, or model dependencies. Native-first applies to the actual deployed service and user interface, not just a build flag.

External dependencies are **conditionally admissible**, not forbidden outright. Import or provision one only after a documented and executed capability-gap check establishes that no currently admitted native path satisfies the same input/typed-output/observable-result contract under required quality, performance and safety constraints.

Required gap evidence:
- Capability and its exact externally observable input/output contract; user-visible interface workflow and service route.
- Registry/hydration lookup and real native execution attempt using the deployed service identity, pinned native sources, and inherited signed admission where applicable.
- Deterministic failure or measurable insufficiency of the native path, with reproducible command, result/receipt, and upstream contract diagnosis; a missing import in an optional external implementation alone is **not** proof of a native gap.
- Reasoned external choice, exact package/model/version/ABI and permission scope, security and compatibility checks, and a bounded fallback/revocation strategy. External output remains subordinate to native VM81 admission, typed transcription and Hash216 lineage.
- Dependency-scoped negative tests demonstrating that unnecessary external packages are not loaded when the native capability passes; a verified-gap test that triggers only the explicitly authorized import; parity and full browser-to-native-to-UI checks for both applicable paths.

For the existing production causal-language lane, the pinned `transformers` import is a **present implementation requirement**, not a demonstrated universal capability gap. Preserve its current fail-closed production validation until a native-first alternative is shown to meet the same strict generative-chat, serialized-block, type/ABI and interface contracts through end-to-end validation. Do not simply remove the strict import check or substitute canned responses to obtain green deployment.

Decision order:
`native registry + Hash216 hydration → native constructor execution/proof → gap verdict → scoped external import if and only if authorized → decoded observable result → deployed HTTPS/Chromium acceptance`.

Optimization/racing can rank competing *candidate* paths but cannot choose an unadmitted external provider, silence a native proof failure or create an independent canonical commit authority.

## Mandatory repository guidance and service-index investigation (2026-10-19)

Before changing a failing service, production path, hydration, admission, optimizer or frontend integration:
1. Read `AGENTS.md` and follow its mandatory navigation order: `README.md` → `REPOSITORY_INDEX.md` → `REPOSITORY_HASH216_DEPENDENCY_TREE.md` → Lane5 hydrated repository knowledge graph and database receipt → applicable file-link shards and pass-specific contract/restart record. Also consult `ARCHITECTURE.md`, `RUNTIME_FLOW.md`, and `GLOSSARY.md`.
2. Locate the capability in the service registry/index (`hhs_runtime/hhs_service_registry_v1.py`, repository service documentation, generated index and production service registry). Check registered name, ownership, module/function binding, required authority, schema, validators, route and user-facing caller. Do not conflate a service registry entry with working production wiring.
3. Read its historical contract, source implementation, relevant changed commit/PR, dependency ancestry, failing workflow job logs, and deployed artifact identity. Compare each observed boundary in actual UI-to-native-to-UI order, locate the first contract divergence, and repair forward at that owner.
4. Consult hydrated Lane5 capability knowledge before importing external dependencies or designing duplicate services. Preserve singular VM81/Hash72/Hash216 authority, typed ingress/egress, signed receipts, racing determinism and all admitted native constraints.
5. Verify impacted scoped tests, safety and negative tests, relevant integration paths, current-main deployment and full HTTPS/Chromium UI workflows. Produce restartable state/commit/CI/deployment receipt for unresolved work.

Inspection anchors confirmed on main: `AGENTS.md` is the authoritative agent navigation and execution contract; `REPOSITORY_INDEX.md` explicitly declares itself navigational, not runtime authority; `hhs_runtime/hhs_service_registry_v1.py` is a guarded runtime service discovery/dispatch surface. All three must be consulted, but none alone proves that the deployed interface route works.

## Error-code sourced service contract-gap triage (2026-10-19)
- Inspected repository guidance `AGENTS.md`, `REPOSITORY_INDEX.md`, and guarded registry `hhs_runtime/hhs_service_registry_v1.py`; exact ABI enum source `hhs_runtime/include/hhs_runtime_exact_abi_v1_1_base.h` defines statuses 0..5.
- Implemented read-only `hhs_runtime/hhs_service_contract_gap_triage_v1.py` at `bf3318ac5d1cc01b1409e3693f6ed1c66b8a1889`. It preserves exact status code and definition source, requires service identity, origin, observed boundary, contract path and implementation path, generates deterministic replay digest and refuses to assert a root cause, C++ proof, Lane5 hydration or production closure without evidence. Unknown numeric status fail closed; domain codes are kept verbatim with unresolved source marker.
- Scoped test `tests/pass220/test_hhs_service_contract_gap_triage_v1.py` at `338b5075419fbda2a0f60d8fee5f3921f4f1f76f`; CI `.github/workflows/service-contract-gap-triage.yml` at `935f16c0412a3422cd55bc0e560a82a48dec1b63` runs PR and main path-scoped.
- This is a candidate ledger record, not a verified source-code graph resolver, full repository-wide service census, production repair or automated first-violation proof. Next: consume actual deployed/logged error codes, join to service ownership via hydrated Lane5 index, add real native cell-wall and graph proof receipts and full UI validation.
- Preserve previous main-established mathematical proofs, repair only integration/ABI/environment deviations. All previous production blockers remain open pending verified deployment and browser evidence.

## 2026-10-19 service index ↔ Lane5 diagnostic join
- Previous `Service contract gap triage` run 39324900445 completed SUCCESS at checkpoint bae571bb3601cfe2219b0fc17b579306e4578de5 (not the current head).
- Read existing `HHSServiceRegistry.services()` descriptors and `REPOSITORY_INDEX.md` ownership. No alternate registry or independent canonical store introduced.
- Commit `de0f543b2f9fb17aec6474d7880d7673bd49c281` implements read-only `correlate_service_gap` joining a captured native-error triage to service descriptor and externally supplied Lane5 hydration inventory. It retains declared contract/witness/guard schemas and rejects absent/ambiguous service registration or ambiguous graph records. A missing graph identity is explicitly not proof of invalid native mathematics.
- Commit `b9f83fad7311b432b25d110946835c56ddcd9774` tests present, missing, duplicate graph and absent registry cases. CI outstanding for current head.
- Important next implementation: derive the hydration-node schema from the actual generated Lane5 graph/DB interface (rather than generic name/service_name fixture), load *real* deployed registry snapshot, resolve exact native C++ receipt and Hash216 index proof; identify first violated boundary through actual error trace and run browser E2E acceptance. No authoritative signed closure is claimed.
