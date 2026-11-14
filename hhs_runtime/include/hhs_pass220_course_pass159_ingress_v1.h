#ifndef HHS_PASS220_COURSE_PASS159_INGRESS_V1_H
#define HHS_PASS220_COURSE_PASS159_INGRESS_V1_H

#include "hhs_pass159_api.h"
#include "hhs_runtime_exact_abi_v1_1_base.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Extract exact module source bytes from the indexed canonical expanded course.
 * Caller supplies the course file path; neither source nor phase is rewritten.
 * On BUFFER_TOO_SMALL, required byte count is returned in out_size.
 */
HHS_EXACT_API HHSExactStatus hhs_exact_pass220_course_module_source(
    uint32_t module_number,
    const char *course_file,
    uint8_t *out_bytes,
    size_t out_capacity,
    size_t *out_size
);

/*
 * Pass the exact selected module bytes to the inherited Pass159 frontend:
 * source -> lex -> CST -> AST -> typecheck -> constraint graph -> HIR -> VMIR.
 * VMIR is serialized via the existing Pass159 API, with its original error
 * status returned when the course source is not accepted by that frontend.
 * This API does not assert a VM81 instruction encoding or grant admission.
 */
HHS_EXACT_API HHS159Status hhs_exact_pass220_course_module_pass159_vmir(
    uint32_t module_number,
    const char *course_file,
    HHS159MutableByteSpan *out_vmir,
    char source_hash216[HHS159_HASH216_LENGTH + 1U],
    char vmir_hash216[HHS159_HASH216_LENGTH + 1U]
);

#ifdef __cplusplus
}
#endif
#endif
