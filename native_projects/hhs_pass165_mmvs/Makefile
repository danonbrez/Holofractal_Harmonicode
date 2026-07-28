CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic -O2
CPPFLAGS ?= -Iinclude
BUILD := build
TEST := $(BUILD)/test_hhs_p165_mmvs
all: $(TEST)
$(TEST): src/hhs_p165_mmvs.c tests/test_hhs_p165_mmvs.c include/hhs_p165_mmvs.h
	mkdir -p $(BUILD)
	$(CC) $(CPPFLAGS) $(CFLAGS) src/hhs_p165_mmvs.c tests/test_hhs_p165_mmvs.c -o $(TEST)
test: $(TEST)
	./$(TEST)
clean:
	rm -rf $(BUILD)
.PHONY: all test clean
