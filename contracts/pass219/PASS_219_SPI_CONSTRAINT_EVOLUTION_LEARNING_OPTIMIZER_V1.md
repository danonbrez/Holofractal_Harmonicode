# Pass 219 — SPI Constraint/Evolution Learning Optimizer v1

Status: **ADDITIVE / EXACT / PROJECTION-ONLY / CANDIDATE OPTIMIZER**

## 1. Purpose

This contract makes the HARMONICODE evolution lifecycle executable as a
candidate-learning optimization membrane:

```text
FORMALIZE
-> PROVE
-> IMPLEMENT
-> OPTIMIZE
-> CANONIZE
-> ITERATE
```

The lifecycle is both a development process and a falsification/admission
filter.  A candidate that cannot survive the formalization, proof, and
implementation gates cannot enter optimization or emit a canonization/iteration
receipt.

This layer does not create a second transition authority.  It composes already
proved SPI tensor-translation receipts and exact VM81/Hydration coordinates.

## 2. Constructor theorem

For candidate `c`, define:

```text
G(c) = Formalized(c) ∧ Proved(c) ∧ Implemented(c)
```

Only candidates satisfying `G(c)` may enter the optimization set:

```text
A = { c | G(c) = TRUE }
```

For every admitted candidate:

```text
branch_count(c) ∈ Z+
reusable_branch_count(c) ∈ Z>=0
reusable_branch_count(c) <= branch_count(c)
unresolved_branch_count(c)
  = branch_count(c) - reusable_branch_count(c)
```

The exact deterministic selection rule is:

```text
arg min_c∈A (
  unresolved_branch_count(c),
  -reusable_branch_count(c),
  stable_candidate_id(c)
)
```

No floating objective participates.

## 3. 5,184 knowledge-coordinate binding

Every learning candidate carries one exact VM81 knowledge coordinate:

```text
address5184 = cell81 * 64 + operation64
0 <= address5184 < 5184
```

with exact inverse:

```text
cell81      = address5184 // 64
operation64 = address5184 % 64
```

The candidate also carries one of the four hydration-lane identities.  The
lane is typed metadata and does not create inter-lane canonical transition
authority.

The resulting candidate coordinate is therefore:

```text
(hydration_lane4, cell81, operation64, address5184)
```

The four hydration lanes remain coordinated views of the same singleton VM81
admission architecture.

## 4. Predecessor proof requirement

A candidate is constructible only above the closed SPI tensor-pair translation
stack:

```text
EQUAL_SUM_A2_NORMALIZATION
-> FIBONACCI_PYTHAGOREAN_SCALE
-> TENSOR_PAIR_CUBIC_THREE_SET
```

The predecessor must preserve:

```text
a² = 1                 local scalar scale
∆  = 1                 universal denominator
a²+b²=c²               exact scaling seed
t³=t+a²                 tensor-pair three-set relation
native t unsolved
native tensor identity uncollapsed
projection-only authority
```

## 5. Learning interpretation

The optimizer treats symbolic parameter states, proof branches, tensor
translations, reusable proof subgraphs, and exact execution coordinates as
candidate learning state.

The core update is:

```text
current canonized/proved structure
+ candidate extensions
-> constraint/proof gate
-> exact structural optimization
-> selected candidate receipt
-> next-cycle FORMALIZE seed
```

This is deliberately broader than scalar gradient descent.  The optimized
objects may include:

- symbolic parameter/weight structures;
- tensor decompositions;
- proof strategies;
- formal-system translation tensors;
- branch routing;
- reusable Hash216/vector-store references;
- exact execution-coordinate assignments;
- later optimization procedures represented as candidates themselves.

The v1 implementation optimizes exact branch-reuse work only.  It does not
claim a measured latency or compression improvement.

## 6. Semantic ordering invariant

Semantic meaning is downstream of algebraic/computational admission.

A candidate may carry a `semantic_label`, but:

