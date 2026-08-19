#ifndef HHS_PASS219B_PHASE_QUANTIZED_HYDRATION_1_0_H
#define HHS_PASS219B_PHASE_QUANTIZED_HYDRATION_1_0_H

#include "hhs_pass219_rna_transcription_1_10.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219B_PHASE_VERSION_MAJOR 1U
#define HHS_EXACT_PASS219B_PHASE_VERSION_MINOR 0U
#define HHS_EXACT_PASS219B_PHASE_VERSION_PATCH 0U

#define HHS_EXACT_PASS219B_PHASE_ORIGIN_COUNT 81U
#define HHS_EXACT_PASS219B_OUTER_CELL_COUNT 8U
#define HHS_EXACT_PASS219B_RING_COUNT 2U
#define HHS_EXACT_PASS219B_PARENT_SLOT_COUNT 5184U
#define HHS_EXACT_PASS219B_PHASE_CELLS_PER_5184 419904ULL
#define HHS_EXACT_PASS219B_INHERITED_MANIFOLD_STATES 51648192ULL
#define HHS_EXACT_PASS219B_FULL_PHASE_PROJECTION_CELLS 4183503552ULL

#define HHS_EXACT_PASS219B_TENSOR_SOURCE \
    "List(List(x=1/y,w=-z,(y*x=-xy)),List((w*z=-zw),x+y+z+w=0,(z*w)),List((x*y),z=1/w,y=-x))"

typedef enum HHSExactPass219BRing {
    HHS_EXACT_PASS219B_RING_XY = 0,
    HHS_EXACT_PASS219B_RING_ZW = 1
} HHSExactPass219BRing;

typedef enum HHSExactPass219BRotationFamily {
    HHS_EXACT_PASS219B_ROTATION_I = 1,
    HHS_EXACT_PASS219B_ROTATION_I2 = 2
} HHSExactPass219BRotationFamily;

typedef enum HHSExactPass219BRelationRole {
    HHS_EXACT_PASS219B_REL_X_RECIPROCAL = 0,
    HHS_EXACT_PASS219B_REL_W_OPPOSITION = 1,
    HHS_EXACT_PASS219B_REL_YX_ANTIORIENTED = 2,
    HHS_EXACT_PASS219B_REL_ZW_PRODUCT = 3,
    HHS_EXACT_PASS219B_REL_Y_OPPOSITION = 4,
    HHS_EXACT_PASS219B_REL_Z_RECIPROCAL = 5,
    HHS_EXACT_PASS219B_REL_XY_PRODUCT = 6,
    HHS_EXACT_PASS219B_REL_WZ_ANTIORIENTED = 7
} HHSExactPass219BRelationRole;

typedef struct HHSExactPass219BOuterPhaseCellV1 {
    uint8_t perimeter_index;
    uint8_t ring;
    uint8_t ring_step;
    uint8_t phase_basis;
    uint8_t rotation_family;
    int8_t direction;
    uint8_t phase_position81;
    uint8_t relation_role;
} HHSExactPass219BOuterPhaseCellV1;

typedef struct HHSExactPass219BPhaseCellV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HydrationCoordinateV1 parent;
    uint64_t projection_index;
    uint8_t phase_origin81;
    uint8_t outer_count;
    uint8_t center_closure_preserved;
    uint8_t tensor_source_preserved;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_persistence_authority;
    uint8_t canonical_hash72_authority;
    uint8_t reserved0;
    HHSExactPass219BOuterPhaseCellV1 outer[HHS_EXACT_PASS219B_OUTER_CELL_COUNT];
} HHSExactPass219BPhaseCellV1;

typedef struct HHSExactPass219BExpansionPlanV1 {
    uint32_t struct_size;
    uint32_t version;
    uint64_t parent_count;
    uint32_t origin_count;
    uint32_t reserved0;
    uint64_t required_phase_cells;
    uint64_t phase_cells_per_5184;
    uint64_t inherited_manifold_states;
    uint64_t full_phase_projection_cells;
    uint8_t full_materialization_required;
    uint8_t reserved1[7];
} HHSExactPass219BExpansionPlanV1;

HHS_EXACT_API uint32_t hhs_exact_pass219b_phase_version(void);

HHS_EXACT_API const char *hhs_exact_pass219b_tensor_source(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_projection_index(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    uint64_t *out_projection_index
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_phase_cell(
    const HHSExactPass219HydrationCoordinateV1 *parent,
    uint8_t phase_origin81,
    HHSExactPass219BPhaseCellV1 *out_cell
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_expansion_plan(
    uint64_t parent_count,
    uint32_t origin_count,
    HHSExactPass219BExpansionPlanV1 *out_plan
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219b_expand_selected(
    const HHSExactPass219HydrationCoordinateV1 *parents,
    size_t parent_count,
    uint8_t first_origin81,
    uint8_t origin_count,
    HHSExactPass219BPhaseCellV1 *out_cells,
    size_t capacity,
    size_t *out_count
);

#ifdef __cplusplus
}
#endif

#endif
