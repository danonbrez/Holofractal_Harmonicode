#include "hhs_module196_lane5_coprocessor.h"
#include <cassert>
int main(){
 HHSModule196Candidate out{};
 assert(hhs_m196_evaluate(179971179971ULL,179971179972ULL,&out));
 assert(out.addresses==81 && out.equality_cells==18 && out.local_p2_cells==63);
 assert(out.hnan_addresses==25 && out.hnan_children==2025);
 assert(out.value[40]==125 && out.gate[40] && out.lane_a[40]==125 && out.lane_b[40]==125);
 assert(out.sum==9105 && out.trace==1297);
 assert(!out.vm81_mutation_authority && !out.hash72_authority && !out.hash216_authority);
 HHSModule196Candidate denied{};
 assert(!hhs_m196_evaluate(20,19,&denied));
 assert(denied.accepted_candidate==0);
}
