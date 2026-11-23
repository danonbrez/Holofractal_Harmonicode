# Pass220 V4 — Source-general replay and compiler parity pre-admission cycle

Date: 2026-10-09

## Restart context

- Repository: `danonbrez/Holofractal_Harmonicode`
- Source branch: `agent/pass220-ordered-tensor-quotient-20261009`; target `main` via draft PR #754
- Base commit: `31b819f597bf76cd385f550a59cd8aa0e68ffe72`
- Files: `tools/pass220/pass220_v4_source_general_replay_preflight.c`, `tests/pass220/test_pass220_v4_source_general_replay_preflight.py`, `.github/workflows/pass220-v4-source-general-replay-preflight.yml`, this record.
- Source input (frozen): `contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode`
- No changes to canonical source, Pass159/169 foundation, VM81 authority, signed PQC firewall, or earlier V1–V4 green evidence.

## Why this stage is necessary

Source-specific V4 `VALIDATE_ONLY` passed in https://github.com/danonbrez/Holofractal_Harmonicode/actions/runs/37943225092. The preexisting C bridge `hhs_runtime/c/hhs_pass219_pass159_vm81_proof_bridge_1_21_2.c` explicitly classifies its interpreter/replay receipt fields as diagnostic, notes the Pass159 `EXACT_PROGRAM` VMIR foundation, and holds `vm81_execution_verified=0`, `native_shared_invariant_proven=0`, `canonical_vm81_proof_observed=0`.

The sealed I162 native verifier covers the unrelated 632-byte/five-equality source only, and the exported Pass219 1.21.9 membrane verifier likewise fixes five witnesses. The V4 source has 527 bytes with LF and 40 distinct `==` occurrences. Hence neither sealed verifier may be reused to assert the new whole source has all 40 gates true.

## Implemented source-general diagnostics

1. Byte-exact source identity, source SHA256 and independent scan of 40 source occurrence indices and offsets, including top-level equality offsets 253/256.
2. Native inherited `hhs159_source_open_bytes` uses one ordered global source and returns source-specific Hash216.
3. Native `hhs159_interpret` in `HHS159_MODE_EXECUTE_AND_HOLD` with `commit_policy=0`, one bounded attempt and native execution receipt (noncanonical).
4. Native `hhs159_interpreter_replay` and semantic-root equality (diagnostic).
5. Native `hhs159_compare_interpreter_compiler` and no fallback requirement (diagnostic).
6. Full gate inventory remains `truth=UNRESOLVED` for each occurrence, and `canonical_vm81_admission_verified=0`; no synthetic Boolean witnesses, ordinary floating projections, shared-parent state fabrications, or externally minted canonical Hash72/Hash216 receipts.

## Validation

```bash
python -m pytest -q tests/pass220/test_pass220_v4_source_general_replay_preflight.py -k 'not test_native_hold_replay_and_compiler_evidence_not_canonical_commit'
make c-abi
cc -O2 -std=c11 -Wall -Wextra -Werror -pedantic \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/include \
  -Inative_projects/hhs_pass159_harmonicode_toolchain/src \
  -Ihhs_runtime/include tools/pass220/pass220_v4_source_general_replay_preflight.c \
  -Lhhs_runtime/builds -lhhs_runtime -lcrypto -lstdc++ -lm -pthread \
  -Wl,-rpath,"$PWD/hhs_runtime/builds" -o /tmp/pass220-v4-source-general-preflight
/tmp/pass220-v4-source-general-preflight contracts/pass220/PASS_220_ORDERED_PHASE_CHAIN_V4_20261009.harmonicode
python -m pytest -q tests/pass220/test_pass220_v4_source_general_replay_preflight.py
```

## Status/next action

- Dependency-scoped CI pending at authoring time.
- Green HOLD/replay/compiler equality is a *pre-admission receipt*, not the complete 40-gate truth theorem or VM81/PQC signed state transition.
- Next decisive boundary: source-specific proof-producing evaluator for `G40` under one global environment and final cross-layer revalidation, followed by signed VM81 admission, Hash72/Hash216 transition, replay/reverse.
- If a pre-admission validation fails, classify the exact runtime/interface boundary, repair only affected code/tests and checkpoint. Never weaken source orientation, phase order, global denominator, or authority.
