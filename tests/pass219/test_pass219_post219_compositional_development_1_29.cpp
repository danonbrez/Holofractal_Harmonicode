#include "hhs_pass219_post219_compositional_development_1_29.hpp"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::pass219::Post219CompositionalDevelopmentABIV1;
using hhs::pass219::Post219DevelopmentDecisionV1;
using hhs::pass219::Post219DevelopmentResultV1;
using hhs::substrate::AdmissionProfileAdapterV1;
using hhs::substrate::AlgebraicModuleV1;
using hhs::substrate::CanonicalHandoffDecisionV1;
using hhs::substrate::CanonicalHandoffResultV1;
using hhs::substrate::ProfileValidationResultV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

enum class ArithmeticKind : std::uint8_t {
    ADD = 0U,
    MULTIPLY = 1U
};

struct ArithmeticContext final {
    std::size_t word{};
    std::uint64_t operand{};
    ArithmeticKind kind{ArithmeticKind::ADD};
};

struct ExactWordProfileContext final {
    std::size_t word{};
    std::uint64_t expected{};
};

struct UQCELOwners final {
    std::uint8_t P{4U};
    std::uint8_t p{3U};
    std::uint8_t q{5U};
    std::uint8_t delta{1U};
    std::uint8_t A{16U};
    std::uint8_t B{16U};
};

static bool frames_equal(
    const HHSExactVM81Frame& left,
    const HHSExactVM81Frame& right
) noexcept {
    return std::memcmp(&left, &right, sizeof(left)) == 0;
}

static bool frame_is_zero(const HHSExactVM81Frame& value) noexcept {
    HHSExactVM81Frame zero{};
    return frames_equal(value, zero);
}

static std::uint64_t apply_arithmetic_value(
    std::uint64_t input,
    const ArithmeticContext& context
) noexcept {
    return context.kind == ArithmeticKind::ADD
        ? input + context.operand
        : input * context.operand;
}

