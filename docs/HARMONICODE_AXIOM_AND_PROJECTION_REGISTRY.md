# HARMONICODE Axiom and Projection Registry

Status: repository reference registry; normative Pass 219 requirements are in amendment 1.6.0 and Appendices D–F.

## 1. Automatically shared foundational axiom classes

| ID | Class | Native status | Notes |
|---|---|---|---|
| `H-A1` | Formal deduction | Shared foundational | Inference must follow registered premises/rules. |
| `H-A2` | Symbolic logic | Shared foundational | Operators remain typed; syntax does not imply conventional semantics before resolution. |
| `H-A3` | Higher-dimensional tensor algebra | Shared foundational | Tensor composition/coordinates remain typed; coordinate projection may lose information. |
| `H-A4` | Euclidean geometry | Shared foundational | Euclidean geometric relations are available at the foundational geometry layer; later geometric formalisms require registration. |

No other conventional STEM axiom is automatically native.

## 2. Initial projection registry

| Projection ID | Source | Target | Preservation class | Reverse inference | Authority / validation |
|---|---|---|---|---|---|
| `PI-VM81-BYTES-v1` | VM81 frame | 648-byte little-endian x86_64-aligned carrier | exact serialization | exact | merged VM81 exact kernel/ABI |
| `PI-X64-TRANSPORT-v1` | x86_64 instruction/byte stream | exact ABI byte transport | byte identity | exact byte round-trip | Pass 175/186 + merged exact ABI |
| `PI-VM5184-OP-v1` | VM81 operation state | `(cell81,operation64)` | typed coordinate | exact where inherited mapping defined | VM81 contracts |
| `PI-H72-5184-v1` | Hash72 token occurrence | `(position72,glyph72)` 5,184 plane | position/glyph occurrence | exact occurrence round-trip | exact kernel/ABI + Hash72 contract |
| `PI-H216-v1` | VM81 transition lineage | previous/change/receipt positional vector | transition/token lineage | reconstruction by inherited schema | Hash216 contract |
| `PI-HYDRATION-189-219-v1` | `(operation64,g243)` | `(trit,slot5184)` | bijective local coordinate | exact | Pass 219 Appendix B |
| `PI-SCALAR-ORDINARY-v1` | explicitly scalar-compatible native value | ordinary scalar representation | projection-local scalar laws | profile-dependent | explicit scalar type only |
| `PI-COMPLEX-COMPAT-v1` | registered phase state | conventional complex notation | profile-defined | not assumed | explicit phase/complex projection |
| `PI-MODULAR-v1` | registered native integer/phase state | residue class | residue preservation | requires lift/witness | modulus-specific profile |
| `PI-RNA-COMPAT-v1` | native x,y,z,w transcription state | conventional nucleotide/biological representation | declared biological/format relations only | not assumed | Pass 219 mapping tests |

## 3. Projection fields required before implementation

Every new projection participating in canonical Pass 219 lowering must register:

```text
projection_id
version
source_type
target_type
domain_predicate
forward_rule
reverse_rule_or_none
preserved_invariants
intentionally_lost_information
injectivity_class
reversibility_class
canonical_serialization
validation_oracle
```

## 4. Native identity guard

Repository-wide default:

```text
projection equality != native identity
```

unless the registry entry establishes reverse uniqueness for the active domain.

## 5. Projection-local law guard

A conventional law is binding when its registered projection declares it. It does not automatically propagate upward into unrelated native types.

Examples:

```text
ordinary scalar projection: 0 != 1
native ordered phase: xy and yx retain order
closure projection: zero-residue may correspond to renewed-unit under explicit u^72 closure witness
x86_64 transport: byte equality is byte equality, not automatically complete native semantic identity.
```

## 6. Claim-type registry rule

Papers/contracts should label statements using:

```text
DEFINITION
AXIOM
DERIVED_THEOREM
PROJECTION_THEOREM
IMPLEMENTATION_THEOREM
EMPIRICAL_CLAIM
CONJECTURE.
```

External scientific/biological correspondence is never promoted to a native theorem solely by notation.

## 7. Extension rule

New registry entries are append-only/versioned. A discovered counterexample to an injectivity, reversibility, or preservation claim requires a repair-forward version change and evidence; the domain must not be silently narrowed after the fact to erase the counterexample.
