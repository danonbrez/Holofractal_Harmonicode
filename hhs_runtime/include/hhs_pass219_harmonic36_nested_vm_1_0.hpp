#ifndef HHS_PASS219_HARMONIC36_NESTED_VM_1_0_HPP
#define HHS_PASS219_HARMONIC36_NESTED_VM_1_0_HPP

#include "hhs_pass219_harmonic36_nested_vm_1_0.h"

#include <cstdint>
#include <stdexcept>

namespace hhs::rna {

class Harmonic36Word {
public:
    explicit Harmonic36Word(std::uint64_t raw = 0U) : raw_(raw) {
        if ((raw_ & ~HHS_EXACT_PASS219_H36_WORD_MASK) != 0U)
            throw std::out_of_range("Harmonic36 word exceeds 36 bits");
    }

    static Harmonic36Word render(std::uint16_t rule, std::uint8_t tonic) {
        std::uint64_t out = 0U;
        if (hhs_exact_pass219_h36_harmonic_render(rule, tonic, &out) !=
            HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 render failed");
        return Harmonic36Word(out);
    }

    Harmonic36Word transposed(std::uint8_t semitones) const {
        std::uint64_t out = 0U;
        if (hhs_exact_pass219_h36_harmonic_transpose(
                raw_, semitones, &out) != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 transpose failed");
        return Harmonic36Word(out);
    }

    std::uint64_t raw() const noexcept { return raw_; }

private:
    std::uint64_t raw_;
};

class Harmonic36NestedVM {
public:
    Harmonic36NestedVM() {
        if (hhs_exact_pass219_h36_vm_init(&state_) != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 VM init failed");
    }

    HHSExactPass219H36VMStateV1 &state() noexcept { return state_; }
    const HHSExactPass219H36VMStateV1 &state() const noexcept { return state_; }

    void seed_equal_temperament() {
        if (hhs_exact_pass219_h36_equal_temperament_seed(&state_) !=
            HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 ET seed failed");
    }

    void step() {
        if (hhs_exact_pass219_h36_vm_step(&state_) != HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 VM step failed");
    }

    std::uint32_t run(std::uint32_t max_steps) {
        std::uint32_t steps = 0U;
        if (hhs_exact_pass219_h36_vm_run(&state_, max_steps, &steps) !=
            HHS_EXACT_STATUS_OK)
            throw std::runtime_error("Harmonic36 VM run failed");
        return steps;
    }

    static constexpr bool independent_vm81_authority = false;
    static constexpr bool independent_hash72_authority = false;
    static constexpr bool independent_persistence_authority = false;

private:
    HHSExactPass219H36VMStateV1 state_{};
};

} // namespace hhs::rna
#endif
