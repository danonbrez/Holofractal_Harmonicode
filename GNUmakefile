# Root extension surface for HHS repository-level development entrypoints.
# The complete inherited Makefile remains authoritative and is included unchanged.
include Makefile

# Pass 219 VM81 PQC firewall build overlay.  Keep the inherited Makefile
# byte-identical while linking the C++ RNA cell-wall bridge into the exact ABI.
CXX ?= c++
CXXFLAGS ?= -O2 -std=c++17 -Wall -Wextra -Werror -pedantic \
	-Ihhs_runtime/include -Ihhs_runtime/c \
	-Inative_projects/hhs_pass188_bott_runtime/include \
	-Inative_projects/hhs_pass189_hqlh_runtime/include
PASS219_PQC_CELL_WALL_SRC := hhs_runtime/cpp/hhs_pass219_vm81_pqc_cell_wall_1_30.cpp
PASS219_PQC_CELL_WALL_OBJ := $(RUNTIME_BUILD_DIR)/pass219/hhs_pass219_vm81_pqc_cell_wall_1_30.o

PASS169_RUNTIME_BINDING_SRCS += $(PASS219_PQC_CELL_WALL_OBJ)
LDFLAGS += -lstdc++ -pthread

$(PASS219_PQC_CELL_WALL_OBJ): $(PASS219_PQC_CELL_WALL_SRC) \
		hhs_runtime/include/hhs_pass219_vm81_pqc_firewall_1_30.h \
		hhs_runtime/include/hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp \
		hhs_runtime/include/hhs_pass219_orthogonal_glyph_membrane_1_21.hpp \
		native_projects/hhs_pass188_bott_runtime/include/hhs_pass188_bott_runtime.h \
		native_projects/hhs_pass189_hqlh_runtime/include/hhs_pass189_hqlh.h | $(RUNTIME_BUILD_DIR)
	mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -fPIC -c $(PASS219_PQC_CELL_WALL_SRC) -o $@

$(ABI_LIB): $(PASS219_PQC_CELL_WALL_OBJ)

.PHONY: test-gfcc test-gfcc-negative test-gfcc-replay verify-gfcc package-pass-152 verify-pass-152 setup start setup-start benchmark-ledger

test-gfcc:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc

test-gfcc-negative:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc-negative

test-gfcc-replay:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 test-gfcc-replay

verify-gfcc:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 verify-gfcc

package-pass-152:
	$(MAKE) -C native_projects/hhs_gfcc_pass152 package-pass-152

verify-pass-152:
	$(MAKE) pass152-full
	$(MAKE) -C native_projects/hhs_gfcc_pass152 verify-pass-152

setup:
	bash init.sh

start:
	bash start.sh

setup-start:
	bash init.sh --start

benchmark-ledger: c-kernel
	python3 tools/benchmark_hhs_ledger_append_v1.py --entries $${HHS_BENCHMARK_ENTRIES:-300}
