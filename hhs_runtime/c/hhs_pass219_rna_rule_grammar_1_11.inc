#include "../include/hhs_pass219_rna_rule_grammar_1_11.h"

#include <string.h>

static uint32_t hhs_exact_pass219_rna_rule_version_word(void) {
    return (HHS_EXACT_PASS219_RNA_RULE_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_RNA_RULE_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_RNA_RULE_VERSION_PATCH;
}

static int hhs_exact_pass219_rna_rule_kind_valid(uint32_t kind) {
    return kind >= HHS_EXACT_PASS219_RNA_RULE_COMPLEMENT &&
           kind <= HHS_EXACT_PASS219_RNA_RULE_RELEASE;
}

static int hhs_exact_pass219_rna_domain_valid(const HHSExactPass219RNADomainV1 *domain) {
    if (domain == NULL || domain->struct_size < sizeof(*domain) ||
        domain->version != hhs_exact_pass219_rna_rule_version_word())
        return 0;
    if (domain->phase_basis >= HHS_EXACT_PHASE_BASIS_COUNT)
        return 0;
    if ((domain->role_flags & ~(HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD |
                                HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN)) != 0U)
        return 0;
    return 1;
}

static int hhs_exact_pass219_rna_find_domain(
    const HHSExactPass219RNAStrandV1 *strand,
    uint32_t domain_id,
    uint32_t *out_index
) {
    uint32_t i;
    if (strand == NULL || out_index == NULL)
        return 0;
    for (i = 0U; i < strand->domain_count; ++i) {
        if (strand->domains[i].domain_id == domain_id) {
            *out_index = i;
            return 1;
        }
    }
    return 0;
}

static HHSExactStatus hhs_exact_pass219_rna_apply_rule(
    const HHSExactPass219RNAStrandV1 *strand,
    const HHSExactPass219RNARuleV1 *rule,
    HHSExactPass219RNADomainStateV1 states[HHS_EXACT_PASS219_RNA_MAX_DOMAINS]
) {
    uint32_t source_index;
    uint32_t target_index;
    HHSExactPass219RNADomainStateV1 *source;
    HHSExactPass219RNADomainStateV1 *target;
    const HHSExactPass219RNADomainV1 *source_domain;
    const HHSExactPass219RNADomainV1 *target_domain;

    if (!hhs_exact_pass219_rna_find_domain(strand, rule->source_domain_id, &source_index) ||
        !hhs_exact_pass219_rna_find_domain(strand, rule->target_domain_id, &target_index))
        return HHS_EXACT_STATUS_RANGE_ERROR;

    source = &states[source_index];
    target = &states[target_index];
    source_domain = &strand->domains[source_index];
    target_domain = &strand->domains[target_index];

    switch (rule->kind) {
        case HHS_EXACT_PASS219_RNA_RULE_COMPLEMENT:
            if (source_domain->complement_domain_id != target_domain->domain_id ||
                target_domain->complement_domain_id != source_domain->domain_id ||
                source_domain->orientation == target_domain->orientation)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT;
            target->state_flags |= HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_BINDING:
            if ((source->state_flags & HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT) == 0U ||
                (target->state_flags & HHS_EXACT_PASS219_RNA_STATE_COMPLEMENT) == 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_BOUND;
            target->state_flags |= HHS_EXACT_PASS219_RNA_STATE_BOUND;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_TOEHOLD:
            if ((source_domain->role_flags & HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD) == 0U ||
                (source->state_flags & HHS_EXACT_PASS219_RNA_STATE_BOUND) == 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_EXPOSED;
            target->state_flags |= HHS_EXACT_PASS219_RNA_STATE_EXPOSED;
            source->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_FOLDED;
            target->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_FOLDED;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_HAIRPIN:
            if ((source_domain->role_flags & HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN) == 0U ||
                (source->state_flags & HHS_EXACT_PASS219_RNA_STATE_EXPOSED) != 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_FOLDED;
            source->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_ACTIVE;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_ACTIVATION:
            if ((source->state_flags & HHS_EXACT_PASS219_RNA_STATE_BOUND) == 0U ||
                (source->state_flags & HHS_EXACT_PASS219_RNA_STATE_EXPOSED) == 0U ||
                (source->state_flags & HHS_EXACT_PASS219_RNA_STATE_CLEAVED) != 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_ACTIVE;
            source->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_INHIBITED;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_INHIBITION:
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_INHIBITED;
            source->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_ACTIVE;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_CLEAVAGE:
            if ((source->state_flags & (HHS_EXACT_PASS219_RNA_STATE_ACTIVE |
                                        HHS_EXACT_PASS219_RNA_STATE_INHIBITED)) == 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_CLEAVED;
            source->state_flags &= ~(HHS_EXACT_PASS219_RNA_STATE_ACTIVE |
                                     HHS_EXACT_PASS219_RNA_STATE_BOUND);
            target->state_flags &= ~HHS_EXACT_PASS219_RNA_STATE_BOUND;
            return HHS_EXACT_STATUS_OK;

        case HHS_EXACT_PASS219_RNA_RULE_RELEASE:
            if ((source->state_flags & HHS_EXACT_PASS219_RNA_STATE_CLEAVED) == 0U)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            source->state_flags |= HHS_EXACT_PASS219_RNA_STATE_RELEASED;
            source->state_flags &= ~(HHS_EXACT_PASS219_RNA_STATE_BOUND |
                                     HHS_EXACT_PASS219_RNA_STATE_FOLDED |
                                     HHS_EXACT_PASS219_RNA_STATE_EXPOSED);
            return HHS_EXACT_STATUS_OK;

        default:
            return HHS_EXACT_STATUS_RANGE_ERROR;
    }
}

uint32_t hhs_exact_pass219_rna_rule_version(void) {
    return hhs_exact_pass219_rna_rule_version_word();
}

HHSExactStatus hhs_exact_pass219_rna_domain_init(
    uint32_t domain_id,
    uint32_t complement_domain_id,
    uint8_t phase_basis,
    uint8_t orientation,
    uint32_t role_flags,
    HHSExactPass219RNADomainV1 *out_domain
) {
    if (out_domain == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (phase_basis >= HHS_EXACT_PHASE_BASIS_COUNT || orientation > 1U ||
        (role_flags & ~(HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD |
                        HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN)) != 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out_domain, 0, sizeof(*out_domain));
    out_domain->struct_size = (uint32_t)sizeof(*out_domain);
    out_domain->version = hhs_exact_pass219_rna_rule_version_word();
    out_domain->domain_id = domain_id;
    out_domain->complement_domain_id = complement_domain_id;
    out_domain->role_flags = role_flags;
    out_domain->phase_basis = phase_basis;
    out_domain->orientation = orientation;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_strand_init(
    uint32_t strand_id,
    HHSExactPass219RNAStrandV1 *out_strand
) {
    if (out_strand == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_strand, 0, sizeof(*out_strand));
    out_strand->struct_size = (uint32_t)sizeof(*out_strand);
    out_strand->version = hhs_exact_pass219_rna_rule_version_word();
    out_strand->strand_id = strand_id;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_strand_add_domain(
    HHSExactPass219RNAStrandV1 *strand,
    const HHSExactPass219RNADomainV1 *domain
) {
    uint32_t i;
    if (strand == NULL || !hhs_exact_pass219_rna_domain_valid(domain))
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (strand->struct_size < sizeof(*strand) ||
        strand->version != hhs_exact_pass219_rna_rule_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (strand->domain_count >= HHS_EXACT_PASS219_RNA_MAX_DOMAINS)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (i = 0U; i < strand->domain_count; ++i) {
        if (strand->domains[i].domain_id == domain->domain_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    strand->domains[strand->domain_count++] = *domain;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_rule_init(
    uint32_t rule_id,
    uint32_t kind,
    uint32_t source_domain_id,
    uint32_t target_domain_id,
    HHSExactPass219RNARuleV1 *out_rule
) {
    if (out_rule == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_exact_pass219_rna_rule_kind_valid(kind))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out_rule, 0, sizeof(*out_rule));
    out_rule->struct_size = (uint32_t)sizeof(*out_rule);
    out_rule->version = hhs_exact_pass219_rna_rule_version_word();
    out_rule->rule_id = rule_id;
    out_rule->kind = kind;
    out_rule->source_domain_id = source_domain_id;
    out_rule->target_domain_id = target_domain_id;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_program_init(
    uint32_t program_id,
    HHSExactPass219RNAProgramV1 *out_program
) {
    if (out_program == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    memset(out_program, 0, sizeof(*out_program));
    out_program->struct_size = (uint32_t)sizeof(*out_program);
    out_program->version = hhs_exact_pass219_rna_rule_version_word();
    out_program->program_id = program_id;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_program_add_rule(
    HHSExactPass219RNAProgramV1 *program,
    const HHSExactPass219RNARuleV1 *rule
) {
    uint32_t i;
    if (program == NULL || rule == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (program->struct_size < sizeof(*program) ||
        program->version != hhs_exact_pass219_rna_rule_version_word() ||
        rule->struct_size < sizeof(*rule) ||
        rule->version != hhs_exact_pass219_rna_rule_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (!hhs_exact_pass219_rna_rule_kind_valid(rule->kind))
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (program->rule_count >= HHS_EXACT_PASS219_RNA_MAX_RULES)
        return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    for (i = 0U; i < program->rule_count; ++i) {
        if (program->rules[i].rule_id == rule->rule_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    program->rules[program->rule_count++] = *rule;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_lineage_from_admission(
    const HHSExactPass219RNAAdmissionV1 *admission,
    HHSExactPass219RNALineageV1 *out_lineage
) {
    if (admission == NULL || out_lineage == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (admission->struct_size < sizeof(*admission))
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    memset(out_lineage, 0, sizeof(*out_lineage));
    out_lineage->struct_size = (uint32_t)sizeof(*out_lineage);
    out_lineage->version = hhs_exact_pass219_rna_rule_version_word();
    out_lineage->native_phase = admission->native_phase;
    out_lineage->trinary_gate = admission->trinary_gate;
    out_lineage->coordinate = admission->coordinate;
    memcpy(out_lineage->predecessor_hash72,
           admission->transition.previous_hash72,
           HHS_EXACT_HASH72_STRLEN);
    memcpy(out_lineage->predecessor_hash216_identity,
           admission->transition.transition_identity216,
           HHS_EXACT_UQCEL_HASH216_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_program_execute(
    const HHSExactPass219RNAStrandV1 *strand,
    const HHSExactPass219RNAProgramV1 *program,
    const HHSExactPass219RNALineageV1 *lineage,
    HHSExactPass219TranscriptionWitnessV1 *out_witness
) {
    uint32_t i;
    HHSExactStatus status;
    if (strand == NULL || program == NULL || lineage == NULL || out_witness == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (strand->struct_size < sizeof(*strand) ||
        strand->version != hhs_exact_pass219_rna_rule_version_word() ||
        program->struct_size < sizeof(*program) ||
        program->version != hhs_exact_pass219_rna_rule_version_word() ||
        lineage->struct_size < sizeof(*lineage) ||
        lineage->version != hhs_exact_pass219_rna_rule_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (strand->domain_count == 0U || strand->domain_count > HHS_EXACT_PASS219_RNA_MAX_DOMAINS ||
        program->rule_count > HHS_EXACT_PASS219_RNA_MAX_RULES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_witness, 0, sizeof(*out_witness));
    out_witness->struct_size = (uint32_t)sizeof(*out_witness);
    out_witness->version = hhs_exact_pass219_rna_rule_version_word();
    out_witness->strand_id = strand->strand_id;
    out_witness->program_id = program->program_id;
    out_witness->domain_count = strand->domain_count;
    out_witness->rollback_available = 1U;
    out_witness->lineage = *lineage;

    for (i = 0U; i < strand->domain_count; ++i) {
        if (!hhs_exact_pass219_rna_domain_valid(&strand->domains[i]))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        out_witness->before[i].domain_id = strand->domains[i].domain_id;
        out_witness->after[i].domain_id = strand->domains[i].domain_id;
    }

    for (i = 0U; i < program->rule_count; ++i) {
        status = hhs_exact_pass219_rna_apply_rule(strand, &program->rules[i], out_witness->after);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        out_witness->executed_rule_count = i + 1U;
        out_witness->last_rule_id = program->rules[i].rule_id;
    }
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_rna_witness_rollback(
    const HHSExactPass219TranscriptionWitnessV1 *witness,
    HHSExactPass219RNADomainStateV1 out_states[HHS_EXACT_PASS219_RNA_MAX_DOMAINS],
    uint32_t *out_domain_count
) {
    if (witness == NULL || out_states == NULL || out_domain_count == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (witness->struct_size < sizeof(*witness) ||
        witness->version != hhs_exact_pass219_rna_rule_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (witness->rollback_available != 1U ||
        witness->domain_count > HHS_EXACT_PASS219_RNA_MAX_DOMAINS)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(out_states, 0,
           sizeof(HHSExactPass219RNADomainStateV1) * HHS_EXACT_PASS219_RNA_MAX_DOMAINS);
    memcpy(out_states, witness->before,
           sizeof(HHSExactPass219RNADomainStateV1) * witness->domain_count);
    *out_domain_count = witness->domain_count;
    return HHS_EXACT_STATUS_OK;
}
