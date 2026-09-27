#include "hhs_pass220_fastapi_native_route_kernel_v1.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    HHSFastAPINativeRegistryV1 registry;
    HHSFastAPINativeResolutionV1 out;
    uint64_t fingerprint;

    assert(hhs_fastapi_native_registry_init(&registry) == HHS_FASTAPI_NATIVE_OK);
    assert(hhs_fastapi_native_route_kernel_version() == 1U);

    assert(hhs_fastapi_native_register(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/runtime/graphics/status",
        101U,
        0U
    ) == HHS_FASTAPI_NATIVE_OK);

    assert(hhs_fastapi_native_register(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/items/{item_id}",
        102U,
        0U
    ) == HHS_FASTAPI_NATIVE_OK);

    assert(hhs_fastapi_native_register(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/files/{rest:path}",
        103U,
        0U
    ) == HHS_FASTAPI_NATIVE_OK);

    assert(hhs_fastapi_native_register(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/runtime/graphics/status",
        104U,
        0U
    ) == HHS_FASTAPI_NATIVE_ERR_DUPLICATE);

    assert(hhs_fastapi_native_resolve(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/runtime/graphics/status",
        &out
    ) == HHS_FASTAPI_NATIVE_OK);
    assert(out.handler_id == 101U);
    assert(out.capture_bytes == 0U);

    assert(hhs_fastapi_native_resolve(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/items/5184",
        &out
    ) == HHS_FASTAPI_NATIVE_OK);
    assert(out.handler_id == 102U);
    assert(strcmp(out.captures, "item_id=5184\n") == 0);

    assert(hhs_fastapi_native_resolve(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_GET,
        "/api/files/a/b/c",
        &out
    ) == HHS_FASTAPI_NATIVE_OK);
    assert(out.handler_id == 103U);
    assert(strcmp(out.captures, "rest=a/b/c\n") == 0);

    assert(hhs_fastapi_native_resolve(
        &registry,
        HHS_FASTAPI_NATIVE_METHOD_POST,
        "/api/runtime/graphics/status",
        &out
    ) == HHS_FASTAPI_NATIVE_ERR_NOT_FOUND);

    fingerprint = hhs_fastapi_native_registry_fingerprint(&registry);
    assert(fingerprint != 0U);
    assert(registry.route_count == 3U);

    puts("PASS hhs_pass220_fastapi_native_route_kernel_v1");
    return 0;
}
