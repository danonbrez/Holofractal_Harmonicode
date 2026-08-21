#ifndef HHS_PASS219_HARMONICODE_GLOBAL_CONSTRAINT_MEMBRANE_1_21_9_HPP
#define HHS_PASS219_HARMONICODE_GLOBAL_CONSTRAINT_MEMBRANE_1_21_9_HPP

#include "hhs_pass219_harmonicode_global_constraint_membrane_1_21_9.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace hhs::harmonicode {

class GlobalConstraintMembrane final {
public:
    static constexpr std::size_t kGateCount =
        HHS_EXACT_PASS219_GLOBAL_MEMBRANE_BOOLEAN_GATE_COUNT;
    static constexpr std::size_t kRootBytes =
        HHS_EXACT_PASS219_GLOBAL_MEMBRANE_SHA256_BYTES;

    using GateTruth = std::array<bool, kGateCount>;
    using EnvironmentRoot = std::array<std::uint8_t, kRootBytes>;

    struct Evaluation final {
        HHSExactStatus status{HHS_EXACT_STATUS_INVARIANT_FAILURE};
        HHSExactPass219GlobalMembraneResultV1 result{};

        [[nodiscard]] bool propagated() const noexcept {
            return status == HHS_EXACT_STATUS_OK &&
                   result.decision == HHS_EXACT_PASS219_GLOBAL_MEMBRANE_PROPAGATE &&
                   result.whole_equation_propagated != 0U;
        }
    };

    [[nodiscard]] static HHSExactPass219GlobalMembraneDescriptorV1 descriptor() noexcept {
        HHSExactPass219GlobalMembraneDescriptorV1 value{};
        if (hhs_exact_pass219_global_membrane_descriptor(&value) != HHS_EXACT_STATUS_OK)
            return {};
        return value;
    }

    [[nodiscard]] static Evaluation evaluate(
        const GateTruth &gate_truth,
        const EnvironmentRoot &environment_root,
        bool global_environment_complete,
        bool cross_layer_revalidation_complete,
        bool local_symbol_shadowing_detected = false
    ) noexcept {
        static constexpr std::array<std::uint32_t, kGateCount> kGateOffsets{
            90U, 234U, 260U, 268U, 279U
        };

        Evaluation evaluation{};
        HHSExactPass219GlobalMembraneInputV1 input{};
        const auto source_descriptor = descriptor();

        if (source_descriptor.struct_size != sizeof(source_descriptor))
            return evaluation;

        input.struct_size = static_cast<std::uint32_t>(sizeof(input));
        input.version = hhs_exact_pass219_global_membrane_version();
        std::memcpy(input.combined_source_sha256,
                    source_descriptor.combined_source_sha256,
                    kRootBytes);
        std::memcpy(input.global_symbol_environment_root,
                    environment_root.data(),
                    kRootBytes);
        input.gate_count = static_cast<std::uint32_t>(kGateCount);
        input.global_symbol_environment_complete = global_environment_complete ? 1U : 0U;
        input.cross_layer_revalidation_complete =
            cross_layer_revalidation_complete ? 1U : 0U;
        input.local_symbol_shadowing_detected = local_symbol_shadowing_detected ? 1U : 0U;

        for (std::size_t i = 0; i < kGateCount; ++i) {
            auto &gate = input.gates[i];
            gate.struct_size = static_cast<std::uint32_t>(sizeof(gate));
            gate.version = input.version;
            gate.gate_index = static_cast<std::uint32_t>(i);
            gate.source_offset = kGateOffsets[i];
            gate.boolean_result = gate_truth[i] ? 1U : 0U;
            std::memcpy(gate.combined_source_sha256,
                        input.combined_source_sha256,
                        kRootBytes);
            std::memcpy(gate.global_symbol_environment_root,
                        input.global_symbol_environment_root,
                        kRootBytes);
        }

        evaluation.status =
            hhs_exact_pass219_global_membrane_evaluate(&input, &evaluation.result);
        return evaluation;
    }
};

}  // namespace hhs::harmonicode

#endif