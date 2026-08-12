#include "hhs_pass219_ethical_scope_membrane.hpp"
#include "hhs_pass219_ethical_scope_membrane_c.h"

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <string>
#include <utility>
#include <vector>

namespace hhs::pass219::ethical {
namespace {

bool contains(const std::vector<std::string>& values, const std::string& value) {
    return std::find(values.begin(), values.end(), value) != values.end();
}

std::vector<std::string> ordered_unique(const std::vector<std::string>& values) {
    std::vector<std::string> out;
    out.reserve(values.size());
    for (const auto& value : values) {
        if (value.empty() || contains(out, value)) {
            continue;
        }
        out.push_back(value);
    }
    return out;
}

InvariantState normalize_state(InvariantState state) noexcept {
    switch (state) {
        case InvariantState::Pass:
        case InvariantState::Fail:
        case InvariantState::Unresolved:
            return state;
    }
    return InvariantState::Unresolved;
}

}  // namespace

const std::array<const char*, kInvariantCount>& invariant_ids() noexcept {
    static constexpr std::array<const char*, kInvariantCount> ids = {
        "E01_INTENTION_ALIGNMENT",
        "E02_EPISTEMIC_ADEQUACY",
        "E03_METHOD_ALIGNMENT",
        "E04_ACTION_ALIGNMENT",
        "E05_CONSEQUENCE_ALIGNMENT",
        "E06_EXTERNALITY_CLOSURE",
        "E07_CONSENT_VALIDITY",
        "E08_AUTONOMY_PRESERVATION",
        "E09_NONCOERCION",
        "E10_TRUTH_MODALITY_INTEGRITY",
        "E11_SCOPE_LOCALITY",
        "E12_REVOCABILITY_AND_EXPIRY",
        "E13_DEPENDENCY_DUTY_INTEGRITY",
        "E14_NO_PREDICTION_TO_AUTHORITY",
        "E15_NO_CONSENSUS_TO_AUTHORITY",
        "E16_POST_ACTION_MODEL_CORRECTION",
        "E17_REPAIR_ROLLBACK_ADEQUACY",
        "E18_SAFETY_RECURSION_NO_SELF_GRANT",
    };
    return ids;
}

std::array<InvariantState, kInvariantCount> all_pass_states() noexcept {
    std::array<InvariantState, kInvariantCount> states{};
    states.fill(InvariantState::Pass);
    return states;
}

ScopePreflight preflight_scope(const EvaluationInput& input) {
    ScopePreflight out;
    const auto requested = ordered_unique(input.requested_scope);
    const auto minimum = ordered_unique(input.minimum_necessary_scope);
    const auto granted = ordered_unique(input.granted_scope);
    const auto revoked = ordered_unique(input.revoked_or_expired_scope);

    for (const auto& scope : granted) {
        if (!contains(revoked, scope)) {
            out.active_authority_scope.push_back(scope);
        }
    }

    for (const auto& scope : minimum) {
        const bool was_requested = contains(requested, scope);
        const bool is_authorized = contains(out.active_authority_scope, scope);
        if (!was_requested) {
            out.missing_requested_scope.push_back(scope);
        }
        if (!is_authorized) {
            out.missing_authority_scope.push_back(scope);
        }
        if (was_requested && is_authorized) {
            out.effective_scope.push_back(scope);
        }
    }

    for (const auto& scope : requested) {
        if (!contains(minimum, scope)) {
            out.extra_requested_scope.push_back(scope);
        }
    }

    return out;
}

Evaluation evaluate(const EvaluationInput& input) {
    Evaluation out;
    out.scope = preflight_scope(input);
    out.divergence = input.divergence;
    out.responsibility = input.responsibility;

    for (std::size_t i = 0; i < kInvariantCount; ++i) {
        const InvariantState state = normalize_state(input.invariant_states[i]);
        if (state == InvariantState::Fail) {
            out.failed_invariant_indexes.push_back(i);
        } else if (state == InvariantState::Unresolved) {
            out.unresolved_invariant_indexes.push_back(i);
        }
    }

    const bool scope_valid =
        out.scope.missing_requested_scope.empty() &&
        out.scope.missing_authority_scope.empty() &&
        out.scope.extra_requested_scope.empty();

    out.prospective_alignment =
        scope_valid &&
        out.failed_invariant_indexes.empty() &&
        out.unresolved_invariant_indexes.empty();

    if (!out.scope.missing_requested_scope.empty()) {
        out.decision = EthicalDecision::Hold;
        return out;
    }
    if (!out.scope.missing_authority_scope.empty()) {
        out.decision = EthicalDecision::RequireAdditionalAuthority;
        return out;
    }
    if (!out.scope.extra_requested_scope.empty()) {
        out.decision = EthicalDecision::NarrowAndResimulate;
        return out;
    }

    if (input.phase == EvaluationPhase::Prospective) {
        out.good_closed = false;
        if (!out.failed_invariant_indexes.empty()) {
            out.decision = EthicalDecision::Deny;
        } else if (!out.unresolved_invariant_indexes.empty()) {
            out.decision = EthicalDecision::SimulateOnly;
        } else {
            out.decision = EthicalDecision::ExecuteLocalProvisional;
        }
        return out;
    }

    if (!out.failed_invariant_indexes.empty()) {
        out.decision = EthicalDecision::RepairOrRollback;
        out.good_closed = false;
    } else if (!out.unresolved_invariant_indexes.empty()) {
        out.decision = EthicalDecision::Hold;
        out.good_closed = false;
    } else {
        out.decision = EthicalDecision::CloseGood;
        out.good_closed = true;
    }
    return out;
}

}  // namespace hhs::pass219::ethical

