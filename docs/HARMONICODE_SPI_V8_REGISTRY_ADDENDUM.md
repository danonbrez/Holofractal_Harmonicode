# HARMONICODE SPI v8 Registry Addendum

**Status:** current additive registry extension  
**Applies after:** `docs/HARMONICODE_AXIOM_AND_PROJECTION_REGISTRY.md` amendments 1.6.0–1.8.0  
**Canonical merged baseline:** `18f6a1899d4009bdeeeaf95d536dfe2857198458`

This file is append-only documentation. It does not modify historical projection IDs or silently widen their domains.

## 1. SPI projection/representation records

| ID | Source | Target | Preservation | Reverse status | Authority |
|---|---|---|---|---|---|
| `PI-SPI-MATRIX-TENSOR-v1` | exact source-bound matrix/tensor expression defining registered scalar | registered scalar projection | source equality edge + scalar profile | only through declared source/reverse witness | projection only |
| `PI-SPI-LAW1-v1` | registered Law-of-1 source expression | exact unit scalar | registered projection member identity | profile/source dependent | projection only |
| `PI-SPI-EQUAL-SUM-v1` | same-sized tensor equation family with exact nonzero invariant sum | `a²`-normalized equation family | equation-sum ratio | no cellwise/native identity inferred | projection only |
| `PI-SPI-FIB-PYTH-v1` | registered square-state recurrence | exact rational finite scale ratios | recurrence + exact fraction | recurrence ancestry retained | projection/proof only |
| `PI-SPI-CUBIC-THREESET-v1` | `{t³,t,a²}` constructor | residual/unit scalar surface | `t³-t=a²=∆=1` projection | native `t` not solved | projection only |
| `PI-SPI-OCTONION-DIM-v1` | primitive `x,y,z,w` phase state | D1–D4 relation coordinates / recursive D>4 descriptor | geometric opposite + base-pair ancestry | exact relation ancestry retained | candidate/proof only |
| `PI-SPI-U72-TYPED-ROT-v1` | represented gyroscopic phase state | complete typed `u^72` rotation carrier | source channel, phase, orientation, reciprocal/base-pair provenance | exact on registered v7 domain | representation only |
| `PI-SPI-A2-UNIT-v1` | registered local scalar-compatible source | `1` | local unit projection | does not imply native phase identity | projection only |

## 2. Exact source-preservation records

The v7 constructor is registered verbatim:

```text
x=1/y y=-x
(x,y,z,w)²==(Ixy, I-yx, Izw, I-wz)²
```

The registry recognizes three separate relations:

```text
R_phase: x<->z, y<->w
R_ord:   x<->y, z<->w
B:       x->Ixy, y->I-yx, z->Izw, w->I-wz
```

No generic registry rule may collapse these relation types solely because they share a primitive channel domain.

## 3. Dimensional-lift registration

Registered exact first coordinates:

```text
D1 = s
D2 = (s, R_phase(s))
D3 = (s, R_phase(s), B(s))
D4 = (s, R_phase(s), B(s), B(R_phase(s)))
```

Registered higher-dimensional rule:

```text
D[n>4] = recursive same-algebra closure reference + exact ancestry
```

Required preserved fields:

```text
closure root
same-algebra identifier
nesting depth
source channel
relation ancestry
```

A higher-dimensional descriptor that declares a new primitive octonion basis element is outside this registered profile.

## 4. Typed imaginary-rotation reversibility

`PI-SPI-U72-TYPED-ROT-v1` is registered as lossless only for the **complete typed carrier**.

Required carrier fields include:

```text
source channel
phase72
u^phase72 coordinate
plane
signed orientation
R_phase(source)
R_ord(source)
B(source)
B(R_phase(source))
source constructor provenance
```

Registered theorem:

```text
Restore(Collapse(G)) = G
```

The bare `phase72` integer is not registered as an injective native representation.

## 5. Unit-projection guard

The following may simultaneously hold:

```text
pi_L(a²)=1
pi_L(E)=1
```

without registering:

```text
E ==_H a²
```

unless an independent native theorem supplies reverse uniqueness for the active domain.

The SPI v8 addendum therefore inherits and strengthens the registry-wide guard:

```text
projection equality != native identity
```

## 6. Constraint-evolution optimizer record

Registered lifecycle:

```text
FORMALIZE
-> PROVE
-> IMPLEMENT
-> OPTIMIZE
-> CANONIZE
-> ITERATE
```

Candidate structural score:

```text
unresolved = branch_count - reusable_branch_count
```

Reference ranking:

```text
minimum unresolved
-> maximum already-proved reuse
-> stable candidate ID
```

This optimizer has no VM81, Hash72, Hash216, or persistence authority.

