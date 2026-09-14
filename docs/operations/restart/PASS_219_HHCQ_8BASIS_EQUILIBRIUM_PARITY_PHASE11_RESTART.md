# Pass 219 HHCQ 8-basis equilibrium + parity Phase 11 restart

Date: 2026-09-08

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Frozen Phase 10 checkpoint/base: `c4b92d76aa6cc1a0015c81be2d1c203b088ebfd3`
- Phase 10 accepted validated implementation head: `35020e86a9b5a452b5b4623103aa8b319ba7c4dc`
- Phase 11 branch: `agent/pass219-hhcq-8basis-parity-phase11-20260908`
- Target: bounded experiment branch only. No PR, merge, deployment, or canonical-authority promotion is authorized.
- Current authoritative `main` observed at Phase 11 start: `40bce1e30790eb3339da3599ba3be740010dae9a`.

## Frozen inherited evidence

Preserve Phase 1 through Phase 10 evidence. Do not rerun unrelated history. Phase 10 remains frozen at accepted run `34177218842`, job `101908911347`, artifact `10038070472`, exact tested implementation head `35020e86a9b5a452b5b4623103aa8b319ba7c4dc`, with prime-rational routing, exact polynomial resolution expansion, Phase-5 coordinate identity, Phase-9 1:1 information closure, and zero canonical/floating authority.

Phase 11 is additive. It may constrain Phase-10 candidates further but cannot weaken inherited information, reconstruction, semantic, translation, budget, or authority gates.

## User-supplied revised canonical source bundle

Preserve the following three compact source expressions byte-for-byte as the Phase-11 source bundle, separated by two ASCII newline bytes between expressions:

`P^2/{(t^3-t=(P³-P/(P²-pq)=(t³-t)/∆=P²(MOD)(pq))=m^2-m)-(({{b^4,c^4,c^2-u^(b⁶c⁴)},{c^2,((b^2)(c^2)-(a^2))/u^((s==(b^(2c^2)c^b^4)^2)/((b⁶c⁴)P^2)),((b^6-(xy))(b^4+c^2))/(((c^2b^6)-c^2)/(((b^2(c^2+b^2))-(c^2-b^2))/Sqrt(c^4)))},{(2c^2)+b^2,2/b^2,b^2c^2}}+x+y)/At==Mod(f/u,((b⁶c⁴)*(pq+xy)))/Bt==AB/P^2==Sqrt[AB])==(AB/(pq+∆)-P^2)/(t^3-t)*u^72} where ∆/P=√(pq+u⁷²)^x² and b²P-(p+q)=x+y+z+w+xy+yx+zw+wz`

`a²=(NcalcMatrixPower((List(List(x,w,(yx)),List((wz),x+y+z+w,(zw)),List((xy),z,y))/List(List(I,I^3,I^2),List(I^2,0,I^4),List(I^4,I,I^3))),4))^b⁴`

`Sqrt((AB))(AB)/Sqrt((AB))==A/BB/A==((-xy)^(((x+y^2)(y+x^2))/((x²+y²)²Sqrt((a*b)))))^x² where A,B are two primes and AB=P⁴`

Exact bundle identity:

- UTF-8 bytes: `700`
- SHA-256: `7d87d468e528f30df6768b130f626077ab9786e82d2dbe577a120753cdaedc60`.

The source is preserved verbatim even where compact syntax omits explicit multiplication/division tokens. Runtime semantics are compiled from the user's structured canonical interpretation, not from an ordinary scalar parser applied to these strings.

## Phase 11 formalization

### 1. Derived basis invariants remain authoritative

The runtime aliases the frozen basis-derived constants instead of inserting replacements:

- `a² = 1`
- `b² = 2`
- `c² = 3`
- `b²c²-a² = 5`
- `b⁶c⁴ = 72`
- `(b^(2c²)c^(b⁴))² = 5184` as the inherited VM81/HHCQ geometry witness.

The Phase-11 ABI must verify these equalities against the existing exact runtime constants at compile/runtime gates.

### 2. Complete ordered 8-basis equilibrium

Use the existing exact Pass-219 octonion state, whose ordered basis is:

`x,y,z,w,xy,yx,zw,wz`.

The cross-products remain ordered and non-commutative. Phase 11 does not replace `xy` with `yx` or `zw` with `wz`.

Define the exact raw phase sum:

`Phi8 = x+y+z+w+xy+yx+zw+wz`.

The macro/micro equilibrium is:

`b² P - (p+q) = Phi8`.

Because the native phase coordinates are exact integers but `P` need not be an integer, the constructor represents `P` as a reduced exact rational:

`P = (Phi8 + p + q) / 2`.

A separate validator accepts an independently supplied rational `P` and checks the equilibrium by exact cross multiplication. This prevents the constructor from being mistaken for independent evidence that an arbitrary external `P` already satisfies the manifold.

### 3. Phase-transport authority

