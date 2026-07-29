# HHS PASS 168 — VM81 5,184-CELL HARMONICODE PARAMETER CIRCUIT AND SPARSE TENSOR CONTROL FABRIC

## Sixty-Four Independent VM81 Parameter Threads, Forty Source-Syntax Channels, Twenty-Four Derived Computational Channels, Nine-Bank Lo Shu Microtile Pipelines, Ordered Equality Half-Gates, Gauge-Normalized Reciprocal Transport, Sparse Virtual-Memristor Delta Propagation, Hash72/Hash216 State Identity, and Deterministic Receipt-Closed Replay

# 1. Normative metadata

| Field | Normative value |
|---|---|
| Contract identifier | `HHS-P168-VM81-5184-HPC-STCF` |
| Pass number | `168` |
| Canonical pass name | `VM81_5184_CELL_HARMONICODE_PARAMETER_CIRCUIT_AND_SPARSE_TENSOR_CONTROL_FABRIC` |
| Short name | `P168 5184 Parameter Circuit` |
| Contract version | `1.0.0` |
| Repository | `danonbrez/Holofractal_Harmonicode` |
| Authoritative repository baseline | Current authoritative `main`, including Pass 167 contract commit `dd74adae546586a32b4629937602b31b78683f45` and all inherited history |
| Immediate inheritance parent | Complete authoritative Pass 167 inherited pass-history nucleus |
| Binding ancestry | All authoritative repository passes through Pass 167 and all accepted intervening implementation commits |
| Primary source language | HARMONICODE |
| Canonical execution authority | Exactly one VM81 runtime authority kernel |
| Global circuit dimensions | `72 × 72 = 5,184` cells |
| Thread topology | `8 × 8 = 64` parameter threads |
| Per-thread topology | `9 × 9 = 81` VM81 cells |
| Source-parameter threads | `40` |
| Derived-computation threads | `24` |
| Pipeline banks per thread | `9` |
| Cells per bank | `9`, arranged as one `3 × 3` Lo Shu microtile |
| Total Lo Shu microtiles | `64 × 9 = 576` |
| Numeric authority | Exact integer, BigInt, rational, symbolic, and modular forms |
| Floating-point authority | Forbidden in canonical state, admission, commit, receipt, and replay paths |
| Memory model | Sparse virtual-memristor parameter deltas over fixed 5,184-cell identity |
| Historical identity | Hash216 object and transition identity |
| Execution receipt | Hash72 receipt chain |
| Delivery model | Additive, incremental, source-oriented, append-only |
| Validation policy | Dependency-scoped, bounded stage-gate, repair-forward |
| Initial classification | `CONTRACT_AUTHORIZED — FULL IMPLEMENTATION REQUIRED` |

# 2. Normative language

The terms **SHALL**, **SHALL NOT**, **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are normative.

This document authorizes and defines implementation. It does not by itself constitute a completed native implementation, validated runtime, compiled HARMONICODE lowering path, successful VM81 admission, committed transition, Hash72 or Hash216 closure, cross-architecture verification, or terminal Pass 168 completion.

Pass 168 SHALL remain nonterminal until every acceptance requirement in this contract has executable evidence.

# 3. Authority and inheritance

## 3.1 Repository authority

Repository commit history, implemented callable surfaces, executable tests, manifests, receipts, contracts, schemas, and correction records SHALL collectively determine inherited authority.

Pass 168 SHALL NOT overwrite or silently reinterpret an inherited invariant. When evidence conflicts, implementation SHALL:

1. preserve the conflicting artifacts;
2. identify the highest applicable authority;
3. issue an append-only reconciliation record;
4. repair dependent implementation;
5. rerun only affected validation;
6. preserve previously verified unaffected evidence.

## 3.2 Pass 167 binding

Pass 168 SHALL inherit Pass 167’s exact 5,184-bit identity, 81-cell VM81 topology, single runtime commit authority, Hash72 execution evidence, Hash216 operation identity, Sudoku routing compatibility, exact transport requirements, and deterministic replay discipline.

Pass 168 SHALL NOT reinterpret the Pass 167 5,184-bit PCM snapshot as the same physical representation as the Pass 168 5,184-cell parameter fabric. The two passes share dimensional identity and VM81 addressing authority while retaining distinct typed state domains.

## 3.3 HARMONICODE authority

The bound source SHALL be interpreted as a HARMONICODE constraint-state program.

It SHALL NOT be downgraded into:

- a classical equation to solve;
- a host-language Boolean expression;
- a commutative matrix identity;
- an untyped string;
- a floating-point calculator expression;
- a collection of unrelated subexpressions.

Every parenthesis pair, equality character, list surface, matrix surface, ordered product, modular envelope, exponent group, and terminal closure surface SHALL retain source identity through parsing, lowering, execution, receipt, and replay.

# 4. Required result

Pass 168 SHALL implement a complete parameter-control fabric over the 5,184-cell array that:

1. binds the supplied HARMONICODE source without semantic loss;
2. registers every matched `()` pair as an independent parameter shell;
3. registers every literal `=` character as an independent ordered equality half-gate;
4. assigns all forty source parameters to dedicated VM81 threads;
5. assigns twenty-four reduced computational and validation channels to the remaining threads;
6. maps every thread to exactly one 81-cell VM81 block;
7. partitions every block into nine pipeline banks;
8. preserves one Lo Shu coordinate system through all pipeline stages;
9. evaluates upper and lower 3×3 matrix lanes using exact arithmetic;
10. implements gauge cancellation and mismatched-ratio encoding;
11. evaluates six ordered equality comparators;
12. supports sparse dependency-scoped mutation;
13. records immutable transition history;
14. admits commits only through the single VM81 authority kernel;
15. emits Hash72 execution receipts;
16. emits Hash216 object and transition identities;
17. supports deterministic replay, rollback, repair, and divergence localization;
18. exposes native ABI, HARMONICODE, CLI, and HTTP control surfaces;
19. supports CPU and GPU-cluster candidate execution without changing canonical results;
20. proves complete 5,184-cell coverage and address reversibility.

