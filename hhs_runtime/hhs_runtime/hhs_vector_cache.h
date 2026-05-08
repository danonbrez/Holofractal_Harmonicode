// ============================================================================
// hhs_runtime/hhs_vector_cache.h
// HARMONICODE Vector Cache / Receipt Graph Layer
//
// Purpose:
//
// Persistent searchable graph-memory substrate for:
//
//   - Hash72 receipt chains
//   - deterministic replay
//   - sandbox memory layers
//   - multimodal execution embeddings
//   - adaptive prediction routing
//   - successful closure trace retention
//
// This layer NEVER mutates VM receipts.
// It stores projections of successful runtime transitions.
//
// ============================================================================

#ifndef HHS_VECTOR_CACHE_H
#define HHS_VECTOR_CACHE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// ============================================================================
// CONSTANTS
// ============================================================================

#define HHS_VECTOR_HASH_LEN        72
#define HHS_VECTOR_MAX_NEIGHBORS   32
#define HHS_VECTOR_MAX_TAGS        16
#define HHS_VECTOR_MAX_RECORDS     1048576

// ============================================================================
// CACHE FLAGS
// ============================================================================

#define HHS_CACHE_F_CONVERGED          0x00000001
#define HHS_CACHE_F_TRANSPORT          0x00000002
#define HHS_CACHE_F_ORIENTATION        0x00000004
#define HHS_CACHE_F_CONSTRAINT         0x00000008
#define HHS_CACHE_F_IDENTITY_PASS      0x00000010
#define HHS_CACHE_F_SANDBOX            0x00000020
#define HHS_CACHE_F_REPLAYABLE         0x00000040
#define HHS_CACHE_F_MULTIMODAL         0x00000080

// ============================================================================
// HASH72 VECTOR
// ============================================================================

typedef struct {

    uint8_t values[HHS_VECTOR_HASH_LEN];

} HHSHash72Vector;

// ============================================================================
// RECEIPT NODE
// ============================================================================

typedef struct {

    char state_hash72[73];
    char receipt_hash72[73];
    char parent_hash72[73];

    uint32_t witness_flags;

    uint64_t step;
    uint64_t timestamp;

    uint64_t execution_id;

    int converged;

    double identity_residual;

    HHSHash72Vector projection;

} HHSReceiptNode;

// ============================================================================
// GRAPH EDGE
// ============================================================================

typedef struct {

    uint64_t from_id;
    uint64_t to_id;

    float weight;

    uint32_t relation_flags;

} HHSReceiptEdge;

// ============================================================================
// SANDBOX LAYER
// ============================================================================

typedef struct {

    uint64_t sandbox_id;

    char root_hash72[73];

    uint64_t node_count;

    uint32_t permissions;

} HHSSandboxLayer;

// ============================================================================
// SEARCH QUERY
// ============================================================================

typedef struct {

    char target_hash72[73];

    uint32_t required_flags;
    uint32_t forbidden_flags;

    int require_convergence;

    double max_identity_residual;

    uint64_t limit;

} HHSVectorSearchQuery;

// ============================================================================
// SEARCH RESULT
// ============================================================================

typedef struct {

    uint64_t result_count;

    HHSReceiptNode *nodes;

    float *scores;

} HHSVectorSearchResult;

// ============================================================================
// CACHE DATABASE
// ============================================================================

typedef struct {

    HHSReceiptNode *nodes;
    uint64_t node_count;

    HHSReceiptEdge *edges;
    uint64_t edge_count;

    HHSSandboxLayer *sandboxes;
    uint64_t sandbox_count;

} HHSVectorCache;

// ============================================================================
// CACHE API
// ============================================================================

// Initialize cache
int hhs_vector_cache_init(

    HHSVectorCache *cache
);

// Shutdown cache
void hhs_vector_cache_shutdown(

    HHSVectorCache *cache
);

// Insert receipt node
int hhs_vector_cache_insert(

    HHSVectorCache *cache,
    HHSReceiptNode *node
);

// Link nodes
int hhs_vector_cache_link(

    HHSVectorCache *cache,
    uint64_t from_id,
    uint64_t to_id,
    float weight,
    uint32_t relation_flags
);

// Search cache
int hhs_vector_cache_search(

    HHSVectorCache *cache,
    HHSVectorSearchQuery *query,
    HHSVectorSearchResult *result
);

// ============================================================================
// SANDBOX API
// ============================================================================

// Create sandbox
int hhs_vector_cache_create_sandbox(

    HHSVectorCache *cache,
    HHSSandboxLayer *sandbox
);

// Fork sandbox
int hhs_vector_cache_fork_sandbox(

    HHSVectorCache *cache,
    uint64_t source_sandbox,
    uint64_t target_sandbox
);

// ============================================================================
// HASH72 VECTORIZATION
// ============================================================================

// Convert Hash72 string to vector
void hhs_hash72_vectorize(

    const char *hash72,
    HHSHash72Vector *out
);

// Compute vector similarity
float hhs_hash72_similarity(

    HHSHash72Vector *A,
    HHSHash72Vector *B
);

// ============================================================================
// REPLAY ROUTING
// ============================================================================

// Predict next valid receipt
int hhs_vector_cache_predict(

    HHSVectorCache *cache,
    HHSReceiptNode *current,
    HHSReceiptNode *prediction
);

// Retrieve replay chain
int hhs_vector_cache_replay_chain(

    HHSVectorCache *cache,
    const char *root_hash72,
    HHSReceiptNode **chain_out,
    uint64_t *chain_len
);

// ============================================================================
// SERIALIZATION
// ============================================================================

// Save cache
int hhs_vector_cache_save(

    HHSVectorCache *cache,
    const char *path
);

// Load cache
int hhs_vector_cache_load(

    HHSVectorCache *cache,
    const char *path
);

#ifdef __cplusplus
}
#endif

#endif

// ============================================================================
// END
// ============================================================================