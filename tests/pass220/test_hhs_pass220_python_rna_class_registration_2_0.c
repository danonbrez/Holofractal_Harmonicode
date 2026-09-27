#include "hhs_pass220_python_rna_class_registration_2_0.h"

#include <assert.h>
#include <string.h>

static HHSExactPass220PythonRNAClassDescriptorV1 descriptor(void) {
    HHSExactPass220PythonRNAClassDescriptorV1 value;
    uint32_t i;
    memset(&value, 0, sizeof(value));
    value.struct_size = (uint32_t)sizeof(value);
    value.version = hhs_exact_pass220_python_rna_class_version();
    value.module_id = 101U;
    value.class_id = 202U;
    value.constructor_member_id = 301U;
    value.member_count = 3U;
    for (i = 0U; i < HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES; ++i)
        value.source_sha256[i] = (uint8_t)(i + 1U);
    memset(value.class_identity_hash216, 'H', HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    value.class_identity_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    value.members[0].member_id = 301U;
    value.members[0].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR;
    value.members[0].phase_basis = HHS_EXACT_PHASE_X;
    value.members[0].orientation = 0U;
    value.members[0].role_flags = HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD;

    value.members[1].member_id = 302U;
    value.members[1].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_FIELD;
    value.members[1].phase_basis = HHS_EXACT_PHASE_Y;
    value.members[1].orientation = 1U;
    value.members[1].role_flags = 0U;

    value.members[2].member_id = 303U;
    value.members[2].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_METHOD;
    value.members[2].phase_basis = HHS_EXACT_PHASE_Z;
    value.members[2].orientation = 0U;
    value.members[2].role_flags = HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN;
    return value;
}

int main(void) {
    HHSExactPass220PythonRNAClassDescriptorV1 input = descriptor();
    HHSExactPass220PythonRNAClassRegistrationV1 registration;
    HHSExactPass220PythonRNAClassRegistrationV1 replay;
    HHSExactStatus status;

    assert(hhs_exact_pass220_python_rna_class_version() == UINT32_C(0x00020000));

    status = hhs_exact_pass220_python_rna_class_register(&input, &registration);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(hhs_exact_pass220_python_rna_class_validate_registration(&registration)
           == HHS_EXACT_STATUS_OK);

    assert(registration.module_id == 101U);
    assert(registration.class_id == 202U);
    assert(registration.constructor_member_id == 301U);
    assert(registration.member_count == 3U);
    assert(registration.strand.strand_id == 202U);
    assert(registration.strand.domain_count == 4U);
    assert(registration.strand.domains[0].domain_id == 202U);
    assert(registration.strand.domains[1].domain_id == 301U);
    assert(registration.strand.domains[2].domain_id == 302U);
    assert(registration.strand.domains[3].domain_id == 303U);
    assert(registration.program.rule_count == 0U);
    assert(registration.rna_cell_wall_bound == 1U);
    assert(registration.registration_only == 1U);
    assert(registration.vm81_mutation_authority == 0U);
    assert(registration.hash72_commit_authority == 0U);
    assert(registration.hash216_persistence_authority == 0U);
    assert(registration.floating_point_authority == 0U);
    assert(registration.registration_fingerprint64 != 0U);

    status = hhs_exact_pass220_python_rna_class_register(&input, &replay);
    assert(status == HHS_EXACT_STATUS_OK);
    assert(replay.registration_fingerprint64 == registration.registration_fingerprint64);
    assert(memcmp(&replay.strand, &registration.strand, sizeof(registration.strand)) == 0);
    assert(memcmp(&replay.program, &registration.program, sizeof(registration.program)) == 0);

    input.members[2].member_id = 302U;
    assert(hhs_exact_pass220_python_rna_class_register(&input, &replay)
           == HHS_EXACT_STATUS_INVARIANT_FAILURE);

    input = descriptor();
    input.members[1].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR;
    assert(hhs_exact_pass220_python_rna_class_register(&input, &replay)
           == HHS_EXACT_STATUS_CONSTRAINT_REJECTED);

    return 0;
}
