#ifndef HHS_LANE5_PASS169_CLOSURE_BRIDGE_H
#define HHS_LANE5_PASS169_CLOSURE_BRIDGE_H
#include "hhs_lane5_master_closure.h"
#include "hhs_pass219_pass169_gate_authority_binding_1_21_11.h"
#ifdef __cplusplus
extern "C" {
#endif
typedef struct {
  HhsL5ClosureInput master;
  /* Pass159/169 provenance applies to its own frozen source identity. */
  const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance;
  /* Exact master-to-inherited lineage proof supplied by an upstream evaluator. */
  uint8_t source_lineage_witness;
} HhsL5Pass169ClosureInput;
typedef struct {
  HhsL5ClosureResult closure;
  HhsL5Decision decision;
  uint8_t pass169_propagated;
  uint8_t master_source_distinct;
  uint8_t inherited_receipts_present;
} HhsL5Pass169ClosureResult;
int hhs_lane5_pass169_closure_bridge(const HhsL5Pass169ClosureInput *in,
                                    HhsL5Pass169ClosureResult *out);
#ifdef __cplusplus
}
#endif
#endif
