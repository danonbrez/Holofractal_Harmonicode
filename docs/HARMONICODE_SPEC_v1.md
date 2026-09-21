# HARMONICODE_SPEC_v1

## 0. Purpose

HARMONICODE is a symbolic programming language for audited constraint-state execution.

A HARMONICODE program is not merely a sequence of statements. A program prompt containing multiple equations, chained equalities, list equations, gate declarations, JSON-like blocks, or Python-like function operations is interpreted as a single virtual state machine whose global constraints must be reconciled through the kernel.

The language is designed for:

- custom HHS algebra
- ordered non-commutative symbolic products
- JSON/Python-style program declarations
- calculator expressions
- kernel-audited state transitions
- compiler/interpreter execution
- replayable receipts
- future IDE, AI assistant, DAW, and FFI integration

Core runtime path:

```text
Source -> Parse -> AST -> Constraint Graph -> HARMONICODE IR -> Kernel Audit -> Receipt -> Replay
```

No expression that mutates symbolic state is valid unless it can be lowered into audited IR and checked by the runtime invariants.

---

## 1. Global invariants

Every executable program must preserve:

```text
Δe = 0
Ψ = 0
Θ15 = true
Ω = true
```

Interpretation:

- `Δe=0`: no entropy drift across state transition.
- `Ψ=0`: no semantic drift across projection or expansion.
- `Θ15=true`: Lo Shu / harmonic balance witness holds.
- `Ω=true`: recursive closure / replay closure holds.

If any invariant fails, the interpreter/compiler must emit quarantine or null execution, not fallback success.

---

## 2. Program model

A program is a `ConstraintStateMachine`:

```json
{
  "kind": "ConstraintStateMachine",
  "constraints": [],
  "operations": [],
  "bindings": {},
  "gates": [],
  "receipts": []
}
```

All top-level equations in a source prompt are jointly active unless explicitly scoped.

Example source:

```harmonicode
xy≠yx≠zw≠wz
xy=1/zw=-yx
zw=1/xy=-wz
```

This parses as one global state machine containing three coupled constraints, not three unrelated lines.

---

## 3. Lexical forms

### 3.1 Symbols

Symbols may include ASCII and selected mathematical Unicode:

```text
x y z w X Y A B P p q a b c d e f n m t u O Q R_K QGU PHI I π ρ Π₂
```

Unicode aliases:

```text
π   -> Pi
√   -> Sqrt
ρ   -> rho
φ   -> phi
ψ   -> psi
χ   -> chi
δ   -> delta
τ   -> tau
≠   -> Neq
==  -> Eq
=   -> BindEq / ChainEq depending context
:=  -> DefineGate
```

### 3.2 Numbers

Supported numeric atoms:

```text
integer
rational
signed rational
fixed decimal boundary literal
scientific notation boundary literal
```

Kernel layer prefers exact rational encoding. Decimal literals such as `179971.179971` are represented internally as rational boundary literals:

```text
179971179971 / 1000000
```

### 3.3 Powers and roots

```text
x^2
x²
u^72
√xy
Sqrt((xy))
RealSurd(Sqrt(2),72)
```

Unicode superscripts normalize into explicit `Power(base, exponent)` nodes.

---

## 4. Operators

### 4.1 Ordered product

HARMONICODE preserves ordered products.

```text
xy != yx
zw != wz
x*y != y*x unless projection explicitly collapses them
```

Forms:

```text
xy          // fused ordered product symbol
x*y         // explicit ordered product operation
(x*y)       // grouped ordered product
ListTimes[a,b] // list product operator
```

The parser must retain distinction between:

```text
xy
x*y
yx
y*x
```

unless an explicit rewrite or projection rule maps between them.

### 4.2 Equality operators

HARMONICODE has multiple equality modes:

```text
=   chain equality / binding equality depending context
==  assertion equality / witness equality
:=  definition / gate declaration
≠   inequality / distinctness constraint
:   ratio / relation operator
```

Example:

```harmonicode
P²-pq=n⁴=xy
```

Parses as a chain constraint:

```json
{
  "kind": "ChainEq",
  "terms": ["P²-pq", "n⁴", "xy"]
}
```

### 4.3 Inequality chains

```harmonicode
x≠y≠xy≠yx≠√xy≠√yx≠a≠b
```

Parses as a pairwise distinctness chain by default:

```text
DistinctChain[x,y,xy,yx,√xy,√yx,a,b]
```

### 4.4 Ratio chains

```harmonicode
x:y=xy:yx
A:B=B:A
```

