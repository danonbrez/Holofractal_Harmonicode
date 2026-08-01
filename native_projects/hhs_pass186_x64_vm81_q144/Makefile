CC ?= cc
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude

BUILD := build
TARGET := $(BUILD)/hhs_pass186_x64_vm81_q144_smoke
OBJECTS := \
	$(BUILD)/hhs_pass186_x64_vm81_q144_abi.o \
	$(BUILD)/hhs_pass186_x64_registers.o \
	$(BUILD)/hhs_pass186_x64_vm81_q144_smoke.o

.PHONY: all test clean disassemble

all: $(TARGET)

test: $(TARGET)
	./$(TARGET)

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass186_x64_vm81_q144_abi.o: src/hhs_pass186_x64_vm81_q144_abi.c include/hhs_pass186_x64_vm81_q144_abi.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(BUILD)/hhs_pass186_x64_registers.o: src/hhs_pass186_x64_registers.S | $(BUILD)
	$(CC) -c $< -o $@

$(BUILD)/hhs_pass186_x64_vm81_q144_smoke.o: tests/hhs_pass186_x64_vm81_q144_smoke.c include/hhs_pass186_x64_vm81_q144_abi.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $@

disassemble: $(TARGET)
	objdump -d $(TARGET) > $(BUILD)/hhs_pass186_x64_vm81_q144_smoke.disasm
	! grep -E '\b(x87|fld|fst|fadd|fsub|fmul|fdiv|addss|addsd|mulss|mulsd|divss|divsd)\b' $(BUILD)/hhs_pass186_x64_vm81_q144_smoke.disasm

clean:
	rm -rf $(BUILD)