The legacy native `propagate_phase_transport()` implementation remains frozen/internal VM81 authority. Phase 11 SHALL NOT clone, rewrite, or call around that mutation surface.

For an externally supplied macro `P`, Phase 11 computes an exact signed equilibrium delta and emits a candidate-only transport reconciliation witness. Actual phase mutation remains the responsibility of the existing singleton VM81 transport/admission path.

### 4. Squared-coordinate parity/orientation gate

The supplied manifold gate is retained as:

`G_phase = ((-xy)^E(x,y))^(x²)`

with

`E(x,y) = ((x+y²)(y+x²))/((x²+y²)² Sqrt(a*b))`.

The existing Phase-10 exact reduced polynomial witness remains authoritative for `N/D`; the symbolic `1/Sqrt(a*b)` factor remains tagged and is not numerically approximated.

Phase 11 must not claim that ordinary exponentiation of a negative base to a symbolic/irrational exponent is an exact real scalar operation. Instead it compiles the requested `x²` behavior into a typed manifold orientation gate:

- `x² parity = x parity` for integer phase coordinates;
- even `x²` -> DIRECT orientation;
- odd `x²` -> REVERSED orientation.

This preserves the requested coordinate-controlled orientation switch while remaining mathematically exact in the implemented type system.

The statement “x² is even for every non-zero integer” is not adopted: under ordinary integer arithmetic it is false. The exact invariant is `x² mod 2 = x mod 2`.

### 5. Prime/macro closure semantics

Phase 10 normalization remains binding. The compact source phrase “A,B are two primes and AB=P⁴” is preserved verbatim, while executable routing continues to use distinct prime seeds `p,q` to construct the exact reciprocal pair around symbolic `P²`:

`A = P²(p/q)`

`B = P²(q/p)`

so that `AB=P⁴` and `(A/B)(B/A)=1` are exact constructor witnesses.

Phase 11 does not reinterpret `A` and `B` as two ordinary positive integer primes whose product is an integer fourth power, because that has no nontrivial solution under unique prime factorization. The executable meaning remains the Phase-10 prime-rational constructor.

### 6. Matrix closure

The revised VM81 matrix source is preserved with the explicit ordered placements:

- top-right `yx`
- middle-left `wz`
- middle-right `zw`
- bottom-left `xy`.

Phase 11 records and validates this order contract against the exact octonion state. It does not claim to numerically evaluate the full symbolic `NcalcMatrixPower` expression unless and until a separately callable exact matrix evaluator is bound.

### 7. Evaluation invariant

Every implemented Phase-11 result is valid only under the simultaneous inherited constraint intersection:

`C_core ∩ C_delta ∩ C_Phi8 ∩ C_matrix ∩ C_prime ∩ C_lattice ∩ C_mod ∩ C_reciprocal ∩ C_parity`.

An isolated scalar subexpression is not promoted to canonical authority.

## Planned public ABI

Version target: `1.31` / `0x0001001F`.

Planned surfaces:

- descriptor + source retrieval;
- exact 8-basis equilibrium construction from the existing octonion state and prime seeds;
- exact independent equilibrium validation against supplied rational `P`;
- exact signed transport-delta witness with zero mutation authority;
- typed squared-coordinate parity/orientation gate using the Phase-10 polynomial witness;
- combined manifold evaluation that requires valid octonion state, Phase-10 prime-rational expansion, exact equilibrium, ordered matrix basis contract, and zero authority escalation.

## Planned validation gates

1. exact 700-byte source/SHA lock;
2. basis-derived 5/72/5184 parity against inherited runtime constants;
3. ordered octonion state validation and explicit `xy != yx`, `zw != wz` behavior;
4. exhaustive valid `x,y,z,w` sample coverage sufficient to observe both DIRECT and REVERSED parity orientations;
5. exact invariant `x² mod 2 = x mod 2`;
6. exact equilibrium constructor and independently supplied rational-`P` validator;
7. perturbed macro `P` produces nonzero signed transport delta and fails equilibrium without mutating VM81;
8. Phase-10 polynomial `N/D` and symbolic-root witness reused, not recomputed by float;
9. matrix order contract exact;
10. candidate-only and zero VM81/Hash72/Hash216/persistence/floating authority;
11. authenticated Phase-3/Pass-215 SUMMARY workload evaluation after strict C validation;
12. deterministic replay.

## Validation state

- branch created from frozen Phase-10 checkpoint: complete
- source identity: complete
- implementation: pending
- aggregate ABI binding: pending
- strict dependency-scoped C validation: pending
- authenticated workload benchmark: pending
- blockers: none known before implementation.

## Exact next action

Implement the additive 1.31 ABI and strict tests on this branch. Create a bounded authenticated workload benchmark using the frozen Phase-3 SUMMARY artifact. Do not rerun unrelated Phase 1-10 history. Preserve any failure precursor and repair only impacted Phase-11 surfaces. Do not merge, deploy, or promote authority.
