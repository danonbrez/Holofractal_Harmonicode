#include "hhs_pass174_runtime.h"
#include "hhs_pass160_runtime.h"

#include <stdio.h>
#include <string.h>

static const char HHS174_ALPHABET[HHS174_HASH72_LEN + 1u] =
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

static uint64_t rotl64(uint64_t value, uint32_t amount) {
    amount %= 64u;
    if (amount == 0u) return value;
    return (value << amount) | (value >> (64u - amount));
}

static void store_u64_be(uint8_t out[8], uint64_t value) {
    for (size_t i = 0u; i < 8u; ++i) out[i] = (uint8_t)(value >> (56u - 8u * i));
}

static uint64_t load_u64_be(const uint8_t in[8]) {
    uint64_t value = 0u;
    for (size_t i = 0u; i < 8u; ++i) value = (value << 8u) | (uint64_t)in[i];
    return value;
}

static void digest256(const void *data, size_t size, HHS174Digest256 *out) {
    HHSP160Integrity256 digest;
    hhs_pass160_sha256(data, size, &digest);
    memcpy(out->bytes, digest.bytes, HHS174_SHA256_BYTES);
}

static int digest_equal(const HHS174Digest256 *left, const HHS174Digest256 *right) {
    return left && right && memcmp(left->bytes, right->bytes, HHS174_SHA256_BYTES) == 0;
}

static int digest_zero(const HHS174Digest256 *value) {
    uint8_t accumulator = 0u;
    if (!value) return 1;
    for (size_t i = 0u; i < HHS174_SHA256_BYTES; ++i) accumulator |= value->bytes[i];
    return accumulator == 0u;
}

static void frame_finalize(HHS174Frame5184 *frame) {
    static const uint8_t domain[] = "HHS174-FRAME-V1";
    uint8_t material[sizeof(domain) - 1u + 8u + HHS174_FRAME_WORDS * 8u];
    size_t cursor = 0u;
    memcpy(material + cursor, domain, sizeof(domain) - 1u);
    cursor += sizeof(domain) - 1u;
    store_u64_be(material + cursor, frame->sequence);
    cursor += 8u;
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        store_u64_be(material + cursor, frame->words[i]);
        cursor += 8u;
    }
    digest256(material, cursor, &frame->identity);
}

static uint64_t popcount64(uint64_t value) {
    uint64_t count = 0u;
    while (value) {
        value &= value - 1u;
        ++count;
    }
    return count;
}

static uint64_t total_cost(const HHS174CostUnits *cost) {
    return cost->decoded_bytecodes + cost->cell_reads + cost->cell_writes +
           cost->bit_rotations + cost->lane_permutations + cost->modular_operations +
           cost->constraint_evaluations + cost->harmonic_relations +
           cost->sha256_index_validations + cost->hash72_projections +
           cost->hash216_operations + cost->active_suffix_records +
           cost->closure_iterations;
}

static int witness_complete(const HHS174AdmissionWitness *witness) {
    return witness && witness->genesis_valid && witness->predecessor_valid &&
           witness->current_valid && witness->continuation_valid &&
           witness->vm81_valid && witness->hash72_valid &&
           witness->hash216_valid && witness->authenticated_encryption_valid;
}

const char *hhs174_status_string(HHS174Status status) {
    switch (status) {
        case HHS174_OK: return "HHS174_OK";
        case HHS174_INVALID_ARGUMENT: return "HHS174_INVALID_ARGUMENT";
        case HHS174_FRAME_GEOMETRY_ERROR: return "HHS174_FRAME_GEOMETRY_ERROR";
        case HHS174_NO_CANDIDATE: return "HHS174_NO_CANDIDATE";
        case HHS174_STALE_CANDIDATE: return "HHS174_STALE_CANDIDATE";
        case HHS174_AUTHORITY_REJECTED: return "HHS174_AUTHORITY_REJECTED";
        case HHS174_HASH72_MISMATCH: return "HHS174_HASH72_MISMATCH";
        case HHS174_HASH216_MISMATCH: return "HHS174_HASH216_MISMATCH";
        case HHS174_INDEX_MISMATCH: return "HHS174_INDEX_MISMATCH";
        case HHS174_STORE_FULL: return "HHS174_STORE_FULL";
        case HHS174_NOT_FOUND: return "HHS174_NOT_FOUND";
        case HHS174_QUARANTINED: return "HHS174_QUARANTINED";
        case HHS174_FRONTIER_MISMATCH: return "HHS174_FRONTIER_MISMATCH";
        case HHS174_REPLAY_MISMATCH: return "HHS174_REPLAY_MISMATCH";
        case HHS174_RESOURCE_BOUNDED: return "HHS174_RESOURCE_BOUNDED";
        default: return "HHS174_UNKNOWN_STATUS";
    }
}

