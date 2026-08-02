CC ?= cc
AR ?= ar
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
LDFLAGS ?=
BUILD := build
LIBOBJ := $(BUILD)/hhs_pass189_hqlh.o

.PHONY: all clean test disassemble validate python-test iteration2-test iteration3-test iteration4-test surface-test iteration2-surface-test iteration3-surface-test iteration4-surface-test

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

iteration2-test:
	PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass189_iteration2.py

iteration3-test:
	PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass189_iteration3.py

iteration4-test:
	PYTHONPATH=python python3 -m unittest -v python/test_hhs_pass189_iteration4.py

surface-test:
	python3 tools/hhs_pass189_surface_smoke.py

iteration2-surface-test:
	python3 tools/hhs_pass189_iteration2_surface_smoke.py

iteration3-surface-test:
	python3 tools/hhs_pass189_iteration3_surface_smoke.py

iteration4-surface-test:
	python3 tools/hhs_pass189_iteration4_surface_smoke.py

validate: clean all test disassemble
	$(BUILD)/hhs_pass189_cli validate
	$(MAKE) python-test
	$(MAKE) iteration2-test
	$(MAKE) iteration3-test
	$(MAKE) iteration4-test
	$(MAKE) surface-test
	$(MAKE) iteration2-surface-test
	$(MAKE) iteration3-surface-test
	$(MAKE) iteration4-surface-test
	python3 -m py_compile python/hhs_pass189.py python/hhs_pass189_iteration2.py python/hhs_pass189_iteration3.py python/hhs_pass189_iteration4.py server/hhs_pass189_server.py server/hhs_pass189_iteration2_server.py server/hhs_pass189_iteration3_server.py server/hhs_pass189_iteration4_server.py
	bash -n deployment/digitalocean/install.sh deployment/digitalocean/verify.sh

clean:
	rm -rf $(BUILD)
