#ifndef HHS_PASS205_CONTINUATION_H
#define HHS_PASS205_CONTINUATION_H

#include <stddef.h>
#include <stdint.h>
#include "../include/hhs_hash216.h"

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS_PASS205_API __declspec(dllexport)
#else
#define HHS_PASS205_API
#endif

#define HHS_PASS205_CELL_COUNT 81u
#define HHS_PASS205_BITS_PER_CELL 64u
#define HHS_PASS205_STATE_BITS 5184u
#define HHS_PASS205_CONTROL_COUNT 243u
#define HHS_PASS205_Q_COUNT 1259712u
#define HHS_PASS205_PROJECTION_CHANNELS 32u

typedef struct {
    uint64_t cells[HHS_PASS205_CELL_COUNT];
} HHSPass205State;

typedef struct {
    uint16_t count;
    uint8_t cell_index[HHS_PASS205_CELL_COUNT];
    uint8_t control_g[HHS_PASS205_CELL_COUNT];
    uint64_t xor_mask[HHS_PASS205_CELL_COUNT];
} HHSPass205Delta;

typedef struct {
    uint8_t cell[HHS_PASS205_CELL_COUNT];
} HHSPass205Frontier;

typedef struct {
    uint32_t channel[HHS_PASS205_PROJECTION_CHANNELS][HHS_PASS205_CELL_COUNT];
} HHSPass205Projection;

typedef struct {
    HHSHash216 parent_root;
    HHSHash216 content_root;
    HHSHash216 delta_root;
    HHSHash216 hydration_root;
    HHSHash216 dependency_root;
    HHSHash216 projection_root;
    HHSHash216 learning_root;
    HHSHash216 continuation_root;
    HHSHash72 parent_receipt;
    HHSHash72 receipt;
    uint64_t generation;
} HHSPass205Token;

HHS_PASS205_API uint32_t hhs_pass205_q_address(uint16_t s, uint8_t g, uint8_t* ok);
HHS_PASS205_API uint8_t hhs_pass205_q_decode(uint32_t q, uint16_t* out_s, uint8_t* out_g);
HHS_PASS205_API void hhs_pass205_state_clear(HHSPass205State* state);
HHS_PASS205_API void hhs_pass205_projection_clear(HHSPass205Projection* projection);
HHS_PASS205_API void hhs_pass205_frontier_clear(HHSPass205Frontier* frontier);
HHS_PASS205_API uint8_t hhs_pass205_validate_delta(const HHSPass205Delta* delta);
HHS_PASS205_API uint8_t hhs_pass205_apply_delta(
    const HHSPass205State* parent,
    const HHSPass205Delta* delta,
    HHSPass205State* child
);
HHS_PASS205_API uint8_t hhs_pass205_build_required_frontier(
    const HHSPass205Delta* delta,
    HHSPass205Frontier* frontier
);
HHS_PASS205_API uint8_t hhs_pass205_validate_frontier(
    const HHSPass205Delta* delta,
    const HHSPass205Frontier* frontier
);
HHS_PASS205_API void hhs_pass205_project_full(
    const HHSPass205State* state,
    HHSPass205Projection* projection
);
HHS_PASS205_API uint8_t hhs_pass205_project_sparse(
    const HHSPass205State* child,
    const HHSPass205Projection* parent_projection,
    const HHSPass205Frontier* frontier,
    HHSPass205Projection* child_projection
);
HHS_PASS205_API uint8_t hhs_pass205_projection_equal(
    const HHSPass205Projection* a,
    const HHSPass205Projection* b
);
HHS_PASS205_API void hhs_pass205_state_hash216(
    const HHSPass205State* state,
    HHSHash216* out_hash
);
HHS_PASS205_API void hhs_pass205_delta_hash216(
    const HHSPass205Delta* delta,
    HHSHash216* out_hash
);
HHS_PASS205_API void hhs_pass205_hydration_hash216(
    const HHSPass205Delta* delta,
    HHSHash216* out_hash
);
HHS_PASS205_API void hhs_pass205_frontier_hash216(
    const HHSPass205Frontier* frontier,
    HHSHash216* out_hash
);
HHS_PASS205_API void hhs_pass205_projection_hash216(
    const HHSPass205Projection* projection,
    HHSHash216* out_hash
);
HHS_PASS205_API void hhs_pass205_hash216_bytes(
    const uint8_t* data,
    size_t size,
    HHSHash216* out_hash
);
HHS_PASS205_API uint8_t hhs_pass205_build_token(
    const HHSHash216* parent_root,
    const HHSHash216* content_root,
    const HHSHash216* delta_root,
    const HHSHash216* hydration_root,
    const HHSHash216* dependency_root,
    const HHSHash216* projection_root,
    const HHSHash216* learning_root,
    const HHSHash72* parent_receipt,
    uint64_t generation,
    HHSPass205Token* out_token
);
HHS_PASS205_API size_t hhs_pass205_sizeof_state(void);
HHS_PASS205_API size_t hhs_pass205_sizeof_delta(void);
HHS_PASS205_API size_t hhs_pass205_sizeof_frontier(void);
HHS_PASS205_API size_t hhs_pass205_sizeof_projection(void);
HHS_PASS205_API size_t hhs_pass205_sizeof_token(void);

#ifdef __cplusplus
}
#endif

#endif
