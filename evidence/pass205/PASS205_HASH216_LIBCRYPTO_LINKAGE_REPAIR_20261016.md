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
