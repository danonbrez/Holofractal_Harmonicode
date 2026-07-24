        case HHS_GAME_OP_QBRANCH:
            if (ins->a < 0 || ins->b < 0 || ins->a >= HHS_VM81_GAME_PROGRAM_LENGTH || ins->b >= HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_GAME_STATUS_INVALID_OPERAND;
            state->qbranch_mode = (uint8_t)(((state->phase / 18U) & 1U) != 0U);
            state->pc = state->qbranch_mode ? (uint32_t)ins->b : (uint32_t)ins->a;
            *branch_taken = 1U;
            break;
        case HHS_GAME_OP_SUB:
            if (!hhs_checked_add_i32(state->accumulator, -state->player.vy_subpx, &state->accumulator)) return HHS_GAME_STATUS_ARITHMETIC_OVERFLOW;
            state->pc = HHS_GAME_OP_OR;
            break;
        case HHS_GAME_OP_OR:
            state->accumulator |= (int32_t)state->player.animation_state;
            state->pc++;
            break;
        case HHS_GAME_OP_AND:
            state->accumulator &= 0x7fffffff;
            state->pc++;
            break;
        case HHS_GAME_OP_BRANCH:
            if (ins->a < 0 || ins->b < 0 || ins->a >= HHS_VM81_GAME_PROGRAM_LENGTH || ins->b >= HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_GAME_STATUS_INVALID_OPERAND;
            state->frame++;
            state->phase = (uint8_t)((state->phase + 1U) % 72U);
            state->pc = state->frame < state->max_frames ? (uint32_t)ins->a : (uint32_t)ins->b;
            *branch_taken = 1U;
            break;
        case HHS_GAME_OP_HALT:
            state->halted = 1U;
            state->pc = HHS_VM81_GAME_PROGRAM_LENGTH;
            break;
        default:
            return HHS_GAME_STATUS_INVALID_OPCODE;
    }
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_execute(HHSVM81GameState* state, const HHSVM81GameRequest* request, HHSVM81GameResult* result) {
    HHSVM81GameState before;
    HHSVM81GameStatus status;
    uint8_t branch_taken = 0U;
    if (!result) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    hhs_result_init(result, state);
    if (!state || !request) return hhs_finish_result(state, NULL, result, HHS_GAME_STATUS_INVALID_ARGUMENT, 0U);
    before = *state;
    if (request->struct_size < sizeof(*request) || request->abi_version != HHS_VM81_GAME_ABI_VERSION || state->abi_version != HHS_VM81_GAME_ABI_VERSION) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_ABI_VERSION_MISMATCH, 0U);
    }
    if (request->authority_admission != HHS_VM81_GAME_AUTHORITY_ADMITTED) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_AUTHORITY_REJECTED, 0U);
    }
    if (request->expected_generation != state->generation) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_STALE_GENERATION, 0U);
    }
    if (request->expected_step != state->step) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_STALE_STEP, 0U);
    }
    if (state->halted) return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_HALTED, 0U);
    if (request->instruction.opcode_digit >= HHS_VM81_GAME_PROGRAM_LENGTH) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_INVALID_OPCODE, 0U);
    }
    if (state->pc >= HHS_VM81_GAME_PROGRAM_LENGTH || request->instruction.opcode_digit != state->program[state->pc].opcode_digit) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_PROGRAM_BOUNDS, 0U);
    }
    if (request->instruction.a != state->program[state->pc].a ||
        request->instruction.b != state->program[state->pc].b ||
        request->instruction.c != state->program[state->pc].c) {
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_INVALID_OPERAND, 0U);
    }
    status = hhs_apply_opcode(state, &request->instruction, &branch_taken);
    if (status != HHS_GAME_STATUS_OK) return hhs_finish_result(state, &before, result, status, 0U);
    state->opcode_coverage |= (1U << request->instruction.opcode_digit);
    state->step++;
    hhs_refresh_hashes(state);
    hhs_receipt_commit(state, request->instruction.opcode_digit, branch_taken);
    if (!hhs_vm81_game_validate_state(state)) {
        *state = before;
        return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_STATE_INVARIANT_FAILURE, 0U);
    }
    return hhs_finish_result(state, &before, result, HHS_GAME_STATUS_OK, 1U);
}

