#include "../../hhs_runtime/include/hhs_pass220_saturated_offset_layer_v1.hpp"
#include <cassert>
#include <iostream>
using namespace hhs::pass220::offset_layer;
int main(){
 for(std::size_t s=0;s<count;++s)assert(to_vm(to_reciprocal(s))==s);
 for(std::size_t t=0;t<count;++t)assert(to_reciprocal(to_vm(t))==t);
 CandidateLayer genesis{}, first{},second{}, duplicate{};
 for(std::size_t s=0;s<count;++s){
  genesis.active[s]=first.active[s]=second.active[s]=duplicate.active[s]=true;
  const auto p=phase(s/64+s%64);
  genesis.genesis[s]=first.genesis[s]=second.genesis[s]=duplicate.genesis[s]=p;
  first.offsets[s]=1;
  second.offsets[s]=2;
  duplicate.offsets[s]=1;
 }
 assert(saturated(first));
 assert(valid_candidate(first,genesis));
 assert(valid_candidate(second,genesis,&first));
 assert(!valid_candidate(duplicate,genesis,&first));
 assert(!valid_candidate(genesis,genesis));
 auto a=project(first);
 assert(vm_view(reciprocal_view(a))==a);
 auto b=project(second);
 auto rel=relative_offsets(first,second);
 for(std::size_t s=0;s<count;++s){
  assert(compose_phase(a[s],rel[s])==b[s]);
  assert(compose_phase(rel[s],inverse_phase(rel[s]))==0);
 }
 first.active[17]=false;
 assert(!saturated(first));
 assert(!valid_candidate(first,genesis));
 std::cout<<"PASS: 5184 reversible positions, saturation, uniqueness and phase offsets\n";
}
