CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
SRC := src/hhs_vm81_game.c
SRC_PARTS := src/hhs_vm81_game_part_00.inc src/hhs_vm81_game_part_01.inc src/hhs_vm81_game_part_02.inc
DIST := dist

.PHONY: all test sanitize clean verify

all: $(DIST)/hhs-vm81-game $(DIST)/test-hhs-vm81-game

$(DIST):
	mkdir -p $(DIST)

$(DIST)/hhs-vm81-game: $(SRC) $(SRC_PARTS) src/hhs_vm81_game_cli.c include/hhs_vm81_game.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) src/hhs_vm81_game_cli.c $(HASH_SRC) -o $@

$(DIST)/test-hhs-vm81-game: $(SRC) $(SRC_PARTS) tests/test_hhs_vm81_game.c include/hhs_vm81_game.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(SRC) tests/test_hhs_vm81_game.c $(HASH_SRC) -o $@

test: all
	$(DIST)/test-hhs-vm81-game
	$(DIST)/hhs-vm81-game > $(DIST)/verification.json
	grep -q 'VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED' $(DIST)/verification.json

sanitize: | $(DIST)
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(SRC) tests/test_hhs_vm81_game.c $(HASH_SRC) -o $(DIST)/test-hhs-vm81-game-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-vm81-game-sanitized

verify: test sanitize

clean:
	rm -rf $(DIST)
