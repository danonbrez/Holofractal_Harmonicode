#include "hhs_pass220_i086_ordered_gate_segments_v1.hpp"
#include <cassert>
#include <string_view>
using namespace hhs::lane5::reciprocal_nesting;
int main() {
 auto tree=parse_ordered_boundaries(kUniversalConstraint);
 auto segments=gate_segments(kUniversalConstraint,tree);
 assert(segments.size()==8);
 for(const auto& g:segments) {
   assert(g.lhs_begin<g.lhs_end && g.rhs_begin<g.rhs_end);
   assert(g.operator_begin==g.lhs_end && g.operator_end==g.rhs_begin);
 }
 auto simple=parse_ordered_boundaries("(A==B==C)");
 auto parts=gate_segments("(A==B==C)",simple);
 assert(parts.size()==2);
 assert(std::string_view("(A==B==C)").substr(parts[0].lhs_begin,parts[0].lhs_end-parts[0].lhs_begin)=="A");
 assert(std::string_view("(A==B==C)").substr(parts[0].rhs_begin,parts[0].rhs_end-parts[0].rhs_begin)=="B");
 assert(std::string_view("(A==B==C)").substr(parts[1].lhs_begin,parts[1].lhs_end-parts[1].lhs_begin)=="B");
 assert(std::string_view("(A==B==C)").substr(parts[1].rhs_begin,parts[1].rhs_end-parts[1].rhs_begin)=="C");
 auto tampered=simple; tampered.nodes[1].parent=-1;
 assert(gate_segments("(A==B==C)",tampered).empty());
}
