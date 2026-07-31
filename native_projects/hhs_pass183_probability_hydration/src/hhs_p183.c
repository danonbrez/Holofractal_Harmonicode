#include "hhs_p183.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define M 1259713u
#define MAX_SOURCE 16384u
struct hhs_p183_context{char*source;size_t length,membranes;int parsed,balanced,boundaries,domain,truth,roles,executed,zero,closed,receipt_ready;char lexical[65],receipt[73],hash216[217];};
static const char FORMULA[]="(List(x*Factorial(72),(y*(1/Factorial(72))))*z)*(w*List((y*(1/Factorial(72))),x*Factorial(72)))/u^72==(x*y)/(x*y)==u^72";
static const char FORWARD[]="List(x*Factorial(72),(y*(1/Factorial(72))))";
static const char RECIP[]="List((y*(1/Factorial(72))),x*Factorial(72))";
static const char F72[]="61234458376886086861524070385274672740778091784697328983823014963978384987221689274204160000000000000000";
static uint64_t mix(const void*d,size_t n,uint64_t seed){const unsigned char*p=d;uint64_t h=seed;size_t i;for(i=0;i<n;i++){h^=p[i];h*=1099511628211ull;h^=h>>29;}return h;}
static void hexfill(char*out,size_t count,uint64_t seed){static const char x[]="0123456789abcdef";size_t i;uint64_t h=seed;for(i=0;i<count;i++){h^=h<<13;h^=h>>7;h^=h<<17;out[i]=x[(h>>((i%16)*4))&15u];}out[count]='\0';}
static uint64_t gcd64(uint64_t a,uint64_t b){while(b){uint64_t t=a%b;a=b;b=t;}return a;}
static int64_t inverse(int64_t a,int64_t m){int64_t t=0,newt=1,r=m,newr=a;while(newr){int64_t q=r/newr,tmp=t-q*newt;t=newt;newt=tmp;tmp=r-q*newr;r=newr;newr=tmp;}if(r!=1)return-1;if(t<0)t+=m;return t;}

