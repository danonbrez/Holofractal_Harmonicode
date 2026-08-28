# Pass 219 I126 — repaired inherited Pass 200A exposure

## Census classification

`INHERITED_IMPLEMENTATION_REPAIR_AND_MEMBRANE_EXPOSURE`

Pass 200A was not missing as an implementation. PR #138 had been accepted and merged, but its post-merge review identified eight defects that remained present at frozen I125. I126 therefore does not classify Pass 200A as `MISSING_MEMBRANE_EXPOSURE`.

Historical accepted identity remains immutable:

- original base: `649be68e1566002ce66c919463a386b8018bc2fb`
- reviewed historical head: `5ef1d3ab6c0ceb3a20d468447b991066626de366`
- accepted squash merge: `eee6670f7d3c6743e1bf32c7e42a4150d07351e3`
- frozen predecessor I125: `21bf16233a0c4573a754c29686d13782bcc4fc44`
- historical V1 runtime blob retained byte-exactly: `1f6d7b0092da3916705a58af9ae2ad2c22c3bab3`

## Repair-forward boundary

I126 adds `hhs_pass200a_proof_carrying_optimization_v2.py` as the corrected canonical production authority. The accepted V1 runtime remains historical provenance rather than being rewritten.

The repair closes review findings `3700651637` through `3700651644`:

1. The compiled B/candidate lane is actually evaluated with the inherited exact Pass199/Pass197 branch evaluator instead of copying the reference root and hardcoding equality.
2. Pass 200A mutation receipts must be present in a fully verified unified `RUNTIME_RECEIPT` Hash72 chain emitted by `HHSRuntimeController.commit_receipt`; 72-character shape alone is rejected.
3. Persisted shadow payloads have their `shadow_hash72` recomputed, and only rows whose hash is also bound in the corresponding append-only Pass 200A event can qualify closure.
4. Every bundle is re-bound to the current Pass198 simplification; stale, revoked, missing, or proof-hash-drifted compiler candidates are rejected.
5. Production closure requires the exact default four holdout identities and exact acceptance totals: 290 parameter states, 580 A/B jobs, 263 admitted states, 27 domain rejections, 1,363,392 VM5184 comparisons, 24 negative mutations, four bundles, four shadow matches, four reference returns, and zero candidate activations. A custom four-state test profile cannot claim production closure.
6. The historical V1 singleton is upgraded in place to the V2 class. The canonical production wrapper does not construct a second authority against the same SQLite/Pass199 state root.
7. Canonical bundle listing uses `simplification_id`, eliminating the historical V1 `ORDER BY name` table-column failure from the production surface.
8. One to three persisted holdout envelopes remain a recoverable `HHS_PASS_200A_IN_PROGRESS` state rather than raising a status exception.

## Exact shadow semantics

For each bundle and invocation I126 executes branch A and branch B independently, then repeats both as an independent deterministic replay. Closure requires equality of exact semantic roots, address-witness roots, and replay roots. A mismatch is persisted as `MISMATCH` and still returns the reference path.

The candidate lane remains non-authoritative:

- candidate may commit: **false**
- candidate may activate: **false**
- compiler auto-activation: **false**
- runtime auto-admission: **false**
- canary: **false**
- active: **false**
- frozen constraint: **false**
- returned path: **REFERENCE**

Pass 200B remains the immediate successor and retains all canary admission authority under its own frozen contract.

## Pass 219 exposure

C:

- `HHSExactPass200ARepairedShadowWitnessV2`
- `HHSExactPass219InheritedPass200ABindingV1`
- `hhs_exact_pass219_inherited_pass200a_version`
- `hhs_exact_pass219_bind_pass200a_repaired_shadow_authority`

C++:

- `hhs::rna::InheritedPass200ARepairedShadowAuthority`

Python:

- `hhs_runtime.hhs_pass219_cumulative_pass_membrane_i126_pass200a`

The Pass 219 membrane is read-only evidence/validation. It adds no candidate authority, canonical mutation authority, persistence authority, Hash72 clock/commit authority, C++ mutation authority, or VM81 mutation authority.
