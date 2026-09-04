#include "hhs_pass219_i163_pass169_reverse_crossarch_1_24.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int require(int condition, const char *message) {
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        return 0;
    }
    return 1;
}

static int read_source(const char *path, uint8_t *out, size_t capacity, size_t *out_size) {
    FILE *file;
    long length;
    size_t size;
    if (path == NULL || out == NULL || out_size == NULL)
        return 0;
    file = fopen(path, "rb");
    if (file == NULL)
        return 0;
    if (fseek(file, 0L, SEEK_END) != 0) {
        fclose(file);
        return 0;
    }
    length = ftell(file);
    if (length < 0L || (unsigned long)length > (unsigned long)capacity ||
        fseek(file, 0L, SEEK_SET) != 0) {
        fclose(file);
        return 0;
    }
    size = fread(out, 1U, (size_t)length, file);
    fclose(file);
    if (size != (size_t)length)
        return 0;
    *out_size = size;
    return 1;
}

int main(int argc, char **argv) {
    static const char EXPECTED_VM81_RECEIPT[HHS_EXACT_PASS219_I163_HASH72_STRLEN] =
        "i91e<BXYyem<yft9yU>pPRowX-aIvY*2esocIG8LVXN6A0TrNm3ttdkrpD4oCN?bS1ID!QoJ";
    static const char EXPECTED_VM81_HASH216[HHS_EXACT_PASS219_I163_HASH216_STRLEN] =
        "xhfHT5FB/MI5rH*yinth2RcAO1zArnsidZHvZXT6yW3IV!?874xAJdm27yhJa3>yEOt+BMAPV-jCe*8!e41n1piMHtVFwX+SvcErOdWFC<*i/DOv?VO//UlYS<>oJT1Ou>//9S/KRYYUF6AuB6B3xsCfcWb(TUolnSU20VK9fYSDQFVzYco8h/xD)PKQ+!/W>bv(azKhx+S9OwtIuCk-1y18";
    uint8_t source[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES];
    size_t source_size = 0U;
    HHSExactPass219I163DescriptorV1 descriptor;
    HHSExactPass219I163ReverseExecutionV1 execution;
    HHSExactStatus status;

    if (argc != 2) {
        fprintf(stderr, "usage: %s <combined-source>\n", argv[0]);
        return 2;
    }
    if (!read_source(argv[1], source, sizeof(source), &source_size) ||
        !require(source_size == sizeof(source), "exact 632-byte source"))
        return 1;

    memset(&descriptor, 0, sizeof(descriptor));
    status = hhs_exact_pass219_i163_descriptor(&descriptor);
    if (!require(status == HHS_EXACT_STATUS_OK, "descriptor") ||
        !require(descriptor.pass169_reverse_runtime_required == 1U,
                 "reverse runtime required") ||
        !require(descriptor.pass159_reverse_api_used == 1U,
                 "Pass159 reverse API used") ||
        !require(descriptor.pass159_reverse_is_transition_receipt == 1U,
                 "Pass159 reverse classified as transition receipt") ||
        !require(descriptor.hash72_reverse_state_api_used == 1U,
                 "Hash72 reverse API used") ||
        !require(descriptor.vm81_transaction_snapshot_restore_required == 1U,
                 "VM81 transaction snapshot restore required") ||
        !require(descriptor.prior_committed_state_restoration_required == 1U,
                 "prior committed state restoration required") ||
        !require(descriptor.cross_architecture_receipt_identity_required == 1U,
                 "cross architecture identity required") ||
        !require(descriptor.python_native_parity_required == 1U,
                 "Python/native parity required") ||
        !require(descriptor.i162_parent_immutable == 1U,
                 "I162 parent immutable") ||
        !require(descriptor.floating_point_authority == 0U,
                 "no floating point authority") ||
        !require(descriptor.canonical_mutation_authority == 0U,
                 "no persistent canonical mutation authority") ||
        !require(descriptor.hash216_persistence_authority == 0U,
                 "no Hash216 persistence authority") ||
        !require(descriptor.pass169_terminal_contract_claimed == 0U,
                 "no terminal overclaim"))
        return 1;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass219_i163_verify_reverse(
        source, source_size, &execution);
    if (status != HHS_EXACT_STATUS_OK) {
        fprintf(stderr,
                "I163 reverse status=%d decision=%u reason=%u forward=%u reverse=%u transition=%u transition_det=%u vm81_restore=%u prior_restored=%u compare=%u ring=%u repeat=%u\n",
                (int)status,
                execution.decision,
                execution.reason,
                execution.forward_commit_verified,
                execution.reverse_runtime_verified,
                execution.reverse_transition_receipt_verified,
                execution.reverse_transition_deterministic,
                execution.vm81_snapshot_reverse_verified,
                execution.prior_committed_state_restored,
                execution.interpreter_compiler_match,
                execution.hash72_ring_restored_prior_state,
                execution.deterministic_repeat_verified);
        fprintf(stderr,
                "forward_root=%s\nreverse_root=%s\nvm81_receipt=%s\nvm81_hash216=%s\n",
                execution.forward_semantic_root_hash216,
                execution.reverse_semantic_root_hash216,
                execution.vm81_receipt_hash72,
                execution.vm81_hash216_identity);
        return 1;
    }

    if (!require(execution.decision == HHS_EXACT_PASS219_I163_VERIFIED,
                 "reverse decision verified") ||
        !require(execution.source_provenance_exact == 1U,
                 "source provenance exact") ||
        !require(execution.forward_commit_verified == 1U,
                 "forward commit verified") ||
        !require(execution.reverse_runtime_verified == 1U,
                 "reverse runtime verified") ||
        !require(execution.reverse_transition_receipt_verified == 1U,
                 "reverse transition receipt verified") ||
        !require(execution.reverse_transition_deterministic == 1U,
                 "reverse transition deterministic") ||
        !require(execution.vm81_snapshot_reverse_verified == 1U,
                 "VM81 transactional reverse verified") ||
        !require(execution.prior_committed_state_restored == 1U,
                 "prior committed transaction state restored") ||
        !require(execution.vm5184_address == 1U,
                 "VM5184 address preserved") ||
        !require(strcmp(execution.vm81_receipt_hash72, EXPECTED_VM81_RECEIPT) == 0,
                 "VM81 receipt identity preserved") ||
        !require(strcmp(execution.vm81_hash216_identity, EXPECTED_VM81_HASH216) == 0,
                 "VM81 Hash216 identity preserved") ||
        !require(execution.interpreter_compiler_match == 1U,
                 "interpreter compiler match") ||
        !require(execution.hash72_ring_reverse_verified == 1U &&
                 execution.hash72_ring_restored_prior_state == 1U,
                 "Hash72 ring reverse restored prior state") ||
        !require(execution.deterministic_repeat_verified == 1U,
                 "deterministic forward repeat verified") ||
        !require(execution.forward_receipt_hash72_valid == 1U &&
                 execution.reverse_receipt_hash72_valid == 1U &&
                 execution.forward_receipt_hash216_valid == 1U &&
                 execution.reverse_receipt_hash216_valid == 1U,
                 "Pass159 receipt identities valid") ||
        !require(strcmp(execution.forward_semantic_root_hash216,
                        execution.reverse_semantic_root_hash216) != 0,
                 "reverse transition root distinct from forward root") ||
        !require(execution.floating_point_authority == 0U &&
                 execution.canonical_mutation_authority == 0U &&
                 execution.hash216_persistence_authority == 0U,
                 "no authority escalation") ||
        !require(execution.pass169_terminal_contract_claimed == 0U,
                 "terminal remains unclaimed"))
        return 1;

    printf("PASS219 I163 Pass169 reverse runtime: PASS\n");
    return 0;
}