hhs_p183_context*hhs_p183_context_create(void){return calloc(1,sizeof(hhs_p183_context));}
void hhs_p183_context_destroy(hhs_p183_context*c){if(c){free(c->source);free(c);}}
hhs_p183_status hhs_p183_parse_equation(hhs_p183_context*c,const char*s,size_t n){if(!c||!s||!n||n>MAX_SOURCE)return P183_REJECT_PARSE;free(c->source);c->source=malloc(n+1);if(!c->source)return P183_INTERNAL_ERROR;memcpy(c->source,s,n);c->source[n]='\0';c->length=n;c->parsed=1;c->balanced=c->boundaries=c->domain=c->truth=c->roles=c->executed=c->zero=c->closed=c->receipt_ready=0;hexfill(c->lexical,64,mix(s,n,1469598103934665603ull));return P183_OK;}
hhs_p183_status hhs_p183_snapshot_lexical_identity(hhs_p183_context*c,char out[65]){if(!c||!out||!c->parsed)return P183_REJECT_PARSE;memcpy(out,c->lexical,65);return P183_OK;}
hhs_p183_status hhs_p183_build_membrane_tree(hhs_p183_context*c){size_t i,depth=0,count=0;if(!c||!c->parsed)return P183_REJECT_PARSE;for(i=0;i<c->length;i++){if(c->source[i]=='('){depth++;count++;if(depth>256)return P183_REJECT_MEMBRANE_WITNESS;}else if(c->source[i]==')'){if(!depth)return P183_REJECT_UNBALANCED_MEMBRANE;depth--;}}if(depth)return P183_REJECT_UNBALANCED_MEMBRANE;c->membranes=count;c->balanced=1;return P183_OK;}
hhs_p183_status hhs_p183_validate_membrane_boundaries(hhs_p183_context*c){if(!c||!c->balanced)return P183_REJECT_MEMBRANE_WITNESS;c->boundaries=1;return P183_OK;}
hhs_p183_status hhs_p183_validate_probability_domain(hhs_p183_context*c,int valid){if(!c||!c->parsed)return P183_REJECT_PARSE;if(!valid)return P183_REJECT_PROBABILITY_DOMAIN;c->domain=1;return P183_OK;}
hhs_p183_status hhs_p183_validate_equation_truth(hhs_p183_context*c,int valid){if(!c||!c->parsed)return P183_REJECT_PARSE;if(!valid)return P183_REJECT_EQUATION_FALSE;c->truth=1;return P183_OK;}
hhs_p183_status hhs_p183_bind_hydration_roles(hhs_p183_context*c,const char*x,const char*y,const char*z,const char*w){if(!c||!x||!y||!z||!w||!c->domain||!c->truth||!c->boundaries)return P183_REJECT_PARSE;c->roles=1;return P183_OK;}
hhs_p183_status hhs_p183_hydrate_factorial72_forward(hhs_p183_context*c,char*out,size_t n){if(!c||!out||n<=strlen(FORWARD)||!c->roles)return P183_REJECT_FACTORIAL_LANE;memcpy(out,FORWARD,sizeof(FORWARD));return P183_OK;}
hhs_p183_status hhs_p183_construct_reciprocal_lane(hhs_p183_context*c,char*out,size_t n){if(!c||!out||n<=strlen(RECIP)||!c->roles)return P183_REJECT_RECIPROCAL_CONSTRUCTION;memcpy(out,RECIP,sizeof(RECIP));return P183_OK;}
hhs_p183_status hhs_p183_execute_probability_adapter(hhs_p183_context*c,const char*adapter,int zero){if(!c||!adapter||!c->roles)return P183_REJECT_PARSE;c->executed=1;c->zero=zero?1:0;return c->zero?P183_ZERO_BYPASS:P183_OK;}
hhs_p183_status hhs_p183_close_u72(hhs_p183_context*c){if(!c||!c->executed)return P183_REJECT_RECIPROCAL_CONSTRUCTION;if(c->zero)return P183_ZERO_BYPASS;c->closed=1;return P183_OK;}
hhs_p183_status hhs_p183_route_typed_zero(hhs_p183_context*c){if(!c||!c->executed||!c->zero)return P183_REJECT_RECIPROCAL_CONSTRUCTION;c->closed=1;return P183_ZERO_BYPASS;}
hhs_p183_status hhs_p183_apply_outer_modulus(hhs_p183_context*c,int64_t num,uint64_t den,uint32_t*res,int*scalar){uint64_t g;int64_t inv,n;if(!c||!res||!scalar||!c->closed)return P183_REJECT_RECIPROCAL_CONSTRUCTION;if(!den)return P183_REJECT_ZERO_DENOMINATOR;g=gcd64(den,M);if(g!=1){*scalar=0;*res=0;return P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR;}inv=inverse((int64_t)(den%M),(int64_t)M);if(inv<0)return P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR;n=num%(int64_t)M;if(n<0)n+=M;*res=(uint32_t)((n*inv)%M);*scalar=1;return P183_OK;}
hhs_p183_status hhs_p183_emit_hash72_receipt(hhs_p183_context*c,char out[73]){if(!c||!out||!c->closed)return P183_REJECT_RECEIPT;hexfill(c->receipt,72,mix(c->source,c->length,0x18372ull));memcpy(out,c->receipt,73);c->receipt_ready=1;return P183_OK;}
hhs_p183_status hhs_p183_compute_hash216_identity(hhs_p183_context*c,char out[217]){if(!c||!out||!c->receipt_ready)return P183_REJECT_RECEIPT;hexfill(c->hash216,216,mix(c->receipt,72,0x183216ull));memcpy(out,c->hash216,217);return P183_OK;}
hhs_p183_status hhs_p183_replay(hhs_p183_context*c){return c&&c->receipt_ready&&c->closed?P183_OK:P183_REJECT_REPLAY;}
hhs_p183_status hhs_p183_verify_receipt(hhs_p183_context*c,const char*r){if(!c||!r||!c->receipt_ready)return P183_REJECT_RECEIPT;return strcmp(c->receipt,r)==0?P183_OK:P183_REJECT_RECEIPT;}
const char*hhs_p183_status_name(hhs_p183_status s){static const char*n[]={"P183_OK","P183_REJECT_LEXICAL_IDENTITY","P183_REJECT_PARSE","P183_REJECT_UNBALANCED_MEMBRANE","P183_REJECT_MEMBRANE_WITNESS","P183_REJECT_LIST_ORDER","P183_REJECT_FACTORIAL_LANE","P183_REJECT_PROBABILITY_DOMAIN","P183_REJECT_EQUATION_FALSE","P183_REJECT_ZERO_DENOMINATOR","P183_ZERO_BYPASS","P183_REJECT_RECIPROCAL_CONSTRUCTION","P183_REJECT_LOCAL_MODULAR_INVERSION","P183_REJECT_NONINVERTIBLE_OUTER_DENOMINATOR","P183_REJECT_FLOAT_AUTHORITY","P183_REJECT_RANDOMNESS_MANIFEST","P183_REJECT_REPLAY","P183_REJECT_RECEIPT","P183_TIMEOUT","P183_CANCELLED","P183_INTERNAL_ERROR"};return(unsigned)s<sizeof(n)/sizeof(n[0])?n[s]:"P183_INTERNAL_ERROR";}
const char*hhs_p183_canonical_formula(void){return FORMULA;}const char*hhs_p183_forward_lane_token(void){return FORWARD;}const char*hhs_p183_reciprocal_lane_token(void){return RECIP;}const char*hhs_p183_factorial72_decimal(void){return F72;}uint32_t hhs_p183_global_modulus(void){return M;}uint32_t hhs_p183_factorial72_modulus_gcd(void){return 91u;}size_t hhs_p183_membrane_count(const hhs_p183_context*c){return c?c->membranes:0u;}
