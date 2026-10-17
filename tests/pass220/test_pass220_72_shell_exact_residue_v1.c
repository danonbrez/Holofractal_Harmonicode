#include "hhs_pass220_72_shell_exact_residue_v1.h"
#include <string.h>
#include <stdio.h>
int main(void){
char n[160],d[160],small[2];
const char *en="775710873160901421359061468620360862729920180854006643986760192036";
const char *ed="3110094060648844770831880556173301180945943326884396380767822265625";
if(!hhs_pass220_72_shell_exact_residue(n,sizeof(n),d,sizeof(d)))return 1;
if(strcmp(n,en)||strcmp(d,ed))return 2;
if(hhs_pass220_72_shell_exact_residue(small,sizeof(small),d,sizeof(d)))return 3;
if(hhs_pass220_72_shell_exact_residue(NULL,0,d,sizeof(d)))return 4;
puts("PASS exact 72-shell OpenSSL BigNum rational + negative bounds");
return 0;
}