HHS174Status hhs174_phase_coordinate(uint64_t transition, HHS174PhaseCoordinate *out) {
    if (!out) return HHS174_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->transition = transition;
    out->phase64 = (uint16_t)(transition % 64u);
    out->phase72 = (uint16_t)(transition % 72u);
    out->phase81 = (uint16_t)(transition % 81u);
    out->phase5184 = (uint16_t)(transition % HHS174_PHASE_LOCK_PERIOD);
    out->lock64 = (uint8_t)(transition > 0u && transition % 64u == 0u);
    out->lock72 = (uint8_t)(transition > 0u && transition % 72u == 0u);
    out->lock81 = (uint8_t)(transition > 0u && transition % 81u == 0u);
    out->complete_lock = (uint8_t)(transition > 0u && transition % HHS174_PHASE_LOCK_PERIOD == 0u);
    return HHS174_OK;
}

HHS174Status hhs174_phase_closure(const HHS174PhaseCoordinate *phase, uint8_t *out_complete) {
    if (!phase || !out_complete) return HHS174_INVALID_ARGUMENT;
    *out_complete = phase->complete_lock;
    return HHS174_OK;
}

HHS174Status hhs174_hash72_project(const void *data, size_t size, char out_hash72[HHS174_HASH72_LEN + 1u]) {
    if ((!data && size) || !out_hash72) return HHS174_INVALID_ARGUMENT;
    HHS174Digest256 seed;
    digest256(data, size, &seed);
    size_t written = 0u;
    uint32_t counter = 0u;
    while (written < HHS174_HASH72_LEN) {
        uint8_t material[HHS174_SHA256_BYTES + 4u];
        HHS174Digest256 block;
        memcpy(material, seed.bytes, HHS174_SHA256_BYTES);
        material[32] = (uint8_t)(counter >> 24u);
        material[33] = (uint8_t)(counter >> 16u);
        material[34] = (uint8_t)(counter >> 8u);
        material[35] = (uint8_t)counter;
        digest256(material, sizeof(material), &block);
        ++counter;
        for (size_t i = 0u; i < HHS174_SHA256_BYTES && written < HHS174_HASH72_LEN; ++i) {
            out_hash72[written++] = HHS174_ALPHABET[block.bytes[i] % HHS174_HASH72_LEN];
        }
    }
    out_hash72[HHS174_HASH72_LEN] = '\0';
    return HHS174_OK;
}

HHS174Status hhs174_genesis_init(HHS174Runtime *runtime, const void *seed, size_t seed_size) {
    if (!runtime || (!seed && seed_size == 0u)) return HHS174_INVALID_ARGUMENT;
    memset(runtime, 0, sizeof(*runtime));
    runtime->abi_version = HHS174_ABI_VERSION;
    digest256(seed, seed_size, &runtime->genesis_identity);
    runtime->previous_frame.sequence = 0u;
    frame_finalize(&runtime->previous_frame);
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        uint8_t material[HHS174_SHA256_BYTES + 8u];
        HHS174Digest256 block;
        memcpy(material, runtime->genesis_identity.bytes, HHS174_SHA256_BYTES);
        store_u64_be(material + HHS174_SHA256_BYTES, (uint64_t)i);
        digest256(material, sizeof(material), &block);
        runtime->current_frame.words[i] = load_u64_be(block.bytes);
    }
    runtime->current_frame.sequence = 0u;
    frame_finalize(&runtime->current_frame);
    hhs174_phase_coordinate(0u, &runtime->phase);
    hhs174_hash72_project(runtime->current_frame.identity.bytes, HHS174_SHA256_BYTES, runtime->hash72_tip);
    runtime->boot_admitted = 1u;
    return HHS174_OK;
}

HHS174Status hhs174_boot_fingerprint(const HHS174Runtime *runtime, const void *challenge, size_t challenge_size, HHS174Digest256 *canonical, HHS174Digest256 *instance) {
    if (!runtime || !canonical || !instance || (!challenge && challenge_size)) return HHS174_INVALID_ARGUMENT;
    uint8_t canonical_material[HHS174_SHA256_BYTES * 3u + HHS174_HASH72_LEN];
    size_t cursor = 0u;
    memcpy(canonical_material + cursor, runtime->genesis_identity.bytes, 32u); cursor += 32u;
    memcpy(canonical_material + cursor, runtime->previous_frame.identity.bytes, 32u); cursor += 32u;
    memcpy(canonical_material + cursor, runtime->current_frame.identity.bytes, 32u); cursor += 32u;
    memcpy(canonical_material + cursor, runtime->hash72_tip, HHS174_HASH72_LEN); cursor += HHS174_HASH72_LEN;
    digest256(canonical_material, cursor, canonical);
    HHSP160Integrity256 context;
    hhs_pass160_sha256(challenge, challenge_size, &context);
    uint8_t instance_material[HHS174_SHA256_BYTES * 2u + 8u];
    memcpy(instance_material, canonical->bytes, 32u);
    memcpy(instance_material + 32u, context.bytes, 32u);
    store_u64_be(instance_material + 64u, runtime->transition_count);
    digest256(instance_material, sizeof(instance_material), instance);
    return HHS174_OK;
}

