PYTHON ?= python3
REPO_ROOT := ../..
PACKAGE := native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_runner_v2
EVIDENCE := native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence

.PHONY: validate bootstrap test generate verify-existing bundle no-sandbox-drift

bootstrap:
	cd $(REPO_ROOT) && $(MAKE) verify-c
	cd $(REPO_ROOT) && $(PYTHON) hhs_runtime/kernel_resolution.py
	cd $(REPO_ROOT) && $(PYTHON) hhs_runtime_smoke_tests_v1.py
	cd $(REPO_ROOT) && $(PYTHON) hhs_regression_suite_v1.py

test:
	cd $(REPO_ROOT) && $(PYTHON) -m pytest -q \
		tests/test_terminal_hhsprog_v4_symbolic_compat_v1.py \
		tests/test_hhs_pass191_dyadic_quartic_phase_lattice_v1.py

generate:
	cd $(REPO_ROOT) && $(PYTHON) -m $(PACKAGE) --output-dir $(EVIDENCE)

verify-existing:
	cd $(REPO_ROOT) && $(PYTHON) -m $(PACKAGE) --output-dir $(EVIDENCE) --verify-existing

bundle:
	cd $(REPO_ROOT) && $(PYTHON) hhs_v1_bundle_runner.py

no-sandbox-drift:
	cd $(REPO_ROOT) && ! grep -R "/mnt/data" \
		native_projects/hhs_pass191_dyadic_quartic_phase_lattice \
		terminal_hhsprog_v4_symbolic.py \
		HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md

validate: bootstrap test generate verify-existing bundle no-sandbox-drift
