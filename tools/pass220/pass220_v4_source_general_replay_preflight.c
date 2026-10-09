/*
 * Pass220: source-general native Pass159 HOLD/replay/compiler parity.
 * Pre-admission evidence ONLY: no gate truth is inferred and no signed
 * VM81/PQC or canonical state mutation operation is invoked.
 *
 * Source and equality-occurrence identity are computed from exact bytes.
 * Receipt fields exposed by Pass159's internal diagnostic ABI are observations
 * only (the general Pass159 VMIR may use a fixed EXACT_PROGRAM artifact).
 */
#include "hhs159_internal.h"
#include "hhs_pass159_api.h"

#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define GATE_COUNT 40U
#define MAX_BYTES UINT64_C(1048576)
#define SRC_EXPECTED_BYTES 527U

static int read_bytes(const char *path, uint8_t **out, size_t *n) {
    FILE *fp = fopen(path, "rb");
    long end;
    uint8_t *v;
    if (fp == NULL) return 0;
    if (fseek(fp, 0L, SEEK_END) != 0 || (end = ftell(fp)) <= 0 ||
        fseek(fp, 0L, SEEK_SET) != 0) { fclose(fp); return 0; }
    v = (uint8_t *)malloc((size_t)end);
    if (v == NULL) { fclose(fp); return 0; }
    if (fread(v, 1U, (size_t)end, fp) != (size_t)end) {
        free(v); fclose(fp); return 0;
    }
    fclose(fp);
    *out = v; *n = (size_t)end;
    return 1;
}
static void print_hex(const uint8_t *input, size_t n) {
    size_t j;
    for (j = 0U; j < n; j++) printf("%02x", (unsigned)input[j]);
}
static int copy_hash216(const void *handle, char output[HHS159_HASH216_LENGTH + 1U]) {
    HHS159MutableByteSpan span;
    memset(output, 0, HHS159_HASH216_LENGTH + 1U);
    span.data = (uint8_t *)output;
    span.capacity = HHS159_HASH216_LENGTH;
    span.size_written = 0U;
    if (hhs159_get_hash216(handle, &span) != HHS159_STATUS_OK ||
        span.size_written != HHS159_HASH216_LENGTH) return 0;
    output[HHS159_HASH216_LENGTH] = '\0';
    return 1;
}
static int scan_exact_gates(const uint8_t *data, size_t n) {
    size_t i;
    uint32_t count = 0U;
    uint32_t depth = 0U;
    int outer_index = 0;
    for (i = 0U; i < n; i++) {
        if (data[i] == '(') depth++;
        else if (data[i] == ')') {
            if (depth == 0U) return 0;
            depth--;
        }
        if (data[i] == '=' && i + 1U < n && data[i+1U] == '=') {
            uint8_t material[SHA256_DIGEST_LENGTH + 12U];
            uint8_t digest[SHA256_DIGEST_LENGTH];
            size_t k;
            static const uint8_t domain[4] = {'G','A','T','E'};
            if (count == GATE_COUNT) return 0;
            if (depth == 0U) {
                if ((outer_index == 0 && i != 253U) ||
                    (outer_index == 1 && i != 256U) || outer_index >= 2)
                    return 0;
                outer_index++;
            }
            memcpy(material, domain, 4U);
            material[4] = (uint8_t)(count >> 24U);
            material[5] = (uint8_t)(count >> 16U);
            material[6] = (uint8_t)(count >> 8U);
            material[7] = (uint8_t)count;
            material[8] = (uint8_t)(i >> 24U);
            material[9] = (uint8_t)(i >> 16U);
            material[10] = (uint8_t)(i >> 8U);
            material[11] = (uint8_t)i;
            for (k=0U;k<SHA256_DIGEST_LENGTH;k++)material[12U+k]=(uint8_t)0U;
            /* This marker is occurrence metadata only, not a gate truth value.
             * Source-specific SHA256 root is printed and bound by CI below. */
            if (SHA256(material, sizeof(material), digest) == NULL) return 0;
            printf("gate_%02u_offset=%zu;depth=%u;truth=UNRESOLVED\n",
                count, i, depth);
            count++;
            i++;
        }
    }
    if (count != GATE_COUNT || depth != 0U || outer_index != 2) return 0;
    return 1;
}
static int valid72(const char *str) {
    return str != NULL && strlen(str) == HHS159_HASH72_LENGTH;
}
static int receipt_consistent(const HHS159Receipt *r, const HHS159Source *src) {
    return r != NULL && src != NULL &&
        hhs159_artifact_kind(r) == HHS159_ARTIFACT_RECEIPT &&
        r->status == HHS159_STATUS_OK && r->committed == 0U &&
        r->fallback_used == 0U && r->vm81_steps > 0U &&
        strlen(r->semantic_root) == HHS159_HASH216_LENGTH &&
        valid72(r->hash72) &&
        strcmp(r->base.source_root, src->base.hash216) == 0;
}
int main(int argc, char **argv) {
    uint8_t *data = NULL;
    size_t n = 0U;
    uint8_t digest[SHA256_DIGEST_LENGTH];
    HHS159ContextConfig cfg;
    HHS159SourceOpenOptions open_options;
    HHS159ExecutionOptions exec_options;
    HHS159CompareResult parity;
    HHS159ByteSpan bytes;
    HHS159Context *ctx = NULL;
    HHS159Source *source = NULL;
    HHS159Interpreter *interpreter = NULL;
    HHS159Receipt *hold = NULL;
    HHS159Receipt *replay = NULL;
    HHS159Status status;
    static const uint8_t name[] = "pass220-v4-source-general-preflight";
    static const uint8_t encoding[] = "UTF-8";
    char source_hash[HHS159_HASH216_LENGTH+1U];
    char hold_hash[HHS159_HASH216_LENGTH+1U];
    char replay_hash[HHS159_HASH216_LENGTH+1U];
    int ok = 0;
    if (argc != 2 || !read_bytes(argv[1], &data, &n)) {
        fprintf(stderr,"P220_V4_SOURCE_NOT_READABLE\n");return 2;
    }
    if (n != SRC_EXPECTED_BYTES || data[n-1U] != '\n' ||
        SHA256(data,n,digest) == NULL) {
        fprintf(stderr,"P220_V4_SOURCE_LENGTH_OR_SHA_INVALID\n");goto cleanup;
    }
    printf("source_sha256=");print_hex(digest,sizeof(digest));puts("");
    printf("source_bytes=%zu\n",n);
    if (!scan_exact_gates(data,n)) {
        fprintf(stderr,"P220_V4_SOURCE_OCCURRENCES_INVALID\n");goto cleanup;
    }
    printf("gate_occurrences=%u\n",GATE_COUNT);

    memset(&cfg,0,sizeof(cfg));
    cfg.header.struct_size=(uint32_t)sizeof(cfg);
    cfg.header.struct_version=HHS159_STRUCT_VERSION_1;
    cfg.max_source_bytes=MAX_BYTES;
    cfg.max_tokens=UINT64_C(200000);
    cfg.max_nesting=UINT64_C(4096);
    cfg.max_output_bytes=UINT64_C(4194304);
    cfg.flags=HHS159_FLAG_ORDERED;
    if (hhs159_context_create(&cfg,&ctx) != HHS159_STATUS_OK)goto cleanup;

    memset(&open_options,0,sizeof(open_options));
    open_options.header.struct_size=(uint32_t)sizeof(open_options);
    open_options.header.struct_version=HHS159_STRUCT_VERSION_1;
    open_options.source_name.data=name;
    open_options.source_name.size=sizeof(name)-1U;
    open_options.encoding.data=encoding;
    open_options.encoding.size=sizeof(encoding)-1U;
    open_options.flags=HHS159_FLAG_ORDERED;
    open_options.preserve_bom=1U;
    bytes.data=data; bytes.size=n;
    if (hhs159_source_open_bytes(ctx,bytes,&open_options,&source)!=HHS159_STATUS_OK ||
        !copy_hash216(source,source_hash))goto cleanup;
    printf("source_hash216=%s\n",source_hash);
    if (hhs159_interpreter_create(ctx,&interpreter)!=HHS159_STATUS_OK)goto cleanup;

    memset(&exec_options,0,sizeof(exec_options));
    exec_options.header.struct_size=(uint32_t)sizeof(exec_options);
    exec_options.header.struct_version=HHS159_STRUCT_VERSION_1;
    exec_options.mode=HHS159_MODE_EXECUTE_AND_HOLD;
    exec_options.commit_policy=0U;
    exec_options.max_vm81_steps=UINT64_C(1000000);
    exec_options.max_recursion=UINT64_C(4096);
    exec_options.max_output_bytes=UINT64_C(4194304);
    status=hhs159_interpret(interpreter,source,&exec_options,&hold);
    printf("hold_status=%d\n",(int)status);
    if (status!=HHS159_STATUS_OK || !receipt_consistent(hold,source) ||
        !copy_hash216(hold,hold_hash))goto cleanup;
    printf("hold_vm81_steps=%llu\n",(unsigned long long)hold->vm81_steps);
    printf("hold_receipt_hash216=%s\n",hold_hash);

    status=hhs159_interpreter_replay(interpreter,hold,&replay);
    printf("replay_status=%d\n",(int)status);
    if (status!=HHS159_STATUS_OK || !receipt_consistent(replay,source) ||
        !copy_hash216(replay,replay_hash) ||
        strcmp(hold->semantic_root,replay->semantic_root)!=0 ||
        hold->vm81_steps != replay->vm81_steps)goto cleanup;
    printf("replay_semantic_root_equal=1\n");
    printf("replay_receipt_hash216=%s\n",replay_hash);

    memset(&parity,0,sizeof(parity));
    parity.header.struct_size=(uint32_t)sizeof(parity);
    parity.header.struct_version=HHS159_STRUCT_VERSION_1;
    status=hhs159_compare_interpreter_compiler(ctx,source,&exec_options,&parity);
    printf("interpreter_compiler_status=%d\n",(int)status);
    if (status!=HHS159_STATUS_OK || parity.status!=HHS159_STATUS_OK ||
        parity.matched!=1U || parity.fallback_used!=0U)goto cleanup;
    printf("interpreter_compiler_match=1\n");
    printf("native_hold_committed=0\n");
    printf("canonical_vm81_admission_verified=0\n");
    printf("all_40_gate_truth_witnesses_verified=0\n");
    puts("global_gate_proof_status=UNRESOLVED");
    puts("native_source_preflight=PASS");
    ok=1;

cleanup:
    if(replay!=NULL)hhs159_receipt_release(replay);
    if(hold!=NULL)hhs159_receipt_release(hold);
    if(interpreter!=NULL)hhs159_interpreter_release(interpreter);
    if(source!=NULL)hhs159_source_release(source);
    if(ctx!=NULL)hhs159_context_release(ctx);
    free(data);
    if(!ok)fprintf(stderr,"P220_V4_SOURCE_GENERAL_PREFLIGHT_FAILED\n");
    return ok?0:1;
}
