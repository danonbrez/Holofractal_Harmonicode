#ifndef HHS_PASS219_HHCQ_SYMBOLIC_PHASE_GEAR_1_32_H
#define HHS_PASS219_HHCQ_SYMBOLIC_PHASE_GEAR_1_32_H

#include "hhs_pass219_hhcq_8basis_equilibrium_parity_1_31.h"

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_VERSION UINT32_C(0x00010020)
#define HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT UINT32_C(8)
#define HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_SOURCE_BYTES HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SOURCE_BYTES

typedef enum HHSExactPass219HHCQPhaseSymbolV1 {
    HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_INVALID = 0,
    HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I = 1,
    HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I2 = 2,
    HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I3 = 3,
    HHS_EXACT_PASS219_HHCQ_PHASE_SYMBOL_I4 = 4
} HHSExactPass219HHCQPhaseSymbolV1;

typedef enum HHSExactPass219HHCQSymbolicOrientationV1 {
    HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_INVALID = 0,
    HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_DIRECT = 1,
    HHS_EXACT_PASS219_HHCQ_SYMBOLIC_ORIENTATION_REVERSED = 2
} HHSExactPass219HHCQSymbolicOrientationV1;

typedef struct HHSExactPass219HHCQSymbolicPhaseDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t phase_modulus;
    uint32_t parameter_count;
    uint32_t basis_count;
    uint32_t inherited_policy_state_bytes;
    uint32_t phase11_source_bytes;
    uint8_t phase11_source_sha256[HHS_EXACT_PASS219_HHCQ_8BASIS_PARITY_SHA256_BYTES];
    uint8_t symbolic_phase_symbols;
    uint8_t global_constraint_graph_required;
    uint8_t reciprocal_opposition_relations_required;
    uint8_t ordered_noncommutative_products_required;
    uint8_t symbolic_phi8_equilibrium;
    uint8_t symbolic_x_squared_gate;
    uint8_t phase11_scalar_equilibrium_superseded;
    uint8_t phase11_scalar_parity_superseded;
    uint8_t raw_phase_residue_authority;
    uint8_t scalar_phase_sum_authority;
    uint8_t scalar_x_parity_authority;
    uint8_t phase10_projection_witness_only;
    uint8_t candidate_only;
    uint8_t exact_integer_storage_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[5];
} HHSExactPass219HHCQSymbolicPhaseDescriptorV1;

typedef struct HHSExactPass219HHCQSymbolicCarrierV1 {
    uint32_t struct_size;
    uint32_t version;
    uint8_t x_symbol;
    uint8_t y_symbol;
    uint8_t z_symbol;
    uint8_t w_symbol;
    uint8_t xy_symbol;
    uint8_t yx_symbol;
    uint8_t zw_symbol;
    uint8_t wz_symbol;
    uint8_t xy_ring_orientation;
    uint8_t zw_ring_orientation;
    uint8_t x_inverse_y;
    uint8_t y_opposes_x;
    uint8_t z_inverse_w;
    uint8_t w_opposes_z;
    uint8_t xy_is_i4;
    uint8_t yx_is_i2;
    uint8_t zw_is_i4;
    uint8_t wz_is_i2;
    uint8_t ordered_noncommutative_products;
    uint8_t global_relation_graph_exact;
    uint8_t projection_residue72[HHS_EXACT_PASS219_HHCQ_SYMBOLIC_PHASE_BASIS_COUNT];
    uint8_t projection_residue_authority;
    uint8_t candidate_only;
    uint8_t exact_integer_storage_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[3];
    uint64_t carrier_signature64;
} HHSExactPass219HHCQSymbolicCarrierV1;

typedef struct HHSExactPass219HHCQSymbolicAdmissionV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQSymbolicCarrierV1 carrier;
    uint8_t raw_projection_valid;
    uint8_t raw_projection_matches_symbolic_carrier;
    uint8_t symbolic_carrier_admitted;
    uint8_t raw_projection_authority;
    uint8_t scalar_zero_reinterpreted_as_symbolic_zero;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint64_t admission_signature64;
} HHSExactPass219HHCQSymbolicAdmissionV1;

