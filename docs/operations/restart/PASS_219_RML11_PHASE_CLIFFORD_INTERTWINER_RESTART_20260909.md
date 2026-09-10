# Pass 219 RML11 Phase-Transport / Clifford Intertwiner — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Working branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent branch head before RML11: `5b055bded3a5891344848d936682625705c87458`
- Parent RML10 validated head: `6f34ad65377e48ed12b417c54e73a5e4f5f0c553`
- RML11 implementation: `773fe9d3a083b76fc30bfbdaf42f624e6757310d`
- RML11 tests: `616b0e93307d444883ba36620c045ca93eee80be`
- RML11 contract: `774c649db23b90b6b4390ee2d0d9c5307707aad5`
- RML11 workflow / validation target: `01bfb38b10976ac23dabc418441035522e656bc1`

The unrelated temporary ref `agent/pass219-recursive-manifold-learning-20260909-rml9-temp` remains non-authoritative and is not a restart source.

## Parent validation frozen

RML10 remains dependency-scoped validated:

- Workflow: `Pass 219 Real Clifford Morita Witness`
- Run: `34431130138`
- Job: `102726687935`
- Result: `18 passed, 0 failed, 1 inherited pytest-config warning in 15.57s`
- Inherited Pass188 native validation: green
- Pass188 hydrated states: `1,259,712`
- Pass188 coordinate drift: `0`
- Pass188 checksum: `0x11e3bbf0214751c3`

## RML11 implementation purpose

RML11 binds the RML4 `SIGNED_IMAGINARY_PHASE_ROTATION` transition surface to the constructive RML10 `Cl_(0,8) ~= M16(R)` witness without replacing native `u^72` phase state with matrix state.

### One-gyroscope Clifford action

RML11 deliberately does not model product channels as four independent gyroscope axes.

```text
x  -> e_x
y  -> e_y
z  -> e_z
w  -> e_w

xy -> e_x e_y
yx -> e_y e_x
zw -> e_z e_w
wz -> e_w e_z
```

The exact matrix projection requires:

```text
xy = -yx
zw = -wz
```

while ordered channel identity and RML4 reciprocal construction metadata remain receipt-visible even when a matrix projection coincides.

## Exact u72 / Clifford boundary

A signed phase delta is decomposed as

```text
delta = 18*q + r
|r| < 18
```

with sign-symmetric remainder.

- `q` is the exact discrete quarter-cycle component lifted to the Clifford action.
- `r` remains exact native `u^72` phase state.
- No residual is rounded, discarded, or scalarized.
- A complete Clifford lift is claimed only when every residual is zero.

This preserves all 72 phase states while allowing exact Clifford grading at the `u^18` boundary.

## Exact Clifford classification

Let `Omega_8` be the exact volume/chirality operator of the validated RML10 `Cl_(0,8)` representation.

RML11 proves:

```text
primitive actions x,y,z,w          anticommute with Omega_8
product bivectors xy,yx,zw,wz     commute with Omega_8
Omega_8^2                          = I
```

Complete lifts are classified as:

```text
FULL_CL08_MODULE_INTERTWINER
EVEN_CLIFFORD_CHIRALITY_SECTOR_PRESERVING
ODD_CLIFFORD_CHIRALITY_SECTOR_SWAPPING
```

A full module intertwiner must commute with all eight RML10 `Cl_(0,8)` generators. Sector-preserving and sector-swapping classifications are therefore not conflated with full module endomorphism.

## Noncommutative inverse discipline

The forward Clifford factor sequence uses the preserved channel order

```text
x,y,z,w,xy,yx,zw,wz
```

and the exact inverse reverses factor order before applying inverse powers.

RML11 explicitly does not assume that a same-order list of negated exponents is the inverse of a noncommutative product.

## Unified +, *, ^ bridge

The existing RML4 operator identity remains receipt-visible:

```text
+  -> coupled phase displacement
*  -> ordered product-bivector quarter-turn
^  -> recursive phase orbit / repeated Clifford action
```

All three retain `SIGNED_IMAGINARY_PHASE_ROTATION` as the underlying phase primitive. Coincident Clifford matrix projections never collapse the source operator or operand ordering.

## Expected finite RML5 audit

The existing RML5 generator family has exactly:

```text
288 coupled Z72 generator/product moves
2   u36 chiral-pair flips
290 total
```

RML11's executable expected partition is:

```text
18  complete Clifford lifts
272 residual-u72 partial lifts

within the 18 complete lifts:
10 full Cl_(0,8) module intertwiners
0  even sector-preserving nonintertwiners
8  odd chirality-sector swaps
```

The existing Hopf partition remains independent and must remain:

```text
4   same-base identities
286 base-moving Hopf transports
0   inverse restoration failures
```

RML11 does not claim that Hopf classification equals Clifford classification.

## Files added

- `hhs_runtime/pass219/phase_clifford_intertwiner.py`
- `tests/pass219/test_pass219_phase_clifford_intertwiner.py`
- `contracts/pass219/PASS_219_RML11_PHASE_CLIFFORD_INTERTWINER_1_0.json`
- `.github/workflows/pass219-phase-clifford-intertwiner.yml`
- `docs/operations/restart/PASS_219_RML11_PHASE_CLIFFORD_INTERTWINER_RESTART_20260909.md`

## Validation status at checkpoint creation

- Workflow: `Pass 219 Phase Clifford Intertwiner`
- Run: `34432290908`
- Job: `102730127210`
- Validation target head: `01bfb38b10976ac23dabc418441035522e656bc1`
- Status at checkpoint creation: `in_progress`

## Required next action

1. Inspect run `34432290908`, job `102730127210`.
2. If green, record exact native Pass188 output and exact RML10-RML11 pytest count/time, promote the RML11 contract to dependency-scoped validated, and seal this restart record.
3. If red, repair only RML11 and rerun the same targeted dependency scope.
4. Preserve frozen RML1-RML10, Pass187/188, I148, and Pass169 evidence in place.
