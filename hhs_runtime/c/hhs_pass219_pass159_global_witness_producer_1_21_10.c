#include "hhs_pass219_pass159_global_witness_provenance_1_21_10.h"

#include "hhs_pass159_api.h"
#include "hhs159_internal.h"

#include <openssl/sha.h>
#include <string.h>

#if HHS159_HASH216_LENGTH != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN
#error "Pass159 Hash216 length drift"
#endif

static const uint8_t HHS219_I12110_SOURCE_SHA256[
    HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES
] = {
    0x33U, 0x15U, 0x64U, 0x1cU, 0x8dU, 0x6aU, 0xa9U, 0xfcU,
    0x4fU, 0x39U, 0x18U, 0xecU, 0xcdU, 0xa8U, 0xe3U, 0xa4U,
    0x0cU, 0x84U, 0x45U, 0xccU, 0x41U, 0x7aU, 0x65U, 0xe5U,
    0xdeU, 0xa6U, 0x83U, 0xf6U, 0x80U, 0x20U, 0xcfU, 0x53U
};

static const uint32_t HHS219_I12110_GATE_OFFSETS[
    HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT
] = {96U, 240U, 266U, 274U, 285U};

static uint32_t hhs219_i12110_version_word(void) {
    return (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MAJOR << 16U) |
           (HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_MINOR << 8U) |
           HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_VERSION_PATCH;
}

static int hhs219_i12110_hash216_present(const char *value) {
    size_t i;
    if (value == NULL || value[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN] != '\0')
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN; ++i) {
        if (value[i] == '\0')
            return 0;
    }
    return 1;
}

static int hhs219_i12110_copy_hash216(
    const void *handle,
    char out[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN]
) {
    HHS159MutableByteSpan span;
    HHS159Status status;
    if (handle == NULL || out == NULL)
        return 0;
    memset(out, 0, HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_STRLEN);
    span.data = (uint8_t *)out;
    span.capacity = HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN;
    span.size_written = 0U;
    status = hhs159_get_hash216(handle, &span);
    if (status != HHS159_STATUS_OK ||
        span.size_written != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN)
        return 0;
    out[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN] = '\0';
    return hhs219_i12110_hash216_present(out);
}

static int hhs219_i12110_scan_gates(
    const uint8_t *source,
    size_t source_length,
    uint32_t out_offsets[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT]
) {
    size_t i;
    uint32_t count = 0U;
    if (source == NULL || out_offsets == NULL)
        return 0;
    for (i = 0U; i + 1U < source_length; ++i) {
        if (source[i] == (uint8_t)'=' && source[i + 1U] == (uint8_t)'=') {
            if (count >= HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT)
                return 0;
            out_offsets[count++] = (uint32_t)i;
            ++i;
        }
    }
    if (count != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT)
        return 0;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT; ++i) {
        if (out_offsets[i] != HHS219_I12110_GATE_OFFSETS[i])
            return 0;
    }
    return 1;
}

static int hhs219_i12110_source_root_matches(
    const HHS159ArtifactBase *artifact,
    const HHS159Source *source
) {
    if (artifact == NULL || source == NULL)
        return 0;
    if (!hhs219_i12110_hash216_present(artifact->source_root))
        return 0;
    if (memcmp(
            artifact->source_root,
            source->base.hash216,
            HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN) == 0)
        return 1;
    return hhs219_i12110_hash216_present(source->base.source_root) &&
           memcmp(
               artifact->source_root,
               source->base.source_root,
               HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN) == 0;
}

static int hhs219_i12110_root_nonzero(
    const uint8_t root[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES]
) {
    size_t i;
    uint8_t aggregate = 0U;
    for (i = 0U; i < HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES; ++i)
        aggregate = (uint8_t)(aggregate | root[i]);
    return aggregate != 0U;
}

static void hhs219_i12110_write_u32_be(uint8_t out[4], uint32_t value) {
    out[0] = (uint8_t)(value >> 24U);
    out[1] = (uint8_t)(value >> 16U);
    out[2] = (uint8_t)(value >> 8U);
    out[3] = (uint8_t)value;
}

