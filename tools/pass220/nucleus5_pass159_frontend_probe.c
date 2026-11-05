/* Pass 220 nucleus-5 source -> inherited Pass159 frontend and diagnostic interpreter.
 * No canonical VM81 commit: verifies native parser, graph, held receipt and replay.
 * Input is supplied as a byte-exact HARMONICODE circuit source file.
 */
#include "hhs_pass159_api.h"
#include "hhs159_internal.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_source(const char *path, uint8_t **out, size_t *len) {
    FILE *f = fopen(path, "rb");
    long count;
    uint8_t *bytes;
    if (f == NULL) return 0;
    if (fseek(f, 0, SEEK_END) != 0 || (count = ftell(f)) <= 0 ||
        count > 1048576L || fseek(f, 0, SEEK_SET) != 0) {
        fclose(f);
        return 0;
    }
    bytes = (uint8_t *)malloc((size_t)count);
    if (bytes == NULL) { fclose(f); return 0; }
    if (fread(bytes, 1, (size_t)count, f) != (size_t)count) {
        free(bytes); fclose(f); return 0;
    }
    fclose(f);
    *out = bytes; *len = (size_t)count;
    return 1;
}

/* Verify the source-topology manifest against the bytes passed to Pass159.
 * This does not establish effectful instruction lowering or VM81 admission.
 */
static int verify_span_manifest(const char *path, const uint8_t *source, size_t size) {
    FILE *fp = fopen(path, "r");
    char line[256];
    char expected[65], digest_hex[65];
    uint8_t digest[SHA256_DIGEST_LENGTH];
    unsigned long source_len;
    unsigned m, r, c, start, end, gate, cell_count = 0U, gate_count = 0U;
    size_t i;
    int result = 0;
    if (fp == NULL || source == NULL) return 0;
    if (fgets(line, sizeof(line), fp) == NULL ||
        sscanf(line, "NUCLEUS5_V1 %lu %64s", &source_len, expected) != 2 ||
        source_len != size || SHA256(source, size, digest) == NULL) goto done;
    for (i = 0; i < SHA256_DIGEST_LENGTH; ++i)
        (void)sprintf(digest_hex + 2U * i, "%02x", (unsigned)digest[i]);
    digest_hex[64] = '\0';
    if (strcmp(digest_hex, expected) != 0) goto done;
    /* Pin the inherited canonical base/successor sources independently of
       the supplied span manifest. A rewritten source plus regenerated
       manifest cannot authorize an alternate tensor. */
    if (!((size == 1015U &&
           strcmp(digest_hex, "1655ebcb15ca331d187f73064cf0bf60acc4d1bbc50f7b71e882744bcc12af2b") == 0) ||
          (size == 1095U &&
           strcmp(digest_hex, "caf4f13214825cefa1905ae1cba34fd0bc702f735acc74c684cef4492dc79565") == 0)))
        goto done;
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (line[0] == 'C' && line[1] == ' ') {
            if (sscanf(line, "C %u %u %u %u %u %64s",
                       &m, &r, &c, &start, &end, expected) != 6 ||
                cell_count >= 48U || m != cell_count / 16U ||
                r != (cell_count % 16U) / 4U ||
                c != cell_count % 4U ||
                start >= end || end > size ||
                SHA256(source + start, end - start, digest) == NULL) goto done;
            for (i = 0; i < SHA256_DIGEST_LENGTH; ++i)
                (void)sprintf(digest_hex + 2U * i, "%02x", (unsigned)digest[i]);
            digest_hex[64] = '\0';
            if (strcmp(digest_hex, expected) != 0) goto done;
            ++cell_count;
        } else if (line[0] == 'E' && line[1] == ' ') {
            if (cell_count != 48U ||
                sscanf(line, "E %u %u %u", &gate, &start, &end) != 3 ||
                gate != gate_count || start + 2U != end || end > size ||
                memcmp(source + start, "==", 2U) != 0) goto done;
            ++gate_count;
        } else if (strncmp(line, "END ", 4U) == 0) {
            unsigned declared_cells, declared_gates;
            if (sscanf(line, "END %u %u", &declared_cells, &declared_gates) != 2 ||
                declared_cells != 48U || declared_cells != cell_count ||
                declared_gates != gate_count || gate_count < 3U ||
                fgets(line, sizeof(line), fp) != NULL) goto done;
            result = 1;
            break;
        } else goto done;
    }
done:
    fclose(fp);
    return result;
}

static int read_hash216(const void *artifact, char value[HHS159_HASH216_LENGTH + 1U]) {
    memset(value, 0, HHS159_HASH216_LENGTH + 1U);
    HHS159MutableByteSpan span = {
        (uint8_t *)value, HHS159_HASH216_LENGTH, 0U
    };
    return hhs159_get_hash216(artifact, &span) == HHS159_STATUS_OK &&
           span.size_written == HHS159_HASH216_LENGTH;
}