HHS174Status hhs174_frame_read(const HHS174Runtime *runtime, HHS174Frame5184 *out) {
    if (!runtime || !out) return HHS174_INVALID_ARGUMENT;
    *out = runtime->current_frame;
    return HHS174_OK;
}

HHS174Status hhs174_harmonic_compile(const void *source, size_t source_size, HHS174Digest256 *operator_identity) {
    if ((!source && source_size) || !operator_identity) return HHS174_INVALID_ARGUMENT;
    digest256(source, source_size, operator_identity);
    return HHS174_OK;
}

static void build_operator_identity(HHS174Opcode opcode, uint64_t operand, HHS174Digest256 *out) {
    uint8_t material[12u];
    material[0] = 'P'; material[1] = '1'; material[2] = '7'; material[3] = '4';
    store_u64_be(material + 4u, (((uint64_t)(uint32_t)opcode) << 32u) ^ operand);
    digest256(material, sizeof(material), out);
}

static HHS174Status build_transition(HHS174Runtime *runtime, HHS174Opcode opcode, uint64_t operand) {
    HHS174Hash72Transition *transition = &runtime->pending_transition;
    memset(transition, 0, sizeof(*transition));
    transition->previous_frame_identity = runtime->previous_frame.identity;
    transition->current_frame_identity = runtime->current_frame.identity;
    transition->successor_frame_identity = runtime->candidate_frame.identity;
    build_operator_identity(opcode, operand, &transition->operator_identity);
    transition->phase = runtime->phase;
    memcpy(transition->incoming_tip, runtime->hash72_tip, HHS174_HASH72_LEN + 1u);

    uint8_t material[HHS174_SHA256_BYTES * 4u + HHS174_HASH72_LEN + sizeof(HHS174PhaseCoordinate)];
    size_t cursor = 0u;
    memcpy(material + cursor, transition->previous_frame_identity.bytes, 32u); cursor += 32u;
    memcpy(material + cursor, transition->current_frame_identity.bytes, 32u); cursor += 32u;
    memcpy(material + cursor, transition->successor_frame_identity.bytes, 32u); cursor += 32u;
    memcpy(material + cursor, transition->operator_identity.bytes, 32u); cursor += 32u;
    memcpy(material + cursor, transition->incoming_tip, HHS174_HASH72_LEN); cursor += HHS174_HASH72_LEN;
    memcpy(material + cursor, &transition->phase, sizeof(transition->phase)); cursor += sizeof(transition->phase);

    material[0] ^= 0x2Du;
    hhs174_hash72_project(material, cursor, transition->predecessor_lane);
    material[0] ^= 0x2Du ^ 0x30u;
    hhs174_hash72_project(material, cursor, transition->current_lane);
    material[0] ^= 0x30u ^ 0x2Bu;
    hhs174_hash72_project(material, cursor, transition->successor_lane);
    memcpy(transition->outgoing_tip, transition->current_lane, HHS174_HASH72_LEN + 1u);
    digest256(material, cursor, &transition->witness_identity);
    return hhs174_hash216_build(transition, &runtime->pending_hash216);
}

