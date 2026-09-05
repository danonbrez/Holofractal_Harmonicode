# Pass 219 Iteration 145 — inherited Pass 181 graphics hydration reconciliation

## Scope

I145 restores cumulative exposure for the validated Pass 181 graphics-hydration nucleus while preserving the contract's still-unclosed terminal acceptance requirements.

- Contract: `HHS-P181-NCSR-GHIR-VM81-H72-H216`
- Historical repaired green head: `3ae56827b27500c2c8187126d5825a901d4feb40`
- Historical Pass 181 green workflow run: `30660886113`
- Frozen predecessor I144 checkpoint: `132694cee0af4a43113ddc4c50f867c084a22bae`
- Branch: `agent/pass219-iteration145-pass181-graphics-hydration-reconciliation`
- Merge target: `main`
- Current-main observed during I145 construction: `75396e1bbf2fe95920311a5f8005b6ac1cde4cce`
- Merge base with current main: `e8ecb02cc2fc823d0ffb49fa2e6d765a2cc73191`
- Pre-final-validation comparison: branch lineage `223` commits ahead / `284` behind current main

## Historical nucleus preserved

The cumulative Pass 181 binding preserves the merged runtime surfaces for:

1. immutable read-only MP4 evidence identity;
2. deterministic canonical MP4 frame/audio timeline identity;
3. native reconstruction recipe and typed residual logic;
4. bounded serialized optimization;
5. Pass-165-backed vector hydration and invariant candidates;
6. append-only constraint/style freeze, supersession, rollback, and frontier replay.

The historical nucleus remains reachable as implementation evidence. I145 does not rewrite it into a different graphics authority.

## I145 singleton-authority repair

Repository reconciliation found that the Phase-6 registry's freeze and rollback operations labeled their operator as VM81-authorized but did not themselves invoke the inherited VM81 admission/commit path. A legacy direct `GraphicsHydrationRuntime.promote_constraint()` path could also write a frozen constraint independently of the governed registry.

I145 repairs both gaps:

- `GraphicsConstraintRegistry` accepts an inherited `VMRCRuntime` authority instead of constructing a peer;
- the production registry is wired to `GRAPHICS_VECTOR_HYDRATION.vm81_authority`, which is the already-bound Pass 165/163 runtime;
- freeze and rollback execute a deterministic `VMRC_COMMIT` under capability `P181_GRAPHICS_CONSTRAINT_PROMOTION` before registry mutation;
- VM81 validation remains non-mutating until commit;
- the VM81 commit receipt and operation identity are recorded with the registry transition;
- a registry without VM81 authority fails closed;
- the legacy direct promotion method is disabled and the governed registry route remains the only freeze projection.

This preserves one VM81 mutation authority and does not grant Hash72, Hash216, vector observations, Three.js, or the registry an independent mutation clock.

## Cumulative exact ABI

I145 adds:

- `hhs_runtime/include/hhs_pass219_inherited_pass181_1_45.h`;
- `hhs_runtime/include/hhs_pass219_inherited_pass181_1_45.hpp`;
- `hhs_runtime/c/hhs_pass219_inherited_pass181_1_45.inc`;
- `hhs_exact_pass219_bind_pass181_graphics_hydration`.

The aggregate inherited tail becomes:

`185 -> 184 -> 183 -> 182 -> 181`.

The mandatory global-default census becomes:

- ceiling: `218`;
- floor: `181`;
- binding count: `40`;
- Pass 200a, Pass 200b, and Pass 200c remain distinct bindings.

## Nonterminal Pass 181 state

Cumulative exposure is not equivalent to terminal Pass 181 completion.

The binding requires:

- `terminal_completion_claimed == 0`;
- `repair_forward_required == 1`;
- exactly three unresolved terminal obligations.

Those obligations are:

1. `DETERMINISTIC_COLD_START_NATIVE_RECONSTRUCTION_REPLAY`;
2. `THREEJS_EDITOR_PREVIEW_ENHANCEMENT_NO_FINAL_FRAME_AUTHORITY`;
3. `FULL_90_SECOND_INVERSE_RENDER_AND_ONE_CLICK_EVIDENCE_EXPORT`.

The already-implemented constraint-frontier cold restart replay does not substitute for full native reconstruction replay.

## Validation and restart evidence

The dedicated validation surface is:

`.github/workflows/pass219-i145-pass181-graphics-hydration.yml`.

The authoritative branch-local executed result is stored in:

`evidence/pass181/i145/PASS_219_I145_PASS181_VALIDATION_RECEIPT_INDEX.json`.

If that receipt index is absent, the I145 executed-validation state is pending. If present, its exact head, workflow run, test counts, receipts, and artifact digest govern the branch-local validation claim.

No merge, authoritative-main verification, deployment, or terminal Pass 181 completion is implied by a branch-local green receipt.