static int hhs219_i12110_environment_root(
    const HHSExactPass219Pass159GlobalWitnessProvenanceV1 *provenance,
    uint8_t out[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES]
) {
    static const uint8_t domain[] =
        "HHS-P219-I121.10-PASS159-WHOLE-EXPRESSION-PROVENANCE-V1";
    uint8_t material[2048];
    size_t cursor = 0U;
    size_t i;
    const char *hashes[8];

    if (provenance == NULL || out == NULL)
        return 0;

    hashes[0] = provenance->source_hash216;
    hashes[1] = provenance->tokens_hash216;
    hashes[2] = provenance->cst_hash216;
    hashes[3] = provenance->ast_hash216;
    hashes[4] = provenance->type_environment_hash216;
    hashes[5] = provenance->constraint_graph_hash216;
    hashes[6] = provenance->hir_hash216;
    hashes[7] = provenance->vmir_hash216;

    if (sizeof(domain) - 1U > sizeof(material))
        return 0;
    memcpy(material + cursor, domain, sizeof(domain) - 1U);
    cursor += sizeof(domain) - 1U;

    if (cursor + sizeof(provenance->combined_source_sha256) > sizeof(material))
        return 0;
    memcpy(material + cursor,
           provenance->combined_source_sha256,
           sizeof(provenance->combined_source_sha256));
    cursor += sizeof(provenance->combined_source_sha256);

    for (i = 0U; i < 8U; ++i) {
        if (!hhs219_i12110_hash216_present(hashes[i]) ||
            cursor + HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN > sizeof(material))
            return 0;
        memcpy(material + cursor,
               hashes[i],
               HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN);
        cursor += HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN;
    }

    for (i = 0U; i < HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT; ++i) {
        uint8_t encoded[4];
        if (cursor + sizeof(encoded) > sizeof(material))
            return 0;
        hhs219_i12110_write_u32_be(encoded, provenance->gate_offsets[i]);
        memcpy(material + cursor, encoded, sizeof(encoded));
        cursor += sizeof(encoded);
    }

    return SHA256(material, cursor, out) != NULL && hhs219_i12110_root_nonzero(out);
}

uint32_t hhs_exact_pass219_pass159_global_witness_version(void) {
    return hhs219_i12110_version_word();
}

