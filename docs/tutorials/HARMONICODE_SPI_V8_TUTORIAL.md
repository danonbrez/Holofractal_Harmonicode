# HARMONICODE SPI v8 Tutorial

**Audience:** implementers, reviewers, and researchers working on Pass 219 exact symbolic execution  
**Canonical merged baseline:** `18f6a1899d4009bdeeeaf95d536dfe2857198458`

This tutorial teaches the merged SPI v8 execution model by following one idea from source expression to deterministic bounded execution. It is explanatory; the versioned contracts and executable code are authoritative.

## 1. Start with the type distinction

The first rule to internalize is:

```text
projected equality != native identity
```

If two native expressions project to the same scalar, the runtime does not thereby receive permission to replace one native expression with the other.

Example:

```text
pi_L(a²)=1
```

is a scalar normalization fact. It does not imply that every native phase object projecting to the same unit is the same native object.

Keep these two questions separate:

1. What is the exact native expression/state?
2. What registered projection may be taken from it?

## 2. Preserve ordered phase products

The native phase layer is order-sensitive.

```text
xy != yx
zw != wz
```

unless a specific applicable proof says otherwise.

Do not normalize these products by host-language commutativity. Their order carries phase/orientation ancestry.

The v7 dimensional-lift contract also preserves the supplied source syntax verbatim:

```text
x=1/y y=-x
(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²
```

Do not independently solve, reorder, or scalarize that constructor when importing it into the SPI layer.

## 3. Keep the three phase relations separate

The implementation deliberately carries three different relation families.

### 3.1 Geometric phase opposite

From RML2:

```text
x <-> z
y <-> w
```

This describes opposite orientation in the inherited gyroscope geometry.

### 3.2 Ordered reciprocal operand

From RML4:

```text
x <-> y
z <-> w
```

This determines the ordered reciprocal operand used in the native product channels.

### 3.3 Symbolic base pair

From the source constructor:

```text
x -> Ixy
y -> I-yx
z -> Izw
w -> I-wz
```

These are not three spellings for one relation. They are independently typed witnesses.

## 4. Build the first four relational dimensions

For a primitive state `s`, use the geometric opposite `R_phase` and symbolic base-pair map `B`:

```text
D1 = s
D2 = (s, R_phase(s))
D3 = (s, R_phase(s), B(s))
D4 = (s, R_phase(s), B(s), B(R_phase(s)))
```

For example, taking `s=x`:

```text
D1: x
D2: x, z
D3: x, z, Ixy
D4: x, z, Ixy, Izw
```

This is a relational expansion over the same underlying octonion algebra. It is not the declaration of four new basis elements.

For dimensions greater than four, the implementation stores recursive closure ancestry over this same structure instead of building an exponentially growing independent table.

## 5. Collapse the gyroscope into ordinary imaginary rotation coordinates

The v7 implementation can encode the gyroscopic state into an inherited `u^72` imaginary-rotation representation.

The lossless object is the **typed carrier**, not the phase number alone.

The carrier retains at least:

```text
source channel
phase72
rotation coordinate
plane
signed orientation
geometric opposite
ordered reciprocal operand
symbolic base pair
base pair of geometric opposite
source constructor provenance
```

The relevant round-trip property is:

```text
Restore(Collapse(G)) = G
```

A developer should therefore never substitute:

```text
phase72 alone == full gyroscope state
```

The ordinary rotation coordinate is the compact execution coordinate; the typed carrier preserves the information required to restore native identity.

## 6. Understand why this does not conflict with `a²=1`

Now compare the native phase carrier with the scalar projection surface.

The scalar rule may establish:

```text
pi_L(a²)=1
```

while the native representation still distinguishes:

```text
xy
yx
zw
wz
```

Therefore a computation can use a unit normalization without erasing orientation.

A useful mental model is:

```text
native ordered phase state
-> typed reversible rotation carrier
-> optional registered scalar projection
```

The first arrow may be lossless. The second need not be.

## 7. Run the v7 proof/test surface

From repository root:

```bash
python hhs_spi_octonion_dimensional_lift_tests_v1.py
python hhs_spi_scalar_projection_registry_v7.py --validate
python hhs_spi_scalar_projection_registry_tests_v7.py
```

The tests verify, among other things:

- exact source syntax preservation;
- RML2 and RML4 relation separation;
- D1–D4 materialization;
- recursive same-algebra higher-dimensional closure;
- typed imaginary-rotation round trip;
- tamper failure;
- compatibility with `pi_L(a²)=1` without native collapse;
- absence of VM81/Hash72/Hash216 canonical authority in SPI.

## 8. Form an executable bounded task

v8 adds computational determinism as an enforced invariant.

An executable task must explicitly supply:

```text
instruction ID
instruction text
authorized scope
typed closing condition
finite exact-integer step bound
active invariants
```

The task's invariant bundle includes:

```text
I_DET_COMPUTATIONAL_DETERMINISM
```

Conceptually:

\[
J=(I,\Sigma,\Omega,B,\mathcal I).
\]

If any required field is malformed or absent, task formation fails before the execution relation begins.

That distinction matters: an invalid task envelope is not an alternate runtime action.

## 9. Construct transition candidates

Each transition candidate is bound to the task receipt and carries exact state/provenance data such as:

