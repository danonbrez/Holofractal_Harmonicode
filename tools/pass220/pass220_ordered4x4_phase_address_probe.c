/* Inherited VM81 address and native phase product test for typed s/v.
 * 64 operation-pair enumeration and distinct xy/yx orientation.
 */
#include "hhs_runtime_exact_abi.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#define CHECK(expr,msg) do{if(!(expr)){fprintf(stderr,"FAIL:%s\n",msg);return 1;}}while(0)

static uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U];
static uint8_t s_serialized[5184U],v_serialized[5184U];
static HHSExactPass219Hash216TransitionViewV1 parent;
static HHS220Ordered4x4PhaseAddressGateV1 base,replay,changed,rejected;

static HHSExactStatus execute(
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *reference,
 HHS220Ordered4x4PhaseAddressGateV1 *out) {
 return hhs_exact_pass220_ordered4x4_phase_address_gate(
 source,HHS220_ORDERED4X4_SOURCE_BYTES,s,v,reference,out);
}

int main(void) {
 HHS220Ordered4x4NativeTensorBindingV1 s,v;
 HHSExactPass219Hash216TransitionViewV1 forged;
 HHSExactPass219NativePhaseWitnessV1 phase_check;
 FILE *file=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 size_t n;
 uint8_t op;
 uint8_t xy_root[32];
 CHECK(file!=NULL,"source file");
 n=fread(source,1U,sizeof(source),file);
 CHECK(!ferror(file) && fclose(file)==0 && n==HHS220_ORDERED4X4_SOURCE_BYTES,
       "verbatim source");
 CHECK(hhs_exact_pass219_vm81_pqc_hash216_genesis_reference(&parent)==HHS_EXACT_STATUS_OK,
       "inherited complete indexed parent");
 memset(s_serialized,'X',sizeof(s_serialized));
 memset(v_serialized,'Y',sizeof(v_serialized));
 memset(&s,0,sizeof(s));memset(&v,0,sizeof(v));
 s.struct_size=(uint32_t)sizeof(s);s.symbol='s';s.cell81=4U;s.operation64=9U;
 s.state_utf8=s_serialized;s.state_bytes=sizeof(s_serialized);
 s.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 s.predecessor_bytes=216U;
 v.struct_size=(uint32_t)sizeof(v);v.symbol='v';v.cell81=8U;v.operation64=17U;
 v.state_utf8=v_serialized;v.state_bytes=sizeof(v_serialized);
 v.predecessor_hash216=(const uint8_t *)parent.transition_identity216;
 v.predecessor_bytes=216U;

 CHECK(execute(&s,&v,&parent,&base)==HHS_EXACT_STATUS_OK,"phase gate accepted");
 CHECK(execute(&s,&v,&parent,&replay)==HHS_EXACT_STATUS_OK,"phase gate repeated");
 CHECK(memcmp(&base,&replay,sizeof(base))==0,"complete deterministic phase-address witness");
 CHECK(base.verbatim_source_verified==1U && base.inherited_parent_index_verified==1U &&
       base.ordered_outer_geometry_verified==1U &&
       base.both_phase_address_roundtrips_verified==1U &&
       base.both_native_phase_products_verified==1U,
       "source bound inherited native phase products");
 CHECK(base.bindings[0].address5184==265U && base.bindings[1].address5184==529U,
       "VM81 address retained");
 CHECK(base.bindings[0].left_phase_basis8==1U &&
       base.bindings[0].right_phase_basis8==1U &&
       base.bindings[1].left_phase_basis8==2U &&
       base.bindings[1].right_phase_basis8==1U,
       "operation64 decodes ordered native phase bases");
 CHECK(base.bindings[0].native_phase_witness.ordered_source_preserved==1U &&
       base.bindings[1].native_phase_witness.ordered_source_preserved==1U,
       "native phase pair source order");
 CHECK(!base.tensor_action_rank_resolved && !base.tensor_phase_state_fully_verified &&
       !base.matrix_values_derived && !base.equation_equality_proved &&
       !base.parent_signature_authenticated && !base.signed_vm81_admitted &&
       !base.hash72_commit_authority && !base.hash216_commit_authority &&
       !base.canonical_vm81_mutation_authority,
       "phase address does not establish full tensor proof or canonical receipts");

 for(op=0U;op<64U;++op) {
  const HHS220Ordered4x4PhaseAddressV1 *witness;
  uint16_t encoded=0U;
  s.operation64=op;
  CHECK(execute(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,
        "all 64 ordered phase addresses admitted for source binding");
  witness=&changed.bindings[0];
  CHECK(witness->left_phase_basis8==(uint8_t)(op/8U) &&
        witness->right_phase_basis8==(uint8_t)(op%8U) &&
        witness->address5184==(uint16_t)(256U+op),
        "ordered VM81 basis-pair decode");
  CHECK(hhs_exact_vm5184_address_encode(
     4U,witness->left_phase_basis8,witness->right_phase_basis8,&encoded)==HHS_EXACT_STATUS_OK
     && encoded==witness->address5184,"native 5184 encode roundtrip");
  CHECK(hhs_exact_pass219_native_phase_witness(
     witness->left_phase_basis8,witness->right_phase_basis8,&phase_check)==HHS_EXACT_STATUS_OK,
     "registered native RNA phase witness");
  CHECK(memcmp(&phase_check,&witness->native_phase_witness,sizeof(phase_check))==0,
        "exact native phase witness equality");
  CHECK(memcmp(changed.bindings[1].directional_phase_address_root,
               base.bindings[1].directional_phase_address_root,32U)==0,
        "s phase movement does not alter v phase-address root");
  CHECK(!changed.tensor_action_rank_resolved &&
        !changed.tensor_phase_state_fully_verified &&
        !changed.hash216_commit_authority,"all candidate phase-pairs stay nonauthoritative");
 }
 s.operation64=1U; /* x then y */
 CHECK(execute(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"xy ordered pair");
 CHECK(changed.bindings[0].left_phase_basis8==HHS_EXACT_PHASE_X &&
       changed.bindings[0].right_phase_basis8==HHS_EXACT_PHASE_Y,"xy orientation");
 memcpy(xy_root,changed.bindings[0].directional_phase_address_root,32U);
 s.operation64=8U; /* y then x */
 CHECK(execute(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"yx ordered pair");
 CHECK(changed.bindings[0].left_phase_basis8==HHS_EXACT_PHASE_Y &&
       changed.bindings[0].right_phase_basis8==HHS_EXACT_PHASE_X,"yx orientation");
 CHECK(memcmp(xy_root,changed.bindings[0].directional_phase_address_root,32U)!=0,
       "xy and yx addressed phase roots are different");
 s.operation64=9U;
 s_serialized[0]='S';
 CHECK(execute(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"typed s state changed");
 CHECK(memcmp(changed.bindings[0].directional_phase_address_root,
              base.bindings[0].directional_phase_address_root,32U)!=0,
       "s state provenance impacts phase-address root");
 CHECK(memcmp(changed.bindings[1].directional_phase_address_root,
              base.bindings[1].directional_phase_address_root,32U)==0,
       "s state does not alter v independent phase address");
 s_serialized[0]='X';
 v_serialized[0]='V';
 CHECK(execute(&s,&v,&parent,&changed)==HHS_EXACT_STATUS_OK,"typed v state changed");
 CHECK(memcmp(changed.bindings[0].directional_phase_address_root,
              base.bindings[0].directional_phase_address_root,32U)==0,
       "v state does not alter s phase address");
 CHECK(memcmp(changed.bindings[1].directional_phase_address_root,
              base.bindings[1].directional_phase_address_root,32U)!=0,
       "v state provenance changes own phase-address root");
 v_serialized[0]='Y';

 s.operation64=64U;
 CHECK(execute(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
       "invalid operation phase coordinate rejected");
 s.operation64=9U;
 v.cell81=81U;
 CHECK(execute(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
       "invalid cell81 rejected");
 v.cell81=8U;
 v.symbol='s';
 CHECK(execute(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
       "swapped tensor role rejected");
 v.symbol='v';
 forged=parent;
 forged.occurrences[215].sha256_index_record[0]^=1U;
 CHECK(execute(&s,&v,&forged,&rejected)!=HHS_EXACT_STATUS_OK,
       "corrupt inherited Hash216 reference rejected");
 source[0]^=1U;
 CHECK(execute(&s,&v,&parent,&rejected)!=HHS_EXACT_STATUS_OK,
       "corrupt verbatim equation rejected");
 CHECK(!rejected.both_native_phase_products_verified &&
       !rejected.hash72_commit_authority &&
       !rejected.hash216_commit_authority,
       "failure does not confer phase or receipt authority");
 source[0]^=1U;
 CHECK(hhs_exact_pass220_ordered4x4_phase_address_gate(
       source,n,&s,&v,&parent,NULL)!=HHS_EXACT_STATUS_OK,
       "null output rejected");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_NATIVE_PHASE_ADDRESS_V1\","
      "\"all_64_phase_addresses\":true,\"xy_yx_distinct\":true,"
      "\"source_bound_native_RNA_witness\":true,\"typed_branch_isolation\":true,"
      "\"negative_cases_rejected\":true,\"tensor_rank_resolved\":false,"
      "\"complete_phase_state_verified\":false,\"matrix_values_derived\":false,"
      "\"equality_proved\":false,\"signed_VM81_admitted\":false,"
      "\"hash72_commit\":false,\"hash216_commit\":false}");
 return 0;
}
