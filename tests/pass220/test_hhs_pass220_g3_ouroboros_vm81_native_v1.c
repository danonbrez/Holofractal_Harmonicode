#define main hhs_pass220_i028_embedded_vm81_main
#include "../../hhs_runtime/HARMONICODE_VM_RUNTIME.c"
#undef main

#include <assert.h>
#include <stdint.h>
#include <stdio.h>

static void add(VM81 *vm, Opcode op, uint8_t a, uint8_t b, uint8_t c) {
    vm->program[vm->program_len++] = instruction_make(op, a, b, c, 41, 0);
}

static void init_vm(VM81 *vm) {
    assert(init_hash72());
    vm81_init(vm, 123456789ULL, SEED_PLAIN);
    vm->program_len = 0;
    vm->pc = 0;
    vm->halted = 0;
}

static void test_opcode_values(void) {
    assert(OP_HALT == 23);
    assert(OP_G3_IEEE_INGRESS == 24);
    assert(OP_G3_PAL_FOLD == 25);
    assert(OP_G3_RNA_TRANSCRIBE == 26);
    assert(OP_G3_BIND_P4_C4 == 27);
    assert(OP_G3_CONSTRAIN_C5 == 28);
    assert(OP_G3_CONSTRAIN_C7 == 29);
    assert(OP_G3_SERIALIZE_A2_C1 == 30);
    assert(OP_G3_ZERO_SUM_CLOSE == 31);
    assert(OP_G3_RNA_REVERSE == 32);
    assert(OP_G3_IEEE_EGRESS == 33);
    assert(OP_G3_OUROBOROS == 34);
    assert(OP__COUNT == 35);
}

static void test_sequential_path(void) {
    VM81 vm;
    const uint64_t raw = UINT64_C(0x3ff0000000000000);
    const uint32_t expected[10] = {
        W_G3_IEEE_INGRESS,
        W_G3_PAL_FOLD,
        W_G3_RNA_TRANSCRIBE,
        W_G3_BIND_P4_C4,
        W_G3_CONSTRAIN_C5,
        W_G3_CONSTRAIN_C7,
        W_G3_SERIALIZE_A2_C1,
        W_G3_ZERO_SUM_CLOSE,
        W_G3_RNA_REVERSE,
        W_G3_IEEE_EGRESS,
    };

    init_vm(&vm);
    vm.cells[0] = raw;
    vm.cells[1] = 9u; /* P^4 */
    vm.cells[2] = 9u; /* c^4 */

    add(&vm, OP_G3_IEEE_INGRESS, 0, 0, 10);
    add(&vm, OP_G3_PAL_FOLD, 0, 0, 11);
    add(&vm, OP_G3_RNA_TRANSCRIBE, 0, 0, 12);
    add(&vm, OP_G3_BIND_P4_C4, 1, 2, 13);
    add(&vm, OP_G3_CONSTRAIN_C5, 0, 0, 14);
    add(&vm, OP_G3_CONSTRAIN_C7, 0, 0, 15);
    add(&vm, OP_G3_SERIALIZE_A2_C1, 0, 0, 16);
    add(&vm, OP_G3_ZERO_SUM_CLOSE, 0, 0, 17);
    add(&vm, OP_G3_RNA_REVERSE, 0, 0, 18);
    add(&vm, OP_G3_IEEE_EGRESS, 0, 0, 19);

    for (int i = 0; i < 10; i++) {
        vm81_step(&vm);
        assert(vm.last_receipt.ledger_advanced == 1);
        assert((vm.last_receipt.witness & expected[i]) != 0u);
        assert((vm.last_receipt.witness & W_G3_REJECT) == 0u);
        assert(vm.step == (uint64_t)(i + 1));
    }

    assert(vm.g3.stage_mask == G3_STAGE_ALL);
    assert(vm.g3.rejected == 0u);
    assert(vm.g3.bigint_lo_shu_value == 1u);
    assert(vm.g3.bigint_lo_shu_local_index == 7u);
    assert(vm.g3.nucleus_zero_sum == 0);
    assert(vm.g3.ieee_in_bits == raw);
    assert(vm.g3.ieee_out_bits == raw);
    assert(vm.cells[19] == raw);
}

