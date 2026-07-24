#ifndef HHS_VM81_GAME_H
#define HHS_VM81_GAME_H

#include <stddef.h>
#include <stdint.h>
#include "hhs_hash216.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_VM81_GAME_ABI_VERSION 1U
#define HHS_VM81_GAME_SCREEN_WIDTH 160
#define HHS_VM81_GAME_SCREEN_HEIGHT 144
#define HHS_VM81_GAME_TILE_SIZE 8
#define HHS_VM81_GAME_VIEW_TILES_X 20
#define HHS_VM81_GAME_VIEW_TILES_Y 18
#define HHS_VM81_GAME_LEVEL_TILES_X 64
#define HHS_VM81_GAME_LEVEL_TILES_Y 18
#define HHS_VM81_GAME_PLAYER_WIDTH 16
#define HHS_VM81_GAME_PLAYER_HEIGHT 16
#define HHS_VM81_GAME_TICKS_PER_SECOND 60
#define HHS_VM81_GAME_SUBPIXELS 16
#define HHS_VM81_GAME_VM_CELLS 81
#define HHS_VM81_GAME_VISIBLE_CELLS 72
#define HHS_VM81_GAME_LOSHU_CELLS 9
#define HHS_VM81_GAME_PROGRAM_LENGTH 19
#define HHS_VM81_GAME_BASE20_RADIX 20
#define HHS_VM81_GAME_BASE20_TERMINATOR 19
#define HHS_VM81_GAME_MAX_PROGRAM_STEPS 64
#define HHS_VM81_GAME_MAX_INPUT_FRAMES 1024
#define HHS_VM81_GAME_RECEIPT_CAPACITY 256
#define HHS_VM81_GAME_AUTHORITY_REJECTED 0U
#define HHS_VM81_GAME_AUTHORITY_ADMITTED 1U

#define HHS_VM81_GAME_INPUT_LEFT  (1U << 0)
#define HHS_VM81_GAME_INPUT_RIGHT (1U << 1)
#define HHS_VM81_GAME_INPUT_JUMP  (1U << 2)
#define HHS_VM81_GAME_INPUT_RESET (1U << 3)

typedef enum HHSVM81RegisteredOpcode {
    HHS_VM81_REG_NOP = 0,
    HHS_VM81_REG_ADD = 1,
    HHS_VM81_REG_SUB = 2,
    HHS_VM81_REG_ROT = 3,
    HHS_VM81_REG_XOR = 4,
    HHS_VM81_REG_AND = 5,
    HHS_VM81_REG_OR = 6,
    HHS_VM81_REG_LOAD = 7,
    HHS_VM81_REG_STORE = 8,
    HHS_VM81_REG_BRANCH = 9,
    HHS_VM81_REG_BZ = 10,
    HHS_VM81_REG_BNZ = 11,
    HHS_VM81_REG_MULXY = 12,
    HHS_VM81_REG_MULYX = 13,
    HHS_VM81_REG_QGU = 14,
    HHS_VM81_REG_GATE_APB = 15,
    HHS_VM81_REG_GATE_CLOSURE = 16,
    HHS_VM81_REG_QBRANCH = 17,
    HHS_VM81_REG_CONSTRAIN = 18,
    HHS_VM81_REG_RELAX = 19,
    HHS_VM81_REG_SWEEP81 = 20,
    HHS_VM81_REG_CLOSE81 = 21,
    HHS_VM81_REG_HALT = 22
} HHSVM81RegisteredOpcode;

typedef enum HHSVM81GameOpcodeDigit {
    HHS_GAME_OP_LOAD = 0,
    HHS_GAME_OP_ADD = 1,
    HHS_GAME_OP_MULXY = 2,
    HHS_GAME_OP_QGU = 3,
    HHS_GAME_OP_SWEEP81 = 4,
    HHS_GAME_OP_CLOSE81 = 5,
    HHS_GAME_OP_CONSTRAIN = 6,
    HHS_GAME_OP_RELAX = 7,
    HHS_GAME_OP_GATE_APB = 8,
    HHS_GAME_OP_GATE_CLOSURE = 9,
    HHS_GAME_OP_MULYX = 10,
    HHS_GAME_OP_ROT = 11,
    HHS_GAME_OP_XOR = 12,
    HHS_GAME_OP_QBRANCH = 13,
    HHS_GAME_OP_SUB = 14,
    HHS_GAME_OP_OR = 15,
    HHS_GAME_OP_AND = 16,
    HHS_GAME_OP_BRANCH = 17,
    HHS_GAME_OP_HALT = 18
} HHSVM81GameOpcodeDigit;

typedef enum HHSVM81GameStatus {
    HHS_GAME_STATUS_OK = 0,
    HHS_GAME_STATUS_INVALID_ARGUMENT = 1,
    HHS_GAME_STATUS_ABI_VERSION_MISMATCH = 2,
    HHS_GAME_STATUS_INVALID_OPCODE = 3,
    HHS_GAME_STATUS_INVALID_OPERAND = 4,
    HHS_GAME_STATUS_AUTHORITY_REJECTED = 5,
    HHS_GAME_STATUS_STALE_GENERATION = 6,
    HHS_GAME_STATUS_STALE_STEP = 7,
    HHS_GAME_STATUS_HALTED = 8,
    HHS_GAME_STATUS_ARITHMETIC_OVERFLOW = 9,
    HHS_GAME_STATUS_PROGRAM_BOUNDS = 10,
    HHS_GAME_STATUS_STATE_INVARIANT_FAILURE = 11,
    HHS_GAME_STATUS_REPLAY_MISMATCH = 12,
    HHS_GAME_STATUS_BASE20_INVALID = 13,
    HHS_GAME_STATUS_OUTPUT_CAPACITY = 14
} HHSVM81GameStatus;

