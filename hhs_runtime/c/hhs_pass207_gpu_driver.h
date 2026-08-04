#ifndef HHS_PASS207_GPU_DRIVER_H
#define HHS_PASS207_GPU_DRIVER_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define HHS_PASS207_API __declspec(dllexport)
#else
#define HHS_PASS207_API __attribute__((visibility("default")))
#endif

#define HHS_PASS207_API_VERSION 1u
#define HHS_PASS207_CELL_COUNT 81u
#define HHS_PASS207_BITS_PER_CELL 64u
#define HHS_PASS207_STATE_BITS 5184u
#define HHS_PASS207_LOGICAL_HYPERTHREADS 64u
#define HHS_PASS207_LOGICAL_LANES 5184u
#define HHS_PASS207_PHASE_DIMENSION 72u
#define HHS_PASS207_CONTROL_COUNT 243u
#define HHS_PASS207_Q_COUNT 1259712u
#define HHS_PASS207_PROJECTION_CHANNELS 32u
#define HHS_PASS207_CACHE_KEY_BYTES 32u
#define HHS_PASS207_DEFAULT_WORKGROUP 64u

typedef enum {
    HHS_PASS207_BACKEND_AUTO = 0,
    HHS_PASS207_BACKEND_CPU_REFERENCE = 1,
    HHS_PASS207_BACKEND_OPENCL = 2
} HHSPass207Backend;

typedef enum {
    HHS_PASS207_OK = 0,
    HHS_PASS207_ERR_INVALID_ARGUMENT = 1,
    HHS_PASS207_ERR_OUT_OF_MEMORY = 2,
    HHS_PASS207_ERR_BACKEND_UNAVAILABLE = 3,
    HHS_PASS207_ERR_BACKEND_FAILURE = 4,
    HHS_PASS207_ERR_HYDRATION_MISMATCH = 5,
    HHS_PASS207_ERR_CPU_VERIFICATION = 6,
    HHS_PASS207_ERR_CACHE_MISS = 7,
    HHS_PASS207_ERR_BUFFER_TOO_SMALL = 8
} HHSPass207Status;

typedef enum {
    HHS_PASS207_CACHE_STATE_SOA = 1,
    HHS_PASS207_CACHE_PROJECTION_SOA = 2,
    HHS_PASS207_CACHE_DELTA_CSR = 3,
    HHS_PASS207_CACHE_HYDRATION_CSR = 4,
    HHS_PASS207_CACHE_CHILD_STATE_SOA = 5,
    HHS_PASS207_CACHE_CHILD_PROJECTION_SOA = 6,
    HHS_PASS207_CACHE_VECTOR_MATRIX = 7
} HHSPass207CacheKind;

typedef struct HHSPass207GPUDriver HHSPass207GPUDriver;

typedef struct {
    uint32_t api_version;
    HHSPass207Backend requested_backend;
    uint32_t device_index;
    uint64_t cache_capacity_bytes;
    uint32_t cache_capacity_entries;
    uint8_t verify_against_cpu;
    uint8_t require_physical_gpu;
    uint8_t reserved[6];
} HHSPass207GPUConfig;

typedef struct {
    uint32_t batch_size;
    const uint64_t* state_soa;
    const uint32_t* projection_soa;
    const uint32_t* delta_offsets;
    const uint32_t* delta_cells;
    const uint8_t* delta_controls;
    const uint64_t* delta_xor_masks;
    const uint32_t* hydration_offsets;
    const uint32_t* hydration_q;
    uint32_t delta_count;
    uint32_t hydration_count;
    const uint8_t* input_cache_key;
    const uint8_t* output_cache_key;
    uint8_t reuse_cached_inputs;
    uint8_t retain_outputs;
    uint8_t reserved[6];
} HHSPass207Batch;

typedef struct {
    uint64_t* child_state_soa;
    uint32_t* child_projection_soa;
    uint8_t* frontier_soa;
    uint8_t* hydration_valid;
} HHSPass207BatchOutput;

typedef struct {
    HHSPass207Backend selected_backend;
    uint8_t physical_gpu;
    uint8_t deterministic_integer_only;
    uint8_t verified_against_cpu;
    uint8_t cache_input_hit;
    uint8_t cache_output_retained;
    uint8_t reserved[3];
    uint32_t device_index;
    uint32_t platform_count;
    uint32_t device_count;
    uint32_t logical_hyperthreads_per_cell;
    uint32_t logical_lanes_per_batch;
    uint32_t physical_workgroup_size;
    uint8_t stable_lane_identity;
    uint8_t disjoint_lane_writes;
    uint8_t canonical_reduction_order;
    uint8_t reserved_topology;
    uint64_t dispatch_count;
    uint64_t vector_dispatch_count;
    uint64_t input_bytes_uploaded;
    uint64_t output_bytes_downloaded;
    uint64_t cache_hits;
    uint64_t cache_misses;
    uint64_t cache_evictions;
    uint64_t cache_resident_bytes;
    uint32_t cache_entries;
    char backend_name[32];
    char device_name[128];
    char last_error[256];
} HHSPass207GPUStatus;

HHS_PASS207_API uint16_t hhs_pass207_lane_address(
    uint8_t cell,
    uint8_t hyperthread,
    uint8_t* ok
);
HHS_PASS207_API uint8_t hhs_pass207_lane_decode(
    uint16_t lane,
    uint8_t* out_cell,
    uint8_t* out_hyperthread
);
HHS_PASS207_API uint8_t hhs_pass207_lane_phase_coordinate(
    uint16_t lane,
    uint8_t* out_phase_row,
    uint8_t* out_phase_column
);
HHS_PASS207_API HHSPass207GPUConfig hhs_pass207_gpu_default_config(void);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_create(
    const HHSPass207GPUConfig* config,
    HHSPass207GPUDriver** out_driver
);
HHS_PASS207_API void hhs_pass207_gpu_destroy(HHSPass207GPUDriver* driver);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_get_status(
    const HHSPass207GPUDriver* driver,
    HHSPass207GPUStatus* out_status
);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_dispatch(
    HHSPass207GPUDriver* driver,
    const HHSPass207Batch* batch,
    HHSPass207BatchOutput* output
);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_vector_distance72(
    HHSPass207GPUDriver* driver,
    const uint8_t query[72],
    const uint8_t* candidate_matrix,
    uint32_t candidate_count,
    const uint8_t* matrix_cache_key,
    uint8_t reuse_cached_matrix,
    uint32_t* out_distances
);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_cache_store(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind,
    const void* data,
    size_t size
);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_cache_load(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind,
    void* out_data,
    size_t capacity,
    size_t* out_size
);
HHS_PASS207_API HHSPass207Status hhs_pass207_gpu_cache_remove(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind
);
HHS_PASS207_API void hhs_pass207_gpu_cache_clear(HHSPass207GPUDriver* driver);
HHS_PASS207_API const char* hhs_pass207_gpu_status_string(HHSPass207Status status);

#ifdef __cplusplus
}
#endif

#endif
