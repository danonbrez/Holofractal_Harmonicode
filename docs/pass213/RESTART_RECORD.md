# Pass 213 Restart Record — Iteration 9

- Contract: `HHS-P213-TB-AMT-CROM-RMIK-H72-H216-VM5184-G243`
- Immediate parent: Pass 212 full-hydration compression and physical erasure recovery
- Base commit: `2be050264a6e9c659603100be802979bbc49bf7a`
- Branch: `agent/pass213-compiled-rom-integrity`
- Final validated Iteration 8 branch head: `b4db0de704e4fb43f5f382e3f11d114418af181c`
- Validated Iteration 9 implementation head: `109aa45e39a33622a645a48fccb15d6101d06c38`
- Validated Iteration 9 contract/documentation head: `43c16a00b1be009b59cdbdec1202808ea432fbe5`
- Validated Iteration 9 restart evidence head: `bdc68a9bf288f4220ae91415362698c1755353e5`
- Final validated Iteration 9 branch head: `fb0f07bf207b8814469a69416ad009277579fa48`
- Merge target: `main`
- Draft pull request: `#169`
- Iteration: `9`

## Cumulative runtime state

Iterations 1–9 are implemented and repository-validated. The chain includes immutable compiled-ROM identity, Pass 212 correction before interpretation, protected native memory, dependency-scoped parametric admission, persistent inventory/tombstones/recovery, post-quantum checkpoint enclosure, RFC 3161 external timestamp anchoring, exact trusted-anchor-bound moving tensors, and capability-governed API/CLI public projections.

## Iteration 9 files

Added:

- `hhs_backend/runtime/hhs_pass213_governed_surface_v1.py`
- `hhs_backend/runtime/hhs_pass213_governed_surface_v2.py`
- `hhs_backend/api/pass213_compiled_rom_routes.py`
- `hhs_runtime/pass213/__init__.py`
- `hhs_runtime/pass213/cli.py`
- `tests/test_pass213_governed_surface_v1.py`
- `tests/test_pass213_api_cli_v1.py`

Extended:

- `requirements/pass213-pqc.txt`
- `scripts/run_pass213_iteration1_validation.sh`
- `.github/workflows/pass213-compiled-rom-integrity.yml`
- `contracts/pass213/PASS_213_CONTRACT.json`
- `HHS_PASS_213_TIMESTAMP_BOUND_AUTHENTICATED_MOVING_TENSOR_COMPILED_ROM.md`
- `docs/pass213/README.md`
- `docs/pass213/RESTART_RECORD.md`

## Iteration 9 authority

- one shared governed operation dispatcher for HTTP and CLI;
- short-lived HMAC-SHA-256 capabilities bound to subject, exact scopes, issue/expiry nanoseconds, epoch, nonce, and capability Hash216;
- append-only HMAC-authenticated SQLite WAL public-projection chain;
- projection Hash216 roots and projection-domain Hash72 receipts;
- strict separation between canonical source receipts and public-projection receipts;
- sanitized compiled-ROM, inventory, moving-tensor, timestamp-anchor, integrity, and receipt commitments;
- FastAPI Bearer and `X-HHS-Capability` handling with conflict rejection;
- argparse CLI parity and structured nonzero rejection results;
- local-only capability issuance with no HTTP issuance route;
- rejection of keys, tokens, carriers, bytes, physical mappings, tensor seeds, native addresses, RFC 3161 DER, canonical floats, and uncommitted state;
- compile, execute, repair, deletion, protected-memory reads, physical maps, recovery carriers, DER reads, and network capability issuance remain unexposed.

## Final validation

```text
workflow: Pass 213 Compiled ROM Integrity
run: 31059269764
job: 92483397702
validated head: fb0f07bf207b8814469a69416ad009277579fa48
cumulative tests: 102 passed
result: SUCCESS
artifact: pass213-iteration9-validation-31059269764
artifact digest: sha256:c18683cb3fbadeb02bd0a04552e5d6c7f4c288012fecffdf303d37ebc16ed08a
```

The complete gate builds the native arena with warnings as errors, verifies real ML-KEM/ML-DSA/SLH-DSA and RFC 3161 dependencies, executes all 102 cumulative tests, compiles every Iteration 1–9 runtime/API/CLI module, parses the Iteration 9 contract, and retains the complete transcript.

## Workflow state

- Iteration 1–9 implementation validation: complete and successful.
- Iteration 9 contract/documentation validation: complete and successful.
- Final branch-head validation: complete and successful.
- Guarded Continuous Integration remains governed by its inherited path policy.
- Pull request remains draft and unmerged.

## Remaining work

1. Add governed native compiled dispatch.
2. Produce full-hydration performance and recovery evidence.
3. Run final integration, merge, and verified-main closure.

## Next exact action

Begin Iteration 10 by implementing governed native compiled dispatch while retaining every Iteration 1–9 gate. Execution must require an exact protected compiled-ROM identity, current policy and timestamp compatibility, moving-tensor route commitment, singleton VM81 admission, bounded read/write sets, deterministic native result commitment, and successor Hash72/Hash216 receipts. API and CLI must expose only governed execution requests and sanitized result commitments; no native pointers, protected bytes, physical mappings, keys, or uncommitted state may cross the projection boundary. Pass 214 must not merge ahead of authoritative Pass 213 closure.
