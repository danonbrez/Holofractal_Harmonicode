CC ?= cc
PYTHON ?= python3
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
BUILD := build
TERMINAL_BUILD := $(BUILD)/terminal

all: $(BUILD)/libhhs_pass175.a $(BUILD)/test_hhs_pass175 terminal-native

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass175.o: src/hhs_pass175.c include/hhs_pass175.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(BUILD)/libhhs_pass175.a: $(BUILD)/hhs_pass175.o
	ar rcs $@ $<

$(BUILD)/test_hhs_pass175: tests/test_hhs_pass175.c $(BUILD)/hhs_pass175.o
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

terminal-native:
	$(PYTHON) build_terminal_artifacts.py --project-root . --out $(TERMINAL_BUILD)

test: $(BUILD)/test_hhs_pass175 terminal-native
	./$(BUILD)/test_hhs_pass175
	test -s $(TERMINAL_BUILD)/vm81_invariant_kernel_test_receipt.json

clean:
	rm -rf $(BUILD)

.PHONY: all test clean terminal-native
