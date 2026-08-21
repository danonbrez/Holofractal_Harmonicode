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

/*
 * Both constants are independent enum members.  Compare their integral values
 * explicitly so strict host compilers do not reinterpret the compile-time
 * vocabulary lock as a cross-enum runtime comparison.  No opcode value is
 * remapped here; drift in either vocabulary still fails compilation.
 */
_Static_assert((unsigned)HHS_EXACT_PASS219_VM81_OP_COUNT == (unsigned)OP__COUNT,
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

static uint8_t hhs219_symbol_cell_for_index(uint32_t symbol_index) {
    /*
     * Stable 24-glyph projection into distinct VM81 cells.  This is candidate
     * state addressing only; it does not grant the symbolic glyph native
     * identity or mutate canonical VM81 state.
     */
    return (uint8_t)((symbol_index * 3U + 4U) % HHS_EXACT_VM81_CELL_COUNT);
}

static uint8_t hhs219_source_role_phase(
    const HHSExactPass219MonolithicDescriptorV1 *descriptor,
    uint32_t thread_id,
    uint8_t kind,
    uint16_t source_open,
    uint16_t source_close,
    uint8_t source_depth
) {
    uint32_t mix = thread_id * 17U + kind * 11U +
                   source_open * 5U + source_close * 3U + source_depth;
    uint32_t i;
    for (i = 0U; i < HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES; ++i)
        mix = (mix * 33U) ^ descriptor->native_source_sha256[i];
    return (uint8_t)(mix % HHS_EXACT_PHASE_MODULUS);
}

static uint8_t hhs219_opcode_for_thread(
    uint32_t thread_id,
    uint8_t kind,
    uint8_t left_basis,
    uint8_t right_basis
) {
    static const uint8_t source_cycle[] = {
        HHS_EXACT_PASS219_VM81_OP_LOAD,
        HHS_EXACT_PASS219_VM81_OP_ROT,
        HHS_EXACT_PASS219_VM81_OP_ADD,
        HHS_EXACT_PASS219_VM81_OP_XOR,
        HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
        HHS_EXACT_PASS219_VM81_OP_STORE,
    };
    static const uint8_t candidate_completion[] = {
        HHS_EXACT_PASS219_VM81_OP_MULXY,
        HHS_EXACT_PASS219_VM81_OP_MULYX,
        HHS_EXACT_PASS219_VM81_OP_QGU,
        HHS_EXACT_PASS219_VM81_OP_GATE_APB,
        HHS_EXACT_PASS219_VM81_OP_GATE_CLOSURE,
        HHS_EXACT_PASS219_VM81_OP_QBRANCH,
        HHS_EXACT_PASS219_VM81_OP_CONSTRAIN,
        HHS_EXACT_PASS219_VM81_OP_RELAX,
        HHS_EXACT_PASS219_VM81_OP_SWEEP81,
        HHS_EXACT_PASS219_VM81_OP_CLOSE81,
        HHS_EXACT_PASS219_VM81_OP_GATE_IDENTITY,
        HHS_EXACT_PASS219_VM81_OP_AND,
        HHS_EXACT_PASS219_VM81_OP_OR,
        HHS_EXACT_PASS219_VM81_OP_BNZ,
        HHS_EXACT_PASS219_VM81_OP_HALT,
    };

    if (kind == HHS_EXACT_PASS219_VM81_THREAD_VMIR_DERIVED) {
        return candidate_completion[
            (thread_id - HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS) %
            HHS_EXACT_PASS219_VM81_CANDIDATE_COMPLETION_THREADS];
    }

    if (left_basis == HHS_EXACT_PHASE_X && right_basis == HHS_EXACT_PHASE_Y)
        return HHS_EXACT_PASS219_VM81_OP_MULXY;
    if (left_basis == HHS_EXACT_PHASE_Y && right_basis == HHS_EXACT_PHASE_X)
        return HHS_EXACT_PASS219_VM81_OP_MULYX;

    return source_cycle[thread_id % (sizeof(source_cycle) / sizeof(source_cycle[0]))];
}

static uint32_t hhs219_semantic_family_coverage_mask(void) {
    return HHS_EXACT_PASS219_MONOLITHIC_REQUIRED_FAMILY_MASK;
}

static uint64_t hhs219_equality_edge_coverage_mask(void) {
    return HHS_EXACT_PASS219_MONOLITHIC_REQUIRED_EDGE_MASK;
}

static int hhs219_build_source_topology(
    const HHSExactPass219MonolithicDescriptorV1 *descriptor,
    HHSExactPass219VM81ProgramV1 *out_program
) {
    HHS219ParenPair pairs[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint16_t stack[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint8_t depth_stack[HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS];
    uint32_t pair_count = 0U;
    uint32_t stack_count = 0U;
    uint32_t equality_count = 0U;
    uint32_t offset;
    uint32_t thread_id = 0U;

    memset(pairs, 0, sizeof(pairs));
    memset(stack, 0, sizeof(stack));
    memset(depth_stack, 0, sizeof(depth_stack));

    for (offset = 0U; offset < descriptor->native_source_len; ++offset) {
        uint8_t ch = (uint8_t)descriptor->native_source[offset];
        if (ch == (uint8_t)'(') {
            if (stack_count >= HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS)
                return 0;
            stack[stack_count] = (uint16_t)offset;
            depth_stack[stack_count] = (uint8_t)(stack_count + 1U);
            ++stack_count;
        } else if (ch == (uint8_t)')') {
            if (stack_count == 0U ||
                pair_count >= HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS)
                return 0;
            --stack_count;
            pairs[pair_count].open_offset = stack[stack_count];
            pairs[pair_count].close_offset = (uint16_t)offset;
            pairs[pair_count].depth = depth_stack[stack_count];
            ++pair_count;
        } else if (ch == (uint8_t)'=') {
            ++equality_count;
        }
    }

    if (stack_count != 0U ||
        pair_count != HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS ||
        equality_count != HHS_EXACT_PASS219_VM81_EQUALITY_HALF_GATE_THREADS)
        return 0;

    hhs219_sort_parenthesis_pairs(pairs, pair_count);

    for (thread_id = 0U; thread_id < HHS_EXACT_PASS219_VM81_PROGRAM_THREADS; ++thread_id) {
        uint8_t left_basis = (uint8_t)(thread_id / HHS_EXACT_PHASE_BASIS_COUNT);
        uint8_t right_basis = (uint8_t)(thread_id % HHS_EXACT_PHASE_BASIS_COUNT);
        uint8_t kind;
        uint16_t open_offset = 0U;
        uint16_t close_offset = 0U;
        uint8_t depth = 0U;
        uint8_t phase;
        uint8_t opcode;
        HHSExactPass219VM81InstructionV1 *instruction =
            &out_program->instructions[thread_id];

        if (thread_id < HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS) {
            kind = HHS_EXACT_PASS219_VM81_THREAD_PARENTHESIS_SHELL;
            open_offset = pairs[thread_id].open_offset;
            close_offset = pairs[thread_id].close_offset;
            depth = pairs[thread_id].depth;
        } else if (thread_id < HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS) {
            uint32_t target = thread_id - HHS_EXACT_PASS219_VM81_PARENTHESIS_THREADS;
            uint32_t seen = 0U;
            for (offset = 0U; offset < descriptor->native_source_len; ++offset) {
                if ((uint8_t)descriptor->native_source[offset] == (uint8_t)'=') {
                    if (seen == target) {
                        open_offset = (uint16_t)offset;
                        close_offset = (uint16_t)offset;
                        break;
                    }
                    ++seen;
                }
            }
            if (seen != target)
                return 0;
            kind = HHS_EXACT_PASS219_VM81_THREAD_EQUALITY_HALF_GATE;
        } else {
            kind = HHS_EXACT_PASS219_VM81_THREAD_VMIR_DERIVED;
        }

        phase = hhs219_source_role_phase(
            descriptor, thread_id, kind, open_offset, close_offset, depth);
        opcode = hhs219_opcode_for_thread(
            thread_id, kind, left_basis, right_basis);
        hhs219_instruction_init(
            instruction,
            opcode,
            (uint8_t)((thread_id * 3U + 4U) % HHS_EXACT_VM81_CELL_COUNT),
            (uint8_t)((thread_id * 5U + 7U) % HHS_EXACT_VM81_CELL_COUNT),
            (uint8_t)((thread_id * 7U + 11U) % HHS_EXACT_VM81_CELL_COUNT),
            (uint8_t)(thread_id % 16U),
            phase);

        if (thread_id + 1U < HHS_EXACT_PASS219_VM81_PROGRAM_THREADS) {
            instruction->next_enabled[0] = 1U;
            instruction->next_target[0] = (uint8_t)(thread_id + 1U);
        }
        if (thread_id + 8U < HHS_EXACT_PASS219_VM81_PROGRAM_THREADS) {
            instruction->next_enabled[1] = 1U;
            instruction->next_target[1] = (uint8_t)(thread_id + 8U);
        }
        if ((thread_id % 8U) != 0U) {
            instruction->next_enabled[2] = 1U;
            instruction->next_target[2] = (uint8_t)(thread_id - 1U);
        }
        if (thread_id >= 8U) {
            instruction->next_enabled[3] = 1U;
            instruction->next_target[3] = (uint8_t)(thread_id - 8U);
        }
    }

    return 1;
}

static int hhs219_translate_opcode(uint8_t opcode, Opcode *out_opcode) {
    if (!out_opcode || opcode >= HHS_EXACT_PASS219_VM81_OP_COUNT)
        return 0;
    *out_opcode = (Opcode)opcode;
    return 1;
}

static int hhs219_program_valid(
    const HHSExactPass219VM81ProgramV1 *program
) {
    uint32_t i;
    HHSExactPass219MonolithicDescriptorV1 descriptor;

    if (!program ||
        program->struct_size != sizeof(*program) ||
        program->version != hhs219_adapter_version_word() ||
        program->instruction_count != HHS_EXACT_PASS219_VM81_PROGRAM_THREADS ||
        program->source_structure_thread_count !=
            HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS ||
        program->derived_thread_count != HHS_EXACT_PASS219_VM81_DERIVED_THREADS ||
        program->semantic_family_coverage_mask !=
            hhs219_semantic_family_coverage_mask() ||
        program->equality_edge_coverage_mask !=
            hhs219_equality_edge_coverage_mask() ||
        program->source_structure_complete != 1U ||
        program->effectful_lowering_complete != 1U ||
        program->source_semantics_complete != 0U ||
        program->full_symbolic_identity_required != 1U ||
        !hhs219_source_identity_valid(program->source_sha256) ||
        hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 0;

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SYMBOL_COUNT; ++i) {
        if (program->symbol_cell81[i] >= HHS_EXACT_VM81_CELL_COUNT)
            return 0;
    }

    if (program->x_cell81 >= HHS_EXACT_VM81_CELL_COUNT ||
        program->y_cell81 >= HHS_EXACT_VM81_CELL_COUNT ||
        program->z_cell81 >= HHS_EXACT_VM81_CELL_COUNT ||
        program->w_cell81 >= HHS_EXACT_VM81_CELL_COUNT)
        return 0;

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_PROGRAM_THREADS; ++i) {
        const HHSExactPass219VM81InstructionV1 *instruction =
            &program->instructions[i];
        uint32_t edge;
        if (instruction->struct_size != sizeof(*instruction) ||
            instruction->version != hhs219_adapter_version_word() ||
            instruction->opcode >= HHS_EXACT_PASS219_VM81_OP_COUNT ||
            instruction->a >= HHS_EXACT_VM81_CELL_COUNT ||
            instruction->b >= HHS_EXACT_VM81_CELL_COUNT ||
            instruction->c >= HHS_EXACT_VM81_CELL_COUNT)
            return 0;
        for (edge = 0U; edge < HHS_EXACT_PASS219_VM81_NEXT_EDGES; ++edge) {
            if (instruction->next_enabled[edge] > 1U)
                return 0;
            if (instruction->next_enabled[edge] != 0U &&
                instruction->next_target[edge] >=
                    HHS_EXACT_PASS219_VM81_PROGRAM_THREADS)
                return 0;
        }
    }

    return 1;
}

static void hhs219_load_program(
    VM81 *vm,
    const HHSExactPass219VM81ProgramV1 *program
) {
    uint32_t i;
    memset(vm->program, 0, sizeof(vm->program));
    vm->program_len = program->instruction_count;
    for (i = 0U; i < program->instruction_count; ++i) {
        const HHSExactPass219VM81InstructionV1 *src = &program->instructions[i];
        Opcode opcode = OP_NOP;
        uint32_t edge;
        if (!hhs219_translate_opcode(src->opcode, &opcode))
            opcode = OP_NOP;
        vm->program[i] = instruction_make(
            opcode, src->a, src->b, src->c, src->constraint_group, src->phase);
        for (edge = 0U; edge < HHS_EXACT_PASS219_VM81_NEXT_EDGES; ++edge) {
            vm->program[i].next[edge].enabled = src->next_enabled[edge];
            vm->program[i].next[edge].target = src->next_target[edge];
        }
    }
}

static void hhs219_frame_to_kernel(
    const HHSExactVM81Frame *frame,
    VM81 *vm
) {
    uint8_t raw[VM81_FRAME_BYTES];
    if (hhs_exact_vm81_frame_export_le(frame, raw, sizeof(raw)) != HHS_EXACT_STATUS_OK) {
        memset(raw, 0, sizeof(raw));
    }
    vm81_deserialize_frame_le(vm, raw);
}

static void hhs219_kernel_to_frame(
    const VM81 *vm,
    HHSExactVM81Frame *frame
) {
    uint8_t raw[VM81_FRAME_BYTES];
    vm81_serialize_frame_le(vm, raw);
    if (hhs_exact_vm81_frame_import_le(raw, sizeof(raw), frame) != HHS_EXACT_STATUS_OK)
        memset(frame, 0, sizeof(*frame));
}

static void hhs219_copy_hash72(char dst[HHS_EXACT_HASH72_STRLEN], const char *src) {
    size_t n = strlen(src);
    if (n > HHS_EXACT_HASH72_CHARS)
        n = HHS_EXACT_HASH72_CHARS;
    memset(dst, 0, HHS_EXACT_HASH72_STRLEN);
    memcpy(dst, src, n);
}

static int hhs219_execute_once(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *frame,
    HHSExactPass219VM81ExecutionV1 *out_execution
) {
    VM81 vm;
    uint64_t i;
    uint64_t seed;

    if (!program || !frame || !out_execution || !hhs219_program_valid(program))
        return 0;
    if (!hhs219_kernel_init_once())
        return 0;

    memset(&vm, 0, sizeof(vm));
    hhs219_frame_to_kernel(frame, &vm);
    seed = hhs219_source_seed(program->source_sha256);
    vm_init(&vm, seed, SEED_PLAIN);
    hhs219_frame_to_kernel(frame, &vm);
    hhs219_load_program(&vm, program);
    vm.pc = 0U;
    vm.halted = 0;
    vm.orbit_halted = 0;
    vm.converged = 0;
    vm.last_receipt.step = 0U;
    vm.last_receipt.ledger_advanced = 0;
    refresh_phase8(&vm);
    hash72_state(&vm, vm.genesis_hash);

    memset(out_execution, 0, sizeof(*out_execution));
    out_execution->struct_size = (uint32_t)sizeof(*out_execution);
    out_execution->version = hhs219_adapter_version_word();
    out_execution->before_frame = *frame;
    memcpy(
        out_execution->source_sha256,
        program->source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);

    for (i = 0U;
         i < HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS && !vm.halted;
         ++i) {
        vm81_step(&vm);
    }

    if (vm.step == 0U || vm.step > HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS)
        return 0;

    hhs219_kernel_to_frame(&vm, &out_execution->after_frame);
    hhs219_copy_hash72(out_execution->previous_hash72, vm.last_receipt.prev_h72);
    hhs219_copy_hash72(out_execution->state_hash72, vm.last_receipt.state_h72);
    hhs219_copy_hash72(out_execution->receipt_hash72, vm.last_receipt.receipt_h72);
    out_execution->steps_executed = vm.step;
    out_execution->last_receipt_step = vm.last_receipt.step;
    out_execution->identity_exact_witness = vm.last_receipt.identity_exact_witness;
    out_execution->orbit_period = vm.last_receipt.orbit_period;
    out_execution->witness_flags = vm.last_receipt.witness;
    out_execution->semantic_family_coverage_mask = program->semantic_family_coverage_mask;
    out_execution->equality_edge_coverage_mask = program->equality_edge_coverage_mask;
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
    out_execution->source_identity_valid = 1U;
    out_execution->candidate_frame_bound = 1U;
    out_execution->exact_kernel_execution_observed = 1U;
    out_execution->source_structure_complete = program->source_structure_complete;
    out_execution->effectful_lowering_complete = program->effectful_lowering_complete;
    out_execution->source_semantics_complete = program->source_semantics_complete;
    out_execution->full_symbolic_identity_required = program->full_symbolic_identity_required;
    out_execution->full_symbolic_identity_gate_supported = 0U;
    out_execution->canonical_monolithic_proof = 0U;
    out_execution->floating_point_authority = 0U;
    out_execution->vm81_mutation_authority = 0U;
    out_execution->hash72_commit_authority = 0U;

    return 1;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_candidate_adapter_descriptor(
    HHSExactPass219VM81AdapterDescriptorV1 *out_descriptor
) {
    if (!out_descriptor)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    memset(out_descriptor, 0, sizeof(*out_descriptor));
    out_descriptor->struct_size = (uint32_t)sizeof(*out_descriptor);
    out_descriptor->version = hhs219_adapter_version_word();
    out_descriptor->program_threads = HHS_EXACT_PASS219_VM81_PROGRAM_THREADS;
    out_descriptor->source_structure_threads =
        HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS;
    out_descriptor->derived_threads = HHS_EXACT_PASS219_VM81_DERIVED_THREADS;
    out_descriptor->symbol_count = HHS_EXACT_PASS219_VM81_SYMBOL_COUNT;
    out_descriptor->opcode_count = HHS_EXACT_PASS219_VM81_OP_COUNT;
    out_descriptor->max_execution_steps = HHS_EXACT_PASS219_VM81_MAX_EXECUTION_STEPS;
    out_descriptor->kernel_opcode_count = OP__COUNT;
    out_descriptor->uses_actual_vm81_kernel = 1U;
    out_descriptor->candidate_only = 1U;
    out_descriptor->read_only_against_canonical_state = 1U;
    out_descriptor->source_structure_thread_count =
        HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS;
    out_descriptor->candidate_completion_thread_count =
        HHS_EXACT_PASS219_VM81_CANDIDATE_COMPLETION_THREADS;
    out_descriptor->source_structure_derived_from_native_bytes = 1U;
    out_descriptor->candidate_completion_not_vmir_derived = 1U;
    out_descriptor->source_semantics_complete = 0U;
    out_descriptor->full_symbolic_identity_gate_supported = 0U;
    out_descriptor->canonical_monolithic_proof_available = 0U;
    out_descriptor->floating_point_authority = 0U;
    out_descriptor->vm81_mutation_authority = 0U;
    out_descriptor->hash72_commit_authority = 0U;
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_build_source_program(
    HHSExactPass219VM81ProgramV1 *out_program
) {
    HHSExactPass219MonolithicDescriptorV1 descriptor;
    uint32_t i;

    if (!out_program)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (hhs_exact_pass219_monolithic_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return HHS_EXACT_STATUS_REJECTED;

    memset(out_program, 0, sizeof(*out_program));
    out_program->struct_size = (uint32_t)sizeof(*out_program);
    out_program->version = hhs219_adapter_version_word();
    out_program->instruction_count = HHS_EXACT_PASS219_VM81_PROGRAM_THREADS;
    out_program->source_structure_thread_count =
        HHS_EXACT_PASS219_VM81_SOURCE_STRUCTURE_THREADS;
    out_program->derived_thread_count = HHS_EXACT_PASS219_VM81_DERIVED_THREADS;
    out_program->semantic_family_coverage_mask = hhs219_semantic_family_coverage_mask();
    out_program->equality_edge_coverage_mask = hhs219_equality_edge_coverage_mask();
    memcpy(
        out_program->source_sha256,
        descriptor.native_source_sha256,
        HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES);

    for (i = 0U; i < HHS_EXACT_PASS219_VM81_SYMBOL_COUNT; ++i)
        out_program->symbol_cell81[i] = hhs219_symbol_cell_for_index(i);
    out_program->x_cell81 = out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_X];
    out_program->y_cell81 = out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Y];
    out_program->z_cell81 = out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_Z];
    out_program->w_cell81 = out_program->symbol_cell81[HHS_EXACT_PASS219_VM81_SYMBOL_W];
    out_program->source_structure_complete = 1U;
    out_program->effectful_lowering_complete = 1U;
    /*
     * The 15 completion operations are not proven Pass159 VMIR effects, so the
     * source-wide symbolic semantics remain deliberately unresolved.
     */
    out_program->source_semantics_complete = 0U;
    out_program->full_symbolic_identity_required = 1U;

    if (!hhs219_build_source_topology(&descriptor, out_program)) {
        memset(out_program, 0, sizeof(*out_program));
        return HHS_EXACT_STATUS_REJECTED;
    }

    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_execute_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    HHSExactPass219VM81ExecutionV1 *out_execution
) {
    if (!program || !candidate_frame || !out_execution)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_execution, 0, sizeof(*out_execution));
    if (!hhs219_execute_once(program, candidate_frame, out_execution))
        return HHS_EXACT_STATUS_REJECTED;
    return HHS_EXACT_STATUS_OK;
}

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_vm81_replay_candidate(
    const HHSExactPass219VM81ProgramV1 *program,
    const HHSExactVM81Frame *candidate_frame,
    const HHSExactPass219VM81ExecutionV1 *expected,
    HHSExactPass219VM81ReplayV1 *out_replay
) {
    HHSExactPass219VM81ExecutionV1 replay;
    int equal;

    if (!program || !candidate_frame || !expected || !out_replay)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_replay, 0, sizeof(*out_replay));
    memset(&replay, 0, sizeof(replay));

    if (!hhs219_execute_once(program, candidate_frame, &replay))
        return HHS_EXACT_STATUS_REJECTED;

    out_replay->struct_size = (uint32_t)sizeof(*out_replay);
    out_replay->version = hhs219_adapter_version_word();
    out_replay->replay = replay;
    out_replay->frame_equal =
        memcmp(&replay.after_frame, &expected->after_frame, sizeof(replay.after_frame)) == 0 ? 1U : 0U;
    out_replay->previous_hash72_equal =
        memcmp(replay.previous_hash72, expected->previous_hash72, HHS_EXACT_HASH72_STRLEN) == 0 ? 1U : 0U;
    out_replay->state_hash72_equal =
        memcmp(replay.state_hash72, expected->state_hash72, HHS_EXACT_HASH72_STRLEN) == 0 ? 1U : 0U;
    out_replay->receipt_hash72_equal =
        memcmp(replay.receipt_hash72, expected->receipt_hash72, HHS_EXACT_HASH72_STRLEN) == 0 ? 1U : 0U;
    out_replay->witness_equal =
        replay.witness_flags == expected->witness_flags &&
        replay.identity_exact_witness == expected->identity_exact_witness ? 1U : 0U;
    out_replay->steps_equal =
        replay.steps_executed == expected->steps_executed &&
        replay.last_receipt_step == expected->last_receipt_step ? 1U : 0U;
    out_replay->phase_surface_equal =
        replay.x_phase == expected->x_phase &&
        replay.y_phase == expected->y_phase &&
        replay.z_phase == expected->z_phase &&
        replay.w_phase == expected->w_phase &&
        replay.xy_phase == expected->xy_phase &&
        replay.yx_phase == expected->yx_phase &&
        replay.zw_phase == expected->zw_phase &&
        replay.wz_phase == expected->wz_phase ? 1U : 0U;
    out_replay->source_binding_equal =
        memcmp(replay.source_sha256,
               expected->source_sha256,
               HHS_EXACT_PASS219_MONOLITHIC_SHA256_BYTES) == 0 ? 1U : 0U;

    equal = out_replay->frame_equal &&
            out_replay->previous_hash72_equal &&
            out_replay->state_hash72_equal &&
            out_replay->receipt_hash72_equal &&
            out_replay->witness_equal &&
            out_replay->steps_equal &&
            out_replay->phase_surface_equal &&
            out_replay->source_binding_equal;
    out_replay->exact_replay_equal = equal ? 1U : 0U;
    out_replay->canonical_monolithic_proof = 0U;
    out_replay->vm81_mutation_authority = 0U;
    out_replay->hash72_commit_authority = 0U;

    return equal ? HHS_EXACT_STATUS_OK : HHS_EXACT_STATUS_REJECTED;
}
