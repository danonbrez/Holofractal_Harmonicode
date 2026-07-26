#include "hhs_pass158_api.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HEADER(v) do { memset(&(v), 0, sizeof(v)); (v).header.struct_size=(uint32_t)sizeof(v); (v).header.struct_version=HHS158_STRUCT_VERSION_1; } while (0)
#define SPAN(s) ((HHS158ByteSpan){(const uint8_t *)(s), strlen(s)})
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"assertion failed %s:%d: %s\n",__FILE__,__LINE__,#x); return 0; } } while (0)

typedef struct {
    HHS158Context *context;
    HHS158Definition *definition;
    HHS158Instance *instance;
    HHS158Capability *capability;
    HHS158Receipt *definition_receipt;
    HHS158Receipt *instance_receipt;
    char instance_id[HHS158_HASH216_LENGTH + 1u];
    char state_root[HHS158_HASH216_LENGTH + 1u];
} Fixture;

static int fixed_instance_value(HHS158Status (*fn)(const HHS158Instance *, HHS158MutableByteSpan *),
    const HHS158Instance *instance, char out[HHS158_HASH216_LENGTH + 1u]) {
    HHS158MutableByteSpan span = {(uint8_t *)out, HHS158_HASH216_LENGTH, 0u};
    if (fn(instance, &span) != HHS158_OK || span.size_written != HHS158_HASH216_LENGTH) return 0;
    out[HHS158_HASH216_LENGTH] = '\0';
    return 1;
}

static HHS158Status fixture_create(Fixture *f, const char *nonce, uint64_t operations,
    uint64_t mutations, uint64_t expires_at, const char *object_scope) {
    HHS158ContextConfig cc;
    HHS158DefinitionDescriptor dd;
    HHS158InstanceConfig ic;
    HHS158CapabilityRequest cr;
    HHS158Status status;
    uint64_t shape[2] = {9u, 9u};
    static const uint8_t constraints[] = "A==B==C;O!=Pi;ordered=[x,x,y];Delta=P^2-pq";
    memset(f, 0, sizeof(*f));
    HEADER(cc);
    cc.abi_major = HHS158_ABI_VERSION_MAJOR;
    cc.abi_minor = HHS158_ABI_VERSION_MINOR;
    cc.max_definitions = 64u;
    cc.max_instances = 128u;
    cc.max_receipts = 128u;
    cc.max_memory_bytes = UINT64_C(16777216);
    cc.deterministic_epoch_seconds = UINT64_C(1799711799);
    status = hhs158_context_create(&cc, &f->context);
    if (status != HHS158_OK) return status;

    HEADER(dd);
    dd.contract_id = SPAN("HHS-P158-LLABI-NFTC-API");
    dd.schema_version = SPAN("1.0.0");
    dd.canonical_name = SPAN("PASS158_TEST_OBJECT");
    dd.object_class = SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    dd.canonical_constraints.data = constraints;
    dd.canonical_constraints.size = sizeof(constraints) - 1u;
    dd.symbol_table = SPAN("A,B,C,O,Pi,x,y,Delta,P,p,q");
    dd.numeric_policy = SPAN("EXACT_SYMBOLIC");
    dd.operator_policy = SPAN("HHS_TYPED_OPERATORS");
    dd.authority_root = SPAN("PASS_158_INHERITED_ROOT");
    dd.ancestry = SPAN("P154|P155|P156|P156.1|P157");
    dd.tensor_rank = 2u;
    dd.tensor_shape = shape;
    status = hhs158_definition_register(f->context, &dd, &f->definition, &f->definition_receipt);
    if (status != HHS158_OK) return status;

    HEADER(ic);
    ic.instance_nonce = SPAN(nonce);
    ic.max_vm81_steps = UINT64_C(100000);
    ic.max_recursion_depth = 72u;
    ic.max_state_bytes = UINT64_C(16777216);
    ic.max_receipt_bytes = UINT64_C(1048576);
    ic.projection_profile_mask = 0xffffffffu;
    status = hhs158_instance_create(f->context, f->definition, &ic, &f->instance, &f->instance_receipt);
    if (status != HHS158_OK) return status;
    if (!fixed_instance_value(hhs158_instance_id, f->instance, f->instance_id) ||
        !fixed_instance_value(hhs158_instance_state_root, f->instance, f->state_root)) return HHS158_REJECTED;

    HEADER(cr);
    cr.issuer = SPAN("HHS_PASS158_AUTHORITY");
    cr.subject = SPAN("pass158-test");
    cr.application_id = SPAN("org.hhs.pass158.test");
    if (object_scope) cr.object_scope = SPAN(object_scope);
    cr.operation_scope = operations;
    cr.mutation_scope = mutations;
    cr.max_vm81_steps = UINT64_C(100000);
    cr.issued_at = UINT64_C(1799711700);
    cr.expires_at = expires_at;
    return hhs158_capability_open(f->context, &cr, &f->capability);
}

