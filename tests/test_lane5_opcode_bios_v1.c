#include "../hhs_runtime/acceleration/hhs_lane5_opcode_bios_v1.h"
#include <assert.h>
#include <limits.h>
#include <string.h>
int main(void) {
  uint8_t h[216], frame[648];
  memset(h,0x5a,sizeof h); memset(frame,0xa5,sizeof frame);
  hhs_bios_cache c={0};
  hhs_bios_view v={h,frame,42};
  assert(hhs_bios_bind(&c,&v)==HHS_BIOS_OK);
  uint8_t got=0;
  assert(hhs_bios_read216(&c,42,215,&got)==HHS_BIOS_OK && got==0x5a);
  assert(hhs_bios_read_frame(&c,42,647,&got)==HHS_BIOS_OK && got==0xa5);
  assert(hhs_bios_read216(&c,41,0,&got)==HHS_BIOS_STALE);
  hhs_bios_instruction ops[3]={{HHS_BIOS_ADD_U64,0,0,0,5,7},
    {HHS_BIOS_PHASE_PAIR,1,0,0,0,0},{HHS_BIOS_MOD72,0,0,0,145,0}};
  hhs_bios_result result[3]={{0}};
  assert(hhs_bios_dispatch(&c,42,ops,3,result)==HHS_BIOS_OK);
  assert(result[0].value==12 && result[1].phase==36 &&
         result[1].orientation==2 && result[2].value==1);
  hhs_bios_result original[3];memcpy(original,result,sizeof result);
  ops[0].left=UINT64_MAX;ops[0].right=1;
  assert(hhs_bios_dispatch(&c,42,ops,3,result)==HHS_BIOS_OVERFLOW);
  assert(memcmp(result,original,sizeof result)==0);
  assert(h[0]==0x5a && frame[0]==0xa5);
  hhs_bios_invalidate(&c);
  assert(hhs_bios_dispatch(&c,42,ops,3,result)==HHS_BIOS_STALE);
  return 0;
}
