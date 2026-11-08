#include "hhs_pass220_q81_hnan_native_phase_candidate_v1.h"
#include <cassert>
#include <cstdint>

int main() {
    const std::int8_t pairs[4][2] = {{0,1},{1,0},{-1,1},{1,-1}};
    for (std::uint8_t index=0; index<4; ++index) {
        std::uint8_t bit=255, orientation=255;
        assert(hhs_pass220_q81_hnan_phase_encode_pair(
            pairs[index][0],pairs[index][1],&bit,&orientation) ==
            HHS_EXACT_STATUS_OK);
        assert(bit == index/2 && orientation == index%2);
        std::int8_t lhs=9,rhs=9;
        assert(hhs_pass220_q81_hnan_phase_decode_pair(
            bit,orientation,&lhs,&rhs) == HHS_EXACT_STATUS_OK);
        assert(lhs==pairs[index][0] && rhs==pairs[index][1]);
    }
    std::uint8_t bit=73,orientation=74;
    assert(hhs_pass220_q81_hnan_phase_encode_pair(2,2,&bit,&orientation) ==
           HHS_EXACT_STATUS_INVALID_ARGUMENT);
    assert(bit==73 && orientation==74); // failure never writes output
    std::int8_t lhs=7,rhs=8;
    assert(hhs_pass220_q81_hnan_phase_decode_pair(2,0,&lhs,&rhs) ==
           HHS_EXACT_STATUS_INVALID_ARGUMENT);
    assert(lhs==7 && rhs==8);
    assert(hhs_pass220_q81_hnan_phase_decode_pair(0,2,&lhs,&rhs) ==
           HHS_EXACT_STATUS_INVALID_ARGUMENT);
    return 0;
}
