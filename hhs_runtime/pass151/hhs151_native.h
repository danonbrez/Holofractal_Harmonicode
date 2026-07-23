#ifndef HHS151_NATIVE_H
#define HHS151_NATIVE_H
#include <stddef.h>
#ifdef __cplusplus
extern "C" {
#endif
typedef enum { HHS151_UNRESOLVED=0,HHS151_BLOCKED=1,HHS151_IMPLEMENTING=2,HHS151_IMPLEMENTED_UNREACHABLE=3,HHS151_REACHABLE_UNTESTED=4,HHS151_PARTIALLY_TESTED=5,HHS151_VERIFIED=6,HHS151_FAILED=7,HHS151_NOT_APPLICABLE_PROVED=8,HHS151_SUPERSEDED_EXPLICITLY=9 } hhs151_state;
int hhs151_is_closed(int implemented,int reachable,int tested,int evidenced,int dependencies_closed,int stub_detected);
int hhs151_state_valid(hhs151_state state);
int hhs151_semantic_may_close(void);
size_t hhs151_copy_error(char *dst,size_t cap,const char *message);
#ifdef __cplusplus
}
#endif
#endif
