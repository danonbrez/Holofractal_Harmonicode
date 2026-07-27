#include "hhs_pass160_runtime.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned long long positive_total = 0u;
static unsigned long long negative_total = 0u;
static unsigned long long failures = 0u;
#define POS(x) do { if (x) positive_total++; else failures++; } while (0)
#define NEG(x) do { if (x) negative_total++; else failures++; } while (0)

static void make_hash(const char *domain, uint64_t value, HHSHash216 *out) {
    char buffer[128];
    (void)snprintf(buffer, sizeof(buffer), "%s:%llu", domain, (unsigned long long)value);
    hhs_hash216_compute(buffer, strlen(buffer), out);
}

static HHS160CertifiedOperation make_operation(void) {
    HHS160CertifiedOperation operation;
    memset(&operation, 0, sizeof(operation));
    operation.struct_size = (uint32_t)sizeof(operation);
    operation.struct_version = HHS160_STRUCT_VERSION;
    make_hash("operation", 1u, &operation.operation_id);
    make_hash("implementation", 1u, &operation.implementation_hash);
    make_hash("semantic", 1u, &operation.semantic_hash);
    make_hash("constraint", 1u, &operation.constraint_root);
    make_hash("runtime-semantic", 1u, &operation.runtime_semantic_root);
    make_hash("registry", 1u, &operation.registry_root);
    make_hash("p159-source", 1u, &operation.pass159_source_root);
    make_hash("p159-vmir", 1u, &operation.pass159_vmir_root);
    make_hash("p159-executable", 1u, &operation.pass159_executable_root);
    operation.maximum_steps = 4096u;
    operation.maximum_memory_bytes = UINT64_C(1) << 20u;
    operation.permitted_read_mask = 0x7fu;
    operation.permitted_write_mask = 0x18u;
    operation.deterministic = 1u;
    operation.reusable = 1u;
    operation.pass159_bound = 1u;
    return operation;
}

static HHS160ValidatedTransition make_transition(const HHS160CertifiedOperation *operation, uint64_t index, const HHSHash216 *parent_tip, const HHSHash216 *parent_state) {
    HHS160ValidatedTransition transition;
    memset(&transition, 0, sizeof(transition));
    transition.struct_size = (uint32_t)sizeof(transition);
    transition.struct_version = HHS160_STRUCT_VERSION;
    transition.transition_epoch = index + 1u;
    transition.operation_sequence = index;
    transition.maximum_reuse_count = 1000000000u;
    transition.original_validation_epoch = 1u;
    transition.parent_receipt_tip = *parent_tip;
    transition.parent_state_root = *parent_state;
    transition.operation_id = operation->operation_id;
    transition.operation_implementation_hash = operation->implementation_hash;
    transition.operation_semantic_hash = operation->semantic_hash;
    make_hash("input", index, &transition.canonical_input_hash);
    make_hash("delta", index, &transition.canonical_delta_hash);
    make_hash("state", index + 1u, &transition.resulting_state_root);
    make_hash("tip", index + 1u, &transition.resulting_receipt_tip);
    transition.constraint_root = operation->constraint_root;
    transition.runtime_semantic_root = operation->runtime_semantic_root;
    transition.operation_registry_root = operation->registry_root;
    make_hash("validation-receipt", index, &transition.validation_receipt_hash);
    make_hash("validator", 1u, &transition.validator_manifest_hash);
    transition.pass159_source_root = operation->pass159_source_root;
    transition.pass159_vmir_root = operation->pass159_vmir_root;
    transition.pass159_executable_root = operation->pass159_executable_root;
    make_hash("p159-equivalence", index, &transition.pass159_equivalence_receipt);
    transition.permitted_read_mask = operation->permitted_read_mask;
    transition.permitted_write_mask = operation->permitted_write_mask;
    transition.maximum_steps = 64u;
    transition.maximum_memory_bytes = 4096u;
    transition.input_schema_id = 1u;
    transition.delta_schema_id = 1u;
    transition.state_schema_id = 1u;
    transition.semantically_validated = 1u;
    transition.sealed = 1u;
    transition.external_effect_free = 1u;
    transition.pass159_bound = 1u;
    return transition;
}

static int outer_accept(const HHS160CommitCandidate *candidate, void *user_data) {
    (void)user_data;
    return candidate && candidate->verified;
}