Parses as relation/ration constraints, not division unless explicitly written with `/`.

---

## 5. Lists and matrices

### 5.1 List syntax

HARMONICODE accepts both Mathematica-style and JSON-style lists:

```harmonicode
List(x,y,xy,yx)
[x,y,xy,yx]
```

Both normalize to:

```json
{"kind":"List","items":[...]}
```

### 5.2 Nested lists / matrices

```harmonicode
List(List(x==1/y,(xy),y==-x),List((-xy),x+y+z+w+(xy)+(zw)==0,(-zw)),List(z==1/w,(zw),w==-z))
```

Normalizes to a `Matrix` node if rows are uniform length, otherwise a nested list.

---

## 6. Gate declarations

Gate declaration syntax:

```harmonicode
PLASTIC_EIGENSTATE_CLOSURE_GATE :=
{
  ρ³ = ρ + 1,
  b = ρ²,
  b² = ρ⁴,
  a² = 1,
  c² = b² + a²
}
```

Parses as:

```json
{
  "kind": "GateDeclaration",
  "name": "PLASTIC_EIGENSTATE_CLOSURE_GATE",
  "constraints": [...]
}
```

Gate declarations are reusable constraint macros.

A bare gate name after declaration invokes the gate in the current constraint state:

```harmonicode
PLASTIC_EIGENSTATE_CLOSURE_GATE
```

---

## 7. Python / JSON style operations

HARMONICODE supports structured programming forms so the same language can serve as programming language, calculator language, and IDE scripting language.

### 7.1 Function call

```harmonicode
Mod(x+y, u^72)
Sqrt((xy))
Factorial((x*y)!=(y*x))
ListTimes(List(a,b),List(b,a))
```

### 7.2 JSON-style object

```json
{
  "op": "Define",
  "symbol": "rho",
  "constraint": "rho^3 = rho + 1"
}
```

### 7.3 Python-style block form

```harmonicode
fn normalize_delta(delta, rho):
    return delta * rho^-1
```

This lowers into structured IR, not directly into host Python execution.

---

## 8. Canonical AST families

Required AST node kinds:

```text
Program
ConstraintStateMachine
Symbol
Number
BoundaryDecimal
Power
Root
OrderedProduct
FusedProduct
Sum
Difference
Quotient
ChainEq
AssertEq
Inequality
DistinctChain
Ratio
List
Matrix
FunctionCall
GateDeclaration
GateInvocation
Projection
Transport
Modulo
Assignment
Return
Block
EffectOperation
```

---

## 9. Constraint semantics

### 9.1 Global reconciliation

All active constraints are reconciled as a whole. For example:

```harmonicode
xy≠yx
xy=-1/yx
yx=-xy
```

The interpreter must build a constraint graph, not reduce each line independently.

### 9.2 No unauthorized commutation

The compiler may not rewrite:

```text
xy -> yx
x*y -> y*x
AB -> BA
```

unless a rule explicitly declares a projection or normalized commutative shadow.

### 9.3 Projection layers

Some identities exist at projection level, not raw scalar level. Example from Plastic Eigenstate Closure Gate:

```harmonicode
a²:b²:c² = 1:2:3
```

is tagged as normalized projection, while:

```harmonicode
b² = ρ⁴ = ρ² + ρ
```

belongs to literal eigenstate layer.

AST/IR must preserve both layers.

---

## 10. Effect model preview

Effects:

```text
PURE        symbolic rewrite only
AUDITED     state patch requiring kernel audit
EXTERNAL    host IO / audio / FFI / device boundary
QUARANTINE  invalid or unverified transition
```

All `AUDITED` and `EXTERNAL` operations require receipts.

---

## 11. Calculator syntax profile

Calculator mode is a restricted HARMONICODE source profile.

Supported forms:

```text
1+2*3
Sqrt(xy)
Mod(x+y,u^72)
Matrix([[4,9,2],[3,5,7],[8,1,6]])
xy=-1/yx
rho^3=rho+1
```

Calculator scripts lower into the same AST and IR as regular programs.

---

## 12. Error classes

```text
ParseError
AmbiguousTokenError
UnclosedGroupError
UnauthorizedCommutationError
ProjectionLayerError
InvariantFailure
ReceiptMismatch
ExternalBoundaryUnsealed
KernelAuditFailure
```

---

## 13. Minimal valid program examples

### 13.1 Ordered reciprocal lock

```harmonicode
x=1/y
y=-x
xy=-1/yx
yx=-xy
xy≠yx
```

### 13.2 Plastic eigenstate gate

