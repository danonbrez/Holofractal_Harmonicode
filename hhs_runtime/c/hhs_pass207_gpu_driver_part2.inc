static void* hhs_open_library(void) {
#if defined(_WIN32)
    return (void*)LoadLibraryA("OpenCL.dll");
#elif defined(__APPLE__)
    return dlopen("/System/Library/Frameworks/OpenCL.framework/OpenCL", RTLD_NOW | RTLD_LOCAL);
#else
    void* library = dlopen("libOpenCL.so.1", RTLD_NOW | RTLD_LOCAL);
    if (library == NULL) {
        library = dlopen("libOpenCL.so", RTLD_NOW | RTLD_LOCAL);
    }
    return library;
#endif
}

static void hhs_close_library(HHSOpenCLLibrary library) {
    if (library == NULL) {
        return;
    }
#if defined(_WIN32)
    (void)FreeLibrary(library);
#else
    (void)dlclose(library);
#endif
}

static void* hhs_load_symbol(HHSOpenCLLibrary library, const char* name) {
#if defined(_WIN32)
    return (void*)GetProcAddress(library, name);
#else
    return dlsym(library, name);
#endif
}

#define HHS_LOAD_CL(api, field, symbol_name) \
    do { \
        void* hhs_symbol_pointer = hhs_load_symbol((api)->library, (symbol_name)); \
        if (hhs_symbol_pointer == NULL) { return 0u; } \
        memcpy(&(api)->field, &hhs_symbol_pointer, sizeof((api)->field)); \
    } while (0)

static uint8_t hhs_load_opencl(HHSOpenCLAPI* api) {
    if (api == NULL) {
        return 0u;
    }
    memset(api, 0, sizeof(*api));
    api->library = (HHSOpenCLLibrary)hhs_open_library();
    if (api->library == NULL) {
        return 0u;
    }
    HHS_LOAD_CL(api, GetPlatformIDs, "clGetPlatformIDs");
    HHS_LOAD_CL(api, GetDeviceIDs, "clGetDeviceIDs");
    HHS_LOAD_CL(api, GetDeviceInfo, "clGetDeviceInfo");
    HHS_LOAD_CL(api, CreateContext, "clCreateContext");
    HHS_LOAD_CL(api, CreateCommandQueue, "clCreateCommandQueue");
    HHS_LOAD_CL(api, CreateProgramWithSource, "clCreateProgramWithSource");
    HHS_LOAD_CL(api, BuildProgram, "clBuildProgram");
    HHS_LOAD_CL(api, GetProgramBuildInfo, "clGetProgramBuildInfo");
    HHS_LOAD_CL(api, CreateKernel, "clCreateKernel");
    HHS_LOAD_CL(api, CreateBuffer, "clCreateBuffer");
    HHS_LOAD_CL(api, SetKernelArg, "clSetKernelArg");
    HHS_LOAD_CL(api, EnqueueWriteBuffer, "clEnqueueWriteBuffer");
    HHS_LOAD_CL(api, EnqueueReadBuffer, "clEnqueueReadBuffer");
    HHS_LOAD_CL(api, EnqueueNDRangeKernel, "clEnqueueNDRangeKernel");
    HHS_LOAD_CL(api, Finish, "clFinish");
    HHS_LOAD_CL(api, ReleaseMemObject, "clReleaseMemObject");
    HHS_LOAD_CL(api, ReleaseKernel, "clReleaseKernel");
    HHS_LOAD_CL(api, ReleaseProgram, "clReleaseProgram");
    HHS_LOAD_CL(api, ReleaseCommandQueue, "clReleaseCommandQueue");
    HHS_LOAD_CL(api, ReleaseContext, "clReleaseContext");
    return 1u;
}

#undef HHS_LOAD_CL

