#include "hhs_vm81_game_release.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#define HHS_RELEASE_HAZARD_Y_PX 120
#define HHS_RELEASE_RESTORE_FRAME_LIMIT 768U

static int hhs_release_append(char* out, size_t capacity, size_t* used, const char* format, ...) {
    va_list args;
    int written;
    if (!out || !used || !format || *used >= capacity) return 0;
    va_start(args, format);
    written = vsnprintf(out + *used, capacity - *used, format, args);
    va_end(args);
    if (written < 0 || (size_t)written >= capacity - *used) return 0;
    *used += (size_t)written;
    return 1;
}

static int hhs_release_x_overlap(int32_t player_x_px, int32_t left_px, int32_t right_px) {
    int32_t player_right_px = player_x_px + HHS_VM81_GAME_PLAYER_WIDTH;
    return player_right_px > left_px && player_x_px < right_px;
}

static int hhs_release_is_hazard(const HHSVM81GameRelease* release) {
    static const int32_t hazard_ranges[][2] = {
        {13 * HHS_VM81_GAME_TILE_SIZE, 14 * HHS_VM81_GAME_TILE_SIZE},
        {27 * HHS_VM81_GAME_TILE_SIZE, 28 * HHS_VM81_GAME_TILE_SIZE},
        {41 * HHS_VM81_GAME_TILE_SIZE, 42 * HHS_VM81_GAME_TILE_SIZE}
    };
    int32_t player_x_px;
    int32_t player_bottom_px;
    size_t i;
    if (!release) return 0;
    player_x_px = release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS;
    player_bottom_px = release->vm.player.y_subpx / HHS_VM81_GAME_SUBPIXELS + HHS_VM81_GAME_PLAYER_HEIGHT;
    if (player_bottom_px < HHS_RELEASE_HAZARD_Y_PX) return 0;
    for (i = 0U; i < sizeof(hazard_ranges) / sizeof(hazard_ranges[0]); ++i) {
        if (hhs_release_x_overlap(player_x_px, hazard_ranges[i][0], hazard_ranges[i][1])) return 1;
    }
    return 0;
}

static int hhs_release_tile_is_hazard(int tile_x, int tile_y) {
    if (tile_y != 15) return 0;
    return (tile_x >= 13 && tile_x < 14) ||
           (tile_x >= 27 && tile_x < 28) ||
           (tile_x >= 41 && tile_x < 42);
}

static HHSVM81GameStatus hhs_release_execute_current_instruction(HHSVM81GameRelease* release) {
    HHSVM81GameRequest request;
    HHSVM81GameResult result;
    HHSVM81GameStatus status;
    if (!release || release->vm.halted || release->vm.pc >= HHS_VM81_GAME_PROGRAM_LENGTH) {
        return HHS_GAME_STATUS_PROGRAM_BOUNDS;
    }
    memset(&request, 0, sizeof(request));
    request.struct_size = (uint32_t)sizeof(request);
    request.abi_version = HHS_VM81_GAME_ABI_VERSION;
    request.authority_admission = HHS_VM81_GAME_AUTHORITY_ADMITTED;
    request.expected_generation = release->vm.generation;
    request.expected_step = release->vm.step;
    request.instruction = release->vm.program[release->vm.pc];
    status = hhs_vm81_game_execute(&release->vm, &request, &result);
    if (status == HHS_GAME_STATUS_OK) release->instructions_executed++;
    return status;
}

static HHSVM81GameStatus hhs_release_execute_frame(HHSVM81GameRelease* release, uint8_t input_bits) {
    uint64_t start_frame;
    uint32_t guard = 0U;
    if (!release) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->vm.frame >= release->vm.input_count || release->vm.halted) return HHS_GAME_STATUS_PROGRAM_BOUNDS;
    start_frame = release->vm.frame;
    release->vm.input_trace[start_frame] = input_bits;
    while (!release->vm.halted && release->vm.frame == start_frame) {
        HHSVM81GameStatus status;
        if (guard >= HHS_VM81_GAME_MAX_PROGRAM_STEPS) return HHS_GAME_STATUS_PROGRAM_BOUNDS;
        status = hhs_release_execute_current_instruction(release);
        if (status != HHS_GAME_STATUS_OK) return status;
        guard++;
    }
    return HHS_GAME_STATUS_OK;
}

static HHSVM81GameStatus hhs_release_close_vm(HHSVM81GameRelease* release) {
    HHSVM81GameStatus status;
    while (!release->vm.halted) {
        if (release->vm.frame < release->vm.input_count) {
            status = hhs_release_execute_frame(release, 0U);
        } else {
            status = hhs_release_execute_current_instruction(release);
        }
        if (status != HHS_GAME_STATUS_OK) return status;
    }
    return HHS_GAME_STATUS_OK;
}

