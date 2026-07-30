CC ?= cc
CFLAGS ?= -std=c11 -O3 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
BUILD := build

all: $(BUILD)/libhhs_pass175.a $(BUILD)/test_hhs_pass175

$(BUILD):
	mkdir -p $(BUILD)

$(BUILD)/hhs_pass175.o: src/hhs_pass175.c include/hhs_pass175.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

$(BUILD)/libhhs_pass175.a: $(BUILD)/hhs_pass175.o
	ar rcs $@ $<

$(BUILD)/test_hhs_pass175: tests/test_hhs_pass175.c $(BUILD)/hhs_pass175.o
	$(CC) $(CPPFLAGS) $(CFLAGS) $^ -o $@

test: $(BUILD)/test_hhs_pass175
	./$(BUILD)/test_hhs_pass175

clean:
	rm -rf $(BUILD)

.PHONY: all test clean
