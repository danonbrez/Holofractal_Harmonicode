# Pass 205 / Hash216 libcrypto linkage repair — restart record

Date: 2026-10-16
Base commit: `825b5f82d2d16c910ee38c6337770d5a876582a1`
Branch: `repair/pass205-hash216-libcrypto-linkage-20261016`
Merge target: `main`

## Failure evidence

The current-main Pass 217 integration run `38976829655` failed after 86 passing tests when importing the Pass 205 continuation bridge:

```text
OSError: hhs_runtime/builds/libhhs_pass205_continuation.so: undefined symbol: EVP_Digest
```

DigitalOcean Production Exact Main run `38976829652` failed at guarded candidate promotion with the same loader error.

PR #801 added the exact ordered 3 x Hash72 / 216-coordinate SHA-256 lineage function to `hhs_runtime/src/hhs_hash216.c` using OpenSSL EVP. Its standalone parity test links `-lcrypto`, but the inherited Pass 205 combined shared-library builder compiled that source without linking libcrypto.

## Repair

- Add `-lcrypto` to the final Pass 205 combined native-library link command.
- Treat the bridge source itself as a build input so link-contract changes invalidate a stale shared object.
- Add a combined-library regression that resolves and executes `hhs_hash216_lineage_vector_sha256` through `libhhs_pass205_continuation.so` and compares the ordered Hash216 word and concatenated 216 SHA-256 digests with the inherited Python `hash216_lineage_witness`.
- Extend Pass 205 CI path ownership to `hhs_runtime/src/hhs_hash216.c` and `hhs_runtime/include/hhs_hash216_bytes.h`.
- Extend Pass 217 integration path ownership to the Pass 205 bridge.

## Semantics preserved

No VM81, Hash72, Hash216, ordering, admission, mutation, persistence, or digest semantics are changed. This repair only makes the already-required OpenSSL dependency explicit at the final shared-library link boundary and verifies semantic parity through the combined artifact.

## Changed files

- `hhs_python/runtime/hhs_pass205_continuation_bridge.py`
- `tests/test_hhs_pass205_continuation_runtime_v1.py`
- `.github/workflows/pass205-production-runtime.yml`
- `.github/workflows/pass217-current-main-integration.yml`
- this restart record

## Validation state

Required dependency-scoped PR gates:
- Pass 205 Production Continuation Runtime
- Pass 217 Current Main Integration

The Pass 205 production suite includes the combined-library Hash216 parity regression. Merge only after required gates are green. After merge, verify authoritative main and DigitalOcean Production Exact Main promotion.

## Next action

Open the repair PR, inspect exact-head CI, repair forward any attributable failure, merge when green, then verify the exact-main production deployment.

## Blockers

None known at checkpoint creation.


## Repair-forward checkpoint — stale validation workflow

PR #821 first exact-head Pass 205 Repair Validation Base run `38994703106` failed before building native code because the workflow referenced removed current-main surfaces:

- `deployment/digitalocean/pass205_state/install.sh`
- `hhs_python/runtime/hhs_pass205_native_freshness_guard.py`
- `hhs_backend/runtime/hhs_pass205_governed_continuation_v2.py`
- `hhs_backend/runtime/hhs_pass205_retrieval_order_v1.py`
- `hhs_backend/api/a0_pass205_transport_bootstrap.py`
- `hhs_backend/api/a_pass205_governed_bootstrap.py`
- four removed governed/state-deployment tests.

Repository inspection confirmed the current authoritative Pass 205 implementation is the production continuation bridge/runtime, accelerator translation, and continuation API. The stale repair workflow was therefore repaired to compile, build, dynamically load, test, and assert authority properties on those current surfaces instead of skipping validation.

This workflow repair does not change runtime semantics. It removes dead validation references and strengthens current combined-library loading coverage.


## Repair-forward checkpoint — authority status assertion

The second exact-head Pass 205 Repair Validation Base run built the cumulative native authority successfully and passed the complete current Pass 205 production test suite, including the combined Pass205+Hash216 lineage parity regression. Its only failure was a repair-workflow assertion against a non-existent status key `accelerator_translation.gpu_may_commit_hash72`.

