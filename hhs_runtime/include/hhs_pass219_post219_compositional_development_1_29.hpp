#ifndef HHS_PASS219_POST219_COMPOSITIONAL_DEVELOPMENT_1_29_HPP
#define HHS_PASS219_POST219_COMPOSITIONAL_DEVELOPMENT_1_29_HPP

#include "hhs_pass219_plug_and_play_canonical_handoff_1_28.hpp"
#include "hhs_pass219_rna_transcription_1_10.hpp"
#include "hhs_pass219_vm81_pqc_signature_1_31.h"

#include <cstddef>
#include <cstdint>

namespace hhs::pass219 {

static constexpr std::uint32_t HHS_PASS219_POST219_MIN_PASS_V1 = 220U;
static constexpr std::uint32_t HHS_PASS219_POST219_INTERFACE_VERSION_V1 = 1U;

enum class Post219DevelopmentDecisionV1 : std::uint8_t {
    INVALID = 0U,
    PASS_NUMBER_REJECTED = 1U,
    COMPOSITION_REJECTED = 2U,
    READY = 3U
};

struct Post219DevelopmentResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    Post219DevelopmentDecisionV1 decision{Post219DevelopmentDecisionV1::INVALID};
    std::uint32_t interface_version{HHS_PASS219_POST219_INTERFACE_VERSION_V1};
    std::uint32_t pass_number{};
    hhs::substrate::CompositionResultV1 composition{};

    bool development_surface{true};
    bool candidate_only{true};
    bool pass219_substrate_required{true};
    bool pass219_rna_lowering_available{true};
    bool canonical_handoff_required{true};
    bool pqc_firewall_required{true};
    bool asymmetric_pqc_signature_required{true};
    bool unsigned_canonical_submit_disabled{true};
    bool legacy_direct_canonical_submit_disabled{true};
    bool external_invocation_is_authority{false};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

class Post219CompositionalDevelopmentABIV1 final {
public:
    static HHSExactStatus compose(
        std::uint32_t pass_number,
        const hhs::substrate::AlgebraicModuleV1* modules,
        std::size_t module_count,
        const HHSExactVM81Frame& seed,
        Post219DevelopmentResultV1& out_result
    ) noexcept {
        out_result = Post219DevelopmentResultV1{};
        out_result.pass_number = pass_number;
        out_result.composition.candidate = seed;

        if (!pass_number_valid(pass_number)) {
            out_result.status = HHS_EXACT_STATUS_RANGE_ERROR;
            out_result.decision = Post219DevelopmentDecisionV1::PASS_NUMBER_REJECTED;
            return out_result.status;
        }

        const HHSExactStatus status =
            hhs::substrate::PlugAndPlayMathLogicSubstrateV1::compose(
                modules,
                module_count,
                seed,
                out_result.composition);

        out_result.status = status;
        if (status != HHS_EXACT_STATUS_OK) {
            out_result.decision = Post219DevelopmentDecisionV1::COMPOSITION_REJECTED;
            return status;
        }

        if (!composition_is_candidate_only(out_result.composition)) {
            out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out_result.decision = Post219DevelopmentDecisionV1::COMPOSITION_REJECTED;
            out_result.composition.candidate = seed;
            return out_result.status;
        }

        out_result.decision = Post219DevelopmentDecisionV1::READY;
        return HHS_EXACT_STATUS_OK;
    }

    static HHSExactStatus validate_profile(
        const Post219DevelopmentResultV1& development,
        const hhs::substrate::AdmissionProfileAdapterV1& profile,
        hhs::substrate::ProfileValidationResultV1& out_profile
    ) noexcept {
        out_profile = hhs::substrate::ProfileValidationResultV1{};
        if (!development_ready(development))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;

        return hhs::substrate::PlugAndPlayMathLogicSubstrateV1::validate_profile(
            profile,
            development.composition.candidate,
            out_profile);
    }

    static HHSExactStatus lower_native_phase(
        std::uint32_t pass_number,
        std::uint8_t left_basis,
        std::uint8_t right_basis,
        HHSExactPass219NativePhaseWitnessV1& out_witness
    ) noexcept {
        out_witness = HHSExactPass219NativePhaseWitnessV1{};
        if (!pass_number_valid(pass_number))
            return HHS_EXACT_STATUS_RANGE_ERROR;
        return hhs_exact_pass219_native_phase_witness(
            left_basis,
            right_basis,
            &out_witness);
    }

    static HHSExactStatus lower_hydration_coordinate(
        std::uint32_t pass_number,
        std::uint8_t cell81,
        std::int8_t lo_shu_group,
        std::uint8_t operation64,
        std::uint16_t g243,
        HHSExactPass219HydrationCoordinateV1& out_coordinate
    ) noexcept {
        out_coordinate = HHSExactPass219HydrationCoordinateV1{};
        if (!pass_number_valid(pass_number))
            return HHS_EXACT_STATUS_RANGE_ERROR;
        return hhs_exact_pass219_coordinate_from_pass189(
            cell81,
            lo_shu_group,
            operation64,
            g243,
            &out_coordinate);
    }

