# HHS / HARMONICODE v1 release build surface
# Scope: C runtime ABI and standalone VM81 verification only.

CC ?= gcc
CXX ?= c++
CFLAGS ?= -O2 -std=c11 -Wall -Wextra -Ihhs_runtime/include -Ihhs_runtime/c
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Werror -pedantic -Ihhs_runtime/include -Ihhs_runtime/c
LDFLAGS ?= -lm -lcrypto
CXX_RUNTIME_LDFLAGS ?= -lstdc++ -pthread
RUNTIME_BUILD_DIR := hhs_runtime/builds
ABI_LIB := $(RUNTIME_BUILD_DIR)/libhhs_runtime.so
EXACT_ABI_DEPS := hhs_runtime/c/hhs_runtime_exact_abi.c $(wildcard hhs_runtime/c/*.inc)
PASS219_PQC_CELL_WALL_SRC := hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp
PASS219_PQC_CELL_WALL_OBJ := $(RUNTIME_BUILD_DIR)/pass219/hhs_pass219_vm81_pqc_cell_wall_1_30.o
PASS159_ROOT := native_projects/hhs_pass159_harmonicode_toolchain
PASS159_CORE := $(RUNTIME_BUILD_DIR)/pass159/hhs159_core.c
PASS159_INCLUDES := -I$(PASS159_ROOT)/include -I$(PASS159_ROOT)/src
PASS169_RUNTIME_BINDING_SRCS := \
	hhs_runtime/c/hhs_pass219_pass159_global_witness_producer_1_21_10.c \
	hhs_runtime/c/hhs_pass219_pass169_gate_authority_binding_1_21_11.c \
	hhs_runtime/c/hhs_pass219_pass169_runtime_provider_1_21_13.c \
	hhs_runtime/c/hhs_pass219_i162_pass169_vm81_exact_symbolic_execution_1_23.c \
	hhs_runtime/c/hhs_pass219_i163_pass169_reverse_crossarch_1_24.c \
	hhs_runtime/c/hhs_pass219_i163_hash72_reverse_witness_1_24.c \
	hhs_runtime/c/hhs_pass219_i163_vm81_snapshot_reverse_witness_1_24.c \
	hhs_runtime/c/hhs_pass219_i168_pass169_general_runtime_binding_1_25.c
VM81_BIN := $(RUNTIME_BUILD_DIR)/hhs_vm81

.PHONY: all c-kernel c-abi vm81 verify-c emulate-c service-registry io-gateway semantic-memory-guard runtime-dataflow-guard persistence-guard runtime-contract foundational-standards hash72-u72 hash72-kernel-authority backend-routes gui-runtime-contract srcg-primitive srcg-api-surface system-closure-harness runtime-reachability runtime-integration-decisions guarded-plugin-adapters plugin-capability-planner guarded-plugin-invocation-executor contract-schema-registry constraint-stack-security-harness runtime-constraint-enforcement zero-bypass-runtime-interposer test clean

all: c-kernel

c-kernel: c-abi vm81

$(RUNTIME_BUILD_DIR):
	mkdir -p $(RUNTIME_BUILD_DIR)

c-abi: $(ABI_LIB)

$(PASS159_CORE): $(PASS159_ROOT)/src/hhs159_core.c.gz | $(RUNTIME_BUILD_DIR)
	mkdir -p $(dir $@)
	gzip -dc $< > $@

$(PASS219_PQC_CELL_WALL_OBJ): $(PASS219_PQC_CELL_WALL_SRC) \
		hhs_runtime/include/hhs_pass219_vm81_pqc_firewall_1_30.h \
		hhs_runtime/include/hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp \
		hhs_runtime/include/hhs_pass219_orthogonal_glyph_membrane_1_21.hpp | $(RUNTIME_BUILD_DIR)
	mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -fPIC -c $(PASS219_PQC_CELL_WALL_SRC) -o $@

$(ABI_LIB): hhs_runtime/c/hhs_runtime_abi.c hhs_runtime/src/hhs_hash216.c hhs_runtime/c/hhs_runtime_abi.h hhs_runtime/include/hhs_hash216.h hhs_runtime/include/hhs_runtime_exact_abi.h hhs_runtime/include/hhs_pass219_vm81_pqc_firewall_1_30.h $(EXACT_ABI_DEPS) $(PASS159_CORE) $(PASS169_RUNTIME_BINDING_SRCS) $(PASS219_PQC_CELL_WALL_OBJ) | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) $(PASS159_INCLUDES) -fPIC -shared \
		hhs_runtime/c/hhs_runtime_abi.c hhs_runtime/src/hhs_hash216.c \
		$(PASS159_CORE) $(PASS169_RUNTIME_BINDING_SRCS) $(PASS219_PQC_CELL_WALL_OBJ) \
		-o $(ABI_LIB) $(LDFLAGS) $(CXX_RUNTIME_LDFLAGS)

vm81: $(VM81_BIN)

$(VM81_BIN): hhs_runtime/HARMONICODE_VM_RUNTIME.c hhs_runtime/include/HARMONICODE_VM_RUNTIME.h | $(RUNTIME_BUILD_DIR)
	$(CC) $(CFLAGS) hhs_runtime/HARMONICODE_VM_RUNTIME.c -o $(VM81_BIN) $(LDFLAGS)

verify-c: c-kernel
	$(VM81_BIN) --verify
	test -f $(ABI_LIB)
	nm -D $(ABI_LIB) | grep -E 'hhs_runtime_init|hhs_runtime_step|hhs_validate_abi|hhs_hash216_compute'

emulate-c: c-kernel
	python -m hhs_python.runtime.hhs_runtime_emulator

service-registry: c-kernel
	python -m hhs_runtime.hhs_service_registry_v1

io-gateway: c-kernel
	python -m hhs_runtime.hhs_io_gateway_v1

semantic-memory-guard: c-kernel
	python -m hhs_runtime.hhs_semantic_memory_guard_v1

runtime-dataflow-guard: c-kernel
	python -m hhs_runtime.hhs_runtime_dataflow_guard_v1

persistence-guard: c-kernel
	python -m hhs_runtime.hhs_persistence_guard_v1

runtime-contract: c-kernel
	python -m hhs_runtime.hhs_runtime_contract_v1

foundational-standards: c-kernel
	python -m hhs_foundation.hhs_foundational_standards_v1

hash72-u72: c-kernel
	pytest -q tests/test_hhs_hash72_u72_ring_v1.py

hash72-kernel-authority: c-kernel
	pytest -q tests/test_hhs_hash72_kernel_authority_v1.py

backend-routes: c-kernel
	pytest -q tests/test_hhs_backend_guarded_routes_v1.py

test: c-kernel
	pytest -q

clean:
	rm -rf $(RUNTIME_BUILD_DIR)

.PHONY: hash72-kernel-surfaces
hash72-kernel-surfaces:
	python -m pytest -q tests/test_hhs_hash72_kernel_surface_unification_v1.py


gui-runtime-contract:
	python -m pytest -q tests/test_hhs_gui_runtime_contract_surface_v1.py


srcg-primitive: c-kernel
	python -m pytest -q tests/test_hhs_srcg_gate_v1.py


srcg-api-surface: c-kernel
	python -m pytest -q tests/test_hhs_backend_guarded_routes_v1.py tests/test_hhs_gui_runtime_contract_surface_v1.py


system-closure-harness: c-kernel
	python -m pytest -q tests/test_hhs_system_closure_harness_v1.py


runtime-reachability: c-kernel
	python -m hhs_runtime.hhs_runtime_reachability_audit_v1


runtime-integration-decisions: c-kernel
	python -m hhs_runtime.hhs_runtime_integration_decisions_v1
