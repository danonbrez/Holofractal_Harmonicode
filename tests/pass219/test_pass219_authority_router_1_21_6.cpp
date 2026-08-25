#include "hhs_runtime_exact_abi.h"

#include <cstddef>
#include <cstdint>
#include <type_traits>

static_assert(HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MAJOR == 1U);
static_assert(HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_MINOR == 21U);
static_assert(HHS_EXACT_PASS219_AUTHORITY_ROUTER_VERSION_PATCH == 6U);
static_assert(HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED == 1);
static_assert(HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS191_INHERITED_MANIFOLD <
              HHS_EXACT_PASS219_AUTHORITY_EVIDENCE_PASS169_WHOLE_EXPRESSION);
static_assert(std::is_standard_layout<HHSExactPass219AuthorityEvidenceV1>::value);
static_assert(std::is_standard_layout<HHSExactPass219AuthorityRouteV1>::value);

int main() {
    HHSExactPass219AuthorityRouterDescriptorV1 descriptor{};
    HHSExactPass219AuthorityEvidenceV1 evidence{};
    HHSExactPass219AuthorityRouteV1 route{};
    evidence.struct_size = static_cast<std::uint32_t>(sizeof(evidence));
    evidence.version = hhs_exact_pass219_authority_router_version();
    if (hhs_exact_pass219_authority_router_descriptor(&descriptor) != HHS_EXACT_STATUS_OK)
        return 1;
    if (descriptor.canonical_proven_decision_available != 0U)
        return 2;
    if (hhs_exact_pass219_authority_route_evidence(&evidence, &route) != HHS_EXACT_STATUS_OK)
        return 3;
    if (route.decision != HHS_EXACT_PASS219_AUTHORITY_ROUTE_PASS169_REQUIRED ||
        route.canonical_monolithic_proof != 0U ||
        route.pass169_whole_expression_authority_required != 1U)
        return 4;
    return 0;
}
