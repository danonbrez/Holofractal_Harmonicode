// Compile: c++ -std=c++17 -Wall -Wextra -Werror -I. tests/pass220/test_dirac_hnan_native_candidate_v1.cpp -o /tmp/hhs-dirac-test
#include "hhs_runtime/cpp/hhs_pass220_dirac_hnan_eight_sector_candidate_v1.hpp"
#include <array>
#include <cassert>
using namespace hhs::pass220::dirac;
int main() {
  constexpr Gaussian zero{0,0};
  constexpr std::array<Gaussian,4> psi{zero,zero,zero,zero};
  static_assert(projector_involution(psi),"K squared is identity");
  static_assert(!on_projector_boundary(psi),"zero cannot certify a particle boundary");
  constexpr std::array<Gaussian,4> arbitrary{{{1,2},{2,-3},{4,5},{-2,7}}};
  static_assert(projector_involution(arbitrary),"K squared identity for nonzero spinor");
  static_assert(!on_projector_boundary(arbitrary),"non-admitted spinor rejected");
  std::array<Sector,8> sectors{};
  for(std::size_t i=0;i<8;++i)sectors[i]={addresses[i],roles[i],psi,false};
  auto decision=check(sectors);
  assert(decision.ordered_roles && decision.reference_projector_admissible);
  assert(!decision.all_group_mappings_verified && !decision.native_admission);
  sectors[0].source_group_witness_verified=true;
  for(auto& sector:sectors)sector.source_group_witness_verified=true;
  decision=check(sectors);
  assert(decision.all_group_mappings_verified && !decision.native_admission);
  sectors[2].role="xy";
  assert(!check(sectors).ordered_roles);
  sectors[2].role=roles[2];
  sectors[4].psi=arbitrary;
  assert(!check(sectors).reference_projector_admissible);
}
