#include "hhs_pass220_i086_universal_constraint_source_v1.hpp"
#include <cassert>
#include <cstddef>
#include <string_view>
using namespace hhs::lane5::reciprocal_nesting;
int main() {
    std::size_t opens=0,closes=0,gates=0,equals=0;
    assert(scan_boundaries(kUniversalConstraint,[&](Boundary b){
        if(b.kind==BoundaryKind::Open) ++opens;
        if(b.kind==BoundaryKind::Close) ++closes;
        if(b.kind==BoundaryKind::Gate) ++gates;
        if(b.kind==BoundaryKind::Equality) ++equals;
        assert(b.byte_offset<kUniversalConstraint.size());
    }));
    assert(opens==closes && gates==7 && equals==1);
    assert(kUniversalConstraint.find("AB/-P⁴=")!=std::string_view::npos);
    assert(kUniversalConstraint.find("P⁴/-BA==u(-³⁶)/yx==u⁷²/xy")!=std::string_view::npos);
    assert(kUniversalConstraint.find("(p/q)(q/p)")!=std::string_view::npos);
    assert(!scan_boundaries("(A==B",[](Boundary){}));
    assert(!scan_boundaries("A)==B",[](Boundary){}));
}
