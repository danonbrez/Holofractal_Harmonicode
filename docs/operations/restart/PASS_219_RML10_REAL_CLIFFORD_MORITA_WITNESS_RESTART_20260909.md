# Pass 219 RML10 Real Clifford / Morita Witness — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML9 validated head: `22cf66ccb2f511f7187343df1f64bf6d4c4dacee`
- Parent RML9 contract validation seal: `365a0b7d38549f98e95e0679f720ac3aa707d33d`
- Parent RML9 green restart seal: `fc98f5be073fd07ed61e1a4a937b64e9db26384c`
- RML10 implementation: `ac7c5e8d9b515e7974d4d8146456ad8845b14279`
- RML10 tests: `68ec3d9855485bde8fa5eba2295f256012400b6d`
- RML10 contract: `865db5c7ad5f37606ab7f6f129f93d8e3db1a443`
- RML10 workflow / validation target head: `6f34ad65377e48ed12b417c54e73a5e4f5f0c553`

The unrelated temporary ref `agent/pass219-recursive-manifold-learning-20260909-rml9-temp` remains non-authoritative and contains no RML9/RML10 implementation work.

## Parent validation frozen

RML9 is dependency-scoped validated:

- Workflow: `Pass 219 Classical Bott Correspondence`
- Run: `34428473042`
- Job: `102718664741`
- Result: `43 passed, 0 failed, 1 inherited pytest-config warning in 11.40s`
- Inherited Pass188 native validation: green
- Pass188 hydrated states: `1,259,712`
- Pass188 active period-two states: `629,856`
- Pass188 asymmetric collapse states: `629,856`
- Pass188 coordinate drift: `0`
- Pass188 checksum: `0x11e3bbf0214751c3`

## RML10 purpose

RML10 turns the RML9 real-Clifford period-eight reference into a constructive exact witness while preserving the existing runtime authority membrane.

It reuses repository-native exact algebra types:

```text
ORDERED_MATRIX
MatrixProduct
TensorProduct
ExactMatrix
CliffordRotor
```

and introduces no floating-point canonical authority.

## Constructive Cl_(0,8) witness

RML10 uses the convention

```text
e_i^2 = -I
e_i*e_j + e_j*e_i = 0 for i != j
```

and builds eight exact `16x16` real/integer generators from Kronecker products of exact `2x2` matrices.

Required executable proof surface:

```text
8 generator square checks
28 pairwise anticommutation checks
256 ordered Clifford words
256-dimensional M16(R) target space
exact Frobenius orthogonality of all 256 words
```

When all pass, the representation supplies a constructive exact witness

```text
Cl_(0,8) ~= M16(R)
```

at the implemented representation level.

## Explicit Morita context

RML10 also constructs the standard `16x16` matrix units `E_ij` and verifies the full-corner identity

```text
E_ij E_kl = delta_(j,k) E_il
sum_i E_i0 E_00 E_0i = I_16
E_00 M16(A) E_00 ~= A
```

with standard column module `A^16`.

This is the concrete matrix Morita context used by the period-eight factor. RML10 does not claim to formalize every arbitrary module-functor coherence law inside the runtime.

## Eight residue models

Base models:

```text
Cl_(0,0)=R
Cl_(0,1)=C
Cl_(0,2)=H
Cl_(0,3)=H+H
Cl_(0,4)=M2(H)
Cl_(0,5)=M4(C)
Cl_(0,6)=M8(R)
Cl_(0,7)=M8(R)+M8(R)
```

The constructive `M16(R)` factor yields the one-period lifts:

```text
Cl_(0,8)=M16(R)
Cl_(0,9)=M16(C)
Cl_(0,10)=M16(H)
Cl_(0,11)=M16(H)+M16(H)
Cl_(0,12)=M32(H)
Cl_(0,13)=M64(C)
Cl_(0,14)=M128(R)
Cl_(0,15)=M128(R)+M128(R)
```

Each lift has exact real-dimension factor `256` and carries the full-corner Morita witness back to its residue model.

## Native topology binding

The RML10 packet preserves the validated chain:

```text
8 live phase72 coordinates
-> RML6 exact rational S7 ancestry
-> RML7 exact rational S4 Hopf ancestry
-> RML8 Pass187/188 B8/H8 packet
-> RML9 KO/stable-O typed reference
-> RML10 constructive Clifford/Morita witness
```

It does not identify a live phase coordinate with a Clifford matrix coefficient and does not reclassify generator motion by the Clifford model.

Inherited generator partition remains:

```text
4 same-base identities
286 base-moving Hopf transports
0 inverse restoration failures
```

## Authority boundary

RML10 adds no:

- canonical VM81 mutation authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- floating-point canonical authority;
- scalar-projection substitution authority.

It does not claim a physical topological hardware theorem, full S3 closure of the RML6 image, or full RML5 generator fiber-equivariance.

## Files added

- `hhs_runtime/pass219/real_clifford_morita_witness.py`
- `tests/pass219/test_pass219_real_clifford_morita_witness.py`
- `contracts/pass219/PASS_219_RML10_REAL_CLIFFORD_MORITA_WITNESS_1_0.json`
- `.github/workflows/pass219-real-clifford-morita-witness.yml`
- `docs/operations/restart/PASS_219_RML10_REAL_CLIFFORD_MORITA_WITNESS_RESTART_20260909.md`

## Validation status at checkpoint creation

- Workflow: `Pass 219 Real Clifford Morita Witness`
- Run: `34431130138`
- Job: `102726687935`
- Validation target head: `6f34ad65377e48ed12b417c54e73a5e4f5f0c553`
- Status at checkpoint creation: `in_progress`

## Required next action

1. Inspect run `34431130138`, job `102726687935`.
2. If green, freeze exact native Pass188 output and RML8-RML10 pytest count/time; promote the RML10 contract to dependency-scoped validated and create a green restart seal.
3. If red, repair only RML10 and rerun the same dependency scope.
4. Do not rewrite frozen RML1-RML9, Pass187/188, I148, or Pass169 evidence in place.