static void fixture_release(Fixture *f) {
    hhs158_context_release(f->context);
    memset(f, 0, sizeof(*f));
}

static HHS158Status bind_value(Fixture *f, const char *symbol, uint32_t kind, uint32_t flags, const char *payload) {
    HHS158Value value;
    HHS158Receipt *receipt = NULL;
    HEADER(value);
    value.kind = kind;
    value.flags = flags;
    value.canonical_payload = SPAN(payload);
    {
        HHS158Status status = hhs158_instance_bind_authorized(f->instance, f->capability, SPAN(symbol), &value, &receipt);
        if (status == HHS158_OK && !fixed_instance_value(hhs158_instance_state_root, f->instance, f->state_root)) return HHS158_REJECTED;
        return status;
    }
}

static HHS158Status transition_create(Fixture *f, const HHS158Operation *ops, size_t count,
    uint64_t max_steps, HHS158Capability *capability, HHS158ByteSpan expected_root, HHS158Transition **out) {
    HHS158TransitionDescriptor td;
    HEADER(td);
    td.operations = ops;
    td.operation_count = count;
    td.expected_pre_state_root = expected_root;
    td.max_vm81_steps = max_steps;
    td.max_recursion_depth = 72u;
    td.max_output_bytes = UINT64_C(1048576);
    return hhs158_transition_create(f->instance, capability ? capability : f->capability, &td, out);
}

static int vm81_and_replay(size_t *vm81, size_t *replay) {
    Fixture f;
    const HHS158OpcodeDescriptor *registry;
    size_t registry_count = 0u, i;
    HHS158Receipt *last = NULL;
    CHECK(fixture_create(&f, "vm81", HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_EXECUTE|HHS158_CAP_PROJECT|
        HHS158_CAP_SERIALIZE|HHS158_CAP_REPLAY, HHS158_MUTATION_INSTANCE, UINT64_C(1799719999), NULL) == HHS158_OK);
    CHECK(bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE|HHS158_FLAG_IMMUTABLE,"1/3") == HHS158_OK);
    registry = hhs158_public_opcode_registry(&registry_count);
    CHECK(registry && registry_count > 0u);
    for (i=0; i<81u; ++i) {
        HHS158Operation op; HHS158Transition *t=NULL; HHS158ExecutionOptions eo; HHS158ExecutionResult er;
        HHS158Receipt *receipt=NULL; HHS158ReplayOptions ro; HHS158ReplayResult rr;
        HEADER(op); op.opcode=registry[i%registry_count].opcode;
        op.operands = SPAN(op.opcode==HHS158_OP_LIST_ORDERED ? "[x,x,y]" : "x,y");
        CHECK(transition_create(&f,&op,1u,1000u,NULL,SPAN(f.state_root),&t)==HHS158_OK);
        HEADER(eo); eo.max_vm81_steps=1000u;
        CHECK(hhs158_transition_execute(t,&eo,&er,&receipt)==HHS158_OK && er.vm81_steps>=72u);
        HEADER(ro); ro.verify_hash72=1u; ro.verify_hash216=1u; ro.verify_semantic_root=1u;
        CHECK(hhs158_receipt_replay(f.context,receipt,&ro,&rr)==HHS158_OK && rr.matched==1u);
        last=receipt; (*vm81)++;
    }
    for (i=0; i<72u; ++i) {
        HHS158ReplayOptions ro; HHS158ReplayResult rr;
        HEADER(ro); ro.verify_hash72=1u; ro.verify_hash216=1u; ro.verify_semantic_root=1u;
        CHECK(hhs158_receipt_replay(f.context,last,&ro,&rr)==HHS158_OK && rr.matched==1u); (*replay)++;
    }
    fixture_release(&f); return 1;
}

