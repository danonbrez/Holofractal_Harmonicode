# Pass 220 — Self-verifying 5184 knowledge-graph proof boundary

The combined Lane 5 metadata/linear BigInt serialization graph must carry its own re-derivable **candidate constraint enforcement and closure proof**, rather than unverified flags.

- Input: exactly 5184 ordered positions, each with canonical signed decimal BigInt text, VM81 81×64 and Hash72 72×72 coordinates, explicit zero canonical-authority flags.
- Ordered gate ledger: indexed constraints, closed state, HNAN bypass carrying gain exactly 1 with no phase write. No arbitrary gate permutation.
- Inherited roots: existing pipeline and constructor graph 72-character identities, retained verbatim, **never minted by this adapter**.
- Re-derived proof: canonical candidate payload SHA256 replays under the same inputs, detecting changes to any position, operand text, gate order, or root. This SHA256 is a *candidate evidence digest*, **not native Hash72/Hash216**.
- Native signed acceptance remains the existing `hhs_exact_pass219_hash216_fractal_qudit_witness_validate` and `hhs_exact_pass219_vm81_environment_admit_signed` gate sequence with signed/parent-child transition provenance. This preliminary Python verifier does not implement their entire proof.
- The ethical gate must eventually consume the signed native receipt *together with* the 5184 proof. A positive Python candidate proof alone is never ethical or VM81 execution authorization.

Source: `hhs_runtime/hhs_pass220_lane5_5184_constraint_proof_v1.py`; test: `tests/pass220/test_hhs_pass220_lane5_5184_constraint_proof_v1.py`.
Unfinished: replace the candidate payload projection with the complete native typed 5184 metadata and signed zero-bypass/transition proofs; bind into I028 and ethical admission; verify current CI.
