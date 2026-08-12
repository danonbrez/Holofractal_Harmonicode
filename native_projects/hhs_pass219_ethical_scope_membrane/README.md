# Pass 219 Ethical Scope Membrane

This native project is the exact C++20/C ABI reference implementation for the Pass 219 `1.4.0` ethical action-scope membrane.

It is deliberately a **constraint evaluator**, not a second runtime authority.

It does not:

- commit VM81 state;
- mint Hash72 or Hash216 authority;
- grant capabilities;
- infer consent;
- promote narrative output to truth;
- perform external I/O.

It evaluates exact trinary ethical invariants and minimum-scope authority constraints, then returns one typed routing decision.

## Core laws

```text
GOOD is non-compensatory.

unknown proposition != false proposition
unknown authority != granted authority

safety may narrow authority
safety may not manufacture authority

prospective aligned execution != completed GOOD
```

## C++ surface

`include/hhs_pass219_ethical_scope_membrane.hpp` provides the typed C++20 evaluator.

The required invariant order is fixed at 18 entries and matches:

`HHS_PASS_218_219_AGI_ETHICAL_INVARIANTS_v1.json`.

## C ABI

`include/hhs_pass219_ethical_scope_membrane_c.h` exposes a non-mutating fixed-layout ABI using four 64-bit scope words (256 addressable local scope slots) and 18 exact trinary invariant states.

The ABI returns:

- active authority mask;
- effective minimum scope;
- missing requested scope;
- missing authority scope;
- extra requested scope;
- failed/unresolved invariant counts;
- typed ethical decision;
- prospective-alignment and post-action GOOD-closure flags.

Any canonical state mutation remains downstream of the inherited VM81 admission path.

## Build

```bash
make
make test
```

The tests cover minimum-scope execution, narrowing, missing authority, missing requested scope, revocation, non-compensatory failure, unresolved simulation-only routing, post-action closure, and C/C++ parity for the core decision table.

## Relationship to narrative reasoning

Pass 218 generates typed counterfactual findings. Those findings are folded into the 18 invariant states before this membrane admits a candidate.

A story can therefore falsify an action or expose an invariant defect without becoming an authority source itself.
