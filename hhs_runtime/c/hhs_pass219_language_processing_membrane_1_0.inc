#include "../include/hhs_pass219_language_processing_membrane_1_0.h"
#include <string.h>

static uint32_t hhs_exact_pass219_language_membrane_version_word(void) {
    return (HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_VERSION_MAJOR << 16) |
           (HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_VERSION_MINOR << 8) |
           HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_VERSION_PATCH;
}

static int hhs_exact_pass219_language_hash72_valid(const char value[HHS_EXACT_HASH72_STRLEN]) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_HASH72_LEN] != '\0') return 0;
    for (i = 0U; i < HHS_EXACT_HASH72_LEN; ++i)
        if (value[i] == '\0' || strchr(HHS_EXACT_HASH72_ALPHABET, value[i]) == NULL) return 0;
    return 1;
}

static int hhs_exact_pass219_language_optional_hash72_valid(const char value[HHS_EXACT_HASH72_STRLEN]) {
    if (value == NULL) return 0;
    if (value[0] == '\0') return 1;
    return hhs_exact_pass219_language_hash72_valid(value);
}

static uint64_t hhs_exact_pass219_language_required_flags(uint32_t layer) {
    switch (layer) {
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_VERBATIM_SOURCE: return HHS_EXACT_PASS219_LANGUAGE_FLAG_VERBATIM_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKEN_TENSOR: return HHS_EXACT_PASS219_LANGUAGE_FLAG_LEXEME_OCCURRENCE_SEPARATE | HHS_EXACT_PASS219_LANGUAGE_FLAG_ORDER_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_LEXICAL_RELATION: return HHS_EXACT_PASS219_LANGUAGE_FLAG_TYPED_RELATION;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_GRAMMAR_SYNTAX: return HHS_EXACT_PASS219_LANGUAGE_FLAG_GRAMMAR_ROLE_PRESENT | HHS_EXACT_PASS219_LANGUAGE_FLAG_ORDER_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_PROPOSITION: return HHS_EXACT_PASS219_LANGUAGE_FLAG_REFERENCE_IDENTITY_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_AMBIGUITY: return HHS_EXACT_PASS219_LANGUAGE_FLAG_AMBIGUITY_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TRANSLATION_REGISTER: return HHS_EXACT_PASS219_LANGUAGE_FLAG_ORDER_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_PROVENANCE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_METAPHOR_ANALOGY: return HHS_EXACT_PASS219_LANGUAGE_FLAG_TYPED_RELATION | HHS_EXACT_PASS219_LANGUAGE_FLAG_PATTERN_RECOGNITION_EXPLICIT;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_SEMANTIC_GRAPH: return HHS_EXACT_PASS219_LANGUAGE_FLAG_TYPED_RELATION | HHS_EXACT_PASS219_LANGUAGE_FLAG_PROVENANCE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_CONTEXT_DISCOURSE: return HHS_EXACT_PASS219_LANGUAGE_FLAG_DISCOURSE_HISTORY_PRESENT | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_AUDIO_LANGUAGE: return HHS_EXACT_PASS219_LANGUAGE_FLAG_PROVENANCE_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_REFERENCE_IDENTITY_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_MODEL_PROPOSAL: return HHS_EXACT_PASS219_LANGUAGE_FLAG_UNCERTAINTY_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_AMBIGUITY_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKENIZATION_INGESTION: return HHS_EXACT_PASS219_LANGUAGE_FLAG_VERBATIM_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_LEXEME_OCCURRENCE_SEPARATE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_VECTOR_HYDRATION: return HHS_EXACT_PASS219_LANGUAGE_FLAG_PROVENANCE_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_REVERSIBLE_PROVENANCE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_SYMBOLIC_TRANSLATION: return HHS_EXACT_PASS219_LANGUAGE_FLAG_REFERENCE_IDENTITY_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_NEGATION_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_SCOPE_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_MODALITY_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_TEMPORALITY_PRESERVED | HHS_EXACT_PASS219_LANGUAGE_FLAG_UNCERTAINTY_PRESERVED;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_PATTERN_META_AWARENESS: return HHS_EXACT_PASS219_LANGUAGE_FLAG_PATTERN_RECOGNITION_EXPLICIT | HHS_EXACT_PASS219_LANGUAGE_FLAG_DISCOURSE_HISTORY_PRESENT;
        default: return UINT64_C(0);
    }
}

