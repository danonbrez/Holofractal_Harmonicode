#include "hhs_pass219_vm81_pqc_firewall_1_30.hpp"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

using hhs::pass219::Post219CompositionalDevelopmentABIV1;
using hhs::pass219::Post219DevelopmentResultV1;
using hhs::pass219::VM81PQCInstructionEnvelopeV1;
using hhs::pass219::VM81PQCInstructionFirewallV1;
using hhs::pass219::VM81PQCFirewallDecisionV1;
using hhs::pass219::VM81PQCFirewallResultV1;
using hhs::pass219::VM81PQCHaltReasonV1;
using hhs::rna::CoreHolographicRNACellWall;
using hhs::rna::OrthogonalGlyphMembrane;
using hhs::substrate::AdmissionProfileAdapterV1;
using hhs::substrate::AlgebraicModuleV1;
using hhs::substrate::CanonicalHandoffResultV1;
using hhs::substrate::ProfileValidationResultV1;

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static bool frames_equal(const HHSExactVM81Frame& left, const HHSExactVM81Frame& right) noexcept {
    return std::memcmp(&left, &right, sizeof(left)) == 0;
}

static bool frame_is_zero(const HHSExactVM81Frame& value) noexcept {
    HHSExactVM81Frame zero{};
    return frames_equal(value, zero);
}

