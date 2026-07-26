#ifndef HHS_PASS158_TYPES_H
#define HHS_PASS158_TYPES_H

#include <stddef.h>
#include <stdint.h>
#include "hhs_pass158_status.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS158_ABI_VERSION_MAJOR 1u
#define HHS158_ABI_VERSION_MINOR 0u
#define HHS158_STRUCT_VERSION_1  1u
#define HHS158_HASH72_LENGTH      72u
#define HHS158_HASH216_LENGTH     216u
#define HHS158_MAX_TENSOR_RANK    16u
#define HHS158_MAX_CLASSIFICATION 96u

#define HHS158_FLAG_AUTHORITATIVE      (1u << 0)
#define HHS158_FLAG_PROJECTION         (1u << 1)
#define HHS158_FLAG_ORDERED            (1u << 2)
#define HHS158_FLAG_IMMUTABLE          (1u << 3)
#define HHS158_FLAG_APPROXIMATE        (1u << 4)

#define HHS158_TRANSITION_EXECUTE_AND_COMMIT (1u << 0)
#define HHS158_TRANSITION_VALIDATION_ONLY    (1u << 1)
#define HHS158_TRANSITION_ALLOW_HOLD         (1u << 2)

#define HHS158_CAP_VALIDATE    (1ull << 0)
#define HHS158_CAP_EXECUTE     (1ull << 1)
#define HHS158_CAP_COMMIT      (1ull << 2)
#define HHS158_CAP_PROJECT     (1ull << 3)
#define HHS158_CAP_SERIALIZE   (1ull << 4)
#define HHS158_CAP_COMPOSE     (1ull << 5)
#define HHS158_CAP_REGISTER    (1ull << 6)
#define HHS158_CAP_INSTANTIATE (1ull << 7)
#define HHS158_CAP_BIND        (1ull << 8)
#define HHS158_CAP_REPLAY      (1ull << 9)

#define HHS158_MUTATION_NONE      0ull
#define HHS158_MUTATION_INSTANCE  (1ull << 0)
#define HHS158_MUTATION_COMPOSITE (1ull << 1)

#define HHS158_SCOPE_WILDCARD "*"

typedef struct HHS158Context HHS158Context;
typedef struct HHS158Definition HHS158Definition;
typedef struct HHS158Instance HHS158Instance;
typedef struct HHS158Transition HHS158Transition;
typedef struct HHS158Receipt HHS158Receipt;
typedef struct HHS158Capability HHS158Capability;
typedef struct HHS158Buffer HHS158Buffer;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
} HHS158StructHeader;

typedef struct {
    const uint8_t *data;
    size_t size;
} HHS158ByteSpan;

typedef struct {
    uint8_t *data;
    size_t capacity;
    size_t size_written;
} HHS158MutableByteSpan;

typedef struct {
    HHS158StructHeader header;
    uint8_t sign;
    uint8_t byte_order;
    uint16_t reserved;
    HHS158ByteSpan magnitude;
} HHS158BigInt;

typedef struct {
    HHS158StructHeader header;
    HHS158BigInt numerator;
    HHS158BigInt denominator;
} HHS158Rational;

typedef enum {
    HHS158_VALUE_NULL = 0,
    HHS158_VALUE_BOOL = 1,
    HHS158_VALUE_TRINARY = 2,
    HHS158_VALUE_BIGINT = 3,
    HHS158_VALUE_RATIONAL = 4,
    HHS158_VALUE_SYMBOL = 5,
    HHS158_VALUE_RADICAL = 6,
    HHS158_VALUE_LIST = 7,
    HHS158_VALUE_TENSOR = 8,
    HHS158_VALUE_EXPRESSION = 9,
    HHS158_VALUE_STATE_ROOT = 10,
    HHS158_VALUE_DELTA_VECTOR = 11
} HHS158ValueKind;

typedef struct {
    HHS158StructHeader header;
    uint32_t kind;
    uint32_t flags;
    HHS158ByteSpan canonical_payload;
} HHS158Value;

