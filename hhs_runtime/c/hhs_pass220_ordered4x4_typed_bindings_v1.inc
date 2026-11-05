/* Native exact typed 5184-character s/v candidate execution.
 * Does not scalarize, evaluate tensor values or authenticate signed receipts.
 * Reuses the single inherited source-bound HIR parser and operator evaluator.
 */
#include "../include/hhs_pass220_ordered4x4_typed_bindings_v1.h"
#include <openssl/sha.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#define HHS220_BIND_MATERIAL_CAPACITY (HHS220_ORDERED4X4_MAX_UTF8_BYTES + 512U)

static int hhs220_bound_utf8_exact(
 const uint8_t *bytes, size_t length, uint32_t *out_characters
) {
 size_t i=0U;
 uint32_t count=0U;
 if (bytes==NULL || out_characters==NULL || length==0U ||
     length>HHS220_ORDERED4X4_MAX_UTF8_BYTES) return 0;
 while (i<length) {
  uint8_t b=bytes[i];
  size_t span=0U,j;
  if (b>=0x21U && b<=0x7EU) span=1U;
  else if (b>=0xC2U && b<=0xDFU) span=2U;
  else if (b>=0xE0U && b<=0xEFU) span=3U;
  else if (b>=0xF0U && b<=0xF4U) span=4U;
  else return 0;
  if (span>length-i) return 0;
  for(j=1U;j<span;++j)
   if ((bytes[i+j]&0xC0U)!=0x80U) return 0;
  if (span==3U) {
   if ((b==0xE0U && bytes[i+1U]<0xA0U) ||
       (b==0xEDU && bytes[i+1U]>=0xA0U)) return 0;
  } else if (span==4U) {
   if ((b==0xF0U && bytes[i+1U]<0x90U) ||
       (b==0xF4U && bytes[i+1U]>0x8FU)) return 0;
  }
  i+=span;
  ++count;
  if (count>HHS220_ORDERED4X4_NATIVE_CHARACTERS) return 0;
 }
 if (count!=HHS220_ORDERED4X4_NATIVE_CHARACTERS) return 0;
 *out_characters=count;
 return 1;
}

