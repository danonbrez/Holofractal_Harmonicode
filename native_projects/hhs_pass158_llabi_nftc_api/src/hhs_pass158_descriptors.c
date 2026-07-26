#include "hhs_pass158_internal.h"

#include <stdio.h>
#include <string.h>

static const HHS158OpcodeDescriptor OPCODES[] = {
    {HHS158_OP_NFT_DEF_BEGIN,"NFT_DEF_BEGIN","definition",0,HHS158_OPCODE_MUTATION_PROVISIONAL,HHS158_CAP_REGISTER,9,17,0},
    {HHS158_OP_NFT_DEF_FIELD,"NFT_DEF_FIELD","field,value",0,HHS158_OPCODE_MUTATION_PROVISIONAL,HHS158_CAP_REGISTER,9,17,0},
    {HHS158_OP_NFT_DEF_CLOSE,"NFT_DEF_CLOSE","definition",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_REGISTER,9,17,0},
    {HHS158_OP_NFT_INSTANCE_NEW,"NFT_INSTANCE_NEW","definition,nonce",1,HHS158_OPCODE_MUTATION_PROVISIONAL,HHS158_CAP_INSTANTIATE,9,17,0},
    {HHS158_OP_NFT_INSTANCE_BIND,"NFT_INSTANCE_BIND","symbol,value",0,HHS158_OPCODE_MUTATION_PROVISIONAL,HHS158_CAP_BIND,18,26,0},
    {HHS158_OP_NFT_INSTANCE_SEAL,"NFT_INSTANCE_SEAL","instance",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_VALIDATE,18,26,0},
    {HHS158_OP_NFT_INSTANCE_RETIRE,"NFT_INSTANCE_RETIRE","instance",0,HHS158_OPCODE_MUTATION_RETIRE,HHS158_CAP_COMMIT,72,77,0},
    {HHS158_OP_BIND_EQ,"BIND_EQ","lhs,rhs",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_BIND_NEQ,"BIND_NEQ","lhs,rhs",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_CHAIN_APPEND,"CHAIN_APPEND","lhs,rhs",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_CHAIN_CLOSE,"CHAIN_CLOSE","chain",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_DOMAIN_GUARD,"DOMAIN_GUARD","symbol,domain",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_PHASE_GUARD,"PHASE_GUARD","left,right",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_LIST_ORDERED,"LIST_ORDERED","items[]",1,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_TENSOR_PACK,"TENSOR_PACK","shape,items[]",1,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_CONSTRAINT_PACK,"CONSTRAINT_PACK","graph",1,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,27,35,0},
    {HHS158_OP_TRANSITION_BEGIN,"TRANSITION_BEGIN","instance",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,72,77,0},
    {HHS158_OP_TRANSITION_APPLY,"TRANSITION_APPLY","operation",0,HHS158_OPCODE_MUTATION_CANDIDATE,HHS158_CAP_EXECUTE,72,77,0},
    {HHS158_OP_TRANSITION_VALIDATE,"TRANSITION_VALIDATE","candidate",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_VALIDATE,72,77,0},
    {HHS158_OP_TRANSITION_HOLD,"TRANSITION_HOLD","reason",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_EXECUTE,72,77,0},
    {HHS158_OP_TRANSITION_COMMIT,"TRANSITION_COMMIT","candidate",0,HHS158_OPCODE_MUTATION_COMMIT,HHS158_CAP_COMMIT,72,80,0},
    {HHS158_OP_TRANSITION_ABORT,"TRANSITION_ABORT","reason",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_EXECUTE,72,80,0},
    {HHS158_OP_PROJECT_REFERENCE,"PROJECT_REFERENCE","instance",1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,45,53,0},
    {HHS158_OP_PROJECT_CONTROL,"PROJECT_CONTROL","profile",1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,54,62,0},
    {HHS158_OP_DELTA_RATIO,"DELTA_RATIO","projected,reference",-1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,63,71,0},
    {HHS158_OP_DELTA_ADD,"DELTA_ADD","projected,reference",-1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,63,71,0},
    {HHS158_OP_DELTA_REL,"DELTA_REL","ratio",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,63,71,0},
    {HHS158_OP_DELTA_PACK,"DELTA_PACK","ratio,add,rel",-2,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,63,71,0},
    {HHS158_OP_DELTA_NORMALIZE,"DELTA_NORMALIZE","projected,delta",-1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_PROJECT,63,71,0},
    {HHS158_OP_DELTA_VERIFY,"DELTA_VERIFY","normalized,reference",-1,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_VALIDATE,63,71,0},
    {HHS158_OP_HASH216_INDEX,"HASH216_INDEX","canonical",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_VALIDATE,78,78,0},
    {HHS158_OP_HASH72_WITNESS,"HASH72_WITNESS","execution",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_VALIDATE,79,79,0},
    {HHS158_OP_RECEIPT_PACK,"RECEIPT_PACK","receipt",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_SERIALIZE,79,80,0},
    {HHS158_OP_RECEIPT_VERIFY,"RECEIPT_VERIFY","receipt",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_REPLAY,79,80,0},
    {HHS158_OP_REPLAY_BEGIN,"REPLAY_BEGIN","receipt",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_REPLAY,78,80,0},
    {HHS158_OP_REPLAY_CLOSE,"REPLAY_CLOSE","state",0,HHS158_OPCODE_MUTATION_NONE,HHS158_CAP_REPLAY,80,80,0}
};

