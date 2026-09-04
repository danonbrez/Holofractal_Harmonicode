#include "hhs_pass219_language_processing_membrane_1_0.hpp"
#include <cassert>
#include <cstring>

static void fill_hash(char out[HHS_EXACT_HASH72_STRLEN], char symbol) {
    for (std::size_t i = 0; i < HHS_EXACT_HASH72_LEN; ++i) out[i] = symbol;
    out[HHS_EXACT_HASH72_LEN] = '\0';
}

int main() {
    char source[HHS_EXACT_HASH72_STRLEN];
    fill_hash(source, HHS_EXACT_HASH72_ALPHABET[0]);
    hhs::pass219::LanguageProcessingMembrane membrane(source, 5U);
    assert(membrane.status() == HHS_EXACT_STATUS_OK);
    HHSExactPass219LanguageBindingV1 binding{};
    binding.struct_size = sizeof(binding);
    binding.version = hhs_exact_pass219_language_membrane_version();
    binding.layer = HHS_EXACT_PASS219_LANGUAGE_LAYER_VERBATIM_SOURCE;
    binding.relation = HHS_EXACT_PASS219_LANGUAGE_RELATION_IDENTITY;
    binding.invariant_flags = HHS_EXACT_PASS219_LANGUAGE_FLAG_VERBATIM_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_NONAUTHORITATIVE | HHS_EXACT_PASS219_LANGUAGE_FLAG_EXACT_NO_FLOAT;
    binding.source_start = 0U;
    binding.source_end = 5U;
    binding.occurrence_id = HHS_EXACT_PASS219_LANGUAGE_NO_OCCURRENCE;
    std::memcpy(binding.source_root_hash72, source, HHS_EXACT_HASH72_STRLEN);
    fill_hash(binding.layer_root_hash72, HHS_EXACT_HASH72_ALPHABET[1]);
    assert(membrane.bind(binding) == HHS_EXACT_STATUS_OK);
    assert(membrane.validate() == HHS_EXACT_STATUS_OK);
    return 0;
}
