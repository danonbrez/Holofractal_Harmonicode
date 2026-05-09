// ============================================================================
// hhs_runtime/hhs_ir_lower_python.h
// HARMONICODE Python → IR lowering bridge
//
// Purpose:
//   Convert Python-side symbolic/runtime structures into deterministic
//   HHS IR graphs suitable for VM81 execution.
//
// This layer NEVER executes Python semantics directly.
// It ONLY lowers into deterministic IR.
// ============================================================================

#ifndef HHS_IR_LOWER_PYTHON_H
#define HHS_IR_LOWER_PYTHON_H

#include <stdint.h>
#include "hhs_ir.h"

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// LOWERING CONTEXT
// ============================================================================

typedef struct {

    uint64_t nodes_lowered;
    uint64_t branches_lowered;
    uint64_t tensors_lowered;

    uint64_t receipts_inserted;
    uint64_t qgu_inserted;
    uint64_t closure_gates_inserted;

    int deterministic_only;
    int auto_insert_receipts;
    int auto_insert_closure;

} HHSPythonLowerContext;

// ============================================================================
// PYTHON NODE TYPES
// ============================================================================

typedef enum {

    PY_NODE_UNKNOWN = 0,

    PY_NODE_CONST,
    PY_NODE_NAME,

    PY_NODE_ADD,
    PY_NODE_SUB,
    PY_NODE_MUL,
    PY_NODE_DIV,

    PY_NODE_XOR,
    PY_NODE_AND,
    PY_NODE_OR,

    PY_NODE_COMPARE,

    PY_NODE_ASSIGN,

    PY_NODE_BRANCH,
    PY_NODE_LOOP,

    PY_NODE_CALL,

    PY_NODE_QGU,
    PY_NODE_TENSOR,

    PY_NODE_RECEIPT,
    PY_NODE_CLOSURE,

    PY_NODE_PROGRAM

} HHSPythonNodeType;

// ============================================================================
// PYTHON AST NODE
// ============================================================================

typedef struct HHSPythonNode {

    HHSPythonNodeType type;

    char name[128];

    double value;

    struct HHSPythonNode *left;
    struct HHSPythonNode *right;

    struct HHSPythonNode **children;
    uint64_t child_count;

} HHSPythonNode;

// ============================================================================
// LOWERING API
// ============================================================================

// Initialize lowering context
void hhs_python_lower_init(
    HHSPythonLowerContext *ctx
);

// Lower a Python AST into IR
int hhs_lower_python_ast(
    HHSPythonLowerContext *ctx,
    HHSPythonNode *root,
    HHSIRProgram *program
);

// Lower single expression node
int hhs_lower_python_expr(
    HHSPythonLowerContext *ctx,
    HHSPythonNode *node,
    HHSIRProgram *program
);

// Lower branch structures
int hhs_lower_python_branch(
    HHSPythonLowerContext *ctx,
    HHSPythonNode *node,
    HHSIRProgram *program
);

// Lower tensor operations
int hhs_lower_python_tensor(
    HHSPythonLowerContext *ctx,
    HHSPythonNode *node,
    HHSIRProgram *program
);

// Lower QGU structures
int hhs_lower_python_qgu(
    HHSPythonLowerContext *ctx,
    HHSPythonNode *node,
    HHSIRProgram *program
);

// Insert deterministic receipt boundary
int hhs_insert_receipt_boundary(
    HHSPythonLowerContext *ctx,
    HHSIRProgram *program
);

// Insert closure verification gate
int hhs_insert_closure_gate(
    HHSPythonLowerContext *ctx,
    HHSIRProgram *program
);

// ============================================================================
// NODE BUILDERS
// ============================================================================

HHSPythonNode *hhs_py_node_new(
    HHSPythonNodeType type
);

HHSPythonNode *hhs_py_const(
    double value
);

HHSPythonNode *hhs_py_name(
    const char *name
);

HHSPythonNode *hhs_py_binary(
    HHSPythonNodeType type,
    HHSPythonNode *L,
    HHSPythonNode *R
);

HHSPythonNode *hhs_py_call(
    const char *name
);

void hhs_py_node_add_child(
    HHSPythonNode *parent,
    HHSPythonNode *child
);

void hhs_py_node_free(
    HHSPythonNode *node
);

// ============================================================================
// DEBUG
// ============================================================================

void hhs_python_node_dump(
    HHSPythonNode *node,
    int depth
);

void hhs_python_lower_stats(
    HHSPythonLowerContext *ctx
);

#ifdef __cplusplus
}
#endif

#endif

// ============================================================================
// END
// ============================================================================