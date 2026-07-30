CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -pedantic
ROOT := ../..
P163 := ../hhs_pass163_vmrc
BUILD_DIR ?= build
TARGET := $(BUILD_DIR)/test_hhs_p174_runtime

.PHONY: all test clean test-tmp

all: $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TARGET): src/hhs_p174_runtime.c tests/test_hhs_p174_runtime.c $(P163)/src/hhs_p163_vmrc.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) \
		-Iinclude \
		-I$(P163)/include \
		src/hhs_p174_runtime.c \
		$(P163)/src/hhs_p163_vmrc.c \
		tests/test_hhs_p174_runtime.c \
		-o $(TARGET)

test: $(TARGET)
	$(TARGET)

test-tmp:
	@tmp_root="$${TMPDIR:-/tmp}/hhs-pass174-native-$$$$"; \
	$(MAKE) clean BUILD_DIR="$$tmp_root"; \
	$(MAKE) test BUILD_DIR="$$tmp_root"; \
	rm -rf "$$tmp_root"

clean:
	rm -rf $(BUILD_DIR)
