#define _POSIX_C_SOURCE 200809L
#define main vm81_original_main
#include "../hhs_runtime/HARMONICODE_VM_RUNTIME.c"
#undef main
#include <time.h>
#include <inttypes.h>

static volatile uint64_t sink;
typedef void (*fn_t)(void *);
typedef struct { VM81 vm; char a[73], b[73]; size_t n; uint64_t counter; } Ctx;

static double ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC_RAW, &t);
    return (double)t.tv_sec * 1e9 + t.tv_nsec;
}

static int dc(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static uint64_t calibrate(fn_t f, void *c) {
    uint64_t n = 1;
    for (;;) {
        double t = ns();
        for (uint64_t i = 0; i < n; i++) f(c);
        double d = ns() - t;
        if (d > 5e7) {
            uint64_t r = (uint64_t)(n * 2e8 / d);
            return r ? r : 1;
        }
        n *= 2;
    }
}

static void measure(const char *name, fn_t f, void *c) {
    for (int i = 0; i < 50; i++) f(c);
    uint64_t n = calibrate(f, c);
    double s[9];
    for (int j = 0; j < 9; j++) {
        double t = ns();
        for (uint64_t i = 0; i < n; i++) f(c);
        s[j] = (ns() - t) / n;
    }
    qsort(s, 9, sizeof(double), dc);
    double mean = 0;
    for (int j = 0; j < 9; j++) mean += s[j];
    mean /= 9;
    printf("%s,%.3f,%.3f,%.3f,%.3f,%.3f,%" PRIu64 "\n",
           name, s[4], mean, s[0], s[8], 1e9 / s[4], n);
}

static void init(Ctx *c) {
    memset(c, 0, sizeof(*c));
    init_hash72();
    vm81_init(&c->vm, 0, SEED_LOSHU);
    load_demo(&c->vm);
    memset(c->a, 'A', 72); c->a[72] = 0;
    memset(c->b, 'B', 72); c->b[72] = 0;
}

static void b_init(void *p) {
    Ctx *c = p;
    vm81_init(&c->vm, c->counter++, SEED_LOSHU);
    sink ^= c->vm.cells[0];
}
static void b_sweep(void *p) {
    Ctx *c = p;
    sweep81(&c->vm);
    sink ^= c->vm.cells[0];
}
static void b_project(void *p) {
    Ctx *c = p;
    project_hash72(&c->vm, c->a);
    sink ^= (unsigned char)c->a[0];
}
static void b_receipt(void *p) {
    Ctx *c = p;
    compose_receipt_hash(c->a, 17, 0xa5a55a5a, c->b, c->a);
    sink ^= (unsigned char)c->a[0];
}
static void b_step(void *p) {
    Ctx *c = p;
    if (c->vm.halted) {
        vm81_init(&c->vm, 0, SEED_LOSHU);
        load_demo(&c->vm);
    }
    vm81_step(&c->vm);
    sink ^= c->vm.step;
}
static void b_demo(void *p) {
    Ctx *c = p;
    Options o = {128, 0, SEED_LOSHU, 0, 0, 0};
    vm81_init(&c->vm, c->counter++, SEED_LOSHU);
    load_demo(&c->vm);
    run_vm(&c->vm, &o);
    sink ^= c->vm.step;
}
static void b_orbit(void *p) {
    Ctx *c = p;
    c->vm.seen_count = c->n;
    sink ^= detect_orbit(&c->vm, c->a, c->counter++);
}

static void fill(Ctx *c, size_t n) {
    c->n = n;
    for (size_t i = 0; i < n; i++) {
        memset(c->vm.seen[i].hash, 'A', 72);
        uint64_t x = i;
        for (int k = 0; k < 8; k++) {
            c->vm.seen[i].hash[71-k] = HASH72[x % 72];
            x /= 72;
        }
        c->vm.seen[i].hash[72] = 0;
        c->vm.seen[i].step = i;
    }
    memset(c->a, 'A', 72);
    memset(c->a + 64, '!', 8);
    c->a[72] = 0;
}

int main(void) {
    Ctx c, o256, o1024, o4096, o8192;
    init(&c); init(&o256); init(&o1024); init(&o4096); init(&o8192);
    fill(&o256, 256); fill(&o1024, 1024); fill(&o4096, 4096); fill(&o8192, 8192);
    puts("name,median_ns,mean_ns,min_ns,max_ns,median_ops_per_s,iterations");
    measure("vm81_init", b_init, &c);
    measure("sweep81", b_sweep, &c);
    measure("project_hash72", b_project, &c);
    measure("compose_receipt_hash", b_receipt, &c);
    measure("vm81_step_demo", b_step, &c);
    measure("full_demo_13_steps", b_demo, &c);
    measure("orbit_scan_256", b_orbit, &o256);
    measure("orbit_scan_1024", b_orbit, &o1024);
    measure("orbit_scan_4096", b_orbit, &o4096);
    measure("orbit_scan_8192", b_orbit, &o8192);
    return sink == UINT64_MAX;
}
