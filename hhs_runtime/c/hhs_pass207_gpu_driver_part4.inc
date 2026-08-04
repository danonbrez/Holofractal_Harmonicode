    if (driver->cl.SetKernelArg(kernel, index, size, value) != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL kernel argument binding failed");
        return HHS_PASS207_ERR_BACKEND_FAILURE;
    }
    return HHS_PASS207_OK;
}

static HHSPass207Status hhs_opencl_dispatch(
    HHSPass207GPUDriver* driver,
    const HHSPass207Batch* batch,
    HHSPass207BatchOutput* output
) {
    const size_t state_bytes = (size_t)HHS_PASS207_CELL_COUNT * batch->batch_size * sizeof(uint64_t);
    const size_t projection_bytes = (size_t)HHS_PASS207_PROJECTION_CHANNELS * HHS_PASS207_CELL_COUNT * batch->batch_size * sizeof(uint32_t);
    const size_t frontier_bytes = (size_t)HHS_PASS207_CELL_COUNT * batch->batch_size;
    const size_t lane_bytes = (size_t)HHS_PASS207_LOGICAL_LANES * batch->batch_size;
    const size_t delta_offsets_bytes = ((size_t)batch->batch_size + 1u) * sizeof(uint32_t);
    const size_t delta_cells_bytes = (size_t)(batch->delta_count == 0u ? 1u : batch->delta_count) * sizeof(uint32_t);
    const size_t delta_controls_bytes = (size_t)(batch->delta_count == 0u ? 1u : batch->delta_count) * sizeof(uint8_t);
    const size_t delta_masks_bytes = (size_t)(batch->delta_count == 0u ? 1u : batch->delta_count) * sizeof(uint64_t);
    const size_t hydration_offsets_bytes = ((size_t)batch->batch_size + 1u) * sizeof(uint32_t);
    const size_t hydration_q_bytes = (size_t)(batch->hydration_count == 0u ? 1u : batch->hydration_count) * sizeof(uint32_t);
    const size_t hydration_valid_bytes = (size_t)(batch->hydration_count == 0u ? 1u : batch->hydration_count);
    HHSCacheEntry* cached_state = NULL;
    HHSCacheEntry* cached_projection = NULL;
    cl_mem state_buffer = NULL;
    cl_mem projection_buffer = NULL;
    cl_mem delta_offsets_buffer = NULL;
    cl_mem delta_cells_buffer = NULL;
    cl_mem delta_controls_buffer = NULL;
    cl_mem delta_masks_buffer = NULL;
    cl_mem hydration_offsets_buffer = NULL;
    cl_mem hydration_q_buffer = NULL;
    cl_mem lane_bits_buffer = NULL;
    cl_mem lane_frontier_buffer = NULL;
    cl_mem child_state_buffer = NULL;
    cl_mem child_projection_buffer = NULL;
    cl_mem frontier_buffer = NULL;
    cl_mem hydration_valid_buffer = NULL;
    uint8_t* hydration_each = NULL;
    HHSPass207Status result = HHS_PASS207_OK;
    cl_int cl_status;
    size_t apply_global;
    size_t apply_local = HHS_PASS207_DEFAULT_WORKGROUP;
    size_t pack_global;
    size_t projection_global;
    size_t hydration_global;
    uint32_t arg;

    driver->status.cache_input_hit = 0u;
    driver->status.cache_output_retained = 0u;
    if (batch->reuse_cached_inputs != 0u && hhs_key_present(batch->input_cache_key)) {
        cached_state = hhs_find_cache_entry(driver, batch->input_cache_key, HHS_PASS207_CACHE_STATE_SOA);
        cached_projection = hhs_find_cache_entry(driver, batch->input_cache_key, HHS_PASS207_CACHE_PROJECTION_SOA);
        if (cached_state != NULL && cached_projection != NULL && cached_state->size == state_bytes
            && cached_projection->size == projection_bytes && cached_state->device_buffer != NULL
            && cached_projection->device_buffer != NULL) {
            state_buffer = cached_state->device_buffer;
            projection_buffer = cached_projection->device_buffer;
            driver->status.cache_hits += 2u;
            driver->status.cache_input_hit = 1u;
        } else {
            driver->status.cache_misses += 1u;
        }
    }
    if (state_buffer == NULL) {
        state_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->state_soa, state_bytes, &result);
        if (state_buffer == NULL) goto cleanup;
    }
    if (projection_buffer == NULL) {
        projection_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->projection_soa, projection_bytes, &result);
        if (projection_buffer == NULL) goto cleanup;
    }
    delta_offsets_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->delta_offsets, delta_offsets_bytes, &result);
    if (delta_offsets_buffer == NULL) goto cleanup;
    {
        const uint32_t zero32 = 0u;
        const uint8_t zero8 = 0u;
        const uint64_t zero64 = 0u;
        delta_cells_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->delta_count == 0u ? (const void*)&zero32 : (const void*)batch->delta_cells, delta_cells_bytes, &result);
        if (delta_cells_buffer == NULL) goto cleanup;
        delta_controls_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->delta_count == 0u ? (const void*)&zero8 : (const void*)batch->delta_controls, delta_controls_bytes, &result);
        if (delta_controls_buffer == NULL) goto cleanup;
        delta_masks_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->delta_count == 0u ? (const void*)&zero64 : (const void*)batch->delta_xor_masks, delta_masks_bytes, &result);
        if (delta_masks_buffer == NULL) goto cleanup;
    }
    hydration_offsets_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->hydration_offsets, hydration_offsets_bytes, &result);
    if (hydration_offsets_buffer == NULL) goto cleanup;
    {
        const uint32_t zero32 = 0u;
        hydration_q_buffer = hhs_create_and_upload(driver, CL_MEM_READ_ONLY, batch->hydration_count == 0u ? (const void*)&zero32 : (const void*)batch->hydration_q, hydration_q_bytes, &result);
    }
    if (hydration_q_buffer == NULL) goto cleanup;
    lane_bits_buffer = hhs_create_and_upload(driver, CL_MEM_READ_WRITE, NULL, lane_bytes, &result);
    if (lane_bits_buffer == NULL) goto cleanup;
    lane_frontier_buffer = hhs_create_and_upload(driver, CL_MEM_READ_WRITE, NULL, lane_bytes, &result);
    if (lane_frontier_buffer == NULL) goto cleanup;
    child_state_buffer = hhs_create_and_upload(driver, CL_MEM_READ_WRITE, NULL, state_bytes, &result);
    if (child_state_buffer == NULL) goto cleanup;
    child_projection_buffer = hhs_create_and_upload(driver, CL_MEM_READ_WRITE, NULL, projection_bytes, &result);
    if (child_projection_buffer == NULL) goto cleanup;
    frontier_buffer = hhs_create_and_upload(driver, CL_MEM_READ_WRITE, NULL, frontier_bytes, &result);
    if (frontier_buffer == NULL) goto cleanup;
    hydration_valid_buffer = hhs_create_and_upload(driver, CL_MEM_WRITE_ONLY, NULL, hydration_valid_bytes, &result);
    if (hydration_valid_buffer == NULL) goto cleanup;

    arg = 0u;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(state_buffer), &state_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(delta_offsets_buffer), &delta_offsets_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(delta_cells_buffer), &delta_cells_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(delta_controls_buffer), &delta_controls_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(delta_masks_buffer), &delta_masks_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(batch->batch_size), &batch->batch_size)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(lane_bits_buffer), &lane_bits_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->apply_kernel, arg++, sizeof(lane_frontier_buffer), &lane_frontier_buffer)) != HHS_PASS207_OK) goto cleanup;
    apply_global = (size_t)batch->batch_size * HHS_PASS207_LOGICAL_LANES;
    cl_status = driver->cl.EnqueueNDRangeKernel(driver->queue, driver->apply_kernel, 1u, NULL, &apply_global, &apply_local, 0u, NULL, NULL);
    if (cl_status != CL_SUCCESS) { result = HHS_PASS207_ERR_BACKEND_FAILURE; hhs_set_error(driver, "OpenCL 5,184-lane VM81 hyperthread dispatch failed"); goto cleanup; }

    arg = 0u;
    if ((result = hhs_set_arg(driver, driver->pack_kernel, arg++, sizeof(lane_bits_buffer), &lane_bits_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->pack_kernel, arg++, sizeof(lane_frontier_buffer), &lane_frontier_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->pack_kernel, arg++, sizeof(batch->batch_size), &batch->batch_size)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->pack_kernel, arg++, sizeof(child_state_buffer), &child_state_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->pack_kernel, arg++, sizeof(frontier_buffer), &frontier_buffer)) != HHS_PASS207_OK) goto cleanup;
    pack_global = (size_t)batch->batch_size * HHS_PASS207_CELL_COUNT;
    cl_status = driver->cl.EnqueueNDRangeKernel(driver->queue, driver->pack_kernel, 1u, NULL, &pack_global, NULL, 0u, NULL, NULL);
    if (cl_status != CL_SUCCESS) { result = HHS_PASS207_ERR_BACKEND_FAILURE; hhs_set_error(driver, "OpenCL canonical hyperthread reduction failed"); goto cleanup; }

    arg = 0u;
    if ((result = hhs_set_arg(driver, driver->projection_kernel, arg++, sizeof(child_state_buffer), &child_state_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->projection_kernel, arg++, sizeof(projection_buffer), &projection_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->projection_kernel, arg++, sizeof(frontier_buffer), &frontier_buffer)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->projection_kernel, arg++, sizeof(batch->batch_size), &batch->batch_size)) != HHS_PASS207_OK) goto cleanup;
    if ((result = hhs_set_arg(driver, driver->projection_kernel, arg++, sizeof(child_projection_buffer), &child_projection_buffer)) != HHS_PASS207_OK) goto cleanup;
    projection_global = (size_t)batch->batch_size * HHS_PASS207_CELL_COUNT * HHS_PASS207_PROJECTION_CHANNELS;
    cl_status = driver->cl.EnqueueNDRangeKernel(driver->queue, driver->projection_kernel, 1u, NULL, &projection_global, NULL, 0u, NULL, NULL);
    if (cl_status != CL_SUCCESS) { result = HHS_PASS207_ERR_BACKEND_FAILURE; hhs_set_error(driver, "OpenCL projection dispatch failed"); goto cleanup; }

    if (batch->hydration_count > 0u) {
        arg = 0u;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(hydration_offsets_buffer), &hydration_offsets_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(hydration_q_buffer), &hydration_q_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(batch->hydration_count), &batch->hydration_count)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(delta_offsets_buffer), &delta_offsets_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(delta_cells_buffer), &delta_cells_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(delta_controls_buffer), &delta_controls_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(delta_masks_buffer), &delta_masks_buffer)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(batch->batch_size), &batch->batch_size)) != HHS_PASS207_OK) goto cleanup;
        if ((result = hhs_set_arg(driver, driver->hydration_kernel, arg++, sizeof(hydration_valid_buffer), &hydration_valid_buffer)) != HHS_PASS207_OK) goto cleanup;
        hydration_global = batch->hydration_count;
        cl_status = driver->cl.EnqueueNDRangeKernel(driver->queue, driver->hydration_kernel, 1u, NULL, &hydration_global, NULL, 0u, NULL, NULL);
        if (cl_status != CL_SUCCESS) { result = HHS_PASS207_ERR_BACKEND_FAILURE; hhs_set_error(driver, "OpenCL hydration dispatch failed"); goto cleanup; }
    }
    if (driver->cl.Finish(driver->queue) != CL_SUCCESS) {
        result = HHS_PASS207_ERR_BACKEND_FAILURE;
        hhs_set_error(driver, "OpenCL dispatch completion failed");
        goto cleanup;
    }
    if (driver->cl.EnqueueReadBuffer(driver->queue, child_state_buffer, CL_TRUE, 0u, state_bytes, output->child_state_soa, 0u, NULL, NULL) != CL_SUCCESS
        || driver->cl.EnqueueReadBuffer(driver->queue, child_projection_buffer, CL_TRUE, 0u, projection_bytes, output->child_projection_soa, 0u, NULL, NULL) != CL_SUCCESS
        || driver->cl.EnqueueReadBuffer(driver->queue, frontier_buffer, CL_TRUE, 0u, frontier_bytes, output->frontier_soa, 0u, NULL, NULL) != CL_SUCCESS) {
        result = HHS_PASS207_ERR_BACKEND_FAILURE;
        hhs_set_error(driver, "OpenCL result download failed");
        goto cleanup;
    }
    driver->status.output_bytes_downloaded += state_bytes + projection_bytes + frontier_bytes;
    memset(output->hydration_valid, 1, batch->batch_size);
    if (batch->hydration_count > 0u) {
        uint32_t index;
        uint32_t batch_index = 0u;
        hydration_each = (uint8_t*)calloc(batch->hydration_count, 1u);
        if (hydration_each == NULL) { result = HHS_PASS207_ERR_OUT_OF_MEMORY; goto cleanup; }
        if (driver->cl.EnqueueReadBuffer(driver->queue, hydration_valid_buffer, CL_TRUE, 0u, batch->hydration_count, hydration_each, 0u, NULL, NULL) != CL_SUCCESS) {
            result = HHS_PASS207_ERR_BACKEND_FAILURE;
            hhs_set_error(driver, "OpenCL hydration result download failed");
            goto cleanup;
        }
        driver->status.output_bytes_downloaded += batch->hydration_count;
        for (index = 0u; index < batch->hydration_count; ++index) {
            while (batch_index + 1u < batch->batch_size && index >= batch->hydration_offsets[batch_index + 1u]) {
                batch_index += 1u;
            }
            if (hydration_each[index] == 0u) {
                output->hydration_valid[batch_index] = 0u;
            }
        }
        for (batch_index = 0u; batch_index < batch->batch_size; ++batch_index) {
            if (output->hydration_valid[batch_index] == 0u) {
                result = HHS_PASS207_ERR_HYDRATION_MISMATCH;
                hhs_set_error(driver, "GPU hydration q-address validation failed");
                goto cleanup;
            }
        }
    }
    if (driver->config.verify_against_cpu != 0u) {
        if (!hhs_compare_cpu(batch, output)) {
            result = HHS_PASS207_ERR_CPU_VERIFICATION;
            hhs_set_error(driver, "GPU result differs from exact CPU VM5184 oracle");
            goto cleanup;
        }
        driver->status.verified_against_cpu = 1u;
    }

    if (hhs_key_present(batch->input_cache_key) && driver->status.cache_input_hit == 0u) {
        if (cached_state == NULL) {
            cl_mem retained = state_buffer;
            state_buffer = NULL;
            (void)hhs_cache_store_locked(driver, batch->input_cache_key, HHS_PASS207_CACHE_STATE_SOA, batch->state_soa, state_bytes, retained);
        }
        if (cached_projection == NULL) {
            cl_mem retained = projection_buffer;
            projection_buffer = NULL;
            (void)hhs_cache_store_locked(driver, batch->input_cache_key, HHS_PASS207_CACHE_PROJECTION_SOA, batch->projection_soa, projection_bytes, retained);
        }
    }
    if (batch->retain_outputs != 0u && hhs_key_present(batch->output_cache_key)) {
        cl_mem retained_state = child_state_buffer;
        cl_mem retained_projection = child_projection_buffer;
        child_state_buffer = NULL;
        child_projection_buffer = NULL;
        if (hhs_cache_store_locked(driver, batch->output_cache_key, HHS_PASS207_CACHE_CHILD_STATE_SOA, output->child_state_soa, state_bytes, retained_state) == HHS_PASS207_OK
            && hhs_cache_store_locked(driver, batch->output_cache_key, HHS_PASS207_CACHE_CHILD_PROJECTION_SOA, output->child_projection_soa, projection_bytes, retained_projection) == HHS_PASS207_OK) {
            driver->status.cache_output_retained = 1u;
        }
    }

