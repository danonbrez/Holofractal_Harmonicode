#include "hhs_pass220_72_shell_outer_projection_v1.h"
#include <stdio.h>
#include <string.h>
int main(void){
 char n[16],d[16],shortbuf[1];
 if(!hhs_pass220_72_shell_outer_projection(n,sizeof(n),d,sizeof(d)))return 1;
 if(strcmp(n,"1")||strcmp(d,"1"))return 2;
 if(hhs_pass220_72_shell_outer_projection(shortbuf,sizeof(shortbuf),d,sizeof(d)))return 3;
 if(hhs_pass220_72_shell_outer_projection(n,sizeof(n),n,sizeof(n)))return 4;
 puts("PASS exact BigNum outer canonical projection E^2=1; no native proof");
 return 0;
}
