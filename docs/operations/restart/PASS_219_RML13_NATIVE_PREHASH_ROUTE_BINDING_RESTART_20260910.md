# Pass 219 RML13 Native Pre-Hash Route Binding — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML12 green restart seal: `356b60ef25321e86c6c54f173e3e0a554e7be747`
- RML13 ABI header initial commit: `887cb62d8280d0cf06d00ba6722006b8ec50b6f6`
- RML13 ABI header partition repair: `00c90931502548cd642a3393477cb7b532610285`
- RML13 native C implementation: `1ae81ffc78ec6db1d53810cb3421f7560d5c7332`
- RML13 native extension build surface: `53ee7fdaba8b59592a6a85cbc91ef603a7bd7b88`
- RML13 Python bridge: `4f392321fd4dfd59e3f71ee5de7cfc9809b727a4`
- RML13 tests: `a79887d67d681086ffd0094d3a3762e9b2274768`
- RML13 contract: `40d81a812e4ef7b6c8bf33a00c7292d2ec560247`
- RML13 workflow / implementation head: `51fcdbd1053fb730964fdcf9a6dec099e4440e16`

The unrelated temporary ref `agent/pass219-recursive-manifold-learning-20260909-rml9-temp` remains non-authoritative and is not a restart source.

## Frozen parent evidence

RML12 remains validated and is not rerun except where directly included in the RML13 dependency scope:

- Workflow: `Pass 219 Reciprocal Route Optimizer`
- Run: `34436975540`
- Job: `102743988934`
- Result: `14 passed, 0 failed, 1 inherited pytest-config warning in 38.66s`
- Validated head: `7806163e541fa400ffbe2ad65a28cde6418d2ca3`
- Contract validation seal: `f7d8b056dde95c5c66cca91d4f0ca5fa3e4afb77`
- Green restart seal: `356b60ef25321e86c6c54f173e3e0a554e7be747`

## Exact native issuance path inspected

The frozen path is:

```text
I162 constructs candidate HHSExactVM81Frame
    -> hhs_exact_vm81_admit_uqcel
        -> candidate frame export (648 bytes)
        -> change_hash72 = Hash72(candidate frame bytes)
        -> receipt_hash72 = Hash72(frozen UQCEL admission material)
        -> hash216_triplet = previous_hash72 || change_hash72 || receipt_hash72
        -> transition/hash216 identity = Hash216(hash216_triplet)
I168 copies these already-issued values into its general binding record
```

Therefore a wrapper around I168 would be post-hash and could not truthfully claim native pre-hash route binding.

## RML13 implementation

RML13 introduces versioned ABI `1.26.0` as a native extension:

- `hhs_runtime/include/hhs_pass219_rml13_native_route_witness_binding_1_26.h`
- `hhs_runtime/c/hhs_pass219_rml13_native_route_witness_binding_1_26.c`
- output library: `hhs_runtime/builds/libhhs_pass219_rml13.so`
- build surface: `native_projects/hhs_pass219_rml13_route_binding/Makefile`

The extension links the existing `libhhs_runtime.so` and delegates actual VM81 admission/replay to the existing exported `hhs_exact_vm81_admit_uqcel` entrypoint. It does not add a second commit primitive and does not modify frozen I162, I168, UQCEL v1, or the root runtime Makefile.

## Fixed RML12 witness packet

The native packet contains raw SHA-256 digests for:

```text
selected route
route selection
selected-route bundle
source state
target state
```

It also contains exact route partitions:

```text
edge count
pair flips
coupled generator/product moves
Hopf same-base / base-moving
Clifford full intertwiner / chirality swap / even-sector preserving / residual-u72
```

Native admission rejects the packet unless all route partitions equal edge count and the upstream route asserts:

```text
admissible product geometry
all edges reversible
exact target reached
reverse edge sequence restores exact source
optimizer transition authority = 0
floating-point authority = 0
```

## Pre-hash binding

RML13 serializes the packet with explicit big-endian integer fields and computes an exact SHA-256 witness root.

A route-environment root then binds:

```text
Pass159 global symbol-environment root
Pass159 exact combined-source SHA-256
RML13 witness root
```

The resulting 648-byte VM81 candidate frame embeds the route, selection, bundle, source, target, witness, route-environment, and Pass159 provenance digests before calling inherited UQCEL admission.

Consequently:

```text
route witness -> candidate frame -> change_hash72 -> hash216_triplet -> transition Hash216
```

This is the precise pre-hash claim made by RML13.

## Honesty boundary

Frozen UQCEL v1 `receipt_hash72` material does not contain the candidate frame or `change_hash72`. RML13 therefore explicitly records:

```text
change_hash72 directly route-bound: yes
Hash216 identity route-bound: yes
inherited UQCEL receipt_hash72 directly route-bound: no
```

RML13 does not rewrite the inherited receipt algorithm and does not claim otherwise.

## Tests added

`tests/pass219/test_pass219_rml13_native_route_witness_binding.py` verifies:

1. selected RML12 route serializes into the fixed native packet with exact partitions;
2. native binding verifies Pass159 provenance and embeds the witness before Hash72/Hash216 issuance;
3. native replay is deterministic;
4. two different valid RML12 routes change witness root, route environment root, candidate frame, `change_hash72`, Hash216 triplet, and transition Hash216;
5. those two routes retain the same frozen UQCEL `receipt_hash72`, proving the honesty boundary;
6. an inconsistent native route partition is rejected.

The dedicated workflow also reruns the frozen I168 regression and validates the existing Pass188 native Bott runtime.

## Validation state at checkpoint creation

Dedicated workflow:

- Name: `Pass 219 RML13 Native Prehash Route Binding`
- Run: `34438142834`
- Job: `102747417114`
- Head: `51fcdbd1053fb730964fdcf9a6dec099e4440e16`
- State at checkpoint creation: `queued`
- Conclusion: pending external runner allocation

No green result is claimed yet.

## Validation command encoded in workflow

```text
make -C native_projects/hhs_pass219_rml13_route_binding validate
make -C native_projects/hhs_pass188_bott_runtime validate
nm -D hhs_runtime/builds/libhhs_runtime.so | grep hhs_exact_pass219_i168_bind_canonical
PYTHONPATH=$PWD python -m pytest -q -s \
  tests/pass219/test_pass219_reciprocal_route_optimizer.py \
  tests/pass219/test_pass219_rml13_native_route_witness_binding.py \
  tests/pass219/test_pass219_i168_pass169_general_runtime_binding.py
```

## Authority boundary

RML13 adds no optimizer commit authority, floating-point canonical authority, Hash216 persistence authority, or scalar-projection substitution authority. Python only serializes the validated route packet and invokes C; it does not mint Hash72 or Hash216 values.

## Required next action

Inspect run `34438142834` when runner state changes.

- If red: repair only the impacted RML13 native/build/bridge/test surface, rerun the same dependency scope, and preserve all frozen parent evidence.
- If green: freeze exact counts/log evidence into the RML13 contract, commit a green validation seal and restart checkpoint, then update PR #414.

Do not merge PR #414 solely from this pending checkpoint.
