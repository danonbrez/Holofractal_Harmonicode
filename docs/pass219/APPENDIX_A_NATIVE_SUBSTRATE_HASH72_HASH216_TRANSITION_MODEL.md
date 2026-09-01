# Pass 219 Appendix A — Native Substrate, Hash72 Primitive Language, and Hash216 Transition Model

Status: `NORMATIVE APPENDIX TO HHS-P219-NATIVE-RNA-TRANSCRIPTION-ABI-1.5.0`

This appendix freezes the low-level identity chain Pass 219 must expose through reusable ABI classes.

## A1. Authority ordering

```text
x86_64 host carrier / canonical byte transport
        ↓
C VM81 runtime nucleus
        ↓
ordered noncommutative reciprocal-phase computation over x,y,z,w
        ↓
Hash72 external VM81 state-change primitive
        ↓
three-Hash72 transition record
        ↓
per-character positional SHA-256 expansion
        ↓
Hash216 vector index / continuation record
```

The carrier, internal algebra, external primitive, and vector index are different typed views of one admitted transition lineage. They are not independent state authorities.

## A2. Internal digital-DNA state

The minimum native operator identity is:

```text
D = (x,y,z,w)
```

Registered ordered products retain order:

```text
xy != yx
zw != wz
```

where inequality denotes ordered source/phase identity unless an active exact constraint proves a particular projected equality.

A native phase transition witness MUST retain enough information to reconstruct the ordered operation that caused the Hash72 external transition primitive.

## A3. Hash72 external state-change primitive

A Hash72 state-change primitive is an ordered 72-position sequence:

```text
H = (g_0, ..., g_71)
```

Every occurrence has at minimum:

```text
glyph
position
transition identity
phase ancestry
lineage role
```

Hash72 is not a binary-memory alias. It is the runtime's externally exposed symbolic transition primitive generated from the internal native phase operation.

Because each occurrence survives into per-character Hash216 indexing, the Hash72 glyph stream is the native external token language for runtime transitions.

## A4. Hash216 transition triple

For one admitted operation:

```text
H_prev    : previous-state Hash72
H_change  : current state-change Hash72
H_receipt : resulting execution/closure receipt Hash72
```

The exact transition word is:

```text
W216 = H_prev || H_change || H_receipt
len(W216) = 216
```

Lane offsets are frozen:

```text
0..71     PREVIOUS
72..143   CHANGE
144..215  RECEIPT
```

Changing lane order changes transition identity.

## A5. Per-character SHA-256 relational index

Every `W216[i]` SHALL resolve one inherited domain-separated positional SHA-256 relational index record.

The exact existing preimage/domain-separation schema remains inherited. Pass 219 may wrap it but SHALL NOT silently replace it.

A logical record SHALL expose at least:

```text
transition_id
lane_role
lane_position
absolute_position_216
glyph
sha256_index_record
predecessor lineage
```

A whole-transition digest MAY be added as an integrity root but SHALL NOT replace the 216 positional records.

## A6. Primitive token identity vs token occurrence

The same Hash72 glyph MAY occur at multiple positions. Therefore:

```text
GLYPH_IDENTITY
!=
TOKEN_OCCURRENCE_IDENTITY
```

A token occurrence is qualified by position, lane role, and transition lineage.

This preserves a small native primitive alphabet while permitting exact contextual indexing without conflating repeated symbols.

## A7. Retrieval semantics

A Hash216 vector-store hit means:

```text
an authenticated previously computed transition/state candidate has been located
```

It does not mean:

```text
permission to mutate canonical state without current dependency/admission checks.
```

Normal continuation is:

```text
Hash216 lookup
→ authenticated predecessor verification
→ exact required-state decomposition
→ bounded hydration / delta computation
→ stable C ABI
→ VM81 admission
→ new Hash72 receipt
→ new Hash216 vector record
```

## A8. C++/C ABI requirements

Pass 219 SHALL expose reusable typed views equivalent to:

```cpp
struct Hash72TokenOccurrence;
struct Hash72PrimitiveView;
struct Hash216LaneView;
struct Hash216TransitionView;
struct Hash216IndexEntry;
struct NativePhaseWitness;
struct VM81TransitionView;
```

The stable C ABI representation MUST use fixed-width/versioned records, handles, offsets, byte spans, or another implementation-independent representation.

No C++ object layout crosses the stable public ABI directly.

## A9. Required invariants

```text
I-A01  internal ordered phase operation is recoverably bound to external Hash72 transition state
I-A02  every Hash72 transition primitive contains exactly 72 positions
I-A03  every Hash216 transition contains exactly three ordered Hash72 lanes
I-A04  every Hash216 transition therefore contains exactly 216 token occurrences
I-A05  every occurrence has one inherited positional SHA-256 relational index record
I-A06  per-position vector topology survives whole-record integrity hashing
I-A07  indexed retrieval never becomes independent VM81 mutation authority
I-A08  serialization/restart reproduces lane roles, positions, glyphs, SHA records, and predecessor lineage exactly
```


## A10. Compression-debt transfer at the native 5184 membrane

Pass 219 compression debt is unresolved computational obligation, not elapsed time.

At the native boundary:

```text
81 * 64 = 5184 bits
72 * 72 = 5184 Hash72 coordinates
3 * 72 = 216 Hash216 occurrences
```

A debt transfer may use Hash216 as its exact source/target address only when both transition records have all 216 inherited positional SHA-256 index records resolved.

A transfer record is therefore bound to:

```text
source transition216
target transition216
source layer
target layer
modality
amount
source slot5184
target slot5184
ordered phase pair
closure witness
```

and the receiver MUST record a reciprocal credit with exactly equal amount and identity.

Hash216 remains an index/witness layer. This transfer mechanism does not grant Hash216 mutation authority.

Additional invariants:

```text
I-A09  no anonymous compression debt crosses the native 5184 boundary
I-A10  every debt transfer source/target has complete 216-position SHA-256 indexing
I-A11  every transfer debit has one exact reciprocal receiving credit
I-A12  elapsed time is never represented as debt credit
```
