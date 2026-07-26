#ifndef HHS_LSHPVS_H
#define HHS_LSHPVS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_LSHPVS_ABI_VERSION 1U
#define HHS_LSHPVS_MAX_ENTRIES 64U
#define HHS_LSHPVS_MAX_FOLD_PATH 192U
#define HHS_LSHPVS_HASH72_STRLEN 73U
#define HHS_LSHPVS_HASH216_STRLEN 217U

#define HHS_LSHPVS_STATUS_LOCAL_VERIFIED \
    "HHS_PASS_156_1_LOCAL_CORE_VERIFIED"
#define HHS_LSHPVS_STATUS_INHERITED_BLOCKED \
    "HHS_PASS_156_1_INCOMPLETE"

typedef enum HHSLshpvsStatus {
    HHS_LSHPVS_OK = 0,
    HHS_LSHPVS_INVALID_ARGUMENT = 1,
    HHS_LSHPVS_DIVIDE_BY_ZERO = 2,
    HHS_LSHPVS_OVERFLOW = 3,
    HHS_LSHPVS_NON_HERMITIAN = 4,
    HHS_LSHPVS_SINGULAR_PROPAGATOR = 5,
    HHS_LSHPVS_NORM_MISMATCH = 6,
    HHS_LSHPVS_ROTATION_RECONSTRUCTION_MISMATCH = 7,
    HHS_LSHPVS_VM81_REJECTED = 8,
    HHS_LSHPVS_STORE_FULL = 9,
    HHS_LSHPVS_VERSION_CONFLICT = 10,
    HHS_LSHPVS_NOT_FOUND = 11,
    HHS_LSHPVS_SERIALIZATION_BOUNDED = 12,
    HHS_LSHPVS_BATCH_REJECTED = 13,
    HHS_LSHPVS_REPLAY_MISMATCH = 14
} HHSLshpvsStatus;

typedef struct HHSLshpvsRational {
    int64_t num;
    int64_t den;
} HHSLshpvsRational;

typedef struct HHSLshpvsComplex {
    HHSLshpvsRational re;
    HHSLshpvsRational im;
} HHSLshpvsComplex;

typedef struct HHSLshpvsMatrix2 {
    HHSLshpvsComplex cell[2][2];
} HHSLshpvsMatrix2;

typedef struct HHSLshpvsVector2 {
    HHSLshpvsComplex cell[2];
} HHSLshpvsVector2;

typedef struct HHSLshpvsRotationIndex {
    char contract_root_hash216[HHS_LSHPVS_HASH216_STRLEN];
    char fold_path[HHS_LSHPVS_MAX_FOLD_PATH];
    uint32_t nesting_depth;
    int64_t modulus_M;
    int64_t full_rotation_n;
    int64_t overflow_quotient_q;
    int64_t local_residue_r;
    char winding_operator_id[HHS_LSHPVS_HASH216_STRLEN];
    int32_t orientation_sector;
    uint64_t version;
} HHSLshpvsRotationIndex;

typedef struct HHSLshpvsParameterVector {
    HHSLshpvsRational h00;
    HHSLshpvsComplex h01;
    HHSLshpvsRational h11;
    HHSLshpvsRational delta_tau;
    HHSLshpvsRational hbar;
    int64_t P;
    int64_t s;
    int64_t f;
    int64_t A;
    int64_t B;
    int64_t pq;
    int64_t Delta;
    int64_t xy;
    int64_t yx;
    uint32_t bound_mask;
} HHSLshpvsParameterVector;

typedef struct HHSLshpvsEntry {
    char key_hash216[HHS_LSHPVS_HASH216_STRLEN];
    char parent_key_hash216[HHS_LSHPVS_HASH216_STRLEN];
    HHSLshpvsRotationIndex index;
    HHSLshpvsParameterVector parameters;
    HHSLshpvsMatrix2 hamiltonian;
    HHSLshpvsVector2 pre_state;
    HHSLshpvsVector2 post_state;
    HHSLshpvsMatrix2 propagator;
    HHSLshpvsMatrix2 winding;
    HHSLshpvsMatrix2 reconstructed_rotation;
    char source_expression_root_hash216[HHS_LSHPVS_HASH216_STRLEN];
    char membrane_root_hash216[HHS_LSHPVS_HASH216_STRLEN];
    char hash72_head[HHS_LSHPVS_HASH72_STRLEN];
    char state_hash216[HHS_LSHPVS_HASH216_STRLEN];
    uint64_t committed_sequence;
    uint8_t hermitian_verified;
    uint8_t norm_verified;
    uint8_t rotation_reconstruction_verified;
    uint8_t vm81_admitted;
    uint8_t committed;
} HHSLshpvsEntry;

typedef struct HHSLshpvsStore {
    HHSLshpvsEntry entries[HHS_LSHPVS_MAX_ENTRIES];
    size_t count;
    uint64_t next_sequence;
    char chain_hash216[HHS_LSHPVS_HASH216_STRLEN];
} HHSLshpvsStore;

typedef struct HHSLshpvsTransitionPackage {
    char package_hash216[HHS_LSHPVS_HASH216_STRLEN];
    char constructor_id[64];
    uint64_t expected_version;
    HHSLshpvsEntry candidate;
    uint8_t vm81_authority_admission;
} HHSLshpvsTransitionPackage;

HHSLshpvsStatus hhs_lshpvs_rational_make(int64_t num, int64_t den, HHSLshpvsRational *out);
HHSLshpvsStatus hhs_lshpvs_rotation_decompose(int64_t n, int64_t M, int64_t *q, int64_t *r);
HHSLshpvsStatus hhs_lshpvs_entry_prepare(HHSLshpvsEntry *entry);
HHSLshpvsStatus hhs_lshpvs_entry_execute(HHSLshpvsEntry *entry);
HHSLshpvsStatus hhs_lshpvs_entry_admit_vm81(HHSLshpvsEntry *entry, void *runtime_state);
void hhs_lshpvs_store_init(HHSLshpvsStore *store);
HHSLshpvsStatus hhs_lshpvs_store_commit(HHSLshpvsStore *store, const HHSLshpvsTransitionPackage *package);
HHSLshpvsStatus hhs_lshpvs_store_commit_batch(HHSLshpvsStore *store, const HHSLshpvsTransitionPackage *packages, size_t package_count);
const HHSLshpvsEntry *hhs_lshpvs_store_find_key(const HHSLshpvsStore *store, const char *key_hash216);
const HHSLshpvsEntry *hhs_lshpvs_store_find_index(const HHSLshpvsStore *store, const char *fold_path, int64_t M, int64_t n, uint64_t version);
HHSLshpvsStatus hhs_lshpvs_entry_serialize_json(const HHSLshpvsEntry *entry, char *out, size_t out_size, size_t *written);
HHSLshpvsStatus hhs_lshpvs_entry_replay_verify(const HHSLshpvsEntry *entry);
const char *hhs_lshpvs_status_string(HHSLshpvsStatus status);

#ifdef __cplusplus
}
#endif

#endif
