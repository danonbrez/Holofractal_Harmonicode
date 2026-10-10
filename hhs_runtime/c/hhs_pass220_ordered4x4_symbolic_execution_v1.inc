/* Execute exact typed *symbolic* operators; never a host matrix calculator.
 * The immutable HHS source is authenticated by the inherited 4x4 lowerer.
 * Each node root binds operator, position, ordered operand roots and source.
 * Hashes here are diagnostic SHA-256, NOT Hash72/Hash216 receipts.
 */
#include "../include/hhs_pass220_ordered4x4_symbolic_execution_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

static const uint8_t HHS220_ORDERED4X4_PROGRAM[HHS220_ORDERED4X4_OPCODE_COUNT] = {
 1,2,1,2,3,1,4,3,5,6,7,4,1,3,8
};
enum {
 HHS220_T_MATRIX=1, HHS220_T_NEG_MATRIX=2, HHS220_T_TIMES=3,
 HHS220_T_SYMBOL=4, HHS220_T_QUOTIENT=5, HHS220_T_NEG4=6,
 HHS220_T_POWER=7, HHS220_T_EQUALITY=8
};
typedef struct HHS220SymbolicNode {
 uint8_t type;
 uint8_t digest[32];
} HHS220SymbolicNode;

static int hhs220_symbolic_tensor_operand(uint8_t type) {
 return type==HHS220_T_MATRIX || type==HHS220_T_NEG_MATRIX ||
        type==HHS220_T_TIMES || type==HHS220_T_SYMBOL;
}

static int hhs220_symbolic_node_digest(
 const uint8_t source_digest[32],
 const uint8_t program_digest[32], uint8_t opcode,
 uint8_t position, uint8_t output_type,
 const HHS220SymbolicNode *left, const HHS220SymbolicNode *right,
 const uint8_t *literal, size_t literal_len,
 uint8_t out_digest[32]
) {
 static const char DOMAIN[]="HHS-P220-ORDERED4X4-OPERATOR-TYPED-NODE-V1";
 uint8_t material[256];
 size_t offset=0U;
 size_t domain_len=sizeof(DOMAIN)-1U;
 if (literal_len>64U || (literal_len && literal==NULL))
  return 0;
 memcpy(material+offset,DOMAIN,domain_len); offset+=domain_len;
 memcpy(material+offset,source_digest,32U); offset+=32U;
 memcpy(material+offset,program_digest,32U); offset+=32U;
 material[offset++]=position;
 material[offset++]=opcode;
 material[offset++]=output_type;
 material[offset++]=left ? 1U : 0U;
 if (left) {
  material[offset++]=left->type;
  memcpy(material+offset,left->digest,32U); offset+=32U;
 }
 material[offset++]=right ? 1U : 0U;
 if (right) {
  material[offset++]=right->type;
  memcpy(material+offset,right->digest,32U); offset+=32U;
 }
 material[offset++]=(uint8_t)literal_len;
 if (literal_len) {
  memcpy(material+offset,literal,literal_len); offset+=literal_len;
 }
 if (offset>sizeof(material)) return 0;
 return SHA256(material,offset,out_digest)!=NULL;
}

