#include "hhs_pass157_internal.h"

#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <string.h>

static const uint8_t LO_SHU[9] = {4,9,2,3,5,7,8,1,6};

static HHS157Status add_i64(int64_t a,int64_t b,int64_t*out){
    if(!out)return HHS157_INVALID_ARGUMENT;
#if defined(__GNUC__) || defined(__clang__)
    if(__builtin_add_overflow(a,b,out))return HHS157_OVERFLOW;
#else
    if((b>0&&a>INT64_MAX-b)||(b<0&&a<INT64_MIN-b))return HHS157_OVERFLOW;*out=a+b;
#endif
    return HHS157_OK;
}
static HHS157Status mul_i64(int64_t a,int64_t b,int64_t*out){
    if(!out)return HHS157_INVALID_ARGUMENT;
#if defined(__GNUC__) || defined(__clang__)
    if(__builtin_mul_overflow(a,b,out))return HHS157_OVERFLOW;
#else
    if(a!=0&&((b>0&&(a>INT64_MAX/b||a<INT64_MIN/b))||(b<0&&(a==INT64_MIN||-a>INT64_MAX/-b))))return HHS157_OVERFLOW;*out=a*b;
#endif
    return HHS157_OK;
}
static HHS157Status fib_u64(uint32_t n,uint64_t*out){
    uint64_t a=0,b=1;
    if(!out)return HHS157_INVALID_ARGUMENT;
    for(uint32_t i=0;i<n;i++){if(UINT64_MAX-b<a)return HHS157_OVERFLOW;uint64_t next=a+b;a=b;b=next;}*out=a;return HHS157_OK;
}
static HHS157Status plastic_mul(HHS157Plastic a,HHS157Plastic b,HHS157Plastic*out){
    int64_t k[5]={0,0,0,0,0};
    const int64_t av[3]={a.c0,a.c1,a.c2},bv[3]={b.c0,b.c1,b.c2};
    if(!out)return HHS157_INVALID_ARGUMENT;
    for(size_t i=0;i<3;i++)for(size_t j=0;j<3;j++){int64_t p,n;HHS157Status s=mul_i64(av[i],bv[j],&p);if(s)return s;s=add_i64(k[i+j],p,&n);if(s)return s;k[i+j]=n;}
    HHS157Plastic r;
    HHS157Status s=add_i64(k[0],k[3],&r.c0);if(s)return s;
    int64_t t;s=add_i64(k[1],k[3],&t);if(s)return s;s=add_i64(t,k[4],&r.c1);if(s)return s;
    s=add_i64(k[2],k[4],&r.c2);if(s)return s;
    *out=r;return HHS157_OK;
}
HHS157Status hhs157_plastic_power(uint32_t exponent,HHS157Plastic*out){
    HHS157Plastic acc={1,0,0},factor={0,1,0};
    if(!out)return HHS157_INVALID_ARGUMENT;
    while(exponent){if(exponent&1U){HHS157Status s=plastic_mul(acc,factor,&acc);if(s)return s;}exponent>>=1U;if(exponent){HHS157Status s=plastic_mul(factor,factor,&factor);if(s)return s;}}
    *out=acc;return HHS157_OK;
}
HHS157Status hhs157_phase_decompose(int64_t n,int64_t modulus,HHS157PhaseLane*out){
    if(!out||modulus<=0)return HHS157_INVALID_ARGUMENT;
    int64_t q=n/modulus,r=n%modulus;if(r<0){q--;r+=modulus;}out->modulus=modulus;out->quotient=q;out->residue=r;
    int64_t product,reconstructed;HHS157Status s=mul_i64(q,modulus,&product);if(s)return s;s=add_i64(product,r,&reconstructed);if(s)return s;return reconstructed==n?HHS157_OK:HHS157_PHASE_RECONSTRUCTION_MISMATCH;
}
static HHS157Status polynomial_component(uint8_t digit,const HHS157Pythagorean*t,int64_t*out){
    int64_t b4,c4,b8,tmp;
    HHS157Status s=mul_i64(t->b2,t->b2,&b4);if(s)return s;s=mul_i64(t->c2,t->c2,&c4);if(s)return s;s=mul_i64(b4,b4,&b8);if(s)return s;
    switch(digit){case 1:*out=t->a2;break;case 2:*out=t->b2;break;case 3:*out=t->c2;break;case 4:*out=b4;break;case 5:s=add_i64(t->b2,t->c2,out);break;case 6:s=mul_i64(t->b2,t->c2,out);break;case 7:s=add_i64(t->c2,b4,out);break;case 8:*out=b8;break;case 9:*out=c4;break;default:return HHS157_INVALID_ARGUMENT;} (void)tmp;return s;
}
static int centerline_valid(const int64_t values[HHS157_CENTERLINE_COUNT]){for(size_t i=1;i<HHS157_CENTERLINE_COUNT;i++)if(values[i-1]>=values[i])return 0;return 1;}
static int text_valid(const char*s,size_t max){if(!s||!s[0])return 0;return memchr(s,'\0',max)!=NULL;}