HHSExactStatus hhs_exact_pass219_pass159_global_witness_produce(
    const uint8_t *source_bytes,
    size_t source_length,
    HHSExactPass219Pass159GlobalWitnessProvenanceV1 *out_provenance
) {
    static const uint8_t source_name[] = "pass219-combined-equation-i12110";
    static const uint8_t encoding[] = "UTF-8";
    HHS159ContextConfig config;
    HHS159SourceOpenOptions options;
    HHS159ByteSpan source_span;
    HHS159Context *context = NULL;
    HHS159Source *source = NULL;
    HHS159IR *tokens = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159IR *hir = NULL;
    HHS159IR *vmir = NULL;
    HHS159Status status = HHS159_STATUS_INVALID_STATE;
    HHSExactStatus exact_status = HHS_EXACT_STATUS_INVARIANT_FAILURE;
    uint8_t digest[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SHA256_BYTES];
    uint32_t offsets[HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT];
    int source_lineage = 0;

    if (source_bytes == NULL || out_provenance == NULL)
        return HHS_EXACT_STATUS_INVALID_ARGUMENT;
    if (source_length != HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_SOURCE_BYTES)
        return HHS_EXACT_STATUS_RANGE_ERROR;

    memset(out_provenance, 0, sizeof(*out_provenance));
    out_provenance->struct_size = (uint32_t)sizeof(*out_provenance);
    out_provenance->version = hhs219_i12110_version_word();
    out_provenance->pass159_status = (int32_t)HHS159_STATUS_INVALID_STATE;
    out_provenance->source_length = (uint32_t)source_length;
    out_provenance->pass169_whole_expression_authority_required = 1U;
    out_provenance->canonical_monolithic_proof = 0U;
    out_provenance->floating_point_authority = 0U;
    out_provenance->vm81_mutation_authority = 0U;
    out_provenance->hash72_commit_authority = 0U;
    out_provenance->persistence_mutation_authority = 0U;

    if (SHA256(source_bytes, source_length, digest) == NULL ||
        memcmp(digest, HHS219_I12110_SOURCE_SHA256, sizeof(digest)) != 0)
        goto cleanup;
    memcpy(out_provenance->combined_source_sha256, digest, sizeof(digest));
    out_provenance->source_identity_exact = 1U;

    memset(offsets, 0, sizeof(offsets));
    if (!hhs219_i12110_scan_gates(source_bytes, source_length, offsets))
        goto cleanup;
    memcpy(out_provenance->gate_offsets, offsets, sizeof(offsets));
    out_provenance->gate_count = HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_GATE_COUNT;
    out_provenance->gate_occurrence_provenance_exact = 1U;

    memset(&config, 0, sizeof(config));
    config.header.struct_size = (uint32_t)sizeof(config);
    config.header.struct_version = HHS159_STRUCT_VERSION_1;
    config.max_source_bytes = UINT64_C(1048576);
    config.max_tokens = UINT64_C(200000);
    config.max_nesting = UINT64_C(4096);
    config.max_output_bytes = UINT64_C(4194304);
    config.deterministic_epoch = UINT64_C(0);
    config.flags = HHS159_FLAG_ORDERED;
    status = hhs159_context_create(&config, &context);
    if (status != HHS159_STATUS_OK)
        goto cleanup;

    memset(&options, 0, sizeof(options));
    options.header.struct_size = (uint32_t)sizeof(options);
    options.header.struct_version = HHS159_STRUCT_VERSION_1;
    options.source_name.data = source_name;
    options.source_name.size = sizeof(source_name) - 1U;
    options.encoding.data = encoding;
    options.encoding.size = sizeof(encoding) - 1U;
    options.preserve_bom = 1U;
    options.flags = HHS159_FLAG_ORDERED;

    source_span.data = source_bytes;
    source_span.size = source_length;
    status = hhs159_source_open_bytes(context, source_span, &options, &source);
    if (status != HHS159_STATUS_OK ||
        !hhs219_i12110_copy_hash216(source, out_provenance->source_hash216))
        goto cleanup;

    status = hhs159_lex(context, source, &tokens);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(tokens) != HHS159_ARTIFACT_TOKEN_STREAM ||
        !hhs219_i12110_copy_hash216(tokens, out_provenance->tokens_hash216))
        goto cleanup;

    status = hhs159_parse_cst(context, source, &cst);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(cst) != HHS159_ARTIFACT_CST ||
        !hhs219_i12110_copy_hash216(cst, out_provenance->cst_hash216))
        goto cleanup;

    status = hhs159_build_ast(context, cst, &ast);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(ast) != HHS159_ARTIFACT_AST ||
        !hhs219_i12110_copy_hash216(ast, out_provenance->ast_hash216))
        goto cleanup;

    status = hhs159_typecheck(context, ast, &types);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV ||
        !hhs219_i12110_copy_hash216(types, out_provenance->type_environment_hash216))
        goto cleanup;

    status = hhs159_build_constraint_graph(context, ast, types, &graph);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !hhs219_i12110_copy_hash216(graph, out_provenance->constraint_graph_hash216))
        goto cleanup;

    status = hhs159_lower_hir(context, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR ||
        !hhs219_i12110_copy_hash216(hir, out_provenance->hir_hash216))
        goto cleanup;

    status = hhs159_lower_vmir(context, hir, &vmir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !hhs219_i12110_copy_hash216(vmir, out_provenance->vmir_hash216))
        goto cleanup;

    out_provenance->frontend_chain_complete = 1U;

    source_lineage =
        memcmp(
            out_provenance->source_hash216,
            source->base.hash216,
            HHS_EXACT_PASS219_PASS159_GLOBAL_WITNESS_HASH216_LEN) == 0 &&
        hhs219_i12110_source_root_matches(&tokens->base, source) &&
        hhs219_i12110_source_root_matches(&cst->base, source) &&
        hhs219_i12110_source_root_matches(&ast->base, source) &&
        hhs219_i12110_source_root_matches(&types->base, source) &&
        hhs219_i12110_source_root_matches(&graph->base, source) &&
        hhs219_i12110_source_root_matches(&hir->base, source) &&
        hhs219_i12110_source_root_matches(&vmir->base, source);
    if (!source_lineage)
        goto cleanup;
    out_provenance->source_root_lineage_exact = 1U;

    if (!hhs219_i12110_environment_root(
            out_provenance,
            out_provenance->global_symbol_environment_root))
        goto cleanup;

    out_provenance->pass159_whole_expression_provenance_verified = 1U;
    out_provenance->boolean_gate_results_available = 0U;
    out_provenance->membrane_input_ready = 0U;
    status = HHS159_STATUS_OK;
    exact_status = HHS_EXACT_STATUS_OK;

cleanup:
    out_provenance->pass159_status = (int32_t)status;
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (source != NULL) hhs159_source_release(source);
    if (context != NULL) hhs159_context_release(context);
    return exact_status;
}
