# Pass220 Guarded Lean proof admission restart — 2026-10-19

- Base and merge target: main; working branch `pass220/guarded-service-lean-proof-admission-20261019`.
- Inspected `AGENTS.md`, `REPOSITORY_INDEX.md`, `hhs_runtime/hhs_service_registry_v1.py`, existing `lean-toolchain` pinned `leanprover/lean4:v4.34.0`.
- Source `hhs_runtime/hhs_guarded_service_lean_proof_checker_v1.py` commit `3fa50e9c5526a2cbb61827d131eae2c6c154fd0b`: require checked Lean file inside `formal/lean`, declared SHA256 source integrity, pinned toolchain and live Lean process exit success. No VM81/Hash72/Hash216 mutation authority.
- Registry `hhs_runtime/hhs_service_registry_v1.py` commits `66c41a871caabc58a67bc31fde4b52db3f552d5a`, `eb26ba3ff869f6d38fca378e16796111ce862dd2`: opt-in service-owned `lean_proof_contracts` field, carry through registration and `register_function`, check before storing service. Existing no-manifest services preserve inherited behavior. No false proof inferred from main alone.
- Targeted negative tests commit `95d083b27e9981036071a2de43ef3d63323bf66f`; workflow `4264c2aff9969ec364c16657befc4bfec35c3644` runs PR/main path-scoped Python tests. Current head validation pending. Tests mock Lean invocation; **do not** claim compiled Lean theorem verification succeeded in CI.
- Further obligations: native/production integration checker invoking pinned Lean with real imported Mathlib dependencies, theorem-source and proof identity in signed Hash216 receipts, service-to-theorem mapping for covered services, actual guarded registration negative tests against interposer and full end-to-end UI service validation.
- No main merge, production promotion or browser acceptance claimed.
