// hhs_runtime/hhs_python_bridge.c
//
// HARMONICODE Python ABI bridge
//
// Purpose:
//   Deterministic Python/backend → VM execution boundary.
//
// Design rule:
//
//   Python is NOT authoritative.
//   VM81 runtime remains authoritative.
//
// Execution flow:
//
//   Python call
//       →
//   IR lowering
//       →
//   VM execution
//       →
//   receipt generation
//       →
//   replay verification
//       →
//   Hash72 sealing
//       →
//   result return
//

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include "HARMONICODE_VM_RUNTIME.h"


// ============================================================
// CONSTANTS
// ============================================================

#define HHS_MAX_BINDINGS        256
#define HHS_MAX_CALLSTACK       256
#define HHS_MAX_MODULE_NAME     128
#define HHS_MAX_FUNCTION_NAME   128


// ============================================================
// PYTHON RECEIPT
// ============================================================

typedef struct {

    uint64_t call_id;

    char module[HHS_MAX_MODULE_NAME];
    char function[HHS_MAX_FUNCTION_NAME];

    char input_hash72[73];
    char output_hash72[73];

    uint32_t witness;

    uint64_t parent_call;

    uint64_t replay_steps;

} HHS_PythonReceipt;


// ============================================================
// PYTHON BINDING
// ============================================================

typedef struct {

    const char *name;

    int (*fn)(
        VM81 *vm,
        HHS_IR_Block *blk,
        void *userdata
    );

} HHS_PythonBinding;


// ============================================================
// CALL FRAME
// ============================================================

typedef struct {

    uint64_t call_id;

    char module[HHS_MAX_MODULE_NAME];
    char function[HHS_MAX_FUNCTION_NAME];

} HHS_CallFrame;


// ============================================================
// BRIDGE RUNTIME
// ============================================================

typedef struct {

    HHS_PythonBinding bindings[HHS_MAX_BINDINGS];

    uint32_t binding_count;

    HHS_CallFrame stack[HHS_MAX_CALLSTACK];

    uint32_t stack_depth;

    uint64_t next_call_id;

} HHS_PythonBridgeRuntime;


// ============================================================
// GLOBAL BRIDGE
// ============================================================

static HHS_PythonBridgeRuntime g_bridge;


// ============================================================
// INIT
// ============================================================

void hhs_python_bridge_init(void) {

    memset(
        &g_bridge,
        0,
        sizeof(g_bridge)
    );

    g_bridge.next_call_id = 1;
}


// ============================================================
// REGISTER BINDING
// ============================================================

int hhs_python_register_binding(
    const char *name,
    int (*fn)(
        VM81 *,
        HHS_IR_Block *,
        void *
    )
) {

    if (
        g_bridge.binding_count >=
        HHS_MAX_BINDINGS
    ) {
        return 0;
    }

    HHS_PythonBinding *b =
        &g_bridge.bindings[
            g_bridge.binding_count++
        ];

    b->name = name;
    b->fn   = fn;

    return 1;
}


// ============================================================
// FIND BINDING
// ============================================================

static HHS_PythonBinding *
hhs_python_find_binding(
    const char *name
) {

    for (
        uint32_t i = 0;
        i < g_bridge.binding_count;
        i++
    ) {
        HHS_PythonBinding *b =
            &g_bridge.bindings[i];

        if (!strcmp(b->name, name))
            return b;
    }

    return NULL;
}


// ============================================================
// STACK PUSH
// ============================================================

static uint64_t hhs_push_callframe(
    const char *module,
    const char *function
) {

    if (
        g_bridge.stack_depth >=
        HHS_MAX_CALLSTACK
    ) {
        return 0;
    }

    uint64_t id =
        g_bridge.next_call_id++;

    HHS_CallFrame *f =
        &g_bridge.stack[
            g_bridge.stack_depth++
        ];

    memset(f, 0, sizeof(*f));

    f->call_id = id;

    strncpy(
        f->module,
        module,
        HHS_MAX_MODULE_NAME - 1
    );

    strncpy(
        f->function,
        function,
        HHS_MAX_FUNCTION_NAME - 1
    );

    return id;
}


// ============================================================
// STACK POP
// ============================================================

static void hhs_pop_callframe(void) {

    if (g_bridge.stack_depth > 0)
        g_bridge.stack_depth--;
}


