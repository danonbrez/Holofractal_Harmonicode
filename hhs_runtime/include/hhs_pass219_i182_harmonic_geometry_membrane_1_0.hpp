#ifndef HHS_PASS219_I182_HARMONIC_GEOMETRY_MEMBRANE_1_0_HPP
#define HHS_PASS219_I182_HARMONIC_GEOMETRY_MEMBRANE_1_0_HPP

#include "hhs_pass219_i182_harmonic_geometry_membrane_1_0.h"

#include <type_traits>

namespace hhs::rna {

class I182HarmonicGeometryMembrane final {
public:
    I182HarmonicGeometryMembrane() noexcept {
        status_ = hhs_exact_pass219_i182_geometry_membrane_build(&witness_);
    }

    explicit I182HarmonicGeometryMembrane(
        const HHSExactPass219I182GeometryMembraneWitnessV1& witness
    ) noexcept : witness_(witness) {
        status_ = hhs_exact_pass219_i182_geometry_membrane_validate(&witness_);
    }

    HHSExactStatus status() const noexcept { return status_; }

    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               witness_.factorization_conservation == 1U &&
               witness_.all_platonic_closures_valid == 1U &&
               witness_.dodecahedral_closure_valid == 1U &&
               witness_.canonical_integer_authority == 1U &&
               witness_.canonical_float_authority == 0U &&
               witness_.authoritative_vertex_table_used == 0U;
    }

    bool singleton_vm81_authority_preserved() const noexcept {
        return wired() &&
               witness_.singleton_vm81_authority_preserved == 1U &&
               witness_.vm81_authority_minted == 0U &&
               witness_.vm81_direct_mutation_authority == 0U &&
               witness_.hash72_authority_minted == 0U &&
               witness_.hash216_persistence_authority == 0U &&
               witness_.cxx_mutation_authority == 0U &&
               witness_.public_operation_authority == 0U &&
               witness_.capability_binding_authority == 0U &&
               witness_.rendering_authority == 0U;
    }

    const HHSExactPass219I182GeometryMembraneWitnessV1& record() const noexcept {
        return witness_;
    }

private:
    HHSExactPass219I182GeometryMembraneWitnessV1 witness_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass219I182GeometryFactorWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219I182GeometryFactorWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219I182PentagonalWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219I182PentagonalWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219I182PlatonicClosureV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219I182PlatonicClosureV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219I182GeometryMembraneWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219I182GeometryMembraneWitnessV1>);

}  // namespace hhs::rna

#endif
