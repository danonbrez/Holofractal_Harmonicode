# Pass 200A Restart Record

## Repository state

- Repository: `danonbrez/Holofractal_Harmonicode`
- Branch: `agent/pass200a-proof-carrying-shadow-optimization`
- Merge target: `main`
- Base commit: `649be68e1566002ce66c919463a386b8018bc2fb`
- Contract: `HHS-P200A-HOLDOUT-BUNDLE-SHADOW-VM81-H72-H216`
- Classification target: `HHS_PASS_200A_PROOF_CARRYING_COMPILER_SHADOW_FOUNDATION_VERIFIED`

## Implemented

- four distinct production holdout definitions;
- Pass 199 durable holdout execution;
- exact tree/config/report/state-root independence checks;
- six negative-mutation checks per envelope;
- Pass 198 one-stage promotion through `COMPILER_CANDIDATE`;
- four immutable proof-carrying optimization bundles;
- exact HIR/VMIR shadow-plan generation;
- reference-authoritative shadow execution;
- persistent envelopes, bundles, shadow runs, and Hash72 events;
- bundle tamper rejection;
- restart-safe status and verification;
- governed API and tool surfaces;
- dependency-scoped tests and contract.

## Authority boundary

- Candidate execution is not authority.
- The compiler mode is `SHADOW` only.
- The returned result is always the reference path.
- Canary, active, runtime-admitted, and frozen-constraint modes are disabled.
- Automatic compiler and runtime promotion remain disabled.
- No DigitalOcean or Vercel mutation has been performed.
- No physical hardware evidence is claimed.

## Validation state

Validation is not yet claimed. The dedicated workflow must execute:

- Python compilation;
- eight lifecycle tests;
- four independent production holdouts;
- 290 states and 580 durable branch jobs;
- 263 admitted states and 27 domain rejections;
- 1,363,392 exact address comparisons;
- 24 negative-mutation checks;
- four compiler-candidate bundles;
- four shadow matches with reference return;
- restart persistence;
- no-float scan;
- API and visual source validation.

## Environment

- Pass 200A state: `.hhs/pass200a` or `HHS_PASS200A_STATE_ROOT`.
- Pass 200A database: `proof_carrying_optimization.sqlite3`.
- Inherited Pass 199 state is nested beneath the Pass 200A state root.

## Next action

Add the workflow and visual projection, open a draft PR, run the exact tree, repair only observed dependency-scoped failures, bind the generated evidence, merge, and verify main.
