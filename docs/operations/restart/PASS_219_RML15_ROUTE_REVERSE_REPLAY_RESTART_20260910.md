# Pass 219 RML15 Route Reverse/Replay — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML14 green restart seal: `e7f82b4ed521583b76ffb4cc03053aa920ae5355`
- RML15 ABI header: `2169169439a18261cd4753e1e061485d4ab09694`
- RML15 native implementation: `7ba37c0aa64338d530c8ba9d49d6f92e7d46684d`
- RML15 native build: `eea7f49dc50524a41cb46e5f688077dd0ed47884`
- RML15 Python bridge: `cf9c4d97d53f5921e823ad148c5a49a1446c6bf7`
- RML15 tests: `4b5876167f476468f307956657d29811edd7376e`
- RML15 contract: `2c6200dc270b2519a4b2e5d454001953d04b0a8b`
- RML15 workflow / implementation head: `452ddb502158cf488bbb000f6af2664b06b57ac8`

## Frozen parent evidence

RML14 remains the validated predecessor:

- Workflow: `Pass 219 RML14 Route Bound Receipt Successor`
- Run: `34464850267`
- Job: `102830909024`
- Result: `15 passed, 0 failed, 2 warnings in 4.47s`
- Validated implementation head: `8fb7be0f13070d52e3b59d86d6a26c06a44d6042`
- Contract seal: `892c0a9b8327d3a15c495460c0dd16e6304f67a1`
- Green restart seal: `e7f82b4ed521583b76ffb4cc03053aa920ae5355`
- Pass188: `1,259,712` states, zero coordinate drift, checksum `11e3bbf0214751c3`

## RML15 semantic boundary

RML15 does not invert Hash216. It follows the inherited I163/RML12 distinction between reversible execution and cryptographic identity:

1. invoke validated RML14 once as forward execution;
2. invoke the same RML14 input again and require exact route-aware receipt/Hash216 replay equality;
3. obtain reverse instructions only from the retained selected RML12 edge sequence;
4. begin from the retained target phase state;
5. replay inverse operations in reverse edge order;
6. require exact restoration of the source eight-channel phase tuple, four ordered quarter-turn signs, and radix-72 ambient index;
7. retain the historical source state SHA-256 as ancestry instead of claiming it was reconstructed by hash inversion;
8. issue a new reverse ancestry receipt through the existing canonical Hash72/Hash216 functions.

## Native reverse mechanics

ABI: `1.28.0`.

Channel order:

```text
x, y, z, w, xy, yx, zw, wz
```

Product-sign order:

```text
xy, yx, zw, wz
```

The native reverse engine supports exactly the bounded RML12 generators:

- coupled generator/product move: negate the retained signed `Z72` displacement and apply it to the primitive plus its dependent product;
- chiral pair flip: reapply the exact self-inverse `u^36` pair operation.

After every reverse edge the C layer independently verifies:

- all eight phase coordinates are in `[0,71]`;
- product channels remain exact directed `u^18` images of their generators under retained signs;
- `xy/yx` and `zw/wz` signs remain opposed;
- the radix-72 ambient index matches the eight phase coordinates.

The final native phase/sign/index state must equal the retained source phase/sign/index state.

## Chain preservation

RML15 preserves both prior chains in its output:

```text
historical UQCEL v1 receipt
historical RML13 transition Hash216
RML14 route-bound successor receipt Hash72
RML14 route-bound successor transition Hash216
```

The RML15 reverse receipt is separately classified as an ancestry witness, not an inverse transition identity.

Canonical receipt functions used:

```text
hhs_hash72_compute
hhs_hash216_compute
```

No copied hash algorithm is introduced.

## Tests added

`tests/pass219/test_pass219_rml15_route_reverse_replay.py` covers:

1. a four-edge route containing two coupled moves plus both chiral pair flips;
2. exact reverse instruction order and signed inverse displacements;
3. native RML14 forward/replay equality;
4. exact native phase/sign/ambient restoration;
5. predecessor and RML14 successor chain preservation;
6. deterministic repeated invocation;
7. sensitivity to different valid route endpoints;
8. explicit proof that no Hash216 cryptographic inversion is used;
9. rejection of a mismatched retained endpoint before native execution;
10. native rejection of a corrupted reverse instruction.

## Authority boundary

RML15 adds no VM81 commit primitive, optimizer transition authority, floating-point authority, Hash216 persistence authority, or scalar-projection substitution authority. The local reverse phase struct is proof state only. Python does not mint Hash72 or Hash216 values.

## Validation state at checkpoint creation

Dedicated workflow:

- Name: `Pass 219 RML15 Route Reverse Replay`
- Run: `34466181156`
- Job: `102835196552`
- Head: `452ddb502158cf488bbb000f6af2664b06b57ac8`
- State: `queued`
- Conclusion: pending runner allocation

No green RML15 claim is made at this checkpoint.

## Required next action

Inspect run `34466181156`.

- If red: repair only the impacted RML15 native/build/bridge/test or bounded dependency declaration, rerun the same gate, and preserve frozen RML14 evidence.
- If green: freeze exact count/timing/native evidence into the contract, create the green RML15 restart seal, and update PR #414.

Do not merge PR #414 solely from this pending checkpoint.
