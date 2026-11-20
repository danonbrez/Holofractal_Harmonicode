#include "../../hhs_runtime/include/hhs_lane5_master_closure.h"
#include <assert.h>
int main(void){
 HhsL5ClosureInput x={0}; HhsL5ClosureResult r={0}; unsigned i;
 x.source_length=100; x.source_sha256[0]=1; x.environment_sha256[0]=2;
 x.required_family_mask=255; x.present_family_mask=255; x.true_family_mask=255;
 x.delta_unity=x.ab_p4=x.delta_e_zero=x.psi_zero=x.omega_true=1;
 x.ordered_products_preserved=x.nested_modulus_preserved=x.complete_shared_environment=x.cross_layer_revalidated=1;
 for(i=0;i<81;i++) x.vm81_cell_witness[i]=1;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_ADMISSIBLE);
 x.vm81_cell_witness[42]=0;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_OPEN && r.open_cells==1);
 x.vm81_cell_witness[42]=2;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_PRUNE && r.false_cells==1);
 x.vm81_cell_witness[42]=1; x.false_family_mask=1; x.true_family_mask=254;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_PRUNE);
 x.false_family_mask=0;x.true_family_mask=255; x.delta_unity=0;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_OPEN && (r.open_closure&1));
 x.delta_unity=1;x.nested_modulus_preserved=2;
 assert(hhs_lane5_master_closure(&x,&r)==0 && r.decision==HHS_L5_PRUNE);
 return 0;
}
