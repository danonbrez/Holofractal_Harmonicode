uint16_t hhs_pass207_lane_address(uint8_t cell, uint8_t hyperthread, uint8_t* ok) {
    const uint8_t valid = (uint8_t)(cell < HHS_PASS207_CELL_COUNT && hyperthread < HHS_PASS207_LOGICAL_HYPERTHREADS);
    if (ok != NULL) {
        *ok = valid;
    }
    if (valid == 0u) {
        return UINT16_MAX;
    }
    return (uint16_t)((uint16_t)cell * HHS_PASS207_LOGICAL_HYPERTHREADS + hyperthread);
}

uint8_t hhs_pass207_lane_decode(uint16_t lane, uint8_t* out_cell, uint8_t* out_hyperthread) {
    if (lane >= HHS_PASS207_LOGICAL_LANES || out_cell == NULL || out_hyperthread == NULL) {
        return 0u;
    }
    *out_cell = (uint8_t)(lane / HHS_PASS207_LOGICAL_HYPERTHREADS);
    *out_hyperthread = (uint8_t)(lane % HHS_PASS207_LOGICAL_HYPERTHREADS);
    return 1u;
}

uint8_t hhs_pass207_lane_phase_coordinate(uint16_t lane, uint8_t* out_phase_row, uint8_t* out_phase_column) {
    if (lane >= HHS_PASS207_LOGICAL_LANES || out_phase_row == NULL || out_phase_column == NULL) {
        return 0u;
    }
    *out_phase_row = (uint8_t)(lane / HHS_PASS207_PHASE_DIMENSION);
    *out_phase_column = (uint8_t)(lane % HHS_PASS207_PHASE_DIMENSION);
    return 1u;
}

HHSPass207GPUConfig hhs_pass207_gpu_default_config(void) {
    HHSPass207GPUConfig config;
    memset(&config, 0, sizeof(config));
    config.api_version = HHS_PASS207_API_VERSION;
    config.requested_backend = HHS_PASS207_BACKEND_AUTO;
    config.cache_capacity_bytes = UINT64_C(256) * 1024u * 1024u;
    config.cache_capacity_entries = 256u;
    config.verify_against_cpu = 1u;
    return config;
}

