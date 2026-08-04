#include "hhs_pass207_gpu_driver.h"

#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#if defined(_WIN32)
#include <windows.h>
#else
#include <dlfcn.h>
#endif

/* Minimal OpenCL 1.2 declarations keep the core driver build independent of SDK headers. */
typedef int32_t cl_int;
typedef uint32_t cl_uint;
typedef uint64_t cl_ulong;
typedef uint64_t cl_bitfield;
typedef cl_bitfield cl_device_type;
typedef cl_bitfield cl_mem_flags;
typedef cl_uint cl_bool;
typedef intptr_t cl_context_properties;
typedef struct _cl_platform_id* cl_platform_id;
typedef struct _cl_device_id* cl_device_id;
typedef struct _cl_context* cl_context;
typedef struct _cl_command_queue* cl_command_queue;
typedef struct _cl_mem* cl_mem;
typedef struct _cl_program* cl_program;
typedef struct _cl_kernel* cl_kernel;
typedef struct _cl_event* cl_event;

#define CL_SUCCESS 0
#define CL_TRUE 1u
#define CL_DEVICE_TYPE_GPU (1ULL << 2)
#define CL_MEM_READ_WRITE (1ULL << 0)
#define CL_MEM_WRITE_ONLY (1ULL << 1)
#define CL_MEM_READ_ONLY (1ULL << 2)
#define CL_DEVICE_MAX_WORK_GROUP_SIZE 0x1004u
#define CL_DEVICE_NAME 0x102Bu
#define CL_PROGRAM_BUILD_LOG 0x1183u

#if defined(_WIN32)
typedef HMODULE HHSOpenCLLibrary;
#else
typedef void* HHSOpenCLLibrary;
#endif

typedef cl_int (*PFN_clGetPlatformIDs)(cl_uint, cl_platform_id*, cl_uint*);
typedef cl_int (*PFN_clGetDeviceIDs)(cl_platform_id, cl_device_type, cl_uint, cl_device_id*, cl_uint*);
typedef cl_int (*PFN_clGetDeviceInfo)(cl_device_id, cl_uint, size_t, void*, size_t*);
typedef cl_context (*PFN_clCreateContext)(const cl_context_properties*, cl_uint, const cl_device_id*, void (*)(const char*, const void*, size_t, void*), void*, cl_int*);
typedef cl_command_queue (*PFN_clCreateCommandQueue)(cl_context, cl_device_id, cl_bitfield, cl_int*);
typedef cl_program (*PFN_clCreateProgramWithSource)(cl_context, cl_uint, const char**, const size_t*, cl_int*);
typedef cl_int (*PFN_clBuildProgram)(cl_program, cl_uint, const cl_device_id*, const char*, void (*)(cl_program, void*), void*);
typedef cl_int (*PFN_clGetProgramBuildInfo)(cl_program, cl_device_id, cl_uint, size_t, void*, size_t*);
typedef cl_kernel (*PFN_clCreateKernel)(cl_program, const char*, cl_int*);
typedef cl_mem (*PFN_clCreateBuffer)(cl_context, cl_mem_flags, size_t, void*, cl_int*);
typedef cl_int (*PFN_clSetKernelArg)(cl_kernel, cl_uint, size_t, const void*);
typedef cl_int (*PFN_clEnqueueWriteBuffer)(cl_command_queue, cl_mem, cl_bool, size_t, size_t, const void*, cl_uint, const cl_event*, cl_event*);
typedef cl_int (*PFN_clEnqueueReadBuffer)(cl_command_queue, cl_mem, cl_bool, size_t, size_t, void*, cl_uint, const cl_event*, cl_event*);
typedef cl_int (*PFN_clEnqueueNDRangeKernel)(cl_command_queue, cl_kernel, cl_uint, const size_t*, const size_t*, const size_t*, cl_uint, const cl_event*, cl_event*);
typedef cl_int (*PFN_clFinish)(cl_command_queue);
typedef cl_int (*PFN_clReleaseMemObject)(cl_mem);
typedef cl_int (*PFN_clReleaseKernel)(cl_kernel);
typedef cl_int (*PFN_clReleaseProgram)(cl_program);
typedef cl_int (*PFN_clReleaseCommandQueue)(cl_command_queue);
typedef cl_int (*PFN_clReleaseContext)(cl_context);