static HHSVM81GameStatus hhs_release_restore_checkpoint(HHSVM81GameRelease* release) {
    HHSVM81GameStatus status;
    uint32_t restore_frames = 0U;
    if (!release) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_reset(&release->vm);
    if (status != HHS_GAME_STATUS_OK) return status;
    while ((uint32_t)(release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS) < release->checkpoint_x_px) {
        if (restore_frames >= HHS_RELEASE_RESTORE_FRAME_LIMIT || release->vm.frame >= release->vm.input_count) {
            return HHS_GAME_STATUS_PROGRAM_BOUNDS;
        }
        status = hhs_release_execute_frame(
            release,
            (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)
        );
        if (status != HHS_GAME_STATUS_OK) return status;
        restore_frames++;
    }
    release->event = HHS_GAME_RELEASE_EVENT_RESPAWN;
    return HHS_GAME_STATUS_OK;
}

static void hhs_release_fill_report(const HHSVM81GameRelease* release, HHSVM81GameReleaseReport* report, HHSVM81GameStatus status) {
    memset(report, 0, sizeof(*report));
    report->status = (uint32_t)status;
    report->phase = release->phase;
    report->lives = release->lives;
    report->deaths = release->deaths;
    report->checkpoint = release->checkpoint;
    report->player_frames = release->player_frames;
    report->instructions_executed = release->instructions_executed;
    report->opcode_coverage = release->vm.opcode_coverage;
    report->receipts_emitted = release->vm.receipt_count;
    report->final_player = release->vm.player;
    report->final_receipt_hash72 = release->vm.latest_receipt_hash72;
    report->final_state_identity_hash216 = release->vm.latest_state_identity_hash216;
}

const char* hhs_vm81_game_release_phase_name(uint32_t phase) {
    switch (phase) {
        case HHS_GAME_RELEASE_TITLE: return "TITLE";
        case HHS_GAME_RELEASE_RUNNING: return "RUNNING";
        case HHS_GAME_RELEASE_PAUSED: return "PAUSED";
        case HHS_GAME_RELEASE_VICTORY: return "VICTORY";
        case HHS_GAME_RELEASE_GAME_OVER: return "GAME_OVER";
        case HHS_GAME_RELEASE_QUIT: return "QUIT";
        default: return "INVALID";
    }
}