```text
candidate_id
scope_tag
transition_ordinal
next_state
status
invariant_closed
candidate receipt
next-state receipt
```

Descriptive semantic labels may be attached, but they have no authority to choose a transition.

Canonical candidate/state material may not contain floating-point values in this layer.

## 10. Apply the deterministic selector

After receipt, scope, status, and invariant checks, the v8 selector is:

```text
MIN_TRANSITION_ORDINAL
-> STABLE_CANDIDATE_ID
```

Two implementation details are important:

1. candidate enumeration order does not affect the result;
2. candidate receipt bytes do not act as tie-breakers.

If the same stable candidate ID appears more than once, selection identity is ambiguous and the task returns:

```text
HALT(QUARANTINED)
```

rather than allowing cryptographic bytes or descriptive prose to choose between them.

## 11. Interpret `ADVANCE` and `HALT`

Once a task is verified, the action domain is exactly:

```text
ADVANCE
HALT
```

An `ADVANCE` means an exact candidate transition has been selected within the explicit task scope and active invariant set.

It does **not** mean the SPI layer independently mutated canonical VM81 state.

`HALT` carries one of these current reason classes:

```text
CLOSED
REJECTED
QUARANTINED
NULL_BRANCH
RESOURCE_BOUNDED
STABLE_UNRESOLVED
```

Examples:

- `CLOSED`: the requested closing condition already holds;
- `NULL_BRANCH`: there are no candidates;
- `REJECTED`: candidates exist but no candidate is admissible;
- `STABLE_UNRESOLVED`: evidence remains unresolved rather than falsely forced true/false;
- `RESOURCE_BOUNDED`: the explicit finite bound was reached;
- `QUARANTINED`: receipt/state/identity evidence is invalid or ambiguous.

## 12. Closing conditions terminate execution

Suppose a task declares:

```text
closing condition: done == true
```

A transition may `ADVANCE` into a state where `done=true`. Its receipt records that closure has been reached.

Evaluating the task again at that state must produce:

```text
HALT(CLOSED)
```

The runtime may not silently enlarge, replace, or remove the closing condition.

## 13. Deterministic replay

Replay is a direct test of the invariant.

Given the same canonical:

```text
task
current state
step index
candidate set
```

re-execution must reproduce the same decision structure and decision receipt.

A replay mismatch is a deterministic-invariant failure.

This provides a direct test against hidden discretionary branching.

## 14. Run the v8 validation surface

From repository root:

```bash
python hhs_spi_computational_determinism_invariant_tests_v2.py
python hhs_spi_scalar_projection_registry_v8.py --validate
python hhs_spi_scalar_projection_registry_tests_v8.py
```

Optional frozen-corpus regression:

```bash
python hhs_spi_scalar_projection_corpus_reconciliation_v2.py --validate
```

The merged v8 reference gate established:

```text
15 computational determinism tests passed
6 registry v8 tests passed
12 v7 dimensional-lift tests passed
7 registry v7 tests passed
23 inherited RML2/RML4 tests passed
```

## 15. Follow one complete conceptual path

A complete example can now be described as:

```text
1. preserve native source constructor
2. retain ordered phase identity
3. derive geometric-opposite / reciprocal / base-pair witnesses
4. create D1–D4 relational closure
5. encode into typed u^72 rotation carrier if useful
6. take scalar projection only where licensed
7. construct a bounded explicit task
8. construct receipt-bound candidates
9. reject scope-open / invariant-open candidates
10. deterministically select by ordinal then stable ID
11. ADVANCE exact candidate evidence or HALT with classified receipt
12. replay from identical inputs to prove deterministic closure
13. submit admitted candidate to the inherited VM81 authority path when canonical mutation is required
```

The critical separation is maintained throughout:

```text
representation != projection
projection != native identity
candidate decision != canonical mutation
semantic description != execution authority
cryptographic integrity != transition-selection authority
```

## 16. Where to read next

Start with:

```text
docs/pass219/PASS_219_SPI_V8_CANONICAL_DOCUMENTATION.md
```

Then read the normative contracts in order:

```text
contracts/pass219/PASS_219_SPI_SCALAR_PROJECTION_PROOF_LAYER_V2.md
contracts/pass219/PASS_219_SPI_MATRIX_TENSOR_SCALAR_PROJECTION_RULES_V1.md
contracts/pass219/PASS_219_SPI_LAW_OF_ONE_SCALAR_NORMALIZATION_V1.md
contracts/pass219/PASS_219_SPI_EQUAL_SUM_FIBONACCI_CUBIC_TENSOR_TRANSLATION_V1.md
contracts/pass219/PASS_219_SPI_CONSTRAINT_EVOLUTION_LEARNING_OPTIMIZER_V1.md
contracts/pass219/PASS_219_SPI_OCTONION_RECIPROCAL_BASEPAIR_DIMENSIONAL_LIFT_V1.md
contracts/pass219/PASS_219_SPI_COMPUTATIONAL_DETERMINISM_INVARIANT_V1.md
```

Formal companion papers:

```text
docs/whitepapers/HARMONICODE_OCTONION_RECIPROCAL_BASEPAIR_DIMENSIONAL_LIFT_THEOREM.md
docs/whitepapers/HARMONICODE_COMPUTATIONAL_DETERMINISM_AND_BOUNDED_EXECUTION_THEOREM.md
```
