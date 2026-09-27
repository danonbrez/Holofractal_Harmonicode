#ifndef HHS_PASS220_PYTHON_RNA_CLASS_REGISTRATION_2_0_H
#define HHS_PASS220_PYTHON_RNA_CLASS_REGISTRATION_2_0_H

#include "hhs_pass219_rna_rule_grammar_1_11.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_MAJOR 2U
#define HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_MINOR 0U
#define HHS_EXACT_PASS220_PYTHON_RNA_CLASS_VERSION_PATCH 0U
#define HHS_EXACT_PASS220_PYTHON_RNA_CLASS_MAX_MEMBERS 7U
#define HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES 32U

typedef enum HHSExactPass220PythonRNAClassMemberKindV1 {
    HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CONSTRUCTOR = 1,
    HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_FIELD = 2,
    HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_METHOD = 3,
    HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_CLASS_METHOD = 4,
    HHS_EXACT_PASS220_PYTHON_RNA_MEMBER_STATIC_METHOD = 5
} HHSExactPass220PythonRNAClassMemberKindV1;

typedef struct HHSExactPass220PythonRNAClassMemberV1 {
    uint32_t member_id;
    uint32_t kind;
    uint32_t role_flags;
    uint8_t phase_basis;
    uint8_t orientation;
    uint8_t reserved0[2];
} HHSExactPass220PythonRNAClassMemberV1;

typedef struct HHSExactPass220PythonRNAClassDescriptorV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t module_id;
    uint32_t class_id;
    uint32_t constructor_member_id;
    uint32_t member_count;
    uint8_t source_sha256[HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES];
    char class_identity_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSExactPass220PythonRNAClassMemberV1
        members[HHS_EXACT_PASS220_PYTHON_RNA_CLASS_MAX_MEMBERS];
} HHSExactPass220PythonRNAClassDescriptorV1;

typedef struct HHSExactPass220PythonRNAClassRegistrationV1 {
    uint32_t struct_size;
    uint32_t version;
    uint32_t module_id;
    uint32_t class_id;
    uint32_t constructor_member_id;
    uint32_t member_count;
    uint64_t registration_fingerprint64;
    uint8_t source_sha256[HHS_EXACT_PASS220_PYTHON_RNA_CLASS_SHA256_BYTES];
    char class_identity_hash216[HHS_EXACT_UQCEL_HASH216_STRLEN];
    HHSExactPass219RNAStrandV1 strand;
    HHSExactPass219RNAProgramV1 program;
    HHSExactPass220PythonRNAClassMemberV1
        members[HHS_EXACT_PASS220_PYTHON_RNA_CLASS_MAX_MEMBERS];
    uint8_t rna_cell_wall_bound;
    uint8_t registration_only;
    uint8_t class_identity_bound;
    uint8_t source_identity_bound;
    uint8_t vm81_mutation_authority;
    uint8_t hash72_commit_authority;
    uint8_t hash216_persistence_authority;
    uint8_t floating_point_authority;
} HHSExactPass220PythonRNAClassRegistrationV1;

HHS_EXACT_API uint32_t hhs_exact_pass220_python_rna_class_version(void);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_python_rna_class_register(
    const HHSExactPass220PythonRNAClassDescriptorV1 *descriptor,
    HHSExactPass220PythonRNAClassRegistrationV1 *out_registration
);

HHS_EXACT_API HHSExactStatus hhs_exact_pass220_python_rna_class_validate_registration(
    const HHSExactPass220PythonRNAClassRegistrationV1 *registration
);

#ifdef __cplusplus
}
#endif

#endif
