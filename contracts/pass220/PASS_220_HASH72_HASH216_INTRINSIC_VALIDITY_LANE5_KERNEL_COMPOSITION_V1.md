# Pass 220 — Intrinsic Hash72/Hash216 states and native Lane 5 composition validation

2026-10-09. Inherited global HHS/HARMONICODE policy; preserve established native algebra and VM81/Hash72/Hash216 authority.

## Type/state validity

Every **well-typed native Hash72 or Hash216 state** is a valid state by its canonical type definition. No external `validated` flag, per-object JSON property, extra generic proof, source age, unfamiliar composition, or duplicate state reference can independently invalidate it. Hash72 is 72 glyphs; Hash216 is the ordered triple of 72-glyph lanes (216 glyphs). Malformed input serialization is not an instance of that type and can fail input type checking; this is distinct from judging a well-typed state invalid.

The same native Hash216 state may occur more than once among ranking candidates under different IDs without losing its validity. Candidate IDs remain required to be distinct for deterministic ranking attribution.

## Composition validation

A composition of valid Hash states is an **operation and transition**, not a question of the validity of its operands. Composition constraints and routing decisions belong to existing Lane 5 native C Runtime / Pass205 CPU VM81 / Pass207 GPU-candidate verification, with inherited phase, ordering, denominator and replay constraints. An optimizer output JSON flag is only an observation; it cannot by itself certify a native composition, authorize persistence, mint canonical Hash72/Hash216, or bypass signed VM81 cell-wall admission.

`ValidHash72(h)=true` and `ValidHash216(H)=true` for native typed states; `AcceptComposition(C)` is decided by successful native kernel constraint enforcement, not by `C.validated`.

The scoped repair removes the `candidate.validated` Boolean veto from existing Lane 5 hash216 GPU phase interlace search and removes the duplicate-hash veto. It preserves the actual native `self.phase.prime_route` C ABI and `self.gpu.rank_hash72_vectors` execution path, and candidate-only/CPU replay requirement. The holographic bridge no longer injects `validated=True` as a fabricated validation authority. Legacy `Hash216CompositionCandidate.validated` remains accepted in constructor input for API compatibility but is inert metadata.

**Security and limits:** Well-typed Hash state validity does not mean every proposed composition is executable or signed. The native Lane5 routing kernel and VM81 signed transition still enforce ordered constraints, resource bounds, environmental rights, replay and lineage. A native pure ranking route is not a canonical mutation receipt. In the existing Lane5 streaming ABI 1.48, some route booleans are still caller-authored and the kernel checks their value; these alone are not independent cryptographic proof of workload serialization or composition correctness. They must not be promoted as canonical state authority. This is an inherited implementation hardening target, not grounds to reject a valid Hash state.

## Changes and tests

- `hhs_backend/runtime/hhs_pass219_lane5_hash216_gpu_phase_interlace_1_37.py`
- `hhs_backend/runtime/hhs_pass220_holographic_hash216_lane5_bridge_v1.py`
- `tests/pass219/test_pass219_lane5_hash216_gpu_phase_interlace_1_37.py`
- `tests/pass220/test_pass220_lane5_hash216_kernel_composition_policy_v1.py`
- `.github/workflows/pass220-lane5-intrinsic-hash-states-native-composition.yml`

Tests cover malformed serialization rejection, positive legacy flag=False admission, duplicate Hash216 references, positive real native routing/rank, native phase-router negative failure despite JSON validated=True, and no unauthorized state promotion. Only changed dependency scopes rerun.