HHSVM81GameStatus hhs_vm81_game_run(HHSVM81GameState* state, HHSVM81GameRunReport* report) {
    uint32_t instructions = 0U;
    HHSVM81GameStatus status = HHS_GAME_STATUS_OK;
    if (!state || !report) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    memset(report, 0, sizeof(*report));
    while (!state->halted) {
        HHSVM81GameRequest request;
        HHSVM81GameResult result;
        if (instructions >= state->max_frames * HHS_VM81_GAME_MAX_PROGRAM_STEPS + HHS_VM81_GAME_MAX_PROGRAM_STEPS) {
            status = HHS_GAME_STATUS_PROGRAM_BOUNDS;
            break;
        }
        if (state->pc >= HHS_VM81_GAME_PROGRAM_LENGTH) {
            status = HHS_GAME_STATUS_PROGRAM_BOUNDS;
            break;
        }
        memset(&request, 0, sizeof(request));
        request.struct_size = (uint32_t)sizeof(request);
        request.abi_version = HHS_VM81_GAME_ABI_VERSION;
        request.authority_admission = HHS_VM81_GAME_AUTHORITY_ADMITTED;
        request.expected_generation = state->generation;
        request.expected_step = state->step;
        request.instruction = state->program[state->pc];
        status = hhs_vm81_game_execute(state, &request, &result);
        if (status != HHS_GAME_STATUS_OK) break;
        instructions++;
    }
    report->status = status;
    report->frames_executed = (uint32_t)state->frame;
    report->instructions_executed = instructions;
    report->opcode_coverage = state->opcode_coverage;
    report->receipts_emitted = state->receipt_count;
    report->final_camera_x_px = state->camera_x_px;
    report->final_player = state->player;
    report->final_receipt_hash72 = state->latest_receipt_hash72;
    report->final_state_identity_hash216 = state->latest_state_identity_hash216;
    return status;
}

HHSVM81GameStatus hhs_vm81_game_replay_verify(const uint8_t* input_trace, uint32_t input_count, const HHSVM81GameRunReport* expected, HHSVM81GameRunReport* actual) {
    HHSVM81GameState replay;
    HHSVM81GameStatus status;
    if (!input_trace || !expected || !actual) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    status = hhs_vm81_game_init(&replay, input_trace, input_count);
    if (status != HHS_GAME_STATUS_OK) return status;
    status = hhs_vm81_game_run(&replay, actual);
    if (status != HHS_GAME_STATUS_OK) return status;
    if (expected->frames_executed != actual->frames_executed ||
        expected->instructions_executed != actual->instructions_executed ||
        expected->opcode_coverage != actual->opcode_coverage ||
        expected->receipts_emitted != actual->receipts_emitted ||
        expected->final_camera_x_px != actual->final_camera_x_px ||
        expected->final_player.x_subpx != actual->final_player.x_subpx ||
        expected->final_player.y_subpx != actual->final_player.y_subpx ||
        expected->final_player.vx_subpx != actual->final_player.vx_subpx ||
        expected->final_player.vy_subpx != actual->final_player.vy_subpx ||
        expected->final_player.grounded != actual->final_player.grounded ||
        expected->final_player.facing_right != actual->final_player.facing_right ||
        expected->final_player.animation_state != actual->final_player.animation_state ||
        expected->final_player.animation_frame != actual->final_player.animation_frame ||
        !hhs_hash72_equal(&expected->final_receipt_hash72, &actual->final_receipt_hash72) ||
        !hhs_hash216_equal(&expected->final_state_identity_hash216, &actual->final_state_identity_hash216)) {
        return HHS_GAME_STATUS_REPLAY_MISMATCH;
    }
    return HHS_GAME_STATUS_OK;
}

static void hhs_bigint_zero(HHSGameBigInt* n) {
    memset(n, 0, sizeof(*n));
    n->used = 1U;
}

static int hhs_bigint_mul_add(HHSGameBigInt* n, uint32_t mul, uint32_t add) {
    uint64_t carry = add;
    size_t i;
    for (i = 0; i < n->used; ++i) {
        uint64_t v = (uint64_t)n->limbs[i] * mul + carry;
        n->limbs[i] = (uint32_t)(v % HHS_GAME_BIGINT_BASE);
        carry = v / HHS_GAME_BIGINT_BASE;
    }
    while (carry != 0U) {
        if (n->used >= HHS_GAME_MAX_BIGINT_LIMBS) return 0;
        n->limbs[n->used++] = (uint32_t)(carry % HHS_GAME_BIGINT_BASE);
        carry /= HHS_GAME_BIGINT_BASE;
    }
    return 1;
}

static int hhs_bigint_from_decimal(const char* decimal, HHSGameBigInt* n) {
    size_t i;
    if (!decimal || !*decimal) return 0;
    hhs_bigint_zero(n);
    for (i = 0; decimal[i] != '\0'; ++i) {
        if (decimal[i] < '0' || decimal[i] > '9') return 0;
        if (!hhs_bigint_mul_add(n, 10U, (uint32_t)(decimal[i] - '0'))) return 0;
    }
    return 1;
}

static uint32_t hhs_bigint_div_small(HHSGameBigInt* n, uint32_t divisor) {
    uint64_t rem = 0U;
    size_t i = n->used;
    while (i-- > 0U) {
        uint64_t cur = n->limbs[i] + rem * HHS_GAME_BIGINT_BASE;
        n->limbs[i] = (uint32_t)(cur / divisor);
        rem = cur % divisor;
    }
    while (n->used > 1U && n->limbs[n->used - 1U] == 0U) n->used--;
    return (uint32_t)rem;
}

static int hhs_bigint_is_zero(const HHSGameBigInt* n) {
    return n->used == 1U && n->limbs[0] == 0U;
}

