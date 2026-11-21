#include "../../hhs_runtime/include/hash72_ordered_factorization_translation.hpp"
#include <cassert>
#include <cstddef>
#include <iostream>
int main() {
 using namespace hhs::pass220::factorization;
 for(std::size_t n: {64u,72u,81u})
  for(std::size_t i=0;i<n;++i) for(std::size_t j=0;j<n;++j)
    assert(col(i,j,n)==row(j,i,n));
 for(std::size_t r=0;r<4;++r) for(std::size_t a=0;a<18;++a)
 for(std::size_t c=0;c<4;++c) for(std::size_t b=0;b<18;++b)
  assert(spinorLoShu(r,a,c,b)==row(18*r+a,18*c+b,72));
 std::array<std::size_t,5184> s{};
 for(std::size_t i=0;i<5184;++i)s[i]=i;
 const auto tr=transpose(s,72); assert(transpose(tr,72)==s);
 const auto block=blockTranspose(s);assert(inverseBlockTranspose(block)==s);
 for(std::size_t c=0;c<81;++c)for(std::size_t t=0;t<8;++t)
  for(std::size_t b=0;b<8;++b) assert(vm5184(c,t,b)==64*c+8*t+b);
 std::cout<<"PASS: 64/72/81 transpose, 16x324 factorization and 5184-byte roundtrip\n";
}
