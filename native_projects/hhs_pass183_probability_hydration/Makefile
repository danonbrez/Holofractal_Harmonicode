CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
CPPFLAGS ?= -Iinclude
BUILD := build
LIB := $(BUILD)/libhhs_p183_probability_hydration.a
OBJ := $(BUILD)/hhs_p183.o
TEST := $(BUILD)/test_hhs_p183
CLI := $(BUILD)/hhs-probability-native
.PHONY: all clean test
all: $(LIB) $(CLI)
$(BUILD):
	mkdir -p $(BUILD)
$(OBJ): src/hhs_p183.c include/hhs_p183.h | $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@
$(LIB): $(OBJ)
	ar rcs $@ $^
$(TEST): tests/test_hhs_p183.c $(LIB)
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(LIB) -o $@
$(CLI): cli/hhs_probability.c $(LIB)
	$(CC) $(CPPFLAGS) $(CFLAGS) $< $(LIB) -o $@
test: $(TEST)
	$(TEST)
clean:
	rm -rf $(BUILD)
