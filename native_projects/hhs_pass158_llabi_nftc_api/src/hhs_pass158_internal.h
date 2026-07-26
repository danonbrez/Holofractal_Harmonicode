#ifndef HHS_PASS158_INTERNAL_H
#define HHS_PASS158_INTERNAL_H

#include "hhs_pass158_api.h"
#include "hhs_runtime_abi.h"

#include <stddef.h>
#include <stdint.h>

#define HHS158_CONTEXT_MAGIC    UINT64_C(0x4858533135384354)
#define HHS158_DEFINITION_MAGIC UINT64_C(0x4858533135384446)
#define HHS158_INSTANCE_MAGIC   UINT64_C(0x485853313538494E)
#define HHS158_TRANSITION_MAGIC UINT64_C(0x4858533135385452)
#define HHS158_RECEIPT_MAGIC    UINT64_C(0x4858533135385243)
#define HHS158_CAPABILITY_MAGIC UINT64_C(0x4858533135384341)

#define HHS158_MAX_CONTEXT_OBJECTS 128u
#define HHS158_MAX_BINDINGS 64u
#define HHS158_MAX_OPERATIONS 64u
#define HHS158_MAX_CANONICAL_BYTES 16384u
#define HHS158_MAX_OPERAND_BYTES 1024u
#define HHS158_MAX_SYMBOL_BYTES 128u
#define HHS158_INTERNAL_OWNED_VALUE (1u << 31)

typedef struct {
    char value[HHS158_HASH216_LENGTH + 1u];
} HHS158NativeHash216;

void hhs_hash216_compute(const void *data, size_t size, HHS158NativeHash216 *out_hash);

typedef struct {
    char symbol[HHS158_MAX_SYMBOL_BYTES];
    uint32_t kind;
    uint32_t flags;
    size_t payload_size;
    uint8_t payload[HHS158_MAX_OPERAND_BYTES];
} HHS158BindingRecord;

typedef struct {
    uint32_t opcode;
    uint32_t flags;
    size_t operand_size;
    uint8_t operands[HHS158_MAX_OPERAND_BYTES];
} HHS158StoredOperation;

struct HHS158Context {
    uint64_t magic;
    uint32_t released;
    HHS158ContextConfig config;
    HHSRuntimeState runtime_template;
    HHS158Definition *definitions[HHS158_MAX_CONTEXT_OBJECTS];
    HHS158Instance *instances[HHS158_MAX_CONTEXT_OBJECTS];
    HHS158Receipt *receipts[HHS158_MAX_CONTEXT_OBJECTS];
    HHS158Capability *capabilities[HHS158_MAX_CONTEXT_OBJECTS];
    HHS158Transition *transitions[HHS158_MAX_CONTEXT_OBJECTS];
    size_t definition_count;
    size_t instance_count;
    size_t receipt_count;
    size_t capability_count;
    size_t transition_count;
};

struct HHS158Definition {
    uint64_t magic;
    uint32_t released;
    HHS158Context *context;
    char definition_id[HHS158_HASH216_LENGTH + 1u];
    char canonical_hash[HHS158_HASH216_LENGTH + 1u];
    char origin_receipt[HHS158_HASH72_LENGTH + 1u];
    char canonical_name[256];
    char object_class[128];
    char canonical[HHS158_MAX_CANONICAL_BYTES];
    size_t canonical_size;
    uint32_t tensor_rank;
    uint64_t tensor_shape[HHS158_MAX_TENSOR_RANK];
    uint32_t lifecycle;
};

struct HHS158Capability {
    uint64_t magic;
    uint32_t released;
    uint32_t revoked;
    HHS158Context *context;
    char capability_id[HHS158_HASH216_LENGTH + 1u];
    char application_id[256];
    char object_scope[HHS158_HASH216_LENGTH + 2u];
    uint64_t operation_scope;
    uint64_t mutation_scope;
    uint64_t max_vm81_steps;
    uint64_t issued_at;
    uint64_t expires_at;
    char revocation_root[HHS158_HASH216_LENGTH + 1u];
};

struct HHS158Instance {
    uint64_t magic;
    uint32_t released;
    HHS158Context *context;
    HHS158Definition *definition;
    char instance_id[HHS158_HASH216_LENGTH + 1u];
    char current_state_root[HHS158_HASH216_LENGTH + 1u];
    char origin_receipt[HHS158_HASH72_LENGTH + 1u];
    uint8_t nonce[256];
    size_t nonce_size;
    uint64_t max_vm81_steps;
    uint64_t max_recursion_depth;
    uint64_t max_state_bytes;
    uint64_t max_receipt_bytes;
    uint32_t projection_profile_mask;
    uint32_t lifecycle;
    uint64_t version;
    HHS158BindingRecord bindings[HHS158_MAX_BINDINGS];
    size_t binding_count;
    char last_transition_receipt[HHS158_HASH72_LENGTH + 1u];
};

