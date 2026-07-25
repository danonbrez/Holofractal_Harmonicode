#ifndef HHS_VM81_GAME_RELEASE_H
#define HHS_VM81_GAME_RELEASE_H

#include "hhs_vm81_game.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_VM81_GAME_RELEASE_VERSION 1U
#define HHS_VM81_GAME_RELEASE_INITIAL_LIVES 3U
#define HHS_VM81_GAME_RELEASE_CHECKPOINTS 2U
#define HHS_VM81_GAME_RELEASE_GOAL_X_PX 480U
#define HHS_VM81_GAME_RELEASE_MAX_RENDER_BYTES 8192U

typedef enum HHSVM81GameReleasePhase {
    HHS_GAME_RELEASE_TITLE = 0,
    HHS_GAME_RELEASE_RUNNING = 1,
    HHS_GAME_RELEASE_PAUSED = 2,
    HHS_GAME_RELEASE_VICTORY = 3,
    HHS_GAME_RELEASE_GAME_OVER = 4,
    HHS_GAME_RELEASE_QUIT = 5
} HHSVM81GameReleasePhase;

typedef enum HHSVM81GameReleaseEvent {
    HHS_GAME_RELEASE_EVENT_NONE = 0,
    HHS_GAME_RELEASE_EVENT_STARTED = 1,
    HHS_GAME_RELEASE_EVENT_FRAME = 2,
    HHS_GAME_RELEASE_EVENT_PAUSED = 3,
    HHS_GAME_RELEASE_EVENT_RESUMED = 4,
    HHS_GAME_RELEASE_EVENT_CHECKPOINT = 5,
    HHS_GAME_RELEASE_EVENT_DEATH = 6,
    HHS_GAME_RELEASE_EVENT_RESPAWN = 7,
    HHS_GAME_RELEASE_EVENT_VICTORY = 8,
    HHS_GAME_RELEASE_EVENT_RESET = 9,
    HHS_GAME_RELEASE_EVENT_QUIT = 10
} HHSVM81GameReleaseEvent;

typedef struct HHSVM81GameRelease {
    uint32_t release_version;
    uint32_t phase;
    uint32_t event;
    uint32_t lives;
    uint32_t deaths;
    uint32_t checkpoint;
    uint32_t checkpoint_x_px;
    uint32_t player_frames;
    uint32_t instructions_executed;
    uint32_t input_log_count;
    uint8_t last_input;
    uint8_t input_log[HHS_VM81_GAME_MAX_INPUT_FRAMES];
    HHSVM81GameState vm;
} HHSVM81GameRelease;

typedef struct HHSVM81GameReleaseReport {
    uint32_t status;
    uint32_t phase;
    uint32_t lives;
    uint32_t deaths;
    uint32_t checkpoint;
    uint32_t player_frames;
    uint32_t instructions_executed;
    uint32_t opcode_coverage;
    uint32_t receipts_emitted;
    HHSVM81GamePlayer final_player;
    HHSHash72 final_receipt_hash72;
    HHSHash216 final_state_identity_hash216;
} HHSVM81GameReleaseReport;

const char* hhs_vm81_game_release_phase_name(uint32_t phase);
HHSVM81GameStatus hhs_vm81_game_release_init(HHSVM81GameRelease* release);
HHSVM81GameStatus hhs_vm81_game_release_start(HHSVM81GameRelease* release);
HHSVM81GameStatus hhs_vm81_game_release_pause_toggle(HHSVM81GameRelease* release);
HHSVM81GameStatus hhs_vm81_game_release_restart(HHSVM81GameRelease* release);
HHSVM81GameStatus hhs_vm81_game_release_quit(HHSVM81GameRelease* release);
HHSVM81GameStatus hhs_vm81_game_release_step(HHSVM81GameRelease* release, uint8_t input_bits);
HHSVM81GameStatus hhs_vm81_game_release_run_headless(HHSVM81GameRelease* release, HHSVM81GameReleaseReport* report);
HHSVM81GameStatus hhs_vm81_game_release_replay_verify(const HHSVM81GameRelease* expected, HHSVM81GameReleaseReport* actual);
size_t hhs_vm81_game_release_render_ascii(const HHSVM81GameRelease* release, char* out, size_t capacity);

#ifdef __cplusplus
}
#endif

#endif
