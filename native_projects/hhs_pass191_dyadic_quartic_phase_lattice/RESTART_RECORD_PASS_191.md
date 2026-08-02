# Pass 191 restart record

Base commit: `992b4e92a54d4656d66af4edfab7e03922addca6`

Branch: `agent/pass191-dyadic-quartic-phase-lattice`

Merge target: `main`

Draft pull request: `#124`

## Implemented scope

- exact dyadic/quartic `PhaseState` model;
- syntax-preserving Terminal V4 compatibility module required by Terminal V5;
- W191-A through W191-E with five VM81/AuditedRunner receipts;
- inherited Pass 082 native benchmark binding;
- formal proof/falsification/obstruction ledger;
- Hash72 per-obligation outcomes and formal-ledger root;
- authoritative v2 evidence generator and verifier;
- updated white paper and dependency-scoped CI.

## Formal outcome state

The ordered Pass 191 ledger contains ten obligations:

- `PROVED`: 4;
- `FALSIFIED`: 3;
- `OBSTRUCTED`: 3.

`DQPL-RH-TRANSFER` is controlled by these unresolved dependencies:

1. `ZETA_DOMAIN_AND_ANALYTIC_CONTINUATION_ENCODING`
2. `ZETA_ZERO_TO_PHASE_CLOSURE_EQUIVALENCE`
3. `PHASE_MAP_FAITHFULNESS`
4. `OFF_AXIS_ZERO_EXCLUSION_OR_COUNTEREXAMPLE_TRANSFER`

Admissible continuation paths are proof of all bridge lemmas or an exact off-axis zero certificate accepted by the same phase map.

## Validation sequence

```bash
make verify-c
python hhs_runtime/kernel_resolution.py
python hhs_runtime_smoke_tests_v1.py
python hhs_regression_suite_v1.py
python -m pytest -q tests/test_terminal_hhsprog_v4_symbolic_compat_v1.py tests/test_hhs_pass191_dyadic_quartic_phase_lattice_v1.py
python -m native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_runner_v2 --output-dir native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence
python -m native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_runner_v2 --output-dir native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence --verify-existing
python hhs_v1_bundle_runner.py
```

The GitHub workflow installs the repository-aligned FastAPI validation dependencies before executing `make validate`.

## Restart rule

Resume from the latest head of `agent/pass191-dyadic-quartic-phase-lattice`. Inspect the newest `Pass 191 Dyadic Quartic Phase Lattice` workflow run. Repair only the failing dependency scope, rerun the full Pass 191 validation gate once, commit generated evidence, and keep PR #124 in draft state until the user authorizes merge readiness.
