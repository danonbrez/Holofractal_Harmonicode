# Pass 219 HHCQ Phase 11 precursor failure and repair-forward record

Date: 2026-09-08

## Precursor identity

- Branch: `agent/pass219-hhcq-8basis-parity-phase11-20260908`
- Exact tested head: `8f547b6e6e1679ee65d09a99d6b7fd75cc35bb2a`
- Workflow: `Pass219 HHCQ 8-Basis Equilibrium Parity Phase11`
- Run: `34179166432`
- Job: `101914525020`
- Result: failure

## Frozen successful gates

The precursor established the following Phase-11 implementation surfaces as green before the failure:

1. Ubuntu 24.04 checkout / dependencies;
2. exact aggregate ABI build (`make c-abi`, `libhhs_runtime.so` present);
3. strict C11 Phase-11 invariants with `-Wall -Wextra -Werror -pedantic`;
4. frozen Phase-3 authenticated artifact download from run `34138427959`;
5. exact Phase-3 frame SHA-256 verification:
   `63d0f8816d4c04e10eb5d9644c9c60015b8cdd3b1235f114b3f1821ef08a3433`.

The only failing step was the authenticated C++17 manifold benchmark, which exited with code `21`. In that benchmark, exit 21 is the deterministic direct manifold evaluation/replay gate.

The evidence-gate step was skipped because the benchmark did not emit its terminal JSON. The always-upload artifact contains the empty benchmark output file and has artifact ID `10038284114`, ZIP SHA-256 `367ab9b3b61918d32fc6183ec90ab1d0037677407ca7746f5167b7a7f8ff1232`.

## Exact diagnosis

A bounded parser over the already checksum-verified frozen Phase-3 frame binary reproduced the same 529 SUMMARY records and nine Lo-Shu local anchors (4,761 local states). It found exactly **2** local states where the native octonion projection has:

`x_phase72 = 0`

`y_phase72 = 0`.

The first occurs at SUMMARY ordinal 232, anchor index 7 / VM81 cell 63.

The Phase-11 manifold currently calls the frozen Phase-10 polynomial expansion for every state. Phase 10 deliberately rejects `(x,y)=(0,0)` because the isolated ordinary polynomial fraction has denominator `(x²+y²)²=0`. Therefore the first authenticated native center state causes the Phase-11 manifold API to return before deterministic replay, yielding benchmark exit 21.

This is not a failure of the Phase-11 exact ABI build, 8-basis equilibrium arithmetic, x² parity identity, matrix ordering, or transport-delta logic; those strict C gates already passed.

## Inherited native closure rule

The repository already freezes the Pass-219 native center rule:

`0/0=u^0 mod(u^72)=1`

with scalar projection runtime authority false. This rule appears in the I148/I149/I150 raw5184/octonion hydration contracts, registrations, restart records, benchmarks, and validation receipts.

Phase 11 therefore must evaluate `(x,y)=(0,0)` under the complete VM81 constraint intersection rather than forcing the isolated Phase-10 ordinary-fraction rejection to become authoritative over the full manifold.

## Repair-forward contract

Do **not** modify frozen Phase-10 semantics.

Repair only the additive Phase-11 wrapper:

1. detect exact native `x==0 && y==0` before calling Phase-10 expansion;
2. record an explicit `native_zero_over_zero_u0_closure=1` witness;
3. record `phase10_expansion_executed=0` for that state so no zeroed Phase-10 expansion struct can be mistaken for executed evidence;
4. retain the symbolic exponent/root rather than performing scalar division or negative-base irrational exponentiation;
5. validate the distinct-prime macro constructor independently and record exact prime-rational closure;
6. preserve the inherited Phase-5 base resolution with no coarsening for the native center state rather than inventing a polynomial refinement;
7. evaluate x² parity normally (`x=0 -> DIRECT/+1`);
8. require the combined manifold closure to accept either:
   - a valid executed Phase-10 polynomial expansion, or
   - the explicit inherited native `0/0=u^0 mod(u^72)=1` closure;
9. retain candidate-only state and zero VM81/Hash72/Hash216/persistence/floating authority;
10. add strict C coverage for the native center state and authenticated benchmark accounting for exactly two frozen center closures.

No actual `propagate_phase_transport()` mutation is introduced.

## Next action

Apply only this Phase-11 singular-center repair, rerun the dependency-scoped Phase-11 workflow, and preserve this precursor as negative evidence. Do not merge, deploy, or promote canonical authority.
