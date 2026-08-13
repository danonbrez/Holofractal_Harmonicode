# Pass 217 Iteration 3 Non-Promotional Genesis Candidate

## Outcome

Iteration 3 now provides a deterministic 5,184-bit candidate image and a
compact exhaustive address-map artifact.  Both rebuild exactly from frozen
inherited integer identities and fail closed on byte drift.

This is deliberately **not** the canonical Genesis ROM.  Pass 215/216
reconciliation remains open, so the candidate is evidence for later selection
and validation only.  It does not mutate VM81, activate migration, create a
physical Golay image, or mint Hash72/Hash216 transition authority.

## Candidate profile

For cell `c` and operation `o`:

```text
row, column = divmod(c, 9)
LoShu(c) = LoShu3x3[row mod 3, column mod 3]
quadrant(o) = Pass175PhaseTable[o] / 18
bit(c,o) = (quadrant(o) + LoShu(c)) mod 2
```

All operations are integers.  The inherited phase table has 32 even-quadrant
and 32 odd-quadrant entries, so every 64-bit cell shard contains exactly 32 one
bits and 32 zero bits.  The 81 shards therefore contain 2,592 bits of each
value.

Serialization is explicit LSB0 within each shard: operation `o` is stored in
byte `c*8 + o//8`, bit `o%8`.  Shards are serialized in ascending cell order.

## Address artifact

The address-map binary contains 5,184 fixed-width records in ascending linear
position order.  Each record is six unsigned bytes:

| Byte | Field | Range |
|---:|---|---:|
| 0 | cell | 0–80 |
| 1 | operation | 0–63 |
| 2 | phase alpha | 0–7 |
| 3 | phase beta | 0–7 |
| 4 | Hash72 row | 0–71 |
| 5 | Hash72 column | 0–71 |

The record index is the linear position `s`.  The verifier exhaustively proves:

```text
s = 64*c + o
o = 8*alpha + beta
s = 72*r + k
q = 243*s + g
```

The G243 projection is retained as an exact formula rather than duplicating
1,259,712 records.  Validation nevertheless round-trips every projected pair.

## Frozen inputs

Every input is bound to the exact Iteration 2 remote checkpoint
`bd20174c78127b0fffe9134bc10eac9a6d5445a2`, tree
`f6b5899ae0c77529dcf32400c817b8334e3faf4d`:

- Pass 217 normative contract;
- Iteration 2 machine contract and reference vectors;
- Pass 175 phase table and VM5184/G243 address formulas;
- the inherited tiled Lo Shu address identity; and
- the protected VM81 C runtime.

The tiled Lo Shu source's alternate Hash72 alphabet is explicitly rejected.
Only its exact Lo Shu address lift is reused.

## Deterministic evidence

```text
bundle root SHA-256:          7eb5cf33cb14fb9a61fb071a2801dae7a67997b92691a9820e5d058227302656
candidate SHA-256:            97379c7ae7cdaebd8031a3a3fb58559c967b361b360c7db34ec096acabfc8fe8
candidate shard root SHA-256: 0dcf8f31c4aa75b73514f5ff6fbe2c4c7b8da28931e2d3e5e05cf719bf2e0366
address-map SHA-256:          2f8d8a23114b87f2dbe91f3d302ef089b750f9d91f533d744a4524e907717f5f
candidate bytes:              648
address-map bytes:            31,104
candidate one/zero bits:      2,592 / 2,592
address records:              5,184
G243 projections verified:    1,259,712
```

## Claim boundary

```text
logical Genesis candidate generated: true
address-map artifact generated: true
canonical Genesis selected: false
logical Genesis ROM generated: false
canonical authority promoted: false
physical Golay ROM generated: false
Golay codec implemented: false
runtime mutation performed: false
protected C runtime modified: false
migration started: false
Pass 219 runtime implementation started: false
```

The inheritance status remains:

```text
HOLD_FOR_PASS_215_216_AUTHORITATIVE_RECONCILIATION
```

## Validation

Run:

```text
bash scripts/run_pass217_iteration3_validation.sh
```

The cumulative gate runs all 39 tests from Iterations 1–3, rebuilds every
generated artifact, verifies every candidate bit and address record, exhausts
the G243 projection range, checks pointwise nucleus identity, rejects binary
tampering, and verifies that no physical Golay artifact or protected-runtime
change entered the tree.

## Next bounded action

Iteration 4 may implement non-promotional Hash72 manifold and immutable-nucleus
validators against this candidate.  Canonical selection and runtime admission
remain blocked until the predecessor reconciliation gate is closed.
