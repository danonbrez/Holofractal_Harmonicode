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


---

## 15. Directed recursive constraint semantics

HARMONICODE equality is a directional constraint, not a symmetric substitution rule.

For every native edge LHS = RHS:

RHS enforced closure -> admissible LHS manifold -> local values -> emergent local tensor asymmetry.

The RHS is true by constraint enforcement from the perspective of the dependent LHS. Local asymmetries may be necessary consequences of closure; they must not be modeled as the cause of the global RHS law.

This direction applies recursively at every nested expression node. For N/D, the numerator is the local LHS branch and denominator the local RHS branch; both preserve their own nested tensor structure.

Ordered expressions retain source identity. In AB=P^4, the parent dependency is P^4 -> AB, while the local product has A=LHS and B=RHS. AB and BA are distinct unless an explicit native equality gate proves otherwise. The same identity rule applies to A/B and B/A as reciprocal ordered objects.

Metric equations such as a^2=1, b^2=2 and c^2=3 are projection statements. The scalar is a one-dimensional readout of the manifold geometry, not a replacement mapping. Projection equality never grants native substitution authority.

Executable reference:

hhs_runtime/harmonicode_directed_constraint_semantics_v1.py

Normative contract:

contracts/pass219/PASS_219_CONSTRAINT_ORIENTATION_1_51.md


---

## 16. BigInt nested transcription manifold

The canonical fixed-width 5,184-character BigInt serialization is an executable transcription surface rather than a passive decimal string around a second codec.

Pass 219 Lane 5 1.52 exposes one typed operation:

```text
transcribe_5184
```

which traverses the inherited serializer in either direction:

```text
81 exact normalization offsets <-> 5184-character HARMONICODE serialization
```

For admitted states the read/write roundtrip must be exact. Leading zero state is preserved by the fixed-width 64-character token geometry.

The transcription geometry binds:

```text
G123 = ((1,2,3),(2,4,6),(3,6,9))
1+2+3 = 1*2*3 = 6
6*6 = 36
sum(1..36) = 666
666/6 = 111
(4*3)^2 = 144
144*36 = 5184 = 72^2 = 81*64
palindromic lanes = 123321, 246642, 369963
```

The visible `123321.111` seed is a projection/witness of the complete serialized operand and never replaces that operand.

Rationals, matrices, continued fractions, tensors, ordered phase variables and other nested payloads remain typed boundary objects. The registered universal nesting boundary is:

```harmonicode
(P=√(pq+(P⁴/AB)))/∆
```

Every nested object remains under that shared global denominator unless an explicitly registered subordinate boundary law is supplied. Nesting does not grant independent scalar-normalization, commutation, or substitution authority.

The inherited directed constraint semantics remain active at every nested level, and the inherited ordered identities remain distinct.

Executable reference:

```text
hhs_runtime/harmonicode_lane5_bigint_transcription_v1.py
```

Normative contract:

```text
contracts/pass219/PASS_219_LANE5_BIGINT_NESTED_TRANSCRIPTION_1_52.md
```


---

## 17. Reciprocal phase-boundary theorem

Pass 219 Lane 5 1.53 registers `HHS-T5184-002` as a typed native theorem over the existing BigInt transcription circuit.

The governing source laws are:

```harmonicode
(P=√(pq+(P⁴/AB)))/∆
P=(Bx^5184)/∆
∞∆=Bx^5184
R(∞)=∆
R(∆)=x
x=Γ_x
Γ_x=u^(18/72mod72)*u^36
P≠∞
(P/∞)^(x^2)=P
∆=(∞^(x^2))/∆
P=P/∆
Cancel_∆(S)=forbidden
```

`∆` is the universal denominator/boundary and is never cancelled. A shared `∆` boundary does not authorize the rewrite `P=∞`.

`R` is a directed reciprocal traversal, not ordinary scalar inversion. The implementation therefore does not infer `R²=id`, `∆^-1*∆=1`, or `∆*∆^-1=1`.

`Γ_x` preserves its source order exactly. The factors `u^(18/72mod72)` and `u^36` may not be combined or reordered without an explicit native rule.

The P-state boundary fixed point `P=P/∆` is a native boundary relation. It does not imply `∆=1` and does not authorize denominator removal.

Executable reference:

```text
hhs_runtime/harmonicode_lane5_reciprocal_phase_boundary_v1.py
```

Normative contract:

```text
contracts/pass219/PASS_219_LANE5_RECIPROCAL_PHASE_BOUNDARY_1_53.md
```


---

