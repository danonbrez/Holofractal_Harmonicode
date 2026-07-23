#include "hhs_hash216_vector_resolver_v1.h"

#include <limits.h>
#include <stdio.h>
#include <string.h>

static int reject(const char* message) {
    fprintf(stderr, "%s\n", message);
    return 1;
}

static HHSHash216VectorSeed make_seed(
    uint32_t domain,
    uint32_t role,
    uint32_t position,
    uint32_t lane,
    int64_t phase,
    uint64_t version,
    uint64_t generation,
    const void* data,
    uint64_t length
) {
    HHSHash216VectorSeed seed;
    memset(&seed, 0, sizeof(seed));
    seed.struct_size = (uint32_t)sizeof(seed);
    seed.abi_version = HHS_HASH216_VECTOR_RESOLVER_ABI_VERSION;
    seed.domain = domain;
    seed.role = role;
    seed.position = position;
    seed.lane = lane;
    seed.phase = phase;
    seed.version = version;
    seed.generation = generation;
    seed.element_count = length;
    seed.byte_length = length;
    seed.capacity_bytes = length;
    seed.element_size = 1U;
    seed.element_format = HHS_HASH216_ELEMENT_U8;
    seed.data = data;
    return seed;
}

static int resolver_is_zero(const HHSHash216VectorResolver* resolver) {
    HHSHash216VectorResolver zero;
    memset(&zero, 0, sizeof(zero));
    return memcmp(resolver, &zero, sizeof(zero)) == 0;
}

