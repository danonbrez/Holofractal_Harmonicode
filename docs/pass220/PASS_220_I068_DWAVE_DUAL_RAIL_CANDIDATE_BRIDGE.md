# Pass 220 I068 — D-Wave Dual-Rail Error-Aware Candidate Bridge

Date: 2026-10-03

## Objective

I068 adds a bounded external-simulator ingress surface for D-Wave's gate-model
dual-rail simulator beta. The simulator remains a **candidate evidence source**.
It does not replace VM81 execution authority and it does not gain canonical
Hash72, Hash216, persistence, or external-egress authority.

The bridge is deliberately exact at the HHS boundary. Simulator metadata used
for identity is restricted to exact integers, strings, booleans, ordered
collections, and exact HHS receipt glyphs. Floating-point timing or probability
metadata is not admitted into the candidate identity.

## Upstream simulator surface

The implementation targets the documented D-Wave Ocean/QCDL beta surface:

- `dwave.gate.leap.LeapQCDLSimulator`
- documented simulator identifiers `DRsim_17qubits` and `DRsim_21qubits`
- logical measurement values `0`, `1`, and detected-erasure `*`
- non-destructive mid-circuit erasure detection through `mced()`
- raw result collection with `get_counts(post_select=False)`

Reference documentation:

- https://docs.dwavequantum.com/en/latest/ocean/api_ref_gate/workflow.html
- https://docs.dwavequantum.com/en/latest/ocean/api_ref_gate/simulator.html
- https://www.dwavequantum.com/company/newsroom/press-release/d-wave-launches-gate-model-simulator-beta-program-advancing-error-aware-programming-capabilities/

I068 rejects post-selected-only input. A caller may not discard the erasure
channel before the HHS witness is constructed.

## Exact ordered 3×3 bridge to I027

Let each measured dual-rail symbol carry the exact code

```text
0 -> 0
1 -> 1
* -> 2
```

For an ordered control/target pair the I068 address is

```text
i027_outcome = 3 * control_code + target_code
```

The nine ordered pairs map bijectively onto `0..8`, the same outcome domain
used by the existing I027 quantum-collapse admission bridge. Because control and
target are not commuted, reversing any unequal pair changes its address.

This is an HHS transcription rule. It does not assert that D-Wave defines its
hardware state using this Lo Shu/I027 address geometry.

## Erasure-preserving evidence

Every measurement round retains:

- explicit measurement-register ordering;
- exact per-output counts;
- exact total, clean, and erasure-bearing shot counts;
- per-register erasure counts;
- exact reduced clean-yield numerator/denominator;
- the complete nine-bin I027 outcome histogram;
- optional typed MCED events.

A noisy transcript containing `*` is valid. An ideal
`noise_model=False` transcript containing `*` fails closed.

## Receipt

The candidate receipt is three ordered 72-glyph lanes:

```text
Hash216_candidate =
    Hash72(configuration)
 || Hash72(result + erasure evidence)
 || Hash72(authority boundary)
```

The 216-glyph object is candidate evidence only. It is not a canonical Hash216
commit and cannot advance canonical state.

## Canonical authority boundary

The runtime publishes the following fixed authority classification:

```text
candidate_only                         = true
external_simulator_source              = true
erasure_channel_preserved              = true
post_selection_for_provenance_forbidden = true
exact_integer_transcription            = true

floating_point_authority               = false
canonical_vm81_mutation_authority      = false
canonical_hash72_commit_authority      = false
canonical_hash216_commit_authority     = false
canonical_persistence_authority        = false
external_egress_authority              = false
```

The optional VM81 comparison function requires a caller-supplied canonical
216-glyph receipt and a canonical nine-bin VM81 outcome histogram. It computes
an exact delta witness only. Equality does not grant mutation or receipt-minting
authority.

## Live beta runner

The core transcription surface has no D-Wave dependency. Live execution is
loaded lazily by `run_leap_qcdl_candidate()`, which imports the Ocean SDK only
when invoked. No API token, Leap profile, credential, or remote result is stored
in the repository.

`build_ordered_cz_probe()` constructs a two-qubit QCDL probe using explicit
`control_qubit` and `target_qubit` arguments. This keeps the external gate
ordering visible at the HHS boundary.

## Validation

Dependency-scoped validation completed before repository checkpoint:

```text
python -m pytest -q tests/pass220/test_hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1.py
12 passed

python -m hhs_runtime.hhs_pass220_i068_dwave_dual_rail_candidate_bridge_v1
8 / 8 PASS

connected Wolfram Language kernel
HHS_PASS_220_I068_DWAVE_DUAL_RAIL_WOLFRAM_V1
7 / 7 PASS
failed = {}
```

The Wolfram proof establishes the exact nine-state bijection, ordered reversal
separation for unequal pairs, and the synthetic transcript identity

```text
5 shots = 3 clean + 2 erasure-bearing
clean yield = 3/5
```

without floating-point arithmetic.

## Non-goals

I068 does not claim that:

- the D-Wave simulator is a canonical VM81 execution backend;
- simulator output can directly mutate canonical state;
- a candidate receipt is a canonical Hash72/Hash216 receipt;
- simulator noise is identical to forthcoming physical gate-model hardware;
- post-selection may erase provenance before HHS transcription.