```text
semantic_label_has_selection_authority = FALSE
```

Selection is determined only by the exact typed computational objective and
closed predecessor constraints.

Therefore:

```text
SemanticDescription(c) != AdmissionAuthority(c)
```

and neither favorable nor unfavorable natural-language framing may bypass or
block the formal lifecycle gates.

## 7. Canonization semantics

The optimizer may emit:

```text
CANONIZE = PROJECTION_RECEIPT_ELIGIBLE
```

This means that the selected candidate has survived this projection optimizer
cycle and may be registered/frozen as proof evidence.

It does **not** mean:

- merged to repository `main`;
- admitted as canonical VM81 state;
- authorized to commit Hash72;
- authorized to mint canonical Hash216;
- authorized to persist canonical state.

Repository canonization remains a repository/integration event.  VM81 state
canonization remains the existing singleton admission event.

## 8. Iteration rule

A successful optimizer cycle emits a deterministic next-cycle seed containing:

```text
selected candidate id
selected candidate receipt SHA-256
VM5184 address
hydration lane
symbolic parameter state
next_cycle = FORMALIZE
canonical_state_mutation = FALSE
```

Thus canonization is not an endpoint:

```text
C_n + ∆_n
-> FORMALIZE
-> PROVE
-> IMPLEMENT
-> OPTIMIZE
-> CANONIZE
-> ITERATE
-> C_(n+1)
```

The next cycle must independently traverse its own proof and implementation
gates.

## 9. Hash216/vector-store relationship

The selected candidate is eligible to become Hash216/vector-store reference
metadata so proved subgraphs can be reused by later cycles.

v1 explicitly records:

```text
hash216_vector_store_reference_eligible = TRUE
canonical_hash216_minted = FALSE
```

A later integration may bind the candidate receipt to the repository's existing
Hash216 vector-store APIs.  That binding must preserve the existing Hash216
lineage and singleton VM81 authority instead of defining a second hash/state
authority.

## 10. Falsification conditions

The candidate or cycle fails closed when any of the following occurs:

- FORMALIZE, PROVE, or IMPLEMENT is not `PASS`;
- predecessor tensor translation is not closed;
- a floating-point objective appears;
- branch/reuse work conservation fails;
- `reusable_branch_count > branch_count`;
- VM5184 coordinate does not round-trip exactly;
- hydration lane is outside `0..3`;
- receipt SHA-256 does not match the canonical JSON body;
- semantic metadata is granted selection authority;
- candidate attempts VM81/Hash72/Hash216/persistence authority;
- no candidate survives the formal proof/implementation gates.

These conditions implement the rule that a false, malformed, or unsupported
candidate cannot traverse the complete lifecycle merely through description.

## 11. Empirical-claim boundary

The structural optimizer uses exact integer work units.  It does not infer
runtime speedup from branch-count reduction.

A latency, throughput, memory, compression, or energy claim requires its own
measured benchmark and receipt.  Existing repository performance evidence may
be referenced independently, but v1 does not retroactively claim that this
optimizer caused those measurements.

## 12. Authority boundary

The following are invariant:

```text
candidate_only = TRUE
canonical_admission = FALSE
vm81_mutation = FALSE
canonical_hash72 = FALSE
canonical_hash216 = FALSE
canonical_persistence = FALSE
floating_point = FALSE
```

The optimizer ranks candidates.  It does not replace VM81 admission.

## 13. Required executable artifacts

```text
hhs_spi_constraint_evolution_optimizer_v1.py
hhs_spi_constraint_evolution_optimizer_tests_v1.py
hhs_spi_scalar_projection_registry_v6.py
hhs_spi_scalar_projection_registry_tests_v6.py
.github/workflows/pass219-spi-constraint-evolution-v6.yml
```

The v6 registry is an additive successor to v5 and must prove that every v5
proof object is byte/field-equivalent under `to_dict()` while adding only the
constraint/evolution optimizer proof.
