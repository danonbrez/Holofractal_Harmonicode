static HHSPass207Status hhs_validate_batch(const HHSPass207Batch* batch, const HHSPass207BatchOutput* output) {
    uint32_t batch_index;
    if (batch == NULL || output == NULL || batch->batch_size == 0u
        || batch->state_soa == NULL || batch->projection_soa == NULL
        || batch->delta_offsets == NULL || batch->hydration_offsets == NULL
        || output->child_state_soa == NULL || output->child_projection_soa == NULL
        || output->frontier_soa == NULL || output->hydration_valid == NULL) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    if ((batch->delta_count > 0u && (batch->delta_cells == NULL || batch->delta_controls == NULL || batch->delta_xor_masks == NULL))
        || (batch->hydration_count > 0u && batch->hydration_q == NULL)) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    if (batch->delta_offsets[0] != 0u || batch->hydration_offsets[0] != 0u
        || batch->delta_offsets[batch->batch_size] != batch->delta_count
        || batch->hydration_offsets[batch->batch_size] != batch->hydration_count) {
        return HHS_PASS207_ERR_INVALID_ARGUMENT;
    }
    for (batch_index = 0u; batch_index < batch->batch_size; ++batch_index) {
        uint8_t seen[HHS_PASS207_CELL_COUNT];
        uint32_t event_index;
        uint32_t hydration_cursor = batch->hydration_offsets[batch_index];
        if (batch->delta_offsets[batch_index] > batch->delta_offsets[batch_index + 1u]
            || batch->hydration_offsets[batch_index] > batch->hydration_offsets[batch_index + 1u]) {
            return HHS_PASS207_ERR_INVALID_ARGUMENT;
        }
        memset(seen, 0, sizeof(seen));
        for (event_index = batch->delta_offsets[batch_index]; event_index < batch->delta_offsets[batch_index + 1u]; ++event_index) {
            const uint32_t cell = batch->delta_cells[event_index];
            const uint32_t control = batch->delta_controls[event_index];
            const uint64_t mask = batch->delta_xor_masks[event_index];
            uint32_t bit;
            if (cell >= HHS_PASS207_CELL_COUNT || control >= HHS_PASS207_CONTROL_COUNT || mask == 0u || seen[cell] != 0u) {
                return HHS_PASS207_ERR_INVALID_ARGUMENT;
            }
            seen[cell] = 1u;
            for (bit = 0u; bit < HHS_PASS207_BITS_PER_CELL; ++bit) {
                if ((mask & (UINT64_C(1) << bit)) != 0u) {
                    const uint32_t s = cell * HHS_PASS207_BITS_PER_CELL + bit;
                    const uint32_t expected_q = s * HHS_PASS207_CONTROL_COUNT + control;
                    if (hydration_cursor >= batch->hydration_offsets[batch_index + 1u]
                        || batch->hydration_q[hydration_cursor] != expected_q) {
                        return HHS_PASS207_ERR_HYDRATION_MISMATCH;
                    }
                    hydration_cursor += 1u;
                }
            }
        }
        if (hydration_cursor != batch->hydration_offsets[batch_index + 1u]) {
            return HHS_PASS207_ERR_HYDRATION_MISMATCH;
        }
    }
    return HHS_PASS207_OK;
}