int main(void) {
    HHS160Config config;
    HHS160Runtime *runtime = NULL;
    HHS160CertifiedOperation operation;
    HHS160ValidatedTransition transitions[16];
    HHS160SegmentCertificate left, right;
    HHS160HistoricalFrontier frontier, next;
    HHS160NestedRuntime *nested = NULL;
    HHS160CommitCandidate candidate;
    HHS160EffectProposal proposal;
    HHS160AuditEpoch *audit = NULL;
    HHS160CoverageCertificate coverage;
    HHS160Result result;
    HHSHash216 initial_tip, initial_state;
    uint8_t key[32];
    uint64_t index;
    size_t i;

    memset(&config, 0, sizeof(config));
    config.struct_size = (uint32_t)sizeof(config);
    config.struct_version = HHS160_STRUCT_VERSION;
    config.max_transitions = 128u;
    config.max_segments = 8u;
    config.max_nested_steps = 64u;
    POS(hhs160_runtime_create(&config, &runtime, &result) == HHS160_OK);
    operation = make_operation();
    POS(hhs160_register_operation(runtime, &operation, &result) == HHS160_OK);
    make_hash("tip", 0u, &initial_tip);
    make_hash("state", 0u, &initial_state);
    for (i = 0u; i < 16u; ++i) {
        const HHSHash216 *tip = i ? &transitions[i - 1u].resulting_receipt_tip : &initial_tip;
        const HHSHash216 *state = i ? &transitions[i - 1u].resulting_state_root : &initial_state;
        transitions[i] = make_transition(&operation, i, tip, state);
        POS(hhs160_transition_admit(runtime, &transitions[i], &index, &result) == HHS160_OK);
        POS(index == i);
        POS(hhs160_transition_verify_identity(&transitions[i], &result) == HHS160_OK);
    }
    POS(hhs160_segment_seal(runtime, 0u, 12u, 1u, 4u, &left, &result) == HHS160_OK);
    POS(hhs160_segment_seal(runtime, 8u, 8u, 4u, 1u, &right, &result) == HHS160_OK);
    POS(hhs160_segment_verify_overlap(&left, &right, &result) == HHS160_OK);
    POS(hhs160_frontier_seal(runtime, 7u, &initial_tip, &initial_state, &frontier, &result) == HHS160_OK);
    POS(hhs160_nested_begin(runtime, 81u, 16u, &nested, &result) == HHS160_OK);
    POS(hhs160_nested_capability_count(nested) == 0u);
    for (i = 0u; i < 8u; ++i) POS(hhs160_nested_reuse(nested, (uint64_t)i, 0u, &result) == HHS160_OK);
    POS(hhs160_nested_propose_effect(nested, 1u, "network-request", 15u, &proposal, &result) == HHS160_EXTERNAL_EFFECT_PROPOSAL_ONLY);
    POS(proposal.proposal_only && !proposal.executed && !proposal.externally_admitted);
    POS(hhs160_nested_finalize(nested, HHS160_COMMIT_PASS158, &candidate, &result) == HHS160_OK);
    POS(hhs160_commit_apply(runtime, &candidate, NULL, NULL, &next, &result) == HHS160_OUTER_ADMISSION_REQUIRED);
    POS(hhs160_commit_apply(runtime, &candidate, outer_accept, NULL, &next, &result) == HHS160_OK);
    for (i = 0u; i < sizeof(key); ++i) key[i] = (uint8_t)(i * 7u + 3u);
    POS(hhs160_audit_begin(runtime, 9u, 0u, key, &audit, &result) == HHS160_OK);
    POS(hhs160_audit_complete(audit, &coverage, &result) == HHS160_OK);
    POS(coverage.complete_permutation && coverage.every_index_visited_once && coverage.failed_count == 0u);
    for (i = 0u; i < 160u; ++i) {
        HHS160ValidatedTransition bad = transitions[i % 16u];
        bad.transition_integrity_sha256.bytes[i % 32u] ^= (uint8_t)(i + 1u);
        NEG(hhs160_transition_verify_identity(&bad, &result) == HHS160_INTEGRITY_MISMATCH);
    }
    hhs160_audit_destroy(audit);
    hhs160_nested_destroy(nested);
    hhs160_runtime_destroy(runtime);
    printf("{\"classification\":\"HHS_PASS_160_SANITIZER_AUTHORITY_PATHS_VERIFIED\",\"positive_total\":%llu,\"negative_total\":%llu,\"failures\":%llu}\n", positive_total, negative_total, failures);
    return failures ? EXIT_FAILURE : EXIT_SUCCESS;
}
