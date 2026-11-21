#include "../../hhs_runtime/include/hhs_pass220_genesis_quadruple_gate_v1.hpp"
#include <cassert>
#include <iostream>
using namespace hhs::pass220::quadruple;
int main(){
  for(unsigned p:{0u,18u,36u,54u})
    assert(verify({1},{-1},{2},{1,2},p).status==GateStatus::CandidateClosed);
  assert(verify({2},{-1},{2},{1,2},0).status==GateStatus::CandidateRejected);
  assert(verify({1},{0},{2},{1,2},0).status==GateStatus::Undefined);
  assert(verify({1},{-1},{2},{0},0).status==GateStatus::Undefined);
  assert(verify({1},{-1},{2},{1,2},5).status==GateStatus::Undefined);
  const Big huge=pow(Big(2),512);
  assert(verify({huge},{huge*huge},{1},{1},0).status==GateStatus::CandidateClosed);
  assert(equal(multiply({Big(179971),Big(1)},{Big(1000001),Big(1000000)}),
               {Big("179971179971"),Big(1000000)}));
  std::cout<<"PASS: exact Module 29 BigInt cross-products, guarded divisions and phase addresses\n";
}
