# Next Pass 041 — Closure Harness Bounded Runtime and Control-Flow Transition Audits

Recommended next focus:

1. Make the inherited system closure harness bounded under full pytest.
2. Upgrade `audited_if()` and `audited_loop()` from scalar-proxy checks to full state-transition audits.
3. Bind closure harness residue to the Pass 040 validation-residue state chain.
4. Add explicit sandbox authority-boundary certification tests.

The next pass should reduce inherited long-running certification paths and remove scalar audit shortcuts from control-flow semantics.