## 18. IEEE-754 palindromic decimal-pivot transcription

Pass 219 Lane 5 1.54 registers `HHS-T5184-003`.

IEEE source state is admitted as an exact bit-pattern ingress/egress surface. Host floating-point arithmetic remains non-authoritative.

For a canonical digit frame `F`:

```harmonicode
C(F) = F . Reverse(F)
```

The decimal point is the directional pivot.

Direction A reads forward from the left edge to the pivot. Direction B reads independently from the far right edge backward to the pivot.

For finite IEEE binary16, binary32 and binary64 states:

```text
v = (-1)^s n/2^k
n/2^k = n*5^k/10^k
```

so the source state has an exact terminating decimal coefficient and scale. Both A and B reconstruct the same exact rational and original sign/exponent/fraction bit pattern.

Infinity and NaN retain exact sign/payload bit identity but receive no numeric-value authority.

The 72-position unit is a block size rather than a global numeral ceiling:

```text
F = C0 || C1 || ... || C(n-1)
|Ci| <= 72
Concat(Block72(F)) = F
```

and the reverse-side block traversal independently reconstructs the same `F`.

The executable theorem also preserves:

```text
(y-x)-u^72=G^3
123321.111
(P=√(pq+(P⁴/AB)))/∆
5184=72^2=81*64
```

Executable reference:

```text
hhs_runtime/harmonicode_lane5_ieee754_palindromic_pivot_v1.py
```

Normative contract:

```text
contracts/pass219/PASS_219_LANE5_IEEE754_PALINDROMIC_PIVOT_1_54.md
```


---

## 19. T64 bijective constructor provenance and exhaustive resolution

Pass 219 Lane 5 1.55 registers `HHS-T5184-004`.

The local ordered constructor manifold is:

```harmonicode
{x,y,z,w}^3 <-> {0,1}^6 <-> 8x8
```

with:

```text
x=00
y=01
z=10
w=11
operation64=16*d0+4*d1+d2
operation64=8*left_basis8+right_basis8
```

Distinct ordered triplets retain distinct six-bit addresses and distinct provenance roots.

The exhaustive resolution path is:

```text
triplet
 -> operation64
 -> ordered native phase product
 -> reciprocal_phase=(-phase) mod72
 -> phase zero-sum closure
 -> ((0,-2)+(-2,0))/2
 -> (-1,-1)
```

Acceptance requires:

```text
64/64 ordered triplet round-trips
64/64 unique operation64 addresses
64/64 unique provenance roots
64/64 reciprocal phase closures
64/64 (-1,-1) terminal resolutions
64/64 native C phase cross-checks
5184/5184 native VM5184 address round-trips
```

The structural geometry is:

```text
81*64=5184=72^2
```

No commutation or canonical mutation authority is introduced.

Executable reference:

```text
hhs_runtime/harmonicode_lane5_t64_exhaustive_resolution_v1.py
```

Normative contract:

```text
contracts/pass219/PASS_219_LANE5_T64_EXHAUSTIVE_RESOLUTION_1_55.md
```


---

## 20. RNA self-ingestion bytecode experiment

Pass 219 Lane 5 1.56 registers read-only experiment `HHS-X5184-001` over the green `HHS-T5184-004` T64 invariant.

Two representations are intentionally kept distinct.

Typed native self-ingestion:

```text
{x,y,z,w}^3
 -> kappa
 -> operation64
 -> one exact byte
 -> operation64
 -> inverse kappa
 -> same ordered word
```

This path is an exact 64-state identity.

Experimental untyped projection:

```text
Pi_ascii(W) = BigInt(ASCII(W)) mod64
```

with no canonical authority.

Because a big-endian byte string is a base-256 integer and:

```text
256 mod64 = 0
```

the projection satisfies:

```text
Pi_ascii(W) = final_byte(W) mod64.
```

For the four terminal RNA symbols:

```text
w -> 55 -> wyw
x -> 56 -> wzx
y -> 57 -> wzy
z -> 58 -> wzz
```

Therefore all 64 T64 words collapse in one projected step to exactly four fixed points:

```text
{wyw,wzx,wzy,wzz}
```

with basin size 16 for each.

The external ASCII-BigInt/mod64 projection is explicitly noncanonical. It demonstrates that exact byte transport does not by itself preserve typed ordered provenance.

All projected states remain inside T64 and still resolve under `HHS-T5184-004` to `(-1,-1)`, but only four unique projected operation64 identities remain.

The native exact bytecode membrane is used only for ingress/egress identity. No self-ingested bytes are executed as machine instructions.

