CC ?= cc
CXX ?= c++
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CXXFLAGS ?= -std=c++20 -O2 -Wall -Wextra -Werror -pedantic

ROOT := ../..
PYTHON1 := ../hhs_pass220_python_native_execution
MATHLIB1 := ../hhs_pass220_mathlib_native
RUNTIME_INCLUDE := $(ROOT)/hhs_runtime/include
BUILD := build
TARGET := $(BUILD)/hhs_pass220_mathlib_order_rat_v1_test
PYTHON1_OBJ := $(BUILD)/python1.o
TEST_OBJ := $(BUILD)/test.o

.PHONY: all test clean

all: $(TARGET)

$(BUILD):
	mkdir -p $(BUILD)

$(PYTHON1_OBJ): $(PYTHON1)/src/hhs_pass220_python_native_execution_v1.c | $(BUILD)
	$(CC) $(CFLAGS) -I$(PYTHON1)/include -c $< -o $@

$(TEST_OBJ): tests/hhs_pass220_mathlib_order_rat_v1_test.cpp include/hhs_pass220_mathlib_order_rat_v1.hpp | $(BUILD)
	$(CXX) $(CXXFLAGS) \
		-Iinclude -I$(MATHLIB1)/include -I$(PYTHON1)/include -I$(RUNTIME_INCLUDE) \
		-c $< -o $@

$(TARGET): $(PYTHON1_OBJ) $(TEST_OBJ)
	$(CXX) $(CXXFLAGS) $^ -o $@

test: $(TARGET)
	./$(TARGET)

clean:
	rm -rf $(BUILD)