namespace {

using hhs::pass219::ethical::EthicalDecision;
using hhs::pass219::ethical::EvaluationPhase;
using hhs::pass219::ethical::InvariantState;

bool mask_any(const hhs_p219_scope_mask_v1& mask) noexcept {
    for (std::size_t i = 0; i < HHS_P219_SCOPE_WORD_COUNT; ++i) {
        if (mask.words[i] != 0u) {
            return true;
        }
    }
    return false;
}

hhs_p219_scope_mask_v1 mask_and(
    const hhs_p219_scope_mask_v1& a,
    const hhs_p219_scope_mask_v1& b
) noexcept {
    hhs_p219_scope_mask_v1 out{};
    for (std::size_t i = 0; i < HHS_P219_SCOPE_WORD_COUNT; ++i) {
        out.words[i] = a.words[i] & b.words[i];
    }
    return out;
}

hhs_p219_scope_mask_v1 mask_and_not(
    const hhs_p219_scope_mask_v1& a,
    const hhs_p219_scope_mask_v1& b
) noexcept {
    hhs_p219_scope_mask_v1 out{};
    for (std::size_t i = 0; i < HHS_P219_SCOPE_WORD_COUNT; ++i) {
        out.words[i] = a.words[i] & ~b.words[i];
    }
    return out;
}

uint8_t decision_code(EthicalDecision decision) noexcept {
    return static_cast<uint8_t>(decision);
}

InvariantState decode_state(uint8_t value) noexcept {
    switch (value) {
        case HHS_P219_INVARIANT_PASS:
            return InvariantState::Pass;
        case HHS_P219_INVARIANT_FAIL:
            return InvariantState::Fail;
        case HHS_P219_INVARIANT_UNRESOLVED:
            return InvariantState::Unresolved;
        default:
            return InvariantState::Unresolved;
    }
}

}  // namespace

extern "C" int hhs_p219_ethical_evaluate_v1(
    const hhs_p219_ethical_eval_input_v1* input,
    hhs_p219_ethical_eval_output_v1* output
) {
    if (input == nullptr || output == nullptr) {
        return -1;
    }

    *output = hhs_p219_ethical_eval_output_v1{};

    output->active_authority_scope = mask_and_not(
        input->granted_scope,
        input->revoked_or_expired_scope
    );
    output->missing_requested_scope = mask_and_not(
        input->minimum_necessary_scope,
        input->requested_scope
    );
    output->missing_authority_scope = mask_and_not(
        input->minimum_necessary_scope,
        output->active_authority_scope
    );
    output->extra_requested_scope = mask_and_not(
        input->requested_scope,
        input->minimum_necessary_scope
    );
    output->effective_scope = mask_and(
        mask_and(input->minimum_necessary_scope, input->requested_scope),
        output->active_authority_scope
    );

    for (std::size_t i = 0; i < HHS_P219_ETHICAL_INVARIANT_COUNT; ++i) {
        const InvariantState state = decode_state(input->invariant_states[i]);
        if (state == InvariantState::Fail) {
            ++output->failed_invariant_count;
        } else if (state == InvariantState::Unresolved) {
            ++output->unresolved_invariant_count;
        }
    }

    if (mask_any(output->missing_requested_scope)) {
        output->decision = decision_code(EthicalDecision::Hold);
        return 0;
    }
    if (mask_any(output->missing_authority_scope)) {
        output->decision = decision_code(EthicalDecision::RequireAdditionalAuthority);
        return 0;
    }
    if (mask_any(output->extra_requested_scope)) {
        output->decision = decision_code(EthicalDecision::NarrowAndResimulate);
        return 0;
    }

    output->prospective_alignment =
        (output->failed_invariant_count == 0u &&
         output->unresolved_invariant_count == 0u)
            ? 1u
            : 0u;

    const EvaluationPhase phase =
        input->phase == HHS_P219_PHASE_POST_ACTION
            ? EvaluationPhase::PostAction
            : EvaluationPhase::Prospective;

    if (phase == EvaluationPhase::Prospective) {
        output->good_closed = 0u;
        if (output->failed_invariant_count != 0u) {
            output->decision = decision_code(EthicalDecision::Deny);
        } else if (output->unresolved_invariant_count != 0u) {
            output->decision = decision_code(EthicalDecision::SimulateOnly);
        } else {
            output->decision = decision_code(EthicalDecision::ExecuteLocalProvisional);
        }
        return 0;
    }

    if (output->failed_invariant_count != 0u) {
        output->decision = decision_code(EthicalDecision::RepairOrRollback);
        output->good_closed = 0u;
    } else if (output->unresolved_invariant_count != 0u) {
        output->decision = decision_code(EthicalDecision::Hold);
        output->good_closed = 0u;
    } else {
        output->decision = decision_code(EthicalDecision::CloseGood);
        output->good_closed = 1u;
    }
    return 0;
}
