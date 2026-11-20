#include "../../hhs_runtime/include/hhs_lane5_pass169_closure_bridge.h"
#include <assert.h>
#include <string.h>
#include <openssl/sha.h>
static HHSExactPass219Pass159GlobalWitnessProvenanceV1 prov;
static int mode=0;
static const uint8_t sample_source[]="HARMONICODE_LANE5_MASTER_TEST_SOURCE";
HHSExactStatus hhs_exact_pass219_pass169_bind_authority(
  const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *p,
  HHSExactPass219Pass169BindingResultV1 *out) {
  (void)p; memset(out,0,sizeof(*out));
  out->struct_size=sizeof(*out);
  out->version=(1U<<16)|(21U<<8)|11U;
  if(mode==1) {out->decision=HHS_EXACT_PASS219_PASS169_BINDING_UNRESOLVED;return HHS_EXACT_STATUS_OK;}
  if(mode==2) {out->decision=HHS_EXACT_PASS219_PASS169_BINDING_REJECT;
    out->boolean_gate_results_available=1;
    out->membrane_result.decision=HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT;
    return HHS_EXACT_STATUS_OK;}
  out->decision=HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE;
  out->pass169_authority_verified=1;out->whole_equation_propagated=1;
  out->canonical_monolithic_proof=1;
  out->membrane_result.decision=HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE;
  out->membrane_result.all_nested_boolean_gates_true=1;
  memset(out->proof_hash216,'A',216);memset(out->transition_hash216,'B',216);
  memset(out->receipt_hash72,'C',72);memset(out->replay_hash72,'D',72);
  if(mode==3)out->proof_hash216[15]=0;
  return HHS_EXACT_STATUS_OK;
}
static HhsL5Pass169ClosureInput fixture(void) {
  HhsL5Pass169ClosureInput x;
  unsigned i;
  memset(&x,0,sizeof(x));memset(&prov,0,sizeof(prov));
  prov.combined_source_sha256[0]=3;prov.global_symbol_environment_root[0]=4;
  x.provenance=&prov;
  x.master_source_bytes=sample_source;
  x.master_source_size=sizeof(sample_source)-1U;
  x.master.source_length=(uint32_t)x.master_source_size;
  assert(SHA256(x.master_source_bytes,x.master_source_size,
                x.master.source_sha256)!=NULL);
  memcpy(x.lineage_master_sha256,x.master.source_sha256,32);
  memcpy(x.lineage_inherited_sha256,prov.combined_source_sha256,32);
  x.master.environment_sha256[0]=2;
  x.master.required_family_mask=255;
  x.master.present_family_mask=255;x.master.true_family_mask=255;
  x.master.delta_unity=x.master.ab_p4=x.master.delta_e_zero=1;
  x.master.psi_zero=x.master.omega_true=1;
  x.master.ordered_products_preserved=x.master.nested_modulus_preserved=1;
  x.master.complete_shared_environment=x.master.cross_layer_revalidated=1;
  for(i=0;i<81;i++)x.master.vm81_cell_witness[i]=1;
  x.source_lineage_witness=1;
  return x;
}
int main(void) {
  HhsL5Pass169ClosureInput x=fixture(); HhsL5Pass169ClosureResult r;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0);
  assert(r.decision==HHS_L5_ADMISSIBLE && r.pass169_propagated && r.master_source_distinct);
  x.source_lineage_witness=0;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_OPEN);
  x.source_lineage_witness=2;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_PRUNE);
  x.source_lineage_witness=1;mode=1;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_OPEN);
  mode=0;x=fixture();x.master.vm81_cell_witness[7]=2;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_PRUNE);
  x=fixture();mode=3;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_OPEN);
  mode=2;x=fixture();
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==0 && r.decision==HHS_L5_PRUNE);
  mode=0;x=fixture();x.master.source_sha256[0]^=1U;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==-9);
  x=fixture();x.lineage_inherited_sha256[0]^=1U;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==-10);
  x=fixture();x.master_source_size--;
  assert(hhs_lane5_pass169_closure_bridge(&x,&r)==-9);
  return 0;
}
