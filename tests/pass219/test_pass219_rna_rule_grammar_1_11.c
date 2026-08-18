#include "hhs_pass219_rna_rule_grammar_1_11.h"

#include <assert.h>
#include <string.h>

static HHSExactPass219RNALineageV1 make_lineage(void) {
    HHSExactPass219RNALineageV1 lineage;
    memset(&lineage, 0, sizeof(lineage));
    lineage.struct_size = (uint32_t)sizeof(lineage);
    lineage.version = hhs_exact_pass219_rna_rule_version();
    assert(hhs_exact_pass219_native_phase_witness(
        HHS_EXACT_PHASE_X, HHS_EXACT_PHASE_Y, &lineage.native_phase) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_trinary_phase_gate(0U, &lineage.trinary_gate) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_coordinate_from_pass189(
        0U, 0, 1U, 0U, &lineage.coordinate) == HHS_EXACT_STATUS_OK);
    memset(lineage.predecessor_hash72, '0', HHS_EXACT_HASH72_LEN);
    lineage.predecessor_hash72[HHS_EXACT_HASH72_LEN] = '\0';
    memset(lineage.predecessor_hash216_identity, '1', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    lineage.predecessor_hash216_identity[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';
    return lineage;
}

static void add_rule(HHSExactPass219RNAProgramV1 *program,
                     uint32_t id, uint32_t kind,
                     uint32_t source, uint32_t target) {
    HHSExactPass219RNARuleV1 rule;
    assert(hhs_exact_pass219_rna_rule_init(id, kind, source, target, &rule) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_program_add_rule(program, &rule) == HHS_EXACT_STATUS_OK);
}

int main(void) {
    HHSExactPass219RNADomainV1 a;
    HHSExactPass219RNADomainV1 b;
    HHSExactPass219RNAStrandV1 strand;
    HHSExactPass219RNAProgramV1 program;
    HHSExactPass219TranscriptionWitnessV1 witness;
    HHSExactPass219RNADomainStateV1 rollback[HHS_EXACT_PASS219_RNA_MAX_DOMAINS];
    HHSExactPass219RNALineageV1 lineage = make_lineage();
    uint32_t rollback_count = 0U;

    assert(hhs_exact_pass219_rna_domain_init(
        10U, 20U, HHS_EXACT_PHASE_X, 0U,
        HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD, &a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_domain_init(
        20U, 10U, HHS_EXACT_PHASE_Y, 1U,
        HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN, &b) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_init(7U, &strand) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_add_domain(&strand, &a) == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass219_rna_strand_add_domain(&strand, &b) == HHS_EXACT_STATUS_OK);

    assert(hhs_exact_pass219_rna_program_init(99U, &program) == HHS_EXACT_STATUS_OK);
    add_rule(&program, 1U, HHS_EXACT_PASS219_RNA_RULE_COMPLEMENT, 10U, 20U);
    add_rule(&program, 2U, HHS_EXACT_PASS219_RNA_RULE_BINDING, 10U, 20U);
    add_rule(&program, 3U, HHS_EXACT_PASS219_RNA_RULE_TOEHOLD, 10U, 20U);
    add_rule(&program, 4U, HHS_EXACT_PASS219_RNA_RULE_ACTIVATION, 10U, 20U);
    add_rule(&program, 5U, HHS_EXACT_PASS219_RNA_RULE_CLEAVAGE, 10U, 20U);
    add_rule(&program, 6U, HHS_EXACT_PASS219_RNA_RULE_RELEASE, 10U, 20U);

    assert(hhs_exact_pass219_rna_program_execute(
        &strand, &program, &lineage, &witness) == HHS_EXACT_STATUS_OK);
    assert(witness.executed_rule_count == 6U);
    assert(witness.last_rule_id == 6U);
    assert(witness.rollback_available == 1U);
    assert((witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT) != 0U);
    assert((witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_CLEAVED) != 0U);
    assert((witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_RELEASED) != 0U);
    assert((witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_ACTIVE) == 0U);
    assert((witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_BOUND) == 0U);
    assert((witness.after[1].state_flags & HHS_EXACT_PASS219_RNA_STATE_BOUND) == 0U);
    assert(witness.lineage.native_phase.ordered_product.ordered_tag == lineage.native_phase.ordered_product.ordered_tag);

    assert(hhs_exact_pass219_rna_witness_rollback(
        &witness, rollback, &rollback_count) == HHS_EXACT_STATUS_OK);
    assert(rollback_count == 2U);
    assert(rollback[0].domain_id == 10U && rollback[0].state_flags == 0U);
    assert(rollback[1].domain_id == 20U && rollback[1].state_flags == 0U);

    {
        HHSExactPass219RNAProgramV1 hairpin;
        HHSExactPass219TranscriptionWitnessV1 hairpin_witness;
        assert(hhs_exact_pass219_rna_program_init(100U, &hairpin) == HHS_EXACT_STATUS_OK);
        add_rule(&hairpin, 7U, HHS_EXACT_PASS219_RNA_RULE_HAIRPIN, 20U, 10U);
        assert(hhs_exact_pass219_rna_program_execute(
            &strand, &hairpin, &lineage, &hairpin_witness) == HHS_EXACT_STATUS_OK);
        assert((hairpin_witness.after[1].state_flags & HHS_EXACT_PASS219_RNA_STATE_FOLDED) != 0U);
    }

    {
        HHSExactPass219RNAProgramV1 inhibited;
        HHSExactPass219TranscriptionWitnessV1 inhibited_witness;
        assert(hhs_exact_pass219_rna_program_init(101U, &inhibited) == HHS_EXACT_STATUS_OK);
        add_rule(&inhibited, 8U, HHS_EXACT_PASS219_RNA_RULE_INHIBITION, 10U, 20U);
        assert(hhs_exact_pass219_rna_program_execute(
            &strand, &inhibited, &lineage, &inhibited_witness) == HHS_EXACT_STATUS_OK);
        assert((inhibited_witness.after[0].state_flags & HHS_EXACT_PASS219_RNA_STATE_INHIBITED) != 0U);
    }

    {
        HHSExactPass219RNAProgramV1 invalid_binding;
        HHSExactPass219TranscriptionWitnessV1 rejected;
        assert(hhs_exact_pass219_rna_program_init(102U, &invalid_binding) == HHS_EXACT_STATUS_OK);
        add_rule(&invalid_binding, 9U, HHS_EXACT_PASS219_RNA_RULE_BINDING, 10U, 20U);
        assert(hhs_exact_pass219_rna_program_execute(
            &strand, &invalid_binding, &lineage, &rejected) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    }

    {
        HHSExactPass219RNAProgramV1 invalid_release;
        HHSExactPass219TranscriptionWitnessV1 rejected;
        assert(hhs_exact_pass219_rna_program_init(103U, &invalid_release) == HHS_EXACT_STATUS_OK);
        add_rule(&invalid_release, 10U, HHS_EXACT_PASS219_RNA_RULE_RELEASE, 10U, 20U);
        assert(hhs_exact_pass219_rna_program_execute(
            &strand, &invalid_release, &lineage, &rejected) == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);
    }

    return 0;
}