cleanup:
    free(hydration_each);
    if (hydration_valid_buffer != NULL) (void)driver->cl.ReleaseMemObject(hydration_valid_buffer);
    if (frontier_buffer != NULL) (void)driver->cl.ReleaseMemObject(frontier_buffer);
    if (child_projection_buffer != NULL) (void)driver->cl.ReleaseMemObject(child_projection_buffer);
    if (lane_frontier_buffer != NULL) (void)driver->cl.ReleaseMemObject(lane_frontier_buffer);
    if (lane_bits_buffer != NULL) (void)driver->cl.ReleaseMemObject(lane_bits_buffer);
    if (child_state_buffer != NULL) (void)driver->cl.ReleaseMemObject(child_state_buffer);
    if (hydration_q_buffer != NULL) (void)driver->cl.ReleaseMemObject(hydration_q_buffer);
    if (hydration_offsets_buffer != NULL) (void)driver->cl.ReleaseMemObject(hydration_offsets_buffer);
    if (delta_masks_buffer != NULL) (void)driver->cl.ReleaseMemObject(delta_masks_buffer);
    if (delta_controls_buffer != NULL) (void)driver->cl.ReleaseMemObject(delta_controls_buffer);
    if (delta_cells_buffer != NULL) (void)driver->cl.ReleaseMemObject(delta_cells_buffer);
    if (delta_offsets_buffer != NULL) (void)driver->cl.ReleaseMemObject(delta_offsets_buffer);
    if (projection_buffer != NULL && (cached_projection == NULL || projection_buffer != cached_projection->device_buffer)) (void)driver->cl.ReleaseMemObject(projection_buffer);
    if (state_buffer != NULL && (cached_state == NULL || state_buffer != cached_state->device_buffer)) (void)driver->cl.ReleaseMemObject(state_buffer);
    return result;
}
