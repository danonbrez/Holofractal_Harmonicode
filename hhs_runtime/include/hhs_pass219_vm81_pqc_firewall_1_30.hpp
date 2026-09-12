#ifndef HHS_PASS219_VM81_PQC_FIREWALL_1_30_HPP
#define HHS_PASS219_VM81_PQC_FIREWALL_1_30_HPP

#include "hhs_pass219_post219_compositional_development_1_29.hpp"
#include "hhs_pass219_core_holographic_rna_cell_wall_1_24.hpp"
#include "hhs_hash216_bytes.h"

#include <openssl/crypto.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <vector>

namespace hhs::pass219 {

static constexpr std::uint32_t HHS_PASS219_VM81_PQC_FIREWALL_INTERFACE_VERSION_V1 = 1U;
static constexpr std::size_t HHS_PASS219_VM81_PQC_KEY_BYTES_V1 = 64U;
static constexpr std::size_t HHS_PASS219_VM81_PQC_TAG_BYTES_V1 = 64U;

enum class VM81PQCProfileV1 : std::uint8_t {
    INVALID = 0U,
    HMAC_SHA512_512 = 1U
};

enum class VM81PQCHaltReasonV1 : std::uint8_t {
    NONE = 0U,
    INVALID_FIREWALL_KEY = 1U,
    INVALID_PASS_PATH = 2U,
    INVALID_CELL_WALL_PATH = 3U,
    INVALID_HASH216_REFERENCE = 4U,
    INVALID_HASH_LINEAGE = 5U,
    INVALID_CANDIDATE_HASH = 6U,
    INVALID_PQC_AUTHENTICATOR = 7U,
    AUTHORITY_ESCALATION = 8U,
    CHILD_HASH216_INVARIANT = 9U,
    LATCHED = 10U
};

enum class VM81PQCFirewallDecisionV1 : std::uint8_t {
    INVALID = 0U,
    ROUTED_AND_SEALED = 1U,
    READY_FOR_CANONICAL_ADMISSION = 2U,
    CANONICAL_REJECTED = 3U,
    COMMITTED = 4U,
    HALTED = 5U
};

struct VM81PQCInstructionEnvelopeV1 final {
    std::uint32_t interface_version{HHS_PASS219_VM81_PQC_FIREWALL_INTERFACE_VERSION_V1};
    std::uint32_t pass_number{};
    std::uint64_t instruction_sequence{};
    std::array<char, HHS_HASH72_BYTES_STRLEN> candidate_hash72{};
    std::array<char, HHS_EXACT_UQCEL_HASH216_STRLEN> referenced_hash216_identity{};
    std::array<char, HHS_HASH216_BYTES_STRLEN> cell_wall_path_hash216{};
    std::uint64_t graph_signature64{};
    std::uint64_t tensor_signature64{};
    std::uint64_t decision_signature64{};
    std::uint8_t selected_lane{};
    VM81PQCProfileV1 pqc_profile{VM81PQCProfileV1::HMAC_SHA512_512};
    std::array<std::uint8_t, HHS_PASS219_VM81_PQC_TAG_BYTES_V1> pqc_tag{};

    bool cell_wall_routed{false};
    bool hash216_reference_verified{false};
    bool candidate_only{true};
    bool canonical_mutation_authority{false};
    bool canonical_hash72_authority{false};
    bool canonical_hash216_authority{false};
    bool canonical_persistence_authority{false};
};

struct VM81PQCFirewallResultV1 final {
    HHSExactStatus status{HHS_EXACT_STATUS_INVALID_ARGUMENT};
    VM81PQCFirewallDecisionV1 decision{VM81PQCFirewallDecisionV1::INVALID};
    VM81PQCHaltReasonV1 halt_reason{VM81PQCHaltReasonV1::NONE};
    HHSExactVM81Frame committed_frame{};
    HHSExactPass219RNAAdmissionV1 admission{};