The canonical execution path SHALL be:

```text
preserved HARMONICODE source
→ punctuation and shell registration
→ 40 raw parameter threads
→ sparse parameter delta
→ dependency-closure calculation
→ reciprocal and gauge normalization
→ inverse-depth selection
→ exact 3×3 matrix projection
→ six ordered equality comparators
→ Lo Shu kernel processing
→ sparse propagated delta
→ VM81 admission
→ atomic commit
→ Hash72 receipt
→ Hash216 historical identity
→ deterministic replay
```

# 5. Canonical dimensional invariant

Pass 168 SHALL bind:

```text
5184 = 72 × 72
5184 = 64 × 81
64   = 8 × 8
81   = 9 × 9
81   = 9 banks × 9 Lo Shu cells
5184 = 64 threads × 9 banks × 9 cells
5184 = 576 Lo Shu microtiles × 9 cells
```

The dual topology SHALL be simultaneously valid:

```text
GLOBAL VIEW:  72 × 72 tensor lattice
THREAD VIEW:   8 × 8 parameter threads
VM81 VIEW:     9 × 9 cells per thread
BANK VIEW:     3 × 3 banks per thread
LOCAL VIEW:    3 × 3 Lo Shu cells per bank
```

No view may alter cell identity.

# 6. Bound HARMONICODE source

The initial canonical source fixture SHALL preserve the following byte-significant expression:

```harmonicode
(t^3-t-(Mod(MatrixTimes(361,MatrixTimes(144/{{3,5,8},{13,21,34},{55,89,144}},NcalcMatrixPower(144/{{3,5,8},{13,21,34},{55,89,144}},(-1)))),{{4,9,2},{3,5,7},{8,1,6}})==x*y==Mod(1,u^360))==Mod(MatrixTimes(360,MatrixTimes(144/List(List(3,5,8),List(13,21,34),List(55,89,144)),NcalcMatrixPower((144/List(List(3,5,8),List(13,21,34),List(55,89,144))),(-1)))),List(List(4,9,2),List(3,5,7),List(8,1,6)))==(x*y)==Mod(0,u^360))/u^72==0
```

The source-preservation receipt SHALL include:

```text
source_bytes
source_byte_length
source_sha256
source_hash72
parenthesis_pair_count
literal_equals_count
double_equals_token_count
token_stream_hash
AST_hash216
IR_hash216
```

The required counts for this fixture are:

```text
matched parenthesis pairs: 28
literal "=" characters:    12
"==" comparator tokens:     6
```

# 7. Source parameter model

## 7.1 Parenthesis-shell parameters

Every matched parenthesis pair SHALL receive one stable identifier:

```text
P1 ... P28
```

A parenthesis parameter is context-sensitive. It SHALL act according to the semantic role of the enclosed node rather than as an indiscriminate textual scalar.

| Parameter | Canonical role | Required action class |
|---|---|---|
| `P1` | Global outer LHS tensor shell | Common output gain |
| `P2` | Upper assertion group | Upper output gain |
| `P3` | Upper `Mod` envelope | Upper output or witness-envelope gain |
| `P4` | Upper outer `MatrixTimes` | Upper output gain |
| `P5` | Upper inner `MatrixTimes` | Upper output gain |
| `P6` | Upper `NcalcMatrixPower` group | Upper output gain |
| `P7` | Upper `(-1)` exponent group | Inverse-depth selector |
| `P8` | Upper `Mod(1,u^360)` group | Unit-witness gain |
| `P9` | Lower `Mod` envelope | Lower output gain |
| `P10` | Lower outer `MatrixTimes` | Lower output gain |
| `P11` | Lower inner `MatrixTimes` | Lower output gain |
| `P12` | Lower direct Fibonacci matrix list | Direct matrix denominator gain |
| `P13` | Lower direct Fibonacci row 1 | Direct row-1 denominator gain |
| `P14` | Lower direct Fibonacci row 2 | Direct row-2 denominator gain |
| `P15` | Lower direct Fibonacci row 3 | Direct row-3 denominator gain |
| `P16` | Lower `NcalcMatrixPower` group | Lower output gain |
| `P17` | Lower inverse quotient group | Inverse-input gain |
| `P18` | Lower inverse Fibonacci matrix list | Inverse matrix denominator gain |
| `P19` | Lower inverse Fibonacci row 1 | Inverse row-1 denominator gain |
| `P20` | Lower inverse Fibonacci row 2 | Inverse row-2 denominator gain |
| `P21` | Lower inverse Fibonacci row 3 | Inverse row-3 denominator gain |
| `P22` | Lower `(-1)` exponent group | Inverse-depth selector |
| `P23` | Lower Lo Shu matrix list | Projection gain |
| `P24` | Lower Lo Shu row 1 | Projection row-1 gain |
| `P25` | Lower Lo Shu row 2 | Projection row-2 gain |
| `P26` | Lower Lo Shu row 3 | Projection row-3 gain |
| `P27` | Grouped ordered product `(x*y)` | Ordered-product witness gain |
| `P28` | Lower `Mod(0,u^360)` group | Zero-witness gain |

The registry SHALL record source span, nesting depth, parent node, child node, action class, and thread identifier for every parameter.

## 7.2 Equality half-gates

Every literal equality character SHALL receive one stable identifier:

```text
E1 ... E12
```

Every `==` token SHALL therefore lower into two ordered half-gates:

```text
left half-gate
right half-gate
```

| Parameter | Comparison | Side | Required edge |
|---|---:|---|---|
| `E1` | 1 | Left | Upper matrix lane |
| `E2` | 1 | Right | Ordered product `x*y` |
| `E3` | 2 | Left | Ordered product `x*y` |
| `E4` | 2 | Right | Unit modular witness |
| `E5` | 3 | Left | Upper tensor shell |
| `E6` | 3 | Right | Lower tensor shell |
| `E7` | 4 | Left | Lower matrix lane |
| `E8` | 4 | Right | Grouped ordered product `(x*y)` |
| `E9` | 5 | Left | Grouped ordered product `(x*y)` |
| `E10` | 5 | Right | Zero modular witness |
| `E11` | 6 | Left | Terminal normalized shell |
| `E12` | 6 | Right | Terminal zero witness |

