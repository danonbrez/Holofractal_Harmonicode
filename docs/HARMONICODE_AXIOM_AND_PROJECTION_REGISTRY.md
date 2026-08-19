# HARMONICODE Axiom and Projection Registry

Status: repository reference registry; normative Pass 219 requirements are in amendments 1.6.0–1.8.0 and Appendices D–H.

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

## 8. UQCEL projection records — amendment 1.7.0

The Universal Quantization Constraint Enforcement Law adds the following typed projection records.

| Projection ID | Source | Target | Preservation class | Reverse inference | Authority / validation |
|---|---|---|---|---|---|
| `PI-LOSHU-NUMERAL-v1` | Lo Shu tensor polynomial `L_H` | conventional integer numeral view | exact polynomial evaluation for registered `a^2,b^2,c^2` projection | exact for registered fixed polynomials | amendment 1.7.0 + UQCEL tests |
| `PI-U-PHASE-v1` | native `u` source state | cyclic phase-ring state `u_phase` | `N72` phase closure | requires native source/reconstruction witness | inherited `u^72` authority + Appendix G |
| `PI-U-QUANT-v1` | native `u` source state | dyadic metric state `u_q` | exact symbolic/rational scale relation | not inferred from scalar magnitude alone | amendment 1.7.0 + reference oracle |
| `PI-QR-XY-YX-v1` | odd reciprocity input pair `(p,q)` | ordered `xy/yx` orientation | reciprocity parity/orientation | input pair or equivalent witness required | amendment 1.7.0 + exhaustive odd residue audit |
| `PI-QR-U72-v1` | ordered `xy/yx` reciprocity orientation | `ZERO_L/N36 mod N72` phase address | exact half-cycle orientation | exact for the registered two-lane subdomain | exact ABI + UQCEL audit |

### 8.1 `u_phase` and `u_q` are not scalar aliases

```text
u_phase^N72 = a^2
```

and:

```text
u_q^N5256 * (b^2)^N66 = a^2
```

are type-distinct constraints. Neither may overwrite the other.

## 9. Native Universal Constraint Envelope records — amendment 1.8.0

The Universal Constraint Envelope is the native source program quantized by UQCEL. The following records make that authority order explicit.

| Projection ID | Source | Target | Preservation class | Reverse inference | Authority / validation |
|---|---|---|---|---|---|
| `PI-UCE-SOURCE-v1` | native UCE source expression | canonical ASCII machine fixture + SHA-256 identity | lexical nesting/order and source identity | exact only for the frozen fixture | amendment 1.8.0 + Appendix H |
| `PI-UCE-INTEGER-SYMMETRIC-v1` | typed native UCE | exact BigUInt tuple `(P,p,q,Delta,A,B)` with `P²=pq+Delta`, `A=B=P²`, `AB=P⁴` | represented integer/symmetric constraints | not sufficient for full native identity | exact UCE oracle + ABI tests |
| `PI-UCE-UQCEL-ADMISSION-v1` | integer/symmetric UCE projection + UQCEL witness + VM81 candidate | `ADMIT/REJECT` result and committed/zero VM81 frame | exact represented constraints and ordered QR phase | admission receipt/reconstruction witness required | exact ABI 1.8 gate |
| `PI-UCE-H216-LINEAGE-v1` | previous Hash72 + candidate/change + admission receipt material | 216-character previous/change/receipt triplet + Hash216 identity | ordered transition lineage | inherited Hash216 schema | exact ABI 1.8 receipt tests |
| `PI-UCE-FULL-SYMBOLIC-v1` | complete native UCE | future full typed AST/evaluator | not implemented in 1.8 | none | MUST return `UNSUPPORTED_DOMAIN` while residual mask is nonzero |

### 9.1 BigInt and no-float authority

`PI-UCE-INTEGER-SYMMETRIC-v1` uses canonical minimal big-endian non-negative integer views inherited from the Pass 133/211 BigInt authority. ABI byte bounds are transport limits, not conversion to machine floating point or `uint64_t` scalar authority.

### 9.2 Constraint gate classification

After the 1.8 implementation passes dependency-scoped validation, repository evidence SHALL distinguish:

```text
SUBSTRATE_COMPATIBLE = YES
ADMISSION_GATE_IMPLEMENTED = YES
ENFORCED_FOR_UQCEL_PROFILE = YES
FULL_SYMBOLIC_UCE_EVALUATED = NO
GLOBAL_LEGACY_INTERPOSITION = NO
```

`ENFORCED_FOR_UQCEL_PROFILE` means calls declaring the new UQCEL profile cannot commit a candidate VM81 frame without satisfying the registered gate. It does not mean all legacy execution surfaces are silently intercepted.

### 9.3 Full-symbolic residuals

The unresolved full-source clauses are explicitly represented by the residual mask:

```text
T_M_HARMONIC
TENSOR_S_F_AT_BT
DELTA_P_ROOT
MOD_F_U
```

Returning `UNSUPPORTED_DOMAIN` for that profile is mandatory fail-closed behavior until a later append-only implementation lowers those clauses exactly.