typedef struct {
    HHSOpenCLLibrary library;
    PFN_clGetPlatformIDs GetPlatformIDs;
    PFN_clGetDeviceIDs GetDeviceIDs;
    PFN_clGetDeviceInfo GetDeviceInfo;
    PFN_clCreateContext CreateContext;
    PFN_clCreateCommandQueue CreateCommandQueue;
    PFN_clCreateProgramWithSource CreateProgramWithSource;
    PFN_clBuildProgram BuildProgram;
    PFN_clGetProgramBuildInfo GetProgramBuildInfo;
    PFN_clCreateKernel CreateKernel;
    PFN_clCreateBuffer CreateBuffer;
    PFN_clSetKernelArg SetKernelArg;
    PFN_clEnqueueWriteBuffer EnqueueWriteBuffer;
    PFN_clEnqueueReadBuffer EnqueueReadBuffer;
    PFN_clEnqueueNDRangeKernel EnqueueNDRangeKernel;
    PFN_clFinish Finish;
    PFN_clReleaseMemObject ReleaseMemObject;
    PFN_clReleaseKernel ReleaseKernel;
    PFN_clReleaseProgram ReleaseProgram;
    PFN_clReleaseCommandQueue ReleaseCommandQueue;
    PFN_clReleaseContext ReleaseContext;
} HHSOpenCLAPI;

typedef struct {
    uint8_t key[HHS_PASS207_CACHE_KEY_BYTES];
    HHSPass207CacheKind kind;
    uint8_t* host_data;
    size_t size;
    cl_mem device_buffer;
    uint64_t stamp;
    uint8_t occupied;
} HHSCacheEntry;

struct HHSPass207GPUDriver {
    HHSPass207GPUConfig config;
    HHSPass207GPUStatus status;
    atomic_flag lock;
    uint64_t stamp;
    HHSCacheEntry* cache;
    uint32_t cache_slots;
    HHSOpenCLAPI cl;
    cl_platform_id platform;
    cl_device_id device;
    cl_context context;
    cl_command_queue queue;
    cl_program program;
    cl_kernel apply_kernel;
    cl_kernel pack_kernel;
    cl_kernel projection_kernel;
    cl_kernel hydration_kernel;
    cl_kernel vector_kernel;
};

static const char* HHS_PASS207_OPENCL_SOURCE_PART1 =
"inline ulong hhs_rotl64(ulong v, uint s) { s &= 63u; return s == 0u ? v : ((v << s) | (v >> (64u - s))); }\n"
"inline ulong hhs_rotr64(ulong v, uint s) { s &= 63u; return s == 0u ? v : ((v >> s) | (v << (64u - s))); }\n"
"inline uint hhs_fold32(ulong v) { v ^= v >> 33; v *= (ulong)0xff51afd7ed558ccdUL; v ^= v >> 33; v *= (ulong)0xc4ceb9fe1a85ec53UL; v ^= v >> 33; return (uint)(v ^ (v >> 32)); }\n"
"inline uint hhs_projection_word(__global const ulong* state, uint batch_size, uint batch, uint channel, uint cell) {\n"
"  uint left = (cell + 80u) % 81u; uint right = (cell + 1u) % 81u; uint vertical = (cell + 9u) % 81u;\n"
"  ulong mixed = state[cell * batch_size + batch];\n"
"  mixed ^= hhs_rotl64(state[left * batch_size + batch], (channel + 1u) & 63u);\n"
"  mixed ^= hhs_rotr64(state[right * batch_size + batch], (channel * 3u + 5u) & 63u);\n"
"  mixed ^= hhs_rotl64(state[vertical * batch_size + batch], (channel * 5u + 7u) & 63u);\n"
"  mixed ^= ((ulong)(channel + 1u) * (ulong)0x9E3779B97F4A7C15UL);\n"
"  mixed ^= ((ulong)(cell + 1u) * (ulong)0x517cc1b727220a95UL); return hhs_fold32(mixed);\n"
"}\n"
"__kernel void hhs_vm81_hyperthreads(__global const ulong* parent, __global const uint* offsets, __global const uint* cells, __global const uchar* controls, __global const ulong* masks, uint batch_size, __global uchar* lane_bits, __global uchar* lane_frontier) {\n"
"  uint group = get_group_id(0); uint thread = get_local_id(0); uint batch = group / 81u; uint cell = group % 81u; if (batch >= batch_size || thread >= 64u) return;\n"
"  ulong parent_word = parent[cell * batch_size + batch]; uchar bit = (uchar)((parent_word >> thread) & (ulong)1); uchar affected = (uchar)0;\n"
"  uint start = offsets[batch]; uint end = offsets[batch + 1u];\n"
"  for (uint i = start; i < end; ++i) { uint changed = cells[i]; if (changed == cell && (masks[i] & ((ulong)1 << thread))) bit ^= (uchar)1;\n"
"    if (cell == changed || cell == ((changed + 1u) % 81u) || cell == ((changed + 80u) % 81u) || cell == ((changed + 72u) % 81u)) affected = (uchar)1; (void)controls[i]; }\n"
"  uint lane = batch * 5184u + cell * 64u + thread; lane_bits[lane] = bit; lane_frontier[lane] = affected;\n"
"}\n"
"__kernel void hhs_pack_vm81_state(__global const uchar* lane_bits, __global const uchar* lane_frontier, uint batch_size, __global ulong* child, __global uchar* frontier) {\n"
"  uint index = get_global_id(0); uint total = batch_size * 81u; if (index >= total) return; uint batch = index / 81u; uint cell = index % 81u; uint base = batch * 5184u + cell * 64u; ulong word = (ulong)0;\n"
"  for (uint thread = 0u; thread < 64u; ++thread) if (lane_bits[base + thread]) word |= ((ulong)1 << thread);\n"
"  child[cell * batch_size + batch] = word; frontier[cell * batch_size + batch] = lane_frontier[base];\n"
"}\n";