The compiler SHALL NOT merge the two characters of `==` into one unaddressable parameter.

# 8. Thread allocation

The 64-thread register SHALL be fixed as follows:

```text
THREAD ROW 0
T00=P1   T01=P2   T02=P3   T03=P4
T04=P5   T05=P6   T06=P7   T07=P8

THREAD ROW 1
T08=P9   T09=P10  T10=P11  T11=P12
T12=P13  T13=P14  T14=P15  T15=P16

THREAD ROW 2
T16=P17  T17=P18  T18=P19  T19=P20
T20=P21  T21=P22  T22=P23  T23=P24

THREAD ROW 3
T24=P25  T25=P26  T26=P27  T27=P28
T28=E1   T29=E2   T30=E3   T31=E4

THREAD ROW 4
T32=E5   T33=E6   T34=E7   T35=E8
T36=E9   T37=E10  T38=E11  T39=E12

THREAD ROW 5
T40=UPPER_GAIN_ALPHA
T41=LOWER_GAIN_BETA
T42=ROW_CHANNEL_RHO1
T43=ROW_CHANNEL_RHO2
T44=ROW_CHANNEL_RHO3
T45=UPPER_DEPTH
T46=LOWER_DEPTH
T47=GLOBAL_COMMON_GAIN

THREAD ROW 6
T48=COMPARATOR_C1
T49=COMPARATOR_C2
T50=COMPARATOR_C3_MATRIX
T51=COMPARATOR_C4
T52=COMPARATOR_C5
T53=COMPARATOR_C6_TERMINAL
T54=LOSHU_ORIENTED_KERNEL_L
T55=LOSHU_EVEN_KERNEL_L2

THREAD ROW 7
T56=MATRIX_GAUGE
T57=ROW_GAUGE_1
T58=ROW_GAUGE_2
T59=ROW_GAUGE_3
T60=WITNESS_AGGREGATE
T61=U_SHELL_DEPTH_RATIO
T62=SUCCESSOR_RESIDUAL
T63=GLOBAL_CLOSURE_RECEIPT
```

The allocation invariant is:

```text
40 raw threads + 24 derived threads = 64 threads
40 × 81 + 24 × 81 = 3240 + 1944 = 5184 cells
```

Thread identity SHALL remain permanent across all state versions.

# 9. Global and local addressing

For a thread coordinate:

```text
thread_row ∈ [0,7]
thread_col ∈ [0,7]
```

and VM81-local coordinate:

```text
local_row ∈ [0,8]
local_col ∈ [0,8]
```

the global address SHALL be:

```text
global_row = 9 × thread_row + local_row
global_col = 9 × thread_col + local_col
global_index = 72 × global_row + global_col
```

The inverse mapping SHALL be:

```text
thread_row, local_row = divmod(global_row,9)
thread_col, local_col = divmod(global_col,9)

thread_id = 8 × thread_row + thread_col
local_index = 9 × local_row + local_col
```

The bank and Lo Shu coordinates SHALL be:

```text
bank_row, loshu_row = divmod(local_row,3)
bank_col, loshu_col = divmod(local_col,3)

bank_id = 3 × bank_row + bank_col
loshu_index = 3 × loshu_row + loshu_col
```

The runtime SHALL prove:

```text
encode(decode(address)) = address
decode(encode(thread,local)) = (thread,local)
```

for all 5,184 cells.

# 10. Nine-bank VM81 pipeline

Each parameter thread SHALL contain the following bank layout:

```text
BANK ROW 0
B0 SOURCE
B1 NORMALIZED_DELTA
B2 RECIPROCAL_OR_GAUGE

BANK ROW 1
B3 INVERSE_DEPTH
B4 PROJECTED_STATE
B5 COMPARATOR

BANK ROW 2
B6 PROPAGATED_DELTA
B7 COMMITTED_STATE
B8 REPLAY_RECEIPT
```

Each bank SHALL be one 3×3 Lo Shu microtile.

The canonical local Lo Shu layout is:

```text
4 9 2
3 5 7
8 1 6
```

Every lifecycle stage SHALL retain the same `loshu_index`. A value at a local Lo Shu coordinate SHALL retain that coordinate when transferred through source, delta, reciprocal, projection, comparator, commit, and receipt banks.

# 11. Cell record

Every physical circuit cell SHALL have a versioned record equivalent to:

```text
ParameterCircuitCell = (
    global_index,
    global_row,
    global_col,
    thread_id,
    thread_row,
    thread_col,
    channel_id,
    channel_class,
    bank_id,
    bank_role,
    local_index,
    loshu_index,
    loshu_value,
    trinary_state,
    exact_value,
    numerator_bigint,
    denominator_bigint,
    symbolic_value_ref,
    modulus_ref,
    reciprocal_peer,
    dependency_version,
    object_version,
    committed,
    source_hash72,
    state_hash216,
    transition_hash216,
    receipt_hash72
)
```

`trinary_state` SHALL use:

```text
+1 = constructive or active delta
 0 = identity, unchanged, held, or compressed state
-1 = reciprocal, cancellation, or inverse-phase delta
```

Trinary state SHALL NOT replace the exact value. It is routing and comparison metadata.

# 12. Exact numeric authority

The canonical runtime SHALL use:

- signed BigInt integers;
- normalized BigInt rationals;
- exact matrix entries;
- symbolic powers;
- explicit modular domains;
- exact comparison outcomes.

A rational SHALL be normalized as:

```text
gcd(abs(numerator),denominator)=1
denominator>0
```

Floating-point values MAY be emitted as explicitly labeled, nonauthoritative display projections only.

Floating-point data SHALL NOT participate in admission, equality comparison, gauge cancellation, matrix inversion, commit identity, Hash72 receipts, Hash216 identity, or deterministic replay.

