#define _GNU_SOURCE
#include <errno.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

/*
 * Pass 219 raw Linux serial-ABI capacity calibration.
 *
 * This binary deliberately includes no HHS/VM81 headers and links no HHS
 * library.  Capacity is measured only in raw Linux process-addressable bytes.
 */

#define SCHEMA "HHS_PASS219_RAW_LINUX_SERIAL_ABI_CAPACITY_V1"
#define CAPACITY_UNIT "RAW_LINUX_SERIAL_ABI_BYTES"
#define MIN_PROBE_BYTES UINT64_C(1048576)

static uint64_t monotonic_ns(void) {
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) {
        perror("clock_gettime");
        exit(2);
    }
    return (uint64_t)ts.tv_sec * UINT64_C(1000000000) +
           (uint64_t)ts.tv_nsec;
}

static uint64_t parse_u64(const char *text) {
    char *end = NULL;
    unsigned long long value;
    errno = 0;
    value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0') {
        fprintf(stderr, "invalid integer: %s\n", text);
        exit(2);
    }
    return (uint64_t)value;
}

static int child_probe(uint64_t bytes, size_t page_size) {
    uint8_t *buffer;
    uint64_t offset;
    volatile uint64_t checksum = 0U;

    if (bytes == 0U || bytes > (uint64_t)SIZE_MAX)
        return 3;

    buffer = mmap(
        NULL,
        (size_t)bytes,
        PROT_READ | PROT_WRITE,
        MAP_PRIVATE | MAP_ANONYMOUS,
        -1,
        0
    );
    if (buffer == MAP_FAILED)
        return 4;

    for (offset = 0U; offset < bytes; offset += (uint64_t)page_size) {
        uint8_t value = (uint8_t)((offset >> 12U) ^ (offset >> 20U) ^ UINT64_C(0x5a));
        buffer[(size_t)offset] = value;
    }
    buffer[(size_t)(bytes - 1U)] = (uint8_t)0xA5U;

    for (offset = 0U; offset < bytes; offset += (uint64_t)page_size) {
        uint8_t expected =
            (uint8_t)((offset >> 12U) ^ (offset >> 20U) ^ UINT64_C(0x5a));
        uint8_t actual = buffer[(size_t)offset];
        if (actual != expected) {
            (void)munmap(buffer, (size_t)bytes);
            return 5;
        }
        checksum += (uint64_t)actual;
    }
    if (buffer[(size_t)(bytes - 1U)] != (uint8_t)0xA5U) {
        (void)munmap(buffer, (size_t)bytes);
        return 6;
    }

    if (munmap(buffer, (size_t)bytes) != 0)
        return 7;

    return checksum == UINT64_MAX ? 8 : 0;
}

static int probe_is_success(uint64_t bytes, size_t page_size) {
    pid_t pid;
    int status = 0;

    pid = fork();
    if (pid < 0) {
        perror("fork");
        exit(2);
    }
    if (pid == 0) {
        int rc = child_probe(bytes, page_size);
        _exit(rc);
    }
    if (waitpid(pid, &status, 0) < 0) {
        perror("waitpid");
        exit(2);
    }
    return WIFEXITED(status) && WEXITSTATUS(status) == 0;
}

static uint64_t align_down(uint64_t value, uint64_t alignment) {
    return value - (value % alignment);
}

int main(int argc, char **argv) {
#if !defined(__linux__) || !defined(__x86_64__)
    fprintf(stderr, "raw Linux serial ABI capacity calibration requires Linux x86_64\n");
    return 2;
#else
    long page_long;
    uint64_t page_size;
    uint64_t ceiling;
    uint64_t low = 0U;
    uint64_t high;
    uint64_t probe;
    uint64_t started;
    uint64_t elapsed;
    uint64_t attempts = 0U;

    if (argc != 2) {
        fprintf(stderr, "usage: %s MAX_PROBE_BYTES\n", argv[0]);
        return 2;
    }

    page_long = sysconf(_SC_PAGESIZE);
    if (page_long <= 0) {
        fprintf(stderr, "invalid page size\n");
        return 2;
    }
    page_size = (uint64_t)page_long;
    ceiling = align_down(parse_u64(argv[1]), page_size);
    if (ceiling < page_size) {
        fprintf(stderr, "probe ceiling too small\n");
        return 2;
    }

    started = monotonic_ns();

    probe = align_down(MIN_PROBE_BYTES, page_size);
    if (probe < page_size)
        probe = page_size;
    if (probe > ceiling)
        probe = ceiling;

    while (probe <= ceiling) {
        ++attempts;
        if (!probe_is_success(probe, (size_t)page_size))
            break;
        low = probe;
        if (probe == ceiling)
            break;
        if (probe > ceiling / 2U)
            probe = ceiling;
        else
            probe *= 2U;
    }

    if (low == ceiling) {
        high = ceiling;
    } else {
        high = probe > ceiling ? ceiling : probe;
        if (high < page_size)
            high = page_size;

        while (high > low + page_size) {
            uint64_t mid = align_down(low + (high - low) / 2U, page_size);
            if (mid <= low)
                mid = low + page_size;
            ++attempts;
            if (probe_is_success(mid, (size_t)page_size))
                low = mid;
            else
                high = mid;
        }
    }

    elapsed = monotonic_ns() - started;
    if (low == 0U) {
        fprintf(stderr, "no successful raw-byte probe\n");
        return 1;
    }

    printf(
        "{"
        "\"schema\":\"%s\","
        "\"capacity_unit\":\"%s\","
        "\"max_serial_abi_bytes\":%" PRIu64 ","
        "\"probe_ceiling_bytes\":%" PRIu64 ","
        "\"page_size\":%" PRIu64 ","
        "\"benchmark_window_ns\":%" PRIu64 ","
        "\"probe_attempts\":%" PRIu64 ","
        "\"hhs_present\":false,"
        "\"vm81_services_present\":false,"
        "\"lane5_present\":false,"
        "\"rna_services_present\":false,"
        "\"hash72_present\":false,"
        "\"hash216_present\":false,"
        "\"pqc_present\":false"
        "}\n",
        SCHEMA,
        CAPACITY_UNIT,
        low,
        ceiling,
        page_size,
        elapsed,
        attempts
    );
    return 0;
#endif
}
