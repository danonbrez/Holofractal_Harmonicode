#include "hhs_pass219_plug_and_play_canonical_handoff_1_28.hpp"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::substrate::AdmissionProfileAdapterV1;
using hhs::substrate::AlgebraicModuleV1;
using hhs::substrate::CanonicalHandoffDecisionV1;
using hhs::substrate::CanonicalHandoffResultV1;
using hhs::substrate::CompositionResultV1;
using hhs::substrate::Pass219UQCELCanonicalHandoffV1;
using hhs::substrate::PlugAndPlayMathLogicSubstrateV1;
using hhs::substrate::ProfileValidationResultV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

struct WordTransformContext final {
    std::size_t word{};
    std::uint64_t xor_mask{};
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

static HHSExactStatus xor_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const WordTransformContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    *output = *input;
    output->words[context.word] ^= context.xor_mask;
    *witness = output->words[context.word] ^ context.xor_mask ^ UINT64_C(0x128219);
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus xor_verify(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t witness,
    const void* raw_context
) noexcept {
    if (input == nullptr || output == nullptr || raw_context == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const auto& context = *static_cast<const WordTransformContext*>(raw_context);
    if (context.word >= HHS_EXACT_VM81_CELLS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    HHSExactVM81Frame expected = *input;
    expected.words[context.word] ^= context.xor_mask;
    const std::uint64_t expected_witness =
        expected.words[context.word] ^ context.xor_mask ^ UINT64_C(0x128219);
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
    *witness = candidate->words[context.word] ^ context.expected ^ UINT64_C(0xC0A11);
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

static HHSExactVM81Frame build_seed() noexcept {
    std::uint8_t raw[HHS_EXACT_VM81_FRAME_BYTES]{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_FRAME_BYTES; ++i)
        raw[i] = static_cast<std::uint8_t>((i * 17U + 11U) & 0xFFU);
    HHSExactVM81Frame frame{};
    const HHSExactStatus status = hhs_exact_vm81_frame_import_le(raw, sizeof(raw), &frame);
    if (status != HHS_EXACT_STATUS_OK)
        return HHSExactVM81Frame{};
    return frame;
}

int main() {
    static constexpr char MODULE_DESCRIPTOR[] =
        "structure=opaque-exact-transform;operation=word0-xor;presentation=handoff-test";
    static constexpr char PROFILE_DESCRIPTOR[] =
        "profile=exact-word0-postcondition;role=noncanonical-precheck";

    const HHSExactVM81Frame seed = build_seed();
    CHECK(!frame_is_zero(seed));

    WordTransformContext transform_context{0U, UINT64_C(0x0102030405060708)};
    AlgebraicModuleV1 module{};
    module.module_identity64 = UINT64_C(0x1280000000000001);
    module.semantic_descriptor = reinterpret_cast<const std::uint8_t*>(MODULE_DESCRIPTOR);
    module.semantic_descriptor_length = sizeof(MODULE_DESCRIPTOR) - 1U;
    module.apply = xor_apply;
    module.verify = xor_verify;
    module.context = &transform_context;

    CompositionResultV1 composition{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::compose(
              &module, 1U, seed, composition) == HHS_EXACT_STATUS_OK);
    CHECK(!frames_equal(composition.candidate, seed));

    ExactWordProfileContext accepted_context{0U, composition.candidate.words[0]};
    AdmissionProfileAdapterV1 accepted_profile{};
    accepted_profile.profile_identity64 = UINT64_C(0x1280000000001001);
    accepted_profile.profile_descriptor =
        reinterpret_cast<const std::uint8_t*>(PROFILE_DESCRIPTOR);
    accepted_profile.profile_descriptor_length = sizeof(PROFILE_DESCRIPTOR) - 1U;
    accepted_profile.validate = exact_word_profile;
    accepted_profile.context = &accepted_context;

    ProfileValidationResultV1 accepted{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::validate_profile(
              accepted_profile, composition.candidate, accepted) == HHS_EXACT_STATUS_OK);
    CHECK(accepted.accepted);

    UQCELOwners owners{};
    HHSExactUQCELInputV1 valid_input{};
    CHECK(build_uqcel_input(owners, valid_input) == HHS_EXACT_STATUS_OK);

    /* Positive path: generic candidate reaches canonical authority only by delegation. */
    CanonicalHandoffResultV1 committed{};
    CHECK(Pass219UQCELCanonicalHandoffV1::commit(
              composition, accepted, valid_input, committed) == HHS_EXACT_STATUS_OK);
    CHECK(committed.decision == CanonicalHandoffDecisionV1::COMMITTED);
    CHECK(committed.delegated_to_inherited_c_authority);
    CHECK(committed.inherited_authority_revalidated);
    CHECK(!committed.adapter_is_canonical_authority);
    CHECK(!committed.profile_precheck_is_commit_authority);
    CHECK(committed.canonical_receipt_owned_by_inherited_authority);
    CHECK(frames_equal(committed.committed_frame, composition.candidate));
    CHECK(committed.admission.uqcel.decision == HHS_EXACT_UQCEL_DECISION_ADMIT);
    CHECK(committed.admission.uqcel.frame_committed == 1U);
    CHECK(std::strlen(committed.admission.final_receipt_hash72) == HHS_EXACT_HASH72_LEN);
    CHECK(std::strlen(committed.admission.final_hash216_triplet) ==
          HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    CHECK(std::strlen(committed.admission.final_hash216_identity) ==
          HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);

    /* Generic profile rejection prevents any invocation of canonical authority. */
    ExactWordProfileContext rejected_context{
        0U, composition.candidate.words[0] ^ UINT64_C(1)};
    AdmissionProfileAdapterV1 rejected_profile = accepted_profile;
    rejected_profile.profile_identity64 = UINT64_C(0x1280000000001002);
    rejected_profile.context = &rejected_context;
    ProfileValidationResultV1 rejected{};
    CHECK(PlugAndPlayMathLogicSubstrateV1::validate_profile(
              rejected_profile, composition.candidate, rejected) == HHS_EXACT_STATUS_OK);
    CHECK(!rejected.accepted);

    CanonicalHandoffResultV1 precheck_rejected{};
    CHECK(Pass219UQCELCanonicalHandoffV1::commit(
              composition, rejected, valid_input, precheck_rejected) ==
          HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(precheck_rejected.decision ==
          CanonicalHandoffDecisionV1::PROFILE_NOT_ACCEPTED);
    CHECK(!precheck_rejected.delegated_to_inherited_c_authority);
    CHECK(!precheck_rejected.inherited_authority_revalidated);
    CHECK(frame_is_zero(precheck_rejected.committed_frame));

    /* A permissive generic profile cannot bypass inherited UQCEL authority. */
    UQCELOwners invalid_owners{};
    invalid_owners.delta = 2U;
    HHSExactUQCELInputV1 invalid_input{};
    CHECK(build_uqcel_input(invalid_owners, invalid_input) == HHS_EXACT_STATUS_OK);

    CanonicalHandoffResultV1 canonical_rejected{};
    CHECK(Pass219UQCELCanonicalHandoffV1::commit(
              composition, accepted, invalid_input, canonical_rejected) ==
          HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(canonical_rejected.decision ==
          CanonicalHandoffDecisionV1::DELEGATED_REJECTED);
    CHECK(canonical_rejected.delegated_to_inherited_c_authority);
    CHECK(canonical_rejected.inherited_authority_revalidated);
    CHECK(frame_is_zero(canonical_rejected.committed_frame));

    /* Tampered candidate metadata cannot gain a canonical handoff. */
    CompositionResultV1 tampered = composition;
    tampered.canonical_hash216_authority = true;
    CanonicalHandoffResultV1 tampered_result{};
    CHECK(Pass219UQCELCanonicalHandoffV1::commit(
              tampered, accepted, valid_input, tampered_result) ==
          HHS_EXACT_STATUS_INVALID_ARGUMENT);
    CHECK(tampered_result.decision == CanonicalHandoffDecisionV1::INVALID);
    CHECK(!tampered_result.delegated_to_inherited_c_authority);

    return 0;
}