uint32_t hhs158_abi_version_major(void) { return HHS158_ABI_VERSION_MAJOR; }
uint32_t hhs158_abi_version_minor(void) { return HHS158_ABI_VERSION_MINOR; }
const char *hhs158_contract_id(void) { return HHS158_CONTRACT_ID; }
const char *hhs158_contract_version(void) { return HHS158_CONTRACT_VERSION; }

const HHS158OpcodeDescriptor *hhs158_public_opcode_registry(size_t *out_count) {
    if (out_count) *out_count = sizeof(OPCODES) / sizeof(OPCODES[0]);
    return OPCODES;
}

int hhs158_opcode_is_public(uint32_t opcode) {
    size_t count = sizeof(OPCODES) / sizeof(OPCODES[0]);
    size_t i;
    for (i = 0; i < count; ++i) if (OPCODES[i].opcode == opcode) return 1;
    return 0;
}

const char *hhs158_status_classification(HHS158Status status) {
    switch (status) {
        case HHS158_OK: return "OK";
        case HHS158_HELD: return "HELD";
        case HHS158_BUFFER_TOO_SMALL: return "BUFFER_TOO_SMALL";
        case HHS158_RESOURCE_BOUNDED: return "RESOURCE_BOUNDED";
        case HHS158_ABI_VERSION_UNSUPPORTED: return "ABI_VERSION_UNSUPPORTED";
        case HHS158_STRUCT_SIZE_INVALID: return "STRUCT_SIZE_INVALID";
        case HHS158_TYPE_MISMATCH: return "TYPE_MISMATCH";
        case HHS158_EXACT_VALUE_LOSS: return "EXACT_VALUE_LOSS";
        case HHS158_HANDLE_RELEASED: return "HANDLE_RELEASED";
        case HHS158_INVALID_UTF8: return "INVALID_UTF8";
        case HHS158_INTEGER_WIDTH_TRUNCATION: return "INTEGER_WIDTH_TRUNCATION";
        case HHS158_CAPABILITY_REQUIRED: return "CAPABILITY_REQUIRED";
        case HHS158_CAPABILITY_SCOPE_VIOLATION: return "CAPABILITY_SCOPE_VIOLATION";
        case HHS158_CAPABILITY_EXPIRED: return "CAPABILITY_EXPIRED";
        case HHS158_CAPABILITY_REVOKED: return "CAPABILITY_REVOKED";
        case HHS158_STATE_ROOT_CONFLICT: return "STATE_ROOT_CONFLICT";
        case HHS158_CONSTRAINT_CHAIN_COLLAPSED: return "CONSTRAINT_CHAIN_COLLAPSED";
        case HHS158_LIST_TOPOLOGY_LOSS: return "LIST_TOPOLOGY_LOSS";
        case HHS158_PHASE_IDENTITY_VIOLATION: return "PHASE_IDENTITY_VIOLATION";
        case HHS158_TENSOR_SHAPE_MISMATCH: return "TENSOR_SHAPE_MISMATCH";
        case HHS158_DEPENDENCY_CYCLE_UNBOUNDED: return "DEPENDENCY_CYCLE_UNBOUNDED";
        case HHS158_UNAUTHORIZED_MUTATION: return "UNAUTHORIZED_MUTATION";
        case HHS158_DUPLICATE_CONFLICTING_BINDING: return "DUPLICATE_CONFLICTING_BINDING";
        case HHS158_VM81_RESOURCE_BOUNDED: return "VM81_RESOURCE_BOUNDED";
        case HHS158_PRIVATE_OPCODE: return "PRIVATE_OPCODE";
        case HHS158_VM81_ADMISSION_REJECTED: return "VM81_ADMISSION_REJECTED";
        case HHS158_SERIALIZATION_INVALID: return "SERIALIZATION_INVALID";
        case HHS158_UNKNOWN_AUTHORITY_FIELD: return "UNKNOWN_AUTHORITY_FIELD";
        case HHS158_IDENTITY_MISMATCH: return "IDENTITY_MISMATCH";
        case HHS158_PROJECTION_CONTROL_COLLAPSE: return "PROJECTION_CONTROL_COLLAPSE";
        case HHS158_DELTA_REFERENCE_NONINVERTIBLE: return "DELTA_REFERENCE_NONINVERTIBLE";
        case HHS158_NONFINITE_PROJECTION: return "NONFINITE_PROJECTION";
        case HHS158_DELTA_VERIFY_FAILED: return "DELTA_VERIFY_FAILED";
        case HHS158_HASH72_RECEIPT_MISMATCH: return "HASH72_RECEIPT_MISMATCH";
        case HHS158_HASH216_IDENTITY_MISMATCH: return "HASH216_IDENTITY_MISMATCH";
        case HHS158_REPLAY_MISMATCH: return "REPLAY_MISMATCH";
        case HHS158_RECEIPT_TRUNCATED: return "RECEIPT_TRUNCATED";
        case HHS158_MEMORY_BOUND: return "MEMORY_BOUND";
        case HHS158_RECURSION_BOUND: return "RECURSION_BOUND";
        case HHS158_OUTPUT_BOUND: return "OUTPUT_BOUND";
        case HHS158_CANCELLED: return "CANCELLED";
        default: return status < 0 ? "REJECTED" : "NONTERMINAL";
    }
}

