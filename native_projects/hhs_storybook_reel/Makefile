CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -Wno-unused-function -pedantic
ROOT := ../..
SIBLING_GAME := ../hhs_vm81_game_level10
VENDORED_GAME := src/hhs_vm81_game_level10
GAME ?= $(if $(wildcard $(SIBLING_GAME)/src/hhs_vm81_game.c),$(SIBLING_GAME),$(if $(wildcard $(VENDORED_GAME)/src/hhs_vm81_game.c),$(VENDORED_GAME),.))
GAME_SRC_DIR := $(if $(wildcard $(GAME)/src/hhs_vm81_game.c),$(GAME)/src,src)
GAME_INCLUDE_DIR := $(if $(wildcard $(GAME)/include/hhs_vm81_game.h),$(GAME)/include,include)
INCLUDES := -Iinclude -I$(GAME_INCLUDE_DIR) -I$(GAME_SRC_DIR) -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
GAME_CORE := $(GAME_SRC_DIR)/hhs_vm81_game.c
GAME_RELEASE := $(GAME_SRC_DIR)/hhs_vm81_game_release.c
GAME_SPRITE := $(GAME_SRC_DIR)/hhs_vm81_game_sprite.c
GAME_TEXTURE := $(GAME_SRC_DIR)/hhs_vm81_game_texture.c
STORY_SRC := \
	src/hhs_storybook_reel_serial.c \
	src/hhs_storybook_reel_style_v2.c \
	src/hhs_storybook_reel_projection_v2.c
STORY_HEADERS := \
	include/hhs_storybook_reel.h \
	include/hhs_storybook_reel_style_v2.h \
	include/hhs_storybook_reel_projection_v2.h
DIST := dist
LIB := $(DIST)/libhhs_storybook_reel.so
CLI := $(DIST)/hhs-storybook-reel
TEST := $(DIST)/test-hhs-storybook-reel
PROJECTION_TEST := $(DIST)/test-hhs-storybook-projection-v2

ifeq ($(wildcard $(GAME_CORE)),)
$(error VM81 game sources not found. Expected sibling $(SIBLING_GAME), vendored $(VENDORED_GAME), or direct files under src/)
endif

.PHONY: all test test-projection sanitize clean print-source-layout

print-source-layout:
	@printf 'GAME=%s\nGAME_SRC_DIR=%s\nGAME_INCLUDE_DIR=%s\n' "$(GAME)" "$(GAME_SRC_DIR)" "$(GAME_INCLUDE_DIR)"

all: $(LIB) $(CLI) $(TEST) $(PROJECTION_TEST)

$(DIST):
	mkdir -p $(DIST)

$(LIB): $(STORY_SRC) $(STORY_HEADERS) $(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) -fPIC -shared $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) $(HASH_SRC) -o $@

$(CLI): $(STORY_SRC) src/hhs_storybook_reel_cli.c src/hhs_storybook_reel_cli_v2.c $(STORY_HEADERS) \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) src/hhs_storybook_reel_cli_v2.c $(HASH_SRC) -o $@

$(TEST): $(STORY_SRC) tests/test_hhs_storybook_reel.c $(STORY_HEADERS) \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		$(STORY_SRC) tests/test_hhs_storybook_reel.c $(HASH_SRC) -o $@

$(PROJECTION_TEST): src/hhs_storybook_reel_projection_v2.c tests/test_hhs_storybook_projection_v2.c $(STORY_HEADERS) \
	$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) \
		$(GAME_CORE) $(GAME_RELEASE) $(GAME_SPRITE) $(GAME_TEXTURE) \
		src/hhs_storybook_reel_projection_v2.c tests/test_hhs_storybook_projection_v2.c $(HASH_SRC) -o $@

test: all
	$(TEST)
	$(PROJECTION_TEST)

test-projection: $(PROJECTION_TEST)
	$(PROJECTION_TEST)

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
