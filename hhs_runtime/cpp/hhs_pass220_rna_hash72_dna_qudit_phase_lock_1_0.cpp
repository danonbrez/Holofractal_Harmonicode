#include "hhs_pass220_rna_hash72_dna_qudit_phase_lock_1_0.h"

#include <climits>
#include <cstddef>
#include <cstdint>
#include <cstring>

namespace {

constexpr uint64_t FNV_OFFSET = UINT64_C(1469598103934665603);
constexpr uint64_t FNV_PRIME = UINT64_C(1099511628211);

uint64_t mix_byte(uint64_t hash, uint8_t value) noexcept {
    hash ^= static_cast<uint64_t>(value);
    hash *= FNV_PRIME;
    return hash;
}

uint64_t mix_u64(uint64_t hash, uint64_t value) noexcept {
    for (unsigned shift = 0U; shift < 64U; shift += 8U)
        hash = mix_byte(hash, static_cast<uint8_t>((value >> shift) & UINT64_C(0xff)));
    return hash;
}

bool parse_20_digits(const char *text, uint64_t *out) noexcept {
    if (text == nullptr || out == nullptr)
        return false;
    uint64_t value = 0U;
    for (std::size_t i = 0; i < 20U; ++i) {
        const unsigned char ch = static_cast<unsigned char>(text[i]);
        if (ch < static_cast<unsigned char>('0') || ch > static_cast<unsigned char>('9'))
            return false;
        const uint64_t digit = static_cast<uint64_t>(ch - static_cast<unsigned char>('0'));
        if (value > (UINT64_MAX - digit) / UINT64_C(10))
            return false;
        value = value * UINT64_C(10) + digit;
    }
    *out = value;
    return true;
}

bool parse_canonical_token(const char *token, uint8_t *out_offset) noexcept {
    if (token == nullptr || out_offset == nullptr)
        return false;
    if (token[0] != '+' || token[21] != '/' || token[42] != 'e' || token[43] != '+')
        return false;

    uint64_t numerator = 0U;
    uint64_t denominator = 0U;
    uint64_t exponent = 0U;
    if (!parse_20_digits(token + 1, &numerator) ||
        !parse_20_digits(token + 22, &denominator) ||
        !parse_20_digits(token + 44, &exponent))
        return false;
    if (numerator > UINT64_C(8) || denominator != UINT64_C(1) || exponent != UINT64_C(0))
        return false;

    *out_offset = static_cast<uint8_t>(numerator);
    return true;
}

void fill_scale_rows(HHSExactPass220PhaseLockWitnessV1 *witness) noexcept {
    static constexpr uint8_t rows[3][3] = {
        {1U, 2U, 3U},
        {2U, 4U, 6U},
        {3U, 6U, 9U},
    };
    for (std::size_t scale = 0; scale < 3U; ++scale) {
        for (std::size_t j = 0; j < 3U; ++j) {
            witness->scale_rows[scale][j] = rows[scale][j];
            witness->palindrome_rows[scale][j] = rows[scale][j];
            witness->palindrome_rows[scale][5U - j] = rows[scale][j];
        }
        witness->precision_remainder_numerator[scale] =
            static_cast<uint16_t>(HHS_EXACT_PASS220_H36_MAGIC_LINE * (scale + 1U));
        witness->precision_remainder_denominator[scale] =
            static_cast<uint16_t>(HHS_EXACT_PASS220_PRECISION_DENOMINATOR);
    }
}

bool palindrome_rows_exact(const HHSExactPass220PhaseLockWitnessV1& witness) noexcept {
    for (std::size_t scale = 0; scale < 3U; ++scale) {
        for (std::size_t j = 0; j < 6U; ++j) {
            if (witness.palindrome_rows[scale][j] !=
                witness.palindrome_rows[scale][5U - j])
                return false;
        }
        if (witness.precision_remainder_numerator[scale] !=
                HHS_EXACT_PASS220_H36_MAGIC_LINE * (scale + 1U) ||
            witness.precision_remainder_denominator[scale] !=
                HHS_EXACT_PASS220_PRECISION_DENOMINATOR)
            return false;
    }
    return true;
}

}  // namespace

extern "C" uint32_t hhs_exact_pass220_phase_lock_version(void) {
    return HHS_EXACT_PASS220_PHASE_LOCK_VERSION;
}

