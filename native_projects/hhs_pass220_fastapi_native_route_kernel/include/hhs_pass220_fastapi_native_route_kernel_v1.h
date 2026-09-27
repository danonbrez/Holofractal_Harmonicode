#ifndef HHS_PASS220_FASTAPI_NATIVE_ROUTE_KERNEL_V1_H
#define HHS_PASS220_FASTAPI_NATIVE_ROUTE_KERNEL_V1_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION 1U
#define HHS_FASTAPI_NATIVE_MAX_ROUTES 512U
#define HHS_FASTAPI_NATIVE_MAX_PATH_BYTES 384U
#define HHS_FASTAPI_NATIVE_MAX_CAPTURES_BYTES 1024U

typedef enum HHSFastAPINativeStatusV1 {
    HHS_FASTAPI_NATIVE_OK = 0,
    HHS_FASTAPI_NATIVE_ERR_ARGUMENT = 1,
    HHS_FASTAPI_NATIVE_ERR_CAPACITY = 2,
    HHS_FASTAPI_NATIVE_ERR_PATH = 3,
    HHS_FASTAPI_NATIVE_ERR_DUPLICATE = 4,
    HHS_FASTAPI_NATIVE_ERR_NOT_FOUND = 5,
    HHS_FASTAPI_NATIVE_ERR_CAPTURE_CAPACITY = 6
} HHSFastAPINativeStatusV1;

typedef enum HHSFastAPINativeMethodV1 {
    HHS_FASTAPI_NATIVE_METHOD_GET = 1,
    HHS_FASTAPI_NATIVE_METHOD_POST = 2,
    HHS_FASTAPI_NATIVE_METHOD_PUT = 3,
    HHS_FASTAPI_NATIVE_METHOD_PATCH = 4,
    HHS_FASTAPI_NATIVE_METHOD_DELETE = 5,
    HHS_FASTAPI_NATIVE_METHOD_OPTIONS = 6,
    HHS_FASTAPI_NATIVE_METHOD_HEAD = 7,
    HHS_FASTAPI_NATIVE_METHOD_WEBSOCKET = 8
} HHSFastAPINativeMethodV1;

typedef struct HHSFastAPINativeRouteV1 {
    uint32_t method;
    uint32_t handler_id;
    uint32_t flags;
    uint32_t reserved;
    char path[HHS_FASTAPI_NATIVE_MAX_PATH_BYTES];
} HHSFastAPINativeRouteV1;

typedef struct HHSFastAPINativeRegistryV1 {
    uint32_t version;
    uint32_t route_count;
    HHSFastAPINativeRouteV1 routes[HHS_FASTAPI_NATIVE_MAX_ROUTES];
} HHSFastAPINativeRegistryV1;

typedef struct HHSFastAPINativeResolutionV1 {
    uint32_t matched;
    uint32_t route_index;
    uint32_t handler_id;
    uint32_t capture_bytes;
    char captures[HHS_FASTAPI_NATIVE_MAX_CAPTURES_BYTES];
} HHSFastAPINativeResolutionV1;

uint32_t hhs_fastapi_native_route_kernel_version(void);

HHSFastAPINativeStatusV1 hhs_fastapi_native_registry_init(
    HHSFastAPINativeRegistryV1 *registry
);

HHSFastAPINativeStatusV1 hhs_fastapi_native_register(
    HHSFastAPINativeRegistryV1 *registry,
    uint32_t method,
    const char *path,
    uint32_t handler_id,
    uint32_t flags
);

HHSFastAPINativeStatusV1 hhs_fastapi_native_resolve(
    const HHSFastAPINativeRegistryV1 *registry,
    uint32_t method,
    const char *path,
    HHSFastAPINativeResolutionV1 *out
);

uint64_t hhs_fastapi_native_registry_fingerprint(
    const HHSFastAPINativeRegistryV1 *registry
);

#ifdef __cplusplus
}
#endif

#endif
