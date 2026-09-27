CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
BUILD := build
TARGET := $(BUILD)/hhs_pass179_render_command_v1_test

.PHONY: all test wasm clean

all: $(TARGET)

$(BUILD):
	mkdir -p $(BUILD)

$(TARGET): src/hhs_pass179_render_command_v1.c include/hhs_pass179_render_command_v1.h tests/hhs_pass179_render_command_v1_test.c | $(BUILD)
	$(CC) $(CFLAGS) -Iinclude src/hhs_pass179_render_command_v1.c tests/hhs_pass179_render_command_v1_test.c -o $(TARGET)

test: $(TARGET)
	./$(TARGET)

wasm:
	sh tools/build_wasm.sh

clean:
	rm -rf $(BUILD)
