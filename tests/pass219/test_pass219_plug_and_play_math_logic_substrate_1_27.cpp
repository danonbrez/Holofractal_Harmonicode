#include "hhs_pass219_plug_and_play_math_logic_substrate_1_27.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>

using hhs::substrate::AdmissionProfileAdapterV1;
using hhs::substrate::AlgebraicModuleV1;
using hhs::substrate::CompositionDecisionV1;
using hhs::substrate::CompositionResultV1;
using hhs::substrate::PlugAndPlayMathLogicSubstrateV1;
using hhs::substrate::ProfileDecisionV1;
using hhs::substrate::ProfileValidationResultV1;
using hhs::substrate::RepresentationEquivalenceResultV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

struct UnaryWordContext final {
    std::size_t word{};
    std::uint64_t parameter{};
};

struct NondeterministicContext final {
    mutable std::uint64_t counter{};
};

struct ProfileContext final {
    std::size_t word{};
    std::uint64_t modulus{1U};
    std::uint64_t residue{};
};

static bool frames_equal(
    const HHSExactVM81Frame& left,
    const HHSExactVM81Frame& right
) noexcept {
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i) {
        if (left.words[i] != right.words[i])
            return false;
    }
    return true;
}

static std::uint64_t add_witness(
    const HHSExactVM81Frame& output,
    const UnaryWordContext& context
) noexcept {
    return output.words[context.word] ^
           context.parameter ^
           (UINT64_C(0xA11D) << (context.word % 17U));
}

static std::uint64_t multiply_witness(
    const HHSExactVM81Frame& output,
    const UnaryWordContext& context
) noexcept {
    return output.words[context.word] ^
           (context.parameter * UINT64_C(0x9e3779b97f4a7c15)) ^
           static_cast<std::uint64_t>(context.word);
}

