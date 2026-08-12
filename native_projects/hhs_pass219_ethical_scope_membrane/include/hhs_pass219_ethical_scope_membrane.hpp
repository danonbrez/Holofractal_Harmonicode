#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace hhs::pass219::ethical {

inline constexpr std::size_t kInvariantCount = 18;
inline constexpr std::size_t kDivergenceCount = 10;
inline constexpr std::size_t kResponsibilityCount = 10;

enum class InvariantState : std::uint8_t {
    Pass = 1,
    Fail = 2,
    Unresolved = 3,
};

enum class EvaluationPhase : std::uint8_t {
    Prospective = 0,
    PostAction = 1,
};

enum class EthicalDecision : std::uint8_t {
    ExecuteLocalProvisional = 1,
    NarrowAndResimulate = 2,
    SimulateOnly = 3,
    Hold = 4,
    Deny = 5,
    RequireAdditionalAuthority = 6,
    CloseGood = 7,
    RepairOrRollback = 8,
};

struct EthicalDivergenceVector final {
    std::array<std::uint8_t, kDivergenceCount> values{};
};

struct ResponsibilityVector final {
    std::array<std::uint8_t, kResponsibilityCount> values{};
};

struct EvaluationInput final {
    EvaluationPhase phase{EvaluationPhase::Prospective};
    std::vector<std::string> requested_scope{};
    std::vector<std::string> minimum_necessary_scope{};
    std::vector<std::string> granted_scope{};
    std::vector<std::string> revoked_or_expired_scope{};
    std::array<InvariantState, kInvariantCount> invariant_states{};
    EthicalDivergenceVector divergence{};
    ResponsibilityVector responsibility{};
};

struct ScopePreflight final {
    std::vector<std::string> active_authority_scope{};
    std::vector<std::string> effective_scope{};
    std::vector<std::string> missing_requested_scope{};
    std::vector<std::string> missing_authority_scope{};
    std::vector<std::string> extra_requested_scope{};
};

struct Evaluation final {
    EthicalDecision decision{EthicalDecision::SimulateOnly};
    bool prospective_alignment{false};
    bool good_closed{false};
    ScopePreflight scope{};
    std::vector<std::size_t> failed_invariant_indexes{};
    std::vector<std::size_t> unresolved_invariant_indexes{};
    EthicalDivergenceVector divergence{};
    ResponsibilityVector responsibility{};
};

[[nodiscard]] const std::array<const char*, kInvariantCount>& invariant_ids() noexcept;

[[nodiscard]] std::array<InvariantState, kInvariantCount> all_pass_states() noexcept;

[[nodiscard]] ScopePreflight preflight_scope(const EvaluationInput& input);

[[nodiscard]] Evaluation evaluate(const EvaluationInput& input);

}  // namespace hhs::pass219::ethical
