#include "hhs_pass220_72_shell_outer_projection_v1.h"
#include <openssl/bn.h>
#include <string.h>
int hhs_pass220_72_shell_outer_projection(char *n,size_t nc,char *d,size_t dc){
 BIGNUM *a2=NULL,*b2=NULL,*c2=NULL,*a4=NULL,*lhsden=NULL,*e2=NULL;
 BN_CTX *ctx=NULL;char *ns=NULL,*ds=NULL;int ok=0;
 if(!n||!d||nc==0U||dc==0U||n==d)return 0;
 n[0]=0;d[0]=0;
 ctx=BN_CTX_new();a2=BN_new();b2=BN_new();c2=BN_new();
 a4=BN_new();lhsden=BN_new();e2=BN_new();remainder=BN_new();
 if(!ctx||!a2||!b2||!c2||!a4||!lhsden||!e2||!remainder)goto done;
 if(!BN_set_word(a2,1U)||!BN_set_word(b2,2U)||!BN_set_word(c2,3U)||
    !BN_sqr(a4,a2,ctx)||!BN_sub(lhsden,c2,a2)||
    BN_is_zero(lhsden)||!BN_mul(e2,a4,lhsden,ctx))goto done;
 /* E^2 = (a^4/b^2)*(c^2-a^2) = 2/2 = 1, exact. */
 if(!BN_div(e2,remainder,e2,b2,ctx)||!BN_is_zero(remainder))goto done;
 ns=BN_bn2dec(e2);ds=BN_bn2dec(a2);
 if(!ns||!ds||strlen(ns)+1U>nc||strlen(ds)+1U>dc)goto done;
 memcpy(n,ns,strlen(ns)+1U);memcpy(d,ds,strlen(ds)+1U);ok=1;
done:
 OPENSSL_free(ns);OPENSSL_free(ds);
 BN_free(a2);BN_free(b2);BN_free(c2);BN_free(a4);BN_free(lhsden);BN_free(e2);BN_free(remainder);
 BN_CTX_free(ctx);if(!ok){n[0]=0;d[0]=0;}return ok;
}