static const char* HHS_PASS207_OPENCL_SOURCE_PART2 =
"__kernel void hhs_project_sparse(__global const ulong* child, __global const uint* parent_projection, __global const uchar* frontier, uint batch_size, __global uint* child_projection) {\n"
"  uint index = get_global_id(0); uint total = batch_size * 81u * 32u; if (index >= total) return;\n"
"  uint batch = index % batch_size; uint mapped = index / batch_size; uint cell = mapped % 81u; uint channel = mapped / 81u;\n"
"  uint out_index = (channel * 81u + cell) * batch_size + batch;\n"
"  child_projection[out_index] = frontier[cell * batch_size + batch] ? hhs_projection_word(child, batch_size, batch, channel, cell) : parent_projection[out_index];\n"
"}\n"
"__kernel void hhs_validate_hydration(__global const uint* hydration_offsets, __global const uint* hydration_q, uint hydration_count, __global const uint* delta_offsets, __global const uint* delta_cells, __global const uchar* delta_controls, __global const ulong* delta_masks, uint batch_size, __global uchar* valid) {\n"
"  uint index = get_global_id(0); if (index >= hydration_count) return; uint batch = 0u;\n"
"  while (batch + 1u < batch_size && index >= hydration_offsets[batch + 1u]) ++batch;\n"
"  uint q = hydration_q[index]; uchar ok = (uchar)0; if (q < 1259712u) { uint s = q / 243u; uint g = q % 243u; uint cell = s / 64u; uint bit = s % 64u;\n"
"    for (uint i = delta_offsets[batch]; i < delta_offsets[batch + 1u]; ++i) if (delta_cells[i] == cell && (uint)delta_controls[i] == g && (delta_masks[i] & ((ulong)1 << bit))) { ok = (uchar)1; break; } } valid[index] = ok;\n"
"}\n"
"__kernel void hhs_vector_distance72(__global const uchar* query, __global const uchar* candidates, uint count, __global uint* distances) {\n"
"  uint candidate = get_global_id(0); if (candidate >= count) return; uint total = 0u; uint base = candidate * 72u;\n"
"  for (uint i = 0u; i < 72u; ++i) { uint a = (uint)query[i]; uint b = (uint)candidates[base + i]; uint d = a > b ? a - b : b - a; total += d < (72u - d) ? d : (72u - d); } distances[candidate] = total;\n"
"}\n";

static void hhs_lock(HHSPass207GPUDriver* driver) {
    while (atomic_flag_test_and_set_explicit(&driver->lock, memory_order_acquire)) {
    }
}

