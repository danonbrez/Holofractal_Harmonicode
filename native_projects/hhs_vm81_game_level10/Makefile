CC ?= cc
PYTHON ?= python3
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Werror -pedantic
ROOT := ../..
INCLUDES := -Iinclude -I$(ROOT)/hhs_runtime/include
HASH_SRC := $(ROOT)/hhs_runtime/src/hhs_hash216.c
CORE_SRC := src/hhs_vm81_game.c
RELEASE_SRC := src/hhs_vm81_game_release.c
SPRITE_SRC := src/hhs_vm81_game_sprite.c
TEXTURE_SRC := src/hhs_vm81_game_texture.c
SRC_PARTS := src/hhs_vm81_game_part_00.inc src/hhs_vm81_game_part_01.inc src/hhs_vm81_game_part_02.inc
DIST := dist

.PHONY: all play test sanitize terminal-io capture modality sprite-capture sprite-modality texture-capture texture-modality holographic-playback holographic-modality clean verify

all: $(DIST)/hhs-vm81-game $(DIST)/test-hhs-vm81-game \
	$(DIST)/hhs-vm81-platformer $(DIST)/test-hhs-vm81-game-release \
	$(DIST)/hhs-vm81-sprite-capture $(DIST)/test-hhs-vm81-game-sprite \
	$(DIST)/hhs-vm81-texture-capture $(DIST)/test-hhs-vm81-game-texture

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

$(DIST)/hhs-vm81-sprite-capture: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) $(SPRITE_SRC) src/hhs_vm81_game_sprite_capture_cli.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h include/hhs_vm81_game_sprite.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) src/hhs_vm81_game_sprite_capture_cli.c $(HASH_SRC) -o $@

$(DIST)/test-hhs-vm81-game-sprite: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) $(SPRITE_SRC) tests/test_hhs_vm81_game_sprite.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h include/hhs_vm81_game_sprite.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) tests/test_hhs_vm81_game_sprite.c $(HASH_SRC) -o $@

$(DIST)/hhs-vm81-texture-capture: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) $(SPRITE_SRC) $(TEXTURE_SRC) src/hhs_vm81_game_texture_capture_cli.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h include/hhs_vm81_game_sprite.h include/hhs_vm81_game_texture.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) $(TEXTURE_SRC) src/hhs_vm81_game_texture_capture_cli.c $(HASH_SRC) -o $@

$(DIST)/test-hhs-vm81-game-texture: $(CORE_SRC) $(SRC_PARTS) $(RELEASE_SRC) $(SPRITE_SRC) $(TEXTURE_SRC) tests/test_hhs_vm81_game_texture.c include/hhs_vm81_game.h include/hhs_vm81_game_release.h include/hhs_vm81_game_sprite.h include/hhs_vm81_game_texture.h $(HASH_SRC) | $(DIST)
	$(CC) $(CFLAGS) $(INCLUDES) $(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) $(TEXTURE_SRC) tests/test_hhs_vm81_game_texture.c $(HASH_SRC) -o $@

play: $(DIST)/hhs-vm81-platformer
	$(DIST)/hhs-vm81-platformer

test: all
	$(DIST)/test-hhs-vm81-game
	$(DIST)/test-hhs-vm81-game-release
	$(DIST)/test-hhs-vm81-game-sprite > $(DIST)/sprite-verification.txt
	$(DIST)/test-hhs-vm81-game-texture > $(DIST)/texture-verification.txt
	$(DIST)/hhs-vm81-game > $(DIST)/verification.json
	$(DIST)/hhs-vm81-platformer --headless > $(DIST)/playable-verification.json
	grep -q 'VM81_C_ABI_19_OPCODE_2D_PLATFORM_DEMO_VERIFIED' $(DIST)/verification.json
	grep -q 'VM81_PLAYABLE_GAME_RELEASE_VERIFIED' $(DIST)/playable-verification.json
	grep -q 'VM81_SPRITE_MAP_OVERLAY_GRADIENTS_VERIFIED' $(DIST)/sprite-verification.txt
	grep -q 'VM81_GOVERNED_TEXTURE_LAYER_FOUNDATION_VERIFIED' $(DIST)/texture-verification.txt
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
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) tests/test_hhs_vm81_game_sprite.c $(HASH_SRC) -o $(DIST)/test-hhs-vm81-game-sprite-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-vm81-game-sprite-sanitized
	$(CC) -std=c11 -O1 -g -Wall -Wextra -Werror -pedantic \
		-fsanitize=address,undefined -fno-omit-frame-pointer $(INCLUDES) \
		$(CORE_SRC) $(RELEASE_SRC) $(SPRITE_SRC) $(TEXTURE_SRC) tests/test_hhs_vm81_game_texture.c $(HASH_SRC) -o $(DIST)/test-hhs-vm81-game-texture-sanitized
	ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 UBSAN_OPTIONS=halt_on_error=1 $(DIST)/test-hhs-vm81-game-texture-sanitized