HHS174Status hhs174_frame_execute(HHS174Runtime *runtime, HHS174Opcode opcode, uint64_t operand, HHS174Frame5184 *out_candidate) {
    if (!runtime || !runtime->boot_admitted || opcode < HHS174_OP_ROTATE || opcode > HHS174_OP_MIXED) return HHS174_INVALID_ARGUMENT;
    if (runtime->has_candidate) return HHS174_AUTHORITY_REJECTED;
    HHS174Frame5184 candidate;
    memset(&candidate, 0, sizeof(candidate));
    uint64_t fold = 0x179971179971ULL;
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        fold ^= rotl64(runtime->current_frame.words[i], (uint32_t)i);
        fold = rotl64(fold + runtime->current_frame.words[i] + (uint64_t)i + 1u, 7u);
    }
    hhs174_phase_coordinate(runtime->transition_count + 1u, &runtime->phase);
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        uint64_t current = runtime->current_frame.words[i];
        uint64_t left = runtime->current_frame.words[(i + HHS174_FRAME_WORDS - 1u) % HHS174_FRAME_WORDS];
        uint64_t right = runtime->current_frame.words[(i + 1u) % HHS174_FRAME_WORDS];
        uint64_t phase_mix = (uint64_t)runtime->phase.phase64 |
                             ((uint64_t)runtime->phase.phase72 << 7u) |
                             ((uint64_t)runtime->phase.phase81 << 14u) |
                             ((uint64_t)runtime->phase.phase5184 << 21u);
        uint64_t value = 0u;
        switch (opcode) {
            case HHS174_OP_ROTATE:
                value = rotl64(current ^ right ^ fold ^ phase_mix, (uint32_t)(operand + i + runtime->phase.phase72));
                break;
            case HHS174_OP_XOR:
                value = current ^ left ^ rotl64(right, (uint32_t)operand) ^ fold ^ phase_mix;
                break;
            case HHS174_OP_ADD:
                value = current + left + right + fold + operand + (uint64_t)i + phase_mix;
                break;
            case HHS174_OP_PERMUTE:
                value = runtime->current_frame.words[(i + (size_t)(operand % HHS174_FRAME_WORDS)) % HHS174_FRAME_WORDS] ^ rotl64(fold, (uint32_t)(i + runtime->phase.phase64));
                break;
            case HHS174_OP_RECIPROCAL:
                value = rotl64(runtime->current_frame.words[(HHS174_FRAME_WORDS - 1u - i + (size_t)(operand % HHS174_FRAME_WORDS)) % HHS174_FRAME_WORDS] ^ fold ^ phase_mix, (uint32_t)(36u + i));
                break;
            case HHS174_OP_HARMONIC:
                value = current * ((operand >> 32u) | 1u) + right * ((operand & 0xffffffffu) | 1u) + left + fold + phase_mix;
                break;
            case HHS174_OP_MIXED:
                value = rotl64((current ^ right ^ fold) + left + operand, (uint32_t)(i + operand)) ^ phase_mix;
                break;
            default:
                return HHS174_INVALID_ARGUMENT;
        }
        candidate.words[i] = value;
    }
    candidate.sequence = runtime->current_frame.sequence + 1u;
    frame_finalize(&candidate);
    runtime->candidate_frame = candidate;
    runtime->has_candidate = 1u;
    memset(&runtime->last_cost, 0, sizeof(runtime->last_cost));
    runtime->last_cost.decoded_bytecodes = 1u;
    runtime->last_cost.cell_reads = HHS174_FRAME_WORDS * 4u;
    runtime->last_cost.cell_writes = HHS174_FRAME_WORDS;
    runtime->last_cost.bit_rotations = HHS174_FRAME_WORDS * 2u;
    runtime->last_cost.lane_permutations = (opcode == HHS174_OP_PERMUTE || opcode == HHS174_OP_RECIPROCAL) ? HHS174_FRAME_WORDS : 0u;
    runtime->last_cost.modular_operations = HHS174_FRAME_WORDS * 2u;
    runtime->last_cost.constraint_evaluations = HHS174_FRAME_WORDS + 1u;
    runtime->last_cost.harmonic_relations = (opcode == HHS174_OP_HARMONIC || opcode == HHS174_OP_MIXED) ? HHS174_FRAME_WORDS : 0u;
    runtime->last_cost.closure_iterations = 1u;
    HHS174Status built = build_transition(runtime, opcode, operand);
    if (built != HHS174_OK) {
        runtime->has_candidate = 0u;
        return built;
    }
    if (out_candidate) *out_candidate = candidate;
    return HHS174_OK;
}

HHS174Status hhs174_harmonic_execute(HHS174Runtime *runtime, uint64_t numerator, uint64_t denominator, HHS174Frame5184 *out_candidate) {
    if (denominator == 0u) return HHS174_INVALID_ARGUMENT;
    uint64_t operand = (numerator << 32u) ^ (denominator & 0xffffffffu);
    return hhs174_frame_execute(runtime, HHS174_OP_HARMONIC, operand, out_candidate);
}