static int hhs220_bound_digest(
 const HHS220Ordered4x4NativeTensorBindingV1 *binding,
 uint8_t required_symbol,
 uint8_t out_digest[32], uint32_t *out_chars
) {
 static const char DOMAIN[]="HHS-P220-4X4-EXACT-TENSOR-BINDING-NONAUTHORITATIVE-V1";
 uint8_t material[HHS220_BIND_MATERIAL_CAPACITY];
 size_t cursor=0U,i;
 size_t domain_bytes=sizeof(DOMAIN)-1U;
 uint32_t chars=0U;
 if (binding==NULL || out_digest==NULL || out_chars==NULL ||
     binding->struct_size!=sizeof(*binding) ||
     binding->symbol!=required_symbol || binding->reserved!=0U ||
     binding->cell81>=81U || binding->operation64>=64U ||
     binding->predecessor_hash216==NULL ||
     binding->predecessor_bytes!=HHS220_ORDERED4X4_PARENT_GLYPHS ||
     !hhs220_bound_utf8_exact(binding->state_utf8,binding->state_bytes,&chars))
  return 0;
 for(i=0U;i<binding->predecessor_bytes;++i)
  if (binding->predecessor_hash216[i]<33U ||
      binding->predecessor_hash216[i]>126U) return 0;

 memcpy(material+cursor,DOMAIN,domain_bytes); cursor+=domain_bytes;
 material[cursor++]=binding->symbol;
 material[cursor++]=binding->cell81;
 material[cursor++]=binding->operation64;
 material[cursor++]=(uint8_t)(binding->state_bytes>>24U);
 material[cursor++]=(uint8_t)(binding->state_bytes>>16U);
 material[cursor++]=(uint8_t)(binding->state_bytes>>8U);
 material[cursor++]=(uint8_t)(binding->state_bytes);
 memcpy(material+cursor,binding->predecessor_hash216,binding->predecessor_bytes);
 cursor+=binding->predecessor_bytes;
 memcpy(material+cursor,binding->state_utf8,binding->state_bytes);
 cursor+=binding->state_bytes;
 if (cursor>sizeof(material) || SHA256(material,cursor,out_digest)==NULL)
  return 0;
 *out_chars=chars;
 return 1;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_execute_bound(
 const uint8_t *source,size_t source_size,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 HHS220Ordered4x4BoundExecutionV1 *out_execution
) {
 HHSExactVM81Frame source_frame;
 HHS220Ordered4x4HIRWitnessV1 source_witness;
 uint8_t program_digest[32];
 uint8_t replay_nodes[HHS220_ORDERED4X4_OPCODE_COUNT][32];
 uint8_t replay_root[32];
 uint32_t s_chars=0U,v_chars=0U,max_depth=0U,replay_depth=0U;
 HHSExactStatus status;
 if (out_execution==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_execution,0,sizeof(*out_execution));
 out_execution->struct_size=(uint32_t)sizeof(*out_execution);
 out_execution->version=UINT32_C(0x00010000);
 if (source==NULL || s==NULL || v==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 if (!hhs220_bound_digest(s,(uint8_t)'s',
         out_execution->binding_roots_sha256[0],&s_chars) ||
     !hhs220_bound_digest(v,(uint8_t)'v',
         out_execution->binding_roots_sha256[1],&v_chars) ||
     memcmp(s->predecessor_hash216,v->predecessor_hash216,
            HHS220_ORDERED4X4_PARENT_GLYPHS)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 status=hhs_exact_pass220_ordered4x4_lower(
    source,source_size,&source_frame,&source_witness);
 if (status!=HHS_EXACT_STATUS_OK ||
     source_witness.source_identity_verified!=1U ||
     source_witness.ordered_topology_verified!=1U ||
     source_witness.vm81_admission_executed!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 if (SHA256(HHS220_ORDERED4X4_PROGRAM,
            HHS220_ORDERED4X4_OPCODE_COUNT,program_digest)==NULL ||
     !hhs220_symbolic_execute_program(
       source_witness.source_sha256,program_digest,
       (const uint8_t (*)[32])out_execution->binding_roots_sha256,
       out_execution->ordered_node_roots,
       out_execution->result_root_sha256,&max_depth) ||
     !hhs220_symbolic_execute_program(
       source_witness.source_sha256,program_digest,
       (const uint8_t (*)[32])out_execution->binding_roots_sha256,
       replay_nodes,replay_root,&replay_depth) ||
     max_depth!=replay_depth ||
     memcmp(out_execution->ordered_node_roots,replay_nodes,
            sizeof(replay_nodes))!=0 ||
     memcmp(out_execution->result_root_sha256,replay_root,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;

 out_execution->ordered_opcodes=HHS220_ORDERED4X4_OPCODE_COUNT;
 out_execution->maximum_stack_depth=max_depth;
 out_execution->s_codepoints=s_chars;
 out_execution->v_codepoints=v_chars;
 out_execution->s_serialized_bytes=(uint32_t)s->state_bytes;
 out_execution->v_serialized_bytes=(uint32_t)v->state_bytes;
 out_execution->s_vm5184_address=(uint16_t)(64U*s->cell81+s->operation64);
 out_execution->v_vm5184_address=(uint16_t)(64U*v->cell81+v->operation64);
 out_execution->source_identity_verified=1U;
 out_execution->ordered_type_graph_executed=1U;
 out_execution->deterministic_bound_graph_replay_verified=1U;
 out_execution->typed_bindings_shape_verified=1U;
 out_execution->native_predecessor_identity_matched=1U;
 /* No signed receipt verification, no numeric evaluation, no mutation. */
 return HHS_EXACT_STATUS_OK;
}
