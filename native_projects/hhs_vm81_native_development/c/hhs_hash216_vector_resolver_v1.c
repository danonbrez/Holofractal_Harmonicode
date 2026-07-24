#include "hhs_hash216_vector_resolver_v1.h"

#include <limits.h>
#include <string.h>

static void hhs_put_u32_be(uint8_t* out, uint32_t value) {
    out[0] = (uint8_t)(value >> 24);
    out[1] = (uint8_t)(value >> 16);
    out[2] = (uint8_t)(value >> 8);
    out[3] = (uint8_t)value;
}

static void hhs_put_u64_be(uint8_t* out, uint64_t value) {
    out[0] = (uint8_t)(value >> 56);
    out[1] = (uint8_t)(value >> 48);
    out[2] = (uint8_t)(value >> 40);
    out[3] = (uint8_t)(value >> 32);
    out[4] = (uint8_t)(value >> 24);
    out[5] = (uint8_t)(value >> 16);
    out[6] = (uint8_t)(value >> 8);
    out[7] = (uint8_t)value;
}

static int hhs_hash216_is_canonical(const HHSHash216* value) {
    size_t i;
    if (!value || value->value[HHS_HASH216_LEN] != '\0') {
        return 0;
    }
    for (i = 0; i < HHS_HASH216_LEN; ++i) {
        if (!strchr(HHS_HASH72_ALPHABET, value->value[i])) {
            return 0;
        }
    }
    return 1;
}

static int hhs_domain_valid(uint32_t domain) {
    return domain >= HHS_HASH216_DOMAIN_PROGRAM &&
           domain <= HHS_HASH216_DOMAIN_METADATA;
}

static int hhs_role_valid(uint32_t role) {
    return role >= HHS_HASH216_VECTOR_ROLE_PRIMARY &&
           role <= HHS_HASH216_VECTOR_ROLE_RECEIPT_CHAIN;
}

static int hhs_element_format_valid(uint32_t format) {
    return format >= HHS_HASH216_ELEMENT_U8 &&
           format <= HHS_HASH216_ELEMENT_OPAQUE_BYTES;
}

static HHSHash216VectorStatus hhs_address_fields_validate(
    const HHSHash216AddressFields* fields
) {
    if (!fields) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    if (fields->struct_size < sizeof(*fields) ||
        fields->abi_version != HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION) {
        return HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH;
    }
    if (!hhs_domain_valid(fields->domain)) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_DOMAIN;
    }
    if (!hhs_role_valid(fields->role)) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ROLE;
    }
    if (fields->position > HHS_HASH216_POSITION_MAX) {
        return HHS_HASH216_VECTOR_STATUS_POSITION_OUT_OF_RANGE;
    }
    if (fields->lane > HHS_VM81_LANE_MAX) {
        return HHS_HASH216_VECTOR_STATUS_LANE_OUT_OF_RANGE;
    }
    if (fields->phase < 0 || fields->phase > HHS_HASH72_PHASE_MAX) {
        return HHS_HASH216_VECTOR_STATUS_PHASE_OUT_OF_RANGE;
    }
    if (fields->version == 0U) {
        return HHS_HASH216_VECTOR_STATUS_VERSION_INVALID;
    }
    if (fields->generation == 0U) {
        return HHS_HASH216_VECTOR_STATUS_GENERATION_INVALID;
    }
    if (!hhs_hash216_is_canonical(&fields->content_commitment)) {
        return HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH;
    }
    return HHS_HASH216_VECTOR_STATUS_OK;
}

