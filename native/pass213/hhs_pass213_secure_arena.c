#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/prctl.h>
#include <unistd.h>

#ifndef MADV_DONTDUMP
#define MADV_DONTDUMP 16
#endif

#ifndef MADV_DONTFORK
#define MADV_DONTFORK 10
#endif

enum {
    HHS_SECURE_OK = 0,
    HHS_SECURE_EINVAL = -1,
    HHS_SECURE_ENOMEM = -2,
    HHS_SECURE_EMMAP = -3,
    HHS_SECURE_EMPROTECT = -4,
    HHS_SECURE_EMLOCK = -5,
    HHS_SECURE_EMADVISE = -6,
    HHS_SECURE_EOWNER = -7,
    HHS_SECURE_EBOUNDS = -8,
    HHS_SECURE_ESEALED = -9,
    HHS_SECURE_ESTATE = -10,
    HHS_SECURE_EPRCTL = -11
};

typedef struct hhs_secure_arena {
    void *mapping;
    uint8_t *data;
    size_t requested_size;
    size_t usable_size;
    size_t mapping_size;
    size_t page_size;
    uint8_t owner_token[32];
    uint64_t mutation_sequence;
    int locked;
    int dontdump;
    int dontfork;
    int sealed;
    int zeroized;
} hhs_secure_arena;

typedef struct hhs_secure_arena_status {
    size_t requested_size;
    size_t usable_size;
    size_t mapping_size;
    size_t page_size;
    uint64_t mutation_sequence;
    int locked;
    int dontdump;
    int dontfork;
    int sealed;
    int zeroized;
    int guard_pages;
} hhs_secure_arena_status;

static void hhs_explicit_zero(void *pointer, size_t length) {
    volatile uint8_t *cursor = (volatile uint8_t *)pointer;
    while (length-- > 0) {
        *cursor++ = 0;
    }
    __asm__ __volatile__("" : : "r"(pointer) : "memory");
}

static int hhs_owner_equal(const uint8_t left[32], const uint8_t right[32]) {
    uint8_t difference = 0;
    size_t index;
    for (index = 0; index < 32; ++index) {
        difference |= (uint8_t)(left[index] ^ right[index]);
    }
    return difference == 0;
}

static size_t hhs_round_up(size_t value, size_t alignment) {
    if (alignment == 0 || value > SIZE_MAX - (alignment - 1)) {
        return 0;
    }
    return ((value + alignment - 1) / alignment) * alignment;
}

int hhs_secure_process_harden(void) {
    if (prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) {
        return HHS_SECURE_EPRCTL;
    }
    return HHS_SECURE_OK;
}

