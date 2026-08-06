# Pass 213 Restart Record — Iteration 10

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full-hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Validated Iteration 10 runtime head: `af36575233248d77b606ff63b41ca5e51ca23ff5`
- Iteration 10 contract commit: `fe1709cf328a832c45f0f12c7cec219ac8c33632`
- Iteration 10 primary specification commit: `2d9f7a7f3a61344a2f1d6154c958938b8e472899`
- Iteration 10 README commit: `7db20fd496f653ec604ecfdbc841dfd0d807c2a0`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `10`

## Cumulative runtime state

Iterations 1–10 are implemented. The chain now includes immutable compiled-ROM identity, Pass 212 correction before interpretation, protected native memory, dependency-scoped parametric admission, persistent inventory/tombstones/recovery, post-quantum checkpoint enclosure, RFC 3161 external timestamp anchoring, exact trusted-anchor-bound moving tensors, capability-governed API/CLI projections, and governed real-C native dispatch.

## Iteration 10 files

Added:

- `native/pass213/hhs_pass213_native_dispatch.c`
- `hhs_backend/runtime/hhs_pass213_native_dispatch_common_v1.py`
- `hhs_backend/runtime/hhs_pass213_native_dispatch_kernel_v1.py`
- `hhs_backend/runtime/hhs_pass213_native_dispatch_ledger_v1.py`
- `hhs_backend/runtime/hhs_pass213_native_dispatch_authority_v1.py`
- `hhs_backend/runtime/hhs_pass213_governed_native_dispatch_v1.py`
- `hhs_backend/api/pass213_native_dispatch_routes.py`
- `hhs_runtime/pass213/native_dispatch_cli.py`
- `tests/test_pass213_governed_native_dispatch_v1.py`
- `tests/test_pass213_native_dispatch_api_cli_v1.py`

Extended:

- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`

## Iteration 10 authority

- fixed-width allocation-free C ABI with no ambient mutable state;
- exact VM81 cell, operation-slot, and G243 route validation;
- protected compiled-ROM lookup by canonical `entry_hash216`;
- current parent, kernel policy, kernel measurement, Hash216 lineage, trusted timestamp, moving tensor, hydration lane, and protected inventory binding;
- exact compiled input/result counts, sorted read/write sets, unsigned-64 operand bounds, and optional modulus;
- native add, subtract, XOR, AND, OR, modular multiply, rotate-left, equality, and conditional select workloads;
- internal moving-tensor physical route with public Hash216 commitment only;
- singleton VM81 lock and pre-native reentry rejection;
- deterministic request, result, route, access-set, and successor Hash216 roots;
- ordered Hash72 successor receipt;
- authenticated SQLite WAL execution ledger with `synchronous=FULL`;
- exact reopen continuation and rejection of database tamper, wrong anchors, sequence gaps, state substitution, receipt substitution, stale parent, duplicate replay, timestamp rollback, policy substitution, tensor substitution, access mismatch, and operand overflow;
- shared FastAPI and CLI execution/receipt parity;
- local-only `dispatch.execute` and `dispatch.read` capability issuance;
- no compilation, protected-memory read, repair, deletion, physical address, carrier, DER, key, or uncommitted-state exposure.

## Validation command

```bash
python -m pip install -r requirements/pass213-pqc.txt
PYOQS_VERSION=0.16.0 bash scripts/run_pass213_iteration1_validation.sh
```

## Repository-native runtime evidence

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31062363170
job: 92492790661
validated runtime head: af36575233248d77b606ff63b41ca5e51ca23ff5
cumulative tests: 122 passed
result: SUCCESS
artifact: pass213-iteration10-validation-31062363170
artifact digest: sha256:46689e6e95a99fdb1e241431809aad60d15778ea954567be22fe2de9010c3522
```

## Validation history and repairs

The first Iteration 10 cumulative run exposed two integration defects: the Iteration 8 closure proof field was named `proof_root_hash216`, and FastAPI worker-thread execution required an explicitly locked cross-thread SQLite connection. Both were repaired without changing inherited Iterations 1–9 behavior.

Subsequent failures were test-only representation assumptions: a safe `physical_route_exposed` boolean was mistaken for the protected `physical_route` key, and protected JSON reconstruction changed tuple containers into canonical-equivalent lists. Tests were corrected to inspect exact protected keys and canonical Hash216 identity.

## Workflow state

- Iteration 1–10 runtime implementation validation: complete and successful.
- Iteration 10 machine contract and documentation: repository-visible.
- Pull request remains draft and unmerged.
- Pass 214 must not merge ahead of authoritative Pass 213 closure.

## Remaining work

1. Produce full-hydration performance and recovery evidence over the 50,388,480-position domain.
2. Run final integration and replay validation.
3. Merge Pass 213 to `main` and verify the exact main head.

## Next exact action

Begin the full-hydration performance and recovery evidence iteration. Measure protected compiled-ROM hit admission, native dispatch, moving-tensor route derivation, successor commitment, ledger append, deterministic replay, controlled damage detection, recovery, and resumed execution across representative exact, parametric, and full-domain workloads. Preserve every Iteration 1–10 gate and do not substitute synthetic throughput claims for measured repository-native evidence.
