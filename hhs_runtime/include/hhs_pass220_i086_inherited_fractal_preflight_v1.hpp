#ifndef HHS_PASS220_I086_INHERITED_FRACTAL_PREFLIGHT_V1_HPP
#define HHS_PASS220_I086_INHERITED_FRACTAL_PREFLIGHT_V1_HPP

#include "hhs_pass220_i086_gate_provenance_v1.hpp"
#include "hhs_pass220_i086_reciprocal_nesting_address_v1.hpp"
#include "hhs_pass219_hash216_fractal_qudit_admission_1_45.h"

namespace hhs::lane5::reciprocal_nesting {
// Fail-closed candidate preflight. The existing P219 fractal-qudit validator
// remains the only executable authority reached by this helper.
inline bool verify_inherited_fractal_geometry(
    const HHSExactPass219Hash216FractalQuditWitnessV1& witness,
    std::string_view exact_equation,
    const OrderedBoundaryTree& boundary_tree,
    const std::vector<GateProvenance>& gate_records
) {
    if(exact_equation != kUniversalConstraint ||
       !validate_ordered_tree(exact_equation,boundary_tree) ||
       !validate_gate_provenance(exact_equation,boundary_tree,gate_records) ||
       gate_records.size() != 8U)
        return false;
    Address address{};
    return from_flat(witness.local5184,address) &&
           address.hash_row == witness.hash72_major &&
           address.hash_col == witness.hash72_minor &&
           address.qudit == witness.cell81 &&
           witness.operation64 == witness.local5184 / 81U;
}

inline HHSExactStatus preflight_inherited_fractal_witness(
    const HHSExactUQCELInputV1* input,
    const HHSExactPass219Hash216TransitionViewV1* parent,
    const HHSExactPass219Hash216FractalQuditWitnessV1* witness,
    std::string_view exact_equation,
    const OrderedBoundaryTree& boundary_tree,
    const std::vector<GateProvenance>& gate_records
) {
    if(input == nullptr || parent == nullptr || witness == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if(!verify_inherited_fractal_geometry(*witness,exact_equation,
                                          boundary_tree,gate_records))
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return hhs_exact_pass219_hash216_fractal_qudit_witness_validate(
        input,parent,witness);
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
