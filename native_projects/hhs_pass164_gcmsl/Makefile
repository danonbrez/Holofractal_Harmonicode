CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic -O2
CPPFLAGS ?= -Iinclude
BUILD_DIR := build
TEST_BIN := $(BUILD_DIR)/test_hhs_p164_gcmsl

.PHONY: all test clean

all: $(TEST_BIN)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TEST_BIN): src/hhs_p164_gcmsl.c tests/test_hhs_p164_gcmsl.c include/hhs_p164_gcmsl.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) src/hhs_p164_gcmsl.c tests/test_hhs_p164_gcmsl.c -o $(TEST_BIN)

test: $(TEST_BIN)
	./$(TEST_BIN)

clean:
	rm -rf $(BUILD_DIR)
