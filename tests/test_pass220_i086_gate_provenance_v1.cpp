#include "hhs_pass220_i086_gate_provenance_v1.hpp"
#include <cassert>
#include <string_view>
using namespace hhs::lane5::reciprocal_nesting;
int main() {
 const auto tree=parse_ordered_boundaries(kUniversalConstraint);
 const auto records=derive_gate_provenance(kUniversalConstraint,tree);
 assert(records.size()==8);
 assert(validate_gate_provenance(kUniversalConstraint,tree,records));
 unsigned gates=0,equalities=0;
 for(const auto& g:records) {
   gates+=g.operator_kind==BoundaryKind::Gate;
   equalities+=g.operator_kind==BoundaryKind::Equality;
   assert(g.lhs_size>0 && g.rhs_size>0);
   assert(g.lhs_offset+g.lhs_size==g.operator_offset);
 }
 assert(gates==7 && equalities==1);
 auto damaged=records; damaged[0].lhs_offset+=1;
 assert(!validate_gate_provenance(kUniversalConstraint,tree,damaged));
 damaged=records; damaged[0].parent=-1;
 assert(!validate_gate_provenance(kUniversalConstraint,tree,damaged));
 const std::string_view chain="(A==B==C)";
 const auto parts=derive_gate_provenance(chain,parse_ordered_boundaries(chain));
 assert(parts.size()==2);
 assert(chain.substr(parts[0].lhs_offset,parts[0].lhs_size)=="A");
 assert(chain.substr(parts[0].rhs_offset,parts[0].rhs_size)=="B");
 assert(chain.substr(parts[1].lhs_offset,parts[1].lhs_size)=="B");
 assert(chain.substr(parts[1].rhs_offset,parts[1].rhs_size)=="C");
}
