CC ?= cc
PYTHON ?= python
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror

ROOT := ../..
BUILD_DIR := .build
RUNTIME_C := $(ROOT)/hhs_runtime/c
RUNTIME_INCLUDE := $(ROOT)/hhs_runtime/include
DEV_C := c

VM81_SMOKE := $(BUILD_DIR)/hhs_vm81_level1_abi_smoke
HASH_SMOKE := $(BUILD_DIR)/hhs_hash216_level0_smoke
TYPED_SMOKE := $(BUILD_DIR)/hhs_vm81_typed_status_smoke
RESOLVER_SMOKE := $(BUILD_DIR)/hhs_hash216_vector_resolver_smoke

.PHONY: all verify verify-native verify-python evidence clean

all: verify-native

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(VM81_SMOKE): $(DEV_C)/hhs_vm81_level1_abi_smoke.c $(RUNTIME_C)/hhs_runtime_abi.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(RUNTIME_C) $^ -lm -o $@

$(HASH_SMOKE): $(DEV_C)/hhs_hash216_level0_smoke.c $(ROOT)/hhs_runtime/src/hhs_hash216.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(RUNTIME_INCLUDE) $^ -o $@

$(TYPED_SMOKE): $(DEV_C)/hhs_vm81_typed_status_smoke.c $(DEV_C)/hhs_vm81_native_dev_abi.c $(RUNTIME_C)/hhs_runtime_abi.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(RUNTIME_C) -I$(DEV_C) $^ -lm -o $@

$(RESOLVER_SMOKE): $(DEV_C)/hhs_hash216_vector_resolver_smoke.c $(DEV_C)/hhs_hash216_vector_resolver_v1.c $(ROOT)/hhs_runtime/src/hhs_hash216.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -I$(DEV_C) -I$(RUNTIME_INCLUDE) $^ -o $@

verify-native: $(VM81_SMOKE) $(HASH_SMOKE) $(TYPED_SMOKE) $(RESOLVER_SMOKE)
	$(VM81_SMOKE)
	$(HASH_SMOKE)
	$(TYPED_SMOKE)
	$(RESOLVER_SMOKE)

verify-python:
	cd $(ROOT) && $(PYTHON) -m pytest -q \
		tests/test_hhs_vm81_native_development_v1.py \
		tests/test_hhs_vm81_typed_status_and_hash_bindings_v1.py \
		tests/test_hhs_hash216_vector_resolver_v1.py

evidence:
	cd $(ROOT) && $(PYTHON) -m native_projects.hhs_vm81_native_development.hhs_vm81_native_development_v1 --write

verify: verify-native verify-python evidence

clean:
	rm -rf $(BUILD_DIR)
