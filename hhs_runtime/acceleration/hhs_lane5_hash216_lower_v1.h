/* Exact Pass174 Hash216Array.build character-index lowering.
 * Uses the same sorted compact ASCII JSON and SHA-256 domain prefixes.
 * This is a candidate computation only; no canonical mint or persistence. */
#ifndef HHS_LANE5_HASH216_LOWER_V1_H
#define HHS_LANE5_HASH216_LOWER_V1_H
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
  const char *genesis_identity; /* 64 lowercase hexadecimal */
  const char *legacy_foundation_root; /* 64 lowercase hexadecimal */
  const char *operation_identity; /* 64 lowercase hexadecimal */
  uint64_t logical_step;
  const char *previous, *change, *receipt; /* 72-char Hash72 inputs */
} hhs_hash216_lower_input;
typedef struct {
  char combined[217];
  char logical_identity_sha256[65];
  char character_indexes_sha256[216][65];
  char index_root_sha256[65];
} hhs_hash216_lower_output;
/* 0 success; nonzero fail closed. Output unchanged upon error. */
int hhs_hash216_lower_pass174(const hhs_hash216_lower_input *in,
                              hhs_hash216_lower_output *out);
#ifdef __cplusplus
}
#endif
#endif
