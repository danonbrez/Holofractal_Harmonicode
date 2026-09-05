#ifndef HHS_PASS219_INHERITED_PASS185_1_41_HPP
#define HHS_PASS219_INHERITED_PASS185_1_41_HPP
#include "hhs_pass219_inherited_pass185_1_41.h"
namespace hhs::rna {
class InheritedPass185ProductionClosure final {
public:
    static constexpr bool candidate_authority() noexcept { return false; }
    static constexpr bool mutation_authority() noexcept { return false; }
    static constexpr bool persistence_authority() noexcept { return false; }
    static constexpr bool hash72_clock_authority() noexcept { return false; }
    static constexpr bool vm81_mutation_authority() noexcept { return false; }
    static constexpr bool frontend_mutation_authority() noexcept { return false; }
    static constexpr bool cumulative_local_closure_is_evidence() noexcept { return true; }
    static HHSExactStatus bind(const HHSExactPass185CumulativeClosureWitnessV1 &witness,
                               HHSExactPass219InheritedPass185BindingV1 &binding) noexcept {
        return hhs_exact_pass219_bind_pass185_cumulative_closure(&witness, &binding);
    }
};
}
#endif
