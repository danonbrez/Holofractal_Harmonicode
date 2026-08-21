#include "hhs_pass219_exact_vm81_candidate_adapter_1_21_3.h"

#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/*
 * Reuse the exact inherited VM81 implementation directly inside this adapter
 * translation unit. All kernel internals remain private; only the explicit
 * Pass 219 adapter ABI below is exported.
 */
#define main hhs_pass219_vm81_embedded_kernel_cli_main
#include "../HARMONICODE_VM_RUNTIME.c"
#undef main

_Static_assert(HHS_EXACT_PASS219_VM81_OP_COUNT == OP__COUNT,
               "Pass219 adapter opcode map drifted from exact VM81 kernel");
_Static_assert(HHS_EXACT_PASS219_VM81_SYMBOL_ENUM_COUNT ==
                   HHS_EXACT_PASS219_VM81_SYMBOL_COUNT,
               "Pass219 glyph map must expose exactly 24 symbols");
_Static_assert(HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS +
                   HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS ==
                   HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS,
               "Pass219 source-structure thread count mismatch");
_Static_assert(HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS +
                   HHS_EXACT_PASS219_VM81_DERIVED_THREADS ==
                   HHS_EXACT_PASS219_VM81_PROGRAM_THREADS,
               "Pass219 permanent VM81 thread count mismatch");
_Static_assert(sizeof(((HHSExactVM81Frame *)0)->words) == VM81_FRAME_BYTES,
               "Pass219 candidate frame must match exact VM81 carrier");

typedef struct HHS219ParenPair {
    uint16_t open_offset;
    uint16_t close_offset;
    uint8_t depth;
} HHS219ParenPair;

static atomic_flag HHS219_KERNEL_INIT_LOCK = ATOMIC_FLAG_INIT;
static atomic_uint HHS219_KERNEL_INIT_DONE = ATOMIC_VAR_INIT(0U);

static uint32_t hhs219_adapter_version_word(void) {
    return (HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_VM81_ADAPTER_VERSION_PATCH;
}

static int hhs219_kernel_init_once(void) {
    if (atomic_load_explicit(&HHS219_KERNEL_INIT_DONE, memory_order_acquire) != 0U)
        return 1;

    while (atomic_flag_test_and_set_explicit(
               &HHS219_KERNEL_INIT_LOCK, memory_order_acquire)) {
    }

    if (atomic_load_explicit(&HHS219_KERNEL_INIT_DONE, memory_order_relaxed) == 0U) {
        if (!init_hash72()) {
            atomic_flag_clear_explicit(&HHS219_KERNEL_INIT_LOCK, memory_order_release);
            return 0;
        }
        atomic_store_explicit(&HHS219_KERNEL_INIT_DONE, 1U, memory_order_release);
    }

    atomic_flag_clear_explicit(&HHS219_KERNEL_INIT_LOCK, memory_order_release);
    return 1;
}

static uint64_t hhs219_source_seed(
    const uint8_t sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES]
) {
    uint64_t state = UINT64_C(1469598103934665603);
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES; ++i) {
        state ^= (uint64_t)sha256[i];
        state *= UINT64_C(1099511628211);
    }
    return state;
}