static HHSExactStatus add_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const UnaryWordContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *output = *input;
    output->words[context.word] += context.parameter;
    *witness = add_witness(*output, context);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus add_verify(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const UnaryWordContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    HHSExactVM81Frame expected = *input;
    expected.words[context.word] += context.parameter;
    if (!frames_equal(expected, *output) || witness != add_witness(*output, context))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus multiply_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const UnaryWordContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *output = *input;
    output->words[context.word] *= context.parameter;
    *witness = multiply_witness(*output, context);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus multiply_verify(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const UnaryWordContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    HHSExactVM81Frame expected = *input;
    expected.words[context.word] *= context.parameter;
    if (!frames_equal(expected, *output) ||
        witness != multiply_witness(*output, context))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus rejecting_verify(
    const HHSExactVM81Frame*,
    const HHSExactVM81Frame*,
    std::uint64_t,
    const void*
) noexcept {
    return HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus nondeterministic_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const NondeterministicContext*>(raw_context);
    *output = *input;
    ++context.counter;
    output->words[0] += context.counter;
    *witness = context.counter;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus nondeterministic_verify(
    const HHSExactVM81Frame*,
    const HHSExactVM81Frame*,
    std::uint64_t,
    const void*
) noexcept {
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus modular_profile_validate(
    const HHSExactVM81Frame* candidate,
    bool* accepted,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (candidate == nullptr || accepted == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const ProfileContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS || context.modulus == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    const std::uint64_t observed = candidate->words[context.word] % context.modulus;
    *accepted = observed == context.residue;
    *witness = observed ^ (context.modulus << 32U) ^ context.residue;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactVM81Frame build_seed() noexcept {
    HHSExactVM81Frame seed{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        seed.words[i] = static_cast<std::uint64_t>(i + 1U) * UINT64_C(17);
    return seed;
}

static AlgebraicModuleV1 build_module(
    std::uint64_t identity,
    const char* descriptor,
    std::size_t descriptor_length,
    hhs::substrate::ModuleApplyFnV1 apply,
    hhs::substrate::ModuleVerifyFnV1 verify,
    const void* context
) noexcept {
    AlgebraicModuleV1 module{};
    module.module_identity64 = identity;
    module.semantic_descriptor = reinterpret_cast<const std::uint8_t*>(descriptor);
    module.semantic_descriptor_length = descriptor_length;
    module.apply = apply;
    module.verify = verify;
    module.context = context;
    return module;
}

int main() {
    static constexpr char DESC_ADD_A[] =
        "structure=ring-mod-2^64;relation=word0-plus-3;presentation=A";
    static constexpr char DESC_ADD_B[] =
        "presentation=B;carrier=uint64-ring;law=successor-by-three";
    static constexpr char DESC_MULTIPLY[] =
        "structure=ring-mod-2^64;relation=word0-times-5";
    static constexpr char DESC_NONDET[] =
        "invalid-test=nondeterministic-counter";
    static constexpr char PROFILE_EVEN[] =
        "profile=word0-even";
    static constexpr char PROFILE_MOD5[] =
        "profile=word0-mod5-equals-zero";

    UnaryWordContext add_three{0U, UINT64_C(3)};
    UnaryWordContext multiply_five{0U, UINT64_C(5)};
    const HHSExactVM81Frame seed = build_seed();

    AlgebraicModuleV1 add_a = build_module(
        UINT64_C(0xA300000000000001),
        DESC_ADD_A,
        sizeof(DESC_ADD_A) - 1U,
        add_apply,
        add_verify,
        &add_three);
    AlgebraicModuleV1 add_b = build_module(
        UINT64_C(0xA300000000000002),
        DESC_ADD_B,
        sizeof(DESC_ADD_B) - 1U,
        add_apply,
        add_verify,
        &add_three);
    AlgebraicModuleV1 multiply = build_module(
        UINT64_C(0xB500000000000001),
        DESC_MULTIPLY,
        sizeof(DESC_MULTIPLY) - 1U,
        multiply_apply,
        multiply_verify,
        &multiply_five);

    /* Subject-blind ordered composition: add then multiply. */
    std::array<AlgebraicModuleV1, 2> add_then_multiply{add_a, multiply};
    CompositionResultV1 forward{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              add_then_multiply.data(), add_then_multiply.size(), seed, forward) ==
          HHS_EXACT_STATUS_OK);
    CHECK(forward.decision == CompositionDecisionV1::READY);
    CHECK(forward.module_count == 2U);
    CHECK(forward.verified_module_count == 2U);
    CHECK(forward.candidate.words[0] == (seed.words[0] + UINT64_C(3)) * UINT64_C(5));
    CHECK(forward.composition_signature64 != 0U);
    CHECK(forward.candidate_only);
    CHECK(forward.exact_machine_surface);
    CHECK(forward.deterministic_replay_required);
    CHECK(forward.semantic_descriptor_opaque);
    CHECK(!forward.fixed_subject_catalog_required);
    CHECK(!forward.publication_form_required);
    CHECK(forward.local_witness_noncanonical);
    CHECK(forward.vm81_handoff_required);
    CHECK(!forward.canonical_mutation_authority);
    CHECK(!forward.canonical_hash72_authority);
    CHECK(!forward.canonical_hash216_authority);
    CHECK(!forward.canonical_persistence_authority);
    CHECK(!forward.floating_point_authority);

    /* Order is semantic data: multiply then add is observably different. */
    std::array<AlgebraicModuleV1, 2> multiply_then_add{multiply, add_a};
    CompositionResultV1 reverse{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              multiply_then_add.data(), multiply_then_add.size(), seed, reverse) ==
          HHS_EXACT_STATUS_OK);
    CHECK(reverse.candidate.words[0] == seed.words[0] * UINT64_C(5) + UINT64_C(3));
    CHECK(reverse.candidate.words[0] != forward.candidate.words[0]);
    CHECK(reverse.composition_signature64 != forward.composition_signature64);

    /* Distinct presentations can prove equivalent without descriptor/signature identity. */
    RepresentationEquivalenceResultV1 equivalence{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::verify_representation_equivalence(
              &add_a,
              1U,
              &add_b,
              1U,
              seed,
              PlugAndPlayMathLogicSubstrateV1::strict_frame_equivalence,
              nullptr,
              equivalence) == HHS_EXACT_STATUS_OK);
    CHECK(equivalence.equivalent);
    CHECK(equivalence.left_composition_signature64 !=
          equivalence.right_composition_signature64);
    CHECK(!equivalence.descriptor_identity_required);
    CHECK(!equivalence.composition_signature_identity_required);
    CHECK(equivalence.explicit_equivalence_relation_required);
    CHECK(!equivalence.canonical_authority);

    /* A failing module verifier fails closed and restores the original seed. */
    AlgebraicModuleV1 verifier_reject = add_a;
    verifier_reject.module_identity64 = UINT64_C(0xBAD0000000000001);
    verifier_reject.verify = rejecting_verify;
    CompositionResultV1 rejected{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              &verifier_reject, 1U, seed, rejected) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(rejected.decision == CompositionDecisionV1::VERIFIER_REJECTED);
    CHECK(frames_equal(rejected.candidate, seed));

    /* Nondeterminism is detected by mandatory immediate replay. */
    NondeterministicContext nondeterministic_context{};
    AlgebraicModuleV1 nondeterministic = build_module(
        UINT64_C(0xBAD0000000000002),
        DESC_NONDET,
        sizeof(DESC_NONDET) - 1U,
        nondeterministic_apply,
        nondeterministic_verify,
        &nondeterministic_context);
    CompositionResultV1 nondeterministic_result{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              &nondeterministic, 1U, seed, nondeterministic_result) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(nondeterministic_result.decision ==
          CompositionDecisionV1::NONDETERMINISTIC_MODULE);
    CHECK(frames_equal(nondeterministic_result.candidate, seed));

    /* Plug-in modules cannot claim canonical VM81 or hash authority. */
    AlgebraicModuleV1 authority_violation = add_a;
    authority_violation.module_identity64 = UINT64_C(0xBAD0000000000003);
    authority_violation.canonical_mutation_authority = true;
    CompositionResultV1 authority_result{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              &authority_violation, 1U, seed, authority_result) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(authority_result.decision == CompositionDecisionV1::INVALID_MODULE);
    CHECK(frames_equal(authority_result.candidate, seed));

    /* The empty ordered word is the identity composition. */
    CompositionResultV1 identity{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              nullptr, 0U, seed, identity) == HHS_EXACT_STATUS_OK);
    CHECK(identity.decision == CompositionDecisionV1::READY);
    CHECK(identity.module_count == 0U);
    CHECK(identity.verified_module_count == 0U);
    CHECK(frames_equal(identity.candidate, seed));

    /* Profile validation is swappable and validator-only. */
    ProfileContext even_context{0U, UINT64_C(2), forward.candidate.words[0] % UINT64_C(2)};
    AdmissionProfileAdapterV1 even_profile{};
    even_profile.profile_identity64 = UINT64_C(0xE000000000000001);
    even_profile.profile_descriptor = reinterpret_cast<const std::uint8_t*>(PROFILE_EVEN);
    even_profile.profile_descriptor_length = sizeof(PROFILE_EVEN) - 1U;
    even_profile.validate = modular_profile_validate;
    even_profile.context = &even_context;

    ProfileValidationResultV1 even_result{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::validate_profile(
              even_profile, forward.candidate, even_result) == HHS_EXACT_STATUS_OK);
    CHECK(even_result.decision == ProfileDecisionV1::ACCEPTED);
    CHECK(even_result.accepted);
    CHECK(even_result.profile_witness64 != 0U);
    CHECK(even_result.profile_signature64 != 0U);
    CHECK(even_result.validator_only);
    CHECK(!even_result.canonical_mutation_authority);
    CHECK(!even_result.canonical_hash72_authority);
    CHECK(!even_result.canonical_hash216_authority);
    CHECK(!even_result.canonical_persistence_authority);
    CHECK(!even_result.floating_point_authority);

    ProfileContext mod5_context{0U, UINT64_C(5), UINT64_C(0)};
    AdmissionProfileAdapterV1 mod5_profile{};
    mod5_profile.profile_identity64 = UINT64_C(0xE000000000000002);
    mod5_profile.profile_descriptor = reinterpret_cast<const std::uint8_t*>(PROFILE_MOD5);
    mod5_profile.profile_descriptor_length = sizeof(PROFILE_MOD5) - 1U;
    mod5_profile.validate = modular_profile_validate;
    mod5_profile.context = &mod5_context;

    ProfileValidationResultV1 mod5_result{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::validate_profile(
              mod5_profile, forward.candidate, mod5_result) == HHS_EXACT_STATUS_OK);
    CHECK(mod5_result.decision == ProfileDecisionV1::REJECTED);
    CHECK(!mod5_result.accepted);
    CHECK(mod5_result.profile_signature64 != even_result.profile_signature64);

    /* A profile is also forbidden from claiming canonical mutation authority. */
    AdmissionProfileAdapterV1 invalid_profile = even_profile;
    invalid_profile.profile_identity64 = UINT64_C(0xE000000000000003);
    invalid_profile.canonical_hash216_authority = true;
    ProfileValidationResultV1 invalid_profile_result{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::validate_profile(
              invalid_profile, forward.candidate, invalid_profile_result) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(invalid_profile_result.decision == ProfileDecisionV1::INVALID);

    return 0;
}
