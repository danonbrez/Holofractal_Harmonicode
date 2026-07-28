CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic -O2
CPPFLAGS ?= -Iinclude
BUILD_DIR := build
TARGET := $(BUILD_DIR)/test_hhs_p163_vmrc

.PHONY: all test clean
all: $(TARGET)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TARGET): src/hhs_p163_vmrc.c tests/test_hhs_p163_vmrc.c include/hhs_p163_vmrc.h | $(BUILD_DIR)
	$(CC) $(CPPFLAGS) $(CFLAGS) src/hhs_p163_vmrc.c tests/test_hhs_p163_vmrc.c -o $(TARGET)

test: $(TARGET)
	./$(TARGET)

clean:
	rm -rf $(BUILD_DIR)
