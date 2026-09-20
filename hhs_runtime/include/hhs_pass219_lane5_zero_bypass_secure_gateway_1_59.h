#ifndef HHS_PASS219_LANE5_ZERO_BYPASS_SECURE_GATEWAY_1_59_H
#define HHS_PASS219_LANE5_ZERO_BYPASS_SECURE_GATEWAY_1_59_H

#include "hhs_pass219_lane5_virtual_bios_control_plane_1_58.h"
#include "hhs_pass219_vm81_environmental_recovery_1_32.h"

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_GATEWAY_VERSION UINT32_C(0x0001013B)
#define HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_FRAME_BYTES HHS_EXACT_VM81_FRAME_BYTES
#define HHS_EXACT_PASS219_LANE5_ZERO_BYPASS_FRAME_BITS HHS_EXACT_VM81_FRAME_BITS

typedef struct HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t frame_bytes;
    uint32_t frame_bits;
    uint32_t vm81_cells;
    uint32_t local_constructor_states;
    uint32_t hydration_lanes;
    uint32_t phase_modulus;

    uint8_t single_public_mutation_gateway;
    uint8_t linux_api_redirect_required;
    uint8_t raw_x86_ingress_allowed;
    uint8_t ieee754_payload_passthrough_allowed;
    uint8_t arbitrary_byte_payload_passthrough_allowed;
    uint8_t parametric_payload_identity;
    uint8_t order_preservation;
    uint8_t concatenation_preservation;
    uint8_t metadata_preservation_required;

    uint8_t cpp_rna_cell_wall_required;
    uint8_t lane5_bios_required;
    uint8_t pqc_environmental_firewall_required;
    uint8_t four_lane_hydration_required;
    uint8_t constraint_forced_execution;
    uint8_t policy_choice_authority;
    uint8_t hash216_composition_compute_fabric;
    uint8_t validated_scoped_reuse_only;
    uint8_t hash216_memory_carries_forward;

    uint8_t raw_transport_is_canonical_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t host_instruction_execution_authority;
    uint8_t hash216_cache_commit_bypass_allowed;
    uint8_t legacy_direct_runtime_bypass_allowed;
    uint8_t reserved0[3];
} HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1;

typedef struct HHSExactPass219Lane5ZeroBypassGatewayReceiptV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t input_bytes;
    uint32_t output_bytes;
    uint64_t instruction_sequence;
    uint64_t environment_witness_sequence;
    uint8_t payload_identity_verified;
    uint8_t lane5_bios_validated;
    uint8_t cpp_rna_cell_wall_routed;
    uint8_t pqc_authenticated;
    uint8_t pqc_signature_verified;
    uint8_t environmental_witness_verified;
    uint8_t parent_hash216_verified;
    uint8_t child_hash216_verified;
    uint8_t vm81_canonical_commit_observed;
    uint8_t hash216_continuation_eligible;
    uint8_t selected_lane;
    uint8_t canonical_authority_owned_by_gateway;
    uint8_t raw_transport_is_canonical_authority;
    uint8_t floating_point_canonical_authority;
    uint8_t host_instruction_execution_authority;
    uint8_t reserved0;
} HHSExactPass219Lane5ZeroBypassGatewayReceiptV1;

HHS_EXACT_API uint32_t hhs_exact_pass219_lane5_zero_bypass_gateway_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_zero_bypass_gateway_descriptor(
    HHSExactPass219Lane5ZeroBypassGatewayDescriptorV1 *out_descriptor
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_zero_bypass_gateway_validate(void);

/*
 * Parametric raw-payload identity surface.
 *
 * For every admitted byte width n, this proves the runtime instance of
 * T^{-1}(T(B)) = B without interpreting IEEE-754, integers, model weights, or
 * any other payload class as canonical arithmetic.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_payload_roundtrip_exact(
    const uint8_t *input,
    size_t length,
    uint8_t *output,
    size_t capacity,
    size_t *out_length
);

/*
 * The sole production mutation gateway introduced by 1.59.
 *
 * Raw x86_64 bytes are transported exactly into one VM5184 candidate frame,
 * then the request is forced through the Lane-5 BIOS invariant, RNA C++ cell
 * wall, PQC environmental/signature membrane, inherited VM81 admission, and
 * Hash72/Hash216 lineage verification.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass219_lane5_gateway_admit_raw5184(
    uint32_t pass_number,
    uint32_t signature_algorithm,
    const HHSExactUQCELInputV1 *input,
    const uint8_t *raw_payload,
    size_t raw_length,
    const HHSExactPass219Hash216TransitionViewV1 *parent_hash216_reference,
    int8_t lo_shu_group,
    uint16_t g243,
    uint8_t feedback_lane,
    int8_t feedback_trinary,
    uint8_t *out_committed_raw,
    size_t out_capacity,
    size_t *out_length,
    HHSExactPass219RNAAdmissionV1 *out_admission,
    HHSExactPass219VM81PQCFirewallReceiptV1 *out_firewall_receipt,
    HHSExactPass219VM81PQCSignatureReceiptV1 *out_signature_receipt,
    HHSExactPass219VM81EnvironmentReceiptV1 *out_environment_receipt,
    HHSExactPass219Lane5ZeroBypassGatewayReceiptV1 *out_gateway_receipt
);

#ifdef __cplusplus
}
#endif

#endif
