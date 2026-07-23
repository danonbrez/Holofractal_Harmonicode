#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define H72_LEN 72
#define VM81_LEN 81
static const char H72_ALPHABET[73] = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-+*/()<>!?";

typedef struct {
    uint8_t positions[H72_LEN];
    int64_t rotation_profile[H72_LEN];
    char dna[H72_LEN + 1];
    uint64_t trace_count;
    uint8_t zero_sum;
    uint8_t last_index;
    int64_t last_delta;
} HHSHash72RingState;

static uint8_t wrap72(int64_t v) {
    v %= 72;
    if (v < 0) v += 72;
    return (uint8_t)v;
}

static void refresh(HHSHash72RingState *ring) {
    uint64_t sum = 0;
    if (!ring) return;
    for (size_t i = 0; i < H72_LEN; i++) {
        uint8_t v = wrap72((int64_t)ring->positions[i]);
        ring->positions[i] = v;
        ring->dna[i] = H72_ALPHABET[v];
        sum = (sum + v) % 72;
    }
    ring->dna[72] = 0;
    ring->zero_sum = (uint8_t)(sum == 0);
}

void hhs_pass133_hash72_init(HHSHash72RingState *ring) {
    if (!ring) return;
    memset(ring, 0, sizeof(*ring));
    for (size_t i = 0; i < H72_LEN; i++) ring->positions[i] = (uint8_t)i;
    ring->positions[71] = wrap72((int64_t)ring->positions[71] + 36);
    refresh(ring);
}

uint8_t hhs_pass133_hash72_rotate(HHSHash72RingState *ring, uint8_t index, int64_t delta) {
    if (!ring) return 0;
    uint8_t i = wrap72(index);
    uint8_t j = wrap72((int64_t)i + 1);
    ring->positions[i] = wrap72((int64_t)ring->positions[i] + delta);
    ring->positions[j] = wrap72((int64_t)ring->positions[j] - delta);
    ring->rotation_profile[i] += delta;
    ring->rotation_profile[j] -= delta;
    ring->trace_count += 1;
    ring->last_index = i;
    ring->last_delta = delta;
    refresh(ring);
    return ring->zero_sum;
}

uint8_t hhs_pass133_hash72_validate(const HHSHash72RingState *ring) {
    if (!ring) return 0;
    uint64_t sum = 0;
    for (size_t i = 0; i < H72_LEN; i++) sum = (sum + wrap72(ring->positions[i])) % 72;
    return (uint8_t)(sum == 0);
}

uint8_t hhs_pass133_hash72_reverse(const HHSHash72RingState *current, HHSHash72RingState *original) {
    if (!current || !original) return 0;
    *original = *current;
    for (size_t i = 0; i < H72_LEN; i++) {
        original->positions[i] = wrap72((int64_t)original->positions[i] - current->rotation_profile[i]);
        original->rotation_profile[i] = 0;
    }
    original->trace_count = current->trace_count + 1;
    original->last_index = 0;
    original->last_delta = 0;
    refresh(original);
    return original->zero_sum;
}

size_t hhs_pass133_sizeof_hash72_ring(void) { return sizeof(HHSHash72RingState); }

uint8_t hhs_pass133_validate_diagonal_sudoku(const uint8_t grid[VM81_LEN]) {
    if (!grid) return 0;
    for (int r = 0; r < 9; r++) {
        uint16_t seen = 0;
        for (int c = 0; c < 9; c++) {
            uint8_t v = grid[r*9+c]; if (v > 8 || (seen & (1u<<v))) return 0; seen |= (1u<<v);
        }
        if (seen != 0x1ff) return 0;
    }
    for (int c = 0; c < 9; c++) {
        uint16_t seen = 0;
        for (int r = 0; r < 9; r++) { uint8_t v=grid[r*9+c]; if (seen&(1u<<v)) return 0; seen|=(1u<<v); }
        if (seen != 0x1ff) return 0;
    }
    for (int br = 0; br < 3; br++) for (int bc = 0; bc < 3; bc++) {
        uint16_t seen = 0;
        for (int dr=0; dr<3; dr++) for (int dc=0; dc<3; dc++) {
            uint8_t v=grid[(br*3+dr)*9+(bc*3+dc)]; if (seen&(1u<<v)) return 0; seen|=(1u<<v);
        }
        if (seen != 0x1ff) return 0;
    }
    uint16_t d1=0,d2=0;
    for (int i=0;i<9;i++) { uint8_t a=grid[i*9+i], b=grid[i*9+(8-i)]; if (d1&(1u<<a) || d2&(1u<<b)) return 0; d1|=(1u<<a); d2|=(1u<<b); }
    return (uint8_t)(d1==0x1ff && d2==0x1ff);
}

void hhs_pass133_loshu_vm81_order(uint8_t out[VM81_LEN]) {
    static const uint8_t w[9] = {3,8,1,2,4,6,7,0,5};
    size_t k=0;
    for (int ri=0;ri<9;ri++) for (int ci=0;ci<9;ci++) out[k++]=(uint8_t)(9*w[ri]+w[ci]);
}