int hhs_secure_arena_create(
    size_t requested_size,
    const uint8_t owner_token[32],
    hhs_secure_arena **out_arena
) {
    long page_size_long;
    size_t page_size;
    size_t usable_size;
    size_t mapping_size;
    void *mapping;
    uint8_t *data;
    hhs_secure_arena *arena;

    if (requested_size == 0 || owner_token == NULL || out_arena == NULL) {
        return HHS_SECURE_EINVAL;
    }
    *out_arena = NULL;

    page_size_long = sysconf(_SC_PAGESIZE);
    if (page_size_long <= 0) {
        return HHS_SECURE_ESTATE;
    }
    page_size = (size_t)page_size_long;
    usable_size = hhs_round_up(requested_size, page_size);
    if (usable_size == 0 || usable_size > SIZE_MAX - 2 * page_size) {
        return HHS_SECURE_EINVAL;
    }
    mapping_size = usable_size + 2 * page_size;

    mapping = mmap(
        NULL,
        mapping_size,
        PROT_NONE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );
    if (mapping == MAP_FAILED) {
        return HHS_SECURE_EMMAP;
    }

    data = (uint8_t *)mapping + page_size;
    if (mprotect(data, usable_size, PROT_READ | PROT_WRITE) != 0) {
        munmap(mapping, mapping_size);
        return HHS_SECURE_EMPROTECT;
    }
    if (mlock(data, usable_size) != 0) {
        hhs_explicit_zero(data, usable_size);
        munmap(mapping, mapping_size);
        return HHS_SECURE_EMLOCK;
    }
    if (madvise(data, usable_size, MADV_DONTDUMP) != 0) {
        hhs_explicit_zero(data, usable_size);
        munlock(data, usable_size);
        munmap(mapping, mapping_size);
        return HHS_SECURE_EMADVISE;
    }
    if (madvise(data, usable_size, MADV_DONTFORK) != 0) {
        hhs_explicit_zero(data, usable_size);
        munlock(data, usable_size);
        munmap(mapping, mapping_size);
        return HHS_SECURE_EMADVISE;
    }

    arena = (hhs_secure_arena *)calloc(1, sizeof(*arena));
    if (arena == NULL) {
        hhs_explicit_zero(data, usable_size);
        munlock(data, usable_size);
        munmap(mapping, mapping_size);
        return HHS_SECURE_ENOMEM;
    }

    hhs_explicit_zero(data, usable_size);
    arena->mapping = mapping;
    arena->data = data;
    arena->requested_size = requested_size;
    arena->usable_size = usable_size;
    arena->mapping_size = mapping_size;
    arena->page_size = page_size;
    memcpy(arena->owner_token, owner_token, 32);
    arena->mutation_sequence = 0;
    arena->locked = 1;
    arena->dontdump = 1;
    arena->dontfork = 1;
    arena->sealed = 0;
    arena->zeroized = 1;
    *out_arena = arena;
    return HHS_SECURE_OK;
}

static int hhs_secure_arena_authorize(
    const hhs_secure_arena *arena,
    const uint8_t owner_token[32]
) {
    if (arena == NULL || owner_token == NULL || arena->data == NULL) {
        return HHS_SECURE_EINVAL;
    }
    if (!hhs_owner_equal(arena->owner_token, owner_token)) {
        return HHS_SECURE_EOWNER;
    }
    return HHS_SECURE_OK;
}

int hhs_secure_arena_write(
    hhs_secure_arena *arena,
    const uint8_t owner_token[32],
    size_t offset,
    const void *source,
    size_t length
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (arena->sealed) {
        return HHS_SECURE_ESEALED;
    }
    if (source == NULL || offset > arena->requested_size ||
        length > arena->requested_size - offset) {
        return HHS_SECURE_EBOUNDS;
    }
    if (length > 0) {
        memcpy(arena->data + offset, source, length);
        arena->zeroized = 0;
        arena->mutation_sequence += 1;
    }
    return HHS_SECURE_OK;
}

int hhs_secure_arena_read(
    const hhs_secure_arena *arena,
    const uint8_t owner_token[32],
    size_t offset,
    void *destination,
    size_t length
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (destination == NULL || offset > arena->requested_size ||
        length > arena->requested_size - offset) {
        return HHS_SECURE_EBOUNDS;
    }
    if (length > 0) {
        memcpy(destination, arena->data + offset, length);
    }
    return HHS_SECURE_OK;
}

int hhs_secure_arena_seal(
    hhs_secure_arena *arena,
    const uint8_t owner_token[32]
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (arena->sealed) {
        return HHS_SECURE_OK;
    }
    if (mprotect(arena->data, arena->usable_size, PROT_READ) != 0) {
        return HHS_SECURE_EMPROTECT;
    }
    arena->sealed = 1;
    arena->mutation_sequence += 1;
    return HHS_SECURE_OK;
}

