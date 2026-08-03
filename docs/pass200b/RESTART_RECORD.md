# Pass 200B Restart Record

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass200b-canary`
- Pull request: `#139`
- Merge target: `main`
- Base commit: `483a18b618dbe51b31025eeb15a8a6435e4040c5`
- Contract: `HHS-P200B-DUAL-APPROVAL-CANARY-ROLLBACK-VM81-H72`
- Classification: `HHS_PASS_200B_GOVERNED_CANARY_ADMISSION_VERIFIED`

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
- dependency-scoped tests, workflow, contract, and evidence.

## Verified workflow

Workflow: `Pass 200B Governed Canary Admission`

Successful integrated run: `30775726043`

Validated executable head: `f13eed02531e77737562b23fb207962c0744ed0d`

Artifact:

- ID: `8841987422`
- Digest: `sha256:b95a8091ba8ce19301ee4b3a1ab51a994503940fe6293c752d24e63f22eb1cd8`

Successful stages:

- Python compilation across runtime, production projection, API, visual server, and tests;
- eight canary lifecycle tests;
- four independent Pass 200A holdout envelopes;
- four Pass 200A compiler-candidate bundles;
- four Pass 200A exact shadow matches;
- first canary admission with dual approvals and one singleton activation receipt;
- eight bounded invocations at ratio `1/4`;
- candidate returns only at ordinals `0` and `4`;
- automatic `EXHAUSTED` reference restoration;
- second canary admission with fresh frontier-bound approvals;
- controlled exact mismatch returning reference;
- automatic `ROLLED_BACK` reference restoration;
- nine total metered invocations;
- two candidate returns and seven reference returns;
- five immutable frontiers;
- fourteen Hash72 events;
- restart reproduction of frontier, counters, returns, and event-chain tip;
- no floating-point canonical operations;
- API and visual source wiring;
- Node syntax validation.

## Canonical identities

- First canary frontier Hash72: `XqCJ1Jb-8M+U61R-j*CuG4k0(El9)798Ifv3M4CD)3LxZywca9DZblkgYxFAXK1bh3KFTSxG`
- Second canary frontier Hash72: `QzWae*WmxCAFNWi+pRH7fZV4m+nU>I7nm2TqTV*ylZqGyB<GYyG5A5Jds<hxq1yMT?iGcH-?`
- Restored current frontier Hash72: `xb0HzUzWcd<R!fnvvLLFWRLrO1mMsLJlaFrM3T!ZiCGSYV7x/vx)+lC6ie-1HscINA?T3v?9`
- Status Hash72: `Qi*2wV+yaNRLMO3M2kKlGPi*)S48tpy83m1O)-DTthuGZ/CTzRID!6v(Dz0?1OosagvUr!NS`
- Event-chain tip Hash72: `gTECBrf>qqsWpntqLpq?lIpTBbo*eYdw>!8E4Ac!w-mxM7AvVK-QAT(5LHpp1DLtj/uh/g(*`

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

## Validation remaining

- receipt-updated workflow on the final documentation/evidence head;
- inspection and removal of unrelated workflow-generated commits;
- ready-for-review transition and merge;
- merged-main verification.

## Next action

Run the receipt-updated workflow, preserve the exact Pass 200B scope, merge PR #139, and verify `main`.
