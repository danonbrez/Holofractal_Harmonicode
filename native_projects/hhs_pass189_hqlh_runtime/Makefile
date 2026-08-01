CC ?= cc
AR ?= ar
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
LDFLAGS ?=
BUILD := build
LIBOBJ := $(BUILD)/hhs_pass189_hqlh.o

.PHONY: all clean test disassemble validate python-test surface-test

all: $(BUILD)/libhhs_pass189.a $(BUILD)/libhhs_pass189.so $(BUILD)/hhs_pass189_cli $(BUILD)/hhs_pass189_test

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass189_hqlh.o: src/hhs_pass189_hqlh.c include/hhs_pass189_hqlh.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -fPIC -c $< -o $@

$(BUILD)/libhhs_pass189.a: $(LIBOBJ)
	$(AR) rcs $@ $^

$(BUILD)/libhhs_pass189.so: $(LIBOBJ)
	$(CC) -shared $(LDFLAGS) $^ -o $@

$(BUILD)/hhs_pass189_cli: tools/hhs_pass189_cli.c $(BUILD)/libhhs_pass189.a
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(BUILD)/libhhs_pass189.a $(LDFLAGS) -o $@

$(BUILD)/hhs_pass189_test: tests/hhs_pass189_hqlh_test.c $(BUILD)/libhhs_pass189.a
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(BUILD)/libhhs_pass189.a $(LDFLAGS) -o $@

test: $(BUILD)/hhs_pass189_test
	$(BUILD)/hhs_pass189_test

disassemble: $(BUILD)/hhs_pass189_test
	objdump -d $(BUILD)/hhs_pass189_test > $(BUILD)/hhs_pass189_test.dis
	! grep -E '\<(f(add|sub|mul|div)|addss|addsd|subss|subsd|mulss|mulsd|divss|divsd|vadd|vsub|vmul|vdiv)' $(BUILD)/hhs_pass189_test.dis

python-test:
	PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass189.py

surface-test:
	python3 tools/hhs_pass189_surface_smoke.py

validate: clean all test disassemble
	$(BUILD)/hhs_pass189_cli validate
	$(MAKE) python-test
	$(MAKE) surface-test
	python3 -m py_compile python/hhs_pass189.py server/hhs_pass189_server.py

clean:
	rm -rf $(BUILD)