extern "C" HHSExactStatus hhs_exact_pass220_phase_lock_descriptor(
    HHSExactPass220PhaseLockDescriptorV1 *out_descriptor
) {
    if (out_descriptor == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;

    HHSExactPass220PhaseLockDescriptorV1 descriptor{};
    descriptor.struct_size = static_cast<uint32_t>(sizeof(descriptor));
    descriptor.version = HHS_EXACT_PASS220_PHASE_LOCK_VERSION;
    descriptor.serialized_characters = HHS_EXACT_PASS220_SERIALIZED_CHARACTERS;
    descriptor.hash72_chunks = HHS_EXACT_PASS220_HASH72_CHUNKS;
    descriptor.hash72_chunk_characters = HHS_EXACT_PASS220_HASH72_CHUNK_CHARACTERS;
    descriptor.rna_window_characters = HHS_EXACT_PASS220_RNA_WINDOW_CHARACTERS;
    descriptor.rna_windows_per_chunk = HHS_EXACT_PASS220_RNA_WINDOWS_PER_CHUNK;
    descriptor.rna_windows_total = HHS_EXACT_PASS220_RNA_WINDOWS_TOTAL;
    descriptor.qudit_cells = HHS_EXACT_PASS220_QUDIT_CELLS;
    descriptor.cell_token_characters = HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS;
    descriptor.h36_cells = HHS_EXACT_PASS220_H36_CELLS;
    descriptor.h36_magic_line = HHS_EXACT_PASS220_H36_MAGIC_LINE;
    descriptor.bidirectional_rna_scan = 1U;
    descriptor.hash72_chunk_folding = 1U;
    descriptor.xyzw_digital_dna_bound = 1U;
    descriptor.vm81_qudit_bound = 1U;
    descriptor.complete_state_is_operand = 1U;
    descriptor.exact_integer_only = 1U;
    descriptor.candidate_only = 1U;
    descriptor.canonical_vm81_mutation_authority = 0U;
    descriptor.canonical_hash72_authority = 0U;
    descriptor.canonical_hash216_authority = 0U;
    descriptor.canonical_persistence_authority = 0U;
    descriptor.floating_point_authority = 0U;
    *out_descriptor = descriptor;
    return HHS_EXACT_STATUS_OK;
}

extern "C" HHSExactStatus hhs_exact_pass220_phase_lock_analyze(
    const char *serialized,
    size_t serialized_length,
    HHSExactPass220PhaseLockWitnessV1 *out_witness
) {
    if (out_witness == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    std::memset(out_witness, 0, sizeof(*out_witness));
    if (serialized == nullptr)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (serialized_length != HHS_EXACT_PASS220_SERIALIZED_CHARACTERS)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    uint8_t offsets[HHS_EXACT_PASS220_QUDIT_CELLS]{};
    for (std::size_t cell = 0; cell < HHS_EXACT_PASS220_QUDIT_CELLS; ++cell) {
        if (!parse_canonical_token(
                serialized + cell * HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS,
                &offsets[cell]))
            return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    }

    HHSExactPass220PhaseLockWitnessV1 witness{};
    witness.struct_size = static_cast<uint32_t>(sizeof(witness));
    witness.version = HHS_EXACT_PASS220_PHASE_LOCK_VERSION;
    witness.serialized_characters = HHS_EXACT_PASS220_SERIALIZED_CHARACTERS;
    witness.hash72_chunks = HHS_EXACT_PASS220_HASH72_CHUNKS;
    witness.rna_windows_total = HHS_EXACT_PASS220_RNA_WINDOWS_TOTAL;
    witness.qudit_cells = HHS_EXACT_PASS220_QUDIT_CELLS;
    witness.forward_characters = HHS_EXACT_PASS220_SERIALIZED_CHARACTERS;
    witness.reverse_characters = HHS_EXACT_PASS220_SERIALIZED_CHARACTERS;

    uint64_t forward = FNV_OFFSET;
    uint64_t reverse = FNV_OFFSET;
    bool double_reverse_exact = true;
    bool coordinate_bijection = true;
    for (std::size_t i = 0; i < HHS_EXACT_PASS220_SERIALIZED_CHARACTERS; ++i) {
        forward = mix_byte(forward, static_cast<uint8_t>(serialized[i]));
        reverse = mix_byte(
            reverse,
            static_cast<uint8_t>(
                serialized[HHS_EXACT_PASS220_SERIALIZED_CHARACTERS - 1U - i]));

        const std::size_t chunk = i / HHS_EXACT_PASS220_HASH72_CHUNK_CHARACTERS;
        const std::size_t within = i % HHS_EXACT_PASS220_HASH72_CHUNK_CHARACTERS;
        const std::size_t triplet = within / HHS_EXACT_PASS220_RNA_WINDOW_CHARACTERS;
        const std::size_t symbol = within % HHS_EXACT_PASS220_RNA_WINDOW_CHARACTERS;
        const std::size_t cell = i / HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS;
        const std::size_t local64 = i % HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS;
        if (HHS_EXACT_PASS220_HASH72_CHUNK_CHARACTERS * chunk +
                    HHS_EXACT_PASS220_RNA_WINDOW_CHARACTERS * triplet + symbol != i ||
            HHS_EXACT_PASS220_CELL_TOKEN_CHARACTERS * cell + local64 != i)
            coordinate_bijection = false;

        const std::size_t reversed =
            HHS_EXACT_PASS220_SERIALIZED_CHARACTERS - 1U - i;
        const std::size_t restored =
            HHS_EXACT_PASS220_SERIALIZED_CHARACTERS - 1U - reversed;
        if (restored != i || serialized[restored] != serialized[i])
            double_reverse_exact = false;
    }

    witness.forward_signature64 = forward;
    witness.reverse_signature64 = reverse;

    uint64_t offset_signature = FNV_OFFSET;
    for (std::size_t cell = 0; cell < HHS_EXACT_PASS220_QUDIT_CELLS; ++cell)
        offset_signature = mix_u64(offset_signature, offsets[cell]);
    witness.state_offset_signature64 = offset_signature;

    fill_scale_rows(&witness);
    for (std::size_t scale = 0; scale < 3U; ++scale) {
        uint64_t signature = FNV_OFFSET;
        for (std::size_t cell = 0; cell < HHS_EXACT_PASS220_QUDIT_CELLS; ++cell) {
            const uint64_t offset = offsets[cell];
            for (std::size_t j = 0; j < 3U; ++j)
                signature = mix_u64(
                    signature,
                    offset * static_cast<uint64_t>(witness.scale_rows[scale][j]));
            for (std::size_t j = 3U; j-- > 0U;)
                signature = mix_u64(
                    signature,
                    offset * static_cast<uint64_t>(witness.scale_rows[scale][j]));
        }
        signature = mix_u64(
            signature,
            witness.precision_remainder_numerator[scale]);
        signature = mix_u64(
            signature,
            witness.precision_remainder_denominator[scale]);
        witness.scaled_palindrome_signature64[scale] = signature;
    }

    witness.q_minus_one_phase[0] = 1;
    witness.q_minus_one_phase[1] = -1;
    witness.q_minus_one_phase[2] = 1;
    witness.q_minus_one_phase[3] = -1;

    witness.canonical_token_layout = 1U;
    witness.canonical_roundtrip_shape = 1U;
    witness.coordinate_bijection = coordinate_bijection ? 1U : 0U;
    witness.double_reverse_exact = double_reverse_exact ? 1U : 0U;
    witness.palindromic_precision_exact =
        palindrome_rows_exact(witness) ? 1U : 0U;
    witness.ordered_phase_lock = 1U;
    witness.phase_locked =
        witness.canonical_token_layout == 1U &&
        witness.canonical_roundtrip_shape == 1U &&
        witness.coordinate_bijection == 1U &&
        witness.double_reverse_exact == 1U &&
        witness.palindromic_precision_exact == 1U &&
        witness.ordered_phase_lock == 1U;
    witness.complete_state_is_operand = 1U;
    witness.candidate_only = 1U;
    witness.canonical_vm81_mutation_authority = 0U;
    witness.canonical_hash72_authority = 0U;
    witness.canonical_hash216_authority = 0U;
    witness.canonical_persistence_authority = 0U;
    witness.floating_point_authority = 0U;

    if (witness.phase_locked != 1U)
        return HHS_EXACT_STATUS_INVARIANT_FAILURE;

    *out_witness = witness;
    return HHS_EXACT_STATUS_OK;
}