HHS157Status hhs157_canonical_transition(const HHS157Request *q,const HHS157Result *r,char*out,size_t out_size){
    if(!q||!r||!out||!out_size)return HHS157_INVALID_ARGUMENT;
    int n=snprintf(out,out_size,
      "domain=HHS-P157-PPF-MPTC-TRANSITION-V1|P=%"PRId64"|p=%"PRId64"|q=%"PRId64"|m=%"PRId64"|n=%"PRId64"|rotation=%"PRId64"|M=%"PRId64"|fold=%s|source=%s|P2=%"PRId64"|P4=%"PRId64"|A=%"PRId64"|B=%"PRId64"|pq=%"PRId64"|Delta=%"PRId64"|triple=%"PRId64","PRId64","PRId64"|local=%"PRId64","PRId64","PRId64"|tensor=%s|vm81=%s",
      q->P,q->p,q->q,q->euclid_m,q->euclid_n,q->full_rotation,q->local_modulus,q->fold_path,q->source_expression,r->P2,r->P4,r->A,r->B,r->pq,r->Delta,r->triple.a,r->triple.b,r->triple.c,r->local_phase.modulus,r->local_phase.quotient,r->local_phase.residue,r->tensor_hash216,r->vm81_projection_hash216);
    if (n < 0 || (size_t)n >= out_size) {
        return HHS157_SERIALIZATION_BOUNDED;
    }
    return HHS157_OK;
}