static void hhs_release_opencl(HHSPass207GPUDriver* driver) {
    if (driver == NULL) {
        return;
    }
    if (driver->vector_kernel != NULL) {
        (void)driver->cl.ReleaseKernel(driver->vector_kernel);
    }
    if (driver->hydration_kernel != NULL) {
        (void)driver->cl.ReleaseKernel(driver->hydration_kernel);
    }
    if (driver->projection_kernel != NULL) {
        (void)driver->cl.ReleaseKernel(driver->projection_kernel);
    }
    if (driver->pack_kernel != NULL) {
        (void)driver->cl.ReleaseKernel(driver->pack_kernel);
    }
    if (driver->apply_kernel != NULL) {
        (void)driver->cl.ReleaseKernel(driver->apply_kernel);
    }
    if (driver->program != NULL) {
        (void)driver->cl.ReleaseProgram(driver->program);
    }
    if (driver->queue != NULL) {
        (void)driver->cl.ReleaseCommandQueue(driver->queue);
    }
    if (driver->context != NULL) {
        (void)driver->cl.ReleaseContext(driver->context);
    }
    hhs_close_library(driver->cl.library);
    memset(&driver->cl, 0, sizeof(driver->cl));
    driver->vector_kernel = NULL;
    driver->hydration_kernel = NULL;
    driver->projection_kernel = NULL;
    driver->pack_kernel = NULL;
    driver->apply_kernel = NULL;
    driver->program = NULL;
    driver->queue = NULL;
    driver->context = NULL;
    driver->device = NULL;
    driver->platform = NULL;
}

