#include "hhs_pass220_python_rna_class_registration_2_0.hpp"

#include <cassert>
#include <cstring>

int main() {
    HHSExactPass220PythonRNAClassDescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<std::uint32_t>(sizeof(descriptor));
    descriptor.version = hhs_exact_pass220_python_rna_class_version();
    descriptor.module_id = 11U;
    descriptor.class_id = 22U;
    descriptor.constructor_member_id = 31U;
    descriptor.member_count = 2U;
    for (std::uint32_t i = 0U; i < HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES; ++i)
        descriptor.source_sha256[i] = static_cast<std::uint8_t>(i + 1U);
    std::memset(
        descriptor.class_identity_hash216,
        'R',
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    descriptor.class_identity_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    descriptor.members[0].member_id = 31U;
    descriptor.members[0].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR;
    descriptor.members[0].phase_basis = HHS_EXACT_PHASE_X;
    descriptor.members[0].orientation = 0U;
    descriptor.members[0].role_flags = HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD;

    descriptor.members[1].member_id = 32U;
    descriptor.members[1].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_METHOD;
    descriptor.members[1].phase_basis = HHS_EXACT_PHASE_W;
    descriptor.members[1].orientation = 1U;
    descriptor.members[1].role_flags = HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN;

    hhs::rna::PythonClassRegistration registration(descriptor);
    assert(registration.status() == HHS_EXACT_STATUS_OK);
    assert(registration.registration_only());
    assert(registration.strand().domain_count == 3U);
    assert(registration.registration_program().rule_count == 0U);
    assert(!hhs::rna::PythonClassRegistration::vm81_mutation_authority());
    assert(!hhs::rna::PythonClassRegistration::hash72_commit_authority());
    assert(!hhs::rna::PythonClassRegistration::hash216_persistence_authority());
    assert(!hhs::rna::PythonClassRegistration::floating_point_authority());
    assert(hhs::rna::PythonClassRegistration::instance_transition_requires_rna_admission());

    return 0;
}
