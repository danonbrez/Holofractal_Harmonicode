#include <jni.h>
#include "hhs_pass158_api.h"

#include <stdlib.h>
#include <string.h>

#define INIT(v) do { memset(&(v),0,sizeof(v)); (v).header.struct_size=(uint32_t)sizeof(v); (v).header.struct_version=HHS158_STRUCT_VERSION_1; } while(0)
#define LIT(s) ((HHS158ByteSpan){(const uint8_t *)(s), sizeof(s)-1u})

JNIEXPORT jstring JNICALL Java_org_hhs_pass158_HHS158_capabilitiesJson(JNIEnv *env, jclass type) {
    HHS158MutableByteSpan output = {0};
    HHS158Status status;
    uint8_t *buffer;
    jstring result;
    (void)type;
    status = hhs158_capabilities_json(&output);
    if (status != HHS158_BUFFER_TOO_SMALL) return (*env)->NewStringUTF(env, hhs158_status_classification(status));
    buffer = (uint8_t *)malloc(output.size_written + 1u);
    if (!buffer) return (*env)->NewStringUTF(env, "MEMORY_BOUND");
    output.data = buffer; output.capacity = output.size_written; output.size_written = 0u;
    status = hhs158_capabilities_json(&output);
    if (status != HHS158_OK) { free(buffer); return (*env)->NewStringUTF(env, hhs158_status_classification(status)); }
    buffer[output.size_written] = '\0';
    result = (*env)->NewStringUTF(env, (const char *)buffer);
    free(buffer);
    return result;
}

JNIEXPORT jstring JNICALL Java_org_hhs_pass158_HHS158_nativeLifecycleSmoke(JNIEnv *env, jclass type) {
    HHS158ContextConfig cc; HHS158Context *context=NULL;
    HHS158DefinitionDescriptor dd; HHS158Definition *definition=NULL; HHS158Receipt *dr=NULL;
    HHS158InstanceConfig ic; HHS158Instance *instance=NULL; HHS158Receipt *ir=NULL;
    HHS158CapabilityRequest cr; HHS158Capability *capability=NULL;
    HHS158Value value; HHS158ValidationPolicy vp; HHS158ValidationReport vr;
    HHS158Operation op; HHS158TransitionDescriptor td; HHS158Transition *transition=NULL;
    HHS158ExecutionOptions eo; HHS158ExecutionResult er; HHS158Receipt *receipt=NULL;
    HHS158ReplayOptions ro; HHS158ReplayResult rr;
    HHS158MutableByteSpan id_output; uint8_t id[HHS158_HASH216_LENGTH+1u];
    uint64_t shape[2]={9u,9u}; HHS158Status status;
    const char *classification="HHS_P158_NFT_INTEGRATION_REQUEST_REJECTED";
    (void)type;

    INIT(cc); cc.abi_major=1u; cc.abi_minor=0u; cc.max_definitions=16u; cc.max_instances=16u; cc.max_receipts=64u;
    cc.max_memory_bytes=UINT64_C(16777216); cc.deterministic_epoch_seconds=UINT64_C(1799711799);
    status=hhs158_context_create(&cc,&context); if(status!=HHS158_OK) goto done;

    INIT(dd); dd.contract_id=LIT("HHS-P158-LLABI-NFTC-API"); dd.schema_version=LIT("1.0.0");
    dd.canonical_name=LIT("JNI_CONSTRAINT_OBJECT"); dd.object_class=LIT("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    dd.canonical_constraints=LIT("A==B==C;O!=Pi"); dd.symbol_table=LIT("A,B,C,O,Pi,x");
    dd.numeric_policy=LIT("EXACT_SYMBOLIC"); dd.operator_policy=LIT("HHS_TYPED_OPERATORS");
    dd.authority_root=LIT("PASS_158_INHERITED_ROOT"); dd.ancestry=LIT("P154|P155|P156|P156.1|P157");
    dd.tensor_rank=2u; dd.tensor_shape=shape;
    status=hhs158_definition_register(context,&dd,&definition,&dr); if(status!=HHS158_OK) goto done;

    INIT(ic); ic.instance_nonce=LIT("jni-instance"); ic.max_vm81_steps=100000u; ic.max_recursion_depth=72u;
    ic.max_state_bytes=16777216u; ic.max_receipt_bytes=1048576u; ic.projection_profile_mask=0xffffffffu;
    status=hhs158_instance_create(context,definition,&ic,&instance,&ir); if(status!=HHS158_OK) goto done;
    id_output.data=id; id_output.capacity=HHS158_HASH216_LENGTH; id_output.size_written=0u;
    status=hhs158_instance_id(instance,&id_output); if(status!=HHS158_OK) goto done; id[HHS158_HASH216_LENGTH]='\0';

    INIT(cr); cr.issuer=LIT("HHS_PASS158_AUTHORITY"); cr.subject=LIT("jni-binding");
    cr.application_id=LIT("org.hhs.pass158.jni"); cr.object_scope.data=id; cr.object_scope.size=HHS158_HASH216_LENGTH;
    cr.operation_scope=HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_EXECUTE|HHS158_CAP_COMMIT|HHS158_CAP_REPLAY;
    cr.mutation_scope=HHS158_MUTATION_INSTANCE; cr.max_vm81_steps=100000u;
    cr.issued_at=UINT64_C(1799711700); cr.expires_at=UINT64_C(1799719999);
    status=hhs158_capability_open(context,&cr,&capability); if(status!=HHS158_OK) goto done;

    INIT(value); value.kind=HHS158_VALUE_RATIONAL; value.flags=HHS158_FLAG_AUTHORITATIVE|HHS158_FLAG_IMMUTABLE;
    value.canonical_payload=LIT("1/3"); { HHS158Receipt *binding_receipt=NULL; status=hhs158_instance_bind_authorized(instance,capability,LIT("x"),&value,&binding_receipt); } if(status!=HHS158_OK) goto done;
    INIT(vp); vp.max_vm81_steps=100000u; vp.max_recursion_depth=72u;
    status=hhs158_instance_validate_static(instance,&vp,&vr); if(status!=HHS158_OK) goto done;

    INIT(op); op.opcode=HHS158_OP_BIND_EQ; op.operands=LIT("A,B");
    INIT(td); td.operations=&op; td.operation_count=1u; td.expected_pre_state_root.data=(const uint8_t*)vr.state_root;
    td.expected_pre_state_root.size=HHS158_HASH216_LENGTH; td.max_vm81_steps=1000u; td.max_recursion_depth=72u; td.max_output_bytes=1048576u;
    status=hhs158_transition_create(instance,capability,&td,&transition); if(status!=HHS158_OK) goto done;
    INIT(eo); eo.max_vm81_steps=1000u; eo.atomic_execute_and_commit=1u;
    status=hhs158_transition_execute(transition,&eo,&er,&receipt); if(status!=HHS158_OK) goto done;
    INIT(ro); ro.verify_hash72=1u; ro.verify_hash216=1u; ro.verify_semantic_root=1u;
    status=hhs158_receipt_replay(context,receipt,&ro,&rr); if(status!=HHS158_OK||!rr.matched) goto done;
    classification="HHS_P158_NFT_TRANSITION_REPLAY_VERIFIED";

done:
    if(context) hhs158_context_release(context);
    return (*env)->NewStringUTF(env, status==HHS158_OK?classification:hhs158_status_classification(status));
}