typedef struct HHSExactPass219HHCQSymbolicEquilibriumV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQSymbolicCarrierV1 carrier;
    uint16_t prime_p;
    uint16_t prime_q;
    uint8_t phi8_symbolic;
    uint8_t macro_p_symbolic;
    uint8_t equilibrium_relation_present;
    uint8_t equilibrium_relation_well_typed;
    uint8_t scalar_phase_sum_evaluated;
    uint8_t scalar_macro_p_constructed;
    uint8_t prime_seed_pair_valid;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[6];
    uint64_t equilibrium_signature64;
} HHSExactPass219HHCQSymbolicEquilibriumV1;

typedef struct HHSExactPass219HHCQSymbolicGateV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQSymbolicCarrierV1 carrier;
    HHSExactPass219HHCQPrimeRationalExpansionV1 phase10_projection;
    uint8_t x_squared_symbol;
    uint8_t negative_xy_symbol;
    uint8_t carrier_orientation;
    uint8_t symbolic_exponent_retained;
    uint8_t symbolic_square_relation_exact;
    uint8_t typed_gate_well_formed;
    uint8_t scalar_x_parity_evaluated;
    uint8_t ordinary_power_evaluated;
    uint8_t phase10_projection_executed;
    uint8_t phase10_projection_authority;
    uint8_t resolution_noncoarsening;
    uint8_t candidate_only;
    uint8_t canonical_authority_changed;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    uint64_t gate_signature64;
} HHSExactPass219HHCQSymbolicGateV1;

typedef struct HHSExactPass219HHCQSymbolicManifoldV1 {
    uint32_t struct_size;
    uint32_t version;
    HHSExactPass219HHCQSymbolicAdmissionV1 admission;
    HHSExactPass219HHCQSymbolicEquilibriumV1 equilibrium;
    HHSExactPass219HHCQSymbolicGateV1 gate;
    uint8_t symbolic_carrier_admitted;
    uint8_t global_relation_graph_exact;
    uint8_t symbolic_equilibrium_exact;
    uint8_t symbolic_square_gate_exact;
    uint8_t ordered_products_exact;
    uint8_t constraint_intersection_satisfied;
    uint8_t raw_projection_authority;
    uint8_t scalar_integer_semantic_authority;
    uint8_t candidate_only;
    uint8_t canonical_mutation_authority;
    uint8_t canonical_hash72_authority;
    uint8_t canonical_hash216_authority;
    uint8_t canonical_persistence_authority;
    uint8_t floating_point_authority;
    uint8_t reserved0[2];
    uint64_t manifold_signature64;
} HHSExactPass219HHCQSymbolicManifoldV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_hhcq_symbolic_phase_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_phase_descriptor(
    HHSExactPass219HHCQSymbolicPhaseDescriptorV1 *out_descriptor);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_construct(
    uint8_t xy_ring_orientation,
    uint8_t zw_ring_orientation,
    HHSExactPass219HHCQSymbolicCarrierV1 *out_carrier);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_carrier_validate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_admit_projection(
    const HHSExactPass219OctonionStateV1 *raw_projection,
    HHSExactPass219HHCQSymbolicAdmissionV1 *out_admission);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_equilibrium(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    HHSExactPass219HHCQSymbolicEquilibriumV1 *out_equilibrium);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_gate(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicGateV1 *out_gate);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_carrier(
    const HHSExactPass219HHCQSymbolicCarrierV1 *carrier,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_projection(
    const HHSExactPass219OctonionStateV1 *raw_projection,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_hhcq_symbolic_manifold_from_vm81(
    const HHSExactVM81Frame *frame,
    uint8_t x_cell,
    uint8_t y_cell,
    uint8_t z_cell,
    uint8_t w_cell,
    uint16_t prime_p,
    uint16_t prime_q,
    uint8_t base_resolution_index,
    HHSExactPass219HHCQSymbolicManifoldV1 *out_manifold);

#ifdef __cplusplus
}
#endif

#endif
