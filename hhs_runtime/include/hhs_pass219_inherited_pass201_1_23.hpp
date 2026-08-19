#ifndef HHS_PASS219_INHERITED_PASS201_1_23_HPP
#define HHS_PASS219_INHERITED_PASS201_1_23_HPP

#include "hhs_pass219_inherited_pass201_1_23.h"

#include <type_traits>

namespace hhs::rna {

class InheritedPass201PublicAPIFederation final {
public:
    explicit InheritedPass201PublicAPIFederation(
        const HHSExactPass201PublicAPIFederationWitnessV1& witness
    ) noexcept {
        status_ = hhs_exact_pass219_bind_pass201_public_api_federation(&witness, &binding_);
    }

    HHSExactStatus status() const noexcept { return status_; }
    bool wired() const noexcept {
        return status_ == HHS_EXACT_STATUS_OK &&
               binding_.classification == HHS_EXACT_PASS219_INHERITED_PASS_WIRED &&
               binding_.pass_number == HHS_EXACT_PASS219_INHERITED_PASS201_NUMBER &&
               binding_.historical_squash_identity_bound == 1U &&
               binding_.immutable_source_identity_bound == 1U &&
               binding_.router_closure_bound == 1U &&
               binding_.deterministic_catalog_bound == 1U &&
               binding_.bounded_tool_boundary_bound == 1U &&
               binding_.native_route_authority_preserved_bound == 1U &&
               binding_.pass202_successor_bound == 1U &&
               binding_.no_new_public_execution_authority_bound == 1U &&
               binding_.no_new_canonical_mutation_authority_bound == 1U &&
               binding_.no_new_persistence_authority_bound == 1U &&
               binding_.no_new_hash72_clock_bound == 1U &&
               binding_.pass219_new_public_execution_authority == 0U &&
               binding_.pass219_new_canonical_mutation_authority == 0U &&
               binding_.pass219_new_persistence_authority == 0U &&
               binding_.pass219_new_hash72_clock == 0U &&
               binding_.cxx_mutation_authority == 0U &&
               binding_.vm81_mutation_authority == 0U;
    }

    const HHSExactPass219InheritedPass201BindingV1& record() const noexcept { return binding_; }

private:
    HHSExactPass219InheritedPass201BindingV1 binding_{};
    HHSExactStatus status_{HHS_EXACT_STATUS_INVALID_ARGUMENT};
};

static_assert(std::is_standard_layout_v<HHSExactPass201PublicAPIFederationWitnessV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass201PublicAPIFederationWitnessV1>);
static_assert(std::is_standard_layout_v<HHSExactPass219InheritedPass201BindingV1>);
static_assert(std::is_trivially_copyable_v<HHSExactPass219InheritedPass201BindingV1>);

}  // namespace hhs::rna

#endif
