# Pass 220 I004 — Genesis Zero-Sum Lo Shu Global Halt

Status: IMPLEMENTED CHECKPOINT / DEPENDENCY-SCOPED CI PENDING / NO AUTHORITY WIDENING

## 1. Purpose

I004 turns the Genesis zero-sum closure law into an executable scheduler boundary.

The system may expand orthogonal constructor branches only while unresolved normalized state or unresolved typed constraint witnesses remain.  When every local Lo Shu nucleus closes at the same global zero center and there is no new raw or normalized state change, scaling halts.

The physics equations and algebraic-number-theory surfaces remain native HARMONICODE computational modalities.  I004 does not reinterpret them as analogies and does not replace their authoritative evaluators.

## 2. Fixed geometry

The I001 normalized VM81 surface contains:

```text
81 cells = 9 local Lo Shu nuclei × 9 cells
Lo Shu = 4 9 2 / 3 5 7 / 8 1 6
```

Inside each local nucleus:

- Lo Shu value `1` is at local flattened index `7`;
- Lo Shu value `7` is at local flattened index `5`.

For nucleus `j in 0..8`:

```text
one_global_index   = 9*j + 7
seven_global_index = 9*j + 5
```

## 3. Local closure

I004 does not independently solve or scalarize the canonical source equations.

Each nucleus consumes typed exact witnesses:

```text
ab_p4_closed
one_ninth_invariant_closed
cell7_constraint_closed
```

A local nucleus is closed only when:

```text
all 9 local normalization offsets == 0
AND local Lo Shu 1-cell offset == 0
AND local Lo Shu 7-cell offset == 0
AND ab_p4_closed
AND one_ninth_invariant_closed
AND cell7_constraint_closed
```

This preserves `AB=P⁴`, the `1/9` invariant, and the 7-cell constraint equations as typed upstream proof surfaces rather than replacing them with a new evaluator.

## 4. Global zero normalization

The global halt predicate requires simultaneous closure:

```text
GLOBAL_ZERO =
    all 81 normalized offsets == 0
AND all 9 local nuclei closed
AND global_modality_zero_closed
```

`global_modality_zero_closed` is a typed exact witness from the aggregate multimodal closure layer.  It represents the requirement that all authoritative modalities resolve to the same Genesis mathematical center.

A single open modality keeps scaling open.

## 5. No-new-state requirement

Zero normalization alone is not enough to halt if a new state is still being generated.

I004 therefore requires both:

```text
current_normalized_offsets == next_normalized_offsets
raw_5184_bit_state_change_zero == true
```

The first check is computed directly over the exact 81-cell normalized vector.

The second is a typed exact witness from the fixed 5184-bit / 648-byte raw ABI state comparison.

Thus:

```text
GLOBAL_STATE_CHANGE_ZERO =
    NORMALIZED_STATE_CHANGE_ZERO
AND RAW_5184_BIT_STATE_CHANGE_ZERO
```

## 6. Halt equation

The executable scheduler predicate is:

```text
HALT =
    GLOBAL_ZERO
AND ALL_LOCAL_NUCLEI_CLOSED
AND GLOBAL_MODALITY_ZERO_CLOSED
AND GLOBAL_STATE_CHANGE_ZERO
```

When `HALT=true`:

```text
candidate_expansion_blocked = true
new_canonical_transition_blocked = true
halt_extends_hash72_ledger = false
halt_mints_hash216_transition = false
```

The halt itself is therefore not a reason to manufacture an additional state-changing Hash216 transition.

## 7. Lane 5 enforcement

The callable gate:

```text
hhs_backend/runtime/hhs_pass220_genesis_zero_sum_lane5_gate_v1.py
```

evaluates I004 closure before invoking the I003 holographic/Lane 5 composition bridge.

If closure is proven, it returns immediately:

```text
lane5_invoked = false
candidate_count_ranked = 0
candidate_expansion_blocked = true
```

This prevents CPU/GPU/vector ranking from spending work on branches after the Genesis nucleus has already reached its global zero-sum fixed point.

If any closure condition remains unresolved, the gate delegates to the inherited I003 bridge and the existing candidate-only authority membrane remains unchanged.

## 8. Fail-closed witness shape

Exactly nine ordered local nucleus witnesses are required.

Rejected inputs include:

- fewer or more than nine witnesses;
- duplicate nucleus indices;
- nucleus index outside `0..8`;
- bool-as-int substitution;
- non-boolean equation witnesses;
- normalized offsets outside `0..8`;
- normalized vectors not exactly 81 cells.

No missing witness is interpreted as closure.

## 9. Authority

I004 is a scheduler/constructor-expansion gate only.

It does not gain:

```text
canonical_vm81_mutation_authority
canonical_hash72_authority
canonical_hash216_authority
```

All remain false.

The typed equation witnesses must originate from their existing authoritative exact evaluators.  I004 only composes those proof results with the I001 normalized state and the exact raw 5184-bit no-change witness.

## 10. Scaling consequence

The hardware calibration determines how much raw work can fit below the x86_64 serialization boundary.

I004 determines whether there is any mathematically valid new branch to compute.

Therefore orthogonal Genesis scaling is governed by both:

```text
hardware capacity available
AND
NOT GENESIS_GLOBAL_ZERO_SUM_CLOSURE
```

Additional CPU capacity cannot create a new canonical state after the closure predicate is true.

## 11. Implemented surfaces

- `hhs_runtime/hhs_pass220_genesis_zero_sum_halt_v1.py`
- `hhs_backend/runtime/hhs_pass220_genesis_zero_sum_lane5_gate_v1.py`
- `tests/pass220/test_hhs_pass220_genesis_zero_sum_halt_v1.py`

The tests cover:

- complete nine-nucleus closure;
- exact Lo Shu 1/7 local-to-global indices;
- one open `1/9` witness;
- nonzero local normalization;
- new normalized state change;
- open global modality closure;
- raw 5184-bit state change;
- malformed/duplicate/non-boolean witnesses;
- proof that Lane 5 is not invoked after closure;
- proof that unresolved closure still delegates to Lane 5.

## 12. Completion boundary

Implementation is repository-visible.  Dependency-scoped CI must still execute against the branch head before the I004 validation claim is sealed.