```harmonicode
PLASTIC_EIGENSTATE_CLOSURE_GATE := {
  ρ³ = ρ + 1,
  b = ρ²,
  b² = ρ⁴,
  a² = 1,
  c² = b² + a²,
  c² - b² = a²,
  Π₂((b²-b)²)=b²
}

PLASTIC_EIGENSTATE_CLOSURE_GATE
```

### 13.3 Python/JSON style operation

```harmonicode
fn qgu_decay(frac, dq, cq):
    return 1 + ((frac * List(dq^4)) * List(1 + cq^2))
```

---

## 14. Compiler rule

The compiler is forbidden from accepting a program as executable unless:

1. Source parses.
2. AST lowers into IR.
3. Constraint graph is built.
4. Effects are classified.
5. State transitions are audited.
6. Receipts are emitted.
7. Replay verifies.
8. Global invariants hold.

Failure emits quarantine, not implicit success.

## 34. Lane 5 1.50–1.62 mathematical extension

Normative documentation summary:

docs/whitepapers/HHS_LANE5_MATHEMATICAL_EXTENSIONS_1_50_1_62_V1.md

Pass 219 compact appendix:

docs/pass219/APPENDIX_J_LANE5_1_50_1_62_MATHEMATICAL_EXTENSIONS.md

The extension preserves these system-internal constraints:

~~~text
RHS closure -> admissible LHS manifold -> local values/asymmetries

AB != BA
A/B != B/A
xy != yx
zw != wz

(P=√(pq+(P⁴/AB)))/∆
Cancel_∆(S)=forbidden

81*64=5184=72^2=144*36=1296*4
81=1+40*2
~~~

The exact ordered sum-of-two-squares correction is:

~~~text
m_D n_D = A^2 + B^2 + Delta_D - Lambda_D
~~~

with ordered-word defects defined in the linked paper. Scalar/commutative projection may annihilate the defect tensors but does not grant native commutation.

The 1.61 tripartite scalar proof surface is:

~~~text
Gamma*P*(q-p)=Sigma*(p+q)
Gamma*(P^2-pq)=Sigma
(P^2-pq)*rho*Gamma=Sigma*Omega
~~~

with Omega and p+q fail-closed at zero.

The reciprocal phase-debt surface preserves:

~~~text
q=n/9
q*=-q
phase modulus=72
half-cycle=36
clock step=±16
all 40 reciprocal classes closed
open_debt_depth=0
~~~

before candidate commit readiness.

The ordered unresolved-stack root is part of receipt state. Hash216 receipt material remains non-authoritative for canonical commit.

The 2026-09-21 Wolfram documentation audit is 44/44 PASS and is stored under evidence/pass219/hhs_lane5_mathematical_synthesis_20260921_v1.*.

The stacked repository currently reuses HHS-T5184-005 for Lane 5 1.60 and 1.61. Until a canonical renumbering is committed, the specification requires pass-qualified references rather than silent identifier substitution.

## 35. Unified relational token manifold

Pass 219 canonicalizes the both-and human/machine resolution model in:

```text
contracts/pass219/PASS_219_RELATIONAL_TOKEN_MANIFOLD_1_0.json
docs/architecture/HHS_RELATIONAL_TOKEN_MANIFOLD_V1.md
hhs_runtime/pass219/relational_token_manifold.py
```

The required synthesis is:

```text
human:
  language AND logic AND code AND geometry AND data AND mathematics

machine:
  exact mathematical relations over preserved character/string state
```

The machine-facing primary surface is not a token-to-integer-ID reduction. A
character token carries exact character identity together with deterministic
metadata including Unicode/UTF-8 identity, exact UTF-8 BigInt projection, Lo
Shu address, prime-modular fingerprint, recursive position, bounded context,
surface roles, source provenance, and shared knowledge-graph edges.

The projection law is:

```text
source string S
  <-> relational character tokens T_i
  <-> shared graph G
  <-> requested higher-order HARMONICODE projections
```

All arrows are additive and reciprocal where the consuming contract declares a
lossless projection. The human-readable source is never deleted merely because
a machine mathematical projection exists.

For the reference character tokenizer:

```text
hydrate(tokenize(S)) == S
```

with exact SHA-256 source identity preserved.

The per-character UTF-8 BigInt field is an exact projection only. It does not
replace the inherited canonical fixed-width 5184-character HARMONICODE BigInt
serialization.

This layer is relational metadata / graph projection authority only. It may feed
Lane 5 candidate composition, but it does not mint canonical VM81 mutation,
Hash72 receipts, or Hash216 lineage.

