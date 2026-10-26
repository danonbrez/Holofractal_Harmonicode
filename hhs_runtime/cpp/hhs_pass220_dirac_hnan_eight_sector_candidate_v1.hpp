#ifndef HHS_PASS220_DIRAC_HNAN_EIGHT_SECTOR_CANDIDATE_V1_HPP
#define HHS_PASS220_DIRAC_HNAN_EIGHT_SECTOR_CANDIDATE_V1_HPP
// Additive native exact candidate guard. No canonical VM81/Hash72/Hash216 writes.
// Coefficient domain: exact Gaussian integers (the reference projector uses
// division by 2, tested without dividing). No floating-point operations.
#include <array>
#include <cstdint>
#include <string_view>

namespace hhs::pass220::dirac {
struct Gaussian { std::int64_t re; std::int64_t im; };
struct Sector {
  std::string_view address;
  std::string_view role;
  std::array<Gaussian,4> psi; // ordered phi[0:2], chi[2:4]
  bool source_group_witness_verified;
};
struct BoundaryDecision {
  bool ordered_roles;
  bool reference_projector_admissible;
  bool all_group_mappings_verified;
  bool native_admission; // ALWAYS false until integrated cell-wall verifier exists
};
constexpr std::array<std::string_view,8> addresses{
  "000","001","010","011","100","101","110","111"};
constexpr std::array<std::string_view,8> roles{
  "xy","x+y","yx","xy-zw","wz-yx","wz","z+w","zw"};
constexpr bool equal(Gaussian a,Gaussian b) noexcept {
  return a.re==b.re && a.im==b.im;
}
// K=i beta alpha_z, with sigma_z=diag(1,-1).
// Kψ=(i χ0,-i χ1,-i φ0,i φ1) (ordered Dirac basis).
constexpr Gaussian plus_i(Gaussian v) noexcept {return {-v.im,v.re};}
constexpr Gaussian minus_i(Gaussian v) noexcept {return {v.im,-v.re};}
constexpr std::array<Gaussian,4> apply_k(const std::array<Gaussian,4>& s) noexcept {
  return {plus_i(s[2]),minus_i(s[3]),minus_i(s[0]),plus_i(s[1])};
}
constexpr bool on_projector_boundary(const std::array<Gaussian,4>& psi) noexcept {
  // Exclude the trivial zero spinor from physical boundary candidacy.
  bool nonzero=false;
  for(const auto& z:psi)nonzero |= z.re!=0 || z.im!=0;
  if(!nonzero)return false;
  // P+ψ=ψ <=> Kψ=ψ; no division, cancellation or approximations.
  const auto k=apply_k(psi);
  for(std::size_t j=0;j<4;++j) if(!equal(k[j],psi[j]))return false;
  return true;
}
constexpr bool projector_involution(const std::array<Gaussian,4>& psi) noexcept {
  const auto twice=apply_k(apply_k(psi));
  for(std::size_t j=0;j<4;++j)if(!equal(twice[j],psi[j]))return false;
  return true;
}
constexpr BoundaryDecision check(const std::array<Sector,8>& sectors) noexcept {
  bool order=true,reference=true,mapped=true;
  for(std::size_t i=0;i<8;++i){
    order &= sectors[i].address==addresses[i] && sectors[i].role==roles[i];
    reference &= projector_involution(sectors[i].psi) &&
                 on_projector_boundary(sectors[i].psi);
    mapped &= sectors[i].source_group_witness_verified;
  }
  return {order,reference,mapped,false};
}
} // namespace hhs::pass220::dirac
#endif
