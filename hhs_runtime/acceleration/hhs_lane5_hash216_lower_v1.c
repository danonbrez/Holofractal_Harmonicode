#include "hhs_lane5_hash216_lower_v1.h"
#include <openssl/evp.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <inttypes.h>
static int hex64(const char *s) {
  if(!s || strlen(s)!=64) return 0;
  for(int i=0;i<64;i++) if(!((s[i]>='0'&&s[i]<='9')||(s[i]>='a'&&s[i]<='f'))) return 0;
  return 1;
}
static int word72(const char *s) {
  static const char abc[]="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";
  if(!s || strlen(s)!=72) return 0;
  for(int i=0;i<72;i++) if(!strchr(abc,s[i])) return 0;
  return 1;
}
static void tohex(const unsigned char d[32],char out[65]) {
  static const char abc[]="0123456789abcdef";
  for(int i=0;i<32;i++) {out[2*i]=abc[d[i]>>4];out[2*i+1]=abc[d[i]&15];}
  out[64]=0;
}
static int sha(const char *domain, const unsigned char *body,size_t len,
               unsigned char out[32]) {
  EVP_MD_CTX *ctx=EVP_MD_CTX_new();unsigned int n=0;int ok=0;
  if(!ctx) return 0;
  ok=EVP_DigestInit_ex(ctx,EVP_sha256(),NULL)==1 &&
     EVP_DigestUpdate(ctx,domain,strlen(domain)+1)==1 &&
     EVP_DigestUpdate(ctx,body,len)==1 &&
     EVP_DigestFinal_ex(ctx,out,&n)==1 && n==32;
  EVP_MD_CTX_free(ctx);return ok;
}
static int root_sha(const unsigned char *body,size_t len,unsigned char out[32]){
  return sha("HHS-P174-HASH216-INDEX-ROOT-V1",body,len,out);
}
int hhs_hash216_lower_pass174(const hhs_hash216_lower_input *in,
                              hhs_hash216_lower_output *out) {
  if(!in||!out||!hex64(in->genesis_identity)||!hex64(in->legacy_foundation_root)||
     !hex64(in->operation_identity)||!word72(in->previous)||
     !word72(in->change)||!word72(in->receipt)) return -1;
  hhs_hash216_lower_output *tmp=calloc(1,sizeof(*tmp));
  if(!tmp) return -1;
  int rc=-1;char body[2048];unsigned char digest[32],prior[32]={0};
  unsigned char index_bytes[216*32];char priorhex[65];
  memset(priorhex,'0',64);priorhex[64]=0;
  memcpy(tmp->combined,in->previous,72);
  memcpy(tmp->combined+72,in->change,72);
  memcpy(tmp->combined+144,in->receipt,72);
  int n=snprintf(body,sizeof(body),
    "{\"genesis_identity\":\"%s\",\"legacy_foundation_root\":\"%s\",\"logical_step\":%" PRIu64 ",\"operation_identity\":\"%s\",\"predecessor\":\"%s\",\"current\":\"%s\",\"schema\":\"HHS_P174_HASH216_ARRAY_V1\",\"successor\":\"%s\"}",
    in->genesis_identity,in->legacy_foundation_root,in->logical_step,
    in->operation_identity,in->previous,in->change,in->receipt);
  /* Python sort_keys orders current before genesis_identity, so build
   * the definitive canonical serialization separately below. */
  n=snprintf(body,sizeof(body),
    "{\"current\":\"%s\",\"genesis_identity\":\"%s\",\"legacy_foundation_root\":\"%s\",\"logical_step\":%" PRIu64 ",\"operation_identity\":\"%s\",\"predecessor\":\"%s\",\"schema\":\"HHS_P174_HASH216_ARRAY_V1\",\"successor\":\"%s\"}",
    in->change,in->genesis_identity,in->legacy_foundation_root,in->logical_step,
    in->operation_identity,in->previous,in->receipt);
  if(n<0||(size_t)n>=sizeof(body)||!sha("HHS-P174-HASH216-ARRAY-V1",(unsigned char*)body,(size_t)n,digest))goto done;
  tohex(digest,tmp->logical_identity_sha256);
  for(int i=0;i<216;i++) {
    n=snprintf(body,sizeof(body),
      "{\"absolute_position\":%d,\"character\":\"%c\",\"genesis_identity\":\"%s\",\"lane\":%d,\"lane_position\":%d,\"legacy_foundation_root\":\"%s\",\"logical_identity_sha256\":\"%s\",\"logical_step\":%" PRIu64 ",\"operation_identity\":\"%s\",\"prior_character_index_sha256\":\"%s\",\"schema\":\"HHS_P174_HASH216_CHARACTER_INDEX_V1\"}",
      i,tmp->combined[i],in->genesis_identity,i/72,i%72,in->legacy_foundation_root,
      tmp->logical_identity_sha256,in->logical_step,in->operation_identity,priorhex);
    if(n<0||(size_t)n>=sizeof(body)||
       !sha("HHS-P174-HASH216-CHARACTER-V1",(unsigned char*)body,(size_t)n,digest))goto done;
    memcpy(index_bytes+i*32,digest,32);
    memcpy(prior,digest,32);
    tohex(prior,tmp->character_indexes_sha256[i]);
    memcpy(priorhex,tmp->character_indexes_sha256[i],65);
  }
  if(!root_sha(index_bytes,sizeof(index_bytes),digest))goto done;
  tohex(digest,tmp->index_root_sha256);
  memcpy(out,tmp,sizeof(*tmp));rc=0;
done:
  free(tmp);return rc;
}