static void hhs_unlock(HHSPass207GPUDriver* driver) {
    atomic_flag_clear_explicit(&driver->lock, memory_order_release);
}

static void hhs_copy_text(char* destination, size_t capacity, const char* source) {
    if (destination == NULL || capacity == 0u) {
        return;
    }
    if (source == NULL) {
        destination[0] = '\0';
        return;
    }
    (void)snprintf(destination, capacity, "%s", source);
}

static void hhs_set_error(HHSPass207GPUDriver* driver, const char* message) {
    if (driver != NULL) {
        hhs_copy_text(driver->status.last_error, sizeof(driver->status.last_error), message);
    }
}

static uint64_t hhs_rotl64(uint64_t value, uint32_t shift) {
    shift &= 63u;
    return shift == 0u ? value : ((value << shift) | (value >> (64u - shift)));
}

static uint64_t hhs_rotr64(uint64_t value, uint32_t shift) {
    shift &= 63u;
    return shift == 0u ? value : ((value >> shift) | (value << (64u - shift)));
}

static uint32_t hhs_fold32(uint64_t value) {
    value ^= value >> 33;
    value *= UINT64_C(0xff51afd7ed558ccd);
    value ^= value >> 33;
    value *= UINT64_C(0xc4ceb9fe1a85ec53);
    value ^= value >> 33;
    return (uint32_t)(value ^ (value >> 32));
}

static uint32_t hhs_projection_word_soa(
    const uint64_t* state,
    uint32_t batch_size,
    uint32_t batch,
    uint32_t channel,
    uint32_t cell
) {
    const uint32_t left = (cell + 80u) % 81u;
    const uint32_t right = (cell + 1u) % 81u;
    const uint32_t vertical = (cell + 9u) % 81u;
    uint64_t mixed = state[(size_t)cell * batch_size + batch];
    mixed ^= hhs_rotl64(state[(size_t)left * batch_size + batch], (channel + 1u) & 63u);
    mixed ^= hhs_rotr64(state[(size_t)right * batch_size + batch], (channel * 3u + 5u) & 63u);
    mixed ^= hhs_rotl64(state[(size_t)vertical * batch_size + batch], (channel * 5u + 7u) & 63u);
    mixed ^= ((uint64_t)(channel + 1u) * UINT64_C(0x9E3779B97F4A7C15));
    mixed ^= ((uint64_t)(cell + 1u) * UINT64_C(0x517cc1b727220a95));
    return hhs_fold32(mixed);
}

static uint8_t hhs_keys_equal(const uint8_t* a, const uint8_t* b) {
    return (uint8_t)(a != NULL && b != NULL && memcmp(a, b, HHS_PASS207_CACHE_KEY_BYTES) == 0);
}

static uint8_t hhs_key_present(const uint8_t* key) {
    uint8_t aggregate = 0u;
    uint32_t index;
    if (key == NULL) {
        return 0u;
    }
    for (index = 0u; index < HHS_PASS207_CACHE_KEY_BYTES; ++index) {
        aggregate |= key[index];
    }
    return (uint8_t)(aggregate != 0u);
}

static void hhs_release_cache_entry(HHSPass207GPUDriver* driver, HHSCacheEntry* entry) {
    if (entry == NULL || entry->occupied == 0u) {
        return;
    }
    if (entry->device_buffer != NULL && driver->cl.ReleaseMemObject != NULL) {
        (void)driver->cl.ReleaseMemObject(entry->device_buffer);
    }
    free(entry->host_data);
    if (driver->status.cache_resident_bytes >= entry->size) {
        driver->status.cache_resident_bytes -= entry->size;
    } else {
        driver->status.cache_resident_bytes = 0u;
    }
    if (driver->status.cache_entries > 0u) {
        driver->status.cache_entries -= 1u;
    }
    memset(entry, 0, sizeof(*entry));
}

static HHSCacheEntry* hhs_find_cache_entry(
    HHSPass207GPUDriver* driver,
    const uint8_t* key,
    HHSPass207CacheKind kind
) {
    uint32_t index;
    if (driver == NULL || key == NULL) {
        return NULL;
    }
    for (index = 0u; index < driver->cache_slots; ++index) {
        HHSCacheEntry* entry = &driver->cache[index];
        if (entry->occupied != 0u && entry->kind == kind && hhs_keys_equal(entry->key, key)) {
            entry->stamp = ++driver->stamp;
            return entry;
        }
    }
    return NULL;
}

