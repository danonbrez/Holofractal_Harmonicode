# Pass 220 exact source-to-proof candidate guard — restart checkpoint

Date: 2026-10-26

Base main: `966f2929f18fff117a73665b68b2453375d33206`

Branch: `pass220/exact-source-proof-binding-guard-20261026`

Target: `main`

## Scope

Add a source-preserving, read-only resolver for exact equation bytes and an
already-existing proof registry record. No new mathematical proof, operator
semantics, VM81 admission, Hash72 mint, Hash216 persistence or production
mutation. Existing `require_native_proof_binding` remains the authority
preflight; it does not independently authenticate untrusted receipt strings.

## Changed files

- `hhs_runtime/hhs_pass220_exact_source_proof_binding_candidate_v1.py`
- `tests/pass220/test_hhs_pass220_exact_source_proof_binding_candidate_v1.py`
- This restart record.

## Required validation

```sh
python -m py_compile hhs_runtime/hhs_pass220_exact_source_proof_binding_candidate_v1.py tests/pass220/test_hhs_pass220_exact_source_proof_binding_candidate_v1.py
PYTHONPATH=. python -m pytest -q tests/pass220/test_hhs_pass220_exact_source_proof_binding_candidate_v1.py tests/pass220/test_pass220_whitepaper_corpus_ingress_v1.py
```

## Current status and limitations

Implementation and targeted tests are committed through the GitHub connector.
No local checkout, Python test run, native ABI test, CI result, deployment,
production promotion, or verified-main completion is claimed.

The resolver takes an explicit list of audited candidate records; it does not
automatically register the four newest expression sources or assert that their
verbatim byte strings already occur in the proof registry.

A passed status and nonempty receipt reference remain *candidate* metadata,
not independently authenticated native evidence. Full admission requires a
trusted registry origin, native receipt authentication and VM81 proof gate.

## Restart instructions

Inspect PR/head checks, run the listed focused tests, repair forward if needed,
then bind the user-supplied exact expression byte sources only after identifying
their existing authoritative proof IDs and authenticated receipts. Do not
guess proof ancestry or change the current main production delivery gate.