// ============================================================
// RECEIPT BUILD
// ============================================================

static void hhs_build_python_receipt(
    VM81 *vm,
    HHS_PythonReceipt *r,
    const char *module,
    const char *function,
    uint64_t call_id,
    uint64_t replay_steps
) {

    memset(r, 0, sizeof(*r));

    r->call_id = call_id;

    strncpy(
        r->module,
        module,
        HHS_MAX_MODULE_NAME - 1
    );

    strncpy(
        r->function,
        function,
        HHS_MAX_FUNCTION_NAME - 1
    );

    strncpy(
        r->input_hash72,
        vm->last_receipt.prev_h72,
        72
    );

    strncpy(
        r->output_hash72,
        vm->last_receipt.state_h72,
        72
    );

    r->witness =
        vm->last_receipt.witness;

    r->replay_steps =
        replay_steps;

    if (g_bridge.stack_depth > 1) {

        r->parent_call =
            g_bridge.stack[
                g_bridge.stack_depth - 2
            ].call_id;
    }
}


// ============================================================
// EXECUTE BINDING
// ============================================================

int hhs_python_execute_binding(
    VM81 *vm,
    const char *module,
    const char *function,
    HHS_IR_Block *blk,
    void *userdata,
    HHS_PythonReceipt *receipt_out
) {

    if (
        !vm ||
        !function ||
        !blk
    ) {
        return 0;
    }

    HHS_PythonBinding *binding =
        hhs_python_find_binding(
            function
        );

    if (!binding)
        return 0;

    uint64_t call_id =
        hhs_push_callframe(
            module,
            function
        );

    if (!call_id)
        return 0;

    char before[73];
    char after[73];

    project_hash72(vm, before);

    uint64_t start_step =
        vm->step;

    int ok =
        binding->fn(
            vm,
            blk,
            userdata
        );

    project_hash72(vm, after);

    uint64_t replay_steps =
        vm->step - start_step;

    if (receipt_out) {

        hhs_build_python_receipt(
            vm,
            receipt_out,
            module,
            function,
            call_id,
            replay_steps
        );
    }

    hhs_pop_callframe();

    return ok;
}


// ============================================================
// DEFAULT EXECUTOR
// ============================================================

int hhs_python_default_executor(
    VM81 *vm,
    HHS_IR_Block *blk,
    void *userdata
) {

    (void)userdata;

    return hhs_ir_execute_block(
        vm,
        blk
    );
}


// ============================================================
// VERIFY EXECUTION
// ============================================================

int hhs_python_verify_execution(
    VM81 *vm,
    HHS_IR_Block *blk,
    HHS_PythonReceipt *receipt
) {

    if (
        !vm ||
        !blk ||
        !receipt
    ) {
        return 0;
    }

    char seal[73];

    memset(seal, 0, sizeof(seal));

    hhs_ir_hash72_seal(
        blk,
        seal
    );

    if (
        strcmp(
            seal,
            receipt->output_hash72
        ) == 0
    ) {
        return 1;
    }

    return 0;
}


// ============================================================
// DEBUG
// ============================================================

void hhs_python_print_receipt(
    HHS_PythonReceipt *r
) {

    if (!r)
        return;

    printf("\n");

    printf("---- PYTHON RECEIPT ----\n");

    printf(
        "call_id      : %llu\n",
        (unsigned long long)
        r->call_id
    );

    printf(
        "parent_call  : %llu\n",
        (unsigned long long)
        r->parent_call
    );

    printf(
        "module       : %s\n",
        r->module
    );

    printf(
        "function     : %s\n",
        r->function
    );

    printf(
        "input_hash72 : %s\n",
        r->input_hash72
    );

    printf(
        "output_hash72: %s\n",
        r->output_hash72
    );

    printf(
        "witness      : 0x%08X\n",
        r->witness
    );

    printf(
        "replay_steps : %llu\n",
        (unsigned long long)
        r->replay_steps
    );

    printf("------------------------\n");
}


// ============================================================
// AUTO-REGISTER DEFAULT EXECUTOR
// ============================================================

void hhs_python_register_defaults(void) {

    hhs_python_register_binding(
        "vm_execute",
        hhs_python_default_executor
    );
}