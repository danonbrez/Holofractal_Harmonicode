# Pass 200B Restart Record

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass200b-canary`
- Pull request: `#139`
- Merge target: `main`
- Base commit: `483a18b618dbe51b31025eeb15a8a6435e4040c5`
- Contract: `HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72`
- Classification target: `HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_VERIFIED`

## Implemented

- immutable reference, canary, rollback, and exhausted frontier records;
- separate bounded invocation counters;
- dual approval validation with distinct principals, capabilities, and receipts;
- approval binding to bundle Hash72, expected frontier Hash72, and expiry;
- singleton VM81 canary activation receipt;
- deterministic integer canary selection;
- exact result, witness, and replay comparison;
- candidate return only after exact match and selection;
- automatic mismatch and expiry rollback;
- explicit rollback;
- invocation-limit exhaustion with reference restoration;
- persistent invocation and Hash72 event records;
- restart recovery and tamper detection;
- governed API and tool routes;
- visual canary controls that cannot generate authority evidence;
- dependency-scoped tests and workflow.

## Authority boundary

- Candidate execution cannot approve or admit itself.
- The API and visual panel are projections, not authority.
- Candidate return is limited to the admitted canary ratio and invocation budget.
- Any exact-result, witness, replay, expiry, or frontier mismatch restores the reference frontier.
- Unrestricted active and frozen-constraint promotion remain disabled.

## Environment

- Pass 200B state root: `.hhs/pass200b` or `HHS_PASS200B_STATE_ROOT`.
- Database: `governed_canary_admission.sqlite3`.
- Pass 200A proof state remains an inherited dependency.

## Validation state

The initial eight unit tests passed on workflow run `30775533595` before API and visual integration. Final production validation remains required for the integrated head.

## Next action

Run the final workflow against a real Pass 200A proof bundle, verify bounded exhaustion and mismatch rollback, bind the generated evidence, remove unrelated workflow-generated commits, merge PR #139, and verify `main`.
