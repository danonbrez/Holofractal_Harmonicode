#include "hhs_pass220_lane5_quartic_phase_carrier_v1.hpp"
#include <cassert>
int main() {
 using namespace hhs::lane5::phase4;
 assert(closed());
 for (unsigned k=0; k<4; ++k) {
  assert(equal(ordered_minor(phase(k)), ordered_minor(source())));
  assert(equal(quarter_turn(phase(k)), phase((k+1)%4)));
 }
 for (unsigned n=0; n<5184; ++n) assert(position_valid(n));
 return 0;
}
