#include "hhs_pass220_72_shell_exact_residue_v1.h"
#include <openssl/bn.h>
#include <string.h>
#include <stdint.h>
int hhs_pass220_72_shell_exact_residue(char *numerator, size_t ncap,
                                      char *denominator, size_t dcap) {
    BIGNUM *p=NULL, *f=NULL, *r=NULL, *g=NULL, *n=NULL, *d=NULL;
    BN_CTX *ctx=NULL;
    char *ns=NULL, *ds=NULL;
    int ok=0, i;
    if(numerator==NULL || denominator==NULL || ncap==0 || dcap==0) return 0;
    numerator[0]=0; denominator[0]=0;
    ctx=BN_CTX_new();p=BN_new();f=BN_new();r=BN_new();g=BN_new();n=BN_new();d=BN_new();
    if(!ctx||!p||!f||!r||!g||!n||!d) goto done;
    if(!BN_one(p)||!BN_one(f)) goto done;
    for(i=0;i<72;i++) if(!BN_mul_word(p,72)) goto done;
    for(i=2;i<=72;i++) if(!BN_mul_word(f,(BN_ULONG)i)) goto done;
    if(!BN_mod(r,p,f,ctx)||!BN_gcd(g,r,f,ctx)||BN_is_zero(r)) goto done;
    if(!BN_div(n,NULL,r,g,ctx)||!BN_div(d,NULL,f,g,ctx)) goto done;
    ns=BN_bn2dec(n);ds=BN_bn2dec(d);
    if(!ns||!ds||strlen(ns)+1>ncap||strlen(ds)+1>dcap) goto done;
    memcpy(numerator,ns,strlen(ns)+1);
    memcpy(denominator,ds,strlen(ds)+1);
    ok=1;
done:
    OPENSSL_free(ns);OPENSSL_free(ds);
    BN_free(p);BN_free(f);BN_free(r);BN_free(g);BN_free(n);BN_free(d);
    BN_CTX_free(ctx);
    if(!ok){numerator[0]=0;denominator[0]=0;}
    return ok;
}
