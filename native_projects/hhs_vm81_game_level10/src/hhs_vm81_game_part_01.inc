    }
    state->vm81[0] = x;
    state->vm81[1] = y;
    state->vm81[2] = z;
    state->vm81[3] = w;
    state->vm81[4] = state->phase;
    state->vm81[5] = (uint8_t)(state->frame % 72U);
    state->vm81[6] = (uint8_t)(state->camera_x_px % 72U);
    state->vm81[7] = state->player.animation_state;
    state->vm81[8] = state->player.animation_frame;
}

static void hhs_level_init(HHSVM81GameState* state) {
    int x;
    memset(state->level, 0, sizeof(state->level));
    for (x = 0; x < HHS_VM81_GAME_LEVEL_TILES_X; ++x) {
        state->level[16][x] = 1U;
        state->level[17][x] = 1U;
    }
    for (x = 8; x <= 13; ++x) state->level[12][x] = 1U;
    for (x = 20; x <= 27; ++x) state->level[10][x] = 1U;
    for (x = 35; x <= 40; ++x) state->level[13][x] = 1U;
    for (x = 50; x <= 57; ++x) state->level[9][x] = 1U;
    state->level[15][31] = 1U;
    state->level[14][31] = 1U;
    state->level[13][31] = 1U;
}

static void hhs_player_reset(HHSVM81GameState* state) {
    state->player.x_subpx = 2 * HHS_VM81_GAME_TILE_SIZE * HHS_VM81_GAME_SUBPIXELS;
    state->player.y_subpx = 14 * HHS_VM81_GAME_TILE_SIZE * HHS_VM81_GAME_SUBPIXELS;
    state->player.vx_subpx = 0;
    state->player.vy_subpx = 0;
    state->player.grounded = 1U;
    state->player.facing_right = 1U;
    state->player.animation_state = HHS_GAME_ANIM_IDLE;
    state->player.animation_frame = 0U;
    state->camera_x_px = 0U;
}

static void hhs_receipt_commit(HHSVM81GameState* state, uint8_t opcode_digit, uint8_t branch_taken) {
    HHSVM81GameReceipt* receipt;
    HHSGameCanonicalState canonical;
    uint8_t payload[4096];
    size_t payload_size = 0U;
    receipt = &state->receipts[state->receipt_count % HHS_VM81_GAME_RECEIPT_CAPACITY];
    state->receipt_count++;
    memset(receipt, 0, sizeof(*receipt));
    receipt->step = state->step;
    receipt->frame = state->frame;
    receipt->opcode_digit = opcode_digit;
    receipt->registered_opcode = hhs_vm81_game_registered_opcode(opcode_digit);
    receipt->input_bits = state->current_input;
    receipt->branch_taken = branch_taken;
    receipt->parent_hash72 = state->latest_receipt_hash72;
    hhs_canonicalize_state(state, &canonical);
    hhs_hash72_compute(canonical.bytes, canonical.size, &receipt->state_hash72);
    hhs_hash216_compute(canonical.bytes, canonical.size, &receipt->state_identity_hash216);
    memcpy(payload + payload_size, receipt->parent_hash72.value, HHS_HASH72_LEN); payload_size += HHS_HASH72_LEN;
    memcpy(payload + payload_size, receipt->state_hash72.value, HHS_HASH72_LEN); payload_size += HHS_HASH72_LEN;
    {
        size_t i;
        for (i = 0; i < 8U; ++i) payload[payload_size++] = (uint8_t)((receipt->step >> (8U * i)) & 0xffU);
        for (i = 0; i < 8U; ++i) payload[payload_size++] = (uint8_t)((receipt->frame >> (8U * i)) & 0xffU);
    }
    payload[payload_size++] = receipt->opcode_digit;
    payload[payload_size++] = receipt->registered_opcode;
    payload[payload_size++] = receipt->input_bits;
    payload[payload_size++] = receipt->branch_taken;
    hhs_hash72_compute(payload, payload_size, &receipt->receipt_hash72);
    state->latest_receipt_hash72 = receipt->receipt_hash72;
    state->latest_state_identity_hash216 = receipt->state_identity_hash216;
}

static int hhs_program_valid(void) {
    size_t i;
    uint32_t seen = 0U;
    for (i = 0; i < HHS_VM81_GAME_PROGRAM_LENGTH; ++i) {
        uint8_t d = HHS_GAME_PROGRAM[i].opcode_digit;
        if (d >= HHS_VM81_GAME_PROGRAM_LENGTH) return 0;
        seen |= (1U << d);
    }
    return seen == ((1U << HHS_VM81_GAME_PROGRAM_LENGTH) - 1U);
}

