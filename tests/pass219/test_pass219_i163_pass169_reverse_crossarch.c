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
        !require(descriptor.hash72_reverse_state_api_used == 1U,
                 "Hash72 reverse API used") ||
        !require(descriptor.cross_architecture_receipt_identity_required == 1U,
                 "cross architecture identity required") ||
        !require(descriptor.python_native_parity_required == 1U,
                 "Python/native parity required") ||
        !require(descriptor.i162_parent_immutable == 1U,
                 "I162 parent immutable") ||
        !require(descriptor.floating_point_authority == 0U,
                 "no floating point authority") ||
        !require(descriptor.pass169_terminal_contract_claimed == 0U,
                 "no terminal overclaim"))
        return 1;

    memset(&execution, 0, sizeof(execution));
    status = hhs_exact_pass219_i163_verify_reverse(
        source, source_size, &execution);
    if (status != HHS_EXACT_STATUS_OK) {
        fprintf(stderr,
                "I163 reverse status=%d decision=%u reason=%u forward=%u reverse=%u restored=%u compare=%u ring=%u repeat=%u\n",
                (int)status,
                execution.decision,
                execution.reason,
                execution.forward_commit_verified,
                execution.reverse_runtime_verified,
                execution.reverse_restored_prior_semantic_root,
                execution.interpreter_compiler_match,
                execution.hash72_ring_restored_prior_state,
                execution.deterministic_repeat_verified);
        fprintf(stderr, "forward_root=%s\nprior_root=%s\nreverse_root=%s\n",
                execution.forward_semantic_root_hash216,
                execution.prior_semantic_root_hash216,
                execution.reverse_semantic_root_hash216);
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
        !require(execution.reverse_restored_prior_semantic_root == 1U,
                 "reverse restored prior semantic root") ||
        !require(execution.interpreter_compiler_match == 1U,
                 "interpreter compiler match") ||
        !require(execution.hash72_ring_reverse_verified == 1U &&
                 execution.hash72_ring_restored_prior_state == 1U,
                 "Hash72 ring reverse restored prior state") ||
        !require(execution.deterministic_repeat_verified == 1U,
                 "deterministic repeat verified") ||
        !require(execution.forward_receipt_hash72_valid == 1U &&
                 execution.reverse_receipt_hash72_valid == 1U &&
                 execution.forward_receipt_hash216_valid == 1U &&
                 execution.reverse_receipt_hash216_valid == 1U,
                 "receipt identities valid") ||
        !require(execution.pass169_terminal_contract_claimed == 0U,
                 "terminal remains unclaimed"))
        return 1;

    printf("PASS219 I163 Pass169 reverse runtime: PASS\n");
    return 0;
}
