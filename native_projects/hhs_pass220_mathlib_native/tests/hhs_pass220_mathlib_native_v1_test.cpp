#include "hhs_pass220_mathlib_native_v1.hpp"

#include <cassert>
#include <cstring>
#include <string_view>

int main() {
    using hhs::mathlib::NativeClassRegistration;
    using hhs::mathlib::NativeInt;
    using hhs::mathlib::NativeNat;

    NativeInt a("999999999999999999999999999999");
    NativeInt b("888888888888888888888888888888");
    assert(a.valid());
    assert(b.valid());

    const NativeInt sum = NativeInt::add(a, b);
    assert(sum.valid());
    assert(std::string_view(sum.decimal()) ==
           "1888888888888888888888888888887");

    const NativeInt product = NativeInt::mul(a, b);
    assert(product.valid());
    assert(std::string_view(product.decimal()) ==
           "888888888888888888888888888887111111111111111111111111111112");
    assert(!NativeInt::host_python_evaluator_used());

    NativeNat natural("72");
    NativeNat rejected("-1");
    assert(natural.valid());
    assert(!rejected.valid());
    const NativeNat squared = NativeNat::mul(natural, natural);
    assert(squared.valid());
    assert(std::string_view(squared.decimal()) == "5184");

    HHSExactPass220PythonRNAClassDescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<std::uint32_t>(sizeof(descriptor));
    descriptor.version = hhs_exact_pass220_python_rna_class_version();
    descriptor.module_id = 220048U;
    descriptor.class_id = 22004801U;
    descriptor.constructor_member_id = 22004811U;
    descriptor.member_count = 3U;

    for (std::uint32_t i = 0U;
         i < HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES;
         ++i) {
        descriptor.source_sha256[i] = static_cast<std::uint8_t>(i + 1U);
    }

    std::memset(
        descriptor.class_identity_hash216,
        'M',
        HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN);
    descriptor.class_identity_hash216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN] = '\0';

    descriptor.members[0].member_id = 22004811U;
    descriptor.members[0].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR;
    descriptor.members[0].phase_basis = HHS_EXACT_PHASE_X;
    descriptor.members[0].role_flags = HHS_EXACT_PASS219_RNA_ROLE_TOEHOLD;

    descriptor.members[1].member_id = 22004812U;
    descriptor.members[1].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_METHOD;
    descriptor.members[1].phase_basis = HHS_EXACT_PHASE_Y;
    descriptor.members[1].orientation = 1U;

    descriptor.members[2].member_id = 22004813U;
    descriptor.members[2].kind = HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_METHOD;
    descriptor.members[2].phase_basis = HHS_EXACT_PHASE_Z;
    descriptor.members[2].role_flags = HHS_EXACT_PASS219_RNA_ROLE_HAIRPIN;

    NativeClassRegistration registration(descriptor);
    assert(registration.status() == HHS_EXACT_STATUS_OK);
    assert(registration.registration_only());
    assert(!NativeClassRegistration::vm81_mutation_authority());
    assert(!NativeClassRegistration::hash72_commit_authority());
    assert(!NativeClassRegistration::hash216_persistence_authority());
    assert(!NativeClassRegistration::proof_kernel_authority());

    return 0;
}