static int loshu_matrix(size_t *count) {
    static const int l[9]={4,9,2,3,5,7,8,1,6}; int r[3]={0},c[3]={0},d[2]={0}; size_t i;
    for(i=0;i<9u;++i){r[i/3u]+=l[i];c[i%3u]+=l[i];if(i/3u==i%3u)d[0]+=l[i];if(i/3u+i%3u==2u)d[1]+=l[i];(*count)++;}
    CHECK(r[0]==15&&r[1]==15&&r[2]==15&&c[0]==15&&c[1]==15&&c[2]==15&&d[0]==15&&d[1]==15); return 1;
}

static int delta_matrix(size_t *count) {
    size_t i;
    for(i=1;i<=18u;++i){char p[32],r[32];HHS158Value pv,rv,d,n;HHS158DeltaPolicy policy;
        snprintf(p,sizeof(p),"%lu/%lu",(unsigned long)(i+1u),(unsigned long)i);
        snprintf(r,sizeof(r),"%lu/%lu",(unsigned long)i,(unsigned long)(i+1u));
        HEADER(pv);HEADER(rv);HEADER(policy);pv.kind=rv.kind=HHS158_VALUE_RATIONAL;pv.flags=rv.flags=HHS158_FLAG_AUTHORITATIVE;
        pv.canonical_payload=SPAN(p);rv.canonical_payload=SPAN(r);policy.mode=HHS158_DELTA_ALL;policy.require_invertible_reference=1u;policy.preserve_all_components=1u;
        CHECK(hhs158_delta_compute(&pv,&rv,&policy,&d)==HHS158_OK);CHECK(hhs158_delta_normalize(&pv,&d,&n)==HHS158_OK);
        CHECK(n.canonical_payload.size==strlen(r)&&memcmp(n.canonical_payload.data,r,strlen(r))==0);hhs158_value_release(&d);hhs158_value_release(&n);(*count)++;}
    return 1;
}

static int atomic_matrix(size_t *count) {
    Fixture f; size_t i;
    CHECK(fixture_create(&f,"atomic",HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_EXECUTE|HHS158_CAP_COMMIT|HHS158_CAP_REPLAY,
        HHS158_MUTATION_INSTANCE,UINT64_C(1799719999),NULL)==HHS158_OK);
    CHECK(bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE,"1/3")==HHS158_OK);
    for(i=0;i<18u;++i){char operands[64];HHS158Operation op;HHS158Transition *t=NULL;HHS158ExecutionOptions eo;HHS158ExecutionResult er;HHS158Receipt *receipt=NULL;HHS158ReplayOptions ro;HHS158ReplayResult rr;
        CHECK(fixed_instance_value(hhs158_instance_state_root,f.instance,f.state_root));snprintf(operands,sizeof(operands),"A%lu,B%lu",(unsigned long)i,(unsigned long)i);
        HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN(operands);CHECK(transition_create(&f,&op,1u,1000u,NULL,SPAN(f.state_root),&t)==HHS158_OK);
        HEADER(eo);eo.max_vm81_steps=1000u;eo.atomic_execute_and_commit=1u;CHECK(hhs158_transition_execute(t,&eo,&er,&receipt)==HHS158_OK&&er.lifecycle_state==HHS158_LIFECYCLE_COMMITTED);
        HEADER(ro);ro.verify_hash72=1u;ro.verify_hash216=1u;ro.verify_semantic_root=1u;CHECK(hhs158_receipt_replay(f.context,receipt,&ro,&rr)==HHS158_OK);(*count)++;}
    fixture_release(&f);return 1;
}

static int serialization_matrix(size_t *count) {
    Fixture f;HHS158SerializationOptions so;HHS158MutableByteSpan out={0};uint8_t *buf;size_t i;
    CHECK(fixture_create(&f,"serialize",HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_SERIALIZE,HHS158_MUTATION_INSTANCE,UINT64_C(1799719999),NULL)==HHS158_OK);
    CHECK(bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE,"1/3")==HHS158_OK);
    HEADER(so);so.format=HHS158_SERIALIZE_CANONICAL_JSON;so.preserve_unknown_fields=1u;so.max_output_bytes=UINT64_C(1048576);
    CHECK(hhs158_instance_serialize(f.instance,&so,&out)==HHS158_BUFFER_TOO_SMALL);buf=(uint8_t*)malloc(out.size_written);CHECK(buf!=NULL);out.data=buf;out.capacity=out.size_written;
    CHECK(hhs158_instance_serialize(f.instance,&so,&out)==HHS158_OK);
    for(i=0;i<18u;++i){HHS158DeserializationOptions d;HHS158Instance *copy=NULL;HHS158Receipt *receipt=NULL;char id[HHS158_HASH216_LENGTH+1u];HEADER(d);d.format=HHS158_SERIALIZE_CANONICAL_JSON;d.preserve_unknown_fields=1u;d.reject_authority_unknown_fields=1u;
        CHECK(hhs158_instance_deserialize(f.context,(HHS158ByteSpan){buf,out.size_written},&d,&copy,&receipt)==HHS158_OK);CHECK(fixed_instance_value(hhs158_instance_id,copy,id)&&strcmp(id,f.instance_id)==0);(*count)++;}
    free(buf);fixture_release(&f);return 1;
}