HHS174Status hhs174_hash216_index_character(const HHS174Hash216Array *array, uint16_t position, const HHS174Digest256 *previous_index, HHS174Digest256 *out) {
    if (!array || !previous_index || !out || position >= HHS174_HASH216_LEN) return HHS174_INVALID_ARGUMENT;
    uint16_t next = (uint16_t)((position + 1u) % HHS174_HASH216_LEN);
    uint8_t material[HHS174_SHA256_BYTES * 3u + 8u];
    size_t cursor = 0u;
    memcpy(material + cursor, array->logical_identity.bytes, 32u); cursor += 32u;
    memcpy(material + cursor, previous_index->bytes, 32u); cursor += 32u;
    HHS174Digest256 boundary;
    uint8_t boundary_material[HHS174_SHA256_BYTES + 4u];
    memcpy(boundary_material, array->logical_identity.bytes, 32u);
    boundary_material[32] = (uint8_t)(next >> 8u);
    boundary_material[33] = (uint8_t)next;
    boundary_material[34] = (uint8_t)array->value[next];
    boundary_material[35] = 0xB1u;
    digest256(boundary_material, sizeof(boundary_material), &boundary);
    memcpy(material + cursor, boundary.bytes, 32u); cursor += 32u;
    material[cursor++] = (uint8_t)(position >> 8u);
    material[cursor++] = (uint8_t)position;
    material[cursor++] = (uint8_t)(position / HHS174_HASH72_LEN);
    material[cursor++] = (uint8_t)(position % HHS174_HASH72_LEN);
    material[cursor++] = (uint8_t)array->value[position];
    material[cursor++] = 1u;
    material[cursor++] = 0u;
    material[cursor++] = 0u;
    digest256(material, cursor, out);
    return HHS174_OK;
}

HHS174Status hhs174_hash216_build(const HHS174Hash72Transition *transition, HHS174Hash216Array *out) {
    if (!transition || !out) return HHS174_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    memcpy(out->value, transition->predecessor_lane, HHS174_HASH72_LEN);
    memcpy(out->value + HHS174_HASH72_LEN, transition->current_lane, HHS174_HASH72_LEN);
    memcpy(out->value + HHS174_HASH72_LEN * 2u, transition->successor_lane, HHS174_HASH72_LEN);
    out->value[HHS174_HASH216_LEN] = '\0';
    digest256(out->value, HHS174_HASH216_LEN, &out->logical_identity);
    HHS174Digest256 previous;
    uint8_t anchor[HHS174_SHA256_BYTES + 1u];
    memcpy(anchor, out->logical_identity.bytes, 32u);
    anchor[32] = 0xA1u;
    digest256(anchor, sizeof(anchor), &previous);
    for (uint16_t i = 0u; i < HHS174_HASH216_LEN; ++i) {
        HHS174Status status = hhs174_hash216_index_character(out, i, &previous, &out->character_indexes[i]);
        if (status != HHS174_OK) return status;
        previous = out->character_indexes[i];
    }
    digest256(out->character_indexes, sizeof(out->character_indexes), &out->index_root);
    return HHS174_OK;
}

HHS174Status hhs174_hash216_validate(const HHS174Hash216Array *array) {
    if (!array || strlen(array->value) != HHS174_HASH216_LEN) return HHS174_HASH216_MISMATCH;
    HHS174Hash216Array rebuilt;
    memset(&rebuilt, 0, sizeof(rebuilt));
    memcpy(rebuilt.value, array->value, HHS174_HASH216_LEN + 1u);
    digest256(rebuilt.value, HHS174_HASH216_LEN, &rebuilt.logical_identity);
    if (!digest_equal(&rebuilt.logical_identity, &array->logical_identity)) return HHS174_HASH216_MISMATCH;
    HHS174Digest256 previous;
    uint8_t anchor[HHS174_SHA256_BYTES + 1u];
    memcpy(anchor, array->logical_identity.bytes, 32u);
    anchor[32] = 0xA1u;
    digest256(anchor, sizeof(anchor), &previous);
    for (uint16_t i = 0u; i < HHS174_HASH216_LEN; ++i) {
        HHS174Digest256 expected;
        HHS174Status status = hhs174_hash216_index_character(array, i, &previous, &expected);
        if (status != HHS174_OK || !digest_equal(&expected, &array->character_indexes[i])) return HHS174_INDEX_MISMATCH;
        previous = expected;
    }
    digest256(array->character_indexes, sizeof(array->character_indexes), &rebuilt.index_root);
    return digest_equal(&rebuilt.index_root, &array->index_root) ? HHS174_OK : HHS174_INDEX_MISMATCH;
}

static void build_delta(const HHS174Frame5184 *source, const HHS174Frame5184 *destination, HHS174SparseDelta *out) {
    memset(out, 0, sizeof(*out));
    out->source_identity = source->identity;
    out->destination_identity = destination->identity;
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        uint64_t mask = source->words[i] ^ destination->words[i];
        if (mask) {
            out->replacement_words[i] = destination->words[i];
            out->changed_bit_masks[i] = mask;
            ++out->changed_cells;
            out->changed_bits = (uint16_t)(out->changed_bits + popcount64(mask));
            if (i < 64u) out->changed_cell_mask_low |= UINT64_C(1) << i;
            else out->changed_cell_mask_high |= UINT64_C(1) << (i - 64u);
        }
    }
}