HHS158Status hhs158_abi_descriptor_json(HHS158MutableByteSpan *output) {
    static const char JSON[] =
        "{\"contract_id\":\"HHS-P158-LLABI-NFTC-API\",\"abi\":\"1.0\","
        "\"opaque_handles\":7,\"struct_header\":{\"size\":true,\"version\":true},"
        "\"numeric_authority\":\"EXACT_SYMBOLIC\",\"state_machine\":\"VM81\","
        "\"object_identity\":\"Hash216\",\"execution_witness\":\"Hash72\"}";
    return hhs158_write_bytes((const uint8_t *)JSON, strlen(JSON), output);
}

HHS158Status hhs158_capabilities_json(HHS158MutableByteSpan *output) {
    static const char JSON[] =
        "{\"abi_version\":\"1.0\",\"object_classes\":[\"NON_FUNGIBLE_TENSOR_CONSTRAINT\"],"
        "\"projection_profiles\":[\"EXACT_REFERENCE\",\"IEEE754_BINARY64_CONTROL\",\"RENDER_FLOAT32\"],"
        "\"vm81_cells\":81,\"opcode_page\":\"0x5800-0x5845\","
        "\"receipt_formats\":[\"HHS_CANONICAL_JSON\",\"HHS_CANONICAL_JSONL\"],"
        "\"bindings\":[\"C\",\"C++\",\"Rust\",\"Python\",\"Java/Kotlin JNI\",\"JavaScript/WASM\"]}";
    return hhs158_write_bytes((const uint8_t *)JSON, strlen(JSON), output);
}

HHS158Status hhs158_opcode_descriptor_json(HHS158MutableByteSpan *output) {
    char json[16384];
    size_t length = 0;
    size_t i;
    int written;
    written = snprintf(json, sizeof(json), "{\"vm81_profile\":\"PASS158_PUBLIC_APPLICATION\",\"opcodes\":[");
    if (written < 0 || (size_t)written >= sizeof(json)) return HHS158_OUTPUT_BOUND;
    length = (size_t)written;
    for (i = 0; i < sizeof(OPCODES) / sizeof(OPCODES[0]); ++i) {
        written = snprintf(json + length, sizeof(json) - length,
            "%s{\"opcode\":%u,\"mnemonic\":\"%s\",\"operands\":\"%s\",\"stack_delta\":%d,\"mutation_class\":%u,\"required_capability\":%llu,\"vm81\":[%u,%u]}",
            i ? "," : "", OPCODES[i].opcode, OPCODES[i].mnemonic, OPCODES[i].operand_types,
            OPCODES[i].stack_delta, OPCODES[i].mutation_class,
            (unsigned long long)OPCODES[i].required_capability,
            (unsigned)OPCODES[i].vm81_cell_start, (unsigned)OPCODES[i].vm81_cell_end);
        if (written < 0 || (size_t)written >= sizeof(json) - length) return HHS158_OUTPUT_BOUND;
        length += (size_t)written;
    }
    if (length + 3u > sizeof(json)) return HHS158_OUTPUT_BOUND;
    json[length++] = ']'; json[length++] = '}'; json[length] = '\0';
    return hhs158_write_bytes((const uint8_t *)json, length, output);
}