static int hhs219_source_identity_valid(
    const uint8_t sha256[HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES]
) {
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 0;
    return memcmp(
               sha256,
               descriptor.native_source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0;
}

static void hhs219_instruction_init(
    HHSExactPass219VM81InstructionV1 *instruction,
    uint8_t opcode,
    uint8_t a,
    uint8_t b,
    uint8_t c,
    uint8_t constraint_group,
    uint8_t phase
) {
    memset(instruction, 0, sizeof(*instruction));
    instruction->struct_size = (uint32_t)sizeof(*instruction);
    instruction->version = hhs219_adapter_version_word();
    instruction->opcode = opcode;
    instruction->a = a;
    instruction->b = b;
    instruction->c = c;
    instruction->constraint_group = constraint_group;
    instruction->phase = phase;
}

static void hhs219_sort_parenthesis_pairs(
    HHS219ParenPair *pairs,
    uint32_t count
) {
    uint32_t i;
    for (i = 1U; i < count; ++i) {
        HHS219ParenPair key = pairs[i];
        uint32_t j = i;
        while (j > 0U && pairs[j - 1U].open_offset > key.open_offset) {
            pairs[j] = pairs[j - 1U];
            --j;
        }
        pairs[j] = key;
    }
}

static HHSExactStatus hhs219_scan_source_structure(
    const uint8_t *source,
    size_t source_length,
    HHS219ParenPair pairs[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS],
    uint16_t equality_offsets[HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS]
) {
    uint16_t stack[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint8_t depth_stack[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint32_t stack_count = 0U;
    uint32_t pair_count = 0U;
    uint32_t equality_count = 0U;
    size_t i;

    if (source == NULL || pairs == NULL || equality_offsets == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    for (i = 0U; i < source_length; ++i) {
        if (source[i] == (uint8_t)'(') {
            if (stack_count >= HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            stack[stack_count] = (uint16_t)i;
            depth_stack[stack_count] = (uint8_t)(stack_count + 1U);
            ++stack_count;
        } else if (source[i] == (uint8_t)')') {
            if (stack_count == 0U ||
                pair_count >= HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            --stack_count;
            pairs[pair_count].open_offset = stack[stack_count];
            pairs[pair_count].close_offset = (uint16_t)i;
            pairs[pair_count].depth = depth_stack[stack_count];
            ++pair_count;
        }

        if (source[i] == (uint8_t)'=') {
            if (equality_count >= HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            equality_offsets[equality_count++] = (uint16_t)i;
        }
    }

    if (stack_count != 0U ||
        pair_count != HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS ||
        equality_count != HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    hhs219_sort_parenthesis_pairs(pairs, pair_count);
    return HHS_EXACT_STATUS_OK;
}

static int hhs219_program_valid(const HHSExactPass219VM81ProgramV1 *program) {
    uint8_t seen_cells[HHS_EXACT_VM81_CELLS];
    uint32_t i;
    HHSExactPass219MonolithicDescriptorV1 descriptor;

    if (program == NULL ||
        program->struct_size < sizeof(*program) ||
        program->version != hhs219_adapter_version_word())
        return 0;

    if (program->instruction_count != HHS_EXACT_PASS219_VM81_PROGRAM_THREADS ||
        program->source_structure_thread_count !=
            HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS ||
        program->derived_thread_count != HHS_EXACT_PASS219_VM81_DERIVED_THREADS ||
        program->source_structure_thread_count + program->derived_thread_count !=
            program->instruction_count)
        return 0;

    if (!hhs219_source_identity_valid(program->source_sha256))
        return 0;

    if ((program->semantic_family_coverage_mask & ~HHS_EXACT_PASS219_FAMILY_REQUIRED) != 0U ||
        (program->equality_edge_coverage_mask &
         ~HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK) != 0U)
        return 0;

    /*
     * 1.21.3 can prove source structure and effectful exact-kernel execution,
     * but it cannot establish semantic completion of the full symbolic chain.
     * A caller is therefore never allowed to assert that completion bit.
     */
    if (program->source_structure_complete > 1U ||
        program->effectful_lowering_complete > 1U ||
        program->source_semantics_complete != 0U ||
        program->full_symbolic_identity_required != 1U)
        return 0;

    memset(seen_cells, 0, sizeof(seen_cells));
    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SYMBOL_COUNT; ++i) {
        const uint8_t cell = program->symbol_cell81[i];
        if (cell >= HHS_EXACT_VM81_CELLS || seen_cells[cell] != 0U)
            return 0;
        seen_cells[cell] = 1U;
    }

    if (program->x_cell81 != program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X] ||
        program->y_cell81 != program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y] ||
        program->z_cell81 != program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Z] ||
        program->w_cell81 != program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_W])
        return 0;

    for (i = 0U; i < program->instruction_count; ++i) {
        const HHSExactPass219VM81InstructionV1 *instruction = &program->instructions[i];
        uint32_t edge;
        if (instruction->struct_size < sizeof(*instruction) ||
            instruction->version != hhs219_adapter_version_word() ||
            instruction->opcode >= HHS_EXACT_PASS219_VM81_OP_COUNT ||
            instruction->a >= HHS_EXACT_VM81_CELLS ||
            instruction->b >= HHS_EXACT_VM81_CELLS ||
            instruction->c >= HHS_EXACT_VM81_CELLS ||
            instruction->constraint_group >= 72U ||
            instruction->phase >= 72U)
            return 0;

        if (i + 1U < program->instruction_count &&
            instruction->opcode == HHS_EXACT_PASS219_VM81_OP_HALT)
            return 0;

        for (edge = 0U; edge < HHS_EXACT_PASS219_VM81_NEXT_EDGES; ++edge) {
            if (instruction->next_enabled[edge] > 1U)
                return 0;
            if (instruction->next_enabled[edge] != 0U &&
                instruction->next_target[edge] >= program->instruction_count)
                return 0;
        }
    }

    if (program->instructions[program->instruction_count - 1U].opcode !=
        HHS_EXACT_PASS219_VM81_OP_HALT)
        return 0;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 0;
    if (descriptor.vm81_proof_required != 1U ||
        descriptor.raw_packet_can_prove != 0U)
        return 0;

    return 1;
}

static void hhs219_copy_instruction_to_kernel(
    const HHSExactPass219VM81InstructionV1 *source,
    Instruction *target
) {
    uint32_t edge;
    memset(target, 0, sizeof(*target));
    target->op = (Opcode)source->opcode;
    target->a = source->a;
    target->b = source->b;
    target->c = source->c;
    target->cg_id = source->constraint_group;
    target->phase = source->phase;
    for (edge = 0U; edge < HHS_EXACT_PASS219_VM81_NEXT_EDGES; ++edge) {
        target->next[edge].enabled = source->next_enabled[edge];
        target->next[edge].target = source->next_target[edge];
    }
}

static int hhs219_hash72_word_valid(const char value[HHS_EXACT_HASH72_STRLEN]) {
    return value != NULL && hash72_validate_word(value);
}

uint32_t hhs_exact_pass219_vm81_adapter_version(void) {
    return hhs219_adapter_version_word();
}

HHSExactStatus hhs_exact_pass219_vm81_lower_monolithic_structure(
    HHSExactPass219VM81ProgramV1 *out_program
) {
    uint8_t source[HHS_EXACT_PASS219_MONOLITHIC_NATIVE_SOURCE_LENGTH];
    size_t source_length = 0U;
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    HHS219ParenPair pairs[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint16_t equality_offsets[HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS];
    uint32_t i;
    uint32_t slot;

    if (out_program == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_program, 0, sizeof(*out_program));
    out_program->struct_size = (uint32_t)sizeof(*out_program);
    out_program->version = hhs219_adapter_version_word();
    out_program->instruction_count = HHS_EXACT_PASS219_VM81_PROGRAM_THREADS;
    out_program->source_structure_thread_count =
        HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS;
    out_program->derived_thread_count = HHS_EXACT_PASS219_VM81_DERIVED_THREADS;
    out_program->semantic_family_coverage_mask = HHS_EXACT_PASS219_FAMILY_REQUIRED;
    out_program->equality_edge_coverage_mask =
        HHS_EXACT_PASS219_MONOLITHIC_ALL_EDGE_MASK;
    out_program->source_structure_complete = 1U;
    out_program->effectful_lowering_complete = 1U;
    out_program->source_semantics_complete = 0U;
    out_program->full_symbolic_identity_required = 1U;

    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(
        out_program->source_sha256,
        descriptor.native_source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);

    if (hhs_exact_pass219_monolithic_native_source(
            source, sizeof(source), &source_length) != HHS_EXACT_STATUS_OK ||
        source_length != sizeof(source))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    if (hhs219_scan_source_structure(
            source, source_length, pairs, equality_offsets) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SYMBOL_COUNT; ++i)
        out_program->symbol_cell81[i] = (uint8_t)i;
    out_program->x_cell81 =
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X];
    out_program->y_cell81 =
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y];
    out_program->z_cell81 =
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Z];
    out_program->w_cell81 =
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_W];

    slot = 0U;
    for (i = 0U; i < HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS; ++i, ++slot) {
        const uint16_t span =
            (uint16_t)(pairs[i].close_offset - pairs[i].open_offset + 1U);
        hhs219_instruction_init(
            &out_program->instructions[slot],
            HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
            (uint8_t)((pairs[i].depth % 8U) + 1U),
            (uint8_t)((pairs[i].open_offset + pairs[i].close_offset) % HHS_EXACT_VM81_CELLS),
            (uint8_t)((span % 5U) + 1U),
            (uint8_t)((pairs[i].open_offset + i) % 72U),
            (uint8_t)(span % 72U));
    }

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS; ++i, ++slot) {
        hhs219_instruction_init(
            &out_program->instructions[slot],
            HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
            9U,
            (uint8_t)(equality_offsets[i] % HHS_EXACT_VM81_CELLS),
            (uint8_t)((i % 5U) + 1U),
            (uint8_t)((equality_offsets[i] + i) % 72U),
            (uint8_t)('=' % 72));
    }

    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_FAMILY_COUNT; ++i, ++slot) {
        HHSExactPass219MonolithicFamilySpanV1 span;
        uint32_t width;
        if (hhs_exact_pass219_monolithic_family_span(i, &span) != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        width = span.byte_end - span.byte_begin + 1U;
        hhs219_instruction_init(
            &out_program->instructions[slot],
            HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
            (uint8_t)(16U + i),
            (uint8_t)(span.byte_begin % HHS_EXACT_VM81_CELLS),
            (uint8_t)((width % 5U) + 1U),
            (uint8_t)(span.byte_end % 72U),
            (uint8_t)((i * 9U) % 72U));
    }

    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_MULXY,
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_XY],
        57U,
        0U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_MULYX,
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_YX],
        58U,
        36U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_QGU,
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_P_UPPER],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_T],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_DELTA],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Q],
        11U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_SWEEP81,
        0U, 0U, 0U, 60U, 0U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_CLOSE81,
        0U, 0U, 0U, 61U, 0U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_GATE_IDENTITY,
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y],
        out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_U],
        62U,
        0U);
    hhs219_instruction_init(
        &out_program->instructions[slot++],
        HHS_EXACT_PASS219_VM81_OP_HALT,
        0U, 0U, 0U, 0U, 0U);

    if (slot != HHS_EXACT_PASS219_VM81_PROGRAM_THREADS ||
        !hhs219_program_valid(out_program))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_execute_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219VM81ExecutionV1 *out_execution
) {
    VM81 vm;
    uint64_t iterations = 0U;
    uint32_t i;

    if (program == NULL || candidate_frame == NULL || out_execution == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs219_kernel_init_once())
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs219_program_valid(program))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memset(out_execution, 0, sizeof(*out_execution));
    out_execution->struct_size = (uint32_t)sizeof(*out_execution);
    out_execution->version = hhs219_adapter_version_word();
    out_execution->before_frame = *candidate_frame;
    memcpy(
        out_execution->source_sha256,
        program->source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);

    vm81_init(&vm, hhs219_source_seed(program->source_sha256), SEED_LOSHU);
    memcpy(vm.cells, candidate_frame->words, sizeof(vm.cells));

    vm.xyzw[0] = fold_word72(vm.cells[program->x_cell81]);
    vm.xyzw[1] = fold_word72(vm.cells[program->y_cell81]);
    vm.xyzw[2] = fold_word72(vm.cells[program->z_cell81]);
    vm.xyzw[3] = fold_word72(vm.cells[program->w_cell81]);
    refresh_phase8(&vm);
    memcpy(vm.genomic, vm.xyzw, sizeof(vm.genomic));

    vm.program_len = program->instruction_count;
    for (i = 0U; i < program->instruction_count; ++i)
        hhs219_copy_instruction_to_kernel(&program->instructions[i], &vm.program[i]);

    while (!vm.halted && iterations < HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS) {
        vm81_step(&vm);
        ++iterations;
    }

    if (!vm.halted || iterations == 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    memcpy(out_execution->after_frame.words, vm.cells, sizeof(vm.cells));
    memcpy(out_execution->previous_hash72,
           vm.last_receipt.prev_h72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_execution->state_hash72,
           vm.last_receipt.state_h72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_execution->receipt_hash72,
           vm.last_receipt.receipt_h72,
           HHS_EXACT_HASH72_STRLEN);

    out_execution->steps_executed = iterations;
    out_execution->last_receipt_step = vm.last_receipt.step;
    out_execution->identity_exact_witness = vm.last_receipt.identity_exact_witness;
    out_execution->orbit_period = vm.last_receipt.orbit_period;
    out_execution->witness_flags = vm.last_receipt.witness;
    out_execution->semantic_family_coverage_mask =
        program->semantic_family_coverage_mask;
    out_execution->equality_edge_coverage_mask =
        program->equality_edge_coverage_mask;

    out_execution->x_phase = vm.phase8[HHS_PHASE_X];
    out_execution->y_phase = vm.phase8[HHS_PHASE_Y];
    out_execution->z_phase = vm.phase8[HHS_PHASE_Z];
    out_execution->w_phase = vm.phase8[HHS_PHASE_W];
    out_execution->xy_phase = vm.phase8[HHS_PHASE_XY];
    out_execution->yx_phase = vm.phase8[HHS_PHASE_YX];
    out_execution->zw_phase = vm.phase8[HHS_PHASE_ZW];
    out_execution->wz_phase = vm.phase8[HHS_PHASE_WZ];

    out_execution->halted = vm.halted ? 1U : 0U;
    out_execution->converged = vm.converged ? 1U : 0U;
    out_execution->ledger_advanced = vm.last_receipt.ledger_advanced ? 1U : 0U;
    out_execution->identity_has_data = vm.last_receipt.identity_has_data ? 1U : 0U;
    out_execution->source_identity_valid =
        hhs219_source_identity_valid(program->source_sha256) ? 1U : 0U;
    out_execution->candidate_frame_bound =
        memcmp(&out_execution->before_frame,
               candidate_frame,
               sizeof(*candidate_frame)) == 0
            ? 1U
            : 0U;
    out_execution->source_structure_complete = program->source_structure_complete;
    out_execution->effectful_lowering_complete = program->effectful_lowering_complete;
    out_execution->source_semantics_complete = program->source_semantics_complete;
    out_execution->full_symbolic_identity_required =
        program->full_symbolic_identity_required;

    /*
     * The inherited check_gate_identity_exact() can currently reject or return
     * unresolved, but cannot emit PASS for the complete symbolic equation.
     */
    out_execution->full_symbolic_identity_gate_supported = 0U;
    out_execution->canonical_monolithic_proof = 0U;
    out_execution->floating_point_authority = 0U;
    out_execution->vm81_mutation_authority = 0U;
    out_execution->hash72_commit_authority = 0U;

    if (!hhs219_hash72_word_valid(out_execution->previous_hash72) ||
        !hhs219_hash72_word_valid(out_execution->state_hash72) ||
        !hhs219_hash72_word_valid(out_execution->receipt_hash72) ||
        out_execution->source_identity_valid != 1U ||
        out_execution->candidate_frame_bound != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    out_execution->exact_kernel_execution_observed = 1U;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_vm81_replay_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219VM81ExecutionV1 *expected,
    HHSExactPass219VM81ReplayV1 *out_replay
) {
    HHSExactStatus status;
    int phase_equal;

    if (program == NULL || candidate_frame == NULL ||
        expected == NULL || out_replay == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (expected->struct_size < sizeof(*expected) ||
        expected->version != hhs219_adapter_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;

    memset(out_replay, 0, sizeof(*out_replay));
    out_replay->struct_size = (uint32_t)sizeof(*out_replay);
    out_replay->version = hhs219_adapter_version_word();

    status = hhs_exact_pass219_vm81_execute_candidate(
        program, candidate_frame, &out_replay->replay);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_replay->frame_equal =
        memcmp(&out_replay->replay.after_frame,
               &expected->after_frame,
               sizeof(expected->after_frame)) == 0
            ? 1U
            : 0U;
    out_replay->previous_hash72_equal =
        memcmp(out_replay->replay.previous_hash72,
               expected->previous_hash72,
               HHS_EXACT_HASH72_STRLEN) == 0
            ? 1U
            : 0U;
    out_replay->state_hash72_equal =
        memcmp(out_replay->replay.state_hash72,
               expected->state_hash72,
               HHS_EXACT_HASH72_STRLEN) == 0
            ? 1U
            : 0U;
    out_replay->receipt_hash72_equal =
        memcmp(out_replay->replay.receipt_hash72,
               expected->receipt_hash72,
               HHS_EXACT_HASH72_STRLEN) == 0
            ? 1U
            : 0U;
    out_replay->witness_equal =
        out_replay->replay.witness_flags == expected->witness_flags &&
        out_replay->replay.identity_exact_witness == expected->identity_exact_witness &&
        out_replay->replay.identity_has_data == expected->identity_has_data
            ? 1U
            : 0U;
    out_replay->steps_equal =
        out_replay->replay.steps_executed == expected->steps_executed &&
        out_replay->replay.last_receipt_step == expected->last_receipt_step
            ? 1U
            : 0U;

    phase_equal =
        out_replay->replay.x_phase == expected->x_phase &&
        out_replay->replay.y_phase == expected->y_phase &&
        out_replay->replay.z_phase == expected->z_phase &&
        out_replay->replay.w_phase == expected->w_phase &&
        out_replay->replay.xy_phase == expected->xy_phase &&
        out_replay->replay.yx_phase == expected->yx_phase &&
        out_replay->replay.zw_phase == expected->zw_phase &&
        out_replay->replay.wz_phase == expected->wz_phase;
    out_replay->phase_surface_equal = phase_equal ? 1U : 0U;

    out_replay->source_identity_equal =
        memcmp(out_replay->replay.source_sha256,
               expected->source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0 &&
        out_replay->replay.source_identity_valid == expected->source_identity_valid
            ? 1U
            : 0U;
    out_replay->coverage_equal =
        out_replay->replay.semantic_family_coverage_mask ==
            expected->semantic_family_coverage_mask &&
        out_replay->replay.equality_edge_coverage_mask ==
            expected->equality_edge_coverage_mask &&
        out_replay->replay.source_structure_complete ==
            expected->source_structure_complete &&
        out_replay->replay.effectful_lowering_complete ==
            expected->effectful_lowering_complete &&
        out_replay->replay.source_semantics_complete ==
            expected->source_semantics_complete
            ? 1U
            : 0U;
    out_replay->authority_boundary_equal =
        out_replay->replay.full_symbolic_identity_required ==
            expected->full_symbolic_identity_required &&
        out_replay->replay.full_symbolic_identity_gate_supported ==
            expected->full_symbolic_identity_gate_supported &&
        out_replay->replay.canonical_monolithic_proof ==
            expected->canonical_monolithic_proof &&
        out_replay->replay.floating_point_authority ==
            expected->floating_point_authority &&
        out_replay->replay.vm81_mutation_authority ==
            expected->vm81_mutation_authority &&
        out_replay->replay.hash72_commit_authority ==
            expected->hash72_commit_authority
            ? 1U
            : 0U;

    out_replay->replay_verified =
        out_replay->frame_equal == 1U &&
        out_replay->previous_hash72_equal == 1U &&
        out_replay->state_hash72_equal == 1U &&
        out_replay->receipt_hash72_equal == 1U &&
        out_replay->witness_equal == 1U &&
        out_replay->steps_equal == 1U &&
        out_replay->phase_surface_equal == 1U &&
        out_replay->source_identity_equal == 1U &&
        out_replay->coverage_equal == 1U &&
        out_replay->authority_boundary_equal == 1U &&
        out_replay->replay.exact_kernel_execution_observed == 1U
            ? 1U
            : 0U;

    return out_replay->replay_verified == 1U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