static size_t hhs_address_material(
    const HHSHash216AddressFields* fields,
    uint8_t* material,
    size_t capacity
) {
    static const uint8_t domain_separator[] = "HHS-HASH216-LOGICAL-ADDRESS-V1";
    size_t used = 0U;
    const size_t required = sizeof(domain_separator) - 1U + 16U + 24U + HHS_HASH216_LEN;
    if (!fields || !material || capacity < required) {
        return 0U;
    }
    memcpy(material + used, domain_separator, sizeof(domain_separator) - 1U);
    used += sizeof(domain_separator) - 1U;
    hhs_put_u32_be(material + used, fields->domain); used += 4U;
    hhs_put_u32_be(material + used, fields->role); used += 4U;
    hhs_put_u32_be(material + used, fields->position); used += 4U;
    hhs_put_u32_be(material + used, fields->lane); used += 4U;
    hhs_put_u64_be(material + used, (uint64_t)fields->phase); used += 8U;
    hhs_put_u64_be(material + used, fields->version); used += 8U;
    hhs_put_u64_be(material + used, fields->generation); used += 8U;
    memcpy(material + used, fields->content_commitment.value, HHS_HASH216_LEN);
    used += HHS_HASH216_LEN;
    return used;
}

HHSHash216VectorStatus hhs_hash216_address_build(
    const HHSHash216AddressFields* fields,
    HHSHash216Address* out_address
) {
    uint8_t material[320];
    size_t material_size;
    HHSHash216VectorStatus status;
    if (!out_address) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memset(out_address, 0, sizeof(*out_address));
    status = hhs_address_fields_validate(fields);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    material_size = hhs_address_material(fields, material, sizeof(material));
    if (material_size == 0U) {
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    out_address->struct_size = (uint32_t)sizeof(*out_address);
    out_address->abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    out_address->fields = *fields;
    hhs_hash216_compute(material, material_size, &out_address->logical_address);
    return HHS_HASH216_VECTOR_STATUS_OK;
}

HHSHash216VectorStatus hhs_hash216_address_validate(
    const HHSHash216Address* address
) {
    HHSHash216 rebuilt;
    uint8_t material[320];
    size_t material_size;
    HHSHash216VectorStatus status;
    if (!address) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    if (address->struct_size < sizeof(*address) ||
        address->abi_version != HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION) {
        return HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH;
    }
    status = hhs_address_fields_validate(&address->fields);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    if (!hhs_hash216_is_canonical(&address->logical_address)) {
        return HHS_HASH216_VECTOR_STATUS_NONCANONICAL_ADDRESS;
    }
    material_size = hhs_address_material(&address->fields, material, sizeof(material));
    if (material_size == 0U) {
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    hhs_hash216_compute(material, material_size, &rebuilt);
    if (!hhs_hash216_equal(&rebuilt, &address->logical_address)) {
        return HHS_HASH216_VECTOR_STATUS_NONCANONICAL_ADDRESS;
    }
    return HHS_HASH216_VECTOR_STATUS_OK;
}

static int hhs_checked_mul_u64(uint64_t a, uint64_t b, uint64_t* out) {
    if (!out) {
        return 0;
    }
    if (a != 0U && b > UINT64_MAX / a) {
        return 0;
    }
    *out = a * b;
    return 1;
}

static size_t hhs_descriptor_material(
    const HHSHash216VectorDescriptor* descriptor,
    uint8_t* material,
    size_t capacity
) {
    static const uint8_t domain_separator[] = "HHS-HASH216-VECTOR-DESCRIPTOR-V1";
    size_t used = 0U;
    const size_t required = sizeof(domain_separator) - 1U + HHS_HASH216_LEN + 40U;
    if (!descriptor || !material || capacity < required) {
        return 0U;
    }
    memcpy(material + used, domain_separator, sizeof(domain_separator) - 1U);
    used += sizeof(domain_separator) - 1U;
    memcpy(material + used, descriptor->address.logical_address.value, HHS_HASH216_LEN);
    used += HHS_HASH216_LEN;
    hhs_put_u64_be(material + used, descriptor->element_count); used += 8U;
    hhs_put_u64_be(material + used, descriptor->byte_length); used += 8U;
    hhs_put_u64_be(material + used, descriptor->capacity_bytes); used += 8U;
    hhs_put_u32_be(material + used, descriptor->element_size); used += 4U;
    hhs_put_u32_be(material + used, descriptor->element_format); used += 4U;
    hhs_put_u32_be(material + used, descriptor->immutable); used += 4U;
    hhs_put_u32_be(material + used, 0U); used += 4U;
    return used;
}

static HHSHash216VectorStatus hhs_descriptor_validate(
    const HHSHash216VectorDescriptor* descriptor
) {
    uint64_t expected_length;
    uint8_t material[320];
    size_t material_size;
    HHSHash216 rebuilt;
    HHSHash216VectorStatus status;
    if (!descriptor) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    if (descriptor->struct_size < sizeof(*descriptor) ||
        descriptor->abi_version != HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION) {
        return HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH;
    }
    status = hhs_hash216_address_validate(&descriptor->address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    if (descriptor->element_count == 0U || descriptor->element_size == 0U ||
        !hhs_element_format_valid(descriptor->element_format) ||
        descriptor->immutable != 1U) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    if (!hhs_checked_mul_u64(
            descriptor->element_count,
            (uint64_t)descriptor->element_size,
            &expected_length)) {
        return HHS_HASH216_VECTOR_STATUS_SIZE_OVERFLOW;
    }
    if (expected_length != descriptor->byte_length) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    if (descriptor->byte_length > descriptor->capacity_bytes ||
        descriptor->capacity_bytes > HHS_HASH216_VECTOR_MAX_BYTES) {
        return HHS_HASH216_VECTOR_STATUS_CAPACITY_VIOLATION;
    }
    if (!hhs_hash216_is_canonical(&descriptor->descriptor_commitment)) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    material_size = hhs_descriptor_material(descriptor, material, sizeof(material));
    if (material_size == 0U) {
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    hhs_hash216_compute(material, material_size, &rebuilt);
    if (!hhs_hash216_equal(&rebuilt, &descriptor->descriptor_commitment)) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    return HHS_HASH216_VECTOR_STATUS_OK;
}

static HHSHash216VectorStatus hhs_slot_from_seed(
    const HHSHash216VectorSeed* seed,
    HHSHash216VectorSlot* slot
) {
    HHSHash216AddressFields fields;
    HHSHash216VectorStatus status;
    uint64_t expected_length;
    uint8_t material[320];
    size_t material_size;
    if (!seed || !slot) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memset(slot, 0, sizeof(*slot));
    if (seed->struct_size < sizeof(*seed) ||
        seed->abi_version != HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION) {
        return HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH;
    }
    if (!hhs_domain_valid(seed->domain)) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_DOMAIN;
    }
    if (!hhs_role_valid(seed->role)) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ROLE;
    }
    if (seed->position > HHS_HASH216_POSITION_MAX) {
        return HHS_HASH216_VECTOR_STATUS_POSITION_OUT_OF_RANGE;
    }
    if (seed->lane > HHS_VM81_LANE_MAX) {
        return HHS_HASH216_VECTOR_STATUS_LANE_OUT_OF_RANGE;
    }
    if (seed->phase < 0 || seed->phase > HHS_HASH72_PHASE_MAX) {
        return HHS_HASH216_VECTOR_STATUS_PHASE_OUT_OF_RANGE;
    }
    if (seed->version == 0U) {
        return HHS_HASH216_VECTOR_STATUS_VERSION_INVALID;
    }
    if (seed->generation == 0U) {
        return HHS_HASH216_VECTOR_STATUS_GENERATION_INVALID;
    }
    if (!seed->data || seed->element_count == 0U || seed->element_size == 0U ||
        !hhs_element_format_valid(seed->element_format)) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    if (!hhs_checked_mul_u64(
            seed->element_count,
            (uint64_t)seed->element_size,
            &expected_length)) {
        return HHS_HASH216_VECTOR_STATUS_SIZE_OVERFLOW;
    }
    if (expected_length != seed->byte_length) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    if (seed->byte_length > seed->capacity_bytes ||
        seed->capacity_bytes > HHS_HASH216_VECTOR_MAX_BYTES) {
        return HHS_HASH216_VECTOR_STATUS_CAPACITY_VIOLATION;
    }

    memset(&fields, 0, sizeof(fields));
    fields.struct_size = (uint32_t)sizeof(fields);
    fields.abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    fields.domain = seed->domain;
    fields.role = seed->role;
    fields.position = seed->position;
    fields.lane = seed->lane;
    fields.phase = seed->phase;
    fields.version = seed->version;
    fields.generation = seed->generation;
    hhs_hash216_compute(seed->data, (size_t)seed->byte_length, &fields.content_commitment);

    slot->descriptor.struct_size = (uint32_t)sizeof(slot->descriptor);
    slot->descriptor.abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    status = hhs_hash216_address_build(&fields, &slot->descriptor.address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    slot->descriptor.element_count = seed->element_count;
    slot->descriptor.byte_length = seed->byte_length;
    slot->descriptor.capacity_bytes = seed->capacity_bytes;
    slot->descriptor.element_size = seed->element_size;
    slot->descriptor.element_format = seed->element_format;
    slot->descriptor.immutable = 1U;
    material_size = hhs_descriptor_material(
        &slot->descriptor, material, sizeof(material));
    if (material_size == 0U) {
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    hhs_hash216_compute(
        material, material_size, &slot->descriptor.descriptor_commitment);
    memcpy(slot->bytes, seed->data, (size_t)seed->byte_length);
    slot->occupied = 1U;
    return hhs_descriptor_validate(&slot->descriptor);
}

static void hhs_slots_sort(HHSHash216VectorResolver* resolver) {
    uint32_t i;
    uint32_t j;
    for (i = 1U; i < resolver->entry_count; ++i) {
        j = i;
        while (j > 0U &&
               memcmp(
                   resolver->slots[j - 1U].descriptor.address.logical_address.value,
                   resolver->slots[j].descriptor.address.logical_address.value,
                   HHS_HASH216_LEN) > 0) {
            HHSHash216VectorSlot temporary = resolver->slots[j - 1U];
            resolver->slots[j - 1U] = resolver->slots[j];
            resolver->slots[j] = temporary;
            --j;
        }
    }
}

static HHSHash216VectorStatus hhs_resolver_root_compute(
    HHSHash216VectorResolver* resolver
) {
    static const uint8_t domain_separator[] = "HHS-HASH216-IMMUTABLE-RESOLVER-ROOT-V1";
    uint8_t material[
        64U + (HHS_HASH216_VECTOR_MAX_OBJECTS * HHS_HASH216_LEN * 2U)
    ];
    size_t used = 0U;
    uint32_t i;
    if (!resolver) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memcpy(material + used, domain_separator, sizeof(domain_separator) - 1U);
    used += sizeof(domain_separator) - 1U;
    hhs_put_u32_be(material + used, resolver->entry_count); used += 4U;
    for (i = 0U; i < resolver->entry_count; ++i) {
        memcpy(
            material + used,
            resolver->slots[i].descriptor.address.logical_address.value,
            HHS_HASH216_LEN);
        used += HHS_HASH216_LEN;
        memcpy(
            material + used,
            resolver->slots[i].descriptor.descriptor_commitment.value,
            HHS_HASH216_LEN);
        used += HHS_HASH216_LEN;
    }
    hhs_hash216_compute(material, used, &resolver->resolver_root);
    return HHS_HASH216_VECTOR_STATUS_OK;
}

static HHSHash216VectorStatus hhs_resolver_validate(
    const HHSHash216VectorResolver* resolver
) {
    HHSHash216VectorResolver copy;
    uint32_t i;
    HHSHash216VectorStatus status;
    if (!resolver) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    if (resolver->struct_size < sizeof(*resolver) ||
        resolver->abi_version != HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION) {
        return HHS_HASH216_VECTOR_STATUS_ABI_VERSION_MISMATCH;
    }
    if (resolver->sealed != 1U) {
        return HHS_HASH216_VECTOR_STATUS_RESOLVER_UNSEALED;
    }
    if (resolver->entry_count == 0U ||
        resolver->entry_count > HHS_HASH216_VECTOR_MAX_OBJECTS) {
        return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
    }
    for (i = 0U; i < resolver->entry_count; ++i) {
        if (resolver->slots[i].occupied != 1U) {
            return HHS_HASH216_VECTOR_STATUS_DESCRIPTOR_INVALID;
        }
        status = hhs_descriptor_validate(&resolver->slots[i].descriptor);
        if (status != HHS_HASH216_VECTOR_STATUS_OK) {
            return status;
        }
        if (i > 0U && memcmp(
                resolver->slots[i - 1U].descriptor.address.logical_address.value,
                resolver->slots[i].descriptor.address.logical_address.value,
                HHS_HASH216_LEN) >= 0) {
            return HHS_HASH216_VECTOR_STATUS_DUPLICATE_ADDRESS;
        }
    }
    copy = *resolver;
    status = hhs_resolver_root_compute(&copy);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    if (!hhs_hash216_equal(&copy.resolver_root, &resolver->resolver_root)) {
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    return HHS_HASH216_VECTOR_STATUS_OK;
}

HHSHash216VectorStatus hhs_hash216_vector_resolver_initialize(
    HHSHash216VectorResolver* resolver,
    const HHSHash216VectorSeed* seeds,
    size_t seed_count
) {
    HHSHash216VectorResolver candidate;
    HHSHash216VectorStatus status;
    uint32_t i;
    if (!resolver) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memset(resolver, 0, sizeof(*resolver));
    if (!seeds || seed_count == 0U ||
        seed_count > HHS_HASH216_VECTOR_MAX_OBJECTS) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memset(&candidate, 0, sizeof(candidate));
    candidate.struct_size = (uint32_t)sizeof(candidate);
    candidate.abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    candidate.entry_count = (uint32_t)seed_count;
    for (i = 0U; i < candidate.entry_count; ++i) {
        status = hhs_slot_from_seed(&seeds[i], &candidate.slots[i]);
        if (status != HHS_HASH216_VECTOR_STATUS_OK) {
            return status;
        }
    }
    hhs_slots_sort(&candidate);
    for (i = 1U; i < candidate.entry_count; ++i) {
        if (hhs_hash216_equal(
                &candidate.slots[i - 1U].descriptor.address.logical_address,
                &candidate.slots[i].descriptor.address.logical_address)) {
            return HHS_HASH216_VECTOR_STATUS_DUPLICATE_ADDRESS;
        }
    }
    candidate.sealed = 1U;
    status = hhs_resolver_root_compute(&candidate);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    status = hhs_resolver_validate(&candidate);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    *resolver = candidate;
    return HHS_HASH216_VECTOR_STATUS_OK;
}

static int hhs_address_stable_identity_equal(
    const HHSHash216Address* left,
    const HHSHash216Address* right
) {
    return left->fields.domain == right->fields.domain &&
           left->fields.role == right->fields.role &&
           left->fields.position == right->fields.position &&
           left->fields.lane == right->fields.lane &&
           left->fields.phase == right->fields.phase;
}

static const HHSHash216VectorSlot* hhs_find_exact_slot(
    const HHSHash216VectorResolver* resolver,
    const HHSHash216Address* address
) {
    uint32_t i;
    for (i = 0U; i < resolver->entry_count; ++i) {
        if (hhs_hash216_equal(
                &resolver->slots[i].descriptor.address.logical_address,
                &address->logical_address)) {
            return &resolver->slots[i];
        }
    }
    return NULL;
}

HHSHash216VectorStatus hhs_hash216_vector_resolve(
    const HHSHash216VectorResolver* resolver,
    const HHSHash216Address* address,
    HHSHash216VectorDescriptor* out_descriptor
) {
    const HHSHash216VectorSlot* exact;
    HHSHash216VectorStatus status;
    uint32_t i;
    if (!out_descriptor) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    memset(out_descriptor, 0, sizeof(*out_descriptor));
    status = hhs_resolver_validate(resolver);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    status = hhs_hash216_address_validate(address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return status;
    }
    exact = hhs_find_exact_slot(resolver, address);
    if (exact) {
        *out_descriptor = exact->descriptor;
        return HHS_HASH216_VECTOR_STATUS_OK;
    }
    for (i = 0U; i < resolver->entry_count; ++i) {
        const HHSHash216Address* current =
            &resolver->slots[i].descriptor.address;
        if (!hhs_address_stable_identity_equal(current, address)) {
            continue;
        }
        if (current->fields.version != address->fields.version) {
            return HHS_HASH216_VECTOR_STATUS_STALE_VERSION;
        }
        if (current->fields.generation != address->fields.generation) {
            return HHS_HASH216_VECTOR_STATUS_STALE_GENERATION;
        }
        if (!hhs_hash216_equal(
                &current->fields.content_commitment,
                &address->fields.content_commitment)) {
            return HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH;
        }
    }
    return HHS_HASH216_VECTOR_STATUS_NOT_FOUND;
}

static void hhs_read_result_initialize(
    HHSHash216VectorReadResult* result,
    const HHSHash216VectorResolver* resolver,
    uint64_t offset,
    uint64_t length
) {
    memset(result, 0, sizeof(*result));
    result->struct_size = (uint32_t)sizeof(*result);
    result->abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    result->requested_offset = offset;
    result->requested_length = length;
    if (resolver) {
        result->resolver_root = resolver->resolver_root;
    }
}

HHSHash216VectorStatus hhs_hash216_vector_read(
    const HHSHash216VectorResolver* resolver,
    const HHSHash216Address* address,
    uint64_t offset,
    uint64_t length,
    void* out_bytes,
    uint64_t out_capacity,
    HHSHash216VectorReadResult* out_result
) {
    HHSHash216VectorDescriptor descriptor;
    const HHSHash216VectorSlot* slot;
    HHSHash216 content;
    HHSHash216VectorStatus status;
    if (!out_result) {
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    hhs_read_result_initialize(out_result, resolver, offset, length);
    if ((length > 0U && !out_bytes) || !address) {
        out_result->status = HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
        return HHS_HASH216_VECTOR_STATUS_INVALID_ARGUMENT;
    }
    status = hhs_hash216_vector_resolve(resolver, address, &descriptor);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        out_result->status = (uint32_t)status;
        return status;
    }
    slot = hhs_find_exact_slot(resolver, address);
    if (!slot) {
        out_result->status = HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
        return HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE;
    }
    hhs_hash216_compute(slot->bytes, (size_t)descriptor.byte_length, &content);
    if (!hhs_hash216_equal(
            &content, &descriptor.address.fields.content_commitment)) {
        out_result->status = HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH;
        return HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH;
    }
    if (offset > descriptor.byte_length ||
        length > descriptor.byte_length - offset) {
        out_result->status = HHS_HASH216_VECTOR_STATUS_READ_OUT_OF_BOUNDS;
        return HHS_HASH216_VECTOR_STATUS_READ_OUT_OF_BOUNDS;
    }
    if (out_capacity < length) {
        out_result->status = HHS_HASH216_VECTOR_STATUS_OUTPUT_TOO_SMALL;
        return HHS_HASH216_VECTOR_STATUS_OUTPUT_TOO_SMALL;
    }
    if (length > 0U) {
        memcpy(out_bytes, slot->bytes + offset, (size_t)length);
    }
    out_result->status = HHS_HASH216_VECTOR_STATUS_OK;
    out_result->bytes_written = length;
    out_result->descriptor = descriptor;
    return HHS_HASH216_VECTOR_STATUS_OK;
}
