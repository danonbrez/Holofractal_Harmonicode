#include "hhs_p165_mmvs.h"
#include <stdio.h>
#include <string.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL:%d:%s\n",__LINE__,#x);return 1;}}while(0)
int main(void){hhs_p165_frame a,b,r;uint8_t value=0u;uint32_t p,l;hhs_p165_source_descriptor source;hhs_p165_rational w={1,2},min={-8,1},max={8,1},bad={1,0};
CHECK(HHS_P165_COORDINATES==5184u);CHECK(sizeof(a.bytes)==648u);CHECK(hhs_p165_frame_clear(&a)==HHS_P165_OK);CHECK(hhs_p165_frame_clear(&b)==HHS_P165_OK);
for(p=0;p<HHS_P165_POSITIONS;p++)for(l=0;l<HHS_P165_LANES;l++)if(((p*64u+l)%17u)==0u)CHECK(hhs_p165_frame_set(&a,p,l,1u)==HHS_P165_OK);
CHECK(hhs_p165_frame_popcount(&a)>0u);CHECK(hhs_p165_frame_get(&a,0u,0u,&value)==HHS_P165_OK);CHECK(value==1u);CHECK(hhs_p165_frame_get(&a,81u,0u,&value)==HHS_P165_OUT_OF_RANGE);
CHECK(hhs_p165_frame_residual(&a,&b,&r)==HHS_P165_OK);CHECK(memcmp(a.bytes,r.bytes,648u)==0);CHECK(hhs_p165_frame_residual(&a,&a,&r)==HHS_P165_OK);CHECK(hhs_p165_frame_popcount(&r)==0u);
memset(&source,0,sizeof(source));source.abi_version=1u;source.byte_length=100u;source.authorization_scope=1u;CHECK(hhs_p165_validate_source(&source)==HHS_P165_OK);source.byte_length=0u;CHECK(hhs_p165_validate_source(&source)==HHS_P165_SIZE_BOUND);
CHECK(hhs_p165_validate_weight(w,min,max)==HHS_P165_OK);CHECK(hhs_p165_validate_weight(bad,min,max)==HHS_P165_NONCANONICAL_WEIGHT);
puts("HHS_PASS_165_NATIVE_TESTS_PASS");return 0;}