static int hhs220_symbolic_execute_program(
 const uint8_t source_digest[32], const uint8_t program_digest[32],
 uint8_t roots[HHS220_ORDERED4X4_OPCODE_COUNT][32],
 uint8_t out_root[32], uint32_t *out_max_depth
) {
 HHS220SymbolicNode stack[HHS220_ORDERED4X4_OPCODE_COUNT];
 size_t depth=0U, max_depth=0U, index;
 unsigned matrix_index=0U, symbol_index=0U;
 memset(stack,0,sizeof(stack));
 for (index=0U;index<HHS220_ORDERED4X4_OPCODE_COUNT;++index) {
  uint8_t op=HHS220_ORDERED4X4_PROGRAM[index], type=0U;
  HHS220SymbolicNode left, right, result;
  const HHS220SymbolicNode *lhs=NULL,*rhs=NULL;
  const uint8_t *literal=NULL;
  size_t literal_size=0U;
  uint8_t symbol=0U;
  memset(&left,0,sizeof(left));
  memset(&right,0,sizeof(right));
  memset(&result,0,sizeof(result));

  switch (op) {
  case HHS220_4X4_PUSH_SOURCE_MATRIX:
   if (matrix_index>=4U) return 0;
   type=HHS220_T_MATRIX;
   literal=(const uint8_t *)HHS220_ORDERED4X4_CELLS[matrix_index++];
   literal_size=16U;
   break;
  case HHS220_4X4_PUSH_SOURCE_SYMBOL:
   if (symbol_index>=2U) return 0;
   type=HHS220_T_SYMBOL;
   symbol=(symbol_index++==0U) ? (uint8_t)'s' : (uint8_t)'v';
   literal=&symbol;
   literal_size=1U;
   break;
  case HHS220_4X4_PUSH_NEGATIVE_FOUR:
   type=HHS220_T_NEG4;
   symbol=4U; /* exact frozen negative-four magnitude; sign in node type */
   literal=&symbol;
   literal_size=1U;
   break;
  case HHS220_4X4_ORDERED_NEGATE:
   if (depth<1U || stack[depth-1U].type!=HHS220_T_MATRIX) return 0;
   left=stack[--depth]; lhs=&left;
   type=HHS220_T_NEG_MATRIX;
   break;
  case HHS220_4X4_MATRIX_TIMES:
   if (depth<2U ||
       !hhs220_symbolic_tensor_operand(stack[depth-2U].type) ||
       !hhs220_symbolic_tensor_operand(stack[depth-1U].type)) return 0;
   right=stack[--depth]; left=stack[--depth];
   lhs=&left; rhs=&right; type=HHS220_T_TIMES;
   break;
  case HHS220_4X4_TYPED_QUOTIENT:
   if (depth<2U || stack[depth-2U].type!=HHS220_T_TIMES ||
       stack[depth-1U].type!=HHS220_T_TIMES) return 0;
   right=stack[--depth]; left=stack[--depth];
   lhs=&left; rhs=&right; type=HHS220_T_QUOTIENT;
   break;
  case HHS220_4X4_NCALC_MATRIX_POWER:
   if (depth<2U || stack[depth-2U].type!=HHS220_T_QUOTIENT ||
       stack[depth-1U].type!=HHS220_T_NEG4) return 0;
   right=stack[--depth]; left=stack[--depth];
   lhs=&left; rhs=&right; type=HHS220_T_POWER;
   break;
  case HHS220_4X4_ORDERED_EQUALITY:
   if (depth!=2U || stack[0].type!=HHS220_T_POWER ||
       stack[1].type!=HHS220_T_TIMES) return 0;
   right=stack[--depth]; left=stack[--depth];
   lhs=&left; rhs=&right; type=HHS220_T_EQUALITY;
   break;
  default:
   return 0;
  }

  if (!hhs220_symbolic_node_digest(source_digest,program_digest,
          op,(uint8_t)index,type,lhs,rhs,literal,literal_size,result.digest))
   return 0;
  result.type=type;
  if (depth>=HHS220_ORDERED4X4_OPCODE_COUNT) return 0;
  stack[depth++]=result;
  memcpy(roots[index],result.digest,32U);
  if (depth>max_depth) max_depth=depth;
 }
 if (depth!=1U || stack[0].type!=HHS220_T_EQUALITY ||
     matrix_index!=4U || symbol_index!=2U) return 0;
 memcpy(out_root,stack[0].digest,32U);
 *out_max_depth=(uint32_t)max_depth;
 return 1;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_program(
 uint8_t *out_program,size_t capacity,size_t *out_length
) {
 if (out_length==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 *out_length=HHS220_ORDERED4X4_OPCODE_COUNT;
 if (out_program==NULL || capacity<HHS220_ORDERED4X4_OPCODE_COUNT)
  return HHS_EXACT_STATUS_BUFFER_TOO_SMALL;
 memcpy(out_program,HHS220_ORDERED4X4_PROGRAM,HHS220_ORDERED4X4_OPCODE_COUNT);
 return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_execute_symbolic(
 const uint8_t *source,size_t source_size,
 const uint8_t *program,size_t program_size,
 HHS220Ordered4x4SymbolicExecutionV1 *out_execution
) {
 HHSExactVM81Frame staged_frame;
 HHS220Ordered4x4HIRWitnessV1 staged_witness;
 uint8_t program_digest[32];
 uint8_t replay_roots[HHS220_ORDERED4X4_OPCODE_COUNT][32];
 uint8_t replay_root[32];
 uint32_t max_depth=0U,replay_depth=0U;
 HHSExactStatus status;
 if (out_execution==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_execution,0,sizeof(*out_execution));
 out_execution->struct_size=(uint32_t)sizeof(*out_execution);
 out_execution->version=UINT32_C(0x00010000);
 if (source==NULL || program==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 if (program_size!=HHS220_ORDERED4X4_OPCODE_COUNT ||
     memcmp(program,HHS220_ORDERED4X4_PROGRAM,program_size)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_lower(
  source,source_size,&staged_frame,&staged_witness);
 if (status!=HHS_EXACT_STATUS_OK) return status;
 if (staged_witness.source_identity_verified!=1U ||
     staged_witness.ordered_topology_verified!=1U ||
     staged_witness.typed_s_unresolved!=1U ||
     staged_witness.typed_v_unresolved!=1U ||
     staged_witness.hash72_commit_authority!=0U ||
     staged_witness.hash216_commit_authority!=0U ||
     staged_witness.vm81_admission_executed!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 if (SHA256(program,program_size,program_digest)==NULL)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 if (!hhs220_symbolic_execute_program(
       staged_witness.source_sha256,program_digest,
       out_execution->ordered_node_roots,
       out_execution->result_node_sha256,&max_depth))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 if (!hhs220_symbolic_execute_program(
       staged_witness.source_sha256,program_digest,
       replay_roots,replay_root,&replay_depth) ||
     max_depth!=replay_depth ||
     memcmp(replay_roots,out_execution->ordered_node_roots,sizeof(replay_roots))!=0 ||
     memcmp(replay_root,out_execution->result_node_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out_execution->steps=HHS220_ORDERED4X4_OPCODE_COUNT;
 out_execution->maximum_stack_depth=max_depth;
 out_execution->matrices_bound=4U;
 out_execution->symbols_bound=2U;
 out_execution->source_identity_verified=1U;
 out_execution->ordered_program_verified=1U;
 out_execution->operator_types_verified=1U;
 out_execution->exact_symbolic_program_executed=1U;
 out_execution->deterministic_symbolic_replay_verified=1U;
 memcpy(out_execution->source_sha256,staged_witness.source_sha256,32U);
 memcpy(out_execution->program_sha256,program_digest,32U);
 /* Semantic equality, matrix values, admission and all receipt flags stay 0. */
 return HHS_EXACT_STATUS_OK;
}
