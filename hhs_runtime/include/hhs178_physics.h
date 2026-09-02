#ifndef HHS178_PHYSICS_H
#define HHS178_PHYSICS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS178_ABI_VERSION UINT32_C(0x00010000)
#define HHS178_MAX_SCALARS 81U
#define HHS178_MAX_MODELS 16U
#define HHS178_HASH216_CHARS 216U

typedef enum HHS178Status {
    HHS178_OK = 0,
    HHS178_INVALID_ARGUMENT = 1,
    HHS178_RANGE_ERROR = 2,
    HHS178_INVARIANT_ERROR = 3,
    HHS178_CAPACITY_ERROR = 4,
    HHS178_AUTHORITY_REQUIRED = 5,
    HHS178_UNSUPPORTED = 6
} HHS178Status;

typedef enum HHS178ModelKind {
    HHS178_MODEL_RELATIVISTIC_FREE_PARTICLE = 1,
    HHS178_MODEL_QUANTUM_CAYLEY_NUCLEUS = 2,
    HHS178_MODEL_HARMONICODE_MEMBRANE = 3
} HHS178ModelKind;

typedef struct HHS178Rational {
    int64_t num;
    int64_t den;
} HHS178Rational;

typedef struct HHS178Complex {
    HHS178Rational real;
    HHS178Rational imag;
} HHS178Complex;

typedef struct HHS178SourceIdentity {
    uint64_t byte_count;
    uint64_t fingerprint64;
    uint32_t byte_preserving;
    uint32_t canonical_mutation_authority;
} HHS178SourceIdentity;

typedef struct HHS178Model {
    uint32_t struct_size;
    uint32_t version;
    uint32_t model_handle;
    uint32_t model_kind;
    uint64_t source_fingerprint64;
    uint64_t constraint_graph_fingerprint64;
    HHS178Rational fixed_step;
    uint32_t registered;
    uint32_t native_commit_authority;
} HHS178Model;

typedef struct HHS178State {
    uint32_t struct_size;
    uint32_t version;
    uint32_t model_handle;
    uint32_t scalar_count;
    uint64_t step_index;
    HHS178Rational scalars[HHS178_MAX_SCALARS];
    uint32_t candidate_validated;
    uint32_t vm81_admitted;
    uint32_t native_commit_authority;
} HHS178State;

typedef struct HHS178RenderPacket {
    uint32_t struct_size;
    uint32_t version;
    uint64_t step_index;
    int64_t world_time_num;
    int64_t world_time_den;
    int64_t position_q32_32[3];
    uint32_t phase_mod_72;
    uint32_t immutable_packet;
    uint32_t renderer_feedback_authority;
    uint32_t simulation_mutation_authority;
    uint64_t packet_fingerprint64;
} HHS178RenderPacket;

typedef struct HHS178Runtime {
    uint32_t struct_size;
    uint32_t version;
    uint32_t open;
    uint32_t model_count;
    uint32_t authoritative_clock;
    uint32_t native_commit_authority;
    HHS178Model models[HHS178_MAX_MODELS];
} HHS178Runtime;

uint32_t hhs178_runtime_version(void);
HHS178Status hhs178_runtime_open(HHS178Runtime *runtime);
HHS178Status hhs178_runtime_close(HHS178Runtime *runtime);
HHS178Status hhs178_source_ingest_exact(
    const void *source,
    size_t source_len,
    HHS178SourceIdentity *out_identity
);
HHS178Status hhs178_model_register(
    HHS178Runtime *runtime,
    uint32_t model_kind,
    const HHS178SourceIdentity *source_identity,
    HHS178Model *out_model
);
HHS178Status hhs178_constraint_bind(
    HHS178Runtime *runtime,
    uint32_t model_handle,
    uint64_t constraint_graph_fingerprint64
);
HHS178Status hhs178_parameter_set_exact(
    HHS178Runtime *runtime,
    uint32_t model_handle,
    HHS178Rational fixed_step
);
HHS178Status hhs178_initial_state_admit(
    const HHS178Runtime *runtime,
    uint32_t model_handle,
    const HHS178Rational *scalars,
    uint32_t scalar_count,
    HHS178State *out_candidate
);
HHS178Status hhs178_step_candidate(
    const HHS178Runtime *runtime,
    const HHS178State *prior,
    HHS178State *out_candidate
);
HHS178Status hhs178_step_validate(HHS178State *candidate);
HHS178Status hhs178_step_commit(
    HHS178Runtime *runtime,
    HHS178State *candidate,
    uint32_t inherited_vm81_admission_verified
);
HHS178Status hhs178_snapshot_vm81(
    const HHS178State *state,
    HHS178State *out_snapshot
);
HHS178Status hhs178_render_packet_project(
    const HHS178State *state,
    HHS178RenderPacket *out_packet
);
HHS178Status hhs178_replay_open(const HHS178State *initial, HHS178State *cursor);
HHS178Status hhs178_replay_step(const HHS178State *record, HHS178State *cursor);
HHS178Status hhs178_measure_registered(
    const HHS178State *state,
    uint64_t registered_measurement_authority_token,
    uint32_t *out_index
);
HHS178Status hhs178_receipt_export(
    const HHS178State *state,
    uint64_t *out_receipt_fingerprint64
);

#ifdef __cplusplus
}
#endif
#endif
