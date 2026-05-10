// ============================================================================
// hhs_runtime/c/hhs_runtime_abi.h
// HARMONICODE / HHS
// CANONICAL RUNTIME ABI
//
// PURPOSE
// -------
// Permanent invariant bridge between:
//
//     - deterministic VM substrate
//     - Python orchestration layer
//     - graph memory
//     - receipt-chain persistence
//     - websocket transport
//     - vector cache systems
//     - replay engines
//     - multimodal routing
//
// DESIGN GOALS
// ------------
// - deterministic layout
// - stable ctypes/cffi bindings
// - replay-safe serialization
// - graph persistence compatibility
// - multimodal transport compatibility
// - forward-compatible envelope semantics
// - invariant-preserving runtime continuity
//
// CORE PRINCIPLE
// --------------
// Python MUST NOT guess runtime memory layout.
//
// ALL runtime communication MUST pass through this ABI.
//
//     Python
//        ↓
//       ABI
//        ↓
//     Deterministic VM
//
// ============================================================================

#ifndef HHS_RUNTIME_ABI_H
#define HHS_RUNTIME_ABI_H

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// STANDARD INCLUDES
// ============================================================================

#include <stdint.h>
#include <stddef.h>

// ============================================================================
// ABI VERSION
// ============================================================================

#define HHS_ABI_VERSION_MAJOR     1
#define HHS_ABI_VERSION_MINOR     0
#define HHS_ABI_VERSION_PATCH     0

#define HHS_HASH72_LEN            72
#define HHS_HASH72_STRLEN         73

#define HHS_RUNTIME_MAGIC         0x48485381ULL

// ============================================================================
// HASH72
// ============================================================================

typedef char HHSHash72[HHS_HASH72_STRLEN];

// ============================================================================
// CLOSURE CLASSES
// ============================================================================

typedef enum {

    HHS_CLOSURE_NONE            = 0,

    HHS_CLOSURE_TRANSPORT       = 1,
    HHS_CLOSURE_ORIENTATION     = 2,
    HHS_CLOSURE_CONSTRAINT      = 3,

    HHS_CLOSURE_CONVERGED       = 4

} HHSClosureClass;

// ============================================================================
// WITNESS FLAGS
// ============================================================================

typedef enum {

    W_QGU_APPLIED               = 1ULL << 0,

    W_CONSTRAINT_FIRED          = 1ULL << 1,

    W_TRANSPORT_CLOSED          = 1ULL << 2,
    W_ORIENTATION_CLOSED        = 1ULL << 3,
    W_CONSTRAINT_CLOSED         = 1ULL << 4,

    W_CONVERGED                 = 1ULL << 5,

    W_ORBIT_DETECTED            = 1ULL << 6,

    W_LEDGER_FROZEN             = 1ULL << 7,

    W_NONCOMMUTATIVE            = 1ULL << 8,

    W_QBRANCH_TAKEN             = 1ULL << 9,

    W_IDENTITY_GATE_PASS        = 1ULL << 10,
    W_IDENTITY_GATE_FAIL        = 1ULL << 11,

    W_SWEEP_APPLIED             = 1ULL << 12,

    W_HALT_REACHED              = 1ULL << 13

} HHSWitnessFlags;

// ============================================================================
// TRANSPORT VECTOR
// ============================================================================

typedef struct {

    int64_t transport_flux;

    int64_t orientation_flux;

    int64_t constraint_flux;

} HHSTransportVector;

// ============================================================================
// TENSOR STATE
// ============================================================================

typedef struct {

    int64_t xy;
    int64_t yx;

    int64_t transport;
    int64_t orientation;
    int64_t constraint;

} HHSTensorState;

// ============================================================================
// GENOMIC STATE
// ============================================================================

typedef struct {

    uint8_t genomic[4];

} HHSGenomicState;

// ============================================================================
// MANIFOLD STATE
// ============================================================================

typedef struct {

    double manifold[9][9];

} HHSManifoldState;

// ============================================================================
// RECEIPT OBJECT
// ============================================================================

typedef struct {

    HHSHash72 parent_receipt;

    HHSHash72 current_receipt;

    uint64_t step;

    uint64_t opcode;

    uint64_t witness_flags;

    int64_t entropy_delta;

    int64_t closure_delta;

} HHSReceipt;

// ============================================================================
// RUNTIME STATE
// ============================================================================

typedef struct {

    // --------------------------------------------------------
    // Runtime identity
    // --------------------------------------------------------

    uint64_t runtime_magic;

    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t abi_patch;

    // --------------------------------------------------------
    // Runtime execution
    // --------------------------------------------------------

    uint64_t step;

    uint64_t orbit_id;

    uint64_t witness_flags;

    // --------------------------------------------------------
    // Flux vectors
    // --------------------------------------------------------

    HHSTransportVector flux;

    // --------------------------------------------------------
    // Hash72 receipt chain
    // --------------------------------------------------------

    HHSHash72 prev_hash72;

    HHSHash72 state_hash72;

    HHSHash72 receipt_hash72;

    // --------------------------------------------------------
    // Closure
    // --------------------------------------------------------

    uint8_t lo_shu_slot;

    uint8_t closure_class;

    uint8_t converged;

    uint8_t halted;

    // --------------------------------------------------------
    // Tensor layer
    // --------------------------------------------------------

    HHSTensorState tensor;

    // --------------------------------------------------------
    // Genomic layer
    // --------------------------------------------------------

    HHSGenomicState genomic;

    // --------------------------------------------------------
    // Manifold layer
    // --------------------------------------------------------

    HHSManifoldState manifold;

} HHSRuntimeState;