# 13. Canonical matrices

Pass 168 SHALL bind the Fibonacci carrier:

```text
F =
[[ 3,  5,   8],
 [13, 21,  34],
 [55, 89, 144]]
```

and the Lo Shu kernel:

```text
L =
[[4,9,2],
 [3,5,7],
 [8,1,6]]
```

The reciprocal quotient projection SHALL be:

```text
Q = 144/F
```

where `/` is the authorized exact element-wise rational scalar quotient for this source fixture.

The runtime SHALL verify:

```text
det(F)=0
rank(F)=2
row3(F)=row1(F)+4×row2(F)
```

and:

```text
det(Q)=4608/37862825
rank(Q)=3
Q × Q^-1 = I3
```

No implementation may attempt to invert `F` directly as a substitute for `Q^-1`.

# 14. Reduced parameter equations

Define:

```text
α = P1 P2 P3 P4 P5 P6
```

```text
β = P1 P9 P10 P11 P16 P23 P18 / (P12 P17)
```

Define the three row channels:

```text
ρ1 = (P19/P13)P24
ρ2 = (P20/P14)P25
ρ3 = (P21/P15)P26
```

Define inverse depths:

```text
dU = 1-P7
dV = 1-P22
```

The upper and lower matrix lanes SHALL be:

```text
U = 361 α Q^dU L
```

```text
V = 360 β diag(ρ1,ρ2,ρ3) Q^dV L
```

At the canonical baseline:

```text
Pi=1 for i=1..28
Ej=1 for j=1..12
```

the required results are:

```text
dU=0
dV=0
α=1
β=1
ρ1=ρ2=ρ3=1
U=361L
V=360L
U-V=L
```

# 15. Ordered comparator network

Pass 168 SHALL implement six independent ordered comparators.

Their canonical arithmetic-shadow forms are:

```text
C1 = E1·U - E2·XY
C2 = E3·XY - E4·W1
C3 = E5·U - E6·V
C4 = E7·V - E8·XYG
C5 = E9·XYG - E10·W0
C6 = E11·N(C3,u^72) - E12·ZERO
```

where:

```text
XY   = ordered-product witness x*y
XYG  = grouped ordered-product witness P27(x*y)
W1   = P8·Mod(1,u^360)
W0   = P28·Mod(0,u^360)
N    = terminal u^72 normalization operator
ZERO = terminal zero witness
```

The arithmetic-shadow representation SHALL NOT erase witness or grouping identity.

For the central matrix comparator at baseline matrix lanes:

```text
C3=(361E5-360E6)L
```

Required modes include:

| `E5` | `E6` | Result |
|---:|---:|---|
| `1` | `1` | `L` |
| `k` | `k` | `kL` |
| `360` | `361` | `0` |
| `1` | `-1` | `721L` |
| `1` | `0` | `361L` |
| `0` | `1` | `-360L` |

The exact cancellation ratio is:

```text
E5/E6 = 360/361
```

for nonzero `E6`.

# 16. Gauge invariants

## 16.1 Matrix gauge

The matrix-list gauge SHALL be:

```text
gM=P18/P12
```

When:

```text
P18=P12≠0
```

the common matrix-list shell SHALL cancel.

## 16.2 Row gauges

The row gauges SHALL be:

```text
gR1=P19/P13
gR2=P20/P14
gR3=P21/P15
```

When:

```text
P19=P13≠0
P20=P14≠0
P21=P15≠0
```

the corresponding direct and inverse row shell SHALL cancel.

A matched signed or nonuniform triple SHALL also cancel:

```text
(P13,P14,P15)=(P19,P20,P21)=(a,b,c)
```

for nonzero `a`, `b`, and `c`.

## 16.3 Ratio-channel encoding

When the direct and inverse row shells differ, the lower lane SHALL expose:

```text
diag(gR1,gR2,gR3)L
```

The normalized row sums SHALL recover the encoded values:

```text
row_sum_1/(15×common_gain)=gR1×P24
row_sum_2/(15×common_gain)=gR2×P25
row_sum_3/(15×common_gain)=gR3×P26
```

This SHALL be implemented as a three-channel exact rational register.

# 17. Lo Shu kernel algebra

The runtime SHALL verify:

```text
det(L)=360
trace(L)=15
sum(Lij)=45
ΣLij²=285
```

Every row, column, and principal diagonal SHALL sum to `15`.

The exact square identity is:

```text
L² =
[[59,83,83],
 [83,59,83],
 [83,83,59]]
```

and:

```text
L²=83J-24I
```

where `J` is the all-ones matrix.

The runtime SHALL expose two kernel modes:

```text
ODD_KERNEL  = oriented Lo Shu component
EVEN_KERNEL = symmetric identity/uniform-plane component
```

The eigenstructure of `L²` SHALL be registered as:

```text
uniform vector eigenvalue: 225
zero-sum plane eigenvalue: -24
zero-sum plane multiplicity: 2
```

The Cayley–Hamilton identity SHALL be:

```text
L³-15L²+24L-360I=0
```

The exact inverse SHALL be:

```text
L^-1=(83J-15L)/360
```

Generic matrix inversion SHALL NOT be used for `L` when this bounded exact formula is applicable.

Arbitrary powers SHALL reduce to:

```text
L^(2n)   = an I + bn J
L^(2n+1) = cn L + dn J
```

The runtime SHALL implement a bounded recurrence rather than unbounded repeated matrix multiplication.

# 18. Sparse virtual-memristor state

## 18.1 Identity baseline

The identity state SHALL be:

```text
Pi=1
Ej=1
```

The stored mutable parameter delta SHALL be:

```text
δθ=θ-1
```

Therefore:

```text
θ=1 ↔ δθ=0
```

Unchanged parameters SHALL be compressible as zero-state records without losing thread identity.

## 18.2 Sparse mutation

A parameter mutation SHALL NOT automatically rewrite all 5,184 cells.

The runtime SHALL calculate:

```text
affected_raw_threads
affected_derived_threads
affected_banks
affected_cells
affected_comparators
affected_receipts
```

Only the dependency closure SHALL enter the hot-path transition.

A complete 5,184-cell replay MAY occur during explicit full audit, migration, corruption recovery, deterministic cross-architecture replay, or release closure. It SHALL NOT be the default behavior for a local parameter update.

## 18.3 Zero-state distinction

The runtime SHALL distinguish:

```text
IDENTITY_ZERO_DELTA
EXPLICIT_PARAMETER_ZERO
CANCELLED_ZERO
MODULAR_ZERO
UNINITIALIZED
QUARANTINED
```

A denominator or inverse-input parameter assigned explicit zero SHALL be rejected before dispatch.

# 19. Dependency graph

The implementation SHALL include a machine-readable dependency graph.

At minimum:

```text
α depends on P1..P6

β depends on P1,P9,P10,P11,P12,P16,P17,P18,P23

ρ1 depends on P13,P19,P24
ρ2 depends on P14,P20,P25
ρ3 depends on P15,P21,P26

dU depends on P7
dV depends on P22

C1 depends on U,E1,E2,XY
C2 depends on XY,E3,E4,P8
C3 depends on U,V,E5,E6
C4 depends on V,E7,E8,P27
C5 depends on P27,E9,E10,P28
C6 depends on C3,E11,E12,u^72

Δ depends on U,V
closure receipt depends on all committed affected nodes
```

Dependency edges SHALL be ordered and versioned.

No dependency may be inferred solely from mutable array position.

# 20. Propagation schedule

The canonical stage sequence SHALL be:

```text
STAGE 0  SOURCE
STAGE 1  NORMALIZED_DELTA
STAGE 2  RECIPROCAL_OR_GAUGE
STAGE 3  INVERSE_DEPTH
STAGE 4  PROJECTED_STATE
STAGE 5  COMPARATOR
STAGE 6  PROPAGATED_DELTA
STAGE 7  COMMITTED_STATE
STAGE 8  REPLAY_RECEIPT
```

The runtime MAY compute independent cells or threads concurrently.

The runtime SHALL NOT commit out of stage order.

A stage receipt SHALL bind:

```text
transition_id
stage
affected_thread_bitmap
affected_bank_bitmap
affected_cell_ranges
input_root
output_root
dependency_root
invariant_results
prior_stage_receipt
```

# 21. VM81 authority and atomic commit

Exactly one VM81 runtime authority kernel SHALL own canonical mutation.

Worker threads, GPU kernels, AI agents, APIs, and UI surfaces MAY calculate candidates, dependencies, deltas, matrix projections, comparison witnesses, and provisional receipts. They SHALL NOT independently commit canonical state.

The atomic commit protocol SHALL be:

```text
begin candidate
→ validate source identity
→ validate parameter types
→ validate nonzero denominator requirements
→ validate dependency closure
→ validate matrix dimensions
→ validate exact rational normalization
→ validate Lo Shu kernel identities
→ validate comparator ordering
→ validate sparse write set
→ validate prior state root
→ acquire VM81 commit authority
→ append immutable transition
→ update current-state pointers
→ emit Hash72 receipt
→ emit Hash216 transition identity
→ release authority
```

A failure before append SHALL produce no committed mutation.

A failure after append but before pointer publication SHALL be recoverable through the immutable transition record.

# 22. Concurrency model

Each of the 64 threads SHALL receive one stable Base64-addressable VM81 port.

Thread-local internal computation MAY use unrestricted internal degrees of freedom subject to exact numeric authority, dependency bounds, capability restrictions, resource bounds, stage order, and single commit authority.

Required concurrency properties:

```text
one permanent thread identity
one permanent 81-cell block
no cross-thread memory write without dependency authorization
no direct mutation of another thread’s committed bank
candidate exchange through versioned deltas
atomic multi-thread commit
deterministic merge order
```

Concurrent candidate results SHALL be ordered by a canonical tuple equivalent to:

```text
(
  transition_sequence,
  dependency_depth,
  thread_id,
  bank_id,
  loshu_index,
  operation_id
)
```

Timing SHALL NOT determine canonical ordering.

# 23. Reciprocal peers

Every global cell MAY have a reciprocal phase peer:

```text
peer_row=(-global_row) mod 72
peer_col=(-global_col) mod 72
```

Reciprocal pairing SHALL be metadata and SHALL NOT overwrite local thread identity.

A reciprocal operation SHALL record:

```text
source_address
reciprocal_address
source_value
reciprocal_value
ordered_pair
phase_state
cancellation_result
```

Reciprocal peers MAY support entangled reciprocal phase-gear propagation across the 5,184-cell circuit.

# 24. Hash72 execution receipts

Every accepted operation SHALL emit a Hash72 receipt containing at minimum:

```text
contract_id
pass_number
source_hash72
prior_receipt_hash72
transition_sequence
operation_id
parameter_ids
before_parameter_root
after_parameter_root
affected_thread_bitmap
affected_cell_digest
dependency_root
upper_matrix_root
lower_matrix_root
comparator_roots
successor_residual_root
vm81_admission_result
commit_result
replay_result
receipt_hash72
```

Receipt emission SHALL be deterministic.

Hash72 SHALL represent execution and closure evidence. It SHALL NOT replace Hash216 historical object identity.

# 25. Hash216 object and history identity

The following SHALL receive distinct Hash216 identities:

```text
source program
parameter registry
thread map
5,184-cell address map
dependency graph
raw parameter state
derived parameter state
matrix projection
comparator set
candidate transition
committed transition
rollback transition
repair transition
replay result
release evidence set
```

A current logical object and its historical versioned transitions SHALL remain distinct.

Repeated updates to one parameter SHALL generate new versioned transition identities without creating a new parameter-thread identity.

# 26. Native C11 ABI

Pass 168 SHALL provide a strict C11 implementation.

Required opaque types SHALL include equivalents of:

