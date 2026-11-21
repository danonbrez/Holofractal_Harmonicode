#pragma once
// Candidate-only exact ordered factorization views. Does not mint Hash72.
#include <array>
#include <cstddef>
#include <stdexcept>
namespace hhs::pass220::factorization {
constexpr std::size_t N=72, Count=N*N;
constexpr std::size_t row(std::size_t i,std::size_t j,std::size_t n) {return n*i+j;}
constexpr std::size_t col(std::size_t i,std::size_t j,std::size_t n) {return n*j+i;}
constexpr std::size_t spinorLoShu(std::size_t sr,std::size_t lr,std::size_t sc,std::size_t lc) {
  return row(18*sr+lr,18*sc+lc,72);
}
constexpr std::size_t vm5184(std::size_t cell,std::size_t octet,std::size_t byte) {
  return row(cell,octet*8+byte,64);
}
constexpr std::size_t blockRow(std::size_t octet,std::size_t cell,std::size_t byte) {
  return octet*648+cell*8+byte;
}
constexpr std::size_t blockColumn(std::size_t octet,std::size_t byte,std::size_t cell) {
  return octet*648+byte*81+cell;
}
static_assert(4*18==72 && 81*8*8==5184);
static_assert(spinorLoShu(3,17,3,17)==5183);
static_assert(vm5184(80,7,7)==5183);
static_assert(blockRow(7,80,7)==5183);
static_assert(blockColumn(7,7,80)==5183);
template <typename T,std::size_t K>
std::array<T,K> transpose(const std::array<T,K>& src,std::size_t n) {
  if(n==0 || K!=n*n) throw std::invalid_argument("matrix dimension");
  std::array<T,K> out{};
  for(std::size_t i=0;i<n;++i) for(std::size_t j=0;j<n;++j) out[col(i,j,n)]=src[row(i,j,n)];
  return out;
}
template <typename T>
std::array<T,5184> blockTranspose(const std::array<T,5184>& src) {
 std::array<T,5184> out{};
 for(std::size_t t=0;t<8;++t) for(std::size_t c=0;c<81;++c) for(std::size_t b=0;b<8;++b)
   out[blockColumn(t,b,c)]=src[blockRow(t,c,b)];
 return out;
}
template <typename T>
std::array<T,5184> inverseBlockTranspose(const std::array<T,5184>& src) {
 std::array<T,5184> out{};
 for(std::size_t t=0;t<8;++t) for(std::size_t c=0;c<81;++c) for(std::size_t b=0;b<8;++b)
   out[blockRow(t,c,b)]=src[blockColumn(t,b,c)];
 return out;
}
}
