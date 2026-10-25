# Pass 220 — HNAN Lane 5 exact-equation checkpoint

Date: 2026-10-25
Base: `8426bc721ab0fcce287ee11567172f28d1016e23`
Branch: `checkpoint/pass220-hnan-lane5-exact-gradient-20261025`
Merge target: `main`

## Change scope
Added read-only exact witness `hhs_runtime/pass220/hnan_lane5_exact_witness_v1.py` and dependency-scoped regression `tests/pass220/test_hnan_lane5_exact_witness_v1.py`.

Implements exact symbolic checks for the supplied U(u).LoShu/pi == B(u) identity using integral Laurent coefficients of formal u^(1/8), nine-cell constant gradient offsets F-G=D, 72-modular reciprocal Hash72 positions, and 72*8*9=5184 address bijection.

No canonical inverse, Genesis closure, native phase noncommutative rewrite, native C++ ABI, VM81 mutation or admission, Hash72 mint, Hash216 receipt, optimized GPU ranking, or performance improvement is asserted. The Wolfram-verified exact matrix factorization does not itself authorize inverse closure.

## Source commits
- `af03f2ef21002d3452d333fad092bf245940674a` — module
- `ca56e7fc5ab11cffa18cf325f1d77c9d71fa418f` — tests

## Evidence and commands
Repository inspection through GitHub connector: AGENTS.md, REPOSITORY_INDEX.md, existing HNAN phase5184 bridge, previous 2026-10-24 restart record. Symbolic Wolfram evaluation in conversation confirmed U(u).LoShu == pi*B(u) and F-G constant offset with equal x gradients.

No shell tests or C++ build run: only GitHub connector access available. Exact targeted command to execute in checkout:
`python -m pytest -q tests/pass220/test_hnan_lane5_exact_witness_v1.py`

## Remaining
1. Run focused test on branch; repair forward.
2. Inspect existing C++ cell-wall native NcalcMatrixPower and HNAN admissibility, and validate exact phase and reciprocal semantics before binding this witness as an enforced Lane 5 optimization admission contract.
3. Review changes and no-authority-bypass; merge PR after validation; verify main.
4. Run native ABI/Lean/Wolfram checks and production dependency-scoped validation as impact requires.

## Environment/blockers
GitHub connector source access; no checked-out repository build or native test execution. No performance measurement, production deployment, completed merge, or verified-main receipt is claimed.

## Continuation — focused CI checkpoint

- Existing Pass 220 I076 `ExactMatrixPower` HIR contract inspected: matrix power stays typed, unevaluated by the host, with VM81 admission required. This work does not substitute scalar/ordinary matrix inversion.
- PR #853 remains draft and mergeable at inspection; unrelated PR-head workflow successes do not certify the focused HNAN tests.
- New file: `.github/workflows/pass220-hnan-lane5-exact-witness.yml` to run focused unittest discovery on affected PR/push changes.
- CI addition commit: `65e4ae06441390021999e8cf8d686d83666e470f`.
- Remaining: inspect new workflow result; repair-forward if needed; native C++/HNAN `NcalcMatrixPower` certification, optimizer candidate-bound guard, and verified-main merge are not yet complete.

## Continuation — 2026-10-25 native 1.63 preflight binding
- Verified exact-witness PR-head workflow 40235318163 completed successfully at commit `960bc4ed6429fdaa1ef6bcb4ce3118505ae7703a`.
- Read native `hhs_runtime/hhs_pass220_recursive_hnan_native_rule_preflight_v1.py` and Pass 220 I076 `ExactMatrixPower` HIR contract. Native preflight already validates authoritative C rule mask and remains candidate-only.
- Added read-only exact-phase witness to the existing native preflight **after** native global verification; any exact-symbolic drift or authority flag drift fails closed.
- Added targeted rejection regression and expanded focused CI path filters and command.
- Changed: native preflight, its regression test, focused workflow, this checkpoint.
- Commits: `e69b58771b6cf3b582fd8f9adb7c7c303b3ff2c7`, `8a4849d06133bb10b1b2c1107a7844112f392d80`, `913f5bc5a38165bc63f73d5d494114705e8a0b21`.
- No new C++ ABI, no proof of NcalcMatrixPower native inverse or Genesis equivalence, no VM81 mutation or canonical Hash72/Hash216 minting. This is exact read-only candidate preflight enforcement, not a fully certified native closure.
- Remaining: inspect fresh workflow results for latest head; dependency-scoped genuine native C++ compile and rule regression; branch review; merge and verify authoritative main. No local checkout executed.

## Continuation — exact gradient derivation repair

- The prior witness held F-G constant as a literal and compared it to the same literal, insufficient as an independent computation.
- Updated `derive_gradient_offsets()` to calculate each of the nine differences from the source `-5` constant and each explicitly expanded phase-carrier constant; exact shared S*carrier coefficients cancel without floating arithmetic or matrix normalization.
- Added positive derivation assertion and negative altered-cell regression. Existing native preflight binding automatically inherits the stronger check.
- Commits: `a88526ae5d015e64207e7c9ab17748ed86119f29` (source), `7756d3addb1d3cb57ffeb3f77926f86067a33f2d` (tests).
- At inspection, latest prior PR-head focused/native workflows were queued; green status cannot be inferred for these new commits. No local shell command or native compile executed.
- Next: inspect focused workflow on current head; repair forward if necessary; native C/Lean/ExactMatrixPower closure still pending. Do not merge before targeted validations.
