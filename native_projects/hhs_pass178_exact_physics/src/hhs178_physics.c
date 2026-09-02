#include "../include/hhs178_physics.h"

#include <limits.h>
#include <string.h>

static uint64_t hhs178_fnv1a(const unsigned char *bytes, size_t length) {
    uint64_t hash = UINT64_C(1469598103934665603);
    size_t i;
    for (i = 0U; i < length; ++i) {
        hash ^= bytes[i];
        hash *= UINT64_C(1099511628211);
    }
    return hash;
}

static uint64_t hhs178_gcd_u64(uint64_t a, uint64_t b) {
    while (b != 0U) {
        uint64_t t = a % b;
        a = b;
        b = t;
    }
    return a == 0U ? 1U : a;
}

static HHS178Status hhs178_rational_normalize(HHS178Rational *value) {
    uint64_t an;
    uint64_t ad;
    uint64_t g;
    if (value == NULL || value->den == 0)
        return HHS178_INVALID_ARGUMENT;
    if (value->den < 0) {
        if (value->num == INT64_MIN || value->den == INT64_MIN)
            return HHS178_RANGE_ERROR;
        value->num = -value->num;
        value->den = -value->den;
    }
    an = value->num < 0 ? (uint64_t)(-(value->num + 1)) + 1U : (uint64_t)value->num;
    ad = (uint64_t)value->den;
    g = hhs178_gcd_u64(an, ad);
    value->num /= (int64_t)g;
    value->den /= (int64_t)g;
    return HHS178_OK;
}

static int hhs178_runtime_valid(const HHS178Runtime *runtime) {
    return runtime != NULL &&
           runtime->struct_size == sizeof(*runtime) &&
           runtime->version == HHS178_ABI_VERSION &&
           runtime->open == 1U &&
           runtime->model_count <= HHS178_MAX_MODELS &&
           runtime->native_commit_authority == 0U;
}

static HHS178Model *hhs178_model_mut(HHS178Runtime *runtime, uint32_t handle) {
    uint32_t i;
    if (!hhs178_runtime_valid(runtime))
        return NULL;
    for (i = 0U; i < runtime->model_count; ++i) {
        if (runtime->models[i].model_handle == handle)
            return &runtime->models[i];
    }
    return NULL;
}

static const HHS178Model *hhs178_model_const(const HHS178Runtime *runtime, uint32_t handle) {
    uint32_t i;
    if (!hhs178_runtime_valid(runtime))
        return NULL;
    for (i = 0U; i < runtime->model_count; ++i) {
        if (runtime->models[i].model_handle == handle)
            return &runtime->models[i];
    }
    return NULL;
}

uint32_t hhs178_runtime_version(void) {
    return HHS178_ABI_VERSION;
}

HHS178Status hhs178_runtime_open(HHS178Runtime *runtime) {
    if (runtime == NULL)
        return HHS178_INVALID_ARGUMENT;
    memset(runtime, 0, sizeof(*runtime));
    runtime->struct_size = (uint32_t)sizeof(*runtime);
    runtime->version = HHS178_ABI_VERSION;
    runtime->open = 1U;
    runtime->native_commit_authority = 0U;
    return HHS178_OK;
}

