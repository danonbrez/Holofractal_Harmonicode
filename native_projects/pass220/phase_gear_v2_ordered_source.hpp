#pragma once
// V2 exact-input candidate constructor. No algebraic normalization, no
// canonical serialization, no Hash216 minting or VM81 admission.
#include <array>
#include <cstddef>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace hhs::pass220::v2 {
inline constexpr std::string_view kCanonicalSource = R"HHS_PHASE_GEAR_V2(List(u^f/u^List(-72,0,72)^Mod(MatrixTimes(-180,List(List(16,2,3,13),List(5,11,10,8),List(9,7,6,12),List(4,14,15,1)))/60,72^(-1)),{{5*(x-1),-1,4,-3},{5*(x^2-1),-2,0,2},{5*(y-1),3,-4,1},{0,5*(x-1),5*(x^2-1),5*(y-1)}},List(List(List(y,y,y,0*x*y)/(z*w)==-4,List(y,y,x,1*x*y)/(z*w)==-3,List(y,x,y,10*x*y)/(z*w)==-2,List(y,x,x,11*x*y)/(z*w)==-1),List(List(x,y,y,100*x*y)/(z*w)==1,List(x,y,x,101*x*y)/(z*w)==2,List(x,x,y,110*x*y)/(z*w)==3,List(x,x,x,111*x*y)/(z*w)==4),List(List(w,w,w,0*z*w)/(x*y)==-4,List(w,w,z,1*z*w)/(x*y)==-3,List(w,z,w,10*z*w)/(x*y)==-2,List(w,z,z,11*z*w)/(x*y)==-1),List(List(z,w,w,100*z*w)/(x*y)==1,List(z,w,z,101*z*w)/(x*y)==2,List(z,z,w,110*z*w)/(x*y)==3,List(z,z,z,111*z*w)/(x*y)==4)==x+y-z-w+x*y+x^2-z*w-z^2-y^2+w^2==0),List(x^2-x-1,x^3-x-1,x^4-x^3-1,x^5-x^4-x^3-x^2-1,x^3-x^2-1,x^6-x^5-x^4+x^2-1,x^5-x^3-x^2-x-1,x^7-x^6-x^5+x^2-1,x^6-2*x^5+x^4-x^2-1,x^5-x^4-x^2-1,x^8-x^7-x^6+x^2-1==x+y-z-w+x*y-x^4-z*w+z^4+x^2-y^2+z^2-w^2==c^2-b^2-a^2)/(x^2-x-1+x^3-x-1+x^4-x^3-1+x^5-x^4-x^3-x^2-1+x^3-x^2-1+x^6-x^5-x^4+x^2-1+x^5-x^3-x^2-x-1+x^7-x^6-x^5+x^2-1+x^6-2*x^5+x^4-x^2-1+x^5-x^4-x^2-1+x^8-x^7-x^6+x^2-1==x*(x^7-x^4-x^3-x^2-x-3)-(b^4*c^2-x*y)==0)))HHS_PHASE_GEAR_V2";

struct OrderedGateCircuit {
  std::array<std::string,4> parts;
  std::array<std::size_t,4> gate_count{};
  bool candidate_only{true};
};

inline std::size_t count_gates(std::string_view s) {
  std::size_t count=0;
  for(std::size_t i=1;i<s.size();++i)
    if(s[i-1]=='=' && s[i]=='=') ++count;
  return count;
}

// Operator-safe lexical boundary. It never interprets == as host equality,
// / as division, or address digits as scalar algebra. Local ordering is retained.
inline std::vector<std::string> split_ordered_list(std::string_view input) {
  if(input.size()<6 || input.substr(0,5)!="List(" || input.back()!=')')
    throw std::invalid_argument("expected outer List(...)");
  const auto body=input.substr(5,input.size()-6);
  std::vector<char> stack;
  std::vector<std::string> out;
  std::size_t start=0;
  for(std::size_t i=0;i<body.size();++i) {
    const char ch=body[i];
    if(ch=='(' || ch=='[' || ch=='{') stack.push_back(ch);
    else if(ch==')' || ch==']' || ch=='}') {
      if(stack.empty()) throw std::invalid_argument("unexpected closer");
      const char previous=stack.back(); stack.pop_back();
      if(!((previous=='(' && ch==')') ||
           (previous=='[' && ch==']') ||
           (previous=='{' && ch=='}')))
        throw std::invalid_argument("mismatched closer");
    } else if(ch==',' && stack.empty()) {
      if(i==start) throw std::invalid_argument("empty component");
      out.emplace_back(body.substr(start,i-start));
      start=i+1;
    }
  }
  if(!stack.empty() || start==body.size())
    throw std::invalid_argument("unclosed or empty component");
  out.emplace_back(body.substr(start));
  return out;
}
inline OrderedGateCircuit construct_source_locked(std::string_view source) {
  if(source!=kCanonicalSource)
    throw std::invalid_argument("source mismatch: fail-closed");
  const auto values=split_ordered_list(source);
  if(values.size()!=4) throw std::invalid_argument("four parts required");
  OrderedGateCircuit result{};
  for(std::size_t i=0;i<4;++i) {
    result.parts[i]=values[i];
    result.gate_count[i]=count_gates(values[i]);
  }
  // Current V2 contract: 16 register gates + 2 global gates, and
  // the last polynomial and denominator each carry 2 ordered gates.
  if(result.gate_count!=std::array<std::size_t,4>{{0,0,18,4}})
    throw std::invalid_argument("V2 ordered gate count mismatch");
  return result;
}
} // namespace hhs::pass220::v2
