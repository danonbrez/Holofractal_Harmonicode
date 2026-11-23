#ifndef HHS_PASS220_72_SHELL_GATE_GRAPH_V1_H
#define HHS_PASS220_72_SHELL_GATE_GRAPH_V1_H
#include "hhs_pass220_72_shell_source_bound_v1.h"
#include <stdint.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum {
 HHS_72_GATE_ORDERED_RELATION = 1,
 HHS_72_GATE_SQUARED_OUTER_RELATION = 2
} HHS72GateKind;
typedef struct {
 uint32_t source_offset;
 uint32_t left_node;
 uint32_t right_node;
 HHS72GateKind kind;
 uint8_t proved;
} HHS72GateEdge;
typedef struct {
 uint8_t source_sha256[32];
 HHS72ShellSpan operands[4];
 HHS72ShellSpan outer_left;
 HHS72ShellSpan outer_right;
 HHS72GateEdge edges[4];
 uint32_t edge_count;
 uint32_t proved_count;
 uint8_t admitted;
} HHS72GateGraph;
/* Deterministic, read-only dependency graph; no proof promotion. */
int hhs_pass220_72_shell_build_gate_graph(
 const uint8_t *source,size_t length,HHS72GateGraph *out);
#ifdef __cplusplus
}
#endif
#endif
