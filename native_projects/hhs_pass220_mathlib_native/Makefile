CC ?= cc
CXX ?= c++
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CXXFLAGS ?= -std=c++20 -O2 -Wall -Wextra -Werror -pedantic

ROOT := ../..
PYTHON1 := ../hhs_pass220_python_native_execution
RUNTIME_INCLUDE := $(ROOT)/hhs_runtime/include
BUILD := build
TARGET := $(BUILD)/hhs_pass220_mathlib_native_v1_test
PYTHON1_OBJ := $(BUILD)/python1.o
EXACT_OBJ := $(BUILD)/exact_abi.o
HASH_OBJ := $(BUILD)/hhs_hash216.o
CELL_WALL_OBJ := $(BUILD)/hhs_pass219_vm81_pqc_cell_wall.o
SUPPORT_STAMP := $(BUILD)/exact-link-support.stamp
TEST_OBJ := $(BUILD)/test.o

.PHONY: all test clean

all: $(TARGET)

$(BUILD):
	mkdir -p $(BUILD)

$(PYTHON1_OBJ): $(PYTHON1)/src/hhs_pass220_python_native_execution_v1.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(PYTHON1)/include -c $< -o $@

$(EXACT_OBJ): $(ROOT)/hhs_runtime/c/hhs_runtime_exact_abi.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(RUNTIME_INCLUDE) -c $< -o $@

$(SUPPORT_STAMP): $(ROOT)/tools/pass219/build_exact_abi_link_support.sh | $(BUILD)
	cd $(ROOT) && CC=$(CC) CXX=$(CXX) bash tools/pass219/build_exact_abi_link_support.sh \
		$(abspath $(BUILD)) full
	touch $@

$(HASH_OBJ) $(CELL_WALL_OBJ): $(SUPPORT_STAMP)
	@test -f $@

$(TEST_OBJ): tests/hhs_pass220_mathlib_native_v1_test.cpp include/hhs_pass220_mathlib_native_v1.hpp | $(BUILD)
	$(CXX) $(CXXFLAGS) -Iinclude -I$(PYTHON1)/include -I$(RUNTIME_INCLUDE) -c $< -o $@

$(TARGET): $(PYTHON1_OBJ) $(EXACT_OBJ) $(HASH_OBJ) $(CELL_WALL_OBJ) $(TEST_OBJ)
	$(CXX) $(CXXFLAGS) \
		$(PYTHON1_OBJ) $(EXACT_OBJ) $(HASH_OBJ) $(CELL_WALL_OBJ) $(TEST_OBJ) \
		-lcrypto -pthread -lm -o $@

test: $(TARGET)
	./$(TARGET)

clean:
	rm -rf $(BUILD)
