#include "hhs_pass219_vm81_pqc_firewall_1_30.h"

#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>

#define CHECK(expr) do { \
    if (!(expr)) { \
        std::fprintf(stderr, "CHECK failed at %s:%d: %s\n", __FILE__, __LINE__, #expr); \
        return 1; \
    } \
} while (0)

static bool all_zero(const std::uint8_t* bytes, std::size_t count) noexcept {
    for (std::size_t i = 0U; i < count; ++i) {
        if (bytes[i] != 0U)
            return false;
    }
    return true;
}

int main() {
    CHECK(hhs_exact_pass219_vm81_pqc_firewall_version() ==
          HHS_EXACT_PASS219_VM81_PQC_VERSION);

    HHSExactPass219Hash216TransitionViewV1 genesis{};
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&genesis) ==
          HHS_EXACT_STATUS_OK);
    CHECK(genesis.resolved_index_count == HHS_EXACT_PASS219_HASH216_OCCURRENCES);
    CHECK(hhs_exact_pass219_hash216_indexes_complete(&genesis) == HHS_EXACT_STATUS_OK);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&genesis) ==
          HHS_EXACT_STATUS_OK);

    for (std::size_t i = 0U; i < HHS_EXACT_PASS219_HASH216_OCCURRENCES; ++i) {
        const auto& occurrence = genesis.occurrences[i];
        CHECK(occurrence.absolute_position216 == i);
        CHECK(occurrence.lane_role == i / HHS_EXACT_HASH72_LEN);
        CHECK(occurrence.lane_position72 == i % HHS_EXACT_HASH72_LEN);
        CHECK(occurrence.sha256_index_present == 1U);
        CHECK(!all_zero(
            occurrence.sha256_index_record,
            HHS_EXACT_PASS219_HASH216_SHA256_BYTES));
    }

    /* A caller cannot substitute or omit one positional record. */
    HHSExactPass219Hash216TransitionViewV1 tampered = genesis;
    tampered.occurrences[117].sha256_index_record[3] ^= UINT8_C(0x01);
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&tampered) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    HHSExactPass219Hash216TransitionViewV1 missing = genesis;
    missing.occurrences[215].sha256_index_present = 0U;
    missing.resolved_index_count = 215U;
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&missing) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    /* Lane text is also part of the re-derived reference identity. */
    HHSExactPass219Hash216TransitionViewV1 lane_tamper = genesis;
    lane_tamper.receipt_hash72[0] = HHS_EXACT_HASH72_ALPHABET[1];
    CHECK(hhs_exact_pass219_vm81_pqc_hash216_reference_verify(&lane_tamper) ==
          HHS_EXACT_STATUS_INVARIANT_FAILURE);

    return 0;
}
