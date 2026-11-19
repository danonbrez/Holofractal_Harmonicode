#ifndef HHS_LANE5_MASTER_CLOSURE_H
#define HHS_LANE5_MASTER_CLOSURE_H
#include <stdint.h>
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
#define HHS_L5_FAMILIES 8u
#define HHS_L5_CELLS 81u
#define HHS_L5_FULL_MASK UINT32_C(255)
/* Families inherit Pass219 monolithic_constraint_abi_1_20.h ordering. */
typedef enum {
 HHS_L5_HARMONIC=0, HHS_L5_MATRIX=1, HHS_L5_ORDERED_PHASE=2,
 HHS_L5_TENSOR_SUBSTITUTION=3, HHS_L5_MODULAR=4, HHS_L5_AB_ROOT=5,
 HHS_L5_TERMINAL=6, HHS_L5_DELTA_ROOT=7
} HhsL5Family;
typedef enum { HHS_L5_OPEN=0, HHS_L5_ADMISSIBLE=1, HHS_L5_PRUNE=2 } HhsL5Decision;
typedef enum { HHS_L5_WITNESS_OPEN=0, HHS_L5_WITNESS_TRUE=1, HHS_L5_WITNESS_FALSE=2 } HhsL5WitnessState;
typedef struct {
 uint32_t source_length;
 uint8_t source_sha256[32];
 uint8_t environment_sha256[32];
 uint32_t required_family_mask;
 uint32_t present_family_mask;
 uint32_t true_family_mask;
 uint32_t false_family_mask;
 /* Typed upstream exact predicates, not a scalar substitution engine. */
 uint8_t delta_unity;
 uint8_t ab_p4;
 uint8_t delta_e_zero;
 uint8_t psi_zero;
 uint8_t omega_true;
 uint8_t ordered_products_preserved;
 uint8_t nested_modulus_preserved;
 uint8_t complete_shared_environment;
 uint8_t cross_layer_revalidated;
 uint8_t vm81_cell_witness[HHS_L5_CELLS];
} HhsL5ClosureInput;
typedef struct {
 HhsL5Decision decision;
 uint32_t open_families;
 uint32_t false_families;
 uint32_t open_cells;
 uint32_t false_cells;
 uint32_t open_closure;
 uint32_t false_closure;
 uint8_t source_bound;
 uint8_t environment_bound;
 uint8_t vm81_candidate_ready;
} HhsL5ClosureResult;
/* Propagates already-evaluated source-bound witnesses. An OPEN witness does not
 refute the equation. PRUNE requires an explicit false witness. Canonical
 mutation remains in the inherited Pass169/VM81 authority path. */
int hhs_lane5_master_closure(const HhsL5ClosureInput *in, HhsL5ClosureResult *out);
#ifdef __cplusplus
}
#endif
#endif