terminal-io: $(DIST)/hhs-vm81-platformer
	rm -rf $(DIST)/terminal-io
	$(PYTHON) tools/verify_terminal_io.py --binary $(DIST)/hhs-vm81-platformer --output $(DIST)/terminal-io > $(DIST)/terminal-io-evidence.log
	test -s $(DIST)/terminal-io/terminal-session.ansi
	test -s $(DIST)/terminal-io/terminal-session.txt
	test -s $(DIST)/terminal-io/terminal-io-evidence.json
	grep -q 'VM81_TERMINAL_IO_MODALITY_VERIFIED' $(DIST)/terminal-io/terminal-io-evidence.json
	grep -q '"terminal_restored": "VERIFIED"' $(DIST)/terminal-io/terminal-io-evidence.json

capture: $(DIST)/hhs-vm81-platformer
	command -v ffmpeg >/dev/null
	command -v ffprobe >/dev/null
	$(PYTHON) -c 'import PIL'
	rm -rf $(DIST)/capture $(DIST)/media
	mkdir -p $(DIST)/capture
	$(DIST)/hhs-vm81-platformer --capture-frames $(DIST)/capture > $(DIST)/capture-command.json
	$(PYTHON) tools/render_terminal_capture.py --input $(DIST)/capture --output $(DIST)/media > $(DIST)/modality-evidence.log

modality: terminal-io capture
	test -s $(DIST)/capture/capture-trace.json
	test -s $(DIST)/media/screenshots/00-overview.png
	test -s $(DIST)/media/screenshots/01-title.png
	test -s $(DIST)/media/screenshots/02-checkpoint-one.png
	test -s $(DIST)/media/screenshots/03-checkpoint-two.png
	test -s $(DIST)/media/screenshots/04-victory.png
	test -s $(DIST)/media/vm81-platformer-playthrough.mp4
	test -s $(DIST)/media/modality-evidence.json
	grep -q 'VM81_TERMINAL_FRAME_STREAM_CAPTURED' $(DIST)/capture/capture-trace.json
	grep -q 'VM81_USER_MODALITY_PRESENTATION_EVIDENCE_VERIFIED' $(DIST)/media/modality-evidence.json
	grep -q '"screenshots": "VERIFIED"' $(DIST)/media/modality-evidence.json
	grep -q '"mp4": "VERIFIED"' $(DIST)/media/modality-evidence.json
	grep -q '"replay": "MATCH"' $(DIST)/media/modality-evidence.json
	grep -q '"opcode_coverage": "19/19"' $(DIST)/media/modality-evidence.json

sprite-capture: $(DIST)/hhs-vm81-sprite-capture
	command -v ffmpeg >/dev/null
	command -v ffprobe >/dev/null
	$(PYTHON) -c 'import PIL'
	rm -rf $(DIST)/sprite-capture $(DIST)/sprite-media
	mkdir -p $(DIST)/sprite-capture
	$(DIST)/hhs-vm81-sprite-capture $(DIST)/sprite-capture > $(DIST)/sprite-capture-command.json
	$(PYTHON) tools/render_sprite_capture.py --input $(DIST)/sprite-capture --output $(DIST)/sprite-media > $(DIST)/sprite-modality.log

sprite-modality: sprite-capture
	test -s $(DIST)/sprite-capture/sprite-capture-trace.json
	test -s $(DIST)/sprite-capture/layers/layer-manifest.json
	test -s $(DIST)/sprite-media/screenshots/00-sprite-gradient-overview.png
	test -s $(DIST)/sprite-media/screenshots/01-title.png
	test -s $(DIST)/sprite-media/screenshots/02-checkpoint-one.png
	test -s $(DIST)/sprite-media/screenshots/03-checkpoint-two.png
	test -s $(DIST)/sprite-media/screenshots/04-victory.png
	test -s $(DIST)/sprite-media/screenshots/05-overlay-gradient-layers.png
	test -s $(DIST)/sprite-media/vm81-platformer-sprite-gradients.mp4
	test -s $(DIST)/sprite-media/sprite-modality-evidence.json
	grep -q 'VM81_SPRITE_MAP_OVERLAY_GRADIENTS_CAPTURED' $(DIST)/sprite-capture/sprite-capture-trace.json
	grep -q 'VM81_SPRITE_OVERLAY_LAYER_COMPARISON_CAPTURED' $(DIST)/sprite-capture/layers/layer-manifest.json
	grep -q 'VM81_SPRITE_MAP_OVERLAY_GRADIENTS_PRESENTATION_VERIFIED' $(DIST)/sprite-media/sprite-modality-evidence.json
	grep -q '"state_projection_non_mutating": "VERIFIED"' $(DIST)/sprite-media/sprite-modality-evidence.json
	grep -q '"replay": "MATCH"' $(DIST)/sprite-media/sprite-modality-evidence.json
	grep -q '"opcode_coverage": "19/19"' $(DIST)/sprite-media/sprite-modality-evidence.json

