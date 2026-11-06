# Pass 220 — Lane 5 exact rational equivalence/congruence restart

- Parent: main after confirmed PR #858 merge `dc2146b2801a699912996dc2065ed339907db226`; branch created from main.
- Branch: `pass220/lean-equivalence-congruence-lane5-20261027`, target main.
- Objective: expose existing I053/I054 Lean ExactRat equivalence and congruence theorem applications to Lane 5 without collapsing unreduced pair identities.
- Source: `formal/lean/HHS/Mathlib/Rat/Equivalence.lean` and `formal/lean/HHS/Mathlib/Rat/Congruence.lean`.
- Added: `hhs_runtime/pass220/lane5_lean_equivalence_congruence_v1.py`, `formal/lean/HHS/Pass220/Lane5EquivalenceApplications.lean`, `tests/pass220/test_lane5_lean_equivalence_congruence_v1.py`, `.github/workflows/pass220-lane5-lean-equivalence-congruence.yml`.
- Six typed theorem applications: refl, symm, trans, neg congruence, add congruence, mul congruence; premises must be supplied as exact unreduced ordered pairs, and are checked before candidate evidence returned.
- Commits: `bbce5f324af2a73350a2e87fdc98ef1eb35c5e54`, `43225ef8359174439f07390a6b2a5755d8614e3c`, `42d5390338892da17fab29a353794c4f89c08eca`, `4b8322af8e9106b5463e07aa23178f27d4bc286a`.
- No actual live Lean kernel invocation in runtime or generic HNAN commutation; candidate-only, no VM81 or Hash216 authority.
- Validation: source inspected, new Lean/CI/tests committed, no new run confirmed. No production deployment.
- Next: open PR, verify CI, repair focused Lean compiler/runtime test failures, then bind proven theorem/dependency identities into Lane 5 evidence before any native admission.