static HHSExactStatus arithmetic_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const ArithmeticContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    *output = *input;
    output->words[context.word] = apply_arithmetic_value(
        input->words[context.word], context);
    *witness = output->words[context.word] ^
               input->words[context.word] ^
               context.operand ^
               static_cast<std::uint64_t>(context.kind) ^
               UINT64_C(0x2200129);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus arithmetic_verify(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const ArithmeticContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    HHSExactVM81Frame expected = *input;
    expected.words[context.word] = apply_arithmetic_value(
        input->words[context.word], context);
    const std::uint64_t expected_witness =
        expected.words[context.word] ^
        input->words[context.word] ^
        context.operand ^
        static_cast<std::uint64_t>(context.kind) ^
        UINT64_C(0x2200129);

    if (!frames_equal(expected, *output) || witness != expected_witness)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus exact_word_profile(
    const HHSExactVM81Frame* candidate,
    bool* accepted,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (candidate == nullptr || accepted == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const ExactWordProfileContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *accepted = candidate->words[context.word] == context.expected;
    *witness = candidate->words[context.word] ^ context.expected ^ UINT64_C(0x220129C0A11);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactBigUIntView view_of(const std::uint8_t* value) noexcept {
    HHSExactBigUIntView view{};
    view.struct_size = static_cast<std::uint32_t>(sizeof(view));
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static HHSExactStatus build_uqcel_input(
    const UQCELOwners& owners,
    HHSExactUQCELInputV1& input
) noexcept {
    input = HHSExactUQCELInputV1{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.flags = 0U;
    input.P = view_of(&owners.P);
    input.p = view_of(&owners.p);
    input.q = view_of(&owners.q);
    input.delta = view_of(&owners.delta);
    input.A = view_of(&owners.A);
    input.B = view_of(&owners.B);
    input.cell81 = 41U;
    input.left_basis8 = 0U;
    input.right_basis8 = 1U;
    const HHSExactStatus status = hhs_exact_uqcel_source_sha256(input.source_envelope_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    std::memset(input.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    input.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    return HHS_EXACT_STATUS_OK;
}

static AlgebraicModuleV1 make_module(
    std::uint64_t identity,
    const char* descriptor,
    std::size_t descriptor_length,
    const ArithmeticContext* context
) noexcept {
    AlgebraicModuleV1 module{};
    module.module_identity64 = identity;
    module.semantic_descriptor = reinterpret_cast<const std::uint8_t*>(descriptor);
    module.semantic_descriptor_length = descriptor_length;
    module.apply = arithmetic_apply;
    module.verify = arithmetic_verify;
    module.context = context;
    return module;
}

int main() {
    static constexpr char ADD_DESCRIPTOR[] =
        "pass=220;operation=add;authority=candidate-only;lowering=pass219-rna";
    static constexpr char MUL_DESCRIPTOR[] =
        "pass=220;operation=multiply;authority=candidate-only;lowering=pass219-rna";
    static constexpr char PROFILE_DESCRIPTOR[] =
        "pass=220;profile=word0-exact;authority=precheck-only";

    HHSExactVM81Frame seed{};
    seed.words[0] = 3U;
    seed.words[1] = UINT64_C(0x219220);

    ArithmeticContext add2{0U, 2U, ArithmeticKind::ADD};
    ArithmeticContext multiply4{0U, 4U, ArithmeticKind::MULTIPLY};

    AlgebraicModuleV1 modules[2] = {
        make_module(UINT64_C(0x2200000000000001), ADD_DESCRIPTOR, sizeof(ADD_DESCRIPTOR) - 1U, &add2),
        make_module(UINT64_C(0x2200000000000002), MUL_DESCRIPTOR, sizeof(MUL_DESCRIPTOR) - 1U, &multiply4),
    };

    /* Pass 220+ composes through the stable Pass 219 substrate. */
    Post219DevelopmentResultV1 development{};
    CHECK(Post219CompositionalDevelopmentABIV1::compose(
              220U, modules, 2U, seed, development) == HHS_EXACT_STATUS_OK);
    CHECK(development.decision == Post219DevelopmentDecisionV1::READY);
    CHECK(development.pass_number == 220U);
    CHECK(development.composition.candidate.words[0] == 20U);
    CHECK(development.development_surface);
    CHECK(development.candidate_only);
    CHECK(development.pass219_substrate_required);
    CHECK(development.pass219_rna_lowering_available);
    CHECK(development.canonical_handoff_required);
    CHECK(!development.external_invocation_is_authority);
    CHECK(!development.canonical_mutation_authority);
    CHECK(!development.canonical_hash72_authority);
    CHECK(!development.canonical_hash216_authority);
    CHECK(!development.canonical_persistence_authority);

    /* Composition order remains semantic data for later passes. */
    AlgebraicModuleV1 reversed[2] = {modules[1], modules[0]};
    Post219DevelopmentResultV1 reversed_development{};
    CHECK(Post219CompositionalDevelopmentABIV1::compose(
              220U, reversed, 2U, seed, reversed_development) == HHS_EXACT_STATUS_OK);
    CHECK(reversed_development.composition.candidate.words[0] == 14U);
    CHECK(!frames_equal(
        development.composition.candidate,
        reversed_development.composition.candidate));

    /* Pass numbers below 220 cannot masquerade as post-219 development. */
    Post219DevelopmentResultV1 pass219_rejected{};
    CHECK(Post219CompositionalDevelopmentABIV1::compose(
              219U, modules, 2U, seed, pass219_rejected) == HHS_EXACT_STATUS_RANGE_ERROR);
    CHECK(pass219_rejected.decision == Post219DevelopmentDecisionV1::PASS_NUMBER_REJECTED);
    CHECK(frames_equal(pass219_rejected.composition.candidate, seed));

    /* Authority-escalating modules are rejected by inherited substrate admission. */
    AlgebraicModuleV1 authority_escalation = modules[0];
    authority_escalation.module_identity64 = UINT64_C(0x22000000000000FF);
    authority_escalation.canonical_hash72_authority = true;
    Post219DevelopmentResultV1 escalation_rejected{};
    CHECK(Post219CompositionalDevelopmentABIV1::compose(
              220U, &authority_escalation, 1U, seed, escalation_rejected) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(escalation_rejected.decision == Post219DevelopmentDecisionV1::COMPOSITION_REJECTED);
    CHECK(frames_equal(escalation_rejected.composition.candidate, seed));

    /* Pass 220+ receives RNA C++ cell-wall lowering/witness services without authority. */
    HHSExactPass219NativePhaseWitnessV1 phase{};
    CHECK(Post219CompositionalDevelopmentABIV1::lower_native_phase(
              220U, 0U, 1U, phase) == HHS_EXACT_STATUS_OK);
    CHECK(phase.ordered_source_preserved == 1U);
    CHECK(phase.left_basis == 0U);
    CHECK(phase.right_basis == 1U);

    HHSExactPass219HydrationCoordinateV1 coordinate{};
    CHECK(Post219CompositionalDevelopmentABIV1::lower_hydration_coordinate(
              220U, 41U, 0, 7U, 42U, coordinate) == HHS_EXACT_STATUS_OK);
    CHECK(coordinate.cell81 == 41U);
    CHECK(coordinate.operation64 == 7U);
    CHECK(coordinate.g243 == 42U);
    CHECK(coordinate.slot5184 < HHS_EXACT_PASS219_HYDRATION_SLOT_COUNT);

    /* Profile checks remain deterministic prechecks rather than commit authority. */
    ExactWordProfileContext accepted_context{0U, 20U};
    AdmissionProfileAdapterV1 profile{};
    profile.profile_identity64 = UINT64_C(0x2200000000010001);
    profile.profile_descriptor = reinterpret_cast<const std::uint8_t*>(PROFILE_DESCRIPTOR);
    profile.profile_descriptor_length = sizeof(PROFILE_DESCRIPTOR) - 1U;
    profile.validate = exact_word_profile;
    profile.context = &accepted_context;

    ProfileValidationResultV1 accepted{};
    CHECK(Post219CompositionalDevelopmentABIV1::validate_profile(
              development, profile, accepted) == HHS_EXACT_STATUS_OK);
    CHECK(accepted.accepted);
    CHECK(accepted.validator_only);
    CHECK(!accepted.canonical_mutation_authority);

    UQCELOwners owners{};
    HHSExactUQCELInputV1 valid_input{};
    CHECK(build_uqcel_input(owners, valid_input) == HHS_EXACT_STATUS_OK);

    /* Canonical success is a delegated request, not Pass 220 authority. */
    CanonicalHandoffResultV1 committed{};
    CHECK(Post219CompositionalDevelopmentABIV1::submit_uqcel_canonical_request(
              development, accepted, valid_input, committed) == HHS_EXACT_STATUS_OK);
    CHECK(committed.decision == CanonicalHandoffDecisionV1::COMMITTED);
    CHECK(committed.delegated_to_inherited_c_authority);
    CHECK(committed.inherited_authority_revalidated);
    CHECK(!committed.adapter_is_canonical_authority);
    CHECK(committed.canonical_receipt_owned_by_inherited_authority);
    CHECK(frames_equal(committed.committed_frame, development.composition.candidate));

    /* Invalid canonical inputs remain rejectable after every high-level precheck passes. */
    UQCELOwners invalid_owners{};
    invalid_owners.delta = 2U;
    HHSExactUQCELInputV1 invalid_input{};
    CHECK(build_uqcel_input(invalid_owners, invalid_input) == HHS_EXACT_STATUS_OK);
    CanonicalHandoffResultV1 canonical_rejected{};
    CHECK(Post219CompositionalDevelopmentABIV1::submit_uqcel_canonical_request(
              development, accepted, invalid_input, canonical_rejected) ==
          HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(canonical_rejected.decision == CanonicalHandoffDecisionV1::DELEGATED_REJECTED);
    CHECK(canonical_rejected.delegated_to_inherited_c_authority);
    CHECK(frame_is_zero(canonical_rejected.committed_frame));

    /* Forged development authority metadata cannot cross the handoff. */
    Post219DevelopmentResultV1 forged = development;
    forged.canonical_hash216_authority = true;
    CanonicalHandoffResultV1 forged_result{};
    CHECK(Post219CompositionalDevelopmentABIV1::submit_uqcel_canonical_request(
              forged, accepted, valid_input, forged_result) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(!forged_result.delegated_to_inherited_c_authority);
    CHECK(frame_is_zero(forged_result.committed_frame));

    return 0;
}
