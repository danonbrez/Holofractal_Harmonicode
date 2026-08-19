#include "hhs_pass219_rna_transcription_1_10.hpp"

#include <cstdint>

int main() {
    using namespace hhs::pass219;

    PhaseOperator x(HHS_EXACT_PHASE_X);
    PhaseOperator y(HHS_EXACT_PHASE_Y);
    OrderedPhaseProduct xy(x, y);
    OrderedPhaseProduct yx(y, x);
    if (xy.status() != HHS_EXACT_STATUS_OK || yx.status() != HHS_EXACT_STATUS_OK)
        return 1;
    if (xy.record().ordered_product.ordered_tag == yx.record().ordered_product.ordered_tag)
        return 2;

    TrinaryPhaseGate gate(2U);
    if (gate.status() != HHS_EXACT_STATUS_OK)
        return 3;
    if (gate.identity() != HHS_EXACT_PASS219_TRINARY_YX)
        return 4;

    Hydration5184View hydration(80U, 20, 63U, 242U);
    if (hydration.status() != HHS_EXACT_STATUS_OK)
        return 5;
    if (hydration.trit() != 2U || hydration.slot() != 5183U)
        return 6;

    Hash72TokenView empty_token;
    Hash216TransitionView empty_transition;
    RNAAdmissionView empty_admission;
    if (empty_token.valid() || empty_transition.valid() || empty_admission.valid())
        return 7;

    return 0;
}