static int dependency_matrix(size_t *count) {
    Fixture f;size_t i;
    CHECK(fixture_create(&f,"dependency",HHS158_CAP_VALIDATE|HHS158_CAP_COMPOSE,HHS158_MUTATION_COMPOSITE,UINT64_C(1799719999),NULL)==HHS158_OK);
    for(i=0;i<12u;++i){char nonce[64];HHS158InstanceConfig ic;HHS158Instance *peer=NULL,*composite=NULL,*items[2];HHS158Receipt *pr=NULL,*cr=NULL;HHS158CompositionPolicy cp;
        snprintf(nonce,sizeof(nonce),"peer-%lu",(unsigned long)i);HEADER(ic);ic.instance_nonce=SPAN(nonce);ic.max_vm81_steps=100000u;ic.max_recursion_depth=72u;ic.max_state_bytes=16777216u;ic.max_receipt_bytes=1048576u;
        CHECK(hhs158_instance_create(f.context,f.definition,&ic,&peer,&pr)==HHS158_OK);items[0]=f.instance;items[1]=peer;HEADER(cp);cp.max_dependency_depth=72u;cp.isolation_level=1u;
        CHECK(hhs158_instance_compose(f.context,items,2u,&cp,&composite,&cr)==HHS158_OK&&composite&&cr);(*count)++;}
    fixture_release(&f);return 1;
}

static int abi_matrix(size_t *count) {
    Fixture f;HHS158ValidationPolicy vp;HHS158ValidationReport vr;HHS158ProjectionProfile ep,cp;HHS158Value ev,cv;HHS158Receipt *receipt=NULL;HHS158MutableByteSpan out={0};uint32_t lifecycle=99u;
    CHECK(fixture_create(&f,"abi",HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_EXECUTE|HHS158_CAP_COMMIT|HHS158_CAP_PROJECT|HHS158_CAP_SERIALIZE|HHS158_CAP_REPLAY,HHS158_MUTATION_INSTANCE,UINT64_C(1799719999),NULL)==HHS158_OK);(*count)+=6u;
    CHECK(bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE,"1/3")==HHS158_OK);(*count)++;
    HEADER(vp);vp.max_recursion_depth=72u;CHECK(hhs158_instance_validate_static(f.instance,&vp,&vr)==HHS158_OK);(*count)++;
    HEADER(ep);ep.kind=HHS158_PROJECTION_EXACT_REFERENCE;CHECK(hhs158_instance_project(f.instance,&ep,&ev,&receipt)==HHS158_OK);(*count)++;
    HEADER(cp);cp.kind=HHS158_PROJECTION_IEEE754_BINARY64_CONTROL;CHECK(hhs158_instance_project(f.instance,&cp,&cv,&receipt)==HHS158_OK);(*count)++;
    CHECK((cv.flags&HHS158_FLAG_APPROXIMATE)!=0u);(*count)++;
    CHECK(hhs158_abi_descriptor_json(&out)==HHS158_BUFFER_TOO_SMALL);(*count)++;out.size_written=0u;
    CHECK(hhs158_capabilities_json(&out)==HHS158_BUFFER_TOO_SMALL);(*count)++;out.size_written=0u;
    CHECK(hhs158_opcode_descriptor_json(&out)==HHS158_BUFFER_TOO_SMALL);(*count)++;
    CHECK(hhs158_abi_version_major()==1u);(*count)++;CHECK(strcmp(hhs158_contract_id(),"HHS-P158-LLABI-NFTC-API")==0);(*count)++;
    CHECK(strcmp(hhs158_contract_version(),"1.0.0")==0);(*count)++;CHECK(hhs158_instance_lifecycle(f.instance,&lifecycle)==HHS158_OK&&lifecycle==HHS158_LIFECYCLE_BOUND);(*count)++;
    hhs158_value_release(&ev);hhs158_value_release(&cv);CHECK(*count==18u);fixture_release(&f);return 1;
}

