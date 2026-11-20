#include "../include/hhs_lane5_pass169_closure_bridge.h"
#include <string.h>
#include <openssl/sha.h>
static int nonzero32(const uint8_t *p) {
  size_t i; uint8_t a=0; for(i=0;i<32;i++) a|=p[i]; return a!=0;
}
static int root72(const char *p) {
  size_t i;
  if (p[72]!='\0') return 0;
  for (i=0;i<72;i++) if (p[i]=='\0') return 0;
  return 1;
}
static int root216(const char *p) {
  size_t i;
  if (p[216]!='\0') return 0;
  for (i=0;i<216;i++) if (p[i]=='\0') return 0;
  return 1;
}
int hhs_lane5_pass169_closure_bridge(const HhsL5Pass169ClosureInput *in,
                                    HhsL5Pass169ClosureResult *out) {
  int rc;
  HHSExactPass219Pass169BindingResultV1 pass169;
  HHSExactStatus status;
  uint8_t source_digest[SHA256_DIGEST_LENGTH];
  if(!in || !out) return -1;
  memset(out,0,sizeof(*out));
  /* Bind exact master bytes before consuming any caller-supplied witness. */
  if(!in->master_source_bytes || in->master_source_size==0 ||
     in->master_source_size!=in->master.source_length ||
     SHA256(in->master_source_bytes,in->master_source_size,source_digest)==NULL ||
     memcmp(source_digest,in->master.source_sha256,SHA256_DIGEST_LENGTH)!=0)
    return -9;
  rc=hhs_lane5_master_closure(&in->master,&out->closure);
  if(rc) return rc;
  out->decision=out->closure.decision;
  if(out->decision==HHS_L5_PRUNE) return 0;
  if(!in->provenance || in->source_lineage_witness>HHS_L5_WITNESS_FALSE) return -6;
  if(!nonzero32(in->provenance->combined_source_sha256) ||
     !nonzero32(in->provenance->global_symbol_environment_root)) return -6;
  if(memcmp(in->lineage_master_sha256,in->master.source_sha256,32)!=0 ||
     memcmp(in->lineage_inherited_sha256,in->provenance->combined_source_sha256,32)!=0)
    return -10;
  out->master_source_distinct=(memcmp(in->master.source_sha256,
                                     in->provenance->combined_source_sha256,32)!=0);
  /* Preserve separate source identities. A typed, verified lineage witness
     binds the new master to the inherited frozen Pass159/169 subgraph. */
  if(in->source_lineage_witness==HHS_L5_WITNESS_FALSE) {
    out->decision=HHS_L5_PRUNE; out->closure.vm81_candidate_ready=0; return 0;
  }
  if(in->source_lineage_witness==HHS_L5_WITNESS_OPEN) {
    out->decision=HHS_L5_OPEN; out->closure.vm81_candidate_ready=0; return 0;
  }
  memset(&pass169,0,sizeof(pass169));
  status=hhs_exact_pass219_pass169_bind_authority(in->provenance,&pass169);
  if(status!=HHS_EXACT_STATUS_OK) return -7;
  if(pass169.struct_size<sizeof(pass169) ||
     pass169.version!=((1U<<16)|(21U<<8)|11U)) return -8;
  if(pass169.decision==HHS_EXACT_PASS219_PASS169_BINDING_REJECT) {
    if(pass169.membrane_result.decision==HHS_EXACT_PASS219_GLOBAL_MEMBRANE_REJECT &&
       pass169.membrane_result.all_nested_boolean_gates_true==0U &&
       pass169.boolean_gate_results_available==1U) out->decision=HHS_L5_PRUNE;
    else out->decision=HHS_L5_OPEN;
  } else if(pass169.decision!=HHS_EXACT_PASS219_PASS169_BINDING_PROPAGATE ||
            !pass169.pass169_authority_verified ||
            !pass169.whole_equation_propagated ||
            !pass169.canonical_monolithic_proof ||
            pass169.membrane_result.decision!=HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE ||
            !pass169.membrane_result.all_nested_boolean_gates_true) {
    out->decision=HHS_L5_OPEN;
  } else {
    out->inherited_receipts_present=(root216(pass169.proof_hash216) &&
      root216(pass169.transition_hash216) &&
      root72(pass169.receipt_hash72) && root72(pass169.replay_hash72));
    out->pass169_propagated=out->inherited_receipts_present;
    if(!out->pass169_propagated) out->decision=HHS_L5_OPEN;
  }
  out->closure.vm81_candidate_ready=(out->decision==HHS_L5_ADMISSIBLE);
  return 0;
}