    bool halted{false};
    bool firewall_is_canonical_authority{false};
    bool delegated_to_inherited_rna_authority{false};
    bool parent_hash216_reference_verified{false};
    bool child_hash216_reference_verified{false};
    bool canonical_receipt_owned_by_inherited_authority{true};
};

/*
 * VM81 pre-execution provenance firewall.
 *
 * The current cryptographic profile is a symmetric SHA-512 HMAC with a
 * 512-bit kernel-held key.  It is used as a post-quantum symmetric
 * authentication profile: the public API never receives the key and cannot
 * manufacture a valid membrane token.  This is intentionally algorithm-
 * versioned so a public-key PQ signature profile (for example ML-DSA) can be
 * added later without changing the authority contract.
 *
 * A valid instruction must simultaneously prove:
 *   1. pass number is post-219 (>= 220),
 *   2. the parent Hash216 array is structurally complete and every one of its
 *      216 positional SHA-256 records revalidates through the authoritative
 *      index resolver,
 *   3. the candidate was routed through the Pass 219 RNA C++ cell wall,
 *   4. the exact VM81 candidate hash and cell-wall path hash still match,
 *   5. the kernel-held HMAC authenticator matches,
 *   6. the UQCEL previous Hash72 is the referenced parent receipt Hash72.
 *
 * Any provenance failure latches the firewall HALTED before canonical RNA
 * admission is invoked.  A normal semantic/canonical constraint rejection is
 * not a firewall fault; it returns CANONICAL_REJECTED with no committed frame.
 */
class VM81PQCInstructionFirewallV1 final {
public:
    using Key = std::array<std::uint8_t, HHS_PASS219_VM81_PQC_KEY_BYTES_V1>;

    VM81PQCInstructionFirewallV1(
        hhs::rna::CoreHolographicRNACellWall& cell_wall,
        const Key& kernel_key
    ) noexcept
        : cell_wall_(cell_wall), kernel_key_(kernel_key) {
        bool any_nonzero = false;
        for (const std::uint8_t value : kernel_key_)
            any_nonzero = any_nonzero || value != 0U;
        if (!any_nonzero)
            latch(VM81PQCHaltReasonV1::INVALID_FIREWALL_KEY);
    }

    bool halted() const noexcept { return halted_; }
    VM81PQCHaltReasonV1 last_halt_reason() const noexcept { return last_halt_reason_; }

