# Pass 220 reconciled V7 pure receipt API test repair — 2026-10-09

Repository: `danonbrez/Holofractal_Harmonicode`
Branch: `agent/pass220-ordered-tensor-quotient-20261009`, PR #754 draft
Base / first-parent checkpoint: `3c7ca1eff304c8c049d979b1758cf0c3c6a27509`
Merge target: main. No main merge, deployment or production state change.

## Concrete diagnostic failure
GitHub Actions completed run `37990042413`, job `114021569816`, at an earlier
PR #754 head, with 1 fail / 10 pass / 1 deselected:
`test_216_native_glyphs_not_hex` failed with
`KeyError: 'pure_replay_hash216'`.
This was not a tensor proof failure and was not caused by queue saturation.

The source at the reconciled head still reproduced the **structural API mismatch**:
`validate_native_pure_output()` intentionally returns
`native_pure_replay_hash216` and
`native_pure_candidate_hash216`, whereas the test asserted
the outdated names `pure_replay_hash216` and `candidate_hash216`.
These remain the same exact 216 original Hash72 alphabet glyphs;
no cryptographic or native runtime semantics changed.

## Bounded repair
Edit only `tests/pass220/test_pass220_v7_native_pure_inherited_execution_v1.py`
to assert both current, real parser-output keys. Preserve the original
negative cases and canonical-mutation false gate.

## Adjacent evidence held
Historical V7 integration failure run `37968200877` asserted
`INVALID_NATIVE_HASH216` but received `MISSING_NATIVE_HASH216_SOURCE`
at an earlier head. Current parser `_fields` no longer strips values,
and the current regression deliberately tests invalid glyphs and
length separately; no speculative edit to that test.
Historical V4 phase-chain failure run `37943151189`
used `SOURCE[259:-1]`; the current test already uses
`SOURCE[262:-1]`; no rerun or edit required.

## Validation and next action
Verified exact source/fixture API keys by reading the live reconciled
GitHub branch and original completed CI failure logs. No local pytest
run or runner execution has been claimed.

Current reconciled-head V7 job `38003978130` was queued at intake;
original signed I091 `38003978026` and native Hash216 I092
`38003978687` were also queued. Continue with exact-head
dependency-scoped CI when runnable; do not regenerate the entire
backlog or modify previously green mathematics.

Changed files: V7 pure API test and this restart note. Tool invocation:
GitHub fetch_workflow_job_logs; fetch_file of parser/test/V4/current glyph
negative; create_tree preserving existing exact base tree; single
source-commit; update_ref with expected head. Remaining validations:
V7 pure test and combined V7 integration, original I089–I092 signed/native
checks. Blocker: GitHub Actions queue. No new canonical Hash72/Hash216
ledger authority or native VM81 mutation.
