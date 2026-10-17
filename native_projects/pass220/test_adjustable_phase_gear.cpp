#include "adjustable_phase_gear_candidate.hpp"
#include <cassert>
int main() {
  using namespace hhs::pass220;
  const auto chiral=swap_inner_columns(kDurer);
  assert(swap_inner_columns(chiral)==kDurer);
  const auto out=covariant(kFibonacciLucas,chiral);
  const Matrix4 expected{{{{73,116,115,70}},{{146,232,230,140}},{{219,348,345,210}},{{270,418,414,258}}}};
  assert(out==expected);
  const auto a=prepare_candidate(-180), b=prepare_candidate(180);
  assert(a.angle!=b.angle && a.quantization==60 && !a.admitted && !b.admitted);
  assert(!a.phase_written && !b.phase_written);
  const PhasePayload p{123,27};
  const auto bypass=hnan_bypass(p);
  assert(bypass.phase==p.phase && bypass.write_count==p.write_count);
}
