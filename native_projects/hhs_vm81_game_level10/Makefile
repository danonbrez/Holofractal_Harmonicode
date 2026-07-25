CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
CORE_SRC := src/hhs_vm81_game.c
RELEASE_SRC := src/hhs_vm81_game_release.c
SRC_PARTS := src/hhs_vm81_game_part_00.inc src/hhs_vm81_game_part_01.inc src/hhs_vm81_game_part_02.inc
DIST := dist

.PHONY: all play test sanitize clean verify

all: $(DIST)/hhs-vm81-game $(DIST)/test-hhs-vm81-game \
	$(DIST)/hhs-vm81-platformer $(DIST)/test-hhs-vm81-game-release

$(DIST):
	mkdir -p $(DIST)

$(DIST)/hhs-vm81-game: $(CORE_SRC) $(SRC_PARTS) src/hhs_vm81_game_cli.c include/hhs_vm81_game.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) src/hhs_vm81_game_cli.c $(HASH_SRC) -o $@

$(DIST)/test-hhs-vm81-game: $(CORE_SRC) $(SRC_PARTS) tests/test_hhs_vm81_game.c include/hhs_vm81_game.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) tests/test_hhs_vm81_game.c $(HASH_SRC) -o $@

$(DIST)/hhs-vm81-platformer: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) src/hhs_vm81_game_playable_cli.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) src/hhs_vm81_game_playable_cli.c $(HASH_SRC) -o $@

$(DIST)/test-hhs-vm81-game-release: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) tests/test_hhs_vm81_game_release.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) tests/test_hhs_vm81_game_release.c $(HASH_SRC) -o $@

play: $(DIST)/hhs-vm81-platformer
	$(DIST)/hhs-vm81-platformer

test: all
	$(DIST)/test-hhs-vm81-game
	$(DIST)/test-hhs-vm81-game-release
	$(DIST)/hhs-vm81-game > $(DIST)/verification.json
	$(DIST)/hhs-vm81-platformer --headless > $(DIST)/playable-verification.json
	grep -q 'VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED' $(DIST)/verification.json
	grep -q 'VM81_PLAYABLE_GAME_RELEASE_VERIFIED' $(DIST)/playable-verification.json
	grep -q '"phase": "VICTORY"' $(DIST)/playable-verification.json
	grep -q '"opcode_coverage": "19/19"' $(DIST)/playable-verification.json
	grep -q '"checkpoints_reached": 2' $(DIST)/playable-verification.json
	grep -q '"replay": "MATCH"' $(DIST)/playable-verification.json

sanitize: | $(DIST)
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(CORE_SRC) tests/test_hhs_vm81_game.c $(HASH_SRC) -o $(DIST)/test-hhs-vm81-game-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-vm81-game-sanitized
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(CORE_SRC) $(RELEASE_SRC) tests/test_hhs_vm81_game_release.c $(HASH_SRC) -o $(DIST)/test-hhs-vm81-game-release-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-vm81-game-release-sanitized

verify: test sanitize

clean:
	rm -rf $(DIST)
