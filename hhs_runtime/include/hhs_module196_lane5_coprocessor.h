#ifndef HHS_MODULE196_LANE5_COPROCESSOR_H
#define HHS_MODULE196_LANE5_COPROCESSOR_H
/* Module 196: exact, candidate-only ingress/egress C surface.
 * No VM81 mutation, Hash72 minting, or Hash216 persistence authority.
 * Caller supplies integer nanoseconds from its authoritative clock. */
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#ifdef __cplusplus
extern "C" {
#endif
enum { HHS_M196_SIDE=9, HHS_M196_CELLS=81, HHS_M196_FRACTAL_SIDE=243,
       HHS_M196_FRACTAL_CELLS=59049, HHS_M196_HNAN_ADDRESSES=25,
       HHS_M196_HNAN_CHILDREN=2025 };
typedef struct {
    uint64_t ingress_ns, egress_ns;
    uint32_t addresses, equality_cells, local_p2_cells, hnan_addresses, hnan_children;
    int64_t value[81];
    uint8_t gate[81]; /* 5/6 => dual lanes; other labels => local P^2 */
    int64_t lane_a[81], lane_b[81];
    int64_t sum, trace;
    uint8_t accepted_candidate, vm81_mutation_authority, hash72_authority, hash216_authority;
} HHSModule196Candidate;
static inline int hhs_m196_powmod(int a,int e,int m) {
    int64_t r=1,b=a%m;
    while(e>0){if(e&1)r=(r*b)%m;b=(b*b)%m;e>>=1;}
    return (int)r;
}
static inline int hhs_m196_legendre(int a,int p) {
    int n=hhs_m196_powmod(a,(p-1)/2,p);
    return n==p-1 ? -1 : n;
}
/* Pure computation: ingress->candidate, not canonical egress/admission. */
static inline int hhs_m196_evaluate(uint64_t ingress_ns,uint64_t egress_ns,
                                   HHSModule196Candidate *out) {
    static const uint8_t sudoku[81]={
       7,3,5,2,4,9,6,8,1, 6,8,1,7,3,5,2,4,9,
       2,4,9,6,8,1,7,3,5, 3,5,7,4,9,2,8,1,6,
       8,1,6,3,5,7,4,9,2, 4,9,2,8,1,6,3,5,7,
       5,7,3,9,2,4,1,6,8, 1,6,8,5,7,3,9,2,4,
       9,2,4,1,6,8,5,7,3 };
    static const uint8_t manifold[81]={
       32,72,16,12,27,6,16,36,8, 24,40,56,9,15,21,12,20,28,
       64,8,48,24,3,18,32,4,24, 4,9,2,20,45,10,36,81,18,
       3,5,7,15,25,35,27,45,63, 8,1,6,40,5,30,72,9,54,
       24,54,12,28,63,14,8,18,4, 18,30,42,21,35,49,6,10,14,
       48,6,36,56,7,42,16,2,12 };
    static const uint8_t prime[9]={5,13,17,3,7,11,19,23,2};
    static const uint8_t seed_value[10]={0,1,2,3,4,5,6,3,8,9};
    if(!out || egress_ns<ingress_ns) return 0;
    HHSModule196Candidate tmp;
    memset(&tmp, 0, sizeof(tmp));
    tmp.ingress_ns=ingress_ns; tmp.egress_ns=egress_ns;
    tmp.addresses=81;
    for(size_t k=0;k<81;k++) {
        int label=sudoku[k];
        int64_t v=(int64_t)manifold[k]*seed_value[label];
        tmp.value[k]=v;
        tmp.gate[k]=(label==5||label==6);
        if(tmp.gate[k]) {
            tmp.lane_a[k]=v;tmp.lane_b[k]=v;tmp.equality_cells++;
        } else tmp.local_p2_cells++;
        tmp.sum+=v;
        if(k/9==k%9) tmp.trace+=v;
    }
    for(int i=0;i<9;i++) for(int j=0;j<9;j++) {
        int a=prime[i],b=prime[j];
        if(a==2||b==2||a==b) {tmp.hnan_addresses++;continue;}
        int x=hhs_m196_legendre(a,b),y=hhs_m196_legendre(b,a);
        int sign=((a%4==3)&&(b%4==3))?-1:1;
        if(x*y!=sign) return 0;
    }
    tmp.hnan_children=tmp.hnan_addresses*81;
    if(tmp.equality_cells!=18 ||tmp.local_p2_cells!=63 ||
       tmp.hnan_addresses!=25 ||tmp.hnan_children!=2025 ||
       tmp.sum!=9105 ||tmp.trace!=1297) return 0;
    tmp.accepted_candidate=1;
    /* Authority flags remain zero; downstream must perform VM81 admission. */
    *out=tmp;
    return 1;
}
#ifdef __cplusplus
}
#endif
#endif
