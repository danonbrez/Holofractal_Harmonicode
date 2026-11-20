#include "../include/hhs_lane5_master_closure.h"
#include <string.h>
static int nonzero(const uint8_t x[32]) { uint8_t a=0; size_t i; for(i=0;i<32;i++) a|=x[i]; return a!=0; }
static int tri(uint8_t x) { return x<=HHS_L5_WITNESS_FALSE; }
int hhs_lane5_master_closure(const HhsL5ClosureInput *in, HhsL5ClosureResult *out) {
 size_t i; const uint8_t *w;
 if(!in||!out) return -1;
 memset(out,0,sizeof(*out));
 if(in->source_length==0 || !nonzero(in->source_sha256) || !nonzero(in->environment_sha256)) return -2;
 if(in->required_family_mask!=HHS_L5_FULL_MASK ||
   ((in->present_family_mask|in->true_family_mask|in->false_family_mask)&~HHS_L5_FULL_MASK)!=0 ||
   (in->true_family_mask&in->false_family_mask)!=0 ||
   ((in->true_family_mask|in->false_family_mask)&~in->present_family_mask)!=0) return -3;
 w=&in->delta_unity;
 for(i=0;i<9;i++) if(!tri(w[i])) return -4;
 for(i=0;i<HHS_L5_CELLS;i++) if(!tri(in->vm81_cell_witness[i])) return -5;
 out->source_bound=1;
 out->environment_bound=1;
 out->open_families=in->required_family_mask & ~in->present_family_mask;
 out->false_families=in->false_family_mask;
 for(i=0;i<9;i++) {
   if(w[i]==HHS_L5_WITNESS_OPEN) out->open_closure|=UINT32_C(1)<<i;
   if(w[i]==HHS_L5_WITNESS_FALSE) out->false_closure|=UINT32_C(1)<<i;
 }
 for(i=0;i<HHS_L5_CELLS;i++) {
   out->open_cells+=(in->vm81_cell_witness[i]==HHS_L5_WITNESS_OPEN);
   out->false_cells+=(in->vm81_cell_witness[i]==HHS_L5_WITNESS_FALSE);
 }
 if(out->false_families || out->false_cells || out->false_closure) out->decision=HHS_L5_PRUNE;
 else if(out->open_families || (in->true_family_mask!=in->required_family_mask) || out->open_cells || out->open_closure)
   out->decision=HHS_L5_OPEN;
 else out->decision=HHS_L5_ADMISSIBLE;
 out->vm81_candidate_ready=(out->decision==HHS_L5_ADMISSIBLE);
 return 0;
}
