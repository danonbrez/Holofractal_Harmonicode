PYTHON ?= python3
CC ?= cc
REPO_ROOT := ../..
PACKAGE := native_projects.hhs_pass191_dyadic_quartic_phase_lattice.hhs_pass191_runner_v4
EVIDENCE := native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence
PASS186 := native_projects/hhs_pass186_x64_vm81_q144
PASS189 := native_projects/hhs_pass189_hqlh_runtime
NATIVE_LIB := native_projects/hhs_pass191_dyadic_quartic_phase_lattice/build/libhhs186_vm81_q144.so
MANIFOLD_SCANNER := native_projects/hhs_pass191_dyadic_quartic_phase_lattice/build/hhs191_manifold_scan
MANIFOLD_SOURCE := native_projects/hhs_pass191_dyadic_quartic_phase_lattice/src/hhs_pass191_manifold_scan.c

.PHONY: validate native-authority manifold-smoke bootstrap test generate verify-existing bundle no-sandbox-drift

native-authority:
	cd $(REPO_ROOT) && $(MAKE) -C $(PASS186) clean test disassemble
	cd $(REPO_ROOT) && mkdir -p native_projects/hhs_pass191_dyadic_quartic_phase_lattice/build
	cd $(REPO_ROOT) && $(CC) -shared -fPIC -std=c11 -O3 -Wall -Wextra -Werror -pedantic \
		-I$(PASS186)/include \
		$(PASS186)/src/hhs_pass186_x64_vm81_q144_abi.c \
		-o $(NATIVE_LIB)
	cd $(REPO_ROOT) && $(CC) -std=c11 -O3 -Wall -Wextra -Werror -pedantic \
		-I$(PASS189)/include \
		$(PASS189)/src/hhs_pass189_hqlh.c \
		$(MANIFOLD_SOURCE) \
		-o $(MANIFOLD_SCANNER)

manifold-smoke:
	cd $(REPO_ROOT) && $(MANIFOLD_SCANNER) 0 4096 0 > native_projects/hhs_pass191_dyadic_quartic_phase_lattice/build/manifold-smoke.json
	cd $(REPO_ROOT) && $(PYTHON) -c 'import json; p=json.load(open("native_projects/hhs_pass191_dyadic_quartic_phase_lattice/build/manifold-smoke.json")); assert p["visited"] == 4096 and p["coordinate_drift"] == 0 and p["quartic_checks"] == 4096'

bootstrap:
	cd $(REPO_ROOT) && $(MAKE) verify-c
	cd $(REPO_ROOT) && $(PYTHON) hhs_runtime/kernel_resolution.py
	cd $(REPO_ROOT) && $(PYTHON) hhs_runtime_smoke_tests_v1.py
	cd $(REPO_ROOT) && $(PYTHON) hhs_regression_suite_v1.py

test:
	cd $(REPO_ROOT) && $(PYTHON) -m pytest -q \
		tests/test_terminal_hhsprog_v4_symbolic_compat_v1.py \
		tests/test_hhs_pass191_dyadic_quartic_phase_lattice_v1.py \
		tests/test_hhs_pass191_integrated_proof_engine_v1.py

generate:
	cd $(REPO_ROOT) && $(PYTHON) -m $(PACKAGE) \
		--output-dir $(EVIDENCE) \
		--native-library $(NATIVE_LIB) \
		--manifold-scanner $(MANIFOLD_SCANNER)

verify-existing:
	cd $(REPO_ROOT) && $(PYTHON) -m $(PACKAGE) \
		--output-dir $(EVIDENCE) \
		--native-library $(NATIVE_LIB) \
		--verify-existing

bundle:
	cd $(REPO_ROOT) && $(PYTHON) hhs_v1_bundle_runner.py

no-sandbox-drift:
	cd $(REPO_ROOT) && ! grep -R \
		--exclude=Makefile \
		--exclude-dir=build \
		--exclude-dir=__pycache__ \
		"/mnt/data" \
		native_projects/hhs_pass191_dyadic_quartic_phase_lattice \
		terminal_hhsprog_v4_symbolic.py \
		HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md

validate: native-authority manifold-smoke bootstrap test generate verify-existing bundle no-sandbox-drift