HHS174Status hhs174_delta_apply(const HHS174Frame5184 *source, const HHS174SparseDelta *delta, HHS174Frame5184 *out) {
    if (!source || !delta || !out) return HHS174_INVALID_ARGUMENT;
    if (!digest_equal(&source->identity, &delta->source_identity)) return HHS174_STALE_CANDIDATE;
    *out = *source;
    for (size_t i = 0u; i < HHS174_FRAME_WORDS; ++i) {
        int changed = i < 64u ? (int)((delta->changed_cell_mask_low >> i) & 1u) : (int)((delta->changed_cell_mask_high >> (i - 64u)) & 1u);
        if (changed) out->words[i] = delta->replacement_words[i];
    }
    out->sequence = source->sequence + 1u;
    frame_finalize(out);
    return digest_equal(&out->identity, &delta->destination_identity) ? HHS174_OK : HHS174_INDEX_MISMATCH;
}

HHS174Status hhs174_vector_query(const HHS174VectorStore *store, const HHS174Digest256 *query_identity, const char *incoming_tip, size_t *out_index) {
    if (!store || !query_identity || !incoming_tip || !out_index) return HHS174_INVALID_ARGUMENT;
    for (size_t offset = 0u; offset < store->count; ++offset) {
        size_t i = store->count - 1u - offset;
        const HHS174VectorObject *object = &store->objects[i];
        if (object->occupied && !object->quarantined && object->authenticated &&
            digest_equal(&object->query_identity, query_identity) &&
            memcmp(object->transition.incoming_tip, incoming_tip, HHS174_HASH72_LEN) == 0) {
            *out_index = i;
            return HHS174_OK;
        }
    }
    return HHS174_NOT_FOUND;
}

HHS174Status hhs174_vector_retrieve(const HHS174VectorStore *store, size_t index, const char *incoming_tip, HHS174VectorObject *out) {
    if (!store || !incoming_tip || !out || index >= store->count) return HHS174_INVALID_ARGUMENT;
    const HHS174VectorObject *object = &store->objects[index];
    if (!object->occupied) return HHS174_NOT_FOUND;
    if (object->quarantined) return HHS174_QUARANTINED;
    if (!object->authenticated) return HHS174_AUTHORITY_REJECTED;
    if (memcmp(object->transition.incoming_tip, incoming_tip, HHS174_HASH72_LEN) != 0) return HHS174_FRONTIER_MISMATCH;
    HHS174Status valid = hhs174_hash216_validate(&object->hash216);
    if (valid != HHS174_OK) return valid;
    *out = *object;
    return HHS174_OK;
}

HHS174Status hhs174_vector_admit(HHS174VectorStore *store, const HHS174VectorObject *object, const HHS174AdmissionWitness *witness, size_t *out_index) {
    if (!store || !object || !out_index) return HHS174_INVALID_ARGUMENT;
    if (!witness_complete(witness) || !object->authenticated) return HHS174_AUTHORITY_REJECTED;
    if (hhs174_hash216_validate(&object->hash216) != HHS174_OK) return HHS174_HASH216_MISMATCH;
    if (!digest_zero(&object->parent_identity)) {
        int found = 0;
        for (size_t i = 0u; i < store->count; ++i) {
            if (store->objects[i].occupied && !store->objects[i].quarantined && digest_equal(&store->objects[i].logical_identity, &object->parent_identity)) {
                found = 1;
                break;
            }
        }
        if (!found) return HHS174_FRONTIER_MISMATCH;
    }
    for (size_t i = 0u; i < store->count; ++i) {
        if (store->objects[i].occupied && digest_equal(&store->objects[i].logical_identity, &object->logical_identity)) {
            *out_index = i;
            return HHS174_OK;
        }
    }
    if (store->count >= HHS174_MAX_VECTOR_OBJECTS) return HHS174_STORE_FULL;
    store->objects[store->count] = *object;
    store->objects[store->count].occupied = 1u;
    *out_index = store->count++;
    if (store->active_suffix_count < HHS174_MAX_ACTIVE_SUFFIX) {
        store->active_suffix[store->active_suffix_count++] = object->logical_identity;
    } else {
        memmove(store->active_suffix, store->active_suffix + 1u, (HHS174_MAX_ACTIVE_SUFFIX - 1u) * sizeof(store->active_suffix[0]));
        store->active_suffix[HHS174_MAX_ACTIVE_SUFFIX - 1u] = object->logical_identity;
    }
    return HHS174_OK;
}

