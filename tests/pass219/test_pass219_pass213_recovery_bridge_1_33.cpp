#include "hhs_runtime_exact_abi.h"
#include "hhs_hash216_bytes.h"

#include <openssl/evp.h>
#include <openssl/hmac.h>

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static constexpr char CHECKPOINT_DOMAIN[] =
    "HHS-P219-VM81-RECOVERY-CHECKPOINT-V1";
static constexpr char CHECKPOINT_AUTH_DOMAIN[] =
    "HHS-P219-VM81-RECOVERY-CHECKPOINT-AUTH-V1";
static constexpr char BRIDGE_KEY_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-BRIDGE-KEY-V1";
static constexpr char BRIDGE_AUTH_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-BRIDGE-AUTH-V1";
static constexpr char EVIDENCE_DOMAIN[] =
    "HHS-P219-PASS213-RECOVERY-EVIDENCE-V1";

static std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES> install_root_key() {
    std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES> key{};
    std::string hex;
    static constexpr char digits[] = "0123456789abcdef";
    hex.reserve(HHS_EXACT_PASS219_VM81_PQC_KEY_HEX_CHARS);
    for (std::size_t i = 0U; i < key.size(); ++i) {
        key[i] = static_cast<std::uint8_t>(i + 1U);
        hex.push_back(digits[(key[i] >> 4U) & 0x0FU]);
        hex.push_back(digits[key[i] & 0x0FU]);
    }
    if (setenv(HHS_EXACT_PASS219_VM81_PQC_KEY_ENV, hex.c_str(), 1) != 0)
        std::abort();
    return key;
}

static HHSExactVM81Frame candidate_frame() noexcept {
    HHSExactVM81Frame frame{};
    for (std::size_t i = 0U; i < HHS_EXACT_VM81_CELLS; ++i)
        frame.words[i] = UINT64_C(0x8877665544332211) ^ static_cast<std::uint64_t>(i * 31U);
    return frame;
}

static bool frame_is_zero(const HHSExactVM81Frame& frame) noexcept {
    HHSExactVM81Frame zero{};
    return std::memcmp(&frame, &zero, sizeof(frame)) == 0;
}

static void append_u32_be(std::uint8_t* out, std::size_t& cursor, std::uint32_t value) {
    out[cursor++] = static_cast<std::uint8_t>(value >> 24U);
    out[cursor++] = static_cast<std::uint8_t>(value >> 16U);
    out[cursor++] = static_cast<std::uint8_t>(value >> 8U);
    out[cursor++] = static_cast<std::uint8_t>(value);
}

static void append_u64_be(std::uint8_t* out, std::size_t& cursor, std::uint64_t value) {
    for (std::size_t i = 0U; i < 8U; ++i)
        out[cursor + 7U - i] = static_cast<std::uint8_t>(value >> (8U * i));
    cursor += 8U;
}

static bool sha256(const std::uint8_t* data, std::size_t size, std::uint8_t out[32]) {
    unsigned int written = 0U;
    return EVP_Digest(data, size, out, &written, EVP_sha256(), nullptr) == 1 && written == 32U;
}

static bool hmac_sha512(
    const std::uint8_t* key,
    std::size_t key_size,
    const std::uint8_t* data,
    std::size_t size,
    std::uint8_t out[64]
) {
    unsigned int written = 0U;
    return HMAC(EVP_sha512(), key, static_cast<int>(key_size), data, size, out, &written) != nullptr &&
           written == 64U;
}

static void fill_registry(
    HHSExactPass219VM81Hash216RegistryEntryV1* entries,
    std::size_t count
) noexcept {
    for (std::size_t i = 0U; i < count; ++i) {
        entries[i] = HHSExactPass219VM81Hash216RegistryEntryV1{};
        entries[i].position = static_cast<std::uint32_t>(i);
        entries[i].tombstoned = i == count - 1U ? 1U : 0U;
        for (std::size_t j = 0U; j < HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES; ++j) {
            entries[i].identity_sha256[j] = static_cast<std::uint8_t>((i + 3U) * 13U + j);
            entries[i].lineage_sha256[j] = static_cast<std::uint8_t>((i + 5U) * 23U + j);
        }
    }
}

