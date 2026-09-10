#ifndef HHS_PASS219_CORE_HOLOGRAPHIC_FOUR_LANE_1_24_H
#define HHS_PASS219_CORE_HOLOGRAPHIC_FOUR_LANE_1_24_H

#include "hhs_pass219_core_constraint_dynamic_circuit_1_23.h"
#include "hhs_pass219_rna_transcription_1_10.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HOLO4_VERSION UINT32_C(0x00010018)
#define HHS_EXACT_PASS219_HOLO4_CELL_COUNT UINT32_C(81)
#define HHS_EXACT_PASS219_HOLO4_BANK_COUNT UINT32_C(9)
#define HHS_EXACT_PASS219_HOLO4_CELLS_PER_BANK UINT32_C(9)
#define HHS_EXACT_PASS219_HOLO4_SUDOKU_PEERS UINT32_C(20)
#define HHS_EXACT_PASS219_HOLO4_DIRECTED_GRAPH_EDGES UINT32_C(1620)
#define HHS_EXACT_PASS219_HOLO4_LANE_COUNT UINT32_C(4)
#define HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE UINT8_C(255)
#define HHS_EXACT_PASS219_HOLO4_WEIGHT_BOUND INT16_C(5184)

typedef enum HHSExactPass219Holo4LaneV1 {
    HHS_EXACT_PASS219_HOLO4_RAW5184_X86_64 = 0,
    HHS_EXACT_PASS219_HOLO4_VM81_HASH72_HASH216 = 1,
    HHS_EXACT_PASS219_HOLO4_OCTONION_DUAL_STEREO_TERNARY = 2,
    HHS_EXACT_PASS219_HOLO4_HARMONIC36_144X36 = 3
} HHSExactPass219Holo4LaneV1;

typedef struct HHSExactPass219Holo4DescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t cell_count;
    uint32_t bank_count;
    uint32_t cells_per_bank;
    uint32_t peers_per_cell;
    uint32_t directed_graph_edges;
    uint32_t lane_count;
    uint32_t phase_modulus;
    uint32_t update_quantum;
    uint8_t nested_loshu_tensor;
    uint8_t sudoku_knowledge_graph;
    uint8_t reciprocal_phase_gear;
    uint8_t local_cell_learning;
    uint8_t bank_learning;
    uint8_t hash216_driven_routing;
    uint8_t cpp_rna_cell_wall_composable;
    uint8_t vm81_abi_carrier;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0;
} HHSExactPass219Holo4DescriptorV1;

typedef struct HHSExactPass219Holo4CellV1 {
    uint8_t cell81;
    uint8_t row9;
    uint8_t column9;
    uint8_t bank9;
    uint8_t local_loshu;
    uint8_t macro_loshu;
    uint8_t phase_basis;
    uint8_t reciprocal_basis;
    uint8_t phase72;
    uint8_t reciprocal_phase72;
    int8_t trinary_activation;
    uint8_t peer_count;
    uint8_t self_popcount;
    uint8_t reserved0;
    uint16_t neighbor_popcount;
    uint16_t hash216_position[HHS_EXACT_PASS219_HOLO4_LANE_COUNT];
    uint64_t peer_mask_lo64;
    uint64_t peer_mask_hi17;
    uint64_t local_signature64;
} HHSExactPass219Holo4CellV1;

typedef struct HHSExactPass219Holo4BankV1 {
    uint8_t bank9;
    uint8_t macro_loshu;
    uint16_t cell_popcount;
    int32_t activation_sum;
    uint64_t bank_signature64;
} HHSExactPass219Holo4BankV1;

typedef struct HHSExactPass219Holo4PreparedV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t word_visits;
    uint32_t graph_edge_visits;
    HHSExactPass219CoreCircuitFeaturesV1 core_features;
    HHSExactPass219CoreCircuitDecisionV1 core_decision;
    HHSExactPass219Holo4CellV1 cells[HHS_EXACT_PASS219_HOLO4_CELL_COUNT];
    HHSExactPass219Holo4BankV1 banks[HHS_EXACT_PASS219_HOLO4_BANK_COUNT];
    char source_transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint64_t graph_signature64;
    uint64_t tensor_signature64;
    uint8_t all_cells_have_20_peers;
    uint8_t reciprocal_phase_closure;
    uint8_t nested_loshu_complete;
    uint8_t hash216_positions_complete;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
} HHSExactPass219Holo4PreparedV1;

typedef struct HHSExactPass219Holo4StateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219CoreCircuitStateV1 core;
    int16_t cell_lane_weights[HHS_EXACT_PASS219_HOLO4_LANE_COUNT][HHS_EXACT_PASS219_HOLO4_CELL_COUNT];
    int16_t bank_lane_weights[HHS_EXACT_PASS219_HOLO4_LANE_COUNT][HHS_EXACT_PASS219_HOLO4_BANK_COUNT];
    int16_t lane_bias[HHS_EXACT_PASS219_HOLO4_LANE_COUNT];
    uint16_t reserved0;
    uint32_t update_count;
    uint64_t step_count;
    uint8_t candidate_only;
    uint8_t bounded_weights;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass219Holo4StateV1;

typedef struct HHSExactPass219Holo4LaneScoreV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t lane_id;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t reserved0;
    int64_t score;
    int32_t cell_contribution[HHS_EXACT_PASS219_HOLO4_CELL_COUNT];
    int32_t bank_contribution[HHS_EXACT_PASS219_HOLO4_BANK_COUNT];
    uint64_t routing_signature64;
} HHSExactPass219Holo4LaneScoreV1;

typedef struct HHSExactPass219Holo4DecisionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT];
    uint8_t selected_lane;
    uint8_t feedback_lane;
    int8_t feedback_trinary;
    uint8_t updated;
    uint32_t update_count;
    uint64_t step_count;
    char source_transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    uint64_t decision_signature64;
    uint8_t candidate_only;
    uint8_t exact_integer_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0;
} HHSExactPass219Holo4DecisionV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_holo4_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_descriptor(
    HHSExactPass219Holo4DescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_state_init(
    HHSExactPass219Holo4StateV1 *out_state);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_validate_state(
    const HHSExactPass219Holo4StateV1 *state);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_prepare(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    const HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4PreparedV1 *out_prepared);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_score_lane(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4StateV1 *state,
    uint8_t lane_id,
    HHSExactPass219Holo4LaneScoreV1 *out_score);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_finalize(
    const HHSExactPass219Holo4PreparedV1 *prepared,
    const HHSExactPass219Holo4LaneScoreV1 lanes[HHS_EXACT_PASS219_HOLO4_LANE_COUNT],
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4DecisionV1 *out_decision);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_holo4_route(
    const HHSExactVM81Frame *frame,
    const HHSExactPass219Hash216TransitionViewV1 *transition,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    HHSExactPass219Holo4StateV1 *state,
    HHSExactPass219Holo4PreparedV1 *out_prepared,
    HHSExactPass219Holo4DecisionV1 *out_decision);

#ifdef __cplusplus
}
#endif

#endif
