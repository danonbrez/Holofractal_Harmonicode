#ifndef HHS_PASS157_INTERNAL_H
#define HHS_PASS157_INTERNAL_H
#include "hhs_pass157.h"
void hhs157_hash216_bytes(const void *data, size_t size, char out[HHS157_HASH216_STRLEN]);
HHS157Status hhs157_canonical_transition(const HHS157Request *request, const HHS157Result *result, char *out, size_t out_size);
#endif