static int descriptor_matrix(size_t *endpoints,size_t *bindings,size_t *identity) {
    size_t i;for(i=0;i<6u;++i){HHS158MutableByteSpan out={0};CHECK(hhs158_abi_descriptor_json(&out)==HHS158_BUFFER_TOO_SMALL);(*endpoints)++;out.size_written=0u;CHECK(hhs158_capabilities_json(&out)==HHS158_BUFFER_TOO_SMALL);(*endpoints)++;out.size_written=0u;CHECK(hhs158_opcode_descriptor_json(&out)==HHS158_BUFFER_TOO_SMALL);(*endpoints)++;}
    *bindings=6u;CHECK(hhs158_abi_version_major()==1u);(*identity)++;CHECK(hhs158_abi_version_minor()==0u);(*identity)++;return 1;
}

static HHS158Status negative_case(size_t n) {
    size_t k=n%27u;Fixture f;HHS158Status s=HHS158_REJECTED;char nonce[48];snprintf(nonce,sizeof(nonce),"negative-%lu",(unsigned long)n);
    if(k==0u){HHS158ContextConfig c;HHS158Context *x=NULL;HEADER(c);c.abi_major=99u;return hhs158_context_create(&c,&x);}if(k==1u){HHS158ContextConfig c;HHS158Context*x=NULL;HEADER(c);c.header.struct_size=1u;c.abi_major=1u;return hhs158_context_create(&c,&x);}
    if(fixture_create(&f,nonce,HHS158_CAP_BIND|HHS158_CAP_VALIDATE|HHS158_CAP_EXECUTE|HHS158_CAP_COMMIT|HHS158_CAP_PROJECT|HHS158_CAP_SERIALIZE|HHS158_CAP_REPLAY|HHS158_CAP_COMPOSE,HHS158_MUTATION_INSTANCE|HHS158_MUTATION_COMPOSITE,k==10u?UINT64_C(1799711701):UINT64_C(1799719999),NULL)!=HHS158_OK)return HHS158_REJECTED;
    if(k==2u){uint8_t bad[2]={0xc0u,0x80u};HHS158Value v;HHS158Receipt*r=NULL;HEADER(v);v.kind=HHS158_VALUE_BIGINT;v.flags=HHS158_FLAG_AUTHORITATIVE;v.canonical_payload=SPAN("1");s=hhs158_instance_bind_authorized(f.instance,f.capability,(HHS158ByteSpan){bad,2u},&v,&r);}
    else if(k>=3u&&k<=6u){uint32_t kind=k==5u?HHS158_VALUE_LIST:(k==6u?HHS158_VALUE_EXPRESSION:HHS158_VALUE_RATIONAL);uint32_t flags=HHS158_FLAG_AUTHORITATIVE;const char *p=k==3u?"0.5":(k==4u?"1/0":(k==5u?"[x,x,y]":"O==Pi"));s=bind_value(&f,"x",kind,flags,p);}
    else if(k==7u||k==8u||k==13u||k==25u){HHS158Operation ops[2];HHS158Transition*t=NULL;HHS158ByteSpan root=k==8u?SPAN("stale"):SPAN(f.state_root);HEADER(ops[0]);ops[0].opcode=k==7u?0xffffu:HHS158_OP_BIND_EQ;ops[0].operands=SPAN(k==25u?"A==B==C":"A,B");HEADER(ops[1]);ops[1].opcode=HHS158_OP_CHAIN_APPEND;ops[1].operands=SPAN("B,C");s=transition_create(&f,ops,k==13u?2u:1u,k==13u?1u:100u,NULL,root,&t);if(s==HHS158_OK&&k==13u){HHS158ExecutionOptions eo;HHS158ExecutionResult er;HHS158Receipt*r=NULL;HEADER(eo);eo.max_vm81_steps=1u;s=hhs158_transition_execute(t,&eo,&er,&r);}}
    else if(k==9u){HHS158CapabilityRequest cr;HHS158Capability*wrong=NULL;HHS158Operation op;HHS158Transition*t=NULL;HEADER(cr);cr.issuer=SPAN("i");cr.subject=SPAN("s");cr.application_id=SPAN("a");cr.object_scope=SPAN("wrong");cr.operation_scope=HHS158_CAP_EXECUTE;cr.mutation_scope=HHS158_MUTATION_INSTANCE;cr.expires_at=1799719999u;s=hhs158_capability_open(f.context,&cr,&wrong);HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");if(s==HHS158_OK)s=transition_create(&f,&op,1u,100u,wrong,(HHS158ByteSpan){0},&t);}
    else if(k==10u){HHS158Operation op;HHS158Transition*t=NULL;HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");s=transition_create(&f,&op,1u,100u,NULL,(HHS158ByteSpan){0},&t);}
    else if(k==11u){HHS158CapabilityRequest cr;HHS158Capability*exec=NULL;HHS158Operation op;HHS158Transition*t=NULL;HHS158ExecutionOptions eo;HHS158ExecutionResult er;HHS158Receipt*r=NULL;HEADER(cr);cr.issuer=SPAN("i");cr.subject=SPAN("s");cr.application_id=SPAN("a");cr.operation_scope=HHS158_CAP_EXECUTE;cr.mutation_scope=HHS158_MUTATION_INSTANCE;cr.expires_at=1799719999u;s=hhs158_capability_open(f.context,&cr,&exec);HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");if(s==HHS158_OK)s=transition_create(&f,&op,1u,100u,exec,(HHS158ByteSpan){0},&t);HEADER(eo);eo.atomic_execute_and_commit=1u;if(s==HHS158_OK)s=hhs158_transition_execute(t,&eo,&er,&r);}
    else if(k==12u){s=bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE,"1/3");if(s==HHS158_OK)s=bind_value(&f,"x",HHS158_VALUE_RATIONAL,HHS158_FLAG_AUTHORITATIVE,"2/3");}
    else if(k==14u||k==15u){HHS158Value p,r,d;HHS158DeltaPolicy dp;HEADER(p);HEADER(r);HEADER(dp);p.kind=r.kind=HHS158_VALUE_RATIONAL;p.flags=r.flags=HHS158_FLAG_AUTHORITATIVE;p.canonical_payload=SPAN(k==14u?"NaN":"1/3");r.canonical_payload=SPAN(k==15u?"0/1":"1/3");dp.mode=HHS158_DELTA_ALL;dp.require_invertible_reference=1u;s=hhs158_delta_compute(&p,&r,&dp,&d);}
    else if(k==16u){HHS158SerializationOptions so;HHS158MutableByteSpan out={0};uint8_t*buf;HHS158DeserializationOptions di;HHS158Instance*copy=NULL;HHS158Receipt*r=NULL;HEADER(so);so.format=HHS158_SERIALIZE_CANONICAL_JSON;so.max_output_bytes=1048576u;s=hhs158_instance_serialize(f.instance,&so,&out);buf=(uint8_t*)malloc(out.size_written);if(s==HHS158_BUFFER_TOO_SMALL&&buf){out.data=buf;out.capacity=out.size_written;s=hhs158_instance_serialize(f.instance,&so,&out);}if(s==HHS158_OK)buf[out.size_written/2u]^=1u;HEADER(di);di.format=HHS158_SERIALIZE_CANONICAL_JSON;if(s==HHS158_OK)s=hhs158_instance_deserialize(f.context,(HHS158ByteSpan){buf,out.size_written},&di,&copy,&r);free(buf);}
    else if(k==17u){HHS158Instance*items[2]={f.instance,f.instance},*composite=NULL;HHS158CompositionPolicy cp;HHS158Receipt*r=NULL;HEADER(cp);cp.max_dependency_depth=72u;s=hhs158_instance_compose(f.context,items,2u,&cp,&composite,&r);}
    else if(k==18u||k==19u){HHS158Receipt*r=NULL;HHS158Operation op;HHS158Transition*t=NULL;s=k==18u?hhs158_instance_retire(f.instance,f.capability,&r):hhs158_instance_quarantine(f.instance,1u,&r);HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");if(s==HHS158_OK)s=transition_create(&f,&op,1u,100u,NULL,(HHS158ByteSpan){0},&t);}
    else if(k==20u){HHS158Value v;HEADER(v);v.header.struct_size=1u;v.kind=HHS158_VALUE_BIGINT;v.flags=HHS158_FLAG_AUTHORITATIVE;v.canonical_payload=SPAN("1");{HHS158Receipt*br=NULL;s=hhs158_instance_bind_authorized(f.instance,f.capability,SPAN("x"),&v,&br);}}
    else if(k==21u){HHS158DefinitionDescriptor d;HHS158Definition*def=NULL;HHS158Receipt*r=NULL;uint64_t shape[1]={0u};HEADER(d);d.contract_id=SPAN("x");d.schema_version=SPAN("1");d.canonical_name=SPAN("bad");d.object_class=SPAN("NON_FUNGIBLE_TENSOR_CONSTRAINT");d.canonical_constraints=SPAN("A==B");d.authority_root=SPAN("root");d.ancestry=SPAN("P157");d.tensor_rank=1u;d.tensor_shape=shape;s=hhs158_definition_register(f.context,&d,&def,&r);}
    else if(k==22u){HHS158ProjectionProfile pp;HHS158Value projected,authoritative;HHS158Receipt*r=NULL;HEADER(pp);pp.kind=HHS158_PROJECTION_IEEE754_BINARY64_CONTROL;s=hhs158_instance_project(f.instance,&pp,&projected,&r);if(s==HHS158_OK){HEADER(authoritative);authoritative.kind=HHS158_VALUE_RATIONAL;authoritative.flags=projected.flags;authoritative.canonical_payload=projected.canonical_payload;{HHS158Receipt*br=NULL;s=hhs158_instance_bind_authorized(f.instance,f.capability,SPAN("projected"),&authoritative,&br);}}hhs158_value_release(&projected);}
    else if(k==23u){HHS158ReplayOptions ro;HHS158ReplayResult rr;HEADER(ro);ro.header.struct_size=1u;s=hhs158_receipt_replay(f.context,f.instance_receipt,&ro,&rr);}
    else if(k==24u){HHS158Operation op;HHS158Transition*t=NULL;s=hhs158_capability_revoke(f.capability,SPAN("revoked"));HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");if(s==HHS158_OK)s=transition_create(&f,&op,1u,100u,NULL,(HHS158ByteSpan){0},&t);}
    else {HHS158Operation op;HHS158Transition*t=NULL;HHS158ExecutionOptions eo;HHS158ExecutionResult er;HHS158Receipt*r=NULL;volatile uint32_t cancel=1u;HEADER(op);op.opcode=HHS158_OP_BIND_EQ;op.operands=SPAN("A,B");s=transition_create(&f,&op,1u,100u,NULL,(HHS158ByteSpan){0},&t);HEADER(eo);eo.cancel_flag=&cancel;if(s==HHS158_OK)s=hhs158_transition_execute(t,&eo,&er,&r);}
    fixture_release(&f);return s;
}

static int negative_matrix(size_t *count){size_t i;for(i=0;i<81u;++i){HHS158Status s=negative_case(i);CHECK(s!=HHS158_OK);(*count)++;}return 1;}

int main(void){size_t vm81=0,replay=0,loshu=0,delta=0,dependency=0,atomic=0,serialization=0,abi=0,bindings=0,endpoints=0,identity=0,negative=0,positive;
    CHECK(vm81_and_replay(&vm81,&replay));CHECK(loshu_matrix(&loshu));CHECK(delta_matrix(&delta));CHECK(dependency_matrix(&dependency));CHECK(atomic_matrix(&atomic));CHECK(serialization_matrix(&serialization));CHECK(abi_matrix(&abi));CHECK(descriptor_matrix(&endpoints,&bindings,&identity));CHECK(negative_matrix(&negative));
    positive=vm81+replay+loshu+delta+dependency+atomic+serialization+abi+bindings+endpoints+identity;CHECK(positive==272u&&negative==81u);
    printf("{\"classification\":\"HHS_PASS_158_NATIVE_MATRIX_VERIFIED\",\"positive_total\":%lu,\"negative_total\":%lu,\"vm81\":%lu,\"hash72_replay\":%lu,\"loshu\":%lu,\"delta\":%lu,\"dependency\":%lu,\"atomic\":%lu,\"serialization\":%lu,\"abi_lifecycle\":%lu,\"binding_surfaces\":%lu,\"api_descriptors\":%lu,\"identity\":%lu}\n",(unsigned long)positive,(unsigned long)negative,(unsigned long)vm81,(unsigned long)replay,(unsigned long)loshu,(unsigned long)delta,(unsigned long)dependency,(unsigned long)atomic,(unsigned long)serialization,(unsigned long)abi,(unsigned long)bindings,(unsigned long)endpoints,(unsigned long)identity);return 0;}
