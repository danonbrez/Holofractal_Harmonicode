#include "../../hhs_runtime/include/hash72_genesis_phase_cell_wall.hpp"
#include <cassert>
#include <iostream>
int main() {
  using namespace hhs::pass220::genesis;
  static_assert(address(3,17,3,17)==5183);
  static_assert(mod72(-1)==71);
  Candidate p; p.sourceHash72=std::string(72,'x');
  for (std::size_t i=0;i<72;++i) {p.genesisRows[i]=i; p.genesisCols[i]=i;}
  const auto m=p.reconstruct();
  for (std::size_t i=0;i<72;++i) {
    assert(m[72*i+i]==0);
    for (std::size_t j=0;j<72;++j)
      assert(compose(m[72*i+j],m[72*j+i])==0);
  }
  p.rowOffsets[0]=18; assert(p.at(0,0)==18);
  p.colOffsets[0]=18; assert(p.at(0,0)==0);
  p.sourceHash72="wrong"; assert(!p.valid());
  std::cout<<"PASS: 5184 candidate addresses with reciprocal closure\n";
}
