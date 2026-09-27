#include "../include/hhs_pass220_python_rna_class_registration_2_0.h"

#include <string.h>

static uint32_t hhs_exact_pass220_python_rna_class_version_word(void) {
    return (HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_MINOR << 8) |
           HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_PATCH;
}

static int hhs_pass220_python_rna_member_kind_valid(uint32_t kind) {
    return kind >= HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR &&
           kind <= HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_STATIC_METHOD;
}

static int hhs_pass220_python_rna_hash216_nonempty(
    const char value[HHS_EXACT_UQCEL_HASH216_STRLEN]
) {
    uint32_t i;
    if (value[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        unsigned char c = (unsigned char)value[i];
        if (c < 33U || c > 126U)
            return 0;
    }
    return 1;
}

static int hhs_pass220_python_rna_sha256_nonzero(
    const uint8_t value[HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES]
) {
    uint32_t i;
    uint8_t acc = 0U;
    for (i = 0U; i < HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES; ++i)
        acc = (uint8_t)(acc | value[i]);
    return acc != 0U;
}

static uint64_t hhs_pass220_python_rna_mix64(uint64_t h, uint64_t value) {
    uint32_t i;
    for (i = 0U; i < 8U; ++i) {
        h ^= (value >> (i * 8U)) & UINT64_C(0xff);
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static uint64_t hhs_pass220_python_rna_fingerprint(
    const HHSExactPass220PythonRNAClassDescriptorV1 *descriptor
) {
    uint64_t h = UINT64_C(14695981039346656037);
    uint32_t i;
    h = hhs_pass220_python_rna_mix64(h, descriptor->module_id);
    h = hhs_pass220_python_rna_mix64(h, descriptor->class_id);
    h = hhs_pass220_python_rna_mix64(h, descriptor->constructor_member_id);
    h = hhs_pass220_python_rna_mix64(h, descriptor->member_count);
    for (i = 0U; i < HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES; ++i) {
        h ^= descriptor->source_sha256[i];
        h *= UINT64_C(1099511628211);
    }
    for (i = 0U; i < HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN; ++i) {
        h ^= (uint8_t)descriptor->class_identity_hash216[i];
        h *= UINT64_C(1099511628211);
    }
    for (i = 0U; i < descriptor->member_count; ++i) {
        const HHSExactPass220PythonRNAClassMemberV1 *member = &descriptor->members[i];
        h = hhs_pass220_python_rna_mix64(h, member->member_id);
        h = hhs_pass220_python_rna_mix64(h, member->kind);
        h = hhs_pass220_python_rna_mix64(h, member->role_flags);
        h = hhs_pass220_python_rna_mix64(h, member->phase_basis);
        h = hhs_pass220_python_rna_mix64(h, member->orientation);
    }
    return h;
}

static HHSExactStatus hhs_pass220_python_rna_descriptor_validate(
    const HHSExactPass220PythonRNAClassDescriptorV1 *descriptor
) {
    uint32_t i;
    uint32_t constructor_count = 0U;
    if (descriptor == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (descriptor->struct_size < sizeof(*descriptor) ||
        descriptor->version != hhs_exact_pass220_python_rna_class_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (descriptor->module_id == 0U || descriptor->class_id == 0U ||
        descriptor->constructor_member_id == 0U)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (descriptor->member_count == 0U ||
        descriptor->member_count > HHS_EXACT_PASS220_PYTHON_RNA_CLASS_MAX_MEMBERS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_pass220_python_rna_hash216_nonempty(descriptor->class_identity_hash216) ||
        !hhs_pass220_python_rna_sha256_nonzero(descriptor->source_sha256))
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;

    for (i = 0U; i < descriptor->member_count; ++i) {
        const HHSExactPass220PythonRNAClassMemberV1 *member = &descriptor->members[i];
        uint32_t j;
        if (member->member_id == 0U || member->member_id == descriptor->class_id ||
            !hhs_pass220_python_rna_member_kind_valid(member->kind) ||
            member->phase_basis >= HHS_EXACT_PHASE_BASIS_COUNT ||
            member->orientation > 1U ||
            (member->role_flags & ~(HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD |
                                    HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN)) != 0U)
            return HHS_EXACT_STATUS_RANGE_ERROR;
        for (j = 0U; j < i; ++j) {
            if (descriptor->members[j].member_id == member->member_id)
                return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        }
        if (member->kind == HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR) {
            if (member->member_id != descriptor->constructor_member_id)
                return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
            ++constructor_count;
        }
    }
    return constructor_count == 1U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
}

uint32_t hhs_exact_pass220_python_rna_class_version(void) {
    return hhs_exact_pass220_python_rna_class_version_word();
}

HHSExactStatus hhs_exact_pass220_python_rna_class_register(
    const HHSExactPass220PythonRNAClassDescriptorV1 *descriptor,
    HHSExactPass220PythonRNAClassRegistrationV1 *out_registration
) {
    HHSExactStatus status;
    HHSExactPass219RNADomainV1 domain;
    uint32_t i;

    if (out_registration == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_pass220_python_rna_descriptor_validate(descriptor);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    memset(out_registration, 0, sizeof(*out_registration));
    out_registration->struct_size = (uint32_t)sizeof(*out_registration);
    out_registration->version = hhs_exact_pass220_python_rna_class_version_word();
    out_registration->module_id = descriptor->module_id;
    out_registration->class_id = descriptor->class_id;
    out_registration->constructor_member_id = descriptor->constructor_member_id;
    out_registration->member_count = descriptor->member_count;
    out_registration->registration_fingerprint64 =
        hhs_pass220_python_rna_fingerprint(descriptor);
    memcpy(out_registration->source_sha256,
           descriptor->source_sha256,
           sizeof(out_registration->source_sha256));
    memcpy(out_registration->class_identity_hash216,
           descriptor->class_identity_hash216,
           sizeof(out_registration->class_identity_hash216));
    memcpy(out_registration->members,
           descriptor->members,
           sizeof(HHSExactPass220PythonRNAClassMemberV1) * descriptor->member_count);

    status = hhs_exact_pass219_rna_strand_init(
        descriptor->class_id,
        &out_registration->strand);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    status = hhs_exact_pass219_rna_domain_init(
        descriptor->class_id,
        descriptor->class_id,
        HHS_EXACT_PHASE_X,
        0U,
        HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD,
        &domain);
    if (status != HHS_EXACT_STATUS_OK)
        return status;
    status = hhs_exact_pass219_rna_strand_add_domain(
        &out_registration->strand,
        &domain);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    for (i = 0U; i < descriptor->member_count; ++i) {
        const HHSExactPass220PythonRNAClassMemberV1 *member = &descriptor->members[i];
        status = hhs_exact_pass219_rna_domain_init(
            member->member_id,
            member->member_id,
            member->phase_basis,
            member->orientation,
            member->role_flags,
            &domain);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
        status = hhs_exact_pass219_rna_strand_add_domain(
            &out_registration->strand,
            &domain);
        if (status != HHS_EXACT_STATUS_OK)
            return status;
    }

    status = hhs_exact_pass219_rna_program_init(
        descriptor->class_id ^ UINT32_C(0x50593200),
        &out_registration->program);
    if (status != HHS_EXACT_STATUS_OK)
        return status;

    out_registration->rna_cell_wall_bound = 1U;
    out_registration->registration_only = 1U;
    out_registration->class_identity_bound = 1U;
    out_registration->source_identity_bound = 1U;
    out_registration->vm81_mutation_authority = 0U;
    out_registration->hash72_commit_authority = 0U;
    out_registration->hash216_persistence_authority = 0U;
    out_registration->floating_point_authority = 0U;

    return hhs_exact_pass220_python_rna_class_validate_registration(
        out_registration);
}

HHSExactStatus hhs_exact_pass220_python_rna_class_validate_registration(
    const HHSExactPass220PythonRNAClassRegistrationV1 *registration
) {
    uint32_t i;
    if (registration == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (registration->struct_size < sizeof(*registration) ||
        registration->version != hhs_exact_pass220_python_rna_class_version_word())
        return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (registration->module_id == 0U || registration->class_id == 0U ||
        registration->constructor_member_id == 0U ||
        registration->member_count == 0U ||
        registration->member_count > HHS_EXACT_PASS220_PYTHON_RNA_CLASS_MAX_MEMBERS)
        return HHS_EXACT_STATUS_RANGE_ERROR;
    if (registration->strand.struct_size < sizeof(registration->strand) ||
        registration->strand.version != hhs_exact_pass219_rna_rule_version() ||
        registration->strand.strand_id != registration->class_id ||
        registration->strand.domain_count != registration->member_count + 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (registration->program.struct_size < sizeof(registration->program) ||
        registration->program.version != hhs_exact_pass219_rna_rule_version() ||
        registration->program.rule_count != 0U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_pass220_python_rna_hash216_nonempty(registration->class_identity_hash216) ||
        !hhs_pass220_python_rna_sha256_nonzero(registration->source_sha256))
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;
    if (registration->rna_cell_wall_bound != 1U ||
        registration->registration_only != 1U ||
        registration->class_identity_bound != 1U ||
        registration->source_identity_bound != 1U ||
        registration->vm81_mutation_authority != 0U ||
        registration->hash72_commit_authority != 0U ||
        registration->hash216_persistence_authority != 0U ||
        registration->floating_point_authority != 0U)
        return HHS_EXACT_STATUS_CONSTRAINT_REJECTED;

    if (registration->strand.domains[0].domain_id != registration->class_id)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    for (i = 0U; i < registration->member_count; ++i) {
        if (registration->strand.domains[i + 1U].domain_id !=
            registration->members[i].member_id)
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }
    return registration->registration_fingerprint64 != 0U
        ? HHS_EXACT_STATUS_OK
        : HHS_EXACT_STATUS_INVARIANT_FAILURE;
}