HHSPass207Status hhs_pass207_gpu_create(
    const HHSPass207GPUConfig* config,
    HHSPass207GPUDriver** out_driver
) {
    HHSPass207GPUConfig selected = config == NULL ? hhs_pass207_gpu_default_config() : *config;
    HHSPass207GPUDriver* driver;
    if (out_driver == NULL || selected.api_version != HHS_PASS207_API_VERSION
        || selected.cache_capacity_entries == 0u || selected.cache_capacity_bytes == 0u) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    *out_driver = NULL;
    driver = (HHSPass207GPUDriver*)calloc(1u, sizeof(*driver));
    if (driver == NULL) {
        return HHS_PASS207_ERR_OUT_OF_MEMORY;
    }
    driver->config = selected;
    driver->cache_slots = selected.cache_capacity_entries;
    driver->cache = (HHSCacheEntry*)calloc(driver->cache_slots, sizeof(*driver->cache));
    if (driver->cache == NULL) {
        free(driver);
        return HHS_PASS207_ERR_OUT_OF_MEMORY;
    }
    atomic_flag_clear(&driver->lock);
    driver->status.deterministic_integer_only = 1u;
    driver->status.logical_hyperthreads_per_cell = HHS_PASS207_LOGICAL_HYPERTHREADS;
    driver->status.logical_lanes_per_batch = HHS_PASS207_LOGICAL_LANES;
    driver->status.physical_workgroup_size = HHS_PASS207_DEFAULT_WORKGROUP;
    driver->status.stable_lane_identity = 1u;
    driver->status.disjoint_lane_writes = 1u;
    driver->status.canonical_reduction_order = 1u;
    driver->status.selected_backend = HHS_PASS207_BACKEND_CPU_REFERENCE;
    hhs_copy_text(driver->status.backend_name, sizeof(driver->status.backend_name), "CPU_REFERENCE");
    hhs_copy_text(driver->status.device_name, sizeof(driver->status.device_name), "HOST_CPU_EXACT_ORACLE");
    if (selected.requested_backend == HHS_PASS207_BACKEND_AUTO || selected.requested_backend == HHS_PASS207_BACKEND_OPENCL) {
        if (!hhs_initialize_opencl(driver)) {
            if (selected.requested_backend == HHS_PASS207_BACKEND_OPENCL || selected.require_physical_gpu != 0u) {
                hhs_pass207_gpu_destroy(driver);
                return HHS_PASS207_ERR_BACKEND_UNAVAILABLE;
            }
            driver->status.selected_backend = HHS_PASS207_BACKEND_CPU_REFERENCE;
            driver->status.physical_gpu = 0u;
            hhs_copy_text(driver->status.backend_name, sizeof(driver->status.backend_name), "CPU_REFERENCE");
            hhs_copy_text(driver->status.device_name, sizeof(driver->status.device_name), "HOST_CPU_EXACT_ORACLE");
        }
    } else if (selected.requested_backend != HHS_PASS207_BACKEND_CPU_REFERENCE) {
        hhs_pass207_gpu_destroy(driver);
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    *out_driver = driver;
    return HHS_PASS207_OK;
}

void hhs_pass207_gpu_destroy(HHSPass207GPUDriver* driver) {
    uint32_t index;
    if (driver == NULL) {
        return;
    }
    for (index = 0u; index < driver->cache_slots; ++index) {
        hhs_release_cache_entry(driver, &driver->cache[index]);
    }
    free(driver->cache);
    hhs_release_opencl(driver);
    free(driver);
}

HHSPass207Status hhs_pass207_gpu_get_status(
    const HHSPass207GPUDriver* driver,
    HHSPass207GPUStatus* out_status
) {
    if (driver == NULL || out_status == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    *out_status = driver->status;
    return HHS_PASS207_OK;
}

HHSPass207Status hhs_pass207_gpu_dispatch(
    HHSPass207GPUDriver* driver,
    const HHSPass207Batch* batch,
    HHSPass207BatchOutput* output
) {
    HHSPass207Status result;
    if (driver == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    hhs_lock(driver);
    result = hhs_validate_batch(batch, output);
    if (result != HHS_PASS207_OK) {
        hhs_unlock(driver);
        return result;
    }
    driver->status.verified_against_cpu = 0u;
    if (driver->status.selected_backend == HHS_PASS207_BACKEND_OPENCL) {
        result = hhs_opencl_dispatch(driver, batch, output);
    } else {
        const size_t state_bytes = (size_t)HHS_PASS207_CELL_COUNT * batch->batch_size * sizeof(uint64_t);
        const size_t projection_bytes = (size_t)HHS_PASS207_PROJECTION_CHANNELS * HHS_PASS207_CELL_COUNT * batch->batch_size * sizeof(uint32_t);
        HHSCacheEntry* state_entry = NULL;
        HHSCacheEntry* projection_entry = NULL;
        HHSPass207Batch local = *batch;
        if (batch->reuse_cached_inputs != 0u && hhs_key_present(batch->input_cache_key)) {
            state_entry = hhs_find_cache_entry(driver, batch->input_cache_key, HHS_PASS207_CACHE_STATE_SOA);
            projection_entry = hhs_find_cache_entry(driver, batch->input_cache_key, HHS_PASS207_CACHE_PROJECTION_SOA);
            if (state_entry != NULL && projection_entry != NULL && state_entry->size == state_bytes && projection_entry->size == projection_bytes) {
                local.state_soa = (const uint64_t*)state_entry->host_data;
                local.projection_soa = (const uint32_t*)projection_entry->host_data;
                driver->status.cache_hits += 2u;
                driver->status.cache_input_hit = 1u;
            } else {
                driver->status.cache_misses += 1u;
                driver->status.cache_input_hit = 0u;
            }
        }
        hhs_cpu_dispatch(&local, output);
        driver->status.verified_against_cpu = 1u;
        if (hhs_key_present(batch->input_cache_key) && driver->status.cache_input_hit == 0u) {
            (void)hhs_cache_store_locked(driver, batch->input_cache_key, HHS_PASS207_CACHE_STATE_SOA, batch->state_soa, state_bytes, NULL);
            (void)hhs_cache_store_locked(driver, batch->input_cache_key, HHS_PASS207_CACHE_PROJECTION_SOA, batch->projection_soa, projection_bytes, NULL);
        }
        if (batch->retain_outputs != 0u && hhs_key_present(batch->output_cache_key)) {
            if (hhs_cache_store_locked(driver, batch->output_cache_key, HHS_PASS207_CACHE_CHILD_STATE_SOA, output->child_state_soa, state_bytes, NULL) == HHS_PASS207_OK
                && hhs_cache_store_locked(driver, batch->output_cache_key, HHS_PASS207_CACHE_CHILD_PROJECTION_SOA, output->child_projection_soa, projection_bytes, NULL) == HHS_PASS207_OK) {
                driver->status.cache_output_retained = 1u;
            }
        }
        result = HHS_PASS207_OK;
    }
    if (result == HHS_PASS207_OK) {
        driver->status.dispatch_count += 1u;
        driver->status.last_error[0] = '\0';
    }
    hhs_unlock(driver);
    return result;
}

HHSPass207Status hhs_pass207_gpu_vector_distance72(
    HHSPass207GPUDriver* driver,
    const uint8_t query[72],
    const uint8_t* candidate_matrix,
    uint32_t candidate_count,
    const uint8_t* matrix_cache_key,
    uint8_t reuse_cached_matrix,
    uint32_t* out_distances
) {
    HHSPass207Status result = HHS_PASS207_OK;
    size_t matrix_bytes;
    HHSCacheEntry* cached = NULL;
    if (driver == NULL || query == NULL || candidate_count == 0u || out_distances == NULL
        || (candidate_matrix == NULL && !(reuse_cached_matrix != 0u && hhs_key_present(matrix_cache_key)))) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    matrix_bytes = (size_t)candidate_count * 72u;
    hhs_lock(driver);
    if (reuse_cached_matrix != 0u && hhs_key_present(matrix_cache_key)) {
        cached = hhs_find_cache_entry(driver, matrix_cache_key, HHS_PASS207_CACHE_VECTOR_MATRIX);
        if (cached != NULL && cached->size == matrix_bytes) {
            candidate_matrix = cached->host_data;
            driver->status.cache_hits += 1u;
        } else if (candidate_matrix == NULL) {
            driver->status.cache_misses += 1u;
            hhs_unlock(driver);
            return HHS_PASS207_ERR_CACHE_MISS;
        } else {
            driver->status.cache_misses += 1u;
        }
    }
    if (driver->status.selected_backend == HHS_PASS207_BACKEND_OPENCL) {
        cl_mem query_buffer = NULL;
        cl_mem matrix_buffer = cached != NULL ? cached->device_buffer : NULL;
        cl_mem distance_buffer = NULL;
        cl_int cl_status;
        size_t global = candidate_count;
        uint32_t arg = 0u;
        query_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, query, 72u, &result);
        if (query_buffer == NULL) goto vector_cleanup;
        if (matrix_buffer == NULL) {
            matrix_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, candidate_matrix, matrix_bytes, &result);
            if (matrix_buffer == NULL) goto vector_cleanup;
        }
        distance_buffer = hhs_create_and_upload(driver, CL_MEM_WRITE_ONLY, NULL, (size_t)candidate_count * sizeof(uint32_t), &result);
        if (distance_buffer == NULL) goto vector_cleanup;
        if ((result = hhs_set_arg(driver, driver->vector_kernel, arg++, sizeof(query_buffer), &query_buffer)) != HHS_PASS207_OK) goto vector_cleanup;
        if ((result = hhs_set_arg(driver, driver->vector_kernel, arg++, sizeof(matrix_buffer), &matrix_buffer)) != HHS_PASS207_OK) goto vector_cleanup;
        if ((result = hhs_set_arg(driver, driver->vector_kernel, arg++, sizeof(candidate_count), &candidate_count)) != HHS_PASS207_OK) goto vector_cleanup;
        if ((result = hhs_set_arg(driver, driver->vector_kernel, arg++, sizeof(distance_buffer), &distance_buffer)) != HHS_PASS207_OK) goto vector_cleanup;
        cl_status = driver->cl.EnqueueNDRangeKernel(driver->queue, driver->vector_kernel, 1u, NULL, &global, NULL, 0u, NULL, NULL);
        if (cl_status != CL_SUCCESS || driver->cl.Finish(driver->queue) != CL_SUCCESS
            || driver->cl.EnqueueReadBuffer(driver->queue, distance_buffer, CL_TRUE, 0u, (size_t)candidate_count * sizeof(uint32_t), out_distances, 0u, NULL, NULL) != CL_SUCCESS) {
            result = HHS_PASS207_ERR_BACKEND_FAILURE;
            hhs_set_error(driver, "OpenCL vector-distance dispatch failed");
            goto vector_cleanup;
        }
        driver->status.output_bytes_downloaded += (size_t)candidate_count * sizeof(uint32_t);
        if (cached == NULL && hhs_key_present(matrix_cache_key)) {
            cl_mem retained = matrix_buffer;
            matrix_buffer = NULL;
            (void)hhs_cache_store_locked(driver, matrix_cache_key, HHS_PASS207_CACHE_VECTOR_MATRIX, candidate_matrix, matrix_bytes, retained);
        }
vector_cleanup:
        if (distance_buffer != NULL) (void)driver->cl.ReleaseMemObject(distance_buffer);
        if (matrix_buffer != NULL && (cached == NULL || matrix_buffer != cached->device_buffer)) (void)driver->cl.ReleaseMemObject(matrix_buffer);
        if (query_buffer != NULL) (void)driver->cl.ReleaseMemObject(query_buffer);
    } else {
        uint32_t candidate;
        for (candidate = 0u; candidate < candidate_count; ++candidate) {
            uint32_t total = 0u;
            uint32_t index;
            for (index = 0u; index < 72u; ++index) {
                const uint32_t a = query[index];
                const uint32_t b = candidate_matrix[(size_t)candidate * 72u + index];
                const uint32_t distance = a > b ? a - b : b - a;
                total += distance < (72u - distance) ? distance : (72u - distance);
            }
            out_distances[candidate] = total;
        }
        if (cached == NULL && hhs_key_present(matrix_cache_key)) {
            (void)hhs_cache_store_locked(driver, matrix_cache_key, HHS_PASS207_CACHE_VECTOR_MATRIX, candidate_matrix, matrix_bytes, NULL);
        }
    }
    if (result == HHS_PASS207_OK) {
        driver->status.vector_dispatch_count += 1u;
        driver->status.last_error[0] = '\0';
    }
    hhs_unlock(driver);
    return result;
}

HHSPass207Status hhs_pass207_gpu_cache_store(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind,
    const void* data,
    size_t size
) {
    HHSPass207Status result;
    if (driver == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    hhs_lock(driver);
    result = hhs_cache_store_locked(driver, key, kind, data, size, NULL);
    hhs_unlock(driver);
    return result;
}

HHSPass207Status hhs_pass207_gpu_cache_load(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind,
    void* out_data,
    size_t capacity,
    size_t* out_size
) {
    HHSCacheEntry* entry;
    if (driver == NULL || key == NULL || out_size == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    hhs_lock(driver);
    entry = hhs_find_cache_entry(driver, key, kind);
    if (entry == NULL) {
        driver->status.cache_misses += 1u;
        hhs_unlock(driver);
        return HHS_PASS207_ERR_CACHE_MISS;
    }
    *out_size = entry->size;
    if (out_data == NULL || capacity < entry->size) {
        hhs_unlock(driver);
        return HHS_PASS207_ERR_BUFFER_TOO_SMALL;
    }
    memcpy(out_data, entry->host_data, entry->size);
    driver->status.cache_hits += 1u;
    hhs_unlock(driver);
    return HHS_PASS207_OK;
}

HHSPass207Status hhs_pass207_gpu_cache_remove(
    HHSPass207GPUDriver* driver,
    const uint8_t key[HHS_PASS207_CACHE_KEY_BYTES],
    HHSPass207CacheKind kind
) {
    HHSCacheEntry* entry;
    if (driver == NULL || key == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    hhs_lock(driver);
    entry = hhs_find_cache_entry(driver, key, kind);
    if (entry == NULL) {
        hhs_unlock(driver);
        return HHS_PASS207_ERR_CACHE_MISS;
    }
    hhs_release_cache_entry(driver, entry);
    hhs_unlock(driver);
    return HHS_PASS207_OK;
}

void hhs_pass207_gpu_cache_clear(HHSPass207GPUDriver* driver) {
    uint32_t index;
    if (driver == NULL) {
        return;
    }
    hhs_lock(driver);
    for (index = 0u; index < driver->cache_slots; ++index) {
        hhs_release_cache_entry(driver, &driver->cache[index]);
    }
    hhs_unlock(driver);
}

const char* hhs_pass207_gpu_status_string(HHSPass207Status status) {
    switch (status) {
        case HHS_PASS207_OK: return "OK";
        case HHS_PASS207_ERR_INVALID_ARGUMENT: return "INVALID_ARGUMENT";
        case HHS_PASS207_ERR_OUT_OF_MEMORY: return "OUT_OF_MEMORY";
        case HHS_PASS207_ERR_BACKEND_UNAVAILABLE: return "BACKEND_UNAVAILABLE";
        case HHS_PASS207_ERR_BACKEND_FAILURE: return "BACKEND_FAILURE";
        case HHS_PASS207_ERR_HYDRATION_MISMATCH: return "HYDRATION_MISMATCH";
        case HHS_PASS207_ERR_CPU_VERIFICATION: return "CPU_VERIFICATION_FAILED";
        case HHS_PASS207_ERR_CACHE_MISS: return "CACHE_MISS";
        case HHS_PASS207_ERR_BUFFER_TOO_SMALL: return "BUFFER_TOO_SMALL";
        default: return "UNKNOWN";
    }
}