static void hhs_cpu_dispatch(const HHSPass207Batch* batch, HHSPass207BatchOutput* output) {
    uint32_t batch_index;
    const uint32_t batch_size = batch->batch_size;
    for (batch_index = 0u; batch_index < batch_size; ++batch_index) {
        uint32_t cell;
        output->hydration_valid[batch_index] = 1u;
        for (cell = 0u; cell < HHS_PASS207_CELL_COUNT; ++cell) {
            const uint64_t parent_word = batch->state_soa[(size_t)cell * batch_size + batch_index];
            uint64_t packed = 0u;
            uint8_t affected = 0u;
            uint32_t hyperthread;
            uint32_t event_index;
            for (event_index = batch->delta_offsets[batch_index]; event_index < batch->delta_offsets[batch_index + 1u]; ++event_index) {
                const uint32_t changed = batch->delta_cells[event_index];
                if (cell == changed || cell == ((changed + 1u) % HHS_PASS207_CELL_COUNT)
                    || cell == ((changed + 80u) % HHS_PASS207_CELL_COUNT)
                    || cell == ((changed + 72u) % HHS_PASS207_CELL_COUNT)) {
                    affected = 1u;
                }
            }
            for (hyperthread = 0u; hyperthread < HHS_PASS207_LOGICAL_HYPERTHREADS; ++hyperthread) {
                uint8_t bit = (uint8_t)((parent_word >> hyperthread) & UINT64_C(1));
                for (event_index = batch->delta_offsets[batch_index]; event_index < batch->delta_offsets[batch_index + 1u]; ++event_index) {
                    if (batch->delta_cells[event_index] == cell
                        && (batch->delta_xor_masks[event_index] & (UINT64_C(1) << hyperthread)) != 0u) {
                        bit ^= 1u;
                    }
                }
                if (bit != 0u) {
                    packed |= UINT64_C(1) << hyperthread;
                }
            }
            output->child_state_soa[(size_t)cell * batch_size + batch_index] = packed;
            output->frontier_soa[(size_t)cell * batch_size + batch_index] = affected;
        }
    }
    {
        uint32_t channel;
        for (channel = 0u; channel < HHS_PASS207_PROJECTION_CHANNELS; ++channel) {
            uint32_t cell;
            for (cell = 0u; cell < HHS_PASS207_CELL_COUNT; ++cell) {
                for (batch_index = 0u; batch_index < batch_size; ++batch_index) {
                    const size_t index = ((size_t)channel * HHS_PASS207_CELL_COUNT + cell) * batch_size + batch_index;
                    output->child_projection_soa[index] = output->frontier_soa[(size_t)cell * batch_size + batch_index] != 0u
                        ? hhs_projection_word_soa(output->child_state_soa, batch_size, batch_index, channel, cell)
                        : batch->projection_soa[index];
                }
            }
        }
    }
}

static uint8_t hhs_compare_cpu(
    const HHSPass207Batch* batch,
    const HHSPass207BatchOutput* output
) {
    const size_t state_count = (size_t)HHS_PASS207_CELL_COUNT * batch->batch_size;
    const size_t projection_count = (size_t)HHS_PASS207_PROJECTION_CHANNELS * HHS_PASS207_CELL_COUNT * batch->batch_size;
    uint64_t* state = (uint64_t*)calloc(state_count, sizeof(*state));
    uint32_t* projection = (uint32_t*)calloc(projection_count, sizeof(*projection));
    uint8_t* frontier = (uint8_t*)calloc(state_count, sizeof(*frontier));
    uint8_t* hydration = (uint8_t*)calloc(batch->batch_size, sizeof(*hydration));
    HHSPass207BatchOutput reference;
    uint8_t equal;
    if (state == NULL || projection == NULL || frontier == NULL || hydration == NULL) {
        free(state);
        free(projection);
        free(frontier);
        free(hydration);
        return 0u;
    }
    reference.child_state_soa = state;
    reference.child_projection_soa = projection;
    reference.frontier_soa = frontier;
    reference.hydration_valid = hydration;
    hhs_cpu_dispatch(batch, &reference);
    equal = (uint8_t)(memcmp(state, output->child_state_soa, state_count * sizeof(*state)) == 0
        && memcmp(projection, output->child_projection_soa, projection_count * sizeof(*projection)) == 0
        && memcmp(frontier, output->frontier_soa, state_count * sizeof(*frontier)) == 0
        && memcmp(hydration, output->hydration_valid, batch->batch_size * sizeof(*hydration)) == 0);
    free(state);
    free(projection);
    free(frontier);
    free(hydration);
    return equal;
}

static cl_mem hhs_create_and_upload(
    HHSPass207GPUDriver* driver,
    cl_mem_flags flags,
    const void* data,
    size_t size,
    HHSPass207Status* out_status
) {
    cl_int status = CL_SUCCESS;
    cl_mem buffer = driver->cl.CreateBuffer(driver->context, flags, size, NULL, &status);
    if (buffer == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL buffer allocation failed");
        *out_status = HHS_PASS207_ERR_BACKEND_FAILURE;
        return NULL;
    }
    if (data != NULL) {
        status = driver->cl.EnqueueWriteBuffer(driver->queue, buffer, CL_TRUE, 0u, size, data, 0u, NULL, NULL);
        if (status != CL_SUCCESS) {
            (void)driver->cl.ReleaseMemObject(buffer);
            hhs_set_error(driver, "OpenCL buffer upload failed");
            *out_status = HHS_PASS207_ERR_BACKEND_FAILURE;
            return NULL;
        }
        driver->status.input_bytes_uploaded += size;
    }
    *out_status = HHS_PASS207_OK;
    return buffer;
}

static HHSPass207Status hhs_set_arg(HHSPass207GPUDriver* driver, cl_kernel kernel, cl_uint index, size_t size, const void* value) {