typedef enum HHSVM81AnimationState {
    HHS_GAME_ANIM_IDLE = 0,
    HHS_GAME_ANIM_WALK = 1,
    HHS_GAME_ANIM_JUMP = 2,
    HHS_GAME_ANIM_FALL = 3
} HHSVM81AnimationState;

typedef struct HHSVM81GameInstruction {
    uint8_t opcode_digit;
    int16_t a;
    int16_t b;
    int16_t c;
} HHSVM81GameInstruction;

typedef struct HHSVM81GamePlayer {
    int32_t x_subpx;
    int32_t y_subpx;
    int32_t vx_subpx;
    int32_t vy_subpx;
    uint8_t grounded;
    uint8_t facing_right;
    uint8_t animation_state;
    uint8_t animation_frame;
} HHSVM81GamePlayer;

typedef struct HHSVM81GameReceipt {
    uint64_t step;
    uint64_t frame;
    uint8_t opcode_digit;
    uint8_t registered_opcode;
    uint8_t input_bits;
    uint8_t branch_taken;
    HHSHash72 parent_hash72;
    HHSHash72 state_hash72;
    HHSHash72 receipt_hash72;
    HHSHash216 state_identity_hash216;
} HHSVM81GameReceipt;

typedef struct HHSVM81GameState {
    uint32_t abi_version;
    uint32_t generation;
    uint64_t step;
    uint64_t frame;
    uint32_t pc;
    uint32_t max_frames;
    uint32_t input_count;
    uint32_t receipt_count;
    uint32_t camera_x_px;
    uint32_t opcode_coverage;
    uint32_t constraint_strength;
    uint8_t phase;
    uint8_t lo_shu_set;
    uint8_t halted;
    uint8_t closure_valid;
    uint8_t current_input;
    uint8_t qbranch_mode;
    uint8_t gate_apb_valid;
    uint8_t gate_closure_valid;
    int32_t accumulator;
    int32_t ordered_xy;
    int32_t ordered_yx;
    int32_t xyzw[4];
    HHSVM81GamePlayer player;
    uint8_t level[HHS_VM81_GAME_LEVEL_TILES_Y][HHS_VM81_GAME_LEVEL_TILES_X];
    uint8_t vm81[HHS_VM81_GAME_VM_CELLS];
    uint8_t input_trace[HHS_VM81_GAME_MAX_INPUT_FRAMES];
    HHSVM81GameInstruction program[HHS_VM81_GAME_PROGRAM_LENGTH];
    HHSVM81GameReceipt receipts[HHS_VM81_GAME_RECEIPT_CAPACITY];
    HHSHash72 latest_receipt_hash72;
    HHSHash216 latest_state_identity_hash216;
} HHSVM81GameState;

typedef struct HHSVM81GameRequest {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t authority_admission;
    uint32_t expected_generation;
    uint64_t expected_step;
    HHSVM81GameInstruction instruction;
} HHSVM81GameRequest;

typedef struct HHSVM81GameResult {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t status;
    uint32_t mutation_performed;
    uint32_t state_unchanged;
    uint32_t pc_before;
    uint32_t pc_after;
    uint64_t step_before;
    uint64_t step_after;
    uint64_t frame_before;
    uint64_t frame_after;
    HHSHash72 receipt_hash72;
    HHSHash216 state_identity_hash216;
} HHSVM81GameResult;

typedef struct HHSVM81GameRunReport {
    uint32_t status;
    uint32_t frames_executed;
    uint32_t instructions_executed;
    uint32_t opcode_coverage;
    uint32_t receipts_emitted;
    uint32_t final_camera_x_px;
    HHSVM81GamePlayer final_player;
    HHSHash72 final_receipt_hash72;
    HHSHash216 final_state_identity_hash216;
} HHSVM81GameRunReport;

const char* hhs_vm81_game_opcode_name(uint8_t opcode_digit);
uint8_t hhs_vm81_game_registered_opcode(uint8_t opcode_digit);
HHSVM81GameStatus hhs_vm81_game_init(HHSVM81GameState* state, const uint8_t* input_trace, uint32_t input_count);
HHSVM81GameStatus hhs_vm81_game_reset(HHSVM81GameState* state);
HHSVM81GameStatus hhs_vm81_game_execute(HHSVM81GameState* state, const HHSVM81GameRequest* request, HHSVM81GameResult* result);
HHSVM81GameStatus hhs_vm81_game_run(HHSVM81GameState* state, HHSVM81GameRunReport* report);
HHSVM81GameStatus hhs_vm81_game_replay_verify(const uint8_t* input_trace, uint32_t input_count, const HHSVM81GameRunReport* expected, HHSVM81GameRunReport* actual);
HHSVM81GameStatus hhs_vm81_game_base20_encode_program(const HHSVM81GameInstruction* program, size_t program_length, char* out_decimal, size_t out_capacity);
HHSVM81GameStatus hhs_vm81_game_base20_decode_program(const char* decimal, uint8_t* out_digits, size_t out_capacity, size_t* out_length);
int hhs_vm81_game_validate_state(const HHSVM81GameState* state);

#ifdef __cplusplus
}
#endif

#endif