const char* hhs_vm81_game_opcode_name(uint8_t opcode_digit) {
    if (opcode_digit >= HHS_VM81_GAME_PROGRAM_LENGTH) return "INVALID";
    return HHS_GAME_OPCODE_NAMES[opcode_digit];
}

uint8_t hhs_vm81_game_registered_opcode(uint8_t opcode_digit) {
    if (opcode_digit >= HHS_VM81_GAME_PROGRAM_LENGTH) return 0xffU;
    return HHS_GAME_REGISTERED_IDS[opcode_digit];
}

HHSVM81GameStatus hhs_vm81_game_init(HHSVM81GameState* state, const uint8_t* input_trace, uint32_t input_count) {
    if (!state || (!input_trace && input_count != 0U) || input_count == 0U || input_count > HHS_VM81_GAME_MAX_INPUT_FRAMES) {
        return HHS_GAME_STATUS_INVALID_ARGUMENT;
    }
    if (!hhs_program_valid()) return HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
    memset(state, 0, sizeof(*state));
    state->abi_version = HHS_VM81_GAME_ABI_VERSION;
    state->generation = 1U;
    state->max_frames = input_count;
    state->input_count = input_count;
    memcpy(state->input_trace, input_trace, input_count);
    memcpy(state->program, HHS_GAME_PROGRAM, sizeof(HHS_GAME_PROGRAM));
    hhs_level_init(state);
    hhs_player_reset(state);
    hhs_project_vm81(state);
    hhs_refresh_hashes(state);
    hhs_hash72_compute("HHS_VM81_GAME_GENESIS", 21U, &state->latest_receipt_hash72);
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_reset(HHSVM81GameState* state) {
    uint8_t trace[HHS_VM81_GAME_MAX_INPUT_FRAMES];
    uint32_t count;
    uint32_t generation;
    HHSVM81GameStatus status;
    if (!state || state->abi_version != HHS_VM81_GAME_ABI_VERSION) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    count = state->input_count;
    generation = state->generation + 1U;
    memcpy(trace, state->input_trace, count);
    status = hhs_vm81_game_init(state, trace, count);
    if (status == HHS_GAME_STATUS_OK) state->generation = generation;
    return status;
}

static void hhs_result_init(HHSVM81GameResult* result, const HHSVM81GameState* state) {
    memset(result, 0, sizeof(*result));
    result->struct_size = (uint32_t)sizeof(*result);
    result->abi_version = HHS_VM81_GAME_ABI_VERSION;
    if (state) {
        result->pc_before = state->pc;
        result->pc_after = state->pc;
        result->step_before = state->step;
        result->step_after = state->step;
        result->frame_before = state->frame;
        result->frame_after = state->frame;
        result->receipt_hash72 = state->latest_receipt_hash72;
        result->state_identity_hash216 = state->latest_state_identity_hash216;
    }
    result->state_unchanged = 1U;
}

static HHSVM81GameStatus hhs_finish_result(
    HHSVM81GameState* state,
    const HHSVM81GameState* before,
    HHSVM81GameResult* result,
    HHSVM81GameStatus status,
    uint32_t mutated
) {
    result->status = (uint32_t)status;
    result->mutation_performed = mutated;
    if (state) {
        result->pc_after = state->pc;
        result->step_after = state->step;
        result->frame_after = state->frame;
        result->receipt_hash72 = state->latest_receipt_hash72;
        result->state_identity_hash216 = state->latest_state_identity_hash216;
    }
    if (state && before) result->state_unchanged = (uint32_t)(memcmp(state, before, sizeof(*state)) == 0);
    if (status != HHS_GAME_STATUS_OK && state && before && !result->state_unchanged) {
        *state = *before;
        result->status = HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
        result->mutation_performed = 0U;
        result->state_unchanged = 1U;
        result->pc_after = state->pc;
        result->step_after = state->step;
        result->frame_after = state->frame;
        return HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
    }
    return (HHSVM81GameStatus)result->status;
}

static HHSVM81GameStatus hhs_apply_opcode(HHSVM81GameState* state, const HHSVM81GameInstruction* ins, uint8_t* branch_taken) {
    int32_t temp;
    uint8_t op = ins->opcode_digit;
    *branch_taken = 0U;
    switch (op) {
        case HHS_GAME_OP_LOAD:
            if (state->frame >= state->input_count) return HHS_GAME_STATUS_PROGRAM_BOUNDS;
            state->current_input = state->input_trace[state->frame];
            if ((state->current_input & ~(HHS_VM81_GAME_INPUT_LEFT | HHS_VM81_GAME_INPUT_RIGHT | HHS_VM81_GAME_INPUT_JUMP | HHS_VM81_GAME_INPUT_RESET)) != 0U) {
                return HHS_GAME_STATUS_INVALID_OPERAND;
            }
            if ((state->current_input & HHS_VM81_GAME_INPUT_RESET) != 0U) hhs_player_reset(state);
            state->accumulator = (int32_t)state->current_input;
            state->pc++;
            break;
        case HHS_GAME_OP_ADD:
            state->player.vx_subpx = 0;
            if ((state->current_input & HHS_VM81_GAME_INPUT_LEFT) != 0U) {
                state->player.vx_subpx -= HHS_GAME_RUN_SPEED;
                state->player.facing_right = 0U;
            }
            if ((state->current_input & HHS_VM81_GAME_INPUT_RIGHT) != 0U) {
                state->player.vx_subpx += HHS_GAME_RUN_SPEED;
                state->player.facing_right = 1U;
            }
            if (!hhs_checked_add_i32(state->accumulator, state->player.vx_subpx, &state->accumulator)) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            state->pc++;
            break;
        case HHS_GAME_OP_MULXY:
            if (!hhs_checked_mul_i32(hhs_wrap72_i64(state->player.x_subpx), hhs_wrap72_i64(state->player.y_subpx), &state->ordered_xy)) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            state->pc++;
            break;
        case HHS_GAME_OP_QGU:
            state->phase = (uint8_t)((state->phase + (uint8_t)ins->a) % 72U);
            state->lo_shu_set = (uint8_t)((state->frame + state->phase) % 41U);
            state->pc++;
            break;
        case HHS_GAME_OP_SWEEP81:
            if ((state->current_input & HHS_VM81_GAME_INPUT_JUMP) != 0U && state->player.grounded) state->player.vy_subpx = HHS_GAME_JUMP_SPEED;
            if (!hhs_checked_add_i32(state->player.vy_subpx, HHS_GAME_GRAVITY, &temp)) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            if (temp > HHS_GAME_MAX_FALL_SPEED) temp = HHS_GAME_MAX_FALL_SPEED;
            state->player.vy_subpx = temp;
            hhs_move_horizontal(state);
            hhs_move_vertical(state);
            hhs_update_camera(state);
            hhs_update_animation(state);
            hhs_project_vm81(state);
            state->pc++;
            break;
        case HHS_GAME_OP_CLOSE81:
            hhs_project_vm81(state);
            if (!state->closure_valid) return HHS_GAME_STATUS_STATE_INVARIANT_FAILURE;
            state->pc++;
            break;
        case HHS_GAME_OP_CONSTRAIN:
            if (ins->a < 0) return HHS_GAME_STATUS_INVALID_OPERAND;
            if (state->constraint_strength > UINT32_MAX - (uint32_t)ins->a) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            state->constraint_strength += (uint32_t)ins->a;
            state->pc++;
            break;
        case HHS_GAME_OP_RELAX:
            if (ins->a < 0) return HHS_GAME_STATUS_INVALID_OPERAND;
            if (state->constraint_strength > (uint32_t)ins->a) state->constraint_strength -= (uint32_t)ins->a;
            else state->constraint_strength = 0U;
            state->pc++;
            break;
        case HHS_GAME_OP_GATE_APB:
            state->gate_apb_valid = (uint8_t)(state->ordered_xy == state->ordered_yx || state->ordered_yx == 0);
            state->pc++;
            break;
        case HHS_GAME_OP_GATE_CLOSURE:
            state->gate_closure_valid = state->closure_valid;
            state->pc++;
            break;
        case HHS_GAME_OP_MULYX:
            if (!hhs_checked_mul_i32(hhs_wrap72_i64(state->player.y_subpx), hhs_wrap72_i64(state->player.x_subpx), &state->ordered_yx)) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            state->gate_apb_valid = (uint8_t)(state->ordered_xy == state->ordered_yx);
            state->pc++;
            break;
        case HHS_GAME_OP_ROT:
            state->accumulator = (int32_t)(((uint32_t)state->accumulator << 1U) | ((uint32_t)state->accumulator >> 31U));
            state->pc++;
            break;
        case HHS_GAME_OP_XOR:
            state->accumulator ^= (int32_t)state->phase;
            state->pc++;
            break;
