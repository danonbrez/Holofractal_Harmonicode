# Resume From Here

1. Load `HHS_CANONICAL_CONTINUATION_STATE.json`.
2. Load `HHS_CANONICAL_RESUME_CHECKPOINT.json`.
3. Verify `pass070_root_hash72` against the current Pass 070 Runtime root.
4. Call `resume_from_checkpoint(...)` from `hhs_restart_safe_phase_gear_folding_v1.py`.
5. Require `completed_stage_roots_match=true`, `context_reset_occurred=false`, and the stored final derivation root before continuing to Pass 072.

No conversational/thread memory is required for this recovery path.
