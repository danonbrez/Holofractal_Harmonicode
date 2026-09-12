#ifndef HHS_PASS219_PLUG_AND_PLAY_MATH_LOGIC_SUBSTRATE_1_27_HPP
#define HHS_PASS219_PLUG_AND_PLAY_MATH_LOGIC_SUBSTRATE_1_27_HPP

#include "hhs_runtime_exact_abi_v1_1_base.h"

#include <array>
#include <cstddef>
#include <cstdint>

namespace hhs::substrate {

static constexpr std::uint32_t HHS_PASS219_SUBSTRATE_INTERFACE_VERSION_V1 = 1U;
static constexpr std::size_t HHS_PASS219_SUBSTRATE_MAX_MODULES_V1 = 32U;
static constexpr std::size_t HHS_PASS219_SUBSTRATE_MAX_DESCRIPTOR_BYTES_V1 = 4096U;

using ModuleApplyFnV1 = HHSExactStatus (*)(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* local_witness64,
    const void* context
) noexcept;

using ModuleVerifyFnV1 = HHSExactStatus (*)(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t local_witness64,
    const void* context
) noexcept;

using ProfileValidateFnV1 = HHSExactStatus (*)(
    const HHSExactVM81Frame* candidate,
    bool* accepted,
    std::uint64_t* profile_witness64,
    const void* context
) noexcept;

using RepresentationEquivalenceFnV1 = HHSExactStatus (*)(
    const HHSExactVM81Frame* left,
    const HHSExactVM81Frame* right,
    bool* equivalent,
    const void* context
) noexcept;

struct AlgebraicModuleV1 final {
    std::uint32_t interface_version{HHS_PASS219_SUBSTRATE_INTERFACE_VERSION_V1};
    std::uint64_t module_identity64{};
    const std::uint8_t* semantic_descriptor{};
    std::size_t semantic_descriptor_length{};
    ModuleApplyFnV1 apply{};
    ModuleVerifyFnV1 verify{};
    const void* context{};