static HHSExactStatus identity_apply(
    const HHSExactVM81Frame* input,
    HHSExactVM81Frame* output,
    std::uint64_t* witness,
    const void*
) noexcept {
    if (input == nullptr || output == nullptr || witness == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *output = *input;
    *witness = UINT64_C(0x2190130000000001) ^ input->words[0];
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus identity_verify(
    const HHSExactVM81Frame* input,
    const HHSExactVM81Frame* output,
    std::uint64_t witness,
    const void*
) noexcept {
    if (input == nullptr || output == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    const std::uint64_t expected = UINT64_C(0x2190130000000001) ^ input->words[0];
    return frames_equal(*input, *output) && witness == expected
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}

static HHSExactStatus accept_profile(
    const HHSExactVM81Frame* candidate,
    bool* accepted,
    std::uint64_t* witness,
    const void*
) noexcept {
    if (candidate == nullptr || accepted == nullptr || witness == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    *accepted = true;
    *witness = UINT64_C(0x2190130000000002) ^ candidate->words[0];
    return HHS_EXACT_STATUS_OK;
}

static HHSExactStatus test_index_resolver(
    const char transition_identity216[HHS_EXACT_UQCEL_HASH216_STRLEN],
    std::uint8_t lane_role,
    std::uint8_t lane_position72,
    std::uint16_t absolute_position216,
    std::uint8_t glyph,
    std::uint8_t out_sha256[HHS_EXACT_PASS219_HASH216_SHA256_BYTES],
    void*
) {
    if (transition_identity216 == nullptr || out_sha256 == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (absolute_position216 !=
        static_cast<std::uint16_t>(static_cast<std::uint16_t>(lane_role) * 72U + lane_position72))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_HASH216_SHA256_BYTES; ++i) {
        out_sha256[i] = static_cast<std::uint8_t>(
            glyph ^ lane_role ^ lane_position72 ^
            static_cast<std::uint8_t>(absolute_position216) ^
            static_cast<std::uint8_t>(i) ^
            static_cast<std::uint8_t>(
                transition_identity216[i % HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]));
    }
    return HHS_EXACT_STATUS_OK;
}

static void fill_hash72(char out[HHS_EXACT_HASH72_STRLEN], std::uint8_t offset) noexcept {
    for (std::size_t i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i + offset) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

static void fill_identity216(char out[HHS_EXACT_UQCEL_HASH216_STRLEN]) noexcept {
    for (std::size_t i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i)
        out[i] = HHS_EXACT_HASH72_ALPHABET[(i * 5U + 7U) % HHS_EXACT_HASH72_LEN];
    out[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
}

static HHSExactStatus build_parent_transition(
    HHSExactPass219Hash216TransitionViewV1& transition
) {
    char previous[HHS_EXACT_HASH72_STRLEN]{};
    char change[HHS_EXACT_HASH72_STRLEN]{};
    char receipt[HHS_EXACT_HASH72_STRLEN]{};
    char identity[HHS_EXACT_UQCEL_HASH216_STRLEN]{};
    fill_hash72(previous, 0U);
    fill_hash72(change, 1U);
    fill_hash72(receipt, 2U);
    fill_identity216(identity);
    HHSExactStatus status = hhs_exact_pass219_hash216_transition_init(
        previous, change, receipt, identity, &transition);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_hash216_resolve_indexes(
        &transition, test_index_resolver, nullptr);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    return hhs_exact_pass219_hash216_indexes_complete(&transition);
}

struct UQCELOwners final {
    std::uint8_t P{4U};
    std::uint8_t p{3U};
    std::uint8_t q{5U};
    std::uint8_t delta{1U};
    std::uint8_t A{16U};
    std::uint8_t B{16U};
};

static HHSExactBigUIntView view_of(const std::uint8_t* value) noexcept {
    HHSExactBigUIntView view{};
    view.struct_size = static_cast<std::uint32_t>(sizeof(view));
    view.byte_length = 1U;
    view.bytes_be = value;
    return view;
}

static HHSExactStatus build_uqcel_input(
    const UQCELOwners& owners,
    const HHSExactPass219Hash216TransitionViewV1& parent,
    HHSExactUQCELInputV1& input
) noexcept {
    input = HHSExactUQCELInputV1{};
    input.struct_size = static_cast<std::uint32_t>(sizeof(input));
    input.uqcel_version = hhs_exact_uqcel_version();
    input.profile = HHS_EXACT_UQCEL_PROFILE_INTEGER_SYMMETRIC_V1;
    input.P = view_of(&owners.P);
    input.p = view_of(&owners.p);
    input.q = view_of(&owners.q);
    input.delta = view_of(&owners.delta);
    input.A = view_of(&owners.A);
    input.B = view_of(&owners.B);
    input.cell81 = 41U;
    input.left_basis8 = HHS_EXACT_PHASE_X;
    input.right_basis8 = HHS_EXACT_PHASE_Y;
    HHSExactStatus status = hhs_exact_uqcel_source_sha256(input.source_envelope_sha256);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    std::memcpy(
        input.previous_hash72,
        parent.receipt_hash72,
        HHS_EXACT_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

static Post219DevelopmentResultV1 build_development(HHSExactVM81Frame seed) {
    static constexpr char DESCRIPTOR[] =
        "pass=220;operation=identity;pqc-firewall=required;authority=candidate-only";
    AlgebraicModuleV1 module{};
    module.module_identity64 = UINT64_C(0x2200000000000130);
    module.semantic_descriptor = reinterpret_cast<const std::uint8_t*>(DESCRIPTOR);
    module.semantic_descriptor_length = sizeof(DESCRIPTOR) - 1U;
    module.apply = identity_apply;
    module.verify = identity_verify;

    Post219DevelopmentResultV1 development{};
    const HHSExactStatus status = Post219CompositionalDevelopmentABIV1::compose(
        220U, &module, 1U, seed, development);
    if (status != HHS_EXACT_STATUS_OK)
        return Post219DevelopmentResultV1{};
    return development;
}

static ProfileValidationResultV1 build_profile(const Post219DevelopmentResultV1& development) {
    static constexpr char DESCRIPTOR[] =
        "pass=220;profile=accept-test;role=noncanonical-precheck";
    AdmissionProfileAdapterV1 profile{};
    profile.profile_identity64 = UINT64_C(0x2200000000010130);
    profile.profile_descriptor = reinterpret_cast<const std::uint8_t*>(DESCRIPTOR);
    profile.profile_descriptor_length = sizeof(DESCRIPTOR) - 1U;
    profile.validate = accept_profile;

    ProfileValidationResultV1 result{};
    if (Post219CompositionalDevelopmentABIV1::validate_profile(
            development, profile, result) != HHS_EXACT_STATUS_OK)
        return ProfileValidationResultV1{};
    return result;
}

static CoreHolographicRNACellWall make_cell_wall(
    OrthogonalGlyphMembrane& membrane
) noexcept {
    return CoreHolographicRNACellWall(membrane);
}

int main() {
    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(build_parent_transition(parent) == HHS_EXACT_STATUS_OK);

    HHSExactVM81Frame seed{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        seed.words[i] = UINT64_C(0x0102030405060708) ^ static_cast<std::uint64_t>(i);

    const Post219DevelopmentResultV1 development = build_development(seed);
    CHECK(development.status == HHS_EXACT_STATUS_OK);
    const ProfileValidationResultV1 profile = build_profile(development);
    CHECK(profile.accepted);

    std::uint8_t one = 1U;
    HHSExactBigUIntView one_view = view_of(&one);
    OrthogonalGlyphMembrane membrane(one_view, one_view);
    CHECK(membrane.status() == HHS_EXACT_STATUS_OK);
    CoreHolographicRNACellWall cell_wall = make_cell_wall(membrane);

    VM81PQCInstructionFirewallV1::Key key{};
    for (std::size_t i = 0U; i < key.size(); ++i)
        key[i] = static_cast<std::uint8_t>(i + 1U);

    HHSExactPass219Holo4StateV1 state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&state) == HHS_EXACT_STATUS_OK);
    HHSExactPass219Holo4PreparedV1 prepared{};
    HHSExactPass219Holo4DecisionV1 decision{};
    VM81PQCInstructionEnvelopeV1 envelope{};

    VM81PQCInstructionFirewallV1 firewall(cell_wall, key);
    CHECK(!firewall.halted());
    CHECK(firewall.route_and_seal(
              220U,
              1U,
              development.composition.candidate,
              parent,
              test_index_resolver,
              nullptr,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE,
              0,
              state,
              prepared,
              decision,
              envelope) == HHS_EXACT_STATUS_OK);
    CHECK(envelope.cell_wall_routed);
    CHECK(envelope.hash216_reference_verified);
    CHECK(envelope.candidate_only);
    CHECK(!envelope.canonical_mutation_authority);

    UQCELOwners owners{};
    HHSExactUQCELInputV1 input{};
    CHECK(build_uqcel_input(owners, parent, input) == HHS_EXACT_STATUS_OK);

    /* Valid cell-wall path + valid parent Hash216 array + valid PQC authenticator commits. */
    VM81PQCFirewallResultV1 committed{};
    CHECK(firewall.admit_or_halt(
              development,
              profile,
              envelope,
              parent,
              input,
              0,
              0U,
              test_index_resolver,
              nullptr,
              committed) == HHS_EXACT_STATUS_OK);
    CHECK(committed.decision == VM81PQCFirewallDecisionV1::COMMITTED);
    CHECK(!committed.halted);
    CHECK(committed.delegated_to_inherited_rna_authority);
    CHECK(committed.parent_hash216_reference_verified);
    CHECK(committed.child_hash216_reference_verified);
    CHECK(committed.canonical_receipt_owned_by_inherited_authority);
    CHECK(frames_equal(committed.committed_frame, development.composition.candidate));
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&committed.admission.transition) ==
          HHS_EXACT_STATUS_OK);

    /* The old post-219 direct handoff is closed; firewall admission is now required. */
    CanonicalHandoffResultV1 legacy_direct{};
    CHECK(Post219CompositionalDevelopmentABIV1::submit_uqcel_canonical_request(
              development, profile, input, legacy_direct) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(frame_is_zero(legacy_direct.committed_frame));

    /* A forged/outside-membrane envelope latches HALT before canonical delegation. */
    HHSExactPass219Holo4StateV1 outside_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&outside_state) == HHS_EXACT_STATUS_OK);
    VM81PQCInstructionFirewallV1 outside_firewall(cell_wall, key);
    VM81PQCInstructionEnvelopeV1 outside{};
    outside.pass_number = 220U;
    VM81PQCFirewallResultV1 outside_result{};
    CHECK(outside_firewall.admit_or_halt(
              development,
              profile,
              outside,
              parent,
              input,
              0,
              0U,
              test_index_resolver,
              nullptr,
              outside_result) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(outside_firewall.halted());
    CHECK(outside_result.decision == VM81PQCFirewallDecisionV1::HALTED);
    CHECK(outside_result.halt_reason == VM81PQCHaltReasonV1::INVALID_CELL_WALL_PATH);
    CHECK(!outside_result.delegated_to_inherited_rna_authority);
    CHECK(frame_is_zero(outside_result.committed_frame));

    /* A wrong authenticator also latches HALT and cannot reach RNA canonical authority. */
    HHSExactPass219Holo4StateV1 auth_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&auth_state) == HHS_EXACT_STATUS_OK);
    VM81PQCInstructionFirewallV1 auth_firewall(cell_wall, key);
    VM81PQCInstructionEnvelopeV1 auth_envelope{};
    HHSExactPass219Holo4PreparedV1 auth_prepared{};
    HHSExactPass219Holo4DecisionV1 auth_decision{};
    CHECK(auth_firewall.route_and_seal(
              220U, 2U, development.composition.candidate, parent,
              test_index_resolver, nullptr,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              auth_state, auth_prepared, auth_decision, auth_envelope) == HHS_EXACT_STATUS_OK);
    auth_envelope.pqc_tag[0] ^= UINT8_C(0x01);
    VM81PQCFirewallResultV1 auth_result{};
    CHECK(auth_firewall.admit_or_halt(
              development, profile, auth_envelope, parent, input,
              0, 0U, test_index_resolver, nullptr, auth_result) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(auth_result.halt_reason == VM81PQCHaltReasonV1::INVALID_PQC_AUTHENTICATOR);
    CHECK(auth_firewall.halted());
    CHECK(!auth_result.delegated_to_inherited_rna_authority);

    /* An incomplete or forged Hash216 positional array halts at the firewall. */
    HHSExactPass219Hash216TransitionViewV1 bad_parent = parent;
    bad_parent.occurrences[17].sha256_index_present = 0U;
    bad_parent.resolved_index_count = HHS_EXACT_PASS219_HASH216_OCCURRENCES - 1U;
    HHSExactPass219Holo4StateV1 hash_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&hash_state) == HHS_EXACT_STATUS_OK);
    VM81PQCInstructionFirewallV1 hash_firewall(cell_wall, key);
    VM81PQCInstructionEnvelopeV1 hash_envelope{};
    HHSExactPass219Holo4PreparedV1 hash_prepared{};
    HHSExactPass219Holo4DecisionV1 hash_decision{};
    CHECK(hash_firewall.route_and_seal(
              220U, 3U, development.composition.candidate, bad_parent,
              test_index_resolver, nullptr,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              hash_state, hash_prepared, hash_decision, hash_envelope) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(hash_firewall.halted());
    CHECK(hash_firewall.last_halt_reason() == VM81PQCHaltReasonV1::INVALID_HASH216_REFERENCE);

    /* Correctly authenticated instructions with the wrong lineage still halt. */
    HHSExactPass219Holo4StateV1 lineage_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&lineage_state) == HHS_EXACT_STATUS_OK);
    VM81PQCInstructionFirewallV1 lineage_firewall(cell_wall, key);
    VM81PQCInstructionEnvelopeV1 lineage_envelope{};
    HHSExactPass219Holo4PreparedV1 lineage_prepared{};
    HHSExactPass219Holo4DecisionV1 lineage_decision{};
    CHECK(lineage_firewall.route_and_seal(
              220U, 4U, development.composition.candidate, parent,
              test_index_resolver, nullptr,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              lineage_state, lineage_prepared, lineage_decision, lineage_envelope) ==
          HHS_EXACT_STATUS_OK);
    HHSExactUQCELInputV1 wrong_lineage = input;
    std::memset(wrong_lineage.previous_hash72, '0', HHS_EXACT_HASH72_LEN);
    wrong_lineage.previous_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    VM81PQCFirewallResultV1 lineage_result{};
    CHECK(lineage_firewall.admit_or_halt(
              development, profile, lineage_envelope, parent, wrong_lineage,
              0, 0U, test_index_resolver, nullptr, lineage_result) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(lineage_result.halt_reason == VM81PQCHaltReasonV1::INVALID_HASH_LINEAGE);
    CHECK(lineage_firewall.halted());

    /* Semantic UQCEL rejection is fail-closed but is not misclassified as a provenance attack. */
    HHSExactPass219Holo4StateV1 reject_state{};
    CHECK(hhs_exact_pass219_holo4_state_init(&reject_state) == HHS_EXACT_STATUS_OK);
    VM81PQCInstructionFirewallV1 reject_firewall(cell_wall, key);
    VM81PQCInstructionEnvelopeV1 reject_envelope{};
    HHSExactPass219Holo4PreparedV1 reject_prepared{};
    HHSExactPass219Holo4DecisionV1 reject_decision{};
    CHECK(reject_firewall.route_and_seal(
              220U, 5U, development.composition.candidate, parent,
              test_index_resolver, nullptr,
              HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              reject_state, reject_prepared, reject_decision, reject_envelope) ==
          HHS_EXACT_STATUS_OK);
    UQCELOwners invalid_owners{};
    invalid_owners.delta = 2U;
    HHSExactUQCELInputV1 invalid_input{};
    CHECK(build_uqcel_input(invalid_owners, parent, invalid_input) == HHS_EXACT_STATUS_OK);
    VM81PQCFirewallResultV1 rejected{};
    CHECK(reject_firewall.admit_or_halt(
              development, profile, reject_envelope, parent, invalid_input,
              0, 0U, test_index_resolver, nullptr, rejected) ==
          HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    CHECK(rejected.decision == VM81PQCFirewallDecisionV1::CANONICAL_REJECTED);
    CHECK(!rejected.halted);
    CHECK(!reject_firewall.halted());
    CHECK(frame_is_zero(rejected.committed_frame));

    return 0;
}
