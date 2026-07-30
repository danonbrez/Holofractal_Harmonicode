#include "hhs_p174_runtime.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static int digest_is_zero(const uint8_t digest[HHS_P174_SHA256_BYTES]) {
    uint32_t i;
    for (i = 0U; i < HHS_P174_SHA256_BYTES; ++i) {
        if (digest[i] != 0U) {
            return 0;
        }
    }
    return 1;
}

int main(void) {
    hhs_p174_phase_coordinate phase;
    hhs_p163_vmrc_snapshot source;
    hhs_p163_vmrc_snapshot candidate;
    hhs_p174_frame_write writes[3];
    uint8_t value = 0U;
    int authority = 174;
    int wrong_authority = 175;
    char predecessor[HHS_P174_HASH72_CHARACTERS];
    char current[HHS_P174_HASH72_CHARACTERS];
    char successor[HHS_P174_HASH72_CHARACTERS];
    char combined[HHS_P174_HASH216_CHARACTERS];
    char changed[HHS_P174_HASH216_CHARACTERS];
    uint8_t logical_identity[HHS_P174_SHA256_BYTES];
    uint8_t indexes[HHS_P174_HASH216_CHARACTERS][HHS_P174_SHA256_BYTES];
    uint8_t indexes_repeated[HHS_P174_HASH216_CHARACTERS][HHS_P174_SHA256_BYTES];
    uint8_t changed_indexes[HHS_P174_HASH216_CHARACTERS][HHS_P174_SHA256_BYTES];
    uint8_t index_root[HHS_P174_SHA256_BYTES];
    uint8_t repeated_root[HHS_P174_SHA256_BYTES];
    uint8_t changed_root[HHS_P174_SHA256_BYTES];
    hhs_p174_execution_path path;
    int64_t advantage;
    uint32_t i;

    assert(hhs_p174_phase_at(UINT64_C(0), &phase) == HHS_P174_OK);
    assert(phase.phase64 == 0U && phase.phase72 == 0U && phase.phase81 == 0U);
    assert(phase.full_phase_lock == 0U);
    assert(hhs_p174_phase_at(UINT64_C(5184), &phase) == HHS_P174_OK);
    assert(phase.phase64 == 0U && phase.phase72 == 0U && phase.phase81 == 0U);
    assert(phase.phase5184 == 0U && phase.full_phase_lock == 1U);

    assert(hhs_p163_vmrc_snapshot_init(&source) == HHS_P163_VMRC_OK);
    writes[0].position = 0U;
    writes[0].thread = 0U;
    writes[0].value = 1U;
    writes[1].position = 8U;
    writes[1].thread = 7U;
    writes[1].value = 1U;
    writes[2].position = 80U;
    writes[2].thread = 63U;
    writes[2].value = 1U;
    assert(hhs_p174_build_candidate_frame(
        &source,
        writes,
        3U,
        &authority,
        &authority,
        &candidate
    ) == HHS_P174_OK);
    assert(hhs_p163_vmrc_snapshot_get(&source, 0U, 0U, &value) == HHS_P163_VMRC_OK);
    assert(value == 0U);
    assert(hhs_p163_vmrc_snapshot_get(&candidate, 0U, 0U, &value) == HHS_P163_VMRC_OK);
    assert(value == 1U);
    assert(hhs_p163_vmrc_snapshot_get(&candidate, 8U, 7U, &value) == HHS_P163_VMRC_OK);
    assert(value == 1U);
    assert(hhs_p174_build_candidate_frame(
        &source,
        writes,
        3U,
        &wrong_authority,
        &authority,
        &candidate
    ) == HHS_P174_AUTHORITY_DENIED);

    for (i = 0U; i < HHS_P174_HASH72_CHARACTERS; ++i) {
        predecessor[i] = (char)('A' + (i % 26U));
        current[i] = (char)('a' + (i % 26U));
        successor[i] = (char)('0' + (i % 10U));
    }
    assert(hhs_p174_hash216_join(
        predecessor,
        sizeof(predecessor),
        current,
        sizeof(current),
        successor,
        sizeof(successor),
        combined,
        sizeof(combined)
    ) == HHS_P174_OK);
    assert(memcmp(combined, predecessor, sizeof(predecessor)) == 0);
    assert(memcmp(combined + HHS_P174_HASH72_CHARACTERS, current, sizeof(current)) == 0);
    assert(memcmp(combined + HHS_P174_HASH72_CHARACTERS * 2U, successor, sizeof(successor)) == 0);

    for (i = 0U; i < HHS_P174_SHA256_BYTES; ++i) {
        logical_identity[i] = (uint8_t)i;
    }
    assert(hhs_p174_hash216_indexes(
        combined,
        sizeof(combined),
        logical_identity,
        indexes,
        index_root
    ) == HHS_P174_OK);
    assert(hhs_p174_hash216_indexes(
        combined,
        sizeof(combined),
        logical_identity,
        indexes_repeated,
        repeated_root
    ) == HHS_P174_OK);
    assert(!digest_is_zero(index_root));
    assert(memcmp(index_root, repeated_root, HHS_P174_SHA256_BYTES) == 0);
    assert(memcmp(indexes, indexes_repeated, sizeof(indexes)) == 0);
    assert(memcmp(indexes[0], indexes[1], HHS_P174_SHA256_BYTES) != 0);

    memcpy(changed, combined, sizeof(changed));
    changed[100] = changed[100] == 'Z' ? 'Y' : 'Z';
    assert(hhs_p174_hash216_indexes(
        changed,
        sizeof(changed),
        logical_identity,
        changed_indexes,
        changed_root
    ) == HHS_P174_OK);
    assert(memcmp(index_root, changed_root, HHS_P174_SHA256_BYTES) != 0);

    assert(hhs_p174_select_execution_path(UINT64_C(1000), UINT64_C(240), &path, &advantage) == HHS_P174_OK);
    assert(path == HHS_P174_EXECUTE_RETRIEVAL && advantage == INT64_C(760));
    assert(hhs_p174_select_execution_path(UINT64_C(100), UINT64_C(240), &path, &advantage) == HHS_P174_OK);
    assert(path == HHS_P174_EXECUTE_DIRECT && advantage == INT64_C(-140));
    assert(hhs_p174_select_execution_path(UINT64_C(100), UINT64_C(100), &path, &advantage) == HHS_P174_OK);
    assert(path == HHS_P174_EXECUTE_EQUAL_COST_DIRECT && advantage == INT64_C(0));

    puts("HHS_PASS_174_NATIVE_PHASE_HASH216_WHOLE_FRAME_ABI_VERIFIED");
    return 0;
}