    /*
     * Historical direct handoff is intentionally retained as a compile-time
     * fail-closed compatibility surface. It can never request mutation.
     */
    static HHSExactStatus submit_uqcel_canonical_request(
        const Post219DevelopmentResultV1&,
        const hhs::substrate::ProfileValidationResultV1&,
        const HHSExactUQCELInputV1&,
        hhs::substrate::CanonicalHandoffResultV1& out_result
    ) noexcept {
        out_result = hhs::substrate::CanonicalHandoffResultV1{};
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    /*
     * Sole Pass 220+ production canonical-request path.  The caller may select
     * one of the fixed PQ signature profiles, but supplies no key, resolver,
     * verifier, or signature.  Candidate construction remains owned by this
     * facade; actual mutation remains owned by the signed Pass 219 firewall.
     */
    static HHSExactStatus submit_pqc_canonical_request_signed(
        const Post219DevelopmentResultV1& development,
        const hhs::substrate::ProfileValidationResultV1& profile,
        std::uint32_t signature_algorithm,
        const HHSExactUQCELInputV1& uqcel_input,
        const HHSExactPass219Hash216TransitionViewV1& parent_hash216_reference,
        std::int8_t lo_shu_group,
        std::uint16_t g243,
        std::uint8_t feedback_lane,
        std::int8_t feedback_trinary,
        HHSExactVM81Frame& out_committed_frame,
        HHSExactPass219RNAAdmissionV1& out_admission,
        HHSExactPass219VM81PQCFirewallReceiptV1& out_firewall_receipt,
        HHSExactPass219VM81PQCSignatureReceiptV1& out_signature_receipt
    ) noexcept {
        out_committed_frame = HHSExactVM81Frame{};
        out_admission = HHSExactPass219RNAAdmissionV1{};
        out_firewall_receipt = HHSExactPass219VM81PQCFirewallReceiptV1{};
        out_signature_receipt = HHSExactPass219VM81PQCSignatureReceiptV1{};
        if (!development_ready(development) || !profile_ready(profile))
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;

        return hhs_exact_pass219_vm81_pqc_admit_signed(
            development.pass_number,
            signature_algorithm,
            &uqcel_input,
            &development.composition.candidate,
            &parent_hash216_reference,
            lo_shu_group,
            g243,
            feedback_lane,
            feedback_trinary,
            &out_committed_frame,
            &out_admission,
            &out_firewall_receipt,
            &out_signature_receipt);
    }

    static constexpr bool pass_number_valid(std::uint32_t pass_number) noexcept {
        return pass_number >= HHS_PASS219_POST219_MIN_PASS_V1;
    }

private:
    static bool composition_is_candidate_only(
        const hhs::substrate::CompositionResultV1& composition
    ) noexcept {
        return composition.status == HHS_EXACT_STATUS_OK &&
               composition.decision == hhs::substrate::CompositionDecisionV1::READY &&
               composition.verified_module_count == composition.module_count &&
               composition.candidate_only &&
               composition.exact_machine_surface &&
               composition.deterministic_replay_required &&
               composition.semantic_descriptor_opaque &&
               !composition.fixed_subject_catalog_required &&
               !composition.publication_form_required &&
               composition.local_witness_noncanonical &&
               composition.vm81_handoff_required &&
               !composition.canonical_mutation_authority &&
               !composition.canonical_hash72_authority &&
               !composition.canonical_hash216_authority &&
               !composition.canonical_persistence_authority &&
               !composition.floating_point_authority;
    }

    static bool profile_ready(
        const hhs::substrate::ProfileValidationResultV1& profile
    ) noexcept {
        return profile.status == HHS_EXACT_STATUS_OK &&
               profile.accepted &&
               profile.validator_only &&
               !profile.canonical_mutation_authority &&
               !profile.canonical_hash72_authority &&
               !profile.canonical_hash216_authority &&
               !profile.canonical_persistence_authority &&
               !profile.floating_point_authority;
    }

    static bool development_ready(
        const Post219DevelopmentResultV1& development
    ) noexcept {
        return development.interface_version == HHS_PASS219_POST219_INTERFACE_VERSION_V1 &&
               pass_number_valid(development.pass_number) &&
               development.status == HHS_EXACT_STATUS_OK &&
               development.decision == Post219DevelopmentDecisionV1::READY &&
               development.development_surface &&
               development.candidate_only &&
               development.pass219_substrate_required &&
               development.pass219_rna_lowering_available &&
               development.canonical_handoff_required &&
               development.pqc_firewall_required &&
               development.asymmetric_pqc_signature_required &&
               development.unsigned_canonical_submit_disabled &&
               development.legacy_direct_canonical_submit_disabled &&
               !development.external_invocation_is_authority &&
               !development.canonical_mutation_authority &&
               !development.canonical_hash72_authority &&
               !development.canonical_hash216_authority &&
               !development.canonical_persistence_authority &&
               !development.floating_point_authority &&
               composition_is_candidate_only(development.composition);
    }
};

}  // namespace hhs::pass219

#endif