Executable reference:

```text
hhs_runtime/harmonicode_lane5_rna_self_ingestion_bytecode_v1.py
```

Experiment contract:

```text
contracts/pass219/PASS_219_LANE5_RNA_SELF_INGESTION_BYTECODE_1_56.md
```

---

## 21. Lane 5 zero-bypass payload and execution closure

Pass 219 Lane 5 1.59 establishes the production-path invariant:

```text
PublicRuntimeEntry
  ⊆ Lane5ZeroBypass
  → RNA_CPP_CELL_WALL
  → FOUR_LANE_HYDRATION
  → PQC_ENVIRONMENTAL_ADMISSION
  → VM81_HASH72_CANONICAL_AUTHORITY
  → HASH216_VALIDATED_CONTINUATION
```

The parametric payload membrane satisfies, for every admitted byte string B of length n:

```text
T_n^-1(T_n(B)) = B.
```

This is an exact byte identity law. IEEE-754 encodings are valid payload bit patterns but never gain floating-point canonical authority.

Execution is constraint-forced:

```text
constraint_forced_execution = TRUE
policy_choice_authority = FALSE
```

The Lane 5 BIOS configures/enforces traversal of the constraint manifold and does not transform the data model or select an unconstrained answer.

Hash216 is validated computational memory:

```text
ValidatedScopedOperation(H) → reusable/composable continuation
Hash216Hit(H) ↛ CanonicalCommit(H).
```

Only the inherited VM81/Hash72 authority can complete canonical admission. Lane 5, RNA/PQC membranes, caches, GPU/vector routing, APIs and compatibility aliases remain noncanonical.

The public Linux/FastAPI operation surfaces are interposed by the Lane 5 zero-bypass control plane. Canonical mutation still enters the native 648-byte/5184-bit gateway and the existing RNA/PQC/VM81 chain.


---

## 22. Thread-lineage normalization and hierarchical memory

Pass 219 Lane 5 1.60 registers `HHS-T5184-005`.

The normalized Genesis/closure coordinate is the inherited exact VM81 offset state:

```text
Q0 = (0,...,0), |Q0| = 81
Ser5184(Q0) = 81 exact 64-character rational-scientific zero tokens
```

The phrase `0^5184` in the structural theorem denotes the zero coordinate geometry. The authoritative serialized object remains the fixed-width 5,184-character HARMONICODE rational-scientific representation; normalization does not replace it with a variable-width host integer or raw text-zero buffer.

The transition law is preserved by coordinate conjugacy:

```text
F_N = N o F o N^-1
F_N(N(S),I) = N(F(S,I))
```

No native phase, RNA, H36, VM81, Hash72 or Hash216 law is rewritten.

A thread address is a projection of the complete admitted boundary:

```text
Scope216  = Hash216(Capabilities)
Pal216    = Hash216(Ser5184 || Reverse(Ser5184))
Thread216 = Hash216(
              Scope216 ||
              Evolution216 ||
              Lineage216 ||
              PQCWitness216 ||
              Pal216 ||
              Ser5184
            )
```

Therefore a thread root is not a detached OS/thread index. Same-process residency does not imply shared computational namespace.

Scope composition is monotone:

```text
Scope(composition) = intersection(required scopes)
Scope(next) subseteq Scope(current)
```

Cross-thread reads require an explicit directed shared-scope bridge, matching admitted evolutionary lineage, and capabilities contained in both source and target scopes. Scope union is forbidden.

Persistent memory uses one physical SQLite/WAL/FULL fabric with boundary-qualified logical indexes:

```text
(scope_hash216, thread_root_hash216, lineage_hash216, object_hash216)
```

The virtual hierarchy is:

```text
/scope/<Scope216>/thread/<Thread216>/lineage/<Lineage216>/<type>/<Object216>
```

Authorization filtering is applied before any vector-distance/ranking stage. Objects outside the admitted namespace never enter the searchable candidate population.

The PQC witness is bound into the thread boundary but does not create a second signature or canonical-commit authority. Canonical execution remains the inherited Lane 5 -> RNA -> PQC -> VM81/Hash72 path; Hash216 remains validated compositional memory.

Wolfram evidence for `HHS-T5184-005` is source/output digest-bound and reports 17/17 exact structural checks passing.

Executable reference:

```text
hhs_backend/runtime/hhs_pass219_lane5_thread_lineage_normalization_1_60.py
```

Normative contract:

```text
contracts/pass219/PASS_219_LANE5_THREAD_LINEAGE_NORMALIZATION_1_60.md
```