texture-capture: $(DIST)/hhs-vm81-texture-capture
	command -v ffmpeg >/dev/null
	command -v ffprobe >/dev/null
	$(PYTHON) -c 'import PIL'
	rm -rf $(DIST)/texture-capture $(DIST)/texture-media
	mkdir -p $(DIST)/texture-capture
	$(DIST)/hhs-vm81-texture-capture $(DIST)/texture-capture > $(DIST)/texture-capture-command.json
	$(PYTHON) tools/render_texture_capture.py --input $(DIST)/texture-capture --output $(DIST)/texture-media > $(DIST)/texture-modality.log

texture-modality: texture-capture
	test -s $(DIST)/texture-capture/texture-capture-trace.json
	test -s $(DIST)/texture-capture/layers/layer-manifest.json
	test -s $(DIST)/texture-media/screenshots/00-texture-layer-overview.png
	test -s $(DIST)/texture-media/screenshots/01-title.png
	test -s $(DIST)/texture-media/screenshots/02-checkpoint-one.png
	test -s $(DIST)/texture-media/screenshots/03-checkpoint-two.png
	test -s $(DIST)/texture-media/screenshots/04-victory.png
	test -s $(DIST)/texture-media/screenshots/05-governed-texture-layers.png
	test -s $(DIST)/texture-media/screenshots/06-texture-detail-crops.png
	test -s $(DIST)/texture-media/vm81-platformer-governed-textures.mp4
	test -s $(DIST)/texture-media/texture-modality-evidence.json
	grep -q 'VM81_GOVERNED_TEXTURE_LAYER_FRAME_STREAM_CAPTURED' $(DIST)/texture-capture/texture-capture-trace.json
	grep -q 'VM81_GOVERNED_TEXTURE_LAYER_COMPARISON_CAPTURED' $(DIST)/texture-capture/layers/layer-manifest.json
	grep -q 'VM81_GOVERNED_TEXTURE_LAYER_PRESENTATION_VERIFIED' $(DIST)/texture-media/texture-modality-evidence.json
	grep -q '"state_projection_non_mutating": "VERIFIED"' $(DIST)/texture-media/texture-modality-evidence.json
	grep -q '"inherited_sprite_projection": "UNCHANGED"' $(DIST)/texture-media/texture-modality-evidence.json
	grep -q '"replay": "MATCH"' $(DIST)/texture-media/texture-modality-evidence.json
	grep -q '"opcode_coverage": "19/19"' $(DIST)/texture-media/texture-modality-evidence.json

holographic-playback:
	command -v ffmpeg >/dev/null
	command -v ffprobe >/dev/null
	$(PYTHON) -c 'import PIL'
	@if ! test -s $(DIST)/texture-capture/texture-capture-trace.json || ! ls $(DIST)/texture-capture/frame_*.ppm >/dev/null 2>&1; then \
		$(MAKE) texture-modality; \
	fi
	rm -rf $(DIST)/holographic-media
	$(PYTHON) tools/render_holographic_playback.py --input $(DIST)/texture-capture --output $(DIST)/holographic-media > $(DIST)/holographic-modality.log

holographic-modality: holographic-playback
	test -s $(DIST)/holographic-media/vm81-holographic-overlay.mp4
	test -s $(DIST)/holographic-media/vm81-platformer-holographic-playback.mp4
	test -s $(DIST)/holographic-media/screenshots/00-holographic-playback-overview.png
	test -s $(DIST)/holographic-media/screenshots/05-mp4-holographic-overlay-stages.png
	test -s $(DIST)/holographic-media/screenshots/06-holographic-depth-lighting-details.png
	test -s $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q 'VM81_MP4_HOLOGRAPHIC_OVERLAY_GENERATED' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q 'VM81_MP4_HOLOGRAPHIC_PLAYBACK_ROUNDTRIP_VERIFIED' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q 'VM81_HOLOGRAPHIC_DEPTH_LIGHTING_COMPOSITE_VERIFIED' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q '"mp4_playback_pixel_exact": "VERIFIED"' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q '"base_texture_frames_unchanged": "VERIFIED"' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q '"vm81_state_mutation": "NONE"' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q '"opcode_coverage": "19/19"' $(DIST)/holographic-media/holographic-playback-evidence.json
	grep -q '"replay": "MATCH"' $(DIST)/holographic-media/holographic-playback-evidence.json

verify: test sanitize modality sprite-modality texture-modality holographic-modality

clean:
	rm -rf $(DIST)
