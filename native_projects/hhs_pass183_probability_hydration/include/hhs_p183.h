#ifndef HHS_P183_H
#define HHS_P183_H

#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif

typedef enum hhs_p183_status {
    P183_OK=0,P183_REJECT_LEXICAL_IDENTITY=1,P183_REJECT_PARSE=2,
    P183_REJECT_UNBALANCED_MEMBRANE=3,P183_REJECT_MEMBRANE_WITNESS=4,
    P183_REJECT_LIST_ORDER=5,P183_REJECT_FACTORIAL_LANE=6,
    P183_REJECT_PROBABILITY_DOMAIN=7,P183_REJECT_EQUATION_FALSE=8,
    P183_REJECT_ZERO_DENOMINATOR=9,P183_ZERO_BYPASS=10,
    P183_REJECT_RECIPROCAL_CONSTRUCTION=11,P183_REJECT_LOCAL_MODULAR_INVERSION=12,
    P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR=13,P183_REJECT_FLOAT_AUTHORITY=14,
    P183_REJECT_RANDOMNESS_MANIFEST=15,P183_REJECT_REPLAY=16,
    P183_REJECT_RECEIPT=17,P183_TIMEOUT=18,P183_CANCELLED=19,P183_INTERNAL_ERROR=20
} hhs_p183_status;

typedef struct hhs_p183_context hhs_p183_context;
hhs_p183_context *hhs_p183_context_create(void);
void hhs_p183_context_destroy(hhs_p183_context *context);
hhs_p183_status hhs_p183_parse_equation(hhs_p183_context*,const char*,size_t);
hhs_p183_status hhs_p183_snapshot_lexical_identity(hhs_p183_context*,char out_sha256[65]);
hhs_p183_status hhs_p183_validate_probability_domain(hhs_p183_context*,int);
hhs_p183_status hhs_p183_validate_equation_truth(hhs_p183_context*,int);
hhs_p183_status hhs_p183_build_membrane_tree(hhs_p183_context*);
hhs_p183_status hhs_p183_validate_membrane_boundaries(hhs_p183_context*);
hhs_p183_status hhs_p183_bind_hydration_roles(hhs_p183_context*,const char*,const char*,const char*,const char*);
hhs_p183_status hhs_p183_hydrate_factorial72_forward(hhs_p183_context*,char*,size_t);
hhs_p183_status hhs_p183_construct_reciprocal_lane(hhs_p183_context*,char*,size_t);
hhs_p183_status hhs_p183_execute_probability_adapter(hhs_p183_context*,const char*,int);
hhs_p183_status hhs_p183_close_u72(hhs_p183_context*);
hhs_p183_status hhs_p183_route_typed_zero(hhs_p183_context*);
hhs_p183_status hhs_p183_apply_outer_modulus(hhs_p183_context*,int64_t,uint64_t,uint32_t*,int*);
hhs_p183_status hhs_p183_emit_hash72_receipt(hhs_p183_context*,char out_hash72[73]);
hhs_p183_status hhs_p183_compute_hash216_identity(hhs_p183_context*,char out_hash216[217]);
hhs_p183_status hhs_p183_replay(hhs_p183_context*);
hhs_p183_status hhs_p183_verify_receipt(hhs_p183_context*,const char*);
const char *hhs_p183_status_name(hhs_p183_status);
const char *hhs_p183_canonical_formula(void);
const char *hhs_p183_forward_lane_token(void);
const char *hhs_p183_reciprocal_lane_token(void);
const char *hhs_p183_factorial72_decimal(void);
uint32_t hhs_p183_global_modulus(void);
uint32_t hhs_p183_factorial72_modulus_gcd(void);
size_t hhs_p183_membrane_count(const hhs_p183_context*);
#ifdef __cplusplus
}
#endif
#endif
