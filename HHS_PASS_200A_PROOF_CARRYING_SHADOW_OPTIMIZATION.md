# HHS PASS 200A — PROOF-CARRYING OPTIMIZATION BUNDLES AND COMPILER SHADOW AUTHORITY

Contract identifier: `HHS-P200A-HOLDOUT-BUNDLE-SHADOW-VM81-H72-H216`

Classification target: `HHS_PASS_200A_PROOF_CARRYING_COMPILER_SHADOW_FOUNDATION_VERIFIED`

## 1. Purpose

Pass 200A converts the proof labels created by Pass 198 and the durable exact calibration evidence created by Pass 199 into operational but non-authoritative compiler optimization bundles.

It implements:

- independent holdout calibration envelopes;
- evidence-independence validation;
- registered negative-mutation execution;
- immutable optimization bundles;
- `CROSS_WORKLOAD_VERIFIED` and `COMPILER_CANDIDATE` proof promotion;
- exact HIR and VMIR compiler shadow plans;
- reference-versus-candidate shadow execution;
- persistent shadow receipts;
- fail-closed bundle and event-chain verification.

Pass 200A does not activate an optimization in the compiler or runtime. The reference path remains authoritative and is always returned.

## 2. Inherited authority

Pass 200A inherits:

- Pass 198 operation specifications, proof records, staged promotion, and revocation;
- Pass 199 durable A/B execution, immutable candidate computation, complete VM5184 witnesses, deterministic replay, and singleton tree commit;
- Pass 190 persistent VM81 mutation authority and Hash72 receipt chain.

The Pass 200A SQLite database, API, compiler shadow plan, candidate lane, frontend, and tool server are not independent canonical authorities.

## 3. Independent holdout envelopes

The production holdout set contains four parameter trees that do not reuse the original Pass 197 grid:

1. larger integers and additional exact fractions;
2. asymmetric sign and axis cardinality;
3. explicit zero reciprocal-domain boundaries;
4. extended lexical `xy` exponents.

An envelope counts as independent only when all of the following identities are distinct:

- parameter-tree Hash72;
- configuration Hash72;
- production report Hash72;
- exact state-root Hash72;
- Pass 198 production run identity.

A different VM81 receipt over the same tree does not count as a distinct envelope.

The default holdouts contain:

- 290 parameter states;
- 580 durable A/B branch jobs;
- 263 admitted states;
- 27 explicit reciprocal-zero rejections;
- 1,363,392 exact VM5184 address comparisons.

Every admitted state must close with zero mismatch and zero singularity.

## 4. Negative mutations

Every holdout records and passes these fail-closed checks:

- production-report summary tampering changes report identity;
- replacing lexical `xy` with numeric `x*y` changes state identity;
- complete deterministic replay is required;
- exactly one singleton tree commit is required;
- retained cell/lane witness coverage is required;
- candidate workers remain non-authoritative.

A failed negative mutation prevents envelope admission and bundle creation.

## 5. Proof promotion

Pass 200A may advance a Pass 198 simplification only through the existing one-stage membrane:

```text
ENVELOPE_VERIFIED
→ CROSS_WORKLOAD_VERIFIED
→ COMPILER_CANDIDATE
```

Promotion requires an explicit VM81-authorized Hash72 receipt and the four distinct production run identities.

Pass 200A does not advance a proof to:

- `RUNTIME_ADMITTED`;
- `FROZEN_CONSTRAINT`.

Automatic promotion remains disabled. `run_holdouts` is an explicit governed mutation request.

## 6. Immutable optimization bundles

One immutable bundle is created for each of the four admitted simplifications:

- original numerator to compact numerator;
- reciprocal denominator factorization;
- VM81 lane-preserving broadcast;
- exact matrix-power caching by lexical `xy`.

Every bundle binds:

- simplification and operation identities;
- current Pass 198 proof Hash72;
- exact rewrite rule;
- four independent production run identities;
- envelope, tree, report, and state-root Hash72 sets;
- retained witnesses;
- exact before/after/saved cost;
- negative-mutation count;
- rollback target;
- compiler mode;
- activation boundaries;
- bundle Hash72.

Bundles are append-only and cannot be edited in place. Identity mismatch or payload tampering fails closed.

## 7. Compiler shadow plan

A compiler-candidate bundle can produce a shadow plan with exact HIR and VMIR records.

The VMIR defines two lanes:

```text
reference_lane = AUTHORITATIVE_RETURN
candidate_lane = NONAUTHORITATIVE_COMPARE_ONLY
```

The shadow plan requires comparison of:

- exact semantic result;
- state-root Hash72;
- replay-root Hash72;
- VM81 lane identity;
- retained witnesses.

The candidate lane may not commit or activate. Its rollback target is always the reference path.

## 8. Shadow execution

The first shadow suite executes an additional exact parameter tree through Pass 199 and records one shadow result per bundle.

Each result must state:

- exact match;
- witness match;
- replay match;
- returned path `REFERENCE`;
- candidate activation `false`;
- candidate worker authority `false`.

Any mismatch prevents Pass 200A closure and is grounds for Pass 198 revocation review.

## 9. Persistence and restart

Pass 200A uses SQLite with:

- WAL journaling;
- full synchronous commits;
- foreign-key enforcement;
- append-only Hash72 events;
- immutable envelope records;
- immutable bundle records;
- persistent shadow-run records.

Cold restart must reproduce the envelope count, bundle identities, shadow results, and event-chain tip without rerunning completed work.

## 10. API and visual surfaces

API prefix:

`/api/runtime/optimization-authority`

Routes:

- `GET /status`
- `POST /holdouts/run`
- `GET /envelopes`
- `GET /bundles`
- `POST /compiler/shadow/compile`
- `POST /compiler/shadow/run`
- `GET /compiler/shadow/runs`
- `GET /verify`
- tool registry and invocation routes.

The visual IDE projects:

- holdout closure;
- bundle count;
- compiler-candidate count;
- shadow-match count;
- reference-return count;
- candidate-activation count;
- event-chain status;
- proof and bundle identities.

The visual panel does not expose canary, active, or frozen-constraint controls.

## 11. Acceptance criteria

Pass 200A closes only when:

- four independent holdout envelopes close;
- 290 parameter states execute as 580 durable jobs;
- 263 states are admitted and 27 remain explicit domain rejections;
- 1,363,392 exact address comparisons complete;
- all holdouts have zero mismatch and zero admitted singularity;
- 24 negative-mutation checks pass;
- exactly four simplifications reach `COMPILER_CANDIDATE`;
- exactly four immutable bundles are created;
- all four compiler shadow plans use reference-return mode;
- all four shadow executions match exactly;
- candidate activation count remains zero;
- restart persistence and event-chain verification pass;
- tampered bundle payloads fail closed;
- floating-point canonical operations remain absent;
- Python, JavaScript, API, and visual wiring validate.

## 12. Claim boundary

Pass 200A does not claim runtime admission, canary execution, active optimized return, frozen constraints, automatic compiler mutation, automatic runtime mutation, arbitrary-expression optimization, multi-host consensus, live DigitalOcean acceptance, or physical hardware evidence.

The next bounded layer is Pass 200B: explicit canary admission, bounded invocation counters, immediate fail-closed rollback, immutable active-frontier history, and singleton activation receipts after additional exact evidence.