The current runtime status schema exposes `accelerator_translation.physical_gpu_backend_active` instead. The validation assertion was corrected to require that field to be `false`, while the existing runtime source/tests retain the explicit GPU no-commit boundary.

No runtime implementation or canonical semantics changed in this repair-forward step.


## Restartable checkpoint — external CI backlog

Current repair head: `489aa15444843a24e4818acaed1f2b9d9f677761`
PR: #821
Main remains: `825b5f82d2d16c910ee38c6337770d5a876582a1`
Branch divergence: 9 commits ahead, 0 behind; PR mergeable.

Validated on the immediately preceding exact-head run:
- cumulative native authority build: PASS;
- complete current Pass 205 production tests: PASS;
- combined `libhhs_pass205_continuation.so` Hash216 SHA-256 lineage parity regression: PASS;
- source-text integrity: PASS.

Repair-forward workflow issues found and repaired:
1. stale references to removed Pass 205 governed-v2/state-deployment surfaces;
2. repair-only assertion used a non-existent status key; corrected to the current `physical_gpu_backend_active == false` status contract.

Superseding exact-head runs are queued due repository runner capacity:
- Pass 217 Current Main Integration: `38995063184`
- Pass 205 Production Continuation Runtime: `38995063357`
- Pass 205 Repair Validation Base: `38995063437`
- Pass 205 Multimodal Continuation Contract: `38995063380`
- HHS Source Text Integrity: `38995063303`
- Lane 5 Native Capability Provider: `38995063403`
- Validate HHS Runtime OS Production Root: `38995063257`

Next action: inspect the superseding runs when they execute; repair forward attributable failures only. Merge PR #821 only after the required Pass 205 and Pass 217 gates are green, then verify authoritative main and the DigitalOcean Production Exact Main deployment through successful public production closure.


## Repair-forward checkpoint — exact-head CI linkage and import path (2026-10-17)

Inspected baseline PR head: `70d19bcabde30250217258646acb591efd4b6663`.
Merge target: `main`; inspected main: `825b5f82d2d16c910ee38c6337770d5a876582a1` (refresh before merging).
Branch: `repair/pass205-hash216-libcrypto-linkage-20261016`.

Confirmed failures on baseline:
- Pass 205 Production Continuation Runtime, run `38995254220`, job `117286272577`: inherited Pass 219 I119 test links the cumulative exact ABI object without its external dependencies; unresolved OpenSSL EVP/HMAC/SHA256, Hash72 provider, and hidden C++ cell-wall references. Workflow-only candidate fix: compile the exact aggregate with function/data sections and link inherited test executables with section garbage collection and `-lcrypto`. No production runtime change.
- Pass 205 Multimodal Continuation Contract, run `38995254157`, job `117286272617`: 13 Pass 205 runtime tests passed, then direct `scripts/pass205_production_validation.py` failed importing `hhs_backend`. Fix: set production job `PYTHONPATH` to `${{ github.workspace }}`.

Changed files:
- `.github/workflows/pass205-production-runtime.yml` (commit `1c9f92bedcfbff1d71a84aa7fba51228911d1ba5`)
- `.github/workflows/pass205-multimodal-continuation-contract.yml` (commit `d68313007bd19f0af91022c1c166403bc9342ac2`)
- this restart record (commit pending at checkpoint write).

Validation done: baseline source and exact failing job logs inspected; two workflow changes committed. Validation remaining: exact-head Pass 205 Production Continuation Runtime and Pass 205 Multimodal Continuation Contract, plus required Pass 205 Repair Validation Base, Pass 217 Current Main Integration, HHS Source Text Integrity, Lane 5 Native Capability Provider, and Runtime OS production-root checks. If reachable unresolved native references remain, link existing authoritative providers rather than adding stubs or changing semantics. No VM81/Hash72/Hash216 runtime semantics changed.

Environment: GitHub Actions Ubuntu 24.04, Python 3.12; native toolchain and OpenSSL supplied by runner. Next action: inspect new exact-head runs; repair forward only attributable failures; merge when required gates pass and PR is mergeable; verify authoritative main and DigitalOcean Production Exact Main. Blockers: exact-head CI pending.