struct HHS158Transition {
    uint64_t magic;
    uint32_t released;
    uint32_t executed;
    uint32_t committed;
    uint32_t aborted;
    HHS158Context *context;
    HHS158Instance *instance;
    HHS158Capability *capability;
    char transition_id[HHS158_HASH216_LENGTH + 1u];
    char pre_state_root[HHS158_HASH216_LENGTH + 1u];
    char candidate_state_root[HHS158_HASH216_LENGTH + 1u];
    char opcode_trace_root[HHS158_HASH216_LENGTH + 1u];
    char replay_material[HHS158_MAX_CANONICAL_BYTES];
    size_t replay_material_size;
    HHS158StoredOperation operations[HHS158_MAX_OPERATIONS];
    size_t operation_count;
    uint64_t max_vm81_steps;
    uint64_t max_recursion_depth;
    uint64_t max_output_bytes;
    uint64_t audit_vm81_steps;
    uint64_t audit_witness_flags;
    uint32_t commit_policy;
    uint32_t flags;
};

struct HHS158Receipt {
    uint64_t magic;
    uint32_t released;
    HHS158Context *context;
    HHS158Status status;
    char receipt_id[HHS158_HASH72_LENGTH + 1u];
    char transition_id[HHS158_HASH216_LENGTH + 1u];
    char definition_id[HHS158_HASH216_LENGTH + 1u];
    char instance_id[HHS158_HASH216_LENGTH + 1u];
    char pre_state_root[HHS158_HASH216_LENGTH + 1u];
    char post_state_root[HHS158_HASH216_LENGTH + 1u];
    char opcode_trace_root[HHS158_HASH216_LENGTH + 1u];
    char object_root[HHS158_HASH216_LENGTH + 1u];
    char classification[HHS158_MAX_CLASSIFICATION];
    char replay_material[HHS158_MAX_CANONICAL_BYTES];
    size_t replay_material_size;
    uint64_t vm81_steps;
    uint64_t witness_flags;
    uint32_t lifecycle_state;
    uint32_t committed;
};

int hhs158_header_valid(const HHS158StructHeader *header, size_t minimum_size);
int hhs158_utf8_valid(HHS158ByteSpan span);
int hhs158_span_equal_text(HHS158ByteSpan span, const char *text);
int hhs158_span_contains(HHS158ByteSpan span, const char *needle);
HHS158Status hhs158_write_bytes(const uint8_t *data, size_t size, HHS158MutableByteSpan *output);
HHS158Status hhs158_value_set(HHS158Value *value, uint32_t kind, uint32_t flags, const uint8_t *data, size_t size);
void hhs158_hash216_bytes(const void *data, size_t size, char output[HHS158_HASH216_LENGTH + 1u]);
void hhs158_hash72_bytes(const void *data, size_t size, char output[HHS158_HASH72_LENGTH + 1u]);
size_t hhs158_hex_encode(const uint8_t *data, size_t size, char *output, size_t capacity);
HHS158Status hhs158_hex_decode(const char *text, uint8_t *output, size_t capacity, size_t *out_size);
HHS158Status hhs158_append_text(char *buffer, size_t capacity, size_t *length, const char *text);
HHS158Status hhs158_append_span_hex(char *buffer, size_t capacity, size_t *length, const char *tag, HHS158ByteSpan span);
HHS158Status hhs158_make_receipt(
    HHS158Context *context,
    HHS158Status status,
    const char *classification,
    const HHS158Definition *definition,
    const HHS158Instance *instance,
    const char *transition_id,
    const char *pre_root,
    const char *post_root,
    const char *trace_root,
    const char *replay_material,
    size_t replay_material_size,
    uint64_t vm81_steps,
    uint64_t witness_flags,
    uint32_t lifecycle_state,
    uint32_t committed,
    HHS158Receipt **out_receipt
);
HHS158Status hhs158_capability_check(
    const HHS158Capability *capability,
    const HHS158Instance *instance,
    uint64_t operation,
    uint64_t mutation
);
void hhs158_fill_validation_report(
    HHS158ValidationReport *report,
    HHS158Status status,
    uint32_t lifecycle,
    uint64_t checked,
    const char *classification,
    const char *state_root
);

#endif
