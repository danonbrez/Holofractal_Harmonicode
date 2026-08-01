CC ?= cc
AR ?= ar
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
LDFLAGS ?=
BUILD := build
LIBOBJ := $(BUILD)/hhs_pass188_bott_runtime.o $(BUILD)/hhs_pass188_bott_step_x86_64.o

.PHONY: all clean test disassemble validate

all: $(BUILD)/libhhs_pass188.a $(BUILD)/libhhs_pass188.so $(BUILD)/hhs_pass188_cli $(BUILD)/hhs_pass188_test

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass188_bott_runtime.o: src/hhs_pass188_bott_runtime.c include/hhs_pass188_bott_runtime.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -c $< -o $@

$(BUILD)/hhs_pass188_bott_step_x86_64.o: src/hhs_pass188_bott_step_x86_64.S | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -c $< -o $@

$(BUILD)/libhhs_pass188.a: $(LIBOBJ)
	$(AR) rcs $@ $^

$(BUILD)/libhhs_pass188.so: $(LIBOBJ)
	$(CC) -shared $(LDFLAGS) $^ -o $@

$(BUILD)/hhs_pass188_cli: tools/hhs_pass188_cli.c $(BUILD)/libhhs_pass188.a
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(BUILD)/libhhs_pass188.a $(LDFLAGS) -o $@

$(BUILD)/hhs_pass188_test: tests/hhs_pass188_bott_runtime_test.c $(BUILD)/libhhs_pass188.a
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(BUILD)/libhhs_pass188.a $(LDFLAGS) -o $@

test: $(BUILD)/hhs_pass188_test
	$(BUILD)/hhs_pass188_test

disassemble: $(BUILD)/hhs_pass188_test
	objdump -d $(BUILD)/hhs_pass188_test > $(BUILD)/hhs_pass188_test.dis
	! grep -E '\<(f(add|sub|mul|div)|addss|addsd|subss|subsd|mulss|mulsd|divss|divsd)\>' $(BUILD)/hhs_pass188_test.dis
	grep -A14 '<hhs188_bott_step_x86_64>:' $(BUILD)/hhs_pass188_test.dis

validate: clean all test disassemble
	$(BUILD)/hhs_pass188_cli hydrate
	PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass188.py
	python3 tools/hhs_pass188_surface_smoke.py
	python3 -m py_compile python/hhs_pass188.py server/hhs_pass188_server.py

clean:
	rm -rf $(BUILD)
