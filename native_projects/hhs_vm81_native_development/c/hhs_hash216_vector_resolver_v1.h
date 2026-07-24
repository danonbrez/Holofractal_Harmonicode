#ifndef HHS_HASH216_VECTOR_RESOLVER_V1_H
#define HHS_HASH216_VECTOR_RESOLVER_V1_H

#include <stddef.h>
#include <stdint.h>

#include "hhs_hash216.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION 1U
#define HHS_HASH216_VECTOR_MAX_OBJECTS 8U
#define HHS_HASH216_VECTOR_MAX_BYTES 4096U
#define HHS_HASH216_POSITION_MAX 215U
#define HHS_VM81_LANE_MAX 80U
#define HHS_HASH72_PHASE_MAX 71U

typedef enum HHSHash216VectorStatus {
    HHS_HASH216_VECTOR_STATUS_OK = 0,
    HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT = 1,
    HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH = 2,
    HHS_HASH216_VECTOR_STATUS_INVALID_DOMAIN = 3,
    HHS_HASH216_VECTOR_STATUS_INVALID_ROLE = 4,
    HHS_HASH216_VECTOR_STATUS_POSITION_OUT_OF_RANGE = 5,
    HHS_HASH216_VECTOR_STATUS_LANE_OUT_OF_RANGE = 6,
    HHS_HASH216_VECTOR_STATUS_PHASE_OUT_OF_RANGE = 7,
    HHS_HASH216_VECTOR_STATUS_VERSION_INVALID = 8,
    HHS_HASH216_VECTOR_STATUS_GENERATION_INVALID = 9,
    HHS_HASH216_VECTOR_STATUS_SIZE_OVERFLOW = 10,
    HHS_HASH216_VECTOR_STATUS_CAPACITY_VIOLATION = 11,
    HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID = 12,
    HHS_HASH216_VECTOR_STATUS_DUPLICATE_ADDRESS = 13,
    HHS_HASH216_VECTOR_STATUS_RESOLVER_UNSEALED = 14,
    HHS_HASH216_VECTOR_STATUS_NONCANONICAL_ADDRESS = 15,
    HHS_HASH216_VECTOR_STATUS_NOT_FOUND = 16,
    HHS_HASH216_VECTOR_STATUS_STALE_VERSION = 17,
    HHS_HASH216_VECTOR_STATUS_STALE_GENERATION = 18,
    HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH = 19,
    HHS_HASH216_VECTOR_STATUS_READ_OUT_OF_BOUNDS = 20,
    HHS_HASH216_VECTOR_STATUS_OUTPUT_TOO_SMALL = 21,
    HHS_HASH216_VECTOR_STATUS_MUTATION_NOT_SUPPORTED = 22,
    HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE = 23
} HHSHash216VectorStatus;

typedef enum HHSHash216Domain {
    HHS_HASH216_DOMAIN_PROGRAM = 1,
    HHS_HASH216_DOMAIN_TILE = 2,
    HHS_HASH216_DOMAIN_MAP = 3,
    HHS_HASH216_DOMAIN_SPRITE = 4,
    HHS_HASH216_DOMAIN_ENTITY = 5,
    HHS_HASH216_DOMAIN_PHYSICS = 6,
    HHS_HASH216_DOMAIN_INPUT = 7,
    HHS_HASH216_DOMAIN_FRAME = 8,
    HHS_HASH216_DOMAIN_HISTORY = 9,
    HHS_HASH216_DOMAIN_RECEIPT = 10,
    HHS_HASH216_DOMAIN_METADATA = 11
} HHSHash216Domain;

typedef enum HHSHash216VectorRole {
    HHS_HASH216_VECTOR_ROLE_PRIMARY = 1,
    HHS_HASH216_VECTOR_ROLE_GRAPHICS = 2,
    HHS_HASH216_VECTOR_ROLE_COLLISION = 3,
    HHS_HASH216_VECTOR_ROLE_METADATA = 4,
    HHS_HASH216_VECTOR_ROLE_FRAMEBUFFER = 5,
    HHS_HASH216_VECTOR_ROLE_PALETTE = 6,
    HHS_HASH216_VECTOR_ROLE_INPUT_SEQUENCE = 7,
    HHS_HASH216_VECTOR_ROLE_RECEIPT_CHAIN = 8
} HHSHash216VectorRole;

