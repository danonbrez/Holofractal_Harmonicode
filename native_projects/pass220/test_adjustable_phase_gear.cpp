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
  std::array<std::uint16_t,16> slots{};
  std::array<std::string,16> digits{};
  for(std::size_t i=0;i<16;++i) { slots[i]=static_cast<std::uint16_t>(i); digits[i]=std::to_string(i); }
  const auto inherited=project_existing_graph(a,slots,digits,std::string(216,'0'));
  assert(inherited.linear5184[15]==15 && inherited.ordered_bigint_digits[15]=="15");
  assert(inherited.parent_hash216.size()==216 && !inherited.native_cell_wall_checked);
  assert(!inherited.signed_environment_admitted && !inherited.canonical_hash216_minted);
  bool rejected=false;
  try { slots[0]=5184; (void)project_existing_graph(a,slots,digits,std::string(216,'0')); }
  catch(const std::invalid_argument&) { rejected=true; }
  assert(rejected);
  slots[0]=0;
  rejected=false;
  try { digits[0]="1.5"; (void)project_existing_graph(a,slots,digits,std::string(216,'0')); }
  catch(const std::invalid_argument&) { rejected=true; }
  assert(rejected);
  digits[0]="0";
  rejected=false;
  try { (void)project_existing_graph(a,slots,digits,"not-a-hash216"); }
  catch(const std::invalid_argument&) { rejected=true; }
  assert(rejected);
  const auto all=compose8(kDurer,kDurer,kFibonacciLucas,kDurer);
  assert(all[0][0]==16 && all[0][4]==16);
  assert(all[4][0]==16 && all[7][7]==18);
  std::array<std::uint16_t,64> full_slots{};
  std::array<std::string,64> full_digits{};
  for(std::size_t i=0;i<64;++i) {
    full_slots[i]=static_cast<std::uint16_t>(i);
    full_digits[i]=std::to_string(all[i/8][i%8]);
  }
  OuterPhaseVectors outer{{-180,0,0,0,0,0,0,0}};
  const auto full=project_full_circuit(outer,all,full_slots,full_digits,std::string(216,'0'));
  assert(full.candidate_only && full.inherited_linear5184[63]==63);
  assert(full.phase_vectors[0]==-180 && full.cells[7][7]==18);
  const PhasePayload p{123,27};
  const auto bypass=hnan_bypass(p);
  assert(bypass.phase==p.phase && bypass.write_count==p.write_count);
}