static int hhs_exact_pass219_language_relation_valid(uint32_t layer, uint32_t relation) {
    switch (layer) {
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_VERBATIM_SOURCE: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_IDENTITY;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKEN_TENSOR:
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKENIZATION_INGESTION: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_OCCURRENCE_OF;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_LEXICAL_RELATION: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_SYNONYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_DEFINITION || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_ANTONYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_HYPERNYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_HYPONYM;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_GRAMMAR_SYNTAX: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_GRAMMAR;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_PROPOSITION: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_PROPOSITION;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_AMBIGUITY: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_AMBIGUITY_ALTERNATIVE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_TRANSLATION_REGISTER: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_TRANSLATION;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_METAPHOR_ANALOGY: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_ANALOGY || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_METAPHOR;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_SEMANTIC_GRAPH: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_SYNONYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_ANTONYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_HYPERNYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_HYPONYM || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_VECTOR_CANDIDATE || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_PATTERN;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_CONTEXT_DISCOURSE: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_CONTEXT || relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_DISCOURSE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_AUDIO_LANGUAGE: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_AUDIO_TRANSCRIPTION;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_MODEL_PROPOSAL: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_MODEL_CANDIDATE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_VECTOR_HYDRATION: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_VECTOR_CANDIDATE;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_SYMBOLIC_TRANSLATION: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_SYMBOLIC_PROJECTION;
        case HHS_EXACT_PASS219_LANGUAGE_LAYER_PATTERN_META_AWARENESS: return relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_PATTERN;
        default: return 0;
    }
}

uint32_t hhs_exact_pass219_language_membrane_version(void) { return hhs_exact_pass219_language_membrane_version_word(); }