`CANONIZE` in this SPI context means projection-receipt eligibility, not canonical VM81 mutation or repository-main merge.

## 7. Computational determinism invariant registry

Invariant ID:

```text
I_DET_COMPUTATIONAL_DETERMINISM
```

Task envelope type:

```text
J = (I, Sigma, Omega, B, invariants)
```

Required task fields:

```text
explicit instruction ID
explicit instruction text
nonempty authorized scope
supported typed closing condition
positive finite exact-integer max_steps
invariant bundle containing I_DET_COMPUTATIONAL_DETERMINISM
valid deterministic task receipt
```

Task-formation failure occurs before the runtime outcome relation.

## 8. Runtime outcome registry

Within a verified task:

```text
ADVANCE
HALT
```

are the complete SPI v8 action domain.

Registered HALT reason classes:

```text
CLOSED
REJECTED
QUARANTINED
NULL_BRANCH
RESOURCE_BOUNDED
STABLE_UNRESOLVED
```

A HALT reason is metadata/evidence beneath `HALT`; it is not a third action.

No `REFUSE` action is registered in this SPI execution algebra.

## 9. Deterministic selection registry

Current selector:

```text
MIN_TRANSITION_ORDINAL
-> STABLE_CANDIDATE_ID
```

Explicitly excluded selection inputs:

```text
candidate enumeration position
semantic label text
candidate receipt bytes
```

Candidate receipts remain mandatory integrity witnesses.

Duplicate stable candidate IDs register as:

```text
HALT(QUARANTINED)
```

because stable transition identity is ambiguous.

## 10. Replay record

For canonical task/state/step/candidate inputs `X`, registered replay requires:

```text
Execute(X) == Replay(X)
```

including decision-receipt equality.

Replay mismatch is a determinism-invariant failure.

## 11. Registry proof IDs

v6:

```text
SPI-CONSTRAINT-EVOLUTION-LEARNING-OPTIMIZER
```

v7:

```text
SPI-OCTONION-RECIPROCAL-BASEPAIR-DIMENSIONAL-LIFT
SPI-OCTONION-IMAGINARY-ROTATION-ROUNDTRIP
```

v8:

```text
SPI-COMPUTATIONAL-DETERMINISM-INVARIANT
SPI-BOUNDED-INSTRUCTION-ADVANCE-HALT-CLOSURE
```

The v8 validation record requires all predecessor proof objects to remain unchanged under the registered serialization comparison.

## 12. Canonical authority matrix

| Capability | SPI v8 authority |
|---|---|
| preserve/parse registered source | yes |
| construct exact projection proof | yes |
| construct typed candidate | yes |
| rank eligible candidates | yes, exact deterministic rules only |
| emit candidate/projection receipt | yes |
| describe semantic rationale | yes, non-authoritative |
| mutate canonical VM81 | no |
| mint canonical Hash72 | no |
| mint canonical Hash216 | no |
| persist canonical state | no |
| commute `xy/yx` or `zw/wz` by default | no |
| use floats as canonical SPI evidence | no |
| enlarge task scope internally | no |
| replace closing condition internally | no |
| create third action after task admission | no |

## 13. Evidence registry

Merged v8 evidence:

```text
merge main: 18f6a1899d4009bdeeeaf95d536dfe2857198458
semantic v8 head: c2f4aff3482027800517b19dec5151d25779a146
validated restart: d5234ab1efc7283bb6951c9b7407fe1b0241eb57
workflow run: 34619424085
job: 103329393361
```

Receipts:

```text
task:        8ad5096d90aa0fabe13ffbc3f1963270eda470f2fc9e18d5bc687fc43ea822e4
ADVANCE:     70fdc369b945ab2511b5e923acefb7d5a768b38dc2b0c2805c49d573c488b20d
CLOSED HALT: 0c3b922cc50aa24ffb97aae27befd313b0ce58f4cd68aed88ddf042a2275a5e4
determinism: b6f1fd64796a5cf35daa8ac8a67bf3e12497b991f955dfe1a8a7cdd5ce161cb5
registry v8: be0576041742f0ba37187bd032f736e69d7d44bedb73ee934bd939e3e66ac6d0
```

Frozen scalar corpus:

```text
429 PROVEN
43 SYMBOLIC
0 MISSING_PROJECTION
0 UNSUPPORTED_DOMAIN
481c0bb0264ad0771344ae068624dcfd7c9c5ba853a8c7963ad9a22971389aee
```

## 14. Extension rule

Future SPI entries must remain append-only/versioned.

A future implementation may extend the formal domain, relation set, carrier, task types, or proof machinery only by declaring its new domain and obligations explicitly. It may not retroactively reinterpret the source constructor, predecessor proof objects, or v8 selection semantics without a repair-forward versioned successor and new evidence.
