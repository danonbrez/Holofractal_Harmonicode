#include "../../hhs_runtime/pass151/hhs151_native.h"
#include <assert.h>
int main(void){assert(hhs151_is_closed(1,1,1,1,1,0)==1);assert(hhs151_is_closed(1,1,1,1,1,1)==0);assert(hhs151_semantic_may_close()==0);assert(hhs151_state_valid(HHS151_VERIFIED));return 0;}