int hhs_secure_arena_zeroize(
    hhs_secure_arena *arena,
    const uint8_t owner_token[32]
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    int was_sealed;
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    was_sealed = arena->sealed;
    if (was_sealed) {
        if (mprotect(arena->data, arena->usable_size, PROT_READ | PROT_WRITE) != 0) {
            return HHS_SECURE_EMPROTECT;
        }
    }
    hhs_explicit_zero(arena->data, arena->usable_size);
    arena->zeroized = 1;
    arena->mutation_sequence += 1;
    if (was_sealed) {
        if (mprotect(arena->data, arena->usable_size, PROT_READ) != 0) {
            return HHS_SECURE_EMPROTECT;
        }
    }
    return HHS_SECURE_OK;
}

int hhs_secure_arena_is_zero(
    const hhs_secure_arena *arena,
    const uint8_t owner_token[32],
    int *out_is_zero
) {
    size_t index;
    uint8_t accumulator = 0;
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (out_is_zero == NULL) {
        return HHS_SECURE_EINVAL;
    }
    for (index = 0; index < arena->usable_size; ++index) {
        accumulator |= arena->data[index];
    }
    *out_is_zero = accumulator == 0;
    return HHS_SECURE_OK;
}

int hhs_secure_arena_status_get(
    const hhs_secure_arena *arena,
    const uint8_t owner_token[32],
    hhs_secure_arena_status *out_status
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (out_status == NULL) {
        return HHS_SECURE_EINVAL;
    }
    out_status->requested_size = arena->requested_size;
    out_status->usable_size = arena->usable_size;
    out_status->mapping_size = arena->mapping_size;
    out_status->page_size = arena->page_size;
    out_status->mutation_sequence = arena->mutation_sequence;
    out_status->locked = arena->locked;
    out_status->dontdump = arena->dontdump;
    out_status->dontfork = arena->dontfork;
    out_status->sealed = arena->sealed;
    out_status->zeroized = arena->zeroized;
    out_status->guard_pages = 2;
    return HHS_SECURE_OK;
}

int hhs_secure_arena_destroy(
    hhs_secure_arena *arena,
    const uint8_t owner_token[32]
) {
    int authorization = hhs_secure_arena_authorize(arena, owner_token);
    if (authorization != HHS_SECURE_OK) {
        return authorization;
    }
    if (arena->sealed) {
        if (mprotect(arena->data, arena->usable_size, PROT_READ | PROT_WRITE) != 0) {
            return HHS_SECURE_EMPROTECT;
        }
    }
    hhs_explicit_zero(arena->data, arena->usable_size);
    munlock(arena->data, arena->usable_size);
    mprotect(arena->data, arena->usable_size, PROT_NONE);
    munmap(arena->mapping, arena->mapping_size);
    hhs_explicit_zero(arena->owner_token, sizeof(arena->owner_token));
    hhs_explicit_zero(arena, sizeof(*arena));
    free(arena);
    return HHS_SECURE_OK;
}

const char *hhs_secure_error_string(int code) {
    switch (code) {
        case HHS_SECURE_OK: return "HHS_SECURE_OK";
        case HHS_SECURE_EINVAL: return "HHS_SECURE_EINVAL";
        case HHS_SECURE_ENOMEM: return "HHS_SECURE_ENOMEM";
        case HHS_SECURE_EMMAP: return "HHS_SECURE_EMMAP";
        case HHS_SECURE_EMPROTECT: return "HHS_SECURE_EMPROTECT";
        case HHS_SECURE_EMLOCK: return "HHS_SECURE_EMLOCK";
        case HHS_SECURE_EMADVISE: return "HHS_SECURE_EMADVISE";
        case HHS_SECURE_EOWNER: return "HHS_SECURE_EOWNER";
        case HHS_SECURE_EBOUNDS: return "HHS_SECURE_EBOUNDS";
        case HHS_SECURE_ESEALED: return "HHS_SECURE_ESEALED";
        case HHS_SECURE_ESTATE: return "HHS_SECURE_ESTATE";
        case HHS_SECURE_EPRCTL: return "HHS_SECURE_EPRCTL";
        default: return "HHS_SECURE_EUNKNOWN";
    }
}
