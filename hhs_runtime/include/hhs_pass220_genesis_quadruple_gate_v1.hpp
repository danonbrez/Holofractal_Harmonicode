#pragma once
// Pass 220 Module 29/30 exact candidate arithmetic: never admits or mints state.
#include <boost/multiprecision/cpp_int.hpp>
#include <stdexcept>
#include <string>
namespace hhs::pass220::quadruple {
using Big = boost::multiprecision::cpp_int;
struct Exact {
  Big num,den;
  Exact(Big n=0,Big d=1):num(n),den(d) {
    if(d==0) throw std::invalid_argument("zero denominator");
    if(den<0){num=-num;den=-den;}
  }
};
inline Big pow(Big x,unsigned n) {
  Big result=1;for(;n;n>>=1,x*=x)if(n&1)result*=x;return result;
}
inline bool nonzero(const Exact& x){return x.num!=0;}
inline Exact multiply(const Exact& a,const Exact& b){return {a.num*b.num,a.den*b.den};}
inline Exact inverse(const Exact& a){if(!nonzero(a)) throw std::invalid_argument("zero inverse");return {a.den,a.num};}
inline Exact power(const Exact& a,unsigned n){return {pow(a.num,n),pow(a.den,n)};}
inline bool equal(const Exact& a,const Exact& b){return a.num*b.den==b.num*a.den;}
enum class GateStatus {CandidateClosed, CandidateRejected, Undefined};
struct GateWitness {
  GateStatus status;
  // The branch phase is a 72-root exponent; quarter turns 0,18,36,54.
  unsigned branchPhase72;
};
inline GateWitness verify(const Exact& x,const Exact& y,const Exact& z,const Exact& w,
                         unsigned branchPhase72) {
  if(branchPhase72!=0&&branchPhase72!=18&&branchPhase72!=36&&branchPhase72!=54)
    return {GateStatus::Undefined,branchPhase72};
  if(!nonzero(y)||!nonzero(z)||!nonzero(w))return {GateStatus::Undefined,branchPhase72};
  // x^4 (zw)^3 = y^2: exact denominator-safe check.
  const Exact lhs=multiply(power(x,4),power(multiply(z,w),3));
  const Exact rhs=power(y,2);
  return {equal(lhs,rhs)?GateStatus::CandidateClosed:GateStatus::CandidateRejected,branchPhase72};
}
constexpr unsigned phaseOpposite(unsigned p){return (p+36u)%72u;}
static_assert(phaseOpposite(18)==54 && phaseOpposite(0)==36);
constexpr bool factorCounts(){return 16*18*18==5184 && 81*64==5184 && 72*72==5184;}
static_assert(factorCounts());
}