static HHSVM81GameStatus hhs_bigint_to_decimal(const HHSGameBigInt* n, char* out, size_t capacity) {
    size_t pos = 0U;
    size_t i;
    int written;
    if (!out || capacity == 0U) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    written = snprintf(out, capacity, "%u", n->limbs[n->used - 1U]);
    if (written < 0 || (size_t)written >= capacity) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    pos = (size_t)written;
    i = n->used - 1U;
    while (i-- > 0U) {
        written = snprintf(out + pos, capacity - pos, "%09u", n->limbs[i]);
        if (written < 0 || (size_t)written >= capacity - pos) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
        pos += (size_t)written;
    }
    return HHS_GAME_STATUS_OK;
}

HHSVM81GameStatus hhs_vm81_game_base20_encode_program(const HHSVM81GameInstruction* program, size_t program_length, char* out_decimal, size_t out_capacity) {
    HHSGameBigInt n;
    size_t i;
    if (!program || !out_decimal || program_length != HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    hhs_bigint_zero(&n);
    /* Leading length sentinel preserves an initial opcode digit of zero. */
    n.limbs[0] = 1U;
    for (i = 0; i < program_length; ++i) {
        if (program[i].opcode_digit >= HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_GAME_STATUS_BASE20_INVALID;
        if (!hhs_bigint_mul_add(&n, HHS_VM81_GAME_BASE20_RADIX, program[i].opcode_digit)) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    }
    if (!hhs_bigint_mul_add(&n, HHS_VM81_GAME_BASE20_RADIX, HHS_VM81_GAME_BASE20_TERMINATOR)) return HHS_GAME_STATUS_OUTPUT_CAPACITY;
    return hhs_bigint_to_decimal(&n, out_decimal, out_capacity);
}

HHSVM81GameStatus hhs_vm81_game_base20_decode_program(const char* decimal, uint8_t* out_digits, size_t out_capacity, size_t* out_length) {
    HHSGameBigInt n;
    uint8_t reverse[HHS_VM81_GAME_PROGRAM_LENGTH + 2U];
    size_t count = 0U;
    size_t i;
    if (!decimal || !out_digits || !out_length) return HHS_GAME_STATUS_INVALID_ARGUMENT;
    if (!hhs_bigint_from_decimal(decimal, &n)) return HHS_GAME_STATUS_BASE20_INVALID;
    while (!hhs_bigint_is_zero(&n)) {
        if (count >= sizeof(reverse)) return HHS_GAME_STATUS_BASE20_INVALID;
        reverse[count++] = (uint8_t)hhs_bigint_div_small(&n, HHS_VM81_GAME_BASE20_RADIX);
    }
    if (count != HHS_VM81_GAME_PROGRAM_LENGTH + 2U ||
        reverse[0] != HHS_VM81_GAME_BASE20_TERMINATOR ||
        reverse[count - 1U] != 1U ||
        out_capacity < HHS_VM81_GAME_PROGRAM_LENGTH) {
        return HHS_GAME_STATUS_BASE20_INVALID;
    }
    for (i = 0; i < HHS_VM81_GAME_PROGRAM_LENGTH; ++i) {
        uint8_t digit = reverse[count - 2U - i];
        if (digit >= HHS_VM81_GAME_PROGRAM_LENGTH) return HHS_GAME_STATUS_BASE20_INVALID;
        out_digits[i] = digit;
    }
    *out_length = HHS_VM81_GAME_PROGRAM_LENGTH;
    return HHS_GAME_STATUS_OK;
}

int hhs_vm81_game_validate_state(const HHSVM81GameState* state) {
    size_t i;
    int32_t max_x_subpx = (HHS_VM81_GAME_LEVEL_TILES_X * HHS_VM81_GAME_TILE_SIZE - HHS_VM81_GAME_PLAYER_WIDTH) * HHS_VM81_GAME_SUBPIXELS;
    int32_t max_y_subpx = (HHS_VM81_GAME_LEVEL_TILES_Y * HHS_VM81_GAME_TILE_SIZE - HHS_VM81_GAME_PLAYER_HEIGHT) * HHS_VM81_GAME_SUBPIXELS;
    if (!state || state->abi_version != HHS_VM81_GAME_ABI_VERSION) return 0;
    if (state->pc > HHS_VM81_GAME_PROGRAM_LENGTH || state->frame > state->max_frames || state->max_frames != state->input_count) return 0;
    if (state->phase >= 72U || state->lo_shu_set >= 41U) return 0;
    if (!state->closure_valid) return 0;
    if (hhs_wrap72_i64((int64_t)state->xyzw[0] + state->xyzw[1] - state->xyzw[2] - state->xyzw[3]) != 0U) return 0;
    for (i = 0; i < HHS_VM81_GAME_LOSHU_CELLS; ++i) if (state->vm81[HHS_VM81_GAME_VISIBLE_CELLS + i] != HHS_LO_SHU[i]) return 0;
    if (state->player.x_subpx < 0 || state->player.x_subpx > max_x_subpx || state->player.y_subpx < 0 || state->player.y_subpx > max_y_subpx) return 0;
    if (state->camera_x_px > (uint32_t)(HHS_VM81_GAME_LEVEL_TILES_X * HHS_VM81_GAME_TILE_SIZE - HHS_VM81_GAME_SCREEN_WIDTH)) return 0;
    return 1;
}