typedef enum {
    HHS158_LIFECYCLE_DECLARED = 0,
    HHS158_LIFECYCLE_CANONICALIZED = 1,
    HHS158_LIFECYCLE_REGISTERED = 2,
    HHS158_LIFECYCLE_INSTANTIATED = 3,
    HHS158_LIFECYCLE_BOUND = 4,
    HHS158_LIFECYCLE_VALIDATED = 5,
    HHS158_LIFECYCLE_AUTHORIZED = 6,
    HHS158_LIFECYCLE_EXECUTING = 7,
    HHS158_LIFECYCLE_HELD = 8,
    HHS158_LIFECYCLE_COMMITTED = 9,
    HHS158_LIFECYCLE_REJECTED = 10,
    HHS158_LIFECYCLE_REPLAYED = 11,
    HHS158_LIFECYCLE_RETIRED = 12,
    HHS158_LIFECYCLE_QUARANTINED = 13
} HHS158LifecycleState;

typedef enum {
    HHS158_SERIALIZE_CANONICAL_BINARY = 1,
    HHS158_SERIALIZE_CANONICAL_JSON = 2,
    HHS158_SERIALIZE_CANONICAL_JSONL = 3,
    HHS158_SERIALIZE_BIGINT_ENVELOPE = 4,
    HHS158_SERIALIZE_TRANSITION_PACKAGE = 5
} HHS158SerializationFormat;

typedef enum {
    HHS158_PROJECTION_EXACT_REFERENCE = 1,
    HHS158_PROJECTION_IEEE754_BINARY64_CONTROL = 2,
    HHS158_PROJECTION_RENDER_FLOAT32 = 3,
    HHS158_PROJECTION_CUSTOM_DECLARED = 4
} HHS158ProjectionKind;

typedef enum {
    HHS158_DELTA_RATIO = 1,
    HHS158_DELTA_ADD = 2,
    HHS158_DELTA_REL = 3,
    HHS158_DELTA_ALL = 4
} HHS158DeltaMode;

typedef struct {
    HHS158StructHeader header;
    uint32_t abi_major;
    uint32_t abi_minor;
    uint32_t max_definitions;
    uint32_t max_instances;
    uint32_t max_receipts;
    uint64_t max_memory_bytes;
    uint64_t deterministic_epoch_seconds;
    uint32_t flags;
    uint32_t reserved;
} HHS158ContextConfig;

typedef struct {
    HHS158StructHeader header;
    HHS158ByteSpan issuer;
    HHS158ByteSpan subject;
    HHS158ByteSpan application_id;
    HHS158ByteSpan object_scope;
    uint64_t operation_scope;
    uint64_t mutation_scope;
    uint64_t max_vm81_steps;
    uint64_t issued_at;
    uint64_t expires_at;
    HHS158ByteSpan revocation_root;
    uint32_t delegation_policy;
    uint32_t flags;
} HHS158CapabilityRequest;

typedef struct {
    HHS158StructHeader header;
    HHS158ByteSpan contract_id;
    HHS158ByteSpan schema_version;
    HHS158ByteSpan canonical_name;
    HHS158ByteSpan object_class;
    HHS158ByteSpan canonical_constraints;
    HHS158ByteSpan symbol_table;
    HHS158ByteSpan numeric_policy;
    HHS158ByteSpan operator_policy;
    HHS158ByteSpan authority_root;
    HHS158ByteSpan ancestry;
    uint32_t tensor_rank;
    const uint64_t *tensor_shape;
    uint32_t flags;
    uint32_t reserved;
} HHS158DefinitionDescriptor;

typedef struct {
    HHS158StructHeader header;
    HHS158ByteSpan instance_nonce;
    HHS158ByteSpan owner_capability_domain;
    uint64_t max_vm81_steps;
    uint64_t max_recursion_depth;
    uint64_t max_state_bytes;
    uint64_t max_receipt_bytes;
    uint32_t projection_profile_mask;
    uint32_t flags;
} HHS158InstanceConfig;

typedef struct {
    HHS158StructHeader header;
    uint32_t mode;
    uint32_t flags;
    uint64_t max_vm81_steps;
    uint64_t max_recursion_depth;
    uint64_t max_dependency_depth;
    uint64_t max_tensor_elements;
} HHS158ValidationPolicy;

