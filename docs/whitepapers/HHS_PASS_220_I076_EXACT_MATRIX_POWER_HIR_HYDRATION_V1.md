# HHS Pass 220 I076 — ExactMatrixPower HIR Hydration

## Scope

I076 begins from merged I075 main `cc8c47ee2f654215ace2677e213c6e7c8d531107`.

It lowers the two typed native HARMONICODE rectangular tensor-power nodes into
the Pass169 canonical HIR type:

```text
ExactMatrixPower
```

The exact source nodes remain:

```text
MatrixPower[M_wz,x^2]
MatrixPower[M_xy,x^4]
```

with 4x2 base shape and exponent tokens `x^2` and `x^4`.

## Pass169 alignment

Pass169 registers `ExactMatrixPower` as a matrix/tensor type and requires
historical `NcalcMatrixPower` forms to lower to exact symbolic matrix-power
nodes rather than becoming floating-point host calculations.

I076 binds that rule directly:

```text
source node
-> typed I075 rectangular tensor-power AST
-> ExactMatrixPower HIR node
```

It does not add an ordinary linear-algebra interpretation.

## HIR node contract

Each HIR node records:

- canonical type = `ExactMatrixPower`;
- node kind = `EXACT_SYMBOLIC_MATRIX_POWER`;
- Pass169 contract identity;
- exact source-node string;
- exact 4x2 base shape;
- exact exponent token;
- ordered source cells and their root;
- source identity preserved;
- ordered topology preserved;
- host MatrixPower evaluation = false;
- square-matrix requirement imported = false;
- numeric exponent evaluation = false;
- matrix-power value derived = false;
- VM81 execution verified = false;
- VM81 admission required = true.

This is therefore an exact lowering stage, not a premature execution claim.

## Hydration

I076 binds:

```text
PREVIOUS = Hash72(I075 parent + source bundle)
CHANGE   = Hash72(ExactMatrixPower HIR forest)
RECEIPT  = Hash72(source/topology/authority witnesses)
```

into a 216-position candidate.

Inherited I065 hydration must reconstruct:

```text
3 * 5184 = 15552
```

attached components and recompress exactly.

The expanded geometry remains validation material and is not persisted by I076.

## Wolfram formalization

Connected-kernel evidence:

```text
status = PASS
checks = 26 / 26
canonical type = ExactMatrixPower
node kind = EXACT_SYMBOLIC_MATRIX_POWER
node count = 2
shapes = 4x2, 4x2
ordered cell occurrences = 16
host MatrixPower evaluations = 0
numeric exponent evaluations = 0
matrix-power values derived = 0
VM81 executions verified = 0
VM81 admission required = true
Hash216 width = 216
full attached components = 15552
```

Wolfram does not execute the rectangular MatrixPower nodes.

## Lean 4

Native module:

```text
HHS.Pass220.I076
```

proves:

- exact Pass169 type and HIR node tags;
- exactly two HIR nodes;
- exact source nodes;
- exact 4x2 shapes;
- exact exponent tokens;
- source and topology preservation;
- no host MatrixPower/square-matrix import;
- no numeric exponent or value derivation;
- no VM81 execution claim;
- VM81 admission remains required;
- `72*72=5184`;
- `3*5184=15552`;
- inherited I075 node count and hydration;
- compact persistence and authority boundaries.

## Authority

I076 remains candidate-only.

It does not grant:

- host MatrixPower authority;
- ordinary square-matrix semantics;
- numeric exponent authority;
- matrix-power value derivation authority;
- VM81 execution/admission authority;
- VM81 mutation authority;
- canonical Hash72/Hash216 commit authority;
- canonical persistence authority;
- projection substitution;
- floating-point authority;
- external-egress authority.

The next implementation tranche is an actual VM81-native execution surface for
source-bound `ExactMatrixPower` HIR nodes. That future surface must preserve the
native 4x2 semantics and emit execution evidence before admission.
