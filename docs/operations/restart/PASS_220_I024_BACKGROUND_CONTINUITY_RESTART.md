# Pass 220 I024 Restart Checkpoint — T_COSMO-06 Exact Background Continuity

Date: 2026-09-21

## Repository state

- repository: danonbrez/Holofractal_Harmonicode
- verified base main: 13fb2ac0be1b20b2a7898c4ed9a328135bb71bbb
- predecessor: merged PR #540 / Pass 220 I023
- working branch: pass220/i024-background-continuity-v1
- merge target: main
- theorem: T_COSMO-06

## Predecessor closure

PR #540 initially failed only at a lexical authority grep that matched formula
strings such as exp(...), not executable numerical calls.

Repair:

- replaced grep authority detection with an AST scan;
- retained exact math.isqrt as the only allowed math import;
- reran dedicated I023 exact-head workflow.

Result:

~~~text
Pass 220 I023 Exact Friedmann Transfer
run 35661909840
conclusion = success
~~~

PR #540 was merged to main at:

~~~text
13fb2ac0be1b20b2a7898c4ed9a328135bb71bbb
~~~

I024 starts exactly from that verified main head.

## I024 closure

I024 removes the arbitrary background-Hubble sequence.

Finite reference state:

~~~text
rho_b,ref
rho_r,ref
rho_D,ref
gamma_G
curvature_sign
anchor_receipt_sha256
~~~

where gamma_G is one exact SHA-bound egress constant representing 8*pi*G/3.

Each committed transition provides:

~~~text
lambda_n
theta_n
phase/Hash receipt SHA
J_D,n
~~~

where J_D,n is an exact nonnegative dark-density source bound to that committed
receipt.

## Exact recurrence

~~~text
B_n =
gamma_G (rho_b,n + rho_D,n + rho_r,n) + K_n

H_n^2 =
B_n + (lambda_n/(tau theta_n))^2

Deltaell_n =
H_n tau theta_n

rho_b,n+1 =
rho_b,n ExpSym(-3 Deltaell_n)

rho_r,n+1 =
rho_r,n ExpSym(-4 Deltaell_n)

rho_D,n+1 =
rho_D,n ExpSym(-3 Deltaell_n) + J_D,n

K_n+1 =
K_n ExpSym(-2 Deltaell_n)
~~~

The J_D=0 branch is exactly the conserved pressureless a^-3 dark branch.

## I023 extension

I024 minimally extends the inherited I023 transfer so background_h2 may be an
ExactExpr.

The rational path remains compatible.

New exact helper surfaces expose deterministic expression construction and
serialization. total_h2 is carried as:

- historical rational string when rational;
- total_h2_exact for all exact values;
- symbolic square-root/exponential nodes when not rationally reducible.

No numerical solver was introduced.

## Receipt chain

Every step binds:

~~~text
previous continuity receipt
+ reference anchor receipt
+ committed phase/Hash receipt
+ current exact density state
-> background input receipt
-> I023 transfer receipt
-> Deltaell_n
-> next density state
-> continuity receipt
~~~

The next step binds the prior continuity SHA.

## Wolfram formalization

Authoritative I024 result:

~~~text
schema = HHS_PASS_220_I024_COSMO_BACKGROUND_CONTINUITY_WOLFRAM_20260921_V2
status = PASS
checks = 10/10
failed = []
~~~

Verified:

- baryon a^-3 continuity;
- radiation a^-4 continuity;
- dark sourced recurrence;
- J_D=0 dark a^-3 invariant;
- curvature a^-2 scaling;
- explicit Friedmann background;
- absence of free Function/InterpolatingFunction background law.

The earlier v1 receipt is retained only as pre-source-term development evidence.

## Files changed

- hhs_runtime/hhs_pass220_exact_friedmann_transfer_v1.py
- hhs_runtime/hhs_pass220_background_continuity_v1.py
- tests/pass220/test_hhs_pass220_background_continuity_v1.py
- docs/pass220/PASS_220_I024_BACKGROUND_CONTINUITY.md
- evidence/pass220/i024_background_continuity_wolfram_20260921_v1.wl
- evidence/pass220/i024_background_continuity_wolfram_20260921_v1.output.json
- evidence/pass220/i024_background_continuity_wolfram_20260921_v2.wl
- evidence/pass220/i024_background_continuity_wolfram_20260921_v2.output.json
- .github/workflows/pass220-i024-background-continuity.yml
- this restart record

## Authority boundaries

No new:

- VM81 mutation authority;
- Delta admission authority;
- Hash72 mint authority;
- Hash216 persistence authority;
- G72 scalar resolution;
- host wall-clock authority;
- floating-point authority;
- numerical sqrt/exp authority;
- B(z) fit function;
- rho(z) fit function;
- inverse H(z)->state authority.

## Validation performed

- I023 predecessor exact-head: SUCCESS;
- I023 merged and verified on main;
- Wolfram I024 v2: 10/10 PASS;
- exact source/replay design audit;
- dark exhaust source corrected from implicit conserved CDM to explicit J_D,n;
- branch restart state is repository-visible.

## Validation remaining

Dedicated I024 exact-head must:

1. AST-audit I023/I024 authority surfaces;
2. py_compile I022-I024;
3. verify Wolfram v2 receipt;
4. run I024 regressions;
5. rerun inherited I023 regressions;
6. rerun inherited I022 regressions.

Queued/slow CI does not invalidate this checkpoint.

## Reference-epoch limitation

The density anchors belong to the selected forward reference epoch. They are not
silently reinterpreted as present-day anchors for a past-directed trajectory.

If a later comparison requires present-day anchors to generate earlier epochs,
that requires a separately proven reverse/boundary transfer.

## Next action

If exact-head is green, merge I024 and verify main.

Then T_COSMO-07 can seal one observational reference receipt and perform
numerical egress only for residual comparison against external BAO/SN/CMB data,
without refitting the native trajectory.
