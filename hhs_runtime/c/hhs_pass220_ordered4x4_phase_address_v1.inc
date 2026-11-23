/* HHS: exact VM81 phase-address interpretation, not inferred scalarization.
 * Reuses inherited VM81 coordinate encode/decode and native RNA phase product.
 * No tensor-action rank, full phase closure or signed authority is implied.
 */
#include "../include/hhs_pass220_ordered4x4_phase_address_v1.h"
#include <openssl/sha.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>

static int hhs220_phase_address_root(
 const uint8_t source[32],const uint8_t parent[32],
 const HHS220Ordered4x4PhaseAddressV1 *address,uint8_t output[32]
) {
 static const char domain[]="HHS-P220-ORDERED4X4-VM81-PHASE-ADDRESS-V1";
 uint8_t bytes[sizeof(domain)-1U+32U+32U+32U+13U];
 size_t cursor=0U;
 const HHSExactPhaseProduct *phase=&address->native_phase_witness.ordered_product;
 memcpy(bytes+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 memcpy(bytes+cursor,source,32U);cursor+=32U;
 memcpy(bytes+cursor,parent,32U);cursor+=32U;
 memcpy(bytes+cursor,address->source_bound_symbol_root,32U);cursor+=32U;
 bytes[cursor++]=address->symbol;
 bytes[cursor++]=address->cell81;
 bytes[cursor++]=address->operation64;
 bytes[cursor++]=address->left_phase_basis8;
 bytes[cursor++]=address->right_phase_basis8;
 bytes[cursor++]=(uint8_t)(address->address5184>>8U);
 bytes[cursor++]=(uint8_t)address->address5184;
 bytes[cursor++]=phase->phase;
 bytes[cursor++]=phase->raw_additive_phase;
 bytes[cursor++]=phase->orientation;
 bytes[cursor++]=phase->closure;
 bytes[cursor++]=(uint8_t)(phase->ordered_tag>>8U);
 bytes[cursor++]=(uint8_t)phase->ordered_tag;
 return cursor==sizeof(bytes) && SHA256(bytes,sizeof(bytes),output)!=NULL;
}

static HHSExactStatus hhs220_phase_address_one(
 const uint8_t source_root[32],const uint8_t parent_root[32],
 const HHS220Ordered4x4NativeTensorBindingV1 *binding,
 const uint8_t binding_root[32],HHS220Ordered4x4PhaseAddressV1 *out
) {
 uint16_t encoded=0U,expected=0U;
 uint8_t cell=0U,left=0U,right=0U;
 HHSExactStatus status;
 if(binding==NULL || out==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out,0,sizeof(*out));
 out->struct_size=(uint32_t)sizeof(*out);
 out->version=UINT32_C(0x00010000);
 expected=(uint16_t)(64U*(uint16_t)binding->cell81+(uint16_t)binding->operation64);
 status=hhs_exact_vm5184_address_decode(expected,&cell,&left,&right);
 if(status!=HHS_EXACT_STATUS_OK || cell!=binding->cell81 ||
    left>=HHS_EXACT_PHASE_BASIS_COUNT ||
    right>=HHS_EXACT_PHASE_BASIS_COUNT ||
    (uint16_t)(8U*(uint16_t)left+(uint16_t)right)!=binding->operation64)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_vm5184_address_encode(cell,left,right,&encoded);
 if(status!=HHS_EXACT_STATUS_OK || encoded!=expected)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass219_native_phase_witness(
          left,right,&out->native_phase_witness);
 if(status!=HHS_EXACT_STATUS_OK ||
    out->native_phase_witness.struct_size!=sizeof(HHSExactPass219NativePhaseWitnessV1) ||
    out->native_phase_witness.version!=hhs_exact_pass219_rna_version() ||
    out->native_phase_witness.ordered_source_preserved!=1U ||
    out->native_phase_witness.left_basis!=left ||
    out->native_phase_witness.right_basis!=right ||
    out->native_phase_witness.ordered_product.left_basis!=left ||
    out->native_phase_witness.ordered_product.right_basis!=right)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out->symbol=binding->symbol;
 out->cell81=cell;
 out->operation64=binding->operation64;
 out->address5184=encoded;
 out->left_phase_basis8=left;
 out->right_phase_basis8=right;
 memcpy(out->source_bound_symbol_root,binding_root,32U);
 if(!hhs220_phase_address_root(
      source_root,parent_root,out,out->directional_phase_address_root))
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out->address_roundtrip_verified=1U;
 out->native_phase_operator_executed=1U;
 out->native_ordered_source_preserved=1U;
 return HHS_EXACT_STATUS_OK;
}

HHSExactStatus hhs_exact_pass220_ordered4x4_phase_address_gate(
 const uint8_t *source,size_t source_bytes,
 const HHS220Ordered4x4NativeTensorBindingV1 *s,
 const HHS220Ordered4x4NativeTensorBindingV1 *v,
 const HHSExactPass219Hash216TransitionViewV1 *parent_reference,
 HHS220Ordered4x4PhaseAddressGateV1 *out_gate
) {
 static const char domain[]="HHS-P220-ORDERED4X4-BOUND-PHASE-GEOMETRY-V1";
 HHS220Ordered4x4OuterGeometryV1 geometry;
 HHS220Ordered4x4BoundExecutionV1 bound;
 uint8_t material[sizeof(domain)-1U+32U*4U];
 size_t cursor=0U;
 HHSExactStatus status;
 if(out_gate==NULL) return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 memset(out_gate,0,sizeof(*out_gate));
 out_gate->struct_size=(uint32_t)sizeof(*out_gate);
 out_gate->version=UINT32_C(0x00010000);
 if(source==NULL || s==NULL || v==NULL || parent_reference==NULL)
  return HHS_EXACT_STATUS_INVALID_ARGUMENT;
 status=hhs_exact_pass220_ordered4x4_outer_geometry(
   source,source_bytes,s,v,parent_reference,&geometry);
 if(status!=HHS_EXACT_STATUS_OK ||
    geometry.source_identity_verified!=1U ||
    geometry.inherited_hash216_index_preflight_verified!=1U ||
    geometry.typed_5184_bindings_verified!=1U ||
    geometry.ordered_operand_roles_verified!=1U ||
    geometry.parent_signed_authenticity_verified!=0U ||
    geometry.equation_equality_proved!=0U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 status=hhs_exact_pass220_ordered4x4_execute_bound(
   source,source_bytes,s,v,&bound);
 if(status!=HHS_EXACT_STATUS_OK ||
    bound.source_identity_verified!=1U ||
    bound.typed_bindings_shape_verified!=1U ||
    bound.deterministic_bound_graph_replay_verified!=1U ||
    memcmp(bound.result_root_sha256,geometry.bound_graph_root_sha256,32U)!=0)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 memcpy(out_gate->source_sha256,geometry.source_sha256,32U);
 memcpy(out_gate->parent_reference_sha256,geometry.parent_reference_sha256,32U);
 if(hhs220_phase_address_one(
       geometry.source_sha256,geometry.parent_reference_sha256,
       s,bound.binding_roots_sha256[0],&out_gate->bindings[0])!=HHS_EXACT_STATUS_OK ||
    hhs220_phase_address_one(
       geometry.source_sha256,geometry.parent_reference_sha256,
       v,bound.binding_roots_sha256[1],&out_gate->bindings[1])!=HHS_EXACT_STATUS_OK)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 if(out_gate->bindings[0].symbol!='s' ||
    out_gate->bindings[1].symbol!='v' ||
    out_gate->bindings[0].address_roundtrip_verified!=1U ||
    out_gate->bindings[1].address_roundtrip_verified!=1U)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 memcpy(material+cursor,domain,sizeof(domain)-1U);
 cursor+=sizeof(domain)-1U;
 memcpy(material+cursor,geometry.source_sha256,32U);cursor+=32U;
 memcpy(material+cursor,geometry.parent_reference_sha256,32U);cursor+=32U;
 memcpy(material+cursor,out_gate->bindings[0].directional_phase_address_root,32U);
 cursor+=32U;
 memcpy(material+cursor,out_gate->bindings[1].directional_phase_address_root,32U);
 cursor+=32U;
 if(cursor!=sizeof(material) ||
    SHA256(material,sizeof(material),out_gate->phase_geometry_root_sha256)==NULL)
  return HHS_EXACT_STATUS_INVARIANT_FAILURE;
 out_gate->verbatim_source_verified=1U;
 out_gate->inherited_parent_index_verified=1U;
 out_gate->ordered_outer_geometry_verified=1U;
 out_gate->both_phase_address_roundtrips_verified=1U;
 out_gate->both_native_phase_products_verified=1U;
 /* Intentional non-authority: phase-address witness != whole tensor proof. */
 return HHS_EXACT_STATUS_OK;
}