typedef struct {
    HHS158StructHeader header;
    HHS158Status status;
    uint32_t lifecycle_state;
    uint64_t checked_constraints;
    uint64_t warnings;
    char classification[HHS158_MAX_CLASSIFICATION];
    char state_root[HHS158_HASH216_LENGTH + 1u];
} HHS158ValidationReport;

typedef struct {
    HHS158StructHeader header;
    const HHS158Value *values;
    size_t value_count;
    HHS158ByteSpan parser_profile;
    HHS158ByteSpan source_text;
    uint32_t flags;
    uint32_t reserved;
} HHS158ExecutionInputs;

typedef struct {
    HHS158StructHeader header;
    uint32_t opcode;
    uint32_t flags;
    HHS158ByteSpan operands;
} HHS158Operation;

typedef struct {
    HHS158StructHeader header;
    const HHS158Operation *operations;
    size_t operation_count;
    HHS158ByteSpan expected_pre_state_root;
    HHS158ByteSpan dependency_roots;
    uint64_t max_vm81_steps;
    uint64_t max_recursion_depth;
    uint64_t max_output_bytes;
    uint32_t projection_policy;
    uint32_t delta_policy;
    uint32_t commit_policy;
    uint32_t flags;
} HHS158TransitionDescriptor;

typedef struct {
    HHS158StructHeader header;
    uint64_t max_vm81_steps;
    uint64_t max_wall_time_ms;
    uint64_t max_cpu_time_ms;
    uint64_t max_memory_bytes;
    uint32_t atomic_execute_and_commit;
    uint32_t allow_hold;
    const volatile uint32_t *cancel_flag;
} HHS158ExecutionOptions;

typedef struct {
    HHS158StructHeader header;
    HHS158Status status;
    uint32_t lifecycle_state;
    uint64_t vm81_steps;
    uint64_t witness_flags;
    char classification[HHS158_MAX_CLASSIFICATION];
    char pre_state_root[HHS158_HASH216_LENGTH + 1u];
    char post_state_root[HHS158_HASH216_LENGTH + 1u];
    char opcode_trace_root[HHS158_HASH216_LENGTH + 1u];
} HHS158ExecutionResult;

typedef struct {
    HHS158StructHeader header;
    uint32_t kind;
    uint32_t flags;
    HHS158ByteSpan profile_name;
    uint32_t decimal_digits;
    uint32_t reserved;
} HHS158ProjectionProfile;

typedef struct {
    HHS158StructHeader header;
    uint32_t mode;
    uint32_t require_invertible_reference;
    uint32_t preserve_all_components;
    uint32_t flags;
} HHS158DeltaPolicy;

typedef struct {
    HHS158StructHeader header;
    uint32_t format;
    uint32_t preserve_unknown_fields;
    uint64_t max_output_bytes;
    uint32_t flags;
    uint32_t reserved;
} HHS158SerializationOptions;

typedef struct {
    HHS158StructHeader header;
    uint32_t format;
    uint32_t preserve_unknown_fields;
    uint32_t reject_authority_unknown_fields;
    uint32_t flags;
} HHS158DeserializationOptions;

typedef struct {
    HHS158StructHeader header;
    uint32_t allow_declared_cycles;
    uint32_t isolation_level;
    uint64_t max_dependency_depth;
    HHS158ByteSpan namespace_prefix;
    uint32_t flags;
    uint32_t reserved;
} HHS158CompositionPolicy;

typedef struct {
    HHS158StructHeader header;
    uint32_t verify_hash72;
    uint32_t verify_hash216;
    uint32_t verify_semantic_root;
    uint32_t flags;
} HHS158ReplayOptions;

typedef struct {
    HHS158StructHeader header;
    HHS158Status status;
    uint32_t matched;
    uint32_t lifecycle_state;
    char classification[HHS158_MAX_CLASSIFICATION];
    char reconstructed_state_root[HHS158_HASH216_LENGTH + 1u];
} HHS158ReplayResult;

#ifdef __cplusplus
}
#endif

#endif
