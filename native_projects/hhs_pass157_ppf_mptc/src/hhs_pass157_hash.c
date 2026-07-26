#include "hhs_pass157_internal.h"
#include "hhs_hash216.h"
#include <string.h>
void hhs157_hash216_bytes(const void *data,size_t size,char out[HHS157_HASH216_STRLEN]){HHSHash216 h;hhs_hash216_compute(data,size,&h);memcpy(out,h.value,HHS157_HASH216_STRLEN);}