HHSExactStatus hhs_exact_pass219_language_membrane_init(const char source_root_hash72[HHS_EXACT_HASH72_STRLEN], uint32_t source_character_count, HHSExactPass219LanguageMembraneV1 *out_membrane) {
    if (source_root_hash72 == NULL || out_membrane == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (!hhs_exact_pass219_language_hash72_valid(source_root_hash72)) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memset(out_membrane, 0, sizeof(*out_membrane));
    out_membrane->struct_size = (uint32_t)sizeof(*out_membrane);
    out_membrane->version = hhs_exact_pass219_language_membrane_version_word();
    out_membrane->source_character_count = source_character_count;
    out_membrane->projection_only = 1U;
    memcpy(out_membrane->source_root_hash72, source_root_hash72, HHS_EXACT_HASH72_STRLEN);
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_language_binding_validate(const HHSExactPass219LanguageBindingV1 *binding, uint32_t source_character_count) {
    uint64_t required;
    if (binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (binding->struct_size < sizeof(*binding) || binding->version != hhs_exact_pass219_language_membrane_version_word()) return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (binding->layer >= HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_LAYER_COUNT || binding->relation > HHS_EXACT_PASS219_LANGUAGE_RELATION_PATTERN) return HHS_EXACT_STATUS_RANGE_ERROR;
    if (binding->relation_polarity < -1 || binding->relation_polarity > 1) return HHS_EXACT_STATUS_RANGE_ERROR;
    if (binding->source_start > binding->source_end || binding->source_end > source_character_count) return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_exact_pass219_language_hash72_valid(binding->source_root_hash72) || !hhs_exact_pass219_language_hash72_valid(binding->layer_root_hash72) || !hhs_exact_pass219_language_optional_hash72_valid(binding->parent_root_hash72) || !hhs_exact_pass219_language_optional_hash72_valid(binding->reconstruction_root_hash72)) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if ((binding->invariant_flags & ~HHS_EXACT_PASS219_LANGUAGE_KNOWN_FLAGS) != 0U || (binding->invariant_flags & HHS_EXACT_PASS219_LANGUAGE_FLAG_NONAUTHORITATIVE) == 0U || (binding->invariant_flags & HHS_EXACT_PASS219_LANGUAGE_FLAG_EXACT_NO_FLOAT) == 0U) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    required = hhs_exact_pass219_language_required_flags(binding->layer);
    if ((binding->invariant_flags & required) != required) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (!hhs_exact_pass219_language_relation_valid(binding->layer, binding->relation)) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (binding->layer == HHS_EXACT_PASS219_LANGUAGE_LAYER_VERBATIM_SOURCE && (binding->source_start != 0U || binding->source_end != source_character_count)) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if ((binding->layer == HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKEN_TENSOR || binding->layer == HHS_EXACT_PASS219_LANGUAGE_LAYER_TOKENIZATION_INGESTION) && binding->occurrence_id == HHS_EXACT_PASS219_LANGUAGE_NO_OCCURRENCE) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (binding->layer == HHS_EXACT_PASS219_LANGUAGE_LAYER_METAPHOR_ANALOGY && binding->relation == HHS_EXACT_PASS219_LANGUAGE_RELATION_METAPHOR && (((binding->invariant_flags & HHS_EXACT_PASS219_LANGUAGE_FLAG_METAPHOR_DECLARED) == 0U) || ((binding->invariant_flags & HHS_EXACT_PASS219_LANGUAGE_FLAG_RECONSTRUCTION_MAP_PRESENT) == 0U) || binding->reconstruction_root_hash72[0] == '\0')) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_language_membrane_add(HHSExactPass219LanguageMembraneV1 *membrane, const HHSExactPass219LanguageBindingV1 *binding) {
    HHSExactStatus status;
    if (membrane == NULL || binding == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (membrane->struct_size < sizeof(*membrane) || membrane->version != hhs_exact_pass219_language_membrane_version_word()) return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (membrane->binding_count >= HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_MAX_BINDINGS) return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
    status = hhs_exact_pass219_language_binding_validate(binding, membrane->source_character_count);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (memcmp(binding->source_root_hash72, membrane->source_root_hash72, HHS_EXACT_HASH72_STRLEN) != 0) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    memcpy(&membrane->bindings[membrane->binding_count], binding, sizeof(*binding));
    membrane->binding_count += 1U;
    membrane->layer_mask |= UINT32_C(1) << binding->layer;
    membrane->aggregate_invariant_flags |= binding->invariant_flags;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_language_membrane_validate(const HHSExactPass219LanguageMembraneV1 *membrane) {
    uint32_t i, observed_mask = 0U;
    uint64_t observed_flags = UINT64_C(0);
    if (membrane == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (membrane->struct_size < sizeof(*membrane) || membrane->version != hhs_exact_pass219_language_membrane_version_word()) return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (membrane->binding_count > HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_MAX_BINDINGS) return HHS_EXACT_STATUS_RANGE_ERROR;
    if (!hhs_exact_pass219_language_hash72_valid(membrane->source_root_hash72) || !hhs_exact_pass219_language_optional_hash72_valid(membrane->membrane_receipt_root_hash72)) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if (membrane->projection_only != 1U || membrane->language_authority != 0U || membrane->vm81_mutation_authority != 0U || membrane->hash72_mint_authority != 0U || membrane->hash216_persistence_authority != 0U || membrane->deterministic_replay_authority != 0U) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    for (i = 0U; i < membrane->binding_count; ++i) {
        HHSExactStatus status = hhs_exact_pass219_language_binding_validate(&membrane->bindings[i], membrane->source_character_count);
        if (status != HHS_EXACT_STATUS_OK) return status;
        if (memcmp(membrane->bindings[i].source_root_hash72, membrane->source_root_hash72, HHS_EXACT_HASH72_STRLEN) != 0) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
        observed_mask |= UINT32_C(1) << membrane->bindings[i].layer;
        observed_flags |= membrane->bindings[i].invariant_flags;
    }
    if (observed_mask != membrane->layer_mask || observed_flags != membrane->aggregate_invariant_flags) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_language_membrane_validate_complete(const HHSExactPass219LanguageMembraneV1 *membrane) {
    HHSExactStatus status = hhs_exact_pass219_language_membrane_validate(membrane);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (membrane->layer_mask != HHS_EXACT_PASS219_LANGUAGE_MEMBRANE_FULL_LAYER_MASK) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    if ((membrane->aggregate_invariant_flags & HHS_EXACT_PASS219_LANGUAGE_CORE_FLAGS) != HHS_EXACT_PASS219_LANGUAGE_CORE_FLAGS) return HHS_EXACT_STATUS_INVARIANT_FAILURE;
    return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass219_language_membrane_project_rna_plan(const HHSExactPass219LanguageMembraneV1 *membrane, const HHSExactPass219RNAExecutionPlanV1 *execution_plan, HHSExactPass219LanguageRNAProjectionV1 *out_projection) {
    HHSExactStatus status;
    if (membrane == NULL || execution_plan == NULL || out_projection == NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    status = hhs_exact_pass219_language_membrane_validate_complete(membrane);
    if (status != HHS_EXACT_STATUS_OK) return status;
    if (execution_plan->struct_size < sizeof(*execution_plan) || execution_plan->version != hhs_exact_pass219_rna_execution_composer_version()) return HHS_EXACT_STATUS_VERSION_MISMATCH;
    if (execution_plan->route < HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_INDEXED_CONTINUATION || execution_plan->route > HHS_EXACT_PASS219_RNA_EXECUTION_ROUTE_GENESIS_REPLAY || execution_plan->requested_bypass_reason > HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT || execution_plan->effective_bypass_reason > HHS_EXACT_PASS219_RNA_BYPASS_EXPLICITLY_AUTHORIZED_AUDIT) return HHS_EXACT_STATUS_RANGE_ERROR;
    memset(out_projection, 0, sizeof(*out_projection));
    out_projection->struct_size = (uint32_t)sizeof(*out_projection);
    out_projection->version = hhs_exact_pass219_language_membrane_version_word();
    out_projection->binding_count = membrane->binding_count;
    out_projection->layer_mask = membrane->layer_mask;
    out_projection->projection_only = 1U;
    out_projection->admission_required = 1U;
    memcpy(out_projection->source_root_hash72, membrane->source_root_hash72, HHS_EXACT_HASH72_STRLEN);
    memcpy(out_projection->membrane_receipt_root_hash72, membrane->membrane_receipt_root_hash72, HHS_EXACT_HASH72_STRLEN);
    memcpy(&out_projection->execution_plan, execution_plan, sizeof(*execution_plan));
    return HHS_EXACT_STATUS_OK;
}
