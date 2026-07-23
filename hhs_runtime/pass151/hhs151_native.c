#include "hhs151_native.h"
#include <string.h>
int hhs151_is_closed(int implemented,int reachable,int tested,int evidenced,int dependencies_closed,int stub_detected){return implemented&&reachable&&tested&&evidenced&&dependencies_closed&&!stub_detected;}
int hhs151_state_valid(hhs151_state state){return state>=HHS151_UNRESOLVED&&state<=HHS151_SUPERSEDED_EXPLICITLY;}
int hhs151_semantic_may_close(void){return 0;}
size_t hhs151_copy_error(char *dst,size_t cap,const char *message){size_t n=message?strlen(message):0;if(dst&&cap){size_t k=n<cap-1?n:cap-1;memcpy(dst,message,k);dst[k]='\0';}return n;}