static HHSCacheEntry* hhs_select_cache_slot(HHSPass207GPUDriver* driver, size_t incoming_size) {
    uint32_t index;
    HHSCacheEntry* oldest = NULL;
    if (driver == NULL || driver->cache_slots == 0u || incoming_size > driver->config.cache_capacity_bytes) {
        return NULL;
    }
    while (driver->status.cache_entries >= driver->config.cache_capacity_entries
           || driver->status.cache_resident_bytes + incoming_size > driver->config.cache_capacity_bytes) {
        oldest = NULL;
        for (index = 0u; index < driver->cache_slots; ++index) {
            HHSCacheEntry* entry = &driver->cache[index];
            if (entry->occupied != 0u && (oldest == NULL || entry->stamp < oldest->stamp)) {
                oldest = entry;
            }
        }
        if (oldest == NULL) {
            return NULL;
        }
        hhs_release_cache_entry(driver, oldest);
        driver->status.cache_evictions += 1u;
    }
    for (index = 0u; index < driver->cache_slots; ++index) {
        if (driver->cache[index].occupied == 0u) {
            return &driver->cache[index];
        }
    }
    return NULL;
}

static HHSPass207Status hhs_cache_store_locked(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind,
    const void* data,
    size_t size,
    cl_mem owned_device_buffer
) {
    HHSCacheEntry* entry;
    uint8_t* copy;
    cl_int cl_status = CL_SUCCESS;
    if (driver == NULL || !hhs_key_present(key) || data == NULL || size == 0u) {
        if (owned_device_buffer != NULL && driver != NULL && driver->cl.ReleaseMemObject != NULL) {
            (void)driver->cl.ReleaseMemObject(owned_device_buffer);
        }
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    entry = hhs_find_cache_entry(driver, key, kind);
    if (entry != NULL) {
        hhs_release_cache_entry(driver, entry);
    } else {
        entry = hhs_select_cache_slot(driver, size);
    }
    if (entry == NULL) {
        if (owned_device_buffer != NULL && driver->cl.ReleaseMemObject != NULL) {
            (void)driver->cl.ReleaseMemObject(owned_device_buffer);
        }
        return HHS_PASS207_ERR_OUT_OF_MEMORY;
    }
    copy = (uint8_t*)malloc(size);
    if (copy == NULL) {
        if (owned_device_buffer != NULL && driver->cl.ReleaseMemObject != NULL) {
            (void)driver->cl.ReleaseMemObject(owned_device_buffer);
        }
        return HHS_PASS207_ERR_OUT_OF_MEMORY;
    }
    memcpy(copy, data, size);
    if (owned_device_buffer == NULL && driver->status.selected_backend == HHS_PASS207_BACKEND_OPENCL) {
        owned_device_buffer = driver->cl.CreateBuffer(driver->context, CL_MEM_READ_WRITE, size, NULL, &cl_status);
        if (owned_device_buffer == NULL || cl_status != CL_SUCCESS) {
            free(copy);
            hhs_set_error(driver, "OpenCL cache buffer allocation failed");
            return HHS_PASS207_ERR_BACKEND_FAILURE;
        }
        cl_status = driver->cl.EnqueueWriteBuffer(driver->queue, owned_device_buffer, CL_TRUE, 0u, size, data, 0u, NULL, NULL);
        if (cl_status != CL_SUCCESS) {
            (void)driver->cl.ReleaseMemObject(owned_device_buffer);
            free(copy);
            hhs_set_error(driver, "OpenCL cache buffer upload failed");
            return HHS_PASS207_ERR_BACKEND_FAILURE;
        }
        driver->status.input_bytes_uploaded += size;
    }
    memcpy(entry->key, key, HHS_PASS207_CACHE_KEY_BYTES);
    entry->kind = kind;
    entry->host_data = copy;
    entry->size = size;
    entry->device_buffer = owned_device_buffer;
    entry->stamp = ++driver->stamp;
    entry->occupied = 1u;
    driver->status.cache_resident_bytes += size;
    driver->status.cache_entries += 1u;
    return HHS_PASS207_OK;
}
