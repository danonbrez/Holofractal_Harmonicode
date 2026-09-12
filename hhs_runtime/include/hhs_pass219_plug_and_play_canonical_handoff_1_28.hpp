#ifndef HHS_PASS219_PLUG_AND_PLAY_CANONICAL_HANDOFF_1_28_HPP
#define HHS_PASS219_PLUG_AND_PLAY_CANONICAL_HANDOFF_1_28_HPP

#include "hhs_pass219_plug_and_play_math_logic_substrate_1_27.hpp"
#include "hhs_pass192_fibonacci_compression_1_9.h"

#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::substrate {

enum class CanonicalHandoffDecisionV1 : std::uint8_t {
    INVALID = 0U,
    PROFILE_NOT_ACCEPTED = 1U,
    DELEGATED_REJECTED = 2U,
    COMMITTED = 3U,
    AUTHORITY_INVARIANT_FAILURE = 4U
};

struct CanonicalHandoffResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    CanonicalHandoffDecisionV1 decision{CanonicalHandoffDecisionV1::INVALID};
    HHSExactVM81Frame committed_frame{};
    HHSExactPass219ComposedAdmissionV1 admission{};

    bool adapter_is_canonical_authority{false};
    bool profile_precheck_is_commit_authority{false};
    bool delegated_to_inherited_c_authority{false};
    bool inherited_authority_revalidated{false};
    bool canonical_receipt_owned_by_inherited_authority{true};
};

/*
 * This is one profile-specific handoff adapter for the already-canonical
 * Pass 219 UQCEL + Fibonacci admission family. It does not redefine the
 * generic substrate and does not grant a plug-in callback commit authority.
 *
 * A generic CompositionResultV1 and ProfileValidationResultV1 can reach
 * canonical state only by being revalidated by hhs_exact_pass219_admit_composed.
 * A permissive or incorrect generic profile therefore cannot bypass the
 * inherited C authority.
 */
class Pass219UQCELCanonicalHandoffV1 final {
public:
    static HHSExactStatus commit(
        const CompositionResultV1& composition,
        const ProfileValidationResultV1& profile,
        const HHSExactUQCELInputV1& uqcel_input,
        CanonicalHandoffResultV1& out_result
    ) noexcept {
        out_result = CanonicalHandoffResultV1{};

        if (!composition_ready(composition)) {
            out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            out_result.decision = CanonicalHandoffDecisionV1::INVALID;
            return out_result.status;
        }

        if (!profile_accepted(profile)) {
            out_result.status = HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            out_result.decision = CanonicalHandoffDecisionV1::PROFILE_NOT_ACCEPTED;
            return out_result.status;
        }

        out_result.delegated_to_inherited_c_authority = true;

        HHSExactVM81Frame staged_committed{};
        HHSExactPass219ComposedAdmissionV1 staged_admission{};
        const HHSExactStatus status = hhs_exact_pass219_admit_composed(
            &uqcel_input,
            &composition.candidate,
            &staged_committed,
            &staged_admission);

        out_result.status = status;
        out_result.inherited_authority_revalidated = true;
        out_result.admission = staged_admission;

        if (status != HHS_EXACT_STATUS_OK) {
            if (!frame_is_zero(staged_committed)) {
                out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
                out_result.decision = CanonicalHandoffDecisionV1::AUTHORITY_INVARIANT_FAILURE;
                return out_result.status;
            }
            out_result.decision = CanonicalHandoffDecisionV1::DELEGATED_REJECTED;
            return status;
        }

        if (staged_admission.uqcel.decision != HHS_EXACT_UQCEL_DECISION_ADMIT ||
            staged_admission.uqcel.frame_committed != 1U ||
            !frame_equal(staged_committed, composition.candidate) ||
            !receipt_shape_valid(staged_admission)) {
            out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out_result.decision = CanonicalHandoffDecisionV1::AUTHORITY_INVARIANT_FAILURE;
            return out_result.status;
        }

        out_result.committed_frame = staged_committed;
        out_result.status = HHS_EXACT_STATUS_OK;
        out_result.decision = CanonicalHandoffDecisionV1::COMMITTED;
        return HHS_EXACT_STATUS_OK;
    }

private:
    static bool composition_ready(const CompositionResultV1& value) noexcept {
        return value.status == HHS_EXACT_STATUS_OK &&
               value.decision == CompositionDecisionV1::READY &&
               value.verified_module_count == value.module_count &&
               value.candidate_only &&
               value.exact_machine_surface &&
               value.deterministic_replay_required &&
               value.vm81_handoff_required &&
               !value.canonical_mutation_authority &&
               !value.canonical_hash72_authority &&
               !value.canonical_hash216_authority &&
               !value.canonical_persistence_authority &&
               !value.floating_point_authority;
    }

    static bool profile_accepted(const ProfileValidationResultV1& value) noexcept {
        return value.status == HHS_EXACT_STATUS_OK &&
               value.decision == ProfileDecisionV1::ACCEPTED &&
               value.accepted &&
               value.validator_only &&
               value.deterministic_replay_required &&
               !value.canonical_mutation_authority &&
               !value.canonical_hash72_authority &&
               !value.canonical_hash216_authority &&
               !value.canonical_persistence_authority &&
               !value.floating_point_authority;
    }

    static bool frame_equal(
        const HHSExactVM81Frame& left,
        const HHSExactVM81Frame& right
    ) noexcept {
        return std::memcmp(&left, &right, sizeof(left)) == 0;
    }

    static bool frame_is_zero(const HHSExactVM81Frame& value) noexcept {
        HHSExactVM81Frame zero{};
        return frame_equal(value, zero);
    }

    static bool receipt_shape_valid(
        const HHSExactPass219ComposedAdmissionV1& value
    ) noexcept {
        return value.final_receipt_hash72[0] != '\0' &&
               value.final_receipt_hash72[HHS_EXACT_HASH72_LEN] == '\0' &&
               value.final_hash216_triplet[0] != '\0' &&
               value.final_hash216_triplet[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] == '\0' &&
               value.final_hash216_identity[0] != '\0' &&
               value.final_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] == '\0';
    }
};

}  // namespace hhs::substrate

#endif
