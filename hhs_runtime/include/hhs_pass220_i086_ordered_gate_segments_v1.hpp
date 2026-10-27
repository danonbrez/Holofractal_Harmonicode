#ifndef HHS_PASS220_I086_ORDERED_GATE_SEGMENTS_V1_HPP
#define HHS_PASS220_I086_ORDERED_GATE_SEGMENTS_V1_HPP
#include "hhs_pass220_i086_ordered_boundary_tree_v1.hpp"
#include <string_view>
#include <vector>
namespace hhs::lane5::reciprocal_nesting {
struct GateSegment final {
  std::size_t operator_begin{}, operator_end{};
  std::size_t lhs_begin{},lhs_end{},rhs_begin{},rhs_end{};
  BoundaryKind kind{};
  std::int32_t parent{-1};
  std::uint32_t depth{};
};
// Source-ordered adjacent operands of each equality in a chain. The parser
// does not assert transitive equality, commute operands, or evaluate gates.
inline std::vector<GateSegment> gate_segments(std::string_view source,
                                             const OrderedBoundaryTree& tree) {
  std::vector<GateSegment> out;
  if(!validate_ordered_tree(source,tree)) return out;
  for(std::size_t i=0;i<tree.nodes.size();++i) {
    const auto& node=tree.nodes[i];
    if(node.kind!=BoundaryKind::Equality && node.kind!=BoundaryKind::Gate) continue;
    std::size_t lo=0,hi=source.size();
    if(node.parent>=0) {
      const auto& parent=tree.nodes[static_cast<std::size_t>(node.parent)];
      lo=parent.begin+1; hi=parent.end-1;
    }
    // Find the immediately adjacent operators at the same nesting level.
    for(std::size_t j=0;j<tree.nodes.size();++j) {
      const auto& other=tree.nodes[j];
      if(j==i || other.parent!=node.parent ||
         (other.kind!=BoundaryKind::Equality && other.kind!=BoundaryKind::Gate)) continue;
      if(other.end<=node.begin && other.end>lo) lo=other.end;
      if(other.begin>=node.end && other.begin<hi) hi=other.begin;
    }
    if(lo>=node.begin || hi<=node.end) {out.clear();return out;}
    out.push_back({node.begin,node.end,lo,node.begin,node.end,hi,node.kind,node.parent,node.depth});
  }
  return out;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