int main(void) {
    static const uint8_t frame_bytes[] = {
        0, 1, 2, 3, 4, 5, 6, 7,
        8, 9, 10, 11, 12, 13, 14, 15
    };
    static const uint8_t palette_bytes[] = {
        0, 0, 0, 255,
        85, 85, 85, 255,
        170, 170, 170, 255,
        255, 255, 255, 255
    };
    HHSHash216VectorSeed seeds_a[2];
    HHSHash216VectorSeed seeds_b[2];
    HHSHash216VectorSeed invalid_seed;
    HHSHash216VectorSeed duplicate_seeds[2];
    HHSHash216VectorResolver resolver_a;
    HHSHash216VectorResolver resolver_b;
    HHSHash216VectorResolver rejected_resolver;
    HHSHash216VectorResolver tampered_resolver;
    HHSHash216VectorDescriptor descriptor;
    HHSHash216VectorDescriptor unused_descriptor;
    HHSHash216VectorReadResult read_result;
    HHSHash216Address frame_address;
    HHSHash216Address stale_address;
    HHSHash216Address noncanonical_address;
    HHSHash216AddressFields stale_fields;
    uint8_t output[8];
    uint8_t sentinel[8];
    HHSHash216VectorStatus status;
    uint32_t frame_slot = 0U;
    uint32_t i;

    memset(sentinel, 0xA5, sizeof(sentinel));
    seeds_a[0] = make_seed(
        HHS_HASH216_DOMAIN_FRAME,
        HHS_HASH216_VECTOR_ROLE_FRAMEBUFFER,
        40U,
        40U,
        36,
        1U,
        1U,
        frame_bytes,
        sizeof(frame_bytes));
    seeds_a[1] = make_seed(
        HHS_HASH216_DOMAIN_FRAME,
        HHS_HASH216_VECTOR_ROLE_PALETTE,
        41U,
        41U,
        37,
        1U,
        1U,
        palette_bytes,
        sizeof(palette_bytes));
    seeds_b[0] = seeds_a[1];
    seeds_b[1] = seeds_a[0];

    status = hhs_hash216_vector_resolver_initialize(&resolver_a, seeds_a, 2U);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return reject("resolver A initialization failed");
    }
    status = hhs_hash216_vector_resolver_initialize(&resolver_b, seeds_b, 2U);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return reject("resolver B initialization failed");
    }
    if (!resolver_a.sealed || resolver_a.entry_count != 2U) {
        return reject("resolver did not publish as a sealed two-entry snapshot");
    }
    if (!hhs_hash216_equal(&resolver_a.resolver_root, &resolver_b.resolver_root)) {
        return reject("resolver root changed when seed order changed");
    }

    for (i = 0U; i < resolver_a.entry_count; ++i) {
        if (resolver_a.slots[i].descriptor.address.fields.role ==
            HHS_HASH216_VECTOR_ROLE_FRAMEBUFFER) {
            frame_slot = i;
            break;
        }
    }
    frame_address = resolver_a.slots[frame_slot].descriptor.address;
    status = hhs_hash216_address_validate(&frame_address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK) {
        return reject("published frame address is not canonical");
    }
    status = hhs_hash216_vector_resolve(
        &resolver_a, &frame_address, &descriptor);
    if (status != HHS_HASH216_VECTOR_STATUS_OK ||
        descriptor.byte_length != sizeof(frame_bytes) ||
        descriptor.immutable != 1U) {
        return reject("exact frame resolve failed");
    }

    memset(output, 0, sizeof(output));
    status = hhs_hash216_vector_read(
        &resolver_a,
        &frame_address,
        4U,
        6U,
        output,
        sizeof(output),
        &read_result);
    if (status != HHS_HASH216_VECTOR_STATUS_OK ||
        read_result.bytes_written != 6U ||
        memcmp(output, frame_bytes + 4U, 6U) != 0 ||
        !hhs_hash216_equal(&read_result.resolver_root, &resolver_a.resolver_root)) {
        return reject("bounded frame read failed");
    }

    stale_fields = frame_address.fields;
    stale_fields.version += 1U;
    status = hhs_hash216_address_build(&stale_fields, &stale_address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK ||
        hhs_hash216_vector_resolve(
            &resolver_a, &stale_address, &unused_descriptor) !=
        HHS_HASH216_VECTOR_STATUS_STALE_VERSION) {
        return reject("stale version was not rejected explicitly");
    }

    stale_fields = frame_address.fields;
    stale_fields.generation += 1U;
    status = hhs_hash216_address_build(&stale_fields, &stale_address);
    if (status != HHS_HASH216_VECTOR_STATUS_OK ||
        hhs_hash216_vector_resolve(
            &resolver_a, &stale_address, &unused_descriptor) !=
        HHS_HASH216_VECTOR_STATUS_STALE_GENERATION) {
        return reject("stale generation was not rejected explicitly");
    }

    noncanonical_address = frame_address;
    noncanonical_address.logical_address.value[0] =
        noncanonical_address.logical_address.value[0] == '0' ? '1' : '0';
    if (hhs_hash216_vector_resolve(
            &resolver_a, &noncanonical_address, &unused_descriptor) !=
        HHS_HASH216_VECTOR_STATUS_NONCANONICAL_ADDRESS) {
        return reject("noncanonical logical address substitution was accepted");
    }

    memcpy(output, sentinel, sizeof(output));
    if (hhs_hash216_vector_read(
            &resolver_a,
            &frame_address,
            15U,
            2U,
            output,
            sizeof(output),
            &read_result) != HHS_HASH216_VECTOR_STATUS_READ_OUT_OF_BOUNDS ||
        memcmp(output, sentinel, sizeof(output)) != 0) {
        return reject("out-of-bounds read changed output memory");
    }

    memcpy(output, sentinel, sizeof(output));
    if (hhs_hash216_vector_read(
            &resolver_a,
            &frame_address,
            0U,
            6U,
            output,
            5U,
            &read_result) != HHS_HASH216_VECTOR_STATUS_OUTPUT_TOO_SMALL ||
        memcmp(output, sentinel, sizeof(output)) != 0) {
        return reject("small output buffer was not rejected before copying");
    }

    tampered_resolver = resolver_a;
    tampered_resolver.slots[frame_slot].bytes[0] ^= 1U;
    if (hhs_hash216_vector_read(
            &tampered_resolver,
            &frame_address,
            0U,
            1U,
            output,
            sizeof(output),
            &read_result) !=
        HHS_HASH216_VECTOR_STATUS_CONTENT_COMMITMENT_MISMATCH) {
        return reject("tampered vector bytes were not detected");
    }

    tampered_resolver = resolver_a;
    tampered_resolver.resolver_root.value[0] =
        tampered_resolver.resolver_root.value[0] == '0' ? '1' : '0';
    if (hhs_hash216_vector_resolve(
            &tampered_resolver, &frame_address, &unused_descriptor) !=
        HHS_HASH216_VECTOR_STATUS_INTERNAL_INVARIANT_FAILURE) {
        return reject("tampered resolver root was not detected");
    }

    invalid_seed = seeds_a[0];
    invalid_seed.position = 216U;
    memset(&rejected_resolver, 0x5A, sizeof(rejected_resolver));
    if (hhs_hash216_vector_resolver_initialize(
            &rejected_resolver, &invalid_seed, 1U) !=
        HHS_HASH216_VECTOR_STATUS_POSITION_OUT_OF_RANGE ||
        !resolver_is_zero(&rejected_resolver)) {
        return reject("invalid position caused partial resolver publication");
    }

    invalid_seed = seeds_a[0];
    invalid_seed.element_count = UINT64_MAX;
    invalid_seed.element_size = 2U;
    invalid_seed.byte_length = 1U;
    memset(&rejected_resolver, 0x5A, sizeof(rejected_resolver));
    if (hhs_hash216_vector_resolver_initialize(
            &rejected_resolver, &invalid_seed, 1U) !=
        HHS_HASH216_VECTOR_STATUS_SIZE_OVERFLOW ||
        !resolver_is_zero(&rejected_resolver)) {
        return reject("size overflow caused partial resolver publication");
    }

    invalid_seed = seeds_a[0];
    invalid_seed.capacity_bytes = HHS_HASH216_VECTOR_MAX_BYTES + 1U;
    memset(&rejected_resolver, 0x5A, sizeof(rejected_resolver));
    if (hhs_hash216_vector_resolver_initialize(
            &rejected_resolver, &invalid_seed, 1U) !=
        HHS_HASH216_VECTOR_STATUS_CAPACITY_VIOLATION ||
        !resolver_is_zero(&rejected_resolver)) {
        return reject("capacity violation caused partial resolver publication");
    }

    duplicate_seeds[0] = seeds_a[0];
    duplicate_seeds[1] = seeds_a[0];
    memset(&rejected_resolver, 0x5A, sizeof(rejected_resolver));
    if (hhs_hash216_vector_resolver_initialize(
            &rejected_resolver, duplicate_seeds, 2U) !=
        HHS_HASH216_VECTOR_STATUS_DUPLICATE_ADDRESS ||
        !resolver_is_zero(&rejected_resolver)) {
        return reject("duplicate address caused partial resolver publication");
    }

    puts("HASH216_IMMUTABLE_VECTOR_RESOLVER_SMOKE_PASSED");
    return 0;
}
