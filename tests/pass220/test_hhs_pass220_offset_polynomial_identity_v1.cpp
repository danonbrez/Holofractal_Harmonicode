#include "../../hhs_runtime/include/hhs_pass220_offset_polynomial_identity_v1.hpp"
#include <cassert>
#include <iostream>
using namespace hhs::pass220::polynomial_offset;
int main(){
 WitnessLayer genesis{},a{},b{},duplicate{};
 for(WitnessLayer* l:{&genesis,&a,&b,&duplicate}){
  l->genesis_id="179971.179971";
  for(std::size_t s=0;s<count;++s){
   l->phase_layer.active[s]=true;l->phase_layer.genesis[s]=phase(s/64+s%64);
   l->witnesses[s]={s,to_reciprocal(s),"G:x+y-z-w+xy-zw","x^4*(zw)^3=y^2","row:column","Genesis;LoShu;Phase72;VM81"};
  }
 }
 for(std::size_t s=0;s<count;++s){a.phase_layer.offsets[s]=1;b.phase_layer.offsets[s]=2;duplicate.phase_layer.offsets[s]=1;}
 assert(complete(a));assert(candidate_distinct(a,genesis,{}));
 assert(candidate_distinct(b,genesis,{&a}));
 assert(!candidate_distinct(duplicate,genesis,{&a}));
 assert(!candidate_distinct(genesis,genesis,{}));
 b.witnesses[11].polynomial_expression="(x^2)^2*(zw)^3=y^2";
 assert(candidate_distinct(b,genesis,{&a}));
 b.witnesses[11].constraint_ancestry.clear();
 assert(!candidate_distinct(b,genesis,{&a}));
 b.witnesses[11].constraint_ancestry="Genesis;LoShu;Phase72;VM81";
 b.witnesses[11].genesis_expression="NOT_GENESIS";
 assert(!candidate_distinct(b,genesis,{&a}));
 std::cout<<"PASS: ordered polynomial witnesses, Genesis ancestry, 5184 reciprocal cells\n";
}
