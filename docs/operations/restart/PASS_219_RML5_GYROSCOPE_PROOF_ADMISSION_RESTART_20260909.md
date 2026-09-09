# Pass 219 RML5 Gyroscope Proof/Admission Membrane — Restart Record

## Authoritative lineage

- Base main: `1b66fc81216e8c9a1540c0cbbf2e5e6007438573`
- Branch: `agent/pass219-recursive-manifold-learning-20260909`
- Merge target: `main`
- Pull request: `#414`
- Parent RML4 checkpoint: `b80baaa72e8b46ac1ea17117b577d7965548f807`
- RML5 implementation commit: `af978040794cf714ec2c65f84953ecb8bbf3ff56`
- RML5 tests commit: `e0793780c496ff6f9c0f8063c5d2dfd99d3b7080`
- RML5 contract commit: `2bf0726a526424270b9f6d73f7791cf79170bf52`
- RML5 workflow/implementation head: `dd4769118e17c90fcafad80084d7bea412d20f56`

## Purpose

RML5 turns the repair-forward RML4 architecture audit into executable proof and admission constraints without rewriting the validated RML4 substrate.

The membrane keeps one canonical phase mechanism across algebraic domains:

```text
RML4 eight-channel phase state
→ exact Genesis rational binding
→ typed chiral +/-a^2 polarity witness
→ licensed P-1/P+1 exact projection witness
→ reciprocal transition proof
→ constructive admitted-manifold path proof
→ candidate for existing VM81 admission authority
```

No second canonical mutation/hash authority is introduced.

## Exact Genesis binding

RML5 imports and verifies the already-canonical repository constants from `hhs_runtime/hhs_genesis_severance_protocol_v1.py`:

```text
179971.179971 = 179971179971/1000000
1.001         = 1001/1000
a^2           = 1
```

Floats have no canonical authority.

## Typed chirality polarity witness

The RML4 ordered quarter-turn signs are projected to typed polarity without replacing the rotor state:

```text
xy : +/- a^2
yx : -/+ a^2
zw : +/- a^2
wz : -/+ a^2
```

Admission requires:

```text
sign(xy) = -sign(yx)
sign(zw) = -sign(wz)
```

The +/-a^2 surface is a polarity witness over the richer rotational state, not scalar substitution authority.

## P-1 / P+1 projection witness

Given exact odd `P > 2` plus an upstream verified prime-witness SHA, RML5 constructs:

```text
p = P-1
q = P+1
p+q = 2P
pq = P^2-1
P^2 = pq+1
```

This remains explicitly projection-only and cannot substitute symbols inside the recursive manifold.

## Reciprocal transition closure

For every supplied RML4 transition:

```text
S_i --delta--> S_j
```

RML5 constructs:

```text
S_j ---delta--> S_i
```

and verifies:

- exact cancellation of all eight signed phase deltas;
- restoration of the exact ambient `72^8` state address;
- restoration of phase coordinates;
- restoration of admissible quarter-turn product geometry.

Receipt ancestry is not erased or rewound. RML5 does not claim Hash216 preimage inversion. The proof is exact phase-state bijectivity with append-only evidence ancestry.

## Chiral pair u^36 operator

RML5 adds an exact self-inverse pair operation:

```text
+u^18 <-> -u^18
```

implemented as one `u^36` half-turn applied to both members of one chiral pair.

This preserves:

- product admissibility;
- pair opposition;
- +/-a^2 polarity balance;
- exact reversibility.

## Constructive strong connectivity

The admitted RML5 manifold is the subset of RML4 product-admissible states with opposed chiral pairs.

A finite exact path between any two states in this admitted manifold is constructed without enumerating `72^8` addresses:

1. use `u^36` chiral-pair flips to align sign sectors;
2. for x, y, z, w, take the exact shortest signed `Z_72` displacement;
3. move each generating primitive and its dependent product by the same displacement.

Because target product phases are determined by the target primitive phases and quarter-turn signs, the construction reaches the target state exactly while remaining inside the admitted manifold.

Proof method:

```text
CONSTRUCTIVE_U36_CHIRAL_FLIPS_PLUS_COUPLED_Z72_GENERATOR_MOVES
```

This proves strong connectivity for the RML5 balanced-chirality admitted manifold, not for arbitrary disequilibrated ambient tuples.

## State-level admission

RML5 state admission requires all of:

- RML4 product geometry admissible;
- opposed chiral pairs;
- exact canonical Genesis rationals;
- upstream verified odd-prime witness;
- P-1/P+1 projection equalities;
- `Omega = true` witness;
- `Delta e = 0` system-internal constraint witness;
- `Psi = 0` system-internal phase-closure witness.

Successful state result:

```text
RML5_STATE_READY_FOR_RECIPROCAL_TRANSITION_PROOF
```

After reciprocal transition certification:

```text
ready_for_existing_vm81_admission_authority = true
```

RML5 itself retains no VM81 mutation, Hash72 mint, or Hash216 persistence authority.

## Topology status

Implemented now:

- constructive strong-connectivity proof operator for the balanced-chirality admitted manifold.

Still repair-forward proof obligations:

- discrete `S^7` embedding;
- Hopf-fibration preservation under phase transport;
- Bott-periodicity correspondence for the discrete RML manifold.

These remain explicit obligations and are not silently promoted to current kernel facts.

## Files added

- `hhs_runtime/pass219/gyroscope_admission_membrane.py`
- `tests/pass219/test_pass219_gyroscope_admission_membrane.py`
- `contracts/pass219/PASS_219_RML5_GYROSCOPE_PROOF_ADMISSION_MEMBRANE_1_0.json`
- `.github/workflows/pass219-gyroscope-proof-admission-membrane.yml`
- `docs/operations/restart/PASS_219_RML5_GYROSCOPE_PROOF_ADMISSION_RESTART_20260909.md`

## Validation status at checkpoint creation

Dedicated workflow:

- Workflow: `Pass 219 Gyroscope Proof Admission Membrane`
- Run: `34418531519`
- Job: `102688673573`
- Validated target head: `dd4769118e17c90fcafad80084d7bea412d20f56`

At checkpoint creation the targeted job is queued due runner congestion. No failure has been observed from the RML5 dependency scope.

The branch is intentionally checkpointed now under the repository responsiveness policy rather than delaying forward progress for queued external CI.

## Required next action

1. Inspect run `34418531519`, job `102688673573`.
2. If green, freeze the exact result and update the RML5 contract status to validated.
3. If red, repair only the impacted RML5 surface and rerun the exact dependency scope.
4. After RML5 validation, continue to the first topology successor: define a discrete `S^7` embedding candidate for the eight-channel `u^72` phase state and test whether RML5 transition generators preserve the proposed embedding before making Hopf/Bott claims canonical.

Do not rewrite frozen RML1-RML4/I148/Pass169 evidence in place.