    HHSExactStatus route_and_seal(
        std::uint32_t pass_number,
        std::uint64_t instruction_sequence,
        const HHSExactVM81Frame& candidate,
        const HHSExactPass219Hash216TransitionViewV1& referenced_hash216,
        HHSExactPass219Hash216IndexResolverV1 index_resolver,
        void* index_context,
        std::uint8_t feedback_lane,
        std::int8_t feedback_trinary,
        HHSExactPass219Holo4StateV1& state,
        HHSExactPass219Holo4PreparedV1& prepared,
        HHSExactPass219Holo4DecisionV1& decision,
        VM81PQCInstructionEnvelopeV1& out_envelope
    ) {
        out_envelope = VM81PQCInstructionEnvelopeV1{};
        if (halted_)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        if (!Post219CompositionalDevelopmentABIV1::pass_number_valid(pass_number)) {
            latch(VM81PQCHaltReasonV1::INVALID_PASS_PATH);
            return HHS_EXACT_STATUS_RANGE_ERROR;
        }
        if (verify_hash216_reference(referenced_hash216, index_resolver, index_context) !=
            HHS_EXACT_STATUS_OK) {
            latch(VM81PQCHaltReasonV1::INVALID_HASH216_REFERENCE);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        const HHSExactStatus route_status = cell_wall_.route_parallel(
            candidate,
            referenced_hash216,
            feedback_lane,
            feedback_trinary,
            state,
            prepared,
            decision);
        if (route_status != HHS_EXACT_STATUS_OK ||
            !route_evidence_valid(prepared, decision, referenced_hash216)) {
            latch(VM81PQCHaltReasonV1::INVALID_CELL_WALL_PATH);
            return route_status == HHS_EXACT_STATUS_OK
                ? HHS_EXACT_STATUS_INVARIANT_FAILURE
                : route_status;
        }

        try {
            out_envelope.pass_number = pass_number;
            out_envelope.instruction_sequence = instruction_sequence;
            out_envelope.graph_signature64 = prepared.graph_signature64;
            out_envelope.tensor_signature64 = prepared.tensor_signature64;
            out_envelope.decision_signature64 = decision.decision_signature64;
            out_envelope.selected_lane = decision.selected_lane;
            out_envelope.cell_wall_routed = true;
            out_envelope.hash216_reference_verified = true;

            if (candidate_hash72(candidate, out_envelope.candidate_hash72) != HHS_EXACT_STATUS_OK) {
                latch(VM81PQCHaltReasonV1::INVALID_CANDIDATE_HASH);
                out_envelope = VM81PQCInstructionEnvelopeV1{};
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
            std::memcpy(
                out_envelope.referenced_hash216_identity.data(),
                referenced_hash216.transition_identity216,
                HHS_EXACT_UQCEL_HASH216_STRLEN);

            std::vector<std::uint8_t> path_material;
            build_path_material(out_envelope, path_material);
            hhs_hash216_compute_bytes(
                path_material.data(),
                path_material.size(),
                out_envelope.cell_wall_path_hash216.data());

            std::vector<std::uint8_t> auth_material;
            if (build_auth_material(
                    out_envelope,
                    candidate,
                    referenced_hash216,
                    auth_material) != HHS_EXACT_STATUS_OK) {
                latch(VM81PQCHaltReasonV1::INVALID_CANDIDATE_HASH);
                out_envelope = VM81PQCInstructionEnvelopeV1{};
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
            if (!compute_hmac(auth_material, out_envelope.pqc_tag)) {
                latch(VM81PQCHaltReasonV1::INVALID_PQC_AUTHENTICATOR);
                out_envelope = VM81PQCInstructionEnvelopeV1{};
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
            return HHS_EXACT_STATUS_OK;
        } catch (...) {
            latch(VM81PQCHaltReasonV1::INVALID_CELL_WALL_PATH);
            out_envelope = VM81PQCInstructionEnvelopeV1{};
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
    }

    HHSExactStatus admit_or_halt(
        const Post219DevelopmentResultV1& development,
        const hhs::substrate::ProfileValidationResultV1& profile,
        const VM81PQCInstructionEnvelopeV1& envelope,
        const HHSExactPass219Hash216TransitionViewV1& referenced_hash216,
        const HHSExactUQCELInputV1& uqcel_input,
        std::int8_t lo_shu_group,
        std::uint16_t g243,
        HHSExactPass219Hash216IndexResolverV1 index_resolver,
        void* index_context,
        VM81PQCFirewallResultV1& out_result
    ) {
        out_result = VM81PQCFirewallResultV1{};
        if (halted_) {
            set_halted_result(out_result, VM81PQCHaltReasonV1::LATCHED);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (!development_ready(development) || !profile_ready(profile) ||
            development.pass_number != envelope.pass_number) {
            latch(VM81PQCHaltReasonV1::AUTHORITY_ESCALATION);
            set_halted_result(out_result, VM81PQCHaltReasonV1::AUTHORITY_ESCALATION);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        const VM81PQCHaltReasonV1 verification = verify_envelope(
            envelope,
            development.composition.candidate,
            referenced_hash216,
            index_resolver,
            index_context);
        if (verification != VM81PQCHaltReasonV1::NONE) {
            latch(verification);
            set_halted_result(out_result, verification);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        out_result.parent_hash216_reference_verified = true;

        if (std::memcmp(
                uqcel_input.previous_hash72,
                referenced_hash216.receipt_hash72,
                HHS_EXACT_HASH72_STRLEN) != 0) {
            latch(VM81PQCHaltReasonV1::INVALID_HASH_LINEAGE);
            set_halted_result(out_result, VM81PQCHaltReasonV1::INVALID_HASH_LINEAGE);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        HHSExactVM81Frame staged_committed{};
        HHSExactPass219RNAAdmissionV1 staged_admission{};
        out_result.delegated_to_inherited_rna_authority = true;
        const HHSExactStatus status = hhs_exact_pass219_rna_admit_composed(
            &uqcel_input,
            &development.composition.candidate,
            lo_shu_group,
            g243,
            index_resolver,
            index_context,
            &staged_committed,
            &staged_admission);
        out_result.status = status;
        out_result.admission = staged_admission;

        if (status != HHS_EXACT_STATUS_OK) {
            if (!frame_is_zero(staged_committed)) {
                latch(VM81PQCHaltReasonV1::CHILD_HASH216_INVARIANT);
                set_halted_result(out_result, VM81PQCHaltReasonV1::CHILD_HASH216_INVARIANT);
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
            }
            out_result.decision = VM81PQCFirewallDecisionV1::CANONICAL_REJECTED;
            return status;
        }

        if (!frame_equal(staged_committed, development.composition.candidate) ||
            verify_hash216_reference(
                staged_admission.transition,
                index_resolver,
                index_context) != HHS_EXACT_STATUS_OK) {
            latch(VM81PQCHaltReasonV1::CHILD_HASH216_INVARIANT);
            set_halted_result(out_result, VM81PQCHaltReasonV1::CHILD_HASH216_INVARIANT);
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }

        out_result.committed_frame = staged_committed;
        out_result.status = HHS_EXACT_STATUS_OK;
        out_result.decision = VM81PQCFirewallDecisionV1::COMMITTED;
        out_result.child_hash216_reference_verified = true;
        return HHS_EXACT_STATUS_OK;
    }

private:
    static constexpr char PATH_DOMAIN[] = "HHS-P219-VM81-PQC-CELL-WALL-PATH-V1";
    static constexpr char AUTH_DOMAIN[] = "HHS-P219-VM81-PQC-INSTRUCTION-AUTH-V1";

    hhs::rna::CoreHolographicRNACellWall& cell_wall_;
    Key kernel_key_{};
    bool halted_{false};
    VM81PQCHaltReasonV1 last_halt_reason_{VM81PQCHaltReasonV1::NONE};

    void latch(VM81PQCHaltReasonV1 reason) noexcept {
        halted_ = true;
        last_halt_reason_ = reason;
    }

    static void set_halted_result(
        VM81PQCFirewallResultV1& out_result,
        VM81PQCHaltReasonV1 reason
    ) noexcept {
        out_result.status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_result.decision = VM81PQCFirewallDecisionV1::HALTED;
        out_result.halt_reason = reason;
        out_result.halted = true;
        out_result.committed_frame = HHSExactVM81Frame{};
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

    static bool development_ready(const Post219DevelopmentResultV1& value) noexcept {
        const auto& composition = value.composition;
        return value.interface_version == HHS_PASS219_POST219_INTERFACE_VERSION_V1 &&
               Post219CompositionalDevelopmentABIV1::pass_number_valid(value.pass_number) &&
               value.status == HHS_EXACT_STATUS_OK &&
               value.decision == Post219DevelopmentDecisionV1::READY &&
               value.development_surface && value.candidate_only &&
               value.pass219_substrate_required && value.pass219_rna_lowering_available &&
               value.canonical_handoff_required &&
               !value.external_invocation_is_authority &&
               !value.canonical_mutation_authority &&
               !value.canonical_hash72_authority &&
               !value.canonical_hash216_authority &&
               !value.canonical_persistence_authority &&
               !value.floating_point_authority &&
               composition.status == HHS_EXACT_STATUS_OK &&
               composition.decision == hhs::substrate::CompositionDecisionV1::READY &&
               composition.verified_module_count == composition.module_count &&
               composition.candidate_only && composition.exact_machine_surface &&
               composition.deterministic_replay_required &&
               composition.vm81_handoff_required &&
               !composition.canonical_mutation_authority &&
               !composition.canonical_hash72_authority &&
               !composition.canonical_hash216_authority &&
               !composition.canonical_persistence_authority &&
               !composition.floating_point_authority;
    }

    static bool profile_ready(
        const hhs::substrate::ProfileValidationResultV1& value
    ) noexcept {
        return value.status == HHS_EXACT_STATUS_OK &&
               value.decision == hhs::substrate::ProfileDecisionV1::ACCEPTED &&
               value.accepted && value.validator_only &&
               value.deterministic_replay_required &&
               !value.canonical_mutation_authority &&
               !value.canonical_hash72_authority &&
               !value.canonical_hash216_authority &&
               !value.canonical_persistence_authority &&
               !value.floating_point_authority;
    }

    static bool route_evidence_valid(
        const HHSExactPass219Holo4PreparedV1& prepared,
        const HHSExactPass219Holo4DecisionV1& decision,
        const HHSExactPass219Hash216TransitionViewV1& referenced_hash216
    ) noexcept {
        return prepared.struct_size == sizeof(prepared) &&
               prepared.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
               decision.struct_size == sizeof(decision) &&
               decision.version == HHS_EXACT_PASS219_HOLO4_VERSION &&
               prepared.candidate_only == 1U && prepared.exact_integer_only == 1U &&
               prepared.hash216_positions_complete == 1U &&
               prepared.canonical_mutation_authority == 0U &&
               prepared.canonical_hash72_authority == 0U &&
               prepared.canonical_hash216_authority == 0U &&
               prepared.canonical_persistence_authority == 0U &&
               prepared.floating_point_authority == 0U &&
               decision.candidate_only == 1U && decision.exact_integer_only == 1U &&
               decision.canonical_mutation_authority == 0U &&
               decision.canonical_hash72_authority == 0U &&
               decision.canonical_hash216_authority == 0U &&
               decision.canonical_persistence_authority == 0U &&
               decision.floating_point_authority == 0U &&
               std::memcmp(
                   prepared.source_transition_identity216,
                   referenced_hash216.transition_identity216,
                   HHS_EXACT_UQCEL_HASH216_STRLEN) == 0 &&
               std::memcmp(
                   decision.source_transition_identity216,
                   referenced_hash216.transition_identity216,
                   HHS_EXACT_UQCEL_HASH216_STRLEN) == 0;
    }

    static HHSExactStatus candidate_hash72(
        const HHSExactVM81Frame& candidate,
        std::array<char, HHS_HASH72_BYTES_STRLEN>& out_hash
    ) noexcept {
        std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> bytes{};
        std::size_t written = 0U;
        const HHSExactStatus status = hhs_exact_vm81_frame_export_le(
            &candidate,
            bytes.data(),
            bytes.size(),
            &written);
        if (status != HHS_EXACT_STATUS_OK || written != bytes.size())
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        hhs_hash72_compute_bytes(bytes.data(), bytes.size(), out_hash.data());
        return out_hash[HHS_HASH72_BYTES_LEN] == '\0'
            ? HHS_EXACT_STATUS_OK
            : HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    static HHSExactStatus verify_hash216_reference(
        const HHSExactPass219Hash216TransitionViewV1& transition,
        HHSExactPass219Hash216IndexResolverV1 index_resolver,
        void* index_context
    ) noexcept {
        if (index_resolver == nullptr)
            return HHS_EXACT_STATUS_INVALID_ARGUMENT;
        if (hhs_exact_pass219_hash216_indexes_complete(&transition) != HHS_EXACT_STATUS_OK)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        HHSExactPass219Hash216TransitionViewV1 normalized{};
        HHSExactStatus status = hhs_exact_pass219_hash216_transition_init(
            transition.previous_hash72,
            transition.change_hash72,
            transition.receipt_hash72,
            transition.transition_identity216,
            &normalized);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        if (std::memcmp(
                normalized.transition_word216,
                transition.transition_word216,
                HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        for (std::size_t i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
            const auto& entry = transition.occurrences[i];
            const auto& expected_entry = normalized.occurrences[i];
            if (entry.struct_size != sizeof(entry) ||
                entry.version != hhs_exact_pass219_rna_version() ||
                entry.absolute_position216 != expected_entry.absolute_position216 ||
                entry.lane_role != expected_entry.lane_role ||
                entry.lane_position72 != expected_entry.lane_position72 ||
                entry.glyph != expected_entry.glyph ||
                entry.sha256_index_present != 1U)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;

            std::array<std::uint8_t, HHS_EXACT_PASS219_HASH216_SHA256_BYTES> expected_index{};
            status = index_resolver(
                transition.transition_identity216,
                entry.lane_role,
                entry.lane_position72,
                entry.absolute_position216,
                entry.glyph,
                expected_index.data(),
                index_context);
            if (status != HHS_EXACT_STATUS_OK)
                return status;
            if (CRYPTO_memcmp(
                    expected_index.data(),
                    entry.sha256_index_record,
                    expected_index.size()) != 0)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        return HHS_EXACT_STATUS_OK;
    }

    static void append_bytes(
        std::vector<std::uint8_t>& out,
        const void* data,
        std::size_t size
    ) {
        const auto* first = static_cast<const std::uint8_t*>(data);
        out.insert(out.end(), first, first + size);
    }

    static void append_u32(std::vector<std::uint8_t>& out, std::uint32_t value) {
        for (std::size_t i = 0U; i < 4U; ++i)
            out.push_back(static_cast<std::uint8_t>(value >> (8U * i)));
    }

    static void append_u64(std::vector<std::uint8_t>& out, std::uint64_t value) {
        for (std::size_t i = 0U; i < 8U; ++i)
            out.push_back(static_cast<std::uint8_t>(value >> (8U * i)));
    }

    static void build_path_material(
        const VM81PQCInstructionEnvelopeV1& envelope,
        std::vector<std::uint8_t>& out
    ) {
        out.clear();
        append_bytes(out, PATH_DOMAIN, sizeof(PATH_DOMAIN) - 1U);
        append_u32(out, envelope.pass_number);
        append_u64(out, envelope.instruction_sequence);
        append_bytes(out, envelope.candidate_hash72.data(), HHS_HASH72_BYTES_LEN);
        append_bytes(
            out,
            envelope.referenced_hash216_identity.data(),
            HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
        append_u64(out, envelope.graph_signature64);
        append_u64(out, envelope.tensor_signature64);
        append_u64(out, envelope.decision_signature64);
        out.push_back(envelope.selected_lane);
    }

    static HHSExactStatus build_auth_material(
        const VM81PQCInstructionEnvelopeV1& envelope,
        const HHSExactVM81Frame& candidate,
        const HHSExactPass219Hash216TransitionViewV1& referenced_hash216,
        std::vector<std::uint8_t>& out
    ) {
        std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> frame_bytes{};
        std::size_t written = 0U;
        const HHSExactStatus status = hhs_exact_vm81_frame_export_le(
            &candidate,
            frame_bytes.data(),
            frame_bytes.size(),
            &written);
        if (status != HHS_EXACT_STATUS_OK || written != frame_bytes.size())
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;

        out.clear();
        append_bytes(out, AUTH_DOMAIN, sizeof(AUTH_DOMAIN) - 1U);
        append_u32(out, envelope.interface_version);
        append_u32(out, envelope.pass_number);
        append_u64(out, envelope.instruction_sequence);
        append_bytes(out, envelope.candidate_hash72.data(), HHS_HASH72_BYTES_LEN);
        append_bytes(
            out,
            envelope.cell_wall_path_hash216.data(),
            HHS_HASH216_BYTES_LEN);
        append_bytes(out, frame_bytes.data(), frame_bytes.size());
        append_bytes(
            out,
            referenced_hash216.transition_word216,
            HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
        append_bytes(
            out,
            referenced_hash216.transition_identity216,
            HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
        for (std::size_t i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
            append_bytes(
                out,
                referenced_hash216.occurrences[i].sha256_index_record,
                HHS_EXACT_PASS219_HASH216_SHA256_BYTES);
        }
        append_u64(out, envelope.graph_signature64);
        append_u64(out, envelope.tensor_signature64);
        append_u64(out, envelope.decision_signature64);
        out.push_back(envelope.selected_lane);
        out.push_back(static_cast<std::uint8_t>(envelope.pqc_profile));
        return HHS_EXACT_STATUS_OK;
    }

    bool compute_hmac(
        const std::vector<std::uint8_t>& material,
        std::array<std::uint8_t, HHS_PASS219_VM81_PQC_TAG_BYTES_V1>& out_tag
    ) const noexcept {
        unsigned int written = 0U;
        unsigned char* result = HMAC(
            EVP_sha512(),
            kernel_key_.data(),
            static_cast<int>(kernel_key_.size()),
            material.data(),
            material.size(),
            out_tag.data(),
            &written);
        return result != nullptr && written == out_tag.size();
    }

    VM81PQCHaltReasonV1 verify_envelope(
        const VM81PQCInstructionEnvelopeV1& envelope,
        const HHSExactVM81Frame& candidate,
        const HHSExactPass219Hash216TransitionViewV1& referenced_hash216,
        HHSExactPass219Hash216IndexResolverV1 index_resolver,
        void* index_context
    ) const {
        if (envelope.interface_version != HHS_PASS219_VM81_PQC_FIREWALL_INTERFACE_VERSION_V1 ||
            envelope.pqc_profile != VM81PQCProfileV1::HMAC_SHA512_512 ||
            !Post219CompositionalDevelopmentABIV1::pass_number_valid(envelope.pass_number))
            return VM81PQCHaltReasonV1::INVALID_PASS_PATH;
        if (!envelope.cell_wall_routed || !envelope.hash216_reference_verified ||
            !envelope.candidate_only ||
            envelope.canonical_mutation_authority ||
            envelope.canonical_hash72_authority ||
            envelope.canonical_hash216_authority ||
            envelope.canonical_persistence_authority)
            return VM81PQCHaltReasonV1::INVALID_CELL_WALL_PATH;
        if (verify_hash216_reference(referenced_hash216, index_resolver, index_context) !=
            HHS_EXACT_STATUS_OK)
            return VM81PQCHaltReasonV1::INVALID_HASH216_REFERENCE;
        if (std::memcmp(
                envelope.referenced_hash216_identity.data(),
                referenced_hash216.transition_identity216,
                HHS_EXACT_UQCEL_HASH216_STRLEN) != 0)
            return VM81PQCHaltReasonV1::INVALID_HASH216_REFERENCE;

        std::array<char, HHS_HASH72_BYTES_STRLEN> expected_candidate_hash{};
        if (candidate_hash72(candidate, expected_candidate_hash) != HHS_EXACT_STATUS_OK ||
            std::memcmp(
                expected_candidate_hash.data(),
                envelope.candidate_hash72.data(),
                HHS_HASH72_BYTES_STRLEN) != 0)
            return VM81PQCHaltReasonV1::INVALID_CANDIDATE_HASH;

        std::vector<std::uint8_t> path_material;
        build_path_material(envelope, path_material);
        std::array<char, HHS_HASH216_BYTES_STRLEN> expected_path{};
        hhs_hash216_compute_bytes(
            path_material.data(),
            path_material.size(),
            expected_path.data());
        if (std::memcmp(
                expected_path.data(),
                envelope.cell_wall_path_hash216.data(),
                HHS_HASH216_BYTES_STRLEN) != 0)
            return VM81PQCHaltReasonV1::INVALID_CELL_WALL_PATH;

        std::vector<std::uint8_t> auth_material;
        if (build_auth_material(envelope, candidate, referenced_hash216, auth_material) !=
            HHS_EXACT_STATUS_OK)
            return VM81PQCHaltReasonV1::INVALID_CANDIDATE_HASH;
        std::array<std::uint8_t, HHS_PASS219_VM81_PQC_TAG_BYTES_V1> expected_tag{};
        if (!compute_hmac(auth_material, expected_tag) ||
            CRYPTO_memcmp(expected_tag.data(), envelope.pqc_tag.data(), expected_tag.size()) != 0)
            return VM81PQCHaltReasonV1::INVALID_PQC_AUTHENTICATOR;
        return VM81PQCHaltReasonV1::NONE;
    }
};

}  // namespace hhs::pass219

#endif