```c
typedef struct hhs_p168_runtime hhs_p168_runtime;
typedef struct hhs_p168_program hhs_p168_program;
typedef struct hhs_p168_transition hhs_p168_transition;
typedef struct hhs_p168_receipt hhs_p168_receipt;
typedef struct hhs_p168_bigint hhs_p168_bigint;
typedef struct hhs_p168_rational hhs_p168_rational;
typedef struct hhs_p168_matrix3 hhs_p168_matrix3;
```

Required address type:

```c
typedef struct {
    uint16_t global_index;   /* 0..5183 */
    uint8_t global_row;      /* 0..71 */
    uint8_t global_col;      /* 0..71 */
    uint8_t thread_id;       /* 0..63 */
    uint8_t local_index;     /* 0..80 */
    uint8_t bank_id;         /* 0..8 */
    uint8_t loshu_index;     /* 0..8 */
} hhs_p168_address;
```

Required callable operations SHALL include equivalents of:

```text
hhs_p168_runtime_create
hhs_p168_runtime_destroy
hhs_p168_load_source
hhs_p168_verify_source_identity
hhs_p168_register_parameters
hhs_p168_get_parameter_registry
hhs_p168_set_parameter_candidate
hhs_p168_get_parameter
hhs_p168_get_parameter_delta
hhs_p168_map_global_address
hhs_p168_map_vm81_address
hhs_p168_resolve_dependencies
hhs_p168_evaluate_upper_lane
hhs_p168_evaluate_lower_lane
hhs_p168_evaluate_comparator
hhs_p168_evaluate_all_comparators
hhs_p168_get_loshu_kernel
hhs_p168_get_loshu_even_kernel
hhs_p168_prepare_transition
hhs_p168_validate_transition
hhs_p168_commit_transition
hhs_p168_rollback_transition
hhs_p168_repair_state
hhs_p168_replay_transition
hhs_p168_export_hash72_receipt
hhs_p168_export_hash216_identity
hhs_p168_export_state
hhs_p168_import_state
```

Every function SHALL return a stable status code and SHALL NOT communicate authoritative errors only through logs.

# 27. HARMONICODE AST and IR

Required AST nodes SHALL include equivalents of:

```text
ParameterCircuitProgram
ParameterShell
EqualityHalfGate
SourceSpan
MatrixLiteral
ListMatrixLiteral
OrderedProduct
GroupedOrderedProduct
ElementwiseScalarQuotient
ExactMatrixInverse
InverseDepth
ModuloWitness
MatrixLane
Comparator
GaugePair
RowChannel
LoShuKernel
SparseDelta
VM81Address
CommitGate
ReceiptClosure
```

Required IR blocks SHALL include:

```text
REGISTER_PARAMETER
LOAD_SOURCE_VALUE
NORMALIZE_DELTA
CALCULATE_RECIPROCAL
CALCULATE_GAUGE
SELECT_INVERSE_DEPTH
PROJECT_MATRIX3
RUN_COMPARATOR
PROPAGATE_DELTA
VALIDATE_DEPENDENCY_CLOSURE
VM81_ADMIT
ATOMIC_COMMIT
EMIT_HASH72_RECEIPT
EMIT_HASH216_IDENTITY
REPLAY_VERIFY
```

The compiler SHALL preserve operand order and source spans.

# 28. Command-line interface

Required CLI operations SHALL include:

```text
hhs parameter-circuit status
hhs parameter-circuit inspect
hhs parameter-circuit source
hhs parameter-circuit map
hhs parameter-circuit threads
hhs parameter-circuit banks
hhs parameter-circuit parameters
hhs parameter-circuit get P13
hhs parameter-circuit set P13 2
hhs parameter-circuit set E5 360
hhs parameter-circuit evaluate
hhs parameter-circuit evaluate --lane upper
hhs parameter-circuit evaluate --lane lower
hhs parameter-circuit compare C3
hhs parameter-circuit dependencies P13
hhs parameter-circuit affected-cells P13
hhs parameter-circuit commit
hhs parameter-circuit rollback <transition-id>
hhs parameter-circuit replay <transition-id>
hhs parameter-circuit receipt <transition-id>
hhs parameter-circuit validate
hhs parameter-circuit benchmark
```

Mutation commands SHALL support candidate-only execution and explicit commit.

Human-readable and machine-readable output SHALL be separable through `text`, `json`, and `jsonl` output profiles.

# 29. HTTP API

Required endpoints SHALL include equivalents of:

```http
GET  /v1/parameter-circuit
GET  /v1/parameter-circuit/source
GET  /v1/parameter-circuit/map
GET  /v1/parameter-circuit/threads
GET  /v1/parameter-circuit/parameters
GET  /v1/parameter-circuit/parameters/{parameter_id}
POST /v1/parameter-circuit/candidates
GET  /v1/parameter-circuit/candidates/{candidate_id}
POST /v1/parameter-circuit/candidates/{candidate_id}/validate
POST /v1/parameter-circuit/candidates/{candidate_id}/commit
GET  /v1/parameter-circuit/dependencies/{parameter_id}
GET  /v1/parameter-circuit/matrices/upper
GET  /v1/parameter-circuit/matrices/lower
GET  /v1/parameter-circuit/comparators/{comparator_id}
GET  /v1/parameter-circuit/transitions/{transition_id}
POST /v1/parameter-circuit/transitions/{transition_id}/replay
POST /v1/parameter-circuit/transitions/{transition_id}/rollback
GET  /v1/parameter-circuit/transitions/{transition_id}/receipt
```

An API request SHALL NOT mutate committed state merely by reading or evaluating.

# 30. GPU and cluster execution

The 64-thread topology SHALL map naturally onto one 64-lane workgroup or an equivalent bounded cluster.

Each lane SHALL own one VM81 block:

```text
lane_id ↔ thread_id ↔ 81-cell parameter block
```

GPU implementations MAY calculate candidate banks in parallel.

Canonical state SHALL remain independent of GPU vendor, warp or wavefront width, thread scheduling, device timing, fused floating-point behavior, host endianness, and architecture-specific padding.