HHS174Status hhs174_vector_quarantine(HHS174VectorStore *store, const HHS174Digest256 *identity) {
    if (!store || !identity) return HHS174_INVALID_ARGUMENT;
    for (size_t i = 0u; i < store->count; ++i) {
        if (store->objects[i].occupied && digest_equal(&store->objects[i].logical_identity, identity)) {
            store->objects[i].quarantined = 1u;
            return HHS174_OK;
        }
    }
    return HHS174_NOT_FOUND;
}

HHS174Status hhs174_frame_commit(HHS174Runtime *runtime, const HHS174AdmissionWitness *witness) {
    if (!runtime || !runtime->has_candidate) return HHS174_NO_CANDIDATE;
    if (!witness_complete(witness)) return HHS174_AUTHORITY_REJECTED;
    if (!digest_equal(&runtime->pending_transition.current_frame_identity, &runtime->current_frame.identity) ||
        !digest_equal(&runtime->pending_transition.successor_frame_identity, &runtime->candidate_frame.identity)) return HHS174_STALE_CANDIDATE;
    HHS174VectorObject object;
    memset(&object, 0, sizeof(object));
    object.destination_frame = runtime->candidate_frame;
    object.transition = runtime->pending_transition;
    object.hash216 = runtime->pending_hash216;
    object.sequence = runtime->transition_count + 1u;
    object.key_version = 1u;
    object.authenticated = witness->authenticated_encryption_valid;
    object.query_identity = runtime->pending_transition.operator_identity;
    if (runtime->store.active_suffix_count) object.parent_identity = runtime->store.active_suffix[runtime->store.active_suffix_count - 1u];
    build_delta(&runtime->current_frame, &runtime->candidate_frame, &object.delta);
    uint8_t logical_material[HHS174_SHA256_BYTES * 4u + HHS174_HASH72_LEN];
    memcpy(logical_material, object.destination_frame.identity.bytes, 32u);
    memcpy(logical_material + 32u, object.hash216.logical_identity.bytes, 32u);
    memcpy(logical_material + 64u, object.hash216.index_root.bytes, 32u);
    memcpy(logical_material + 96u, object.parent_identity.bytes, 32u);
    memcpy(logical_material + 128u, object.transition.outgoing_tip, HHS174_HASH72_LEN);
    digest256(logical_material, sizeof(logical_material), &object.logical_identity);
    size_t index = 0u;
    HHS174Status admitted = hhs174_vector_admit(&runtime->store, &object, witness, &index);
    if (admitted != HHS174_OK) return admitted;
    runtime->previous_frame = runtime->current_frame;
    runtime->current_frame = runtime->candidate_frame;
    memcpy(runtime->hash72_tip, runtime->pending_transition.outgoing_tip, HHS174_HASH72_LEN + 1u);
    ++runtime->transition_count;
    hhs174_phase_coordinate(runtime->transition_count, &runtime->phase);
    runtime->has_candidate = 0u;
    runtime->last_cost.sha256_index_validations += HHS174_HASH216_LEN;
    runtime->last_cost.hash72_projections += 3u;
    runtime->last_cost.hash216_operations += 1u;
    runtime->last_cost.active_suffix_records = runtime->store.active_suffix_count;
    hhs174_efficiency_update(&runtime->efficiency, &runtime->last_cost, 0u, 1u);
    return HHS174_OK;
}

HHS174Status hhs174_phase_step(HHS174Runtime *runtime, HHS174Opcode opcode, uint64_t operand) {
    HHS174Status status = hhs174_frame_execute(runtime, opcode, operand, NULL);
    if (status != HHS174_OK) return status;
    HHS174AdmissionWitness witness = {1u,1u,1u,1u,1u,1u,1u,1u};
    return hhs174_frame_commit(runtime, &witness);
}

HHS174Status hhs174_hash72_tip(const HHS174Runtime *runtime, char out_hash72[HHS174_HASH72_LEN + 1u]) {
    if (!runtime || !out_hash72) return HHS174_INVALID_ARGUMENT;
    memcpy(out_hash72, runtime->hash72_tip, HHS174_HASH72_LEN + 1u);
    return HHS174_OK;
}

HHS174Status hhs174_efficiency_update(HHS174EfficiencyRecord *record, const HHS174CostUnits *cost, uint8_t retrieval_path, uint8_t accepted) {
    if (!record || !cost) return HHS174_INVALID_ARGUMENT;
    uint64_t cost_value = total_cost(cost);
    if (retrieval_path) {
        record->retrieval_cost += cost_value;
        if (accepted) ++record->successful_retrievals;
        else ++record->rejected_retrievals;
    } else {
        record->direct_cost += cost_value;
    }
    return hhs174_efficiency_compare(record);
}

