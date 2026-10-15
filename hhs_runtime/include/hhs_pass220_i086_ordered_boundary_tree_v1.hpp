#ifndef HHS_PASS220_I086_ORDERED_BOUNDARY_TREE_V1_HPP
#define HHS_PASS220_I086_ORDERED_BOUNDARY_TREE_V1_HPP
#include "hhs_pass220_i086_universal_constraint_source_v1.hpp"
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>
namespace hhs::lane5::reciprocal_nesting {
struct OrderedBoundaryNode final { BoundaryKind kind{}; std::size_t begin{},end{}; std::uint32_t depth{}; std::int32_t parent{-1}; };
struct OrderedBoundaryTree final { std::vector<OrderedBoundaryNode> nodes; bool valid{}; };
inline OrderedBoundaryTree parse_ordered_boundaries(std::string_view source) {
 OrderedBoundaryTree result; std::vector<std::size_t> stack;
 for(std::size_t i=0;i<source.size();++i) {
  const auto parent=stack.empty()?-1:static_cast<std::int32_t>(stack.back());
  if(source[i]=='(') {
   const auto index=result.nodes.size();
   result.nodes.push_back({BoundaryKind::Open,i,0,static_cast<std::uint32_t>(stack.size()),parent});
   stack.push_back(index);
  } else if(source[i]==')') {
   if(stack.empty()) return result;
   result.nodes[stack.back()].end=i+1;stack.pop_back();
  } else if(source[i]=='=') {
   const bool gate=i+1<source.size() && source[i+1]=='=';
   result.nodes.push_back({gate?BoundaryKind::Gate:BoundaryKind::Equality,i,i+(gate?2U:1U),static_cast<std::uint32_t>(stack.size()),parent});
   if(gate) ++i;
  }
 }
 result.valid=stack.empty();return result;
}
inline bool validate_ordered_tree(std::string_view source,const OrderedBoundaryTree& candidate) {
 if(!candidate.valid) return false;
 const auto expected=parse_ordered_boundaries(source);
 if(!expected.valid || expected.nodes.size()!=candidate.nodes.size()) return false;
 for(std::size_t i=0;i<expected.nodes.size();++i) {
  const auto& a=expected.nodes[i];const auto& b=candidate.nodes[i];
  if(a.kind!=b.kind || a.begin!=b.begin || a.end!=b.end || a.depth!=b.depth || a.parent!=b.parent) return false;
 }
 return true;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