static void test_c5_c7_c1_bypass_rejected_without_step(void) {
    VM81 vm;

    init_vm(&vm);
    add(&vm, OP_G3_CONSTRAIN_C5, 0, 0, 10);
    vm81_step(&vm);
    assert(vm.step == 0u);
    assert(vm.last_receipt.ledger_advanced == 0);
    assert((vm.last_receipt.witness & W_G3_REJECT) != 0u);
    assert((vm.last_receipt.witness & W_LEDGER_FROZEN) != 0u);

    init_vm(&vm);
    vm.cells[0] = UINT64_C(0x4000000000000000);
    vm.cells[1] = 9u;
    vm.cells[2] = 9u;
    add(&vm, OP_G3_IEEE_INGRESS, 0, 0, 10);
    add(&vm, OP_G3_PAL_FOLD, 0, 0, 11);
    add(&vm, OP_G3_RNA_TRANSCRIBE, 0, 0, 12);
    add(&vm, OP_G3_BIND_P4_C4, 1, 2, 13);
    add(&vm, OP_G3_CONSTRAIN_C7, 0, 0, 14);
    for (int i = 0; i < 4; i++)
        vm81_step(&vm);
    assert(vm.step == 4u);
    vm81_step(&vm);
    assert(vm.step == 4u);
    assert(vm.last_receipt.ledger_advanced == 0);
    assert((vm.last_receipt.witness & W_G3_REJECT) != 0u);

    init_vm(&vm);
    vm.cells[0] = UINT64_C(0x4008000000000000);
    add(&vm, OP_G3_IEEE_INGRESS, 0, 0, 10);
    add(&vm, OP_G3_PAL_FOLD, 0, 0, 11);
    add(&vm, OP_G3_RNA_TRANSCRIBE, 0, 0, 12);
    add(&vm, OP_G3_SERIALIZE_A2_C1, 0, 0, 13);
    for (int i = 0; i < 3; i++)
        vm81_step(&vm);
    assert(vm.step == 3u);
    vm81_step(&vm);
    assert(vm.step == 3u);
    assert(vm.last_receipt.ledger_advanced == 0);
    assert((vm.last_receipt.witness & W_G3_REJECT) != 0u);
}

static void test_fused_success_and_mismatch_rollback(void) {
    VM81 vm;
    const uint64_t raw = UINT64_C(0x7ff8000000000001);

    init_vm(&vm);
    vm.cells[0] = raw;
    vm.cells[1] = 9u;
    vm.cells[2] = 9u;
    add(&vm, OP_G3_OUROBOROS, 0, 1, 2);
    vm81_step(&vm);
    assert(vm.step == 1u);
    assert(vm.last_receipt.ledger_advanced == 1);
    assert((vm.last_receipt.witness & W_G3_OUROBOROS) != 0u);
    assert((vm.last_receipt.witness & W_G3_REJECT) == 0u);
    assert(vm.g3.stage_mask == G3_STAGE_ALL);
    assert(vm.g3.ieee_in_bits == raw);
    assert(vm.g3.ieee_out_bits == raw);
    assert(vm.cells[0] == raw);

    init_vm(&vm);
    vm.cells[0] = raw;
    vm.cells[1] = 9u;
    vm.cells[2] = 8u;
    add(&vm, OP_G3_OUROBOROS, 0, 1, 2);
    vm81_step(&vm);
    assert(vm.step == 0u);
    assert(vm.last_receipt.ledger_advanced == 0);
    assert((vm.last_receipt.witness & W_G3_REJECT) != 0u);
    assert(vm.cells[0] == raw);
    assert(vm.cells[1] == 9u);
    assert(vm.cells[2] == 8u);
}

int main(void) {
    test_opcode_values();
    test_sequential_path();
    test_c5_c7_c1_bypass_rejected_without_step();
    test_fused_success_and_mismatch_rollback();
    puts("PASS220_I028_G3_OUROBOROS_NATIVE=PASS");
    return 0;
}