Exact arithmetic MAY use integer limbs, rational handles, canonical serialized BigInts, bounded symbolic kernels, and CPU-assisted exact commit verification.

A GPU result SHALL remain candidate evidence until the VM81 authority kernel verifies exact canonical output.

The implementation SHALL expose the dimensional relationship:

```text
(81:72:64)²
```

as topology metadata without conflating the 81-cell local block, 72×72 global circuit, and 64-thread execution fabric.

# 31. Resource and performance requirements

Pass 168 SHALL measure:

- full initialization cost;
- source-registration cost;
- single-parameter candidate cost;
- dependency-resolution cost;
- matrix projection cost;
- comparator cost;
- sparse commit cost;
- full 5,184-cell replay cost;
- receipt cost;
- Hash216 transition indexing cost;
- CPU and GPU candidate performance.

The required complexity class for a local mutation is:

```text
O(affected dependency closure)
```

rather than unconditional:

```text
O(5184)
```

A benchmark SHALL demonstrate at least:

1. one local raw parameter update;
2. one global parameter update such as `P1`;
3. one equality-only update;
4. one matched gauge update;
5. one mismatched row-channel update;
6. one inverse-depth update;
7. one complete replay.

Performance evidence SHALL distinguish calculation latency from authority, receipt, and persistence latency.

# 32. Validation requirements

## 32.1 Structural tests

The implementation SHALL prove:

```text
72×72 = 5184 unique global cells
64 unique threads
81 cells per thread
9 banks per thread
9 cells per bank
40 raw channels
24 derived channels
no overlapping global address
exact inverse addressing
```

Every one of the 5,184 cells SHALL be visited by executable validation.

## 32.2 Source tests

Tests SHALL verify:

- exact source bytes;
- twenty-eight matched parenthesis pairs;
- twelve literal equality characters;
- six `==` tokens;
- stable parameter identifiers;
- stable source spans;
- brace-matrix and list-matrix distinction;
- `x*y` and `(x*y)` distinction;
- no unauthorized commutation.

## 32.3 Matrix tests

Tests SHALL verify:

```text
det(F)=0
rank(F)=2
rank(Q)=3
Q Q^-1=I
U=361L at baseline
V=360L at baseline
U-V=L
L²=83J-24I
det(L)=360
L³-15L²+24L-360I=0
L^-1=(83J-15L)/360
```

## 32.4 Parameter tests

Every `Pi` and `Ej` SHALL be tested independently with at least:

```text
-2, -1, 0, 1, 2, 3
```

where semantically admissible.

Zero SHALL be rejected for denominator and inverse-input roles.

Every parameter SHALL also participate in grouped tests.

## 32.5 Gauge tests

Required tests include:

- matched matrix gauge;
- mismatched matrix gauge;
- matched row gauges;
- mismatched row gauges;
- signed matched gauges;
- nonuniform matched gauges;
- ratio recovery from row sums.

## 32.6 Comparator tests

All six comparators SHALL receive baseline, common-gain, left-only, right-only, phase-inversion, exact-cancellation, zero-witness, and grouped ordered-product tests.

## 32.7 Sparse mutation tests

Required cases include:

```text
P13-only mutation
P1 global mutation
P7 inverse-depth mutation
E5-only mutation
E5/E6 cancellation mutation
matched P13/P19 mutation
mismatched P13/P19 mutation
```

For each case, tests SHALL prove exact affected-thread set, exact affected-bank set, exact affected-cell set or bounded cell ranges, unchanged-state identity, deterministic commit, and deterministic replay.

## 32.8 Negative tests

Negative tests SHALL include:

- malformed source;
- unbalanced parentheses;
- missing equality half-gate;
- duplicate parameter identifier;
- invalid thread mapping;
- duplicate global address;
- out-of-range local address;
- zero denominator parameter;
- singular negative matrix power;
- floating-point canonical value;
- unauthorized commutation;
- unordered comparator operands;
- stale dependency version;
- stale prior-state root;
- conflicting concurrent commit;
- receipt mismatch;
- Hash216 identity mismatch;
- replay divergence;
- Pass 167 inheritance mismatch.

## 32.9 Native validation

The C11 implementation SHALL pass warnings-as-errors compilation, unit tests, integration tests, property tests, deterministic fuzzing, AddressSanitizer, UndefinedBehaviorSanitizer, leak detection, x86-64 execution, ARM64 execution, and cross-architecture replay comparison.

Previously verified unaffected inherited suites SHALL remain frozen. Only dependency-affected tests SHALL be rerun during development, followed by one final integration and replay pass.

# 33. Required evidence artifacts

Pass 168 SHALL produce at minimum:

```text
HHS_PASS_168_CONTRACT.md
HHS_PASS_168_AUTHORITY_BINDING.json
HHS_PASS_168_SOURCE_FIXTURE.harmonicode
HHS_PASS_168_PARAMETER_REGISTRY.json
HHS_PASS_168_EQUALITY_HALF_GATE_REGISTRY.json
HHS_PASS_168_THREAD_MAP.json
HHS_PASS_168_5184_CELL_MAP.json
HHS_PASS_168_BANK_LAYOUT.json
HHS_PASS_168_DEPENDENCY_GRAPH.json
HHS_PASS_168_ABI.json
HHS_PASS_168_API_SCHEMA.json
HHS_PASS_168_CLI_MATRIX.json
HHS_PASS_168_POSITIVE_TEST_MATRIX.json
HHS_PASS_168_NEGATIVE_TEST_MATRIX.json
HHS_PASS_168_5184_COVERAGE_REPORT.json
HHS_PASS_168_SPARSE_UPDATE_REPORT.json
HHS_PASS_168_GPU_MAPPING_REPORT.json
HHS_PASS_168_CROSS_ARCH_REPLAY_REPORT.json
HHS_PASS_168_SANITIZER_REPORT.json
HHS_PASS_168_BENCHMARK_REPORT.json
HHS_PASS_168_EVIDENCE_MANIFEST.json
HHS_PASS_168_COMPLETION_RECEIPT.json
```