static int diagnostic_sha256(const HHS159ArtifactBase *artifact, char out[65]) {
    uint8_t digest[SHA256_DIGEST_LENGTH];
    size_t i;
    if (artifact == NULL || artifact->bytes == NULL ||
        artifact->size == 0U || SHA256(artifact->bytes, artifact->size, digest) == NULL)
        return 0;
    for (i = 0U; i < SHA256_DIGEST_LENGTH; ++i)
        (void)sprintf(out + 2U * i, "%02x", (unsigned)digest[i]);
    out[64] = '\0';
    return 1;
}

static int payload_contains(const HHS159ArtifactBase *artifact, const char *needle) {
    size_t len, i;
    if (artifact == NULL || needle == NULL ||
        artifact->bytes == NULL || (len = strlen(needle)) == 0U ||
        len > artifact->size)
        return 0;
    for (i = 0U; i <= artifact->size - len; ++i)
        if (memcmp(artifact->bytes + i, needle, len) == 0)
            return 1;
    return 0;
}

static int hash216(const void *artifact) {
    char digest[HHS159_HASH216_LENGTH + 1U];
    return read_hash216(artifact, digest);
}

int main(int argc, char **argv) {
    static const uint8_t source_name[] = "pass220-nucleus5-ABP";
    static const uint8_t utf8[] = "UTF-8";
    HHS159ContextConfig cfg = {0};
    HHS159SourceOpenOptions opts = {0};
    HHS159Context *ctx = NULL;
    HHS159Source *src = NULL;
    HHS159IR *tokens = NULL, *hir = NULL, *vmir = NULL;
    HHS159CST *cst = NULL;
    HHS159AST *ast = NULL;
    HHS159TypeEnvironment *types = NULL;
    HHS159ConstraintGraph *graph = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Compiler *compiler = NULL;
    HHS159Object *object = NULL;
    HHS159Executable *executable = NULL;
    HHS159Receipt *compile_receipt = NULL, *compiled_receipt = NULL;
    HHS159Receipt *receipt = NULL, *replay_receipt = NULL;
    HHS159ExecutionOptions execution = {0};
    HHS159CompareResult compare = {0};
    HHS159ByteSpan span;
    HHS159Status status = HHS159_STATUS_INVALID_STATE;
    uint8_t *bytes = NULL;
    size_t size = 0U;
    int ok = 0;
    int require_source_effect = 0;
    int source_effect_rejected = 0;
    uint64_t observed_steps = 0U;
    char observed_semantic_root[HHS159_HASH216_LENGTH + 1U] = {0};
    uint32_t observed_commit = 0U;
    uint32_t observed_fallback = 0U;
    char vmir_payload_sha256[65] = {0};
    size_t vmir_payload_bytes = 0U;
    int vmir_fixed_program_marker = 0;
    int vmir_matrix_times_marker = 0;
    uint64_t compiled_steps = 0U;
    char compiled_semantic_root[HHS159_HASH216_LENGTH + 1U] = {0};
    char object_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char executable_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char compiled_receipt_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char source_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char ast_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char graph_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char vmir_id[HHS159_HASH216_LENGTH + 1U] = {0};
    char receipt_id[HHS159_HASH216_LENGTH + 1U] = {0};
    if (argc == 4 && strcmp(argv[3], "--require-source-effect") == 0)
        require_source_effect = 1;
    if ((argc != 3 && !require_source_effect) ||
        !read_source(argv[1], &bytes, &size) ||
        !verify_span_manifest(argv[2], bytes, size))
        goto cleanup;

    cfg.header.struct_size = (uint32_t)sizeof(cfg);
    cfg.header.struct_version = HHS159_STRUCT_VERSION_1;
    cfg.max_source_bytes = UINT64_C(1048576);
    cfg.max_tokens = UINT64_C(200000);
    cfg.max_nesting = UINT64_C(4096);
    cfg.max_output_bytes = UINT64_C(4194304);
    cfg.flags = HHS159_FLAG_ORDERED;
    status = hhs159_context_create(&cfg, &ctx);
    if (status != HHS159_STATUS_OK) goto cleanup;

    opts.header.struct_size = (uint32_t)sizeof(opts);
    opts.header.struct_version = HHS159_STRUCT_VERSION_1;
    opts.source_name.data = source_name;
    opts.source_name.size = sizeof(source_name) - 1U;
    opts.encoding.data = utf8;
    opts.encoding.size = sizeof(utf8) - 1U;
    opts.flags = HHS159_FLAG_ORDERED;
    opts.preserve_bom = 1U;
    span.data = bytes; span.size = size;
    status = hhs159_source_open_bytes(ctx, span, &opts, &src);
    if (status != HHS159_STATUS_OK || !read_hash216(src, source_id)) goto cleanup;
    status = hhs159_lex(ctx, src, &tokens);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(tokens) != HHS159_ARTIFACT_TOKEN_STREAM)
        goto cleanup;
    status = hhs159_parse_cst(ctx, src, &cst);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(cst) != HHS159_ARTIFACT_CST)
        goto cleanup;
    status = hhs159_build_ast(ctx, cst, &ast);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(ast) != HHS159_ARTIFACT_AST ||
        !read_hash216(ast, ast_id)) goto cleanup;
    status = hhs159_typecheck(ctx, ast, &types);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(types) != HHS159_ARTIFACT_TYPE_ENV)
        goto cleanup;
    status = hhs159_build_constraint_graph(ctx, ast, types, &graph);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(graph) != HHS159_ARTIFACT_CONSTRAINT_GRAPH ||
        !read_hash216(graph, graph_id)) goto cleanup;
    status = hhs159_lower_hir(ctx, ast, types, graph, &hir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(hir) != HHS159_ARTIFACT_HIR)
        goto cleanup;
    status = hhs159_lower_vmir(ctx, hir, &vmir);
    if (status != HHS159_STATUS_OK ||
        hhs159_artifact_kind(vmir) != HHS159_ARTIFACT_VMIR ||
        !read_hash216(vmir, vmir_id)) goto cleanup;
    vmir_payload_bytes = vmir->base.size;
    vmir_fixed_program_marker = payload_contains(&vmir->base, "EXACT_PROGRAM");
    vmir_matrix_times_marker = payload_contains(&vmir->base, "MatrixTimes");
    if (!diagnostic_sha256(&vmir->base, vmir_payload_sha256)) goto cleanup;
    /* Invoke the existing Pass159 interpreter without canonical commit.
     * Current VMIR execution may use a fixed EXACT_PROGRAM: these receipts
     * demonstrate ABI/path and replay health, not tensor semantic closure.
     */
    status = hhs159_interpreter_create(ctx, &interpreter);
    if (status != HHS159_STATUS_OK) goto cleanup;
    execution.header.struct_size = (uint32_t)sizeof(execution);
    execution.header.struct_version = HHS159_STRUCT_VERSION_1;
    execution.mode = HHS159_MODE_EXECUTE_AND_HOLD;
    execution.commit_policy = 0U;
    execution.max_vm81_steps = UINT64_C(1000000);
    execution.max_recursion = UINT64_C(4096);
    execution.max_output_bytes = UINT64_C(4194304);
    status = hhs159_interpret(interpreter, src, &execution, &receipt);
    if (status != HHS159_STATUS_OK || receipt == NULL ||
        hhs159_artifact_kind(receipt) != HHS159_ARTIFACT_RECEIPT ||
        !read_hash216(receipt, receipt_id)) goto cleanup;
    observed_steps = receipt->vm81_steps;
    observed_commit = receipt->committed;
    observed_fallback = receipt->fallback_used;
    memcpy(observed_semantic_root, receipt->semantic_root,
           sizeof(observed_semantic_root));
    if (receipt->committed != 0U || receipt->fallback_used != 0U ||
        receipt->status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_interpreter_replay(interpreter, receipt, &replay_receipt);
    if (status != HHS159_STATUS_OK || replay_receipt == NULL ||
        hhs159_artifact_kind(replay_receipt) != HHS159_ARTIFACT_RECEIPT ||
        !hash216(replay_receipt)) goto cleanup;
    compare.header.struct_size = (uint32_t)sizeof(compare);
    compare.header.struct_version = HHS159_STRUCT_VERSION_1;
    status = hhs159_compare_interpreter_compiler(ctx, src, &execution, &compare);
    if (status != HHS159_STATUS_OK ||
        compare.status != HHS159_STATUS_OK ||
        compare.matched != 1U || compare.fallback_used != 0U)
        goto cleanup;
    /* Exercise Pass159's native compiler→object→link→executable path.
     * This is a held diagnostic: its existing exact-program lowering still
     * requires an independent source-effect witness before admission.
     */
    status = hhs159_compiler_create(ctx, &compiler);
    if (status != HHS159_STATUS_OK) goto cleanup;
    status = hhs159_compile_object(compiler, src, &object, &compile_receipt);
    if (status != HHS159_STATUS_OK || object == NULL ||
        hhs159_artifact_kind(object) != HHS159_ARTIFACT_OBJECT ||
        !read_hash216(object, object_id)) goto cleanup;
    status = hhs159_link(ctx, &object, 1U, &executable, &compiled_receipt);
    if (status != HHS159_STATUS_OK || executable == NULL ||
        hhs159_artifact_kind(executable) != HHS159_ARTIFACT_EXECUTABLE ||
        !read_hash216(executable, executable_id)) goto cleanup;
    if (compiled_receipt != NULL) {
        hhs159_receipt_release(compiled_receipt);
        compiled_receipt = NULL;
    }
    status = hhs159_execute(ctx, executable, &execution, &compiled_receipt);
    if (status != HHS159_STATUS_OK || compiled_receipt == NULL ||
        hhs159_artifact_kind(compiled_receipt) != HHS159_ARTIFACT_RECEIPT ||
        !read_hash216(compiled_receipt, compiled_receipt_id)) goto cleanup;
    if (compiled_receipt->status != HHS159_STATUS_OK ||
        compiled_receipt->committed != 0U ||
        compiled_receipt->fallback_used != 0U) goto cleanup;
    compiled_steps = compiled_receipt->vm81_steps;
    memcpy(compiled_semantic_root, compiled_receipt->semantic_root,
           sizeof(compiled_semantic_root));
    /* A successful diagnostic interpreter call does not authorize source
       effect. Admission must reject the inherited fixed-program trace. */
    if (require_source_effect) {
        if (vmir_fixed_program_marker != 0 ||
            observed_steps == 3U || compiled_steps == 3U ||
            vmir_matrix_times_marker == 0) {
            source_effect_rejected = 1;
            goto cleanup;
        }
        /* Even a future nonfixed trace requires a typed, exact cell-effect
         * and HNAN gate witness from the singleton VM81. Until that
         * adapter exists this probe never approves canonical admission. */
        source_effect_rejected = 1;
        goto cleanup;
    }
    ok = 1;
cleanup:
    if (compiled_receipt != NULL) hhs159_receipt_release(compiled_receipt);
    if (compile_receipt != NULL) hhs159_receipt_release(compile_receipt);
    if (executable != NULL) hhs159_artifact_release(executable);
    if (object != NULL) hhs159_artifact_release(object);
    if (compiler != NULL) hhs159_compiler_release(compiler);
    if (replay_receipt != NULL) hhs159_receipt_release(replay_receipt);
    if (receipt != NULL) hhs159_receipt_release(receipt);
    if (interpreter != NULL) hhs159_interpreter_release(interpreter);
    if (vmir != NULL) hhs159_artifact_release(vmir);
    if (hir != NULL) hhs159_artifact_release(hir);
    if (graph != NULL) hhs159_artifact_release(graph);
    if (types != NULL) hhs159_artifact_release(types);
    if (ast != NULL) hhs159_artifact_release(ast);
    if (cst != NULL) hhs159_artifact_release(cst);
    if (tokens != NULL) hhs159_artifact_release(tokens);
    if (src != NULL) hhs159_source_release(src);
    if (ctx != NULL) hhs159_context_release(ctx);
    free(bytes);
    if (!ok && source_effect_rejected) {
        fprintf(stderr, "NUCLEUS5_SOURCE_EFFECT_NOT_PROVED: canonical admission denied\n");
        return 2;
    }
    if (!ok) {
        fprintf(stderr, "NUCLEUS5_PASS159_FRONTEND_REJECTED status=%d %s\n",
                (int)status, hhs159_status_string(status));
        return 1;
    }
    printf("SOURCE_HASH216=%s\n", source_id);
    printf("AST_HASH216=%s\n", ast_id);
    printf("CONSTRAINT_HASH216=%s\n", graph_id);
    printf("VMIR_HASH216=%s\n", vmir_id);
    printf("VMIR_PAYLOAD_SHA256=%s\n", vmir_payload_sha256);
    printf("VMIR_PAYLOAD_BYTES=%zu\n", vmir_payload_bytes);
    printf("VMIR_EXACT_PROGRAM_MARKER=%d\n", vmir_fixed_program_marker);
    printf("VMIR_MATRIXTIMES_MARKER=%d\n", vmir_matrix_times_marker);
    printf("HELD_RECEIPT_HASH216=%s\n", receipt_id);
    printf("HELD_SEMANTIC_ROOT_HASH216=%s\n", observed_semantic_root);
    printf("HELD_VM81_STEPS=%llu\n", (unsigned long long)observed_steps);
    printf("HELD_COMMITTED=%u\n", observed_commit);
    printf("HELD_FALLBACK=%u\n", observed_fallback);
    printf("OBJECT_HASH216=%s\n", object_id);
    printf("EXECUTABLE_HASH216=%s\n", executable_id);
    printf("COMPILED_RECEIPT_HASH216=%s\n", compiled_receipt_id);
    printf("COMPILED_VM81_STEPS=%llu\n", (unsigned long long)compiled_steps);
    printf("COMPILED_SEMANTIC_ROOT_HASH216=%s\n", compiled_semantic_root);
    puts("NUCLEUS5_PASS159_FRONTEND_HELD_INTERPRET_REPLAY_PASS (NO_CANONICAL_TENSOR_CLOSURE)");
    return 0;
}