    bool exact_machine_surface{true};
    bool deterministic_contract{true};
    bool relation_preservation_declared{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

enum class CompositionDecisionV1 : std::uint8_t {
    INVALID = 0U,
    READY = 1U,
    INVALID_MODULE = 2U,
    EXECUTION_FAILED = 3U,
    NONDETERMINISTIC_MODULE = 4U,
    VERIFIER_REJECTED = 5U
};

struct CompositionResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    CompositionDecisionV1 decision{CompositionDecisionV1::INVALID};
    std::uint32_t module_count{};
    std::uint32_t verified_module_count{};
    std::uint64_t composition_signature64{};
    std::array<std::uint64_t, HHS_PASS219_SUBSTRATE_MAX_MODULES_V1> local_witness64{};
    HHSExactVM81Frame candidate{};

    bool candidate_only{true};
    bool exact_machine_surface{true};
    bool deterministic_replay_required{true};
    bool semantic_descriptor_opaque{true};
    bool fixed_subject_catalog_required{false};
    bool publication_form_required{false};
    bool local_witness_noncanonical{true};
    bool vm81_handoff_required{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

struct AdmissionProfileAdapterV1 final {
    std::uint32_t interface_version{HHS_PASS219_SUBSTRATE_INTERFACE_VERSION_V1};
    std::uint64_t profile_identity64{};
    const std::uint8_t* profile_descriptor{};
    std::size_t profile_descriptor_length{};
    ProfileValidateFnV1 validate{};
    const void* context{};

    bool exact_machine_surface{true};
    bool deterministic_contract{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

enum class ProfileDecisionV1 : std::uint8_t {
    INVALID = 0U,
    ACCEPTED = 1U,
    REJECTED = 2U,
    NONDETERMINISTIC_PROFILE = 3U,
    VALIDATOR_FAILED = 4U
};

struct ProfileValidationResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    ProfileDecisionV1 decision{ProfileDecisionV1::INVALID};
    std::uint64_t profile_witness64{};
    std::uint64_t profile_signature64{};
    bool accepted{false};
    bool validator_only{true};
    bool deterministic_replay_required{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
    bool floating_point_authority{false};
};

struct RepresentationEquivalenceResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    bool equivalent{false};
    std::uint64_t left_composition_signature64{};
    std::uint64_t right_composition_signature64{};
    bool descriptor_identity_required{false};
    bool composition_signature_identity_required{false};
    bool explicit_equivalence_relation_required{true};
    bool canonical_authority{false};
};

class PlugAndPlayMathLogicSubstrateV1 final {
public:
    static HHSExactStatus compose(
        const AlgebraicModuleV1* modules,
        std::size_t module_count,
        const HHSExactVM81Frame& seed,
        CompositionResultV1& out_result
    ) noexcept {
        out_result = CompositionResultV1{};
        out_result.candidate = seed;

        if (module_count > HHS_PASS219_SUBSTRATE_MAX_MODULES_V1 ||
            (module_count != 0U && modules == nullptr)) {
            out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return out_result.status;
        }

        out_result.module_count = static_cast<std::uint32_t>(module_count);
        std::uint64_t signature = UINT64_C(0x2190127000000001);
        for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
            signature = fold_signature(signature, seed.words[i]);

        HHSExactVM81Frame working = seed;

        for (std::size_t index = 0U; index < module_count; ++index) {
            const AlgebraicModuleV1& module = modules[index];
            if (!module_valid(module)) {
                out_result.candidate = seed;
                out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
                out_result.decision = CompositionDecisionV1::INVALID_MODULE;
                return out_result.status;
            }

            HHSExactVM81Frame first{};
            HHSExactVM81Frame replay{};
            std::uint64_t first_witness = 0U;
            std::uint64_t replay_witness = 0U;

            HHSExactStatus status = module.apply(
                &working, &first, &first_witness, module.context);
            if (status != HHS_EXACT_STATUS_OK) {
                out_result.candidate = seed;
                out_result.status = status;
                out_result.decision = CompositionDecisionV1::EXECUTION_FAILED;
                return status;
            }

            status = module.apply(
                &working, &replay, &replay_witness, module.context);
            if (status != HHS_EXACT_STATUS_OK) {
                out_result.candidate = seed;
                out_result.status = status;
                out_result.decision = CompositionDecisionV1::EXECUTION_FAILED;
                return status;
            }

            if (!frame_equal(first, replay) || first_witness != replay_witness) {
                out_result.candidate = seed;
                out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
                out_result.decision = CompositionDecisionV1::NONDETERMINISTIC_MODULE;
                return out_result.status;
            }

            status = module.verify(&working, &first, first_witness, module.context);
            if (status != HHS_EXACT_STATUS_OK) {
                out_result.candidate = seed;
                out_result.status = status;
                out_result.decision = CompositionDecisionV1::VERIFIER_REJECTED;
                return status;
            }
            status = module.verify(&working, &replay, replay_witness, module.context);
            if (status != HHS_EXACT_STATUS_OK) {
                out_result.candidate = seed;
                out_result.status = status;
                out_result.decision = CompositionDecisionV1::VERIFIER_REJECTED;
                return status;
            }

            signature = fold_signature(signature, static_cast<std::uint64_t>(index));
            signature = fold_signature(signature, module.module_identity64);
            signature = fold_descriptor(
                signature, module.semantic_descriptor, module.semantic_descriptor_length);
            signature = fold_signature(signature, first_witness);
            for (std::size_t word = 0U; word < HHS_EXACT_VM81_CELLS; ++word)
                signature = fold_signature(signature, first.words[word]);

            out_result.local_witness64[index] = first_witness;
            ++out_result.verified_module_count;
            working = first;
        }

        out_result.candidate = working;
        out_result.composition_signature64 = signature;
        out_result.status = HHS_EXACT_STATUS_OK;
        out_result.decision = CompositionDecisionV1::READY;
        return HHS_EXACT_STATUS_OK;
    }

    static HHSExactStatus validate_profile(
        const AdmissionProfileAdapterV1& profile,
        const HHSExactVM81Frame& candidate,
        ProfileValidationResultV1& out_result
    ) noexcept {
        out_result = ProfileValidationResultV1{};

        if (!profile_valid(profile)) {
            out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return out_result.status;
        }

        bool first_accepted = false;
        bool replay_accepted = false;
        std::uint64_t first_witness = 0U;
        std::uint64_t replay_witness = 0U;

        const HHSExactStatus first_status = profile.validate(
            &candidate, &first_accepted, &first_witness, profile.context);
        const HHSExactStatus replay_status = profile.validate(
            &candidate, &replay_accepted, &replay_witness, profile.context);

        if (first_status != replay_status ||
            first_accepted != replay_accepted ||
            first_witness != replay_witness) {
            out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            out_result.decision = ProfileDecisionV1::NONDETERMINISTIC_PROFILE;
            return out_result.status;
        }

        if (first_status != HHS_EXACT_STATUS_OK) {
            out_result.status = first_status;
            out_result.decision = ProfileDecisionV1::VALIDATOR_FAILED;
            return first_status;
        }

        std::uint64_t signature = UINT64_C(0x2190127000000002);
        signature = fold_signature(signature, profile.profile_identity64);
        signature = fold_descriptor(
            signature, profile.profile_descriptor, profile.profile_descriptor_length);
        signature = fold_signature(signature, first_witness);
        signature = fold_signature(signature, first_accepted ? UINT64_C(1) : UINT64_C(0));
        for (std::size_t word = 0U; word < HHS_EXACT_VM81_CELLS; ++word)
            signature = fold_signature(signature, candidate.words[word]);

        out_result.status = HHS_EXACT_STATUS_OK;
        out_result.accepted = first_accepted;
        out_result.profile_witness64 = first_witness;
        out_result.profile_signature64 = signature;
        out_result.decision = first_accepted
            ? ProfileDecisionV1::ACCEPTED
            : ProfileDecisionV1::REJECTED;
        return HHS_EXACT_STATUS_OK;
    }

    static HHSExactStatus verify_representation_equivalence(
        const AlgebraicModuleV1* left_modules,
        std::size_t left_count,
        const AlgebraicModuleV1* right_modules,
        std::size_t right_count,
        const HHSExactVM81Frame& seed,
        RepresentationEquivalenceFnV1 equivalence,
        const void* equivalence_context,
        RepresentationEquivalenceResultV1& out_result
    ) noexcept {
        out_result = RepresentationEquivalenceResultV1{};
        if (equivalence == nullptr) {
            out_result.status = HHS_EXACT_STATUS_INVALID_ARGUMENT;
            return out_result.status;
        }

        CompositionResultV1 left{};
        CompositionResultV1 right{};
        HHSExactStatus status = compose(left_modules, left_count, seed, left);
        if (status != HHS_EXACT_STATUS_OK) {
            out_result.status = status;
            return status;
        }
        status = compose(right_modules, right_count, seed, right);
        if (status != HHS_EXACT_STATUS_OK) {
            out_result.status = status;
            return status;
        }

        bool first_equivalent = false;
        bool replay_equivalent = false;
        const HHSExactStatus first_status = equivalence(
            &left.candidate, &right.candidate, &first_equivalent, equivalence_context);
        const HHSExactStatus replay_status = equivalence(
            &left.candidate, &right.candidate, &replay_equivalent, equivalence_context);

        if (first_status != replay_status || first_equivalent != replay_equivalent) {
            out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
            return out_result.status;
        }
        if (first_status != HHS_EXACT_STATUS_OK) {
            out_result.status = first_status;
            return first_status;
        }

        out_result.status = HHS_EXACT_STATUS_OK;
        out_result.equivalent = first_equivalent;
        out_result.left_composition_signature64 = left.composition_signature64;
        out_result.right_composition_signature64 = right.composition_signature64;
        return HHS_EXACT_STATUS_OK;
    }

    static HHSExactStatus strict_frame_equivalence(
        const HHSExactVM81Frame* left,
        const HHSExactVM81Frame* right,
        bool* equivalent,
        const void*
    ) noexcept {
        if (left == nullptr || right == nullptr || equivalent == nullptr)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        *equivalent = frame_equal(*left, *right);
        return HHS_EXACT_STATUS_OK;
    }

private:
    static bool module_valid(const AlgebraicModuleV1& module) noexcept {
        return module.interface_version == HHS_PASS219_SUBSTRATE_INTERFACE_VERSION_V1 &&
               module.module_identity64 != 0U &&
               module.semantic_descriptor != nullptr &&
               module.semantic_descriptor_length != 0U &&
               module.semantic_descriptor_length <= HHS_PASS219_SUBSTRATE_MAX_DESCRIPTOR_BYTES_V1 &&
               module.apply != nullptr &&
               module.verify != nullptr &&
               module.exact_machine_surface &&
               module.deterministic_contract &&
               module.relation_preservation_declared &&
               !module.canonical_mutation_authority &&
               !module.canonical_hash72_authority &&
               !module.canonical_hash216_authority &&
               !module.canonical_persistence_authority &&
               !module.floating_point_authority;
    }

    static bool profile_valid(const AdmissionProfileAdapterV1& profile) noexcept {
        return profile.interface_version == HHS_PASS219_SUBSTRATE_INTERFACE_VERSION_V1 &&
               profile.profile_identity64 != 0U &&
               profile.profile_descriptor != nullptr &&
               profile.profile_descriptor_length != 0U &&
               profile.profile_descriptor_length <= HHS_PASS219_SUBSTRATE_MAX_DESCRIPTOR_BYTES_V1 &&
               profile.validate != nullptr &&
               profile.exact_machine_surface &&
               profile.deterministic_contract &&
               !profile.canonical_mutation_authority &&
               !profile.canonical_hash72_authority &&
               !profile.canonical_hash216_authority &&
               !profile.canonical_persistence_authority &&
               !profile.floating_point_authority;
    }

    static bool frame_equal(
        const HHSExactVM81Frame& left,
        const HHSExactVM81Frame& right
    ) noexcept {
        for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
            if (left.words[i] != right.words[i])
                return false;
        }
        return true;
    }

    static std::uint64_t mix64(std::uint64_t value) noexcept {
        value ^= value >> 30U;
        value *= UINT64_C(0xbf58476d1ce4e5b9);
        value ^= value >> 27U;
        value *= UINT64_C(0x94d049bb133111eb);
        value ^= value >> 31U;
        return value;
    }

    static std::uint64_t fold_signature(
        std::uint64_t accumulator,
        std::uint64_t value
    ) noexcept {
        return mix64(accumulator ^ mix64(value + UINT64_C(0x9e3779b97f4a7c15)));
    }

    static std::uint64_t fold_descriptor(
        std::uint64_t accumulator,
        const std::uint8_t* bytes,
        std::size_t length
    ) noexcept {
        accumulator = fold_signature(accumulator, static_cast<std::uint64_t>(length));
        for (std::size_t i = 0U; i < length; ++i)
            accumulator = fold_signature(accumulator, static_cast<std::uint64_t>(bytes[i]));
        return accumulator;
    }
};

}  // namespace hhs::substrate

#endif
