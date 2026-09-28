#include "hhs_pass220_fastapi_native_route_kernel_v1.h"

#include <limits.h>

static size_t hhs_strlen(const char *s) {
    size_t n = 0U;
    if (s == NULL) return 0U;
    while (s[n] != '\0') ++n;
    return n;
}

static void hhs_zero(void *ptr, size_t n) {
    uint8_t *p = (uint8_t *)ptr;
    size_t i;
    for (i = 0U; i < n; ++i) p[i] = 0U;
}

static int hhs_streq(const char *a, const char *b) {
    size_t i = 0U;
    if (a == NULL || b == NULL) return 0;
    while (a[i] != '\0' && b[i] != '\0') {
        if (a[i] != b[i]) return 0;
        ++i;
    }
    return a[i] == b[i];
}

static int method_valid(uint32_t method) {
    return method >= HHS_FASTAPI_NATIVE_METHOD_GET
        && method <= HHS_FASTAPI_NATIVE_METHOD_WEBSOCKET;
}

static int path_valid(const char *path) {
    size_t n;
    if (path == NULL || path[0] != '/') return 0;
    n = hhs_strlen(path);
    return n > 0U && n < HHS_FASTAPI_NATIVE_MAX_PATH_BYTES;
}

static void copy_path(char *dst, const char *src) {
    size_t i = 0U;
    while (src[i] != '\0' && i + 1U < HHS_FASTAPI_NATIVE_MAX_PATH_BYTES) {
        dst[i] = src[i];
        ++i;
    }
    dst[i] = '\0';
}

static int segment_equal(
    const char *a,
    size_t a_start,
    size_t a_end,
    const char *b,
    size_t b_start,
    size_t b_end
) {
    size_t i;
    const size_t a_len = a_end - a_start;
    const size_t b_len = b_end - b_start;
    if (a_len != b_len) return 0;
    for (i = 0U; i < a_len; ++i) {
        if (a[a_start + i] != b[b_start + i]) return 0;
    }
    return 1;
}

static int append_capture(
    HHSFastAPINativeResolutionV1 *out,
    const char *name,
    size_t name_start,
    size_t name_end,
    const char *value,
    size_t value_start,
    size_t value_end
) {
    size_t i;
    const size_t name_len = name_end - name_start;
    const size_t value_len = value_end - value_start;
    const size_t need = name_len + 1U + value_len + 1U;
    size_t pos = (size_t)out->capture_bytes;
    if (pos + need >= HHS_FASTAPI_NATIVE_MAX_CAPTURES_BYTES) return 0;

    for (i = 0U; i < name_len; ++i) out->captures[pos++] = name[name_start + i];
    out->captures[pos++] = '=';
    for (i = 0U; i < value_len; ++i) out->captures[pos++] = value[value_start + i];
    out->captures[pos++] = '\n';
    out->captures[pos] = '\0';
    out->capture_bytes = (uint32_t)pos;
    return 1;
}

static int is_path_capture(
    const char *pattern,
    size_t start,
    size_t end,
    size_t *name_end
) {
    size_t i;
    if (end <= start + 2U || pattern[start] != '{' || pattern[end - 1U] != '}') {
        return 0;
    }
    for (i = start + 1U; i + 5U < end; ++i) {
        if (pattern[i] == ':'
            && pattern[i + 1U] == 'p'
            && pattern[i + 2U] == 'a'
            && pattern[i + 3U] == 't'
            && pattern[i + 4U] == 'h'
            && i + 5U == end - 1U) {
            *name_end = i;
            return 1;
        }
    }
    return 0;
}

static int is_single_capture(
    const char *pattern,
    size_t start,
    size_t end
) {
    size_t i;
    if (end <= start + 2U || pattern[start] != '{' || pattern[end - 1U] != '}') {
        return 0;
    }
    for (i = start + 1U; i < end - 1U; ++i) {
        if (pattern[i] == ':' || pattern[i] == '{' || pattern[i] == '}') return 0;
    }
    return 1;
}

static int route_match(
    const char *pattern,
    const char *path,
    HHSFastAPINativeResolutionV1 *out
) {
    size_t pp = 1U;
    size_t sp = 1U;
    const size_t pn = hhs_strlen(pattern);
    const size_t sn = hhs_strlen(path);

    if (pn == 1U && sn == 1U) return 1;

    while (pp <= pn && sp <= sn) {
        size_t pe = pp;
        size_t se = sp;
        size_t name_end = 0U;

        while (pe < pn && pattern[pe] != '/') ++pe;
        while (se < sn && path[se] != '/') ++se;

        if (is_path_capture(pattern, pp, pe, &name_end)) {
            if (sp >= sn) return 0;
            if (!append_capture(out, pattern, pp + 1U, name_end, path, sp, sn)) return -1;
            pp = pn;
            sp = sn;
            break;
        }

        if (is_single_capture(pattern, pp, pe)) {
            if (se <= sp) return 0;
            if (!append_capture(out, pattern, pp + 1U, pe - 1U, path, sp, se)) return -1;
        } else if (!segment_equal(pattern, pp, pe, path, sp, se)) {
            return 0;
        }

        if (pe == pn && se == sn) {
            pp = pe;
            sp = se;
            break;
        }
        if ((pe == pn) != (se == sn)) return 0;

        pp = pe + 1U;
        sp = se + 1U;
    }

    return pp == pn && sp == sn;
}