typedef enum HHSHash216ElementFormat {
    HHS_HASH216_ELEMENT_U8 = 1,
    HHS_HASH216_ELEMENT_I8 = 2,
    HHS_HASH216_ELEMENT_U16_BE = 3,
    HHS_HASH216_ELEMENT_I16_BE = 4,
    HHS_HASH216_ELEMENT_U32_BE = 5,
    HHS_HASH216_ELEMENT_I32_BE = 6,
    HHS_HASH216_ELEMENT_U64_BE = 7,
    HHS_HASH216_ELEMENT_I64_BE = 8,
    HHS_HASH216_ELEMENT_OPAQUE_BYTES = 9
} HHSHash216ElementFormat;

typedef struct HHSHash216AddressFields {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t domain;
    uint32_t role;
    uint32_t position;
    uint32_t lane;
    int64_t phase;
    uint64_t version;
    uint64_t generation;
    HHSHash216 content_commitment;
} HHSHash216AddressFields;

typedef struct HHSHash216Address {
    uint32_t struct_size;
    uint32_t abi_version;
    HHSHash216AddressFields fields;
    HHSHash216 logical_address;
} HHSHash216Address;

typedef struct HHSHash216VectorSeed {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t domain;
    uint32_t role;
    uint32_t position;
    uint32_t lane;
    int64_t phase;
    uint64_t version;
    uint64_t generation;
    uint64_t element_count;
    uint64_t byte_length;
    uint64_t capacity_bytes;
    uint32_t element_size;
    uint32_t element_format;
    const void* data;
} HHSHash216VectorSeed;

typedef struct HHSHash216VectorDescriptor {
    uint32_t struct_size;
    uint32_t abi_version;
    HHSHash216Address address;
    uint64_t element_count;
    uint64_t byte_length;
    uint64_t capacity_bytes;
    uint32_t element_size;
    uint32_t element_format;
    uint32_t immutable;
    uint32_t reserved0;
    HHSHash216 descriptor_commitment;
} HHSHash216VectorDescriptor;

typedef struct HHSHash216VectorSlot {
    uint32_t occupied;
    uint32_t reserved0;
    HHSHash216VectorDescriptor descriptor;
    uint8_t bytes[HHS_HASH216_VECTOR_MAX_BYTES];
} HHSHash216VectorSlot;

typedef struct HHSHash216VectorResolver {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t sealed;
    uint32_t entry_count;
    HHSHash216 resolver_root;
    HHSHash216VectorSlot slots[HHS_HASH216_VECTOR_MAX_OBJECTS];
} HHSHash216VectorResolver;

typedef struct HHSHash216VectorReadResult {
    uint32_t struct_size;
    uint32_t abi_version;
    uint32_t status;
    uint32_t reserved0;
    uint64_t requested_offset;
    uint64_t requested_length;
    uint64_t bytes_written;
    HHSHash216 resolver_root;
    HHSHash216VectorDescriptor descriptor;
} HHSHash216VectorReadResult;

HHSHash216VectorStatus hhs_hash216_address_build(
    const HHSHash216AddressFields* fields,
    HHSHash216Address* out_address
);

HHSHash216VectorStatus hhs_hash216_address_validate(
    const HHSHash216Address* address
);

HHSHash216VectorStatus hhs_hash216_vector_resolver_initialize(
    HHSHash216VectorResolver* resolver,
    const HHSHash216VectorSeed* seeds,
    size_t seed_count
);

HHSHash216VectorStatus hhs_hash216_vector_resolve(
    const HHSHash216VectorResolver* resolver,
    const HHSHash216Address* address,
    HHSHash216VectorDescriptor* out_descriptor
);

HHSHash216VectorStatus hhs_hash216_vector_read(
    const HHSHash216VectorResolver* resolver,
    const HHSHash216Address* address,
    uint64_t offset,
    uint64_t length,
    void* out_bytes,
    uint64_t out_capacity,
    HHSHash216VectorReadResult* out_result
);

#ifdef __cplusplus
}
#endif

#endif
