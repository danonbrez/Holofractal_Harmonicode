#ifndef HHS_PASS220_72_SHELL_SOURCE_BOUND_V1_H
#define HHS_PASS220_72_SHELL_SOURCE_BOUND_V1_H
#include <stddef.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS_72_SHELL_SOURCE_BYTES 121U
#define HHS_72_SHELL_GATE_COUNT 4U
#define HHS_72_SHELL_OPERAND_COUNT 4U
typedef enum {
 HHS_72_SHELL_INVALID_SOURCE = 0,
 HHS_72_SHELL_STRUCTURAL_ONLY = 1,
 HHS_72_SHELL_NATIVE_PROVED = 2
} HHS72ShellStatus;
typedef struct {
 uint32_t byte_start;
 uint32_t byte_end;
} HHS72ShellSpan;
typedef struct {
 HHS72ShellStatus status;
 uint32_t gate_offsets[HHS_72_SHELL_GATE_COUNT];
 HHS72ShellSpan inner_operands[HHS_72_SHELL_OPERAND_COUNT];
 HHS72ShellSpan squared_chain;
 HHS72ShellSpan outer_left;
 HHS72ShellSpan outer_right;
 uint8_t source_sha256[32];
 uint8_t native_proof_admitted;
 uint8_t vm81_admitted;
} HHS72ShellResult;
/* Read-only source validation: no VM81/Hash72/Hash216 capability. */
HHS72ShellStatus hhs_pass220_72_shell_lower(
 const uint8_t *source, size_t source_size, HHS72ShellResult *out);
#ifdef __cplusplus
}
#endif
#endif