uint32_t hhs_fastapi_native_route_kernel_version(void) {
    return HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION;
}

HHSFastAPINativeStatusV1 hhs_fastapi_native_registry_init(
    HHSFastAPINativeRegistryV1 *registry
) {
    if (registry == NULL) return HHS_FASTAPI_NATIVE_ERR_ARGUMENT;
    hhs_zero(registry, sizeof(*registry));
    registry->version = HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION;
    return HHS_FASTAPI_NATIVE_OK;
}

HHSFastAPINativeStatusV1 hhs_fastapi_native_register(
    HHSFastAPINativeRegistryV1 *registry,
    uint32_t method,
    const char *path,
    uint32_t handler_id,
    uint32_t flags
) {
    uint32_t i;
    HHSFastAPINativeRouteV1 *route;

    if (registry == NULL || !method_valid(method) || !path_valid(path) || handler_id == 0U) {
        return HHS_FASTAPI_NATIVE_ERR_ARGUMENT;
    }
    if (registry->version != HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION) {
        return HHS_FASTAPI_NATIVE_ERR_ARGUMENT;
    }
    if (registry->route_count >= HHS_FASTAPI_NATIVE_MAX_ROUTES) {
        return HHS_FASTAPI_NATIVE_ERR_CAPACITY;
    }
    for (i = 0U; i < registry->route_count; ++i) {
        if (registry->routes[i].method == method && hhs_streq(registry->routes[i].path, path)) {
            return HHS_FASTAPI_NATIVE_ERR_DUPLICATE;
        }
    }

    route = &registry->routes[registry->route_count];
    hhs_zero(route, sizeof(*route));
    route->method = method;
    route->handler_id = handler_id;
    route->flags = flags;
    copy_path(route->path, path);
    registry->route_count += 1U;
    return HHS_FASTAPI_NATIVE_OK;
}

HHSFastAPINativeStatusV1 hhs_fastapi_native_resolve(
    const HHSFastAPINativeRegistryV1 *registry,
    uint32_t method,
    const char *path,
    HHSFastAPINativeResolutionV1 *out
) {
    uint32_t i;
    if (registry == NULL || out == NULL || !method_valid(method) || !path_valid(path)) {
        return HHS_FASTAPI_NATIVE_ERR_ARGUMENT;
    }
    hhs_zero(out, sizeof(*out));

    for (i = 0U; i < registry->route_count; ++i) {
        int matched;
        if (registry->routes[i].method != method) continue;
        hhs_zero(out, sizeof(*out));
        matched = route_match(registry->routes[i].path, path, out);
        if (matched < 0) {
            hhs_zero(out, sizeof(*out));
            return HHS_FASTAPI_NATIVE_ERR_CAPTURE_CAPACITY;
        }
        if (matched) {
            out->matched = 1U;
            out->route_index = i;
            out->handler_id = registry->routes[i].handler_id;
            return HHS_FASTAPI_NATIVE_OK;
        }
    }
    hhs_zero(out, sizeof(*out));
    return HHS_FASTAPI_NATIVE_ERR_NOT_FOUND;
}

uint64_t hhs_fastapi_native_registry_fingerprint(
    const HHSFastAPINativeRegistryV1 *registry
) {
    uint64_t h = UINT64_C(14695981039346656037);
    uint32_t i;
    if (registry == NULL || registry->version != HHS_FASTAPI_NATIVE_ROUTE_KERNEL_VERSION) {
        return 0U;
    }
    for (i = 0U; i < registry->route_count; ++i) {
        const HHSFastAPINativeRouteV1 *route = &registry->routes[i];
        const uint8_t fields[12] = {
            (uint8_t)(route->method & 0xffU),
            (uint8_t)((route->method >> 8) & 0xffU),
            (uint8_t)((route->method >> 16) & 0xffU),
            (uint8_t)((route->method >> 24) & 0xffU),
            (uint8_t)(route->handler_id & 0xffU),
            (uint8_t)((route->handler_id >> 8) & 0xffU),
            (uint8_t)((route->handler_id >> 16) & 0xffU),
            (uint8_t)((route->handler_id >> 24) & 0xffU),
            (uint8_t)(route->flags & 0xffU),
            (uint8_t)((route->flags >> 8) & 0xffU),
            (uint8_t)((route->flags >> 16) & 0xffU),
            (uint8_t)((route->flags >> 24) & 0xffU)
        };
        size_t j;
        const size_t n = hhs_strlen(route->path);
        for (j = 0U; j < sizeof(fields); ++j) {
            h ^= (uint64_t)fields[j];
            h *= UINT64_C(1099511628211);
        }
        for (j = 0U; j < n; ++j) {
            h ^= (uint64_t)(uint8_t)route->path[j];
            h *= UINT64_C(1099511628211);
        }
        h ^= UINT64_C(0xff);
        h *= UINT64_C(1099511628211);
    }
    return h;
}