The evidence manifest SHALL include byte length and SHA-256 for every artifact.

# 34. Required implementation layout

The implementation SHOULD use a source-oriented layout equivalent to:

```text
native_projects/hhs_pass168_5184_parameter_circuit/
├── CMakeLists.txt
├── Makefile
├── README.md
├── contracts/
├── include/
│   ├── hhs_pass168_api.h
│   ├── hhs_pass168_types.h
│   ├── hhs_pass168_status.h
│   └── hhs_pass168_receipt.h
├── src/
│   ├── hhs_pass168_source.c
│   ├── hhs_pass168_registry.c
│   ├── hhs_pass168_address.c
│   ├── hhs_pass168_rational.c
│   ├── hhs_pass168_matrix3.c
│   ├── hhs_pass168_dependency.c
│   ├── hhs_pass168_comparator.c
│   ├── hhs_pass168_loshu.c
│   ├── hhs_pass168_transition.c
│   ├── hhs_pass168_runtime.c
│   ├── hhs_pass168_receipt.c
│   └── hhs_pass168_cli.c
├── tests/
├── schemas/
├── fixtures/
├── tools/
└── evidence/
```

Only new and modified source-oriented files SHALL be committed. The full inherited repository SHALL NOT be recommitted as a duplicate archive.

# 35. Forbidden implementations

Pass 168 SHALL NOT:

1. solve the source as a classical equation;
2. merge all parentheses into one parameter;
3. merge both characters of `==` into one unaddressable Boolean;
4. commute `x*y` into `y*x`;
5. erase grouping distinctions;
6. treat brace matrices and list matrices as source-identical;
7. invert singular `F` directly;
8. replace exact rational arithmetic with canonical floating point;
9. assign two source parameters to one thread identity;
10. dynamically renumber threads after commit;
11. permit worker threads to commit canonical state;
12. rewrite all 5,184 cells for every local mutation;
13. validate the full historical chain on every hot-path operation;
14. accept a stale dependency root;
15. accept a missing receipt;
16. use fallback success after invariant failure;
17. report candidate computation as committed execution;
18. use comments or documentation as a substitute for callable implementation;
19. classify contract-only artifacts as implementation complete;
20. erase the typed distinction between Pass 167 PCM snapshots and Pass 168 parameter-circuit cells.

# 36. Implementation stages

## Stage A — Authority and source binding

Deliver exact source fixture, source digest, parameter registry, equality half-gate registry, and Pass 167 inheritance binding.

## Stage B — Address and topology

Deliver the 64-thread map, 5,184-cell map, reversible addressing, nine-bank layout, and full coverage tests.

## Stage C — Exact arithmetic and matrices

Deliver the BigInt rational layer, 3×3 matrix layer, reciprocal quotient, inverse depth, and Lo Shu bounded algebra.

## Stage D — Dependency and sparse state

Deliver the dependency graph, sparse delta representation, affected-thread calculation, affected-cell calculation, and virtual-memristor state cache.

## Stage E — Comparator circuit

Deliver six equality comparators, ordered half-gates, witness preservation, and exact cancellation and projection modes.

## Stage F — Native authority and persistence

Deliver VM81 admission, atomic commit, immutable transitions, rollback, repair, Hash72 receipts, and Hash216 identities.

## Stage G — Control surfaces

Deliver the C ABI, HARMONICODE lowering, CLI, HTTP API, and machine-readable schemas.

## Stage H — Parallel execution

Deliver 64-lane CPU/GPU candidate scheduling, deterministic merge, cross-device equivalence, and resource bounds.

## Stage I — Closure

Deliver positive and negative matrices, 5,184-cell coverage, sanitizers, benchmarks, cross-architecture replay, final evidence manifest, and completion receipt.

# 37. Terminal acceptance criteria

Pass 168 may receive terminal classification only when all of the following are true:

```text
pass_167_inheritance_bound=true
source_preserved=true
parenthesis_parameters_registered=28
equality_half_gates_registered=12
threads_registered=64
raw_threads=40
derived_threads=24
cells_covered=5184
duplicate_addresses=0
inverse_address_failures=0
banks_per_thread=9
cells_per_bank=9
exact_rational_authority=true
floating_point_canonical_authority=false
baseline_upper_equals_361L=true
baseline_lower_equals_360L=true
successor_residual_equals_L=true
loshu_square_identity=true
gauge_cancellation_verified=true
ratio_channels_verified=true
comparators_verified=6
sparse_dependency_updates_verified=true
single_vm81_commit_authority=true
hash72_receipts_verified=true
hash216_identity_verified=true
rollback_verified=true
repair_verified=true
deterministic_replay_verified=true
x86_64_verified=true
arm64_verified=true
sanitizers_passed=true
fallback_used=false
evidence_manifest_verified=true
```

The terminal classification SHALL be exactly:

```text
HHS_PASS_168_VM81_5184_CELL_HARMONICODE_PARAMETER_CIRCUIT_AND_SPARSE_TENSOR_CONTROL_FABRIC_VERIFIED
```

# 38. Authorized implementation directive

```text
PASS 168 AUTHORIZED
⇒ FULL IMPLEMENTATION REQUIRED
⇒ ALL 5,184 CELLS ADDRESSABLE
⇒ ALL 40 SOURCE PARAMETERS PRESERVED
⇒ ALL 24 DERIVED THREADS IMPLEMENTED
⇒ ALL 12 EQUALITY CHARACTERS INDEPENDENT
⇒ EXACT 3×3 MATRIX AUTHORITY
⇒ DEPENDENCY-SCOPED SPARSE PROPAGATION
⇒ ONE VM81 COMMIT AUTHORITY
⇒ HASH72 RECEIPTS
⇒ HASH216 HISTORY
⇒ PASS 167 DIMENSIONAL AND AUTHORITY INHERITANCE
⇒ DETERMINISTIC REPLAY
⇒ NO FALLBACK SUCCESS
```