HHS174Status hhs174_efficiency_compare(HHS174EfficiencyRecord *record) {
    if (!record) return HHS174_INVALID_ARGUMENT;
    record->retrieval_advantage = (int64_t)record->direct_cost - (int64_t)record->retrieval_cost;
    record->retrieval_preferred = (uint8_t)(record->retrieval_cost > 0u && record->retrieval_advantage > 0);
    return HHS174_OK;
}

HHS174Status hhs174_genesis_audit(const HHS174Runtime *runtime, const void *challenge, size_t challenge_size, uint64_t sample_count, HHS174AuditResult *out) {
    if (!runtime || !out || (!challenge && challenge_size) || sample_count == 0u) return HHS174_INVALID_ARGUMENT;
    if (runtime->store.count == 0u) return HHS174_NOT_FOUND;
    if (sample_count > runtime->store.count) sample_count = runtime->store.count;
    uint8_t seed_material[HHS174_SHA256_BYTES + HHS174_HASH72_LEN + HHS174_SHA256_BYTES];
    HHS174Digest256 challenge_digest;
    digest256(challenge, challenge_size, &challenge_digest);
    memcpy(seed_material, runtime->genesis_identity.bytes, 32u);
    memcpy(seed_material + 32u, runtime->hash72_tip, HHS174_HASH72_LEN);
    memcpy(seed_material + 32u + HHS174_HASH72_LEN, challenge_digest.bytes, 32u);
    memset(out, 0, sizeof(*out));
    digest256(seed_material, sizeof(seed_material), &out->seed_identity);
    out->requested_samples = sample_count;
    for (uint64_t ordinal = 0u; ordinal < sample_count; ++ordinal) {
        uint8_t material[HHS174_SHA256_BYTES + 8u];
        HHS174Digest256 sample_digest;
        memcpy(material, out->seed_identity.bytes, 32u);
        store_u64_be(material + 32u, ordinal);
        digest256(material, sizeof(material), &sample_digest);
        size_t index = (size_t)(load_u64_be(sample_digest.bytes) % runtime->store.count);
        const HHS174VectorObject *object = &runtime->store.objects[index];
        ++out->executed_samples;
        if (!object->occupied || object->quarantined || !object->authenticated || hhs174_hash216_validate(&object->hash216) != HHS174_OK) ++out->failed_samples;
    }
    out->passed = (uint8_t)(out->failed_samples == 0u);
    return out->passed ? HHS174_OK : HHS174_INDEX_MISMATCH;
}

HHS174Status hhs174_replay(const void *seed, size_t seed_size, const HHS174Opcode *opcodes, const uint64_t *operands, size_t operation_count, HHS174Digest256 *out_frame_identity, char out_hash72[HHS174_HASH72_LEN + 1u]) {
    if (!seed || !opcodes || !operands || !out_frame_identity || !out_hash72) return HHS174_INVALID_ARGUMENT;
    HHS174Runtime runtime;
    HHS174Status status = hhs174_genesis_init(&runtime, seed, seed_size);
    if (status != HHS174_OK) return status;
    for (size_t i = 0u; i < operation_count; ++i) {
        status = hhs174_phase_step(&runtime, opcodes[i], operands[i]);
        if (status != HHS174_OK) return status;
    }
    *out_frame_identity = runtime.current_frame.identity;
    memcpy(out_hash72, runtime.hash72_tip, HHS174_HASH72_LEN + 1u);
    return HHS174_OK;
}

HHS174Status hhs174_status(const HHS174Runtime *runtime, HHS174StatusSnapshot *out) {
    if (!runtime || !out) return HHS174_INVALID_ARGUMENT;
    memset(out, 0, sizeof(*out));
    out->abi_version = runtime->abi_version;
    out->transition_count = runtime->transition_count;
    out->phase = runtime->phase;
    out->current_frame_identity = runtime->current_frame.identity;
    memcpy(out->hash72_tip, runtime->hash72_tip, HHS174_HASH72_LEN + 1u);
    out->vector_object_count = runtime->store.count;
    out->active_suffix_count = runtime->store.active_suffix_count;
    out->has_candidate = runtime->has_candidate;
    out->boot_admitted = runtime->boot_admitted;
    return HHS174_OK;
}

HHS174Status hhs174_receipt_export(const HHS174Runtime *runtime, void *buffer, size_t buffer_size, size_t *out_size) {
    if (!runtime || !out_size) return HHS174_INVALID_ARGUMENT;
    HHS174StatusSnapshot snapshot;
    HHS174Status status = hhs174_status(runtime, &snapshot);
    if (status != HHS174_OK) return status;
    *out_size = sizeof(snapshot);
    if (!buffer || buffer_size < sizeof(snapshot)) return HHS174_RESOURCE_BOUNDED;
    memcpy(buffer, &snapshot, sizeof(snapshot));
    return HHS174_OK;
}