static uint8_t hhs_initialize_opencl(HHSPass207GPUDriver* driver) {
    cl_uint platform_count = 0u;
    cl_uint device_total = 0u;
    cl_platform_id* platforms = NULL;
    cl_device_id* devices = NULL;
    cl_int status = CL_SUCCESS;
    uint32_t selected = driver->config.device_index;
    const char* sources[2] = {
        HHS_PASS207_OPENCL_SOURCE_PART1,
        HHS_PASS207_OPENCL_SOURCE_PART2,
    };
    const size_t source_sizes[2] = {
        strlen(HHS_PASS207_OPENCL_SOURCE_PART1),
        strlen(HHS_PASS207_OPENCL_SOURCE_PART2),
    };
    char build_log[4096];
    size_t log_size = 0u;
    uint32_t platform_index;
    uint32_t flattened_index = 0u;

    if (!hhs_load_opencl(&driver->cl)) {
        hhs_set_error(driver, "OpenCL loader unavailable");
        return 0u;
    }
    status = driver->cl.GetPlatformIDs(0u, NULL, &platform_count);
    if (status != CL_SUCCESS || platform_count == 0u) {
        hhs_set_error(driver, "OpenCL reports no platforms");
        hhs_release_opencl(driver);
        return 0u;
    }
    platforms = (cl_platform_id*)calloc(platform_count, sizeof(*platforms));
    if (platforms == NULL) {
        hhs_release_opencl(driver);
        return 0u;
    }
    status = driver->cl.GetPlatformIDs(platform_count, platforms, NULL);
    if (status != CL_SUCCESS) {
        free(platforms);
        hhs_release_opencl(driver);
        return 0u;
    }
    for (platform_index = 0u; platform_index < platform_count; ++platform_index) {
        cl_uint count = 0u;
        status = driver->cl.GetDeviceIDs(platforms[platform_index], CL_DEVICE_TYPE_GPU, 0u, NULL, &count);
        if (status == CL_SUCCESS) {
            device_total += count;
        }
    }
    driver->status.platform_count = platform_count;
    driver->status.device_count = device_total;
    if (device_total == 0u || selected >= device_total) {
        free(platforms);
        hhs_set_error(driver, "OpenCL reports no selectable physical GPU device");
        hhs_release_opencl(driver);
        return 0u;
    }
    devices = (cl_device_id*)calloc(device_total, sizeof(*devices));
    if (devices == NULL) {
        free(platforms);
        hhs_release_opencl(driver);
        return 0u;
    }
    for (platform_index = 0u; platform_index < platform_count; ++platform_index) {
        cl_uint count = 0u;
        status = driver->cl.GetDeviceIDs(platforms[platform_index], CL_DEVICE_TYPE_GPU, 0u, NULL, &count);
        if (status == CL_SUCCESS && count > 0u) {
            cl_device_id* local = (cl_device_id*)calloc(count, sizeof(*local));
            cl_uint local_index;
            if (local == NULL) {
                free(devices);
                free(platforms);
                hhs_release_opencl(driver);
                return 0u;
            }
            status = driver->cl.GetDeviceIDs(platforms[platform_index], CL_DEVICE_TYPE_GPU, count, local, NULL);
            if (status != CL_SUCCESS) {
                free(local);
                continue;
            }
            for (local_index = 0u; local_index < count; ++local_index) {
                devices[flattened_index] = local[local_index];
                if (flattened_index == selected) {
                    driver->platform = platforms[platform_index];
                }
                flattened_index += 1u;
            }
            free(local);
        }
    }
    driver->device = devices[selected];
    free(devices);
    free(platforms);
    {
        size_t maximum_workgroup = 0u;
        status = driver->cl.GetDeviceInfo(
            driver->device,
            CL_DEVICE_MAX_WORK_GROUP_SIZE,
            sizeof(maximum_workgroup),
            &maximum_workgroup,
            NULL
        );
        if (status != CL_SUCCESS || maximum_workgroup < HHS_PASS207_DEFAULT_WORKGROUP) {
            hhs_set_error(driver, "OpenCL GPU cannot host the required 64-lane VM81 workgroup");
            hhs_release_opencl(driver);
            return 0u;
        }
    }

    driver->context = driver->cl.CreateContext(NULL, 1u, &driver->device, NULL, NULL, &status);
    if (driver->context == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL context creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->queue = driver->cl.CreateCommandQueue(driver->context, driver->device, 0u, &status);
    if (driver->queue == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL command queue creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->program = driver->cl.CreateProgramWithSource(driver->context, 2u, sources, source_sizes, &status);
    if (driver->program == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL program creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    status = driver->cl.BuildProgram(driver->program, 1u, &driver->device, "-cl-std=CL1.2", NULL, NULL);
    if (status != CL_SUCCESS) {
        memset(build_log, 0, sizeof(build_log));
        (void)driver->cl.GetProgramBuildInfo(driver->program, driver->device, CL_PROGRAM_BUILD_LOG, sizeof(build_log) - 1u, build_log, &log_size);
        hhs_set_error(driver, log_size > 0u ? build_log : "OpenCL kernel build failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->apply_kernel = driver->cl.CreateKernel(driver->program, "hhs_vm81_hyperthreads", &status);
    if (driver->apply_kernel == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL VM81 hyperthread kernel creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->pack_kernel = driver->cl.CreateKernel(driver->program, "hhs_pack_vm81_state", &status);
    if (driver->pack_kernel == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL VM81 canonical pack kernel creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->projection_kernel = driver->cl.CreateKernel(driver->program, "hhs_project_sparse", &status);
    if (driver->projection_kernel == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL projection kernel creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->hydration_kernel = driver->cl.CreateKernel(driver->program, "hhs_validate_hydration", &status);
    if (driver->hydration_kernel == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL hydration kernel creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    driver->vector_kernel = driver->cl.CreateKernel(driver->program, "hhs_vector_distance72", &status);
    if (driver->vector_kernel == NULL || status != CL_SUCCESS) {
        hhs_set_error(driver, "OpenCL vector kernel creation failed");
        hhs_release_opencl(driver);
        return 0u;
    }
    memset(driver->status.device_name, 0, sizeof(driver->status.device_name));
    (void)driver->cl.GetDeviceInfo(driver->device, CL_DEVICE_NAME, sizeof(driver->status.device_name) - 1u, driver->status.device_name, NULL);
    driver->status.selected_backend = HHS_PASS207_BACKEND_OPENCL;
    driver->status.physical_gpu = 1u;
    driver->status.device_index = selected;
    hhs_copy_text(driver->status.backend_name, sizeof(driver->status.backend_name), "OPENCL_GPU");
    driver->status.last_error[0] = '\0';
    return 1u;
}
