CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -Wno-unused-function -pedantic
ROOT := ../..
GAME := ../hhs_vm81_game_level10
INCLUDES := -Iinclude -I$(GAME)/include -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
GAME_CORE := $(GAME)/src/hhs_vm81_game.c
GAME_RELEASE := $(GAME)/src/hhs_vm81_game_release.c
GAME_SPRITE := $(GAME)/src/hhs_vm81_game_sprite.c
GAME_TEXTURE := $(GAME)/src/hhs_vm81_game_texture.c
STORY_SRC := src/hhs_storybook_reel_serial.c src/hhs_storybook_reel_style_v2.c
DIST := dist
LIB := $(DIST)/libhhs_storybook_reel.so
CLI := $(DIST)/hhs-storybook-reel
TEST := $(DIST)/test-hhs-storybook-reel

.PHONY: all test sanitize clean

all: $(LIB) $(CLI) $(TEST)

$(DIST):
	mkdir -p $(DIST)

$(LIB): $(STORY_SRC) src/hhs_storybook_reel.c include/hhs_storybook_reel.h include/hhs_storybook_reel_style_v2.h \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) $(HASH_SRC) -o $@

$(CLI): $(STORY_SRC) src/hhs_storybook_reel.c src/hhs_storybook_reel_cli.c src/hhs_storybook_reel_cli_v2.c include/hhs_storybook_reel.h include/hhs_storybook_reel_style_v2.h \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) src/hhs_storybook_reel_cli_v2.c $(HASH_SRC) -o $@

$(TEST): $(STORY_SRC) src/hhs_storybook_reel.c tests/test_hhs_storybook_reel.c include/hhs_storybook_reel.h include/hhs_storybook_reel_style_v2.h \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) tests/test_hhs_storybook_reel.c $(HASH_SRC) -o $@

test: all
	$(TEST)

sanitize: | $(DIST)
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -Wno-unused-function -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) tests/test_hhs_storybook_reel.c $(HASH_SRC) \
		-o $(DIST)/test-hhs-storybook-reel-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 \
		$(DIST)/test-hhs-storybook-reel-sanitized

clean:
	rm -rf $(DIST)
