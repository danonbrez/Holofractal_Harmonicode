#include "hhs_pass157.h"
#include "hhs_runtime_abi.h"
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static HHS157Request demo(void){HHS157Request q;memset(&q,0,sizeof(q));q.abi_version=1;q.P=5;q.p=2;q.q=3;q.euclid_m=3;q.euclid_n=2;q.full_rotation=-137;q.local_modulus=72;for(size_t i=0;i<11;i++)q.centerline[i]=(int64_t)i+1;snprintf(q.fold_path,sizeof(q.fold_path),"root/ppf/center/fold-157");snprintf(q.source_expression,sizeof(q.source_expression),"P^2/(t^3-t)==P^2 Mod pq; x+y<zw<x<z<yx<wz<y<w<xy<b^2<c^2");return q;}
static int verify(void){HHS157Request q=demo();HHS157Result r;HHS157AuthorityReceipt receipt;HHSRuntimeState runtime;char json[8192];size_t written;HHS157Status s=hhs157_construct(&q,&r);if(s){fprintf(stderr,"construct:%s\n",hhs157_status_string(s));return 1;}hhs_runtime_init(&runtime);s=hhs157_admit(&q,&r,&runtime,&receipt);if(s){fprintf(stderr,"admit:%s\n",hhs157_status_string(s));return 1;}s=hhs157_replay_verify(&q,&r,&receipt);if(s){fprintf(stderr,"replay:%s\n",hhs157_status_string(s));return 1;}s=hhs157_serialize_json(&q,&r,&receipt,json,sizeof(json),&written);if(s)return 1;puts(json);return 0;}
int main(int argc,char**argv){const char*cmd=argc>1?argv[1]:"verify";if(!strcmp(cmd,"verify")||!strcmp(cmd,"demo"))return verify();if(!strcmp(cmd,"decompose")&&argc==4){HHS157PhaseLane lane;HHS157Status s=hhs157_phase_decompose(strtoll(argv[2],NULL,10),strtoll(argv[3],NULL,10),&lane);if(s)return 2;printf("{\"M\":%"PRId64",\"q\":%"PRId64",\"r\":%"PRId64"}\n",lane.modulus,lane.quotient,lane.residue);return 0;}puts("usage: hhs-pass157 [verify|demo|decompose n M]");return !strcmp(cmd,"--help")?0:2;}