HHSVM81GameStatus hhs_vm81_game_release_init(HHSVM81GameRelease* release) {
    uint8_t trace[HHS_VM81_GAME_MAX_INPUT_FRAMES];
    HHSVM81GameStatus status;
    if (!release) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    memset(trace, 0, sizeof(trace));
    memset(release, 0, sizeof(*release));
    status = hhs_vm81_game_init(&release->vm, trace, HHS_VM81_GAME_MAX_INPUT_FRAMES);
    if (status != HHS_GAME_STATUS_OK) return status;
    release->release_version = HHS_VM81_GAME_RELEASE_VERSION;
    release->phase = HHS_GAME_RELEASE_TITLE;
    release->event = HHS_GAME_RELEASE_EVENT_NONE;
    release->lives = HHS_VM81_GAME_RELEASE_INITIAL_LIVES;
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_release_start(HHSVM81GameRelease* release) {
    if (!release || release->release_version != HHS_VM81_GAME_RELEASE_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->phase == HHS_GAME_RELEASE_TITLE || release->phase == HHS_GAME_RELEASE_PAUSED) {
        release->phase = HHS_GAME_RELEASE_RUNNING;
        release->event = HHS_GAME_RELEASE_EVENT_STARTED;
        return HHS_GAME_STATUS_OK;
    }
    return release->phase == HHS_GAME_RELEASE_RUNNING ? HHS_GAME_STATUS_OK : HHS_GAME_STATUS_INVALID_OPERAND;
}

HHSVM81GameStatus hhs_vm81_game_release_pause_toggle(HHSVM81GameRelease* release) {
    if (!release || release->release_version != HHS_VM81_GAME_RELEASE_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->phase == HHS_GAME_RELEASE_RUNNING) {
        release->phase = HHS_GAME_RELEASE_PAUSED;
        release->event = HHS_GAME_RELEASE_EVENT_PAUSED;
        return HHS_GAME_STATUS_OK;
    }
    if (release->phase == HHS_GAME_RELEASE_PAUSED) {
        release->phase = HHS_GAME_RELEASE_RUNNING;
        release->event = HHS_GAME_RELEASE_EVENT_RESUMED;
        return HHS_GAME_STATUS_OK;
    }
    return HHS_GAME_STATUS_INVALID_OPERAND;
}

HHSVM81GameStatus hhs_vm81_game_release_restart(HHSVM81GameRelease* release) {
    HHSVM81GameStatus status;
    if (!release || release->release_version != HHS_VM81_GAME_RELEASE_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_reset(&release->vm);
    if (status != HHS_GAME_STATUS_OK) return status;
    release->phase = HHS_GAME_RELEASE_RUNNING;
    release->event = HHS_GAME_RELEASE_EVENT_RESET;
    release->lives = HHS_VM81_GAME_RELEASE_INITIAL_LIVES;
    release->deaths = 0U;
    release->checkpoint = 0U;
    release->checkpoint_x_px = 0U;
    release->player_frames = 0U;
    release->instructions_executed = 0U;
    release->input_log_count = 0U;
    release->last_input = 0U;
    memset(release->input_log, 0, sizeof(release->input_log));
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_release_quit(HHSVM81GameRelease* release) {
    if (!release || release->release_version != HHS_VM81_GAME_RELEASE_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    release->phase = HHS_GAME_RELEASE_QUIT;
    release->event = HHS_GAME_RELEASE_EVENT_QUIT;
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_release_step(HHSVM81GameRelease* release, uint8_t input_bits) {
    HHSVM81GameStatus status;
    uint32_t player_x_px;
    uint32_t new_checkpoint = 0U;
    const uint8_t allowed = (uint8_t)(HHS_VM81_GAME_INPUT_LEFT | HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP | HHS_VM81_GAME_INPUT_RESET);
    if (!release || release->release_version != HHS_VM81_GAME_RELEASE_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->phase != HHS_GAME_RELEASE_RUNNING) return HHS_GAME_STATUS_INVALID_OPERAND;
    if ((input_bits & (uint8_t)~allowed) != 0U) return HHS_GAME_STATUS_INVALID_OPERAND;
    if ((input_bits & HHS_VM81_GAME_INPUT_RESET) != 0U) return hhs_vm81_game_release_restart(release);
    if (release->input_log_count >= HHS_VM81_GAME_MAX_INPUT_FRAMES) return HHS_GAME_STATUS_PROGRAM_BOUNDS;

    release->last_input = input_bits;
    release->input_log[release->input_log_count++] = input_bits;
    status = hhs_release_execute_frame(release, input_bits);
    if (status != HHS_GAME_STATUS_OK) return status;
    release->player_frames++;
    release->event = HHS_GAME_RELEASE_EVENT_FRAME;

    player_x_px = (uint32_t)(release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS);
    if (player_x_px >= 320U) new_checkpoint = 2U;
    else if (player_x_px >= 160U) new_checkpoint = 1U;
    if (new_checkpoint > release->checkpoint) {
        release->checkpoint = new_checkpoint;
        release->checkpoint_x_px = new_checkpoint == 1U ? 160U : 320U;
        release->event = HHS_GAME_RELEASE_EVENT_CHECKPOINT;
    }

    if (player_x_px >= HHS_VM81_GAME_RELEASE_GOAL_X_PX) {
        release->phase = HHS_GAME_RELEASE_VICTORY;
        release->event = HHS_GAME_RELEASE_EVENT_VICTORY;
        status = hhs_release_close_vm(release);
        return status;
    }

    if (hhs_release_is_hazard(release)) {
        release->deaths++;
        release->event = HHS_GAME_RELEASE_EVENT_DEATH;
        if (release->lives > 0U) release->lives--;
        if (release->lives == 0U) {
            release->phase = HHS_GAME_RELEASE_GAME_OVER;
            return HHS_GAME_STATUS_OK;
        }
        status = hhs_release_restore_checkpoint(release);
        if (status != HHS_GAME_STATUS_OK) return status;
    }
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_release_run_headless(HHSVM81GameRelease* release, HHSVM81GameReleaseReport* report) {
    HHSVM81GameStatus status;
    uint32_t guard = 0U;
    if (!release || !report) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (release->phase == HHS_GAME_RELEASE_TITLE) {
        status = hhs_vm81_game_release_start(release);
        if (status != HHS_GAME_STATUS_OK) return status;
    }
    while (release->phase == HHS_GAME_RELEASE_RUNNING && guard < HHS_VM81_GAME_MAX_INPUT_FRAMES) {
        status = hhs_vm81_game_release_step(
            release,
            (uint8_t)(HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP)
        );
        if (status != HHS_GAME_STATUS_OK) {
            hhs_release_fill_report(release, report, status);
            return status;
        }
        guard++;
    }
    status = release->phase == HHS_GAME_RELEASE_VICTORY ? HHS_GAME_STATUS_OK : HHS_GAME_STATUS_PROGRAM_BOUNDS;
    hhs_release_fill_report(release, report, status);
    return status;
}

HHSVM81GameStatus hhs_vm81_game_release_replay_verify(const HHSVM81GameRelease* expected, HHSVM81GameReleaseReport* actual) {
    HHSVM81GameRelease replay;
    HHSVM81GameStatus status;
    uint32_t i;
    if (!expected || !actual || expected->input_log_count == 0U) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_release_init(&replay);
    if (status != HHS_GAME_STATUS_OK) return status;
    status = hhs_vm81_game_release_start(&replay);
    if (status != HHS_GAME_STATUS_OK) return status;
    for (i = 0U; i < expected->input_log_count && replay.phase == HHS_GAME_RELEASE_RUNNING; ++i) {
        status = hhs_vm81_game_release_step(&replay, expected->input_log[i]);
        if (status != HHS_GAME_STATUS_OK) return status;
    }
    hhs_release_fill_report(&replay, actual, HHS_GAME_STATUS_OK);
    if (expected->phase != replay.phase ||
        expected->lives != replay.lives ||
        expected->deaths != replay.deaths ||
        expected->checkpoint != replay.checkpoint ||
        expected->player_frames != replay.player_frames ||
        expected->instructions_executed != replay.instructions_executed ||
        expected->vm.opcode_coverage != replay.vm.opcode_coverage ||
        expected->vm.receipt_count != replay.vm.receipt_count ||
        expected->vm.player.x_subpx != replay.vm.player.x_subpx ||
        expected->vm.player.y_subpx != replay.vm.player.y_subpx ||
        expected->vm.player.vx_subpx != replay.vm.player.vx_subpx ||
        expected->vm.player.vy_subpx != replay.vm.player.vy_subpx ||
        !hhs_hash72_equal(&expected->vm.latest_receipt_hash72, &replay.vm.latest_receipt_hash72) ||
        !hhs_hash216_equal(&expected->vm.latest_state_identity_hash216, &replay.vm.latest_state_identity_hash216)) {
        actual->status = HHS_GAME_STATUS_REPLAY_MISMATCH;
        return HHS_GAME_STATUS_REPLAY_MISMATCH;
    }
    return HHS_GAME_STATUS_OK;
}

size_t hhs_vm81_game_release_render_ascii(const HHSVM81GameRelease* release, char* out, size_t capacity) {
    size_t used = 0U;
    uint32_t camera_tile;
    int player_tile_x;
    int player_tile_y;
    int view_y;
    if (!release || !out || capacity == 0U) return 0U;
    out[0] = '\0';
    camera_tile = release->vm.camera_x_px / HHS_VM81_GAME_TILE_SIZE;
    player_tile_x = release->vm.player.x_subpx / HHS_VM81_GAME_SUBPIXELS / HHS_VM81_GAME_TILE_SIZE;
    player_tile_y = release->vm.player.y_subpx / HHS_VM81_GAME_SUBPIXELS / HHS_VM81_GAME_TILE_SIZE;
    if (!hhs_release_append(out, capacity, &used,
            "HHS VM81 PLATFORMER  phase=%s  lives=%u  deaths=%u  checkpoint=%u/2  frame=%u\n",
            hhs_vm81_game_release_phase_name(release->phase), release->lives, release->deaths,
            release->checkpoint, release->player_frames)) return 0U;
    if (!hhs_release_append(out, capacity, &used, "+--------------------+\n")) return 0U;
    for (view_y = 0; view_y < HHS_VM81_GAME_VIEW_TILES_Y; ++view_y) {
        int view_x;
        if (!hhs_release_append(out, capacity, &used, "|")) return 0U;
        for (view_x = 0; view_x < HHS_VM81_GAME_VIEW_TILES_X; ++view_x) {
            int world_x = (int)camera_tile + view_x;
            int world_y = view_y;
            char glyph = ' ';
            if (world_x >= 0 && world_x < HHS_VM81_GAME_LEVEL_TILES_X &&
                release->vm.level[world_y][world_x] != 0U) glyph = '#';
            if (hhs_release_tile_is_hazard(world_x, world_y)) glyph = '^';
            if (world_y == 15 && (world_x == 20 || world_x == 40)) glyph = 'C';
            if (world_y == 14 && world_x == 61) glyph = 'G';
            if (world_x == player_tile_x && world_y == player_tile_y) glyph = '@';
            if (!hhs_release_append(out, capacity, &used, "%c", glyph)) return 0U;
        }
        if (!hhs_release_append(out, capacity, &used, "|\n")) return 0U;
    }
    if (!hhs_release_append(out, capacity, &used,
            "+--------------------+\nA/D move  SPACE/W jump  P pause  R restart  Q quit\n")) return 0U;
    return used;
}
