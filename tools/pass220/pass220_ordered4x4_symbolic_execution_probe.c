/* Native typed-operator execution conformance, no scalar closure shortcuts. */
#include "hhs_runtime_exact_abi.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define REQUIRE(c,msg) do { if (!(c)) { fprintf(stderr,"FAIL:%s\n",msg); return 1; }} while(0)
int main(void) {
 uint8_t source[HHS220_ORDERED4X4_SOURCE_BYTES+1U]={0};
 uint8_t program[HHS220_ORDERED4X4_OPCODE_COUNT]={0};
 HHS220Ordered4x4SymbolicExecutionV1 a,b,bad;
 size_t n=0U,size=0U,i;
 FILE *f=fopen("contracts/pass220/PASS_220_ORDERED_4X4_NEG4_MATRIX_TENSOR_V1.harmonicode","rb");
 REQUIRE(f!=NULL,"source file");
 n=fread(source,1U,sizeof(source),f);
 REQUIRE(!ferror(f),"read source");
 REQUIRE(fclose(f)==0,"close");
 REQUIRE(n==HHS220_ORDERED4X4_SOURCE_BYTES,"source width");

 REQUIRE(hhs_exact_pass220_ordered4x4_program(NULL,0U,&size)==HHS_EXACT_STATUS_BUFFER_TOO_SMALL,"query program width");
 REQUIRE(size==HHS220_ORDERED4X4_OPCODE_COUNT,"program length");
 REQUIRE(hhs_exact_pass220_ordered4x4_program(program,sizeof(program),&size)==HHS_EXACT_STATUS_OK,"get program");
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size,&a)==HHS_EXACT_STATUS_OK,"exact symbolic operator program");
 REQUIRE(a.steps==15U && a.maximum_stack_depth==3U,"stack execution");
 REQUIRE(a.matrices_bound==4U && a.symbols_bound==2U,"literal/symbol bindings");
 REQUIRE(a.source_identity_verified==1U && a.operator_types_verified==1U && a.ordered_program_verified==1U,"source and type verification");
 REQUIRE(a.exact_symbolic_program_executed==1U && a.deterministic_symbolic_replay_verified==1U,"symbolic execution and replay");
 REQUIRE(a.expression_equality_proved==0U && a.matrix_power_value_derived==0U,"no invented equality or matrix values");
 REQUIRE(a.matrix_times_numeric_evaluated==0U && a.quotient_value_derived==0U,"no host arithmetic");
 REQUIRE(a.typed_s_substituted==0U && a.typed_v_substituted==0U,"typed symbols remain bound");
 REQUIRE(a.vm81_admission_executed==0U && a.canonical_vm81_mutation_authority==0U,"no VM81 admission");
 REQUIRE(a.hash72_commit_authority==0U && a.hash216_commit_authority==0U,"no canonical receipts");
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size,&b)==HHS_EXACT_STATUS_OK,"second execution");
 REQUIRE(memcmp(&a,&b,sizeof(a))==0,"deterministic complete symbolic witness");
 REQUIRE(memcmp(a.result_node_sha256,a.ordered_node_roots[14],32U)==0,"final ordered equality node identity");
 for(i=0U;i<HHS220_ORDERED4X4_OPCODE_COUNT;++i) {
  REQUIRE(memcmp(a.ordered_node_roots[i],"\0\0\0\0",4U)!=0,"every symbolic opcode executed");
  program[i]^=1U;
  REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size,&bad)!=HHS_EXACT_STATUS_OK,"reject altered opcode at every position");
  REQUIRE(bad.exact_symbolic_program_executed==0U && bad.hash72_commit_authority==0U,"reject never confers authority");
  program[i]^=1U;
 }
 source[0]^=1U;
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size,&bad)!=HHS_EXACT_STATUS_OK,"source mutation rejected");
 source[0]^=1U;
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n-1U,program,size,&bad)!=HHS_EXACT_STATUS_OK,"source truncation rejected");
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size-1U,&bad)!=HHS_EXACT_STATUS_OK,"truncated opcode sequence rejected");
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,NULL,size,&bad)!=HHS_EXACT_STATUS_OK,"null program rejected");
 REQUIRE(hhs_exact_pass220_ordered4x4_execute_symbolic(source,n,program,size,NULL)!=HHS_EXACT_STATUS_OK,"null output rejected");
 puts("{\"schema\":\"HHS_PASS220_ORDERED4X4_SYMBOLIC_VM81_HIR_EXECUTION_V1\",\"source_verified\":true,\"operator_steps\":15,\"deterministic_symbolic_replay\":true,\"negative_cases_rejected\":true,\"equality_proved\":false,\"vm81_admitted\":false,\"hash72_committed\":false,\"hash216_committed\":false}");
 return 0;
}