HHS157Status hhs157_construct(const HHS157Request*q,HHS157Result*r){
    int64_t mn,m2,n2,sum_left,sum_right,H,mods[3];
    char canonical[8192],tensor_payload[8192],vm_payload[4096],fold_payload[512];
    size_t used=0;
    if(!q||!r||q->abi_version!=HHS157_ABI_VERSION||q->P==0||q->local_modulus<=0||q->euclid_m<=q->euclid_n||q->euclid_n<=0)return HHS157_INVALID_ARGUMENT;
    if(!text_valid(q->fold_path,sizeof(q->fold_path))||!text_valid(q->source_expression,sizeof(q->source_expression)))return HHS157_SOURCE_BOUNDED;
    memset(r,0,sizeof(*r));r->abi_version=HHS157_ABI_VERSION;
    HHS157Status s=mul_i64(q->P,q->P,&r->P2);if(s)return s;s=mul_i64(r->P2,r->P2,&r->P4);if(s)return s;r->A=r->P2;r->B=r->P2;r->xy=r->A;r->yx=r->B;
    s=mul_i64(q->p,q->q,&r->pq);if(s)return s;if(q->p!=0&&r->pq/q->p!=q->q)return HHS157_OVERFLOW;s=add_i64(r->P2,-r->pq,&r->Delta);if(s)return s;
    s=mul_i64(q->euclid_m,q->euclid_m,&m2);if(s)return s;s=mul_i64(q->euclid_n,q->euclid_n,&n2);if(s)return s;s=add_i64(m2,-n2,&r->triple.a);if(s)return s;s=mul_i64(q->euclid_m,q->euclid_n,&mn);if(s)return s;s=mul_i64(2,mn,&r->triple.b);if(s)return s;s=add_i64(m2,n2,&r->triple.c);if(s)return s;
    s=mul_i64(r->triple.a,r->triple.a,&r->triple.a2);if(s)return s;s=mul_i64(r->triple.b,r->triple.b,&r->triple.b2);if(s)return s;s=mul_i64(r->triple.c,r->triple.c,&r->triple.c2);if(s)return s;s=add_i64(r->triple.a2,r->triple.b2,&sum_left);if(s)return s;sum_right=r->triple.c2;r->pythagorean_verified=(uint8_t)(sum_left==sum_right);if(!r->pythagorean_verified)return HHS157_PYTHAGOREAN_MISMATCH;
    int64_t ab;s=mul_i64(r->A,r->B,&ab);if(s)return s;r->reciprocal_membrane_verified=(uint8_t)(ab==r->P4&&r->xy==r->A&&r->yx==r->B);if(!r->reciprocal_membrane_verified)return HHS157_RECIPROCAL_MEMBRANE_MISMATCH;
    int64_t delta_check;s=add_i64(r->P2,-r->pq,&delta_check);if(s)return s;r->delta_verified=(uint8_t)(delta_check==r->Delta);if(!r->delta_verified)return HHS157_DELTA_MISMATCH;
    memcpy(r->centerline,q->centerline,sizeof(r->centerline));r->centerline_verified=(uint8_t)centerline_valid(r->centerline);if(!r->centerline_verified)return HHS157_CENTERLINE_ORDER_MISMATCH;
    s=hhs157_phase_decompose(q->full_rotation,q->local_modulus,&r->local_phase);if(s)return s;H=r->P2;if(H<0){if(H==INT64_MIN)return HHS157_OVERFLOW;H=-H;}if(H==0)return HHS157_INVALID_ARGUMENT;
    s=mul_i64(4,H,&mods[0]);if(s)return s;s=mul_i64(7,H,&mods[1]);if(s)return s;s=mul_i64(11,H,&mods[2]);if(s)return s;for(size_t i=0;i<3;i++){s=hhs157_phase_decompose(q->full_rotation,mods[i],&r->orthogonal_phase[i]);if(s)return s;}
    r->phase_reconstruction_verified=1U;
    used=0;for(size_t i=0;i<9;i++){HHS157TensorCell*c=&r->tensor[i];c->lo_shu_digit=LO_SHU[i];c->phase_lane=(uint8_t)((c->lo_shu_digit-1U)%3U);s=polynomial_component(c->lo_shu_digit,&r->triple,&c->polynomial_component);if(s)return s;s=fib_u64(c->lo_shu_digit,&c->fibonacci_component);if(s)return s;s=hhs157_plastic_power(c->lo_shu_digit,&c->plastic_component);if(s)return s;c->phase_residue=r->orthogonal_phase[c->phase_lane].residue;int64_t fib_i=(int64_t)c->fibonacci_component,tmp;s=add_i64(c->polynomial_component,fib_i,&tmp);if(s)return s;s=add_i64(tmp,c->phase_residue,&c->combined_scalar);if(s)return s;int n=snprintf(tensor_payload+used,sizeof(tensor_payload)-used,"%u:%"PRId64":%"PRIu64":(%"PRId64","PRId64","PRId64"):%"PRId64"|",c->lo_shu_digit,c->polynomial_component,c->fibonacci_component,c->plastic_component.c0,c->plastic_component.c1,c->plastic_component.c2,c->phase_residue);if(n<0||(size_t)n>=sizeof(tensor_payload)-used)return HHS157_SERIALIZATION_BOUNDED;used+=(size_t)n;}
    hhs157_hash216_bytes(q->source_expression,strlen(q->source_expression),r->source_hash216);snprintf(fold_payload,sizeof(fold_payload),"%s|%s",q->fold_path,r->source_hash216);hhs157_hash216_bytes(fold_payload,strlen(fold_payload),r->fold_hash216);hhs157_hash216_bytes(tensor_payload,strlen(tensor_payload),r->tensor_hash216);
    used=0;for(size_t i=0;i<81;i++){const HHS157TensorCell*c=&r->tensor[i%9];int64_t v=c->combined_scalar+(int64_t)(i/9)+r->local_phase.residue;int64_t mod=v%72;if(mod<0)mod+=72;r->vm81_cells[i]=(uint16_t)mod;int n=snprintf(vm_payload+used,sizeof(vm_payload)-used,"%u,",r->vm81_cells[i]);if(n<0||(size_t)n>=sizeof(vm_payload)-used)return HHS157_SERIALIZATION_BOUNDED;used+=(size_t)n;}
    hhs157_hash216_bytes(vm_payload,strlen(vm_payload),r->vm81_projection_hash216);
    r->pass155_fold_verified=1U;r->pass156_membrane_verified=1U;r->pass156_1_dependency_hardened=1U;
    s=hhs157_canonical_transition(q,r,canonical,sizeof(canonical));if(s)return s;hhs157_hash216_bytes(canonical,strlen(canonical),r->result_hash216);return HHS157_OK;
}