HHS178Status hhs178_runtime_close(HHS178Runtime *runtime) {
    if (runtime == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (runtime->struct_size != sizeof(*runtime) ||
        runtime->version != HHS178_ABI_VERSION)
        return HHS178_INVARIANT_ERROR;
    runtime->open = 0U;
    return HHS178_OK;
}

HHS178Status hhs178_source_ingest_exact(
    const void *source,
    size_t source_len,
    HHS178SourceIdentity *out_identity
) {
    if ((source == NULL && source_len != 0U) || out_identity == NULL)
        return HHS178_INVALID_ARGUMENT;
    out_identity->byte_count = (uint64_t)source_len;
    out_identity->fingerprint64 = hhs178_fnv1a((const unsigned char *)source, source_len);
    out_identity->byte_preserving = 1U;
    out_identity->canonical_mutation_authority = 0U;
    return HHS178_OK;
}

HHS178Status hhs178_model_register(
    HHS178Runtime *runtime,
    uint32_t model_kind,
    const HHS178SourceIdentity *source_identity,
    HHS178Model *out_model
) {
    HHS178Model *model;
    if (!hhs178_runtime_valid(runtime) || source_identity == NULL || out_model == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (model_kind < HHS178_MODEL_RELATIVISTIC_FREE_PARTICLE ||
        model_kind > HHS178_MODEL_HARMONICODE_MEMBRANE)
        return HHS178_RANGE_ERROR;
    if (runtime->model_count >= HHS178_MAX_MODELS)
        return HHS178_CAPACITY_ERROR;
    model = &runtime->models[runtime->model_count];
    memset(model, 0, sizeof(*model));
    model->struct_size = (uint32_t)sizeof(*model);
    model->version = HHS178_ABI_VERSION;
    model->model_handle = runtime->model_count + 1U;
    model->model_kind = model_kind;
    model->source_fingerprint64 = source_identity->fingerprint64;
    model->fixed_step.num = 1;
    model->fixed_step.den = 1;
    model->registered = 1U;
    model->native_commit_authority = 0U;
    ++runtime->model_count;
    *out_model = *model;
    return HHS178_OK;
}

HHS178Status hhs178_constraint_bind(
    HHS178Runtime *runtime,
    uint32_t model_handle,
    uint64_t constraint_graph_fingerprint64
) {
    HHS178Model *model = hhs178_model_mut(runtime, model_handle);
    if (model == NULL)
        return HHS178_INVALID_ARGUMENT;
    model->constraint_graph_fingerprint64 = constraint_graph_fingerprint64;
    return HHS178_OK;
}

HHS178Status hhs178_parameter_set_exact(
    HHS178Runtime *runtime,
    uint32_t model_handle,
    HHS178Rational fixed_step
) {
    HHS178Model *model = hhs178_model_mut(runtime, model_handle);
    HHS178Status status;
    if (model == NULL)
        return HHS178_INVALID_ARGUMENT;
    status = hhs178_rational_normalize(&fixed_step);
    if (status != HHS178_OK)
        return status;
    if (fixed_step.num <= 0)
        return HHS178_RANGE_ERROR;
    model->fixed_step = fixed_step;
    return HHS178_OK;
}

HHS178Status hhs178_initial_state_admit(
    const HHS178Runtime *runtime,
    uint32_t model_handle,
    const HHS178Rational *scalars,
    uint32_t scalar_count,
    HHS178State *out_candidate
) {
    uint32_t i;
    if (!hhs178_runtime_valid(runtime) || scalars == NULL || out_candidate == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (hhs178_model_const(runtime, model_handle) == NULL)
        return HHS178_RANGE_ERROR;
    if (scalar_count == 0U || scalar_count > HHS178_MAX_SCALARS)
        return HHS178_RANGE_ERROR;
    memset(out_candidate, 0, sizeof(*out_candidate));
    out_candidate->struct_size = (uint32_t)sizeof(*out_candidate);
    out_candidate->version = HHS178_ABI_VERSION;
    out_candidate->model_handle = model_handle;
    out_candidate->scalar_count = scalar_count;
    out_candidate->step_index = 0U;
    out_candidate->native_commit_authority = 0U;
    for (i = 0U; i < scalar_count; ++i) {
        HHS178Rational v = scalars[i];
        HHS178Status status = hhs178_rational_normalize(&v);
        if (status != HHS178_OK)
            return status;
        out_candidate->scalars[i] = v;
    }
    return HHS178_OK;
}

HHS178Status hhs178_step_candidate(
    const HHS178Runtime *runtime,
    const HHS178State *prior,
    HHS178State *out_candidate
) {
    uint32_t i;
    const HHS178Model *model;
    if (!hhs178_runtime_valid(runtime) || prior == NULL || out_candidate == NULL)
        return HHS178_INVALID_ARGUMENT;
    model = hhs178_model_const(runtime, prior->model_handle);
    if (model == NULL)
        return HHS178_RANGE_ERROR;
    if (prior->struct_size != sizeof(*prior) ||
        prior->version != HHS178_ABI_VERSION ||
        prior->scalar_count == 0U ||
        prior->scalar_count > HHS178_MAX_SCALARS ||
        prior->native_commit_authority != 0U)
        return HHS178_INVARIANT_ERROR;
    *out_candidate = *prior;
    out_candidate->step_index = prior->step_index + 1U;
    out_candidate->candidate_validated = 0U;
    out_candidate->vm81_admitted = 0U;
    if (model->model_kind == HHS178_MODEL_RELATIVISTIC_FREE_PARTICLE &&
        prior->scalar_count >= 8U) {
        /* Convention: x0..x3 then u0..u3; exact free proper-time step. */
        for (i = 0U; i < 4U; ++i) {
            HHS178Rational x = prior->scalars[i];
            HHS178Rational u = prior->scalars[4U + i];
            __int128 num =
                (__int128)x.num * u.den * model->fixed_step.den +
                (__int128)u.num * model->fixed_step.num * x.den;
            __int128 den =
                (__int128)x.den * u.den * model->fixed_step.den;
            if (num > INT64_MAX || num < INT64_MIN || den > INT64_MAX || den <= 0)
                return HHS178_RANGE_ERROR;
            out_candidate->scalars[i].num = (int64_t)num;
            out_candidate->scalars[i].den = (int64_t)den;
            if (hhs178_rational_normalize(&out_candidate->scalars[i]) != HHS178_OK)
                return HHS178_RANGE_ERROR;
        }
    }
    return HHS178_OK;
}

HHS178Status hhs178_step_validate(HHS178State *candidate) {
    uint32_t i;
    if (candidate == NULL ||
        candidate->struct_size != sizeof(*candidate) ||
        candidate->version != HHS178_ABI_VERSION ||
        candidate->scalar_count == 0U ||
        candidate->scalar_count > HHS178_MAX_SCALARS ||
        candidate->native_commit_authority != 0U)
        return HHS178_INVALID_ARGUMENT;
    for (i = 0U; i < candidate->scalar_count; ++i) {
        if (candidate->scalars[i].den <= 0)
            return HHS178_INVARIANT_ERROR;
    }
    candidate->candidate_validated = 1U;
    return HHS178_OK;
}

HHS178Status hhs178_step_commit(
    HHS178Runtime *runtime,
    HHS178State *candidate,
    uint32_t inherited_vm81_admission_verified
) {
    if (!hhs178_runtime_valid(runtime) || candidate == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (candidate->candidate_validated != 1U)
        return HHS178_INVARIANT_ERROR;
    if (inherited_vm81_admission_verified != 1U)
        return HHS178_AUTHORITY_REQUIRED;
    candidate->vm81_admitted = 1U;
    runtime->authoritative_clock = (uint32_t)candidate->step_index;
    return HHS178_OK;
}

HHS178Status hhs178_snapshot_vm81(
    const HHS178State *state,
    HHS178State *out_snapshot
) {
    if (state == NULL || out_snapshot == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (state->vm81_admitted != 1U)
        return HHS178_AUTHORITY_REQUIRED;
    *out_snapshot = *state;
    return HHS178_OK;
}

HHS178Status hhs178_render_packet_project(
    const HHS178State *state,
    HHS178RenderPacket *out_packet
) {
    size_t length;
    if (state == NULL || out_packet == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (state->vm81_admitted != 1U)
        return HHS178_AUTHORITY_REQUIRED;
    memset(out_packet, 0, sizeof(*out_packet));
    out_packet->struct_size = (uint32_t)sizeof(*out_packet);
    out_packet->version = HHS178_ABI_VERSION;
    out_packet->step_index = state->step_index;
    if (state->scalar_count >= 4U) {
        uint32_t i;
        out_packet->world_time_num = state->scalars[0].num;
        out_packet->world_time_den = state->scalars[0].den;
        for (i = 0U; i < 3U; ++i) {
            __int128 scaled = (__int128)state->scalars[i + 1U].num << 32;
            out_packet->position_q32_32[i] =
                (int64_t)(scaled / state->scalars[i + 1U].den);
        }
    } else {
        out_packet->world_time_den = 1;
    }
    out_packet->phase_mod_72 = (uint32_t)(state->step_index % 72U);
    out_packet->immutable_packet = 1U;
    out_packet->renderer_feedback_authority = 0U;
    out_packet->simulation_mutation_authority = 0U;
    length = offsetof(HHS178RenderPacket, packet_fingerprint64);
    out_packet->packet_fingerprint64 =
        hhs178_fnv1a((const unsigned char *)out_packet, length);
    return HHS178_OK;
}

HHS178Status hhs178_replay_open(const HHS178State *initial, HHS178State *cursor) {
    if (initial == NULL || cursor == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (initial->vm81_admitted != 1U || initial->step_index != 0U)
        return HHS178_INVARIANT_ERROR;
    *cursor = *initial;
    return HHS178_OK;
}

HHS178Status hhs178_replay_step(const HHS178State *record, HHS178State *cursor) {
    if (record == NULL || cursor == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (record->vm81_admitted != 1U ||
        record->step_index != cursor->step_index + 1U ||
        record->model_handle != cursor->model_handle)
        return HHS178_INVARIANT_ERROR;
    *cursor = *record;
    return HHS178_OK;
}

HHS178Status hhs178_measure_registered(
    const HHS178State *state,
    uint64_t registered_measurement_authority_token,
    uint32_t *out_index
) {
    if (state == NULL || out_index == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (registered_measurement_authority_token == 0U)
        return HHS178_AUTHORITY_REQUIRED;
    return HHS178_UNSUPPORTED;
}

HHS178Status hhs178_receipt_export(
    const HHS178State *state,
    uint64_t *out_receipt_fingerprint64
) {
    if (state == NULL || out_receipt_fingerprint64 == NULL)
        return HHS178_INVALID_ARGUMENT;
    if (state->vm81_admitted != 1U)
        return HHS178_AUTHORITY_REQUIRED;
    *out_receipt_fingerprint64 = hhs178_fnv1a(
        (const unsigned char *)state,
        offsetof(HHS178State, scalars) +
            state->scalar_count * sizeof(HHS178Rational)
    );
    return HHS178_OK;
}
