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
        frame.words[i] = UINT64_C(0x1122334455667788) ^ static_cast<std::uint64_t>(i * 17U);
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

static bool sha256(
    const std::uint8_t* data,
    std::size_t size,
    std::uint8_t out[HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES]
) {
    unsigned int written = 0U;
    return EVP_Digest(data, size, out, &written, EVP_sha256(), nullptr) == 1 &&
           written == HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES;
}

static bool hmac_sha512(
    const std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_PQC_KEY_BYTES>& key,
    const std::uint8_t* data,
    std::size_t size,
    std::uint8_t out[HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES]
) {
    unsigned int written = 0U;
    return HMAC(EVP_sha512(), key.data(), static_cast<int>(key.size()),
                data, size, out, &written) != nullptr &&
           written == HHS_EXACT_PASS219_VM81_ENV_HMAC_BYTES;
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
            registry, registry_count, checkpoint.expected_registry_root_sha256) !=
        HHS_EXACT_STATUS_OK)
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
    std::memcpy(auth.data() + cursor, CHECKPOINT_AUTH_DOMAIN,
                sizeof(CHECKPOINT_AUTH_DOMAIN) - 1U);
    cursor += sizeof(CHECKPOINT_AUTH_DOMAIN) - 1U;
    std::memcpy(auth.data() + cursor, checkpoint.checkpoint_root_sha256,
                HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES);
    cursor += HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES;
    if (!hmac_sha512(key, auth.data(), cursor, checkpoint.checkpoint_authenticator))
        std::abort();
    return checkpoint;
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
            entries[i].identity_sha256[j] = static_cast<std::uint8_t>((i + 1U) * 11U + j);
            entries[i].lineage_sha256[j] = static_cast<std::uint8_t>((i + 1U) * 29U + j);
        }
    }
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
    CHECK(hhs_exact_pass219_vm81_environment_version() == HHS_EXACT_PASS219_VM81_ENV_VERSION);

    std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES> genesis_a{};
    std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES> genesis_b{};
    CHECK(hhs_exact_pass219_vm81_environment_genesis_root(genesis_a.data()) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_environment_genesis_root(genesis_b.data()) == HHS_EXACT_STATUS_OK);
    CHECK(genesis_a == genesis_b);
    CHECK(hhs_exact_pass219_vm81_environment_state() == HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING);

    std::array<HHSExactPass219VM81Hash216RegistryEntryV1, 4> registry{};
    fill_registry(registry.data(), registry.size());
    std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES> registry_root_a{};
    std::array<std::uint8_t, HHS_EXACT_PASS219_VM81_ENV_SHA256_BYTES> registry_root_b{};
    CHECK(hhs_exact_pass219_vm81_environment_hash216_registry_root(
              registry.data(), registry.size(), registry_root_a.data()) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_environment_hash216_registry_root(
              registry.data(), registry.size(), registry_root_b.data()) == HHS_EXACT_STATUS_OK);
    CHECK(registry_root_a == registry_root_b);

    auto bad_registry = registry;
    bad_registry[2].position = 3U;
    CHECK(hhs_exact_pass219_vm81_environment_hash216_registry_root(
              bad_registry.data(), bad_registry.size(), registry_root_b.data()) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    const HHSExactVM81Frame frame = candidate_frame();
    const auto checkpoint = make_checkpoint(
        key, frame, registry.data(), registry.size(), 10U, 5U);

    CHECK(force_freeze() == 0);
    HHSExactVM81Frame recovered{};
    HHSExactPass219VM81EnvironmentReceiptV1 recovery{};
    CHECK(hhs_exact_pass219_vm81_environment_recover_candidate(
              &checkpoint, registry.data(), registry.size(), &recovered, &recovery) ==
          HHS_EXACT_STATUS_OK);
    CHECK(std::memcmp(&recovered, &frame, sizeof(frame)) == 0);
    CHECK(recovery.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERED_CANDIDATE);
    CHECK(recovery.state == HHS_EXACT_PASS219_VM81_ENV_STATE_RUNNING);
    CHECK(recovery.registry_reconciled == 1U);
    CHECK(recovery.anti_rollback_verified == 1U);
    CHECK(recovery.recovery_candidate_only == 1U);
    CHECK(recovery.canonical_mutation_authority == 0U);
    CHECK(recovery.canonical_receipt_authority == 0U);
    CHECK(hhs_exact_pass219_vm81_environment_anti_rollback_floor() == 10U);
    CHECK(hhs_exact_pass219_vm81_pqc_firewall_halted() == 0U);

    const auto stale = make_checkpoint(
        key, frame, registry.data(), registry.size(), 9U, 9U);
    CHECK(force_freeze() == 0);
    recovered = HHSExactVM81Frame{};
    recovery = HHSExactPass219VM81EnvironmentReceiptV1{};
    CHECK(hhs_exact_pass219_vm81_environment_recover_candidate(
              &stale, registry.data(), registry.size(), &recovered, &recovery) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);
    CHECK(recovery.decision == HHS_EXACT_PASS219_VM81_ENV_DECISION_RECOVERY_REJECTED);
    CHECK(hhs_exact_pass219_vm81_environment_state() ==
          HHS_EXACT_PASS219_VM81_ENV_STATE_RECOVERY_HALTED);
    CHECK(frame_is_zero(recovered));

    std::puts("VM81_ENVIRONMENTAL_RECOVERY_1_32_PASS");
    return 0;
}
