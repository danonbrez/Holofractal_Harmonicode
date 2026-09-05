#include "hhs_pass219_multimodal_optimization_generalization_1_0.hpp"

#include <cassert>

int main() {
    using hhs::rna::MultimodalOptimizationGeneralization;

    static_assert(MultimodalOptimizationGeneralization::optimizations_multimodal_by_default());
    static_assert(MultimodalOptimizationGeneralization::locality_is_exception());
    static_assert(MultimodalOptimizationGeneralization::compatible_untested_requires_validation());
    static_assert(MultimodalOptimizationGeneralization::safe_beneficial_requires_generalization());
    static_assert(!MultimodalOptimizationGeneralization::new_user_directive_required_per_modality());
    static_assert(MultimodalOptimizationGeneralization::descriptor_metadata_drives_compatibility());
    static_assert(MultimodalOptimizationGeneralization::repair_forward_required());

    assert(MultimodalOptimizationGeneralization::validate() == HHS_EXACT_STATUS_OK);
    return 0;
}