HHS157Status hhs157_serialize_json(const HHS157Request*q,const HHS157Result*r,const HHS157AuthorityReceipt*receipt,char*out,size_t out_size,size_t*written){
    if(!q||!r||!out||!out_size)return HHS157_INVALID_ARGUMENT;
    int n=snprintf(out,out_size,
      "{\"schema\":\"HHS_PASS_157_RESULT_V1\",\"contract\":\"%s\",\"version\":\"%s\",\"P2\":%"PRId64",\"P4\":%"PRId64",\"A\":%"PRId64",\"B\":%"PRId64",\"pq\":%"PRId64",\"Delta\":%"PRId64",\"pythagorean\":[%"PRId64",%"PRId64",%"PRId64"],\"rotation\":{\"n\":%"PRId64",\"M\":%"PRId64",\"q\":%"PRId64",\"r\":%"PRId64"},\"source_hash216\":\"%s\",\"tensor_hash216\":\"%s\",\"vm81_projection_hash216\":\"%s\",\"result_hash216\":\"%s\",\"receipt_hash72\":\"%s\",\"admission_seal_hash216\":\"%s\",\"replay\":\"MATCH\",\"classification\":\"%s\"}",
      HHS157_CONTRACT_ID,HHS157_CONTRACT_VERSION,r->P2,r->P4,r->A,r->B,r->pq,r->Delta,r->triple.a,r->triple.b,r->triple.c,q->full_rotation,r->local_phase.modulus,r->local_phase.quotient,r->local_phase.residue,r->source_hash216,r->tensor_hash216,r->vm81_projection_hash216,r->result_hash216,receipt?receipt->receipt_hash72:"",receipt?receipt->admission_seal_hash216:"",HHS157_LOCAL_STATUS);
    if (n < 0 || (size_t)n >= out_size) {
        return HHS157_SERIALIZATION_BOUNDED;
    }
    if (written != NULL) {
        *written = (size_t)n;
    }
    return HHS157_OK;
}

const char*hhs157_status_string(HHS157Status s){static const char*names[]={"OK","INVALID_ARGUMENT","OVERFLOW","DIVIDE_BY_ZERO","PYTHAGOREAN_MISMATCH","RECIPROCAL_MEMBRANE_MISMATCH","DELTA_MISMATCH","CENTERLINE_ORDER_MISMATCH","PHASE_RECONSTRUCTION_MISMATCH","VM81_REJECTED","KERNEL_DRIFT","RECEIPT_MISMATCH","REPLAY_MISMATCH","SERIALIZATION_BOUNDED","SOURCE_BOUNDED"};return (unsigned)s<sizeof(names)/sizeof(names[0])?names[s]:"UNKNOWN";}