static HHSExactPass219VM81RecoveryCheckpointV1 make_checkpoint(
    const std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES>& key,
    const HHSExactVM81Frame& frame,
    const HHSExactPass219VM81Hash216RegistryEntryV1* registry,
    std::size_t registry_count,
    std::uint64_t sequence,
    std::uint64_t floor
) {
    HHSExactPass219VM81RecoveryCheckpointV1 checkpoint{};
    checkpoint.struct_size = static_cast<std::uint32_t>(sizeof(checkpoint));
    checkpoint.version = HHS_EXACT_PASS219_VM81_ENV_VERSION;
    checkpoint.security_epoch = HHS_EXACT_PASS219_VM81_ENV_SECURITY_EPOCH;
    checkpoint.checkpoint_sequence = sequence;
    checkpoint.anti_rollback_floor = floor;
    checkpoint.expected_registry_count = static_cast<std::uint32_t>(registry_count);
    checkpoint.candidate_frame = frame;

    if (hhs_exact_pass219_vm81_environment_hash216_registry_root(
            registry, registry_count, checkpoint.expected_registry_root_sha256) != HHS_EXACT_STATUS_OK)
        std::abort();

    std::array<std::uint8_t, HHS_EXACT_VM81_FRAME_BYTES> frame_bytes{};
    std::size_t written = 0U;
    if (hhs_exact_vm81_frame_export_le(
            &frame, frame_bytes.data(), frame_bytes.size(), &written) != HHS_EXACT_STATUS_OK ||
        written != frame_bytes.size())
        std::abort();
    hhs_hash72_compute_bytes(
        frame_bytes.data(), frame_bytes.size(), checkpoint.expected_candidate_hash72);

    std::array<std::uint8_t, 2048> material{};
    std::size_t cursor = 0U;
    std::memcpy(material.data() + cursor, CHECKPOINT_DOMAIN, sizeof(CHECKPOINT_DOMAIN) - 1U);
    cursor += sizeof(CHECKPOINT_DOMAIN) - 1U;
    append_u64_be(material.data(), cursor, checkpoint.security_epoch);
    append_u64_be(material.data(), cursor, sequence);
    append_u64_be(material.data(), cursor, floor);
    append_u32_be(material.data(), cursor, checkpoint.expected_registry_count);
    std::memcpy(material.data() + cursor, checkpoint.expected_candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor += HHS_EXACT_HASH72_LEN;
    std::memcpy(material.data() + cursor, checkpoint.expected_registry_root_sha256,
                HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor += HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES;
    std::memcpy(material.data() + cursor, frame_bytes.data(), frame_bytes.size());
    cursor += frame_bytes.size();
    if (!sha256(material.data(), cursor, checkpoint.checkpoint_root_sha256))
        std::abort();

    std::array<std::uint8_t, 128> auth{};
    cursor = 0U;
    std::memcpy(auth.data() + cursor, CHECKPOINT_AUTH_DOMAIN, sizeof(CHECKPOINT_AUTH_DOMAIN) - 1U);
    cursor += sizeof(CHECKPOINT_AUTH_DOMAIN) - 1U;
    std::memcpy(auth.data() + cursor, checkpoint.checkpoint_root_sha256,
                HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor += HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES;
    if (!hmac_sha512(key.data(), key.size(), auth.data(), cursor,
                     checkpoint.checkpoint_authenticator))
        std::abort();
    return checkpoint;
}

static HHSExactPass219Pass213RecoveryEvidenceV1 make_evidence(
    const std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES>& key,
    const HHSExactPass219VM81RecoveryCheckpointV1& checkpoint,
    std::uint64_t signed_sequence
) {
    HHSExactPass219Pass213RecoveryEvidenceV1 evidence{};
    evidence.struct_size = static_cast<std::uint32_t>(sizeof(evidence));
    evidence.version = HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION;
    evidence.signed_sequence = signed_sequence;
    evidence.checkpoint_sequence = checkpoint.checkpoint_sequence;

    std::uint8_t* roots[] = {
        evidence.inventory_checkpoint_root_hash216,
        evidence.inventory_root_hash216,
        evidence.signed_checkpoint_root_hash216,
        evidence.verifier_bundle_root_hash216,
        evidence.timestamp_intent_root_hash216,
        evidence.timestamp_evidence_root_hash216,
        evidence.timestamp_anchor_root_hash216,
        evidence.timestamp_verification_receipt_hash216,
        evidence.hash216_lineage_root,
        evidence.prior_anchor_root_hash216,
        evidence.trust_bundle_sha256,
        evidence.message_imprint_sha256
    };
    for (std::size_t i = 0U; i < sizeof(roots) / sizeof(roots[0]); ++i)
        for (std::size_t j = 0U; j < 32U; ++j)
            roots[i][j] = static_cast<std::uint8_t>((i + 1U) * 17U + j + 1U);

    std::array<std::uint8_t, 1024> material{};
    std::size_t cursor = 0U;
    std::memcpy(material.data() + cursor, EVIDENCE_DOMAIN, sizeof(EVIDENCE_DOMAIN) - 1U);
    cursor += sizeof(EVIDENCE_DOMAIN) - 1U;
    append_u32_be(material.data(), cursor, HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION);
    append_u64_be(material.data(), cursor, evidence.signed_sequence);
    append_u64_be(material.data(), cursor, evidence.checkpoint_sequence);
    for (const auto* root : roots) {
        std::memcpy(material.data() + cursor, root, 32U);
        cursor += 32U;
    }
    std::memcpy(material.data() + cursor, checkpoint.checkpoint_root_sha256, 32U);
    cursor += 32U;
    std::memcpy(material.data() + cursor, checkpoint.expected_registry_root_sha256, 32U);
    cursor += 32U;
    std::memcpy(material.data() + cursor, checkpoint.expected_candidate_hash72, HHS_EXACT_HASH72_LEN);
    cursor += HHS_EXACT_HASH72_LEN;

    std::array<std::uint8_t, 64> bridge_key{};
    if (!hmac_sha512(key.data(), key.size(),
                     reinterpret_cast<const std::uint8_t*>(BRIDGE_KEY_DOMAIN),
                     sizeof(BRIDGE_KEY_DOMAIN) - 1U, bridge_key.data()))
        std::abort();
    std::array<std::uint8_t, 1100> auth_material{};
    std::size_t auth_cursor = 0U;
    std::memcpy(auth_material.data() + auth_cursor, BRIDGE_AUTH_DOMAIN,
                sizeof(BRIDGE_AUTH_DOMAIN) - 1U);
    auth_cursor += sizeof(BRIDGE_AUTH_DOMAIN) - 1U;
    std::memcpy(auth_material.data() + auth_cursor, material.data(), cursor);
    auth_cursor += cursor;
    if (!hmac_sha512(bridge_key.data(), bridge_key.size(), auth_material.data(), auth_cursor,
                     evidence.bridge_authenticator))
        std::abort();
    return evidence;
}

static int force_freeze() {
    HHSExactPass219Hash216TransitionViewV1 parent{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent) == HHS_EXACT_STATUS_OK);
    HHSExactVM81Frame frame = candidate_frame();
    HHSExactVM81Frame committed{};
    HHSExactPass219RNAAdmissionV1 admission{};
    HHSExactPass219VM81PQCFirewallReceiptV1 firewall{};
    HHSExactPass219VM81PQCSignatureReceiptV1 signature{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};
    CHECK(hhs_exact_pass219_vm81_environment_admit_signed(
              220U, 99U, nullptr, &frame, &parent,
              0, 0U, HHS_EXACT_PASS219_HOLO4_FEEDBACK_NONE, 0,
              &committed, &admission, &firewall, &signature, &environment) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(hhs_exact_pass219_vm81_environment_state() ==
          HHS_EXACT_PASS219_VM81_ENV_STATE_FROZEN);
    return 0;
}

int main() {
    const auto key = install_root_key();
    CHECK(hhs_exact_pass219_pass213_recovery_version() ==
          HHS_EXACT_PASS219_PASS213_RECOVERY_VERSION);

    std::array<HHSExactPass219VM81Hash216RegistryEntryV1, 4> registry{};
    fill_registry(registry.data(), registry.size());
    const HHSExactVM81Frame frame = candidate_frame();
    const auto checkpoint = make_checkpoint(
        key, frame, registry.data(), registry.size(), 10U, 5U);

    /* signed_sequence intentionally exceeds native checkpoint_sequence to prove
     * the two monotonic sequence domains are independently bound, not conflated. */
    const auto evidence = make_evidence(key, checkpoint, 77U);

    CHECK(force_freeze() == 0);
    HHSExactVM81Frame recovered{};
    HHSExactPass219VM81EnvironmentReceiptV1 environment{};
    HHSExactPass219Pass213RecoveryReceiptV1 pass213{};
    CHECK(hhs_exact_pass219_vm81_environment_recover_pass213_candidate(
              &checkpoint, registry.data(), registry.size(), &evidence,
              &recovered, &environment, &pass213) == HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&recovered, &frame, sizeof(frame)) == 0);
    CHECK(pass213.decision == HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_CANDIDATE_RECOVERED);
    CHECK(pass213.reason == HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_NONE);
    CHECK(pass213.signed_sequence == 77U);
    CHECK(pass213.checkpoint_sequence == 10U);
    CHECK(pass213.inventory_bound == 1U);
    CHECK(pass213.pqc_checkpoint_bound == 1U);
    CHECK(pass213.rfc3161_anchor_bound == 1U);
    CHECK(pass213.hash216_lineage_bound == 1U);
    CHECK(pass213.native_checkpoint_bound == 1U);
    CHECK(pass213.bridge_authenticator_verified == 1U);
    CHECK(pass213.recovery_candidate_only == 1U);
    CHECK(pass213.canonical_mutation_authority == 0U);
    CHECK(pass213.canonical_receipt_authority == 0U);
    CHECK(environment.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERED_CANDIDATE);
    CHECK(hhs_exact_pass219_vm81_environment_anti_rollback_floor() == 10U);
    CHECK(hhs_exact_pass219_vm81_pqc_firewall_halted() == 0U);

    /* Any Pass213 root tamper fails before hidden native recovery and latches
     * both the environmental recovery state and inherited firewall. */
    CHECK(force_freeze() == 0);
    auto tampered = evidence;
    tampered.timestamp_anchor_root_hash216[7] ^= 0x5AU;
    recovered = HHSExactVM81Frame{};
    environment = HHSExactPass219VM81EnvironmentReceiptV1{};
    pass213 = HHSExactPass219Pass213RecoveryReceiptV1{};
    CHECK(hhs_exact_pass219_vm81_environment_recover_pass213_candidate(
              &checkpoint, registry.data(), registry.size(), &tampered,
              &recovered, &environment, &pass213) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(frame_is_zero(recovered));
    CHECK(pass213.decision == HHS_EXACT_PASS219_PASS213_RECOVERY_DECISION_REJECTED);
    CHECK(pass213.reason == HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_AUTHENTICATOR);
    CHECK(hhs_exact_pass219_vm81_environment_state() ==
          HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
    CHECK(hhs_exact_pass219_vm81_pqc_firewall_halted() == 1U);
    CHECK(hhs_exact_pass219_vm81_pqc_firewall_halt_reason() ==
          HHS_EXACT_PASS219_VM81_PQC_HALT_PASS213_RECOVERY_EVIDENCE_FAILED);

    /* Sequence mismatch is independently classified and remains fail closed. */
    auto bad_sequence = evidence;
    bad_sequence.checkpoint_sequence = checkpoint.checkpoint_sequence + 1U;
    recovered = HHSExactVM81Frame{};
    environment = HHSExactPass219VM81EnvironmentReceiptV1{};
    pass213 = HHSExactPass219Pass213RecoveryReceiptV1{};
    CHECK(hhs_exact_pass219_vm81_environment_recover_pass213_candidate(
              &checkpoint, registry.data(), registry.size(), &bad_sequence,
              &recovered, &environment, &pass213) == HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(frame_is_zero(recovered));
    CHECK(pass213.reason == HHS_EXACT_PASS219_PASS213_RECOVERY_REASON_SEQUENCE);
    CHECK(pass213.canonical_mutation_authority == 0U);
    CHECK(pass213.canonical_receipt_authority == 0U);

    std::puts("PASS219_PASS213_RECOVERY_BRIDGE_1_33_PASS");
    return 0;
}
