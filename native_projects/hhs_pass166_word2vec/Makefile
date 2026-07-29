CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Werror -pedantic -O2
CPPFLAGS ?= -Iinclude
BUILD_DIR := build
TEST_BIN := $(BUILD_DIR)/test_hhs_p166_word2vec

.PHONY: all test clean

all: $(TEST_BIN)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(TEST_BIN): src/hhs_p166_word2vec.c tests/test_hhs_p166_word2vec.c include/hhs_p166_word2vec.h | $(BUILD_DIR)
	$(CC) $(CFLAGS) $(CPPFLAGS) src/hhs_p166_word2vec.c tests/test_hhs_p166_word2vec.c -o $(TEST_BIN)

test: $(TEST_BIN)
	./$(TEST_BIN)

clean:
	rm -rf $(BUILD_DIR)
