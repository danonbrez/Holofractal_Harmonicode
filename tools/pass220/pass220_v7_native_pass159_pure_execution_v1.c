/* V7: execute original 70-byte tensor through inherited Pass159 PURE mode.
 * This source-specific probe is not an alternate HHS kernel, interpreter or
 * quotient implementation. It never requests a signed VM81 commit.
 */
#include "hhs_pass159_api.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const uint8_t SOURCE[] =
  "(81*64)/((yx,y+w,wx),(-xy-wz,x+y-z-w+xy+yx-zw-wz,-zw-yx),(xy,x-z,zw))\n";

static int read_exact_source(const char *path,uint8_t *buf,size_t n){
    FILE *fp=fopen(path,"rb");
    size_t got;
    int last;
    if(fp==NULL)return 0;
    got=fread(buf,1,n,fp);
    last=fgetc(fp);
    if(ferror(fp) || fclose(fp)!=0)return 0;
    return got==n && last==EOF && memcmp(buf,SOURCE,n)==0;
}
static int receipt_glyphs(const void *artifact,
                         char out[HHS159_HASH216_LENGTH+1U]){
    HHS159MutableByteSpan dst;
    memset(out,0,HHS159_HASH216_LENGTH+1U);
    memset(&dst,0,sizeof(dst));
    dst.data=(uint8_t *)out;
    dst.capacity=HHS159_HASH216_LENGTH;
    if(hhs159_get_hash216(artifact,&dst)!=HHS159_STATUS_OK ||
       dst.size_written!=HHS159_HASH216_LENGTH)return 0;
    out[HHS159_HASH216_LENGTH]='\0';
    return 1;
}
int main(int argc,char **argv){
    HHS159ContextConfig cfg;
    HHS159SourceOpenOptions open;
    HHS159ExecutionOptions opts;
    HHS159ByteSpan bytes;
    HHS159Context *ctx=NULL;
    HHS159Source *source=NULL;
    HHS159Interpreter *interpreter=NULL;
    HHS159Receipt *pure=NULL,*replay=NULL;
    HHS159Status pure_status=HHS159_STATUS_INVALID_STATE;
    HHS159Status replay_status=HHS159_STATUS_INVALID_STATE;
    static const uint8_t name[]="pass220-v7-native-pure-evaluate";
    static const uint8_t utf8[]="UTF-8";
    uint8_t buffer[sizeof(SOURCE)-1U];
    unsigned char digest[SHA256_DIGEST_LENGTH];
    char glyphs[HHS159_HASH216_LENGTH+1U];
    int opened=0;
    size_t i;
    if(argc!=2 || !read_exact_source(argv[1],buffer,sizeof(buffer))){
        puts("v7_exact_source=REJECTED");
        return 3;
    }
    if(SHA256(buffer,sizeof(buffer),digest)==NULL)return 2;
    memset(&cfg,0,sizeof(cfg));
    cfg.header.struct_size=(uint32_t)sizeof(cfg);
    cfg.header.struct_version=HHS159_STRUCT_VERSION_1;
    cfg.max_source_bytes=UINT64_C(1048576);
    cfg.max_tokens=UINT64_C(200000);
    cfg.max_nesting=UINT64_C(4096);
    cfg.max_output_bytes=UINT64_C(4194304);
    cfg.deterministic_epoch=UINT64_C(0);
    cfg.flags=HHS159_FLAG_ORDERED;
    if(hhs159_context_create(&cfg,&ctx)!=HHS159_STATUS_OK)goto cleanup;
    memset(&open,0,sizeof(open));
    open.header.struct_size=(uint32_t)sizeof(open);
    open.header.struct_version=HHS159_STRUCT_VERSION_1;
    open.source_name.data=name;
    open.source_name.size=sizeof(name)-1U;
    open.encoding.data=utf8;
    open.encoding.size=sizeof(utf8)-1U;
    open.flags=HHS159_FLAG_ORDERED;
    open.preserve_bom=1U;
    bytes.data=buffer;
    bytes.size=sizeof(buffer);
    if(hhs159_source_open_bytes(ctx,bytes,&open,&source)!=HHS159_STATUS_OK)
        goto cleanup;
    opened=1;
    if(hhs159_interpreter_create(ctx,&interpreter)!=HHS159_STATUS_OK)
        goto cleanup;
    memset(&opts,0,sizeof(opts));
    opts.header.struct_size=(uint32_t)sizeof(opts);
    opts.header.struct_version=HHS159_STRUCT_VERSION_1;
    opts.mode=HHS159_MODE_EVALUATE_PURE;
    opts.commit_policy=0U; /* explicitly never commit */
    opts.max_vm81_steps=UINT64_C(100000);
    opts.max_recursion=UINT64_C(4096);
    opts.max_output_bytes=UINT64_C(4194304);
    pure_status=hhs159_interpret(interpreter,source,&opts,&pure);
    if(pure_status==HHS159_STATUS_OK && pure!=NULL){
        if(receipt_glyphs(pure,glyphs)){
            printf("pure_candidate_hash216=%s\n",glyphs);
            replay_status=hhs159_interpreter_replay(interpreter,pure,&replay);
            if(replay_status==HHS159_STATUS_OK && replay!=NULL &&
               receipt_glyphs(replay,glyphs))
                printf("pure_replay_hash216=%s\n",glyphs);
        }
    }
cleanup:
    printf("v7_exact_source=%s\n",opened?"VERIFIED":"OPEN_FAILED");
    printf("source_sha256=");
    for(i=0U;i<SHA256_DIGEST_LENGTH;i++)printf("%02x",(unsigned)digest[i]);
    putchar('\n');
    printf("source_bytes=%zu\n",sizeof(buffer));
    puts("native_runtime=PASS159_INHERITED");
    puts("native_execution_mode=EVALUATE_PURE");
    puts("native_commit_policy=0");
    printf("pure_native_status=%d\n",(int)pure_status);
    printf("pure_replay_status=%d\n",(int)replay_status);
    puts("native_matrix_quotient_result_certified=0");
    puts("source_specific_signed_vm81_commit=0");
    puts("source_specific_hash72_hash216_canonical_receipt=0");
    if(replay!=NULL)hhs159_receipt_release(replay);
    if(pure!=NULL)hhs159_receipt_release(pure);
    if(interpreter!=NULL)hhs159_interpreter_release(interpreter);
    if(source!=NULL)hhs159_source_release(source);
    if(ctx!=NULL)hhs159_context_release(ctx);
    return opened?0:2; /* pure failure is explicitly surfaced as evidence */
}
