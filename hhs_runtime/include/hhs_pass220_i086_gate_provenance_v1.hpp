#ifndef HHS_PASS220_I086_GATE_PROVENANCE_V1_HPP
#define HHS_PASS220_I086_GATE_PROVENANCE_V1_HPP
#include "hhs_pass220_i086_ordered_gate_segments_v1.hpp"
#include <cstddef>
#include <cstdint>
#include <string_view>
#include <vector>

namespace hhs::lane5::reciprocal_nesting {
struct GateProvenance final {
  std::size_t ordinal{};
  std::size_t operator_offset{};
  std::size_t lhs_offset{},lhs_size{},rhs_offset{},rhs_size{};
  std::int32_t parent{-1};
  std::uint32_t depth{};
  BoundaryKind operator_kind{};
};
// Candidate provenance only: every retained byte remains governed by native
// Pass219/Lane5 gate semantics, including AB=P^4 and BA=-P^4.
inline std::vector<GateProvenance> derive_gate_provenance(
  std::string_view source, const OrderedBoundaryTree& tree) {
  std::vector<GateProvenance> records;
  if(!validate_ordered_tree(source,tree)) return records;
  const auto segments=gate_segments(source,tree);
  for(const auto& segment:segments) {
    if(segment.lhs_begin>=segment.lhs_end ||
       segment.rhs_begin>=segment.rhs_end ||
       segment.lhs_end!=segment.operator_begin ||
       segment.rhs_begin!=segment.operator_end ||
       segment.rhs_end>source.size()) {
      records.clear();return records;
    }
    records.push_back({records.size(),segment.operator_begin,
      segment.lhs_begin,segment.lhs_end-segment.lhs_begin,
      segment.rhs_begin,segment.rhs_end-segment.rhs_begin,
      segment.parent,segment.depth,segment.kind});
  }
  return records;
}
inline bool validate_gate_provenance(
  std::string_view source, const OrderedBoundaryTree& tree,
  const std::vector<GateProvenance>& records) {
  const auto expected=derive_gate_provenance(source,tree);
  if(!validate_ordered_tree(source,tree) || records.size()!=expected.size())
    return false;
  for(std::size_t i=0;i<expected.size();++i) {
    const auto& a=records[i];const auto& b=expected[i];
    if(a.ordinal!=b.ordinal || a.operator_offset!=b.operator_offset ||
       a.lhs_offset!=b.lhs_offset || a.lhs_size!=b.lhs_size ||
       a.rhs_offset!=b.rhs_offset || a.rhs_size!=b.rhs_size ||
       a.parent!=b.parent || a.depth!=b.depth ||
       a.operator_kind!=b.operator_kind) return false;
  }
  return true;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
