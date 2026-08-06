# Pass 213 Restart Record — Final Iteration 11

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full-hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Merge target: `main`
- Pull request: `#169`
- Final iteration: `11`
- Implementation state: `COMPLETE`

## Cumulative state

Iterations 1–11 are implemented. Pass 213 now includes immutable compiled-ROM identity, correction before interpretation and execution, protected native memory, dependency-scoped parametric admission, persistent inventory/tombstones/recovery, PQC checkpoint enclosure, RFC 3161 external timestamp anchoring, exact moving tensors, governed API/CLI projections, governed real-C native dispatch, complete full-hydration evidence, and interrupted/resumed deterministic replay closure.

## Final-iteration files

Added:

- `hhs_backend/runtime/hhs_pass213_final_evidence_v1.py`
- `tests/test_pass213_final_evidence_v1.py`
- `scripts/run_pass213_final_evidence.py`

Extended:

- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`

## Final evidence authority

- generates the complete `50,388,480`-bit / `6,298,560`-byte affine hydration;
- selects strict `AFFINE_9720_LEAF_SEEDS_PLUS_SPARSE_XOR` encoding;
- verifies deterministic full-state re-encoding equality;
- removes two data shards from one stripe and reconstructs the exact state before interpretation;
- corrupts a physical shard and verifies rejection before interpretation;
- validates the exact `50,388,480`-position moving-tensor affine closure and route round trips;
- measures 2,048 protected exact compiled-ROM lookups;
- measures 512 parametric admissions with one changed field, two affected constraints, and two reused witnesses;
- executes 32 singleton-VM81 native dispatches;
- crosses a recovery boundary at sequence 16;
- proves uninterrupted and resumed receipt sequences are bit-exactly equal;
- proves final state roots, Hash72 receipts, and authenticated ledger chains are equal;
- commits deterministic semantics and hardware-specific timings into separate Hash216 roots;
- emits a terminal Hash72 receipt over the semantic root;
- exposes no protected bytes, physical addresses, keys, carriers, tensor seeds, native pointers, or uncommitted state.

## Reference semantic evidence

```text
full hydration bits:                 50,388,480
full hydration bytes:                 6,298,560
affine seed bytes:                        2,430
compressed payload bytes:                 2,473
compression ratio:                  6,298,560 / 2,473
missing data shards recovered:                 2
corruption detected before interpretation:  true
moving-tensor domain:               50,388,480
protected exact lookups:                   2,048
parametric admissions:                       512
tensor route round trips:                  8,192
native dispatches:                            32
recovery boundary:                    sequence 16
uninterrupted/resumed equality:              true
ledger chains valid:                          true
```

```text
semantic root Hash216:
b783eaf39ca3cdff05d31dbe1406dc4ed45943a48b1cf89f3ee451a2c0326c0d

terminal receipt Hash72:
mO(Wo87dXeN)Ua2hbw96>2mLKi)iBlLT0Qy-qsjl>1icjig(7cc/d)FJd<9(gmvC20YL?twn
```

## Reference observations

These integer-nanosecond observations are hardware-specific and noncanonical.

```text
GitHub Actions Ubuntu 24.04 x86_64
CPython 3.12.13
logical CPUs: 4
full-state generation:       2,502,120 ns
full-state encode:          76,614,754 ns
two-shard recovery/decode:  30,396,138 ns
corruption detection:          129,224 ns
2,048 protected lookups:   147,036,530 ns
512 parametric admissions: 174,561,123 ns
8,192 tensor routes:       155,074,550 ns
32 baseline dispatches:    125,982,772 ns
32 resumed dispatches:     126,108,221 ns
```

```text
observation root Hash216:
d4bc7fdd97dac1d334711f6ce11e9a2ccdb16dcb1d89d23da8c5a178444d9c53
```

## Validation command

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

## Reference validated evidence

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31064998624
job: 92500772659
validated head: c85e669862079e8346f14404a51a9c152623c062
cumulative tests: 124 passed
result: SUCCESS
evidence JSON SHA-256:
6a79dbf26f7657e4d1726779e93c2edf61685527bbe079e4e8bbaeb980ec78d5
```

## Validation history and repairs

The first final-iteration run passed all 124 tests but the standalone evidence runner could not import `hhs_backend` when launched from the `scripts/` directory. The validation command was repaired by explicitly binding the repository root into `PYTHONPATH`. No runtime authority, inherited test, semantic root, or evidence algorithm changed.

## Restartability

- All implementation changes are committed to `agent/pass213-compiled-rom-integrity`.
- The final evidence workload is executable from repository-visible state.
- Both native libraries are rebuilt in the validation gate with warnings as errors.
- PQC and RFC 3161 dependencies are preflighted.
- The evidence JSON and validation transcript are retained together by the terminal workflow.
- There is no uncommitted or chat-only recovery state.
- There is no remaining Pass 213 implementation iteration.

## Next exact action

Run the final cumulative workflow against the exact completed branch head. When green, mark PR #169 ready, merge it to `main`, run the same terminal gate on the merged main commit, verify the exact main head and retained evidence artifact, and then declare Pass 213 authoritatively closed. Pass 214 must not merge ahead of that verified-main closure.
