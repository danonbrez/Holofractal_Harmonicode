CXX ?= c++
CXXFLAGS ?= -std=c++20 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
BUILD := build

all: $(BUILD)/libhhs_pass219_ethical_scope_membrane.a $(BUILD)/test_hhs_pass219_ethical_scope_membrane

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass219_ethical_scope_membrane.o: src/hhs_pass219_ethical_scope_membrane.cpp include/hhs_pass219_ethical_scope_membrane.hpp include/hhs_pass219_ethical_scope_membrane_c.h | $(BUILD)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $< -o $@

$(BUILD)/libhhs_pass219_ethical_scope_membrane.a: $(BUILD)/hhs_pass219_ethical_scope_membrane.o
	ar rcs $@ $<

$(BUILD)/test_hhs_pass219_ethical_scope_membrane: tests/test_hhs_pass219_ethical_scope_membrane.cpp $(BUILD)/hhs_pass219_ethical_scope_membrane.o
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) $^ -o $@

test: $(BUILD)/test_hhs_pass219_ethical_scope_membrane
	./$(BUILD)/test_hhs_pass219_ethical_scope_membrane

clean:
	rm -rf $(BUILD)

.PHONY: all test clean