// ============================================================================
// VECTOR CACHE RECORD
// ============================================================================

typedef struct {

    HHSHash72 hash72;

    float vector[72];

    uint64_t witness_flags;

    uint64_t replay_count;

    uint64_t prediction_hits;

} HHSVectorCacheRecord;

// ============================================================================
// GRAPH NODE ABI
// ============================================================================

typedef struct {

    uint64_t node_id;

    uint64_t parent_node_id;

    HHSHash72 hash72;

    uint64_t witness_flags;

    uint64_t timestamp;

} HHSGraphNode;

// ============================================================================
// GRAPH EDGE ABI
// ============================================================================

typedef struct {

    uint64_t source_id;

    uint64_t target_id;

    uint32_t edge_type;

    float weight;

} HHSGraphEdge;

// ============================================================================
// SANDBOX STATE
// ============================================================================

typedef struct {

    uint64_t sandbox_id;

    uint64_t active_nodes;

    uint64_t replay_depth;

    uint64_t prediction_depth;

    uint8_t isolated;

} HHSSandboxState;

// ============================================================================
// WEBSOCKET TRANSPORT PACKET
// ============================================================================

typedef struct {

    uint64_t packet_id;

    uint64_t packet_type;

    uint64_t payload_size;

    HHSHash72 runtime_hash;

} HHSRuntimePacket;

// ============================================================================
// OPCODE ABI
// ============================================================================

typedef struct {

    uint64_t opcode;

    uint64_t operand_a;
    uint64_t operand_b;
    uint64_t operand_c;

    uint64_t phase;

    uint64_t cg_id;

} HHSOpcodeEnvelope;

// ============================================================================
// ABI FUNCTION EXPORT MACRO
// ============================================================================

#if defined(_WIN32)
    #define HHS_API __declspec(dllexport)
#else
    #define HHS_API
#endif

// ============================================================================
// CORE RUNTIME FUNCTIONS
// ============================================================================

HHS_API
void hhs_runtime_init(
    HHSRuntimeState* state
);

HHS_API
void hhs_runtime_reset(
    HHSRuntimeState* state
);

HHS_API
void hhs_runtime_step(
    HHSRuntimeState* state,
    HHSTensorState* tensor
);

HHS_API
void hhs_runtime_halt(
    HHSRuntimeState* state
);

// ============================================================================
// RECEIPT FUNCTIONS
// ============================================================================

HHS_API
void hhs_receipt_commit(
    HHSRuntimeState* state,
    HHSReceipt* receipt
);

HHS_API
void hhs_receipt_reset(
    HHSReceipt* receipt
);

// ============================================================================
// HASH72 FUNCTIONS
// ============================================================================

HHS_API
void hhs_hash72_project(
    const uint8_t* cells,
    HHSHash72 out_hash
);

HHS_API
uint64_t hhs_hash72_compare(
    const HHSHash72 a,
    const HHSHash72 b
);

// ============================================================================
// TRANSPORT FUNCTIONS
// ============================================================================

HHS_API
void hhs_transport_apply(
    HHSRuntimeState* state,
    HHSTransportVector* flux
);

// ============================================================================
// TENSOR FUNCTIONS
// ============================================================================

HHS_API
void hhs_tensor_reset(
    HHSTensorState* tensor
);

HHS_API
void hhs_tensor_apply_xy(
    HHSTensorState* tensor,
    int64_t x,
    int64_t y
);

// ============================================================================
// VECTOR CACHE FUNCTIONS
// ============================================================================

HHS_API
void hhs_vectorize_hash72(
    const HHSHash72 hash72,
    float out_vector[72]
);

// ============================================================================
// GRAPH FUNCTIONS
// ============================================================================

HHS_API
uint64_t hhs_graph_node_hash(
    const HHSGraphNode* node
);

// ============================================================================
// ABI VALIDATION
// ============================================================================

HHS_API
int hhs_validate_abi(
    const HHSRuntimeState* state
);

// ============================================================================
// ABI SIZE EXPORTS
// ============================================================================

HHS_API
size_t hhs_sizeof_runtime_state(void);

HHS_API
size_t hhs_sizeof_receipt(void);

HHS_API
size_t hhs_sizeof_tensor_state(void);

HHS_API
size_t hhs_sizeof_graph_node(void);

HHS_API
size_t hhs_sizeof_graph_edge(void);

// ============================================================================
// FUTURE RESERVED ABI SPACE
// Prevents layout drift during expansion.
// ============================================================================

typedef struct {

    uint8_t reserved[512];

} HHSReservedABIBlock;

// ============================================================================
// END
// ============================================================================

#ifdef __cplusplus
}
#endif

#endif // HHS_RUNTIME_ABI_H