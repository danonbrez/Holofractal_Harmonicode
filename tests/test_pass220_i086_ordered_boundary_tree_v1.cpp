#include "hhs_pass220_i086_ordered_boundary_tree_v1.hpp"
#include <cassert>
using namespace hhs::lane5::reciprocal_nesting;
int main() {
 const auto tree=parse_ordered_boundaries(kUniversalConstraint);
 assert(validate_ordered_tree(kUniversalConstraint,tree));
 unsigned groups=0,gates=0,equals=0;
 for(const auto& n:tree.nodes) {
  groups+=n.kind==BoundaryKind::Open;
  gates+=n.kind==BoundaryKind::Gate;
  equals+=n.kind==BoundaryKind::Equality;
 }
 assert(groups==16 && gates==7 && equals==1);
 assert(!parse_ordered_boundaries("((A==B)").valid);
 assert(!parse_ordered_boundaries("A)==B").valid);
 const auto nested=parse_ordered_boundaries("(A==(B=C))");
 assert(validate_ordered_tree("(A==(B=C))",nested));
 assert(nested.nodes.size()==4);
 auto altered=nested;altered.nodes[3].parent=0;
 assert(!validate_ordered_tree("(A==(B=C))",altered));
 altered=nested;altered.nodes.erase(altered.nodes.begin()+1);
 assert(!validate_ordered_tree("(A==(B=C))",altered));
}
