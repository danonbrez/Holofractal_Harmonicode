#pragma once
// Exact, candidate-only four-phase determinant carrier for Lane 5.
// Variables are typed symbolic carriers: no scalar/quaternion commutation assumed.
#include <array>
#include <cstddef>
#include <cstdint>

namespace hhs::lane5::phase4 {
enum class Carrier : std::uint8_t { x, y, z, w };
struct Term { Carrier first, second; std::int8_t coefficient; };
struct Cell { Carrier carrier; std::int8_t sign; };
using Matrix = std::array<Cell, 4>; // row major
using Polynomial = std::array<Term, 2>; // ordered products
constexpr Matrix source() noexcept {
  return {{{Carrier::x,1},{Carrier::y,1},{Carrier::z,1},{Carrier::w,1}}};
}
// Right-multiply by J=[0,-1;1,0]. No carrier multiplication occurs here.
constexpr Matrix quarter_turn(Matrix a) noexcept {
  return {{a[1],{a[0].carrier,static_cast<std::int8_t>(-a[0].sign)},
           a[3],{a[2].carrier,static_cast<std::int8_t>(-a[2].sign)}}};
}
constexpr Matrix phase(std::uint8_t k) noexcept {
  auto out = source();
  for (unsigned i=0; i<(k%4U); ++i) out=quarter_turn(out);
  return out;
}
constexpr bool equal(Matrix a, Matrix b) noexcept {
  for (std::size_t i=0;i<4;++i)
    if(a[i].carrier!=b[i].carrier||a[i].sign!=b[i].sign) return false;
  return true;
}
// D = a*d - b*c. Ordered word identity, NOT quaternion determinant.
constexpr Polynomial ordered_minor(Matrix a) noexcept {
  Polynomial out{{{a[0].carrier,a[3].carrier,
              static_cast<std::int8_t>(a[0].sign*a[3].sign)},
           {a[1].carrier,a[2].carrier,
              static_cast<std::int8_t>(-a[1].sign*a[2].sign)}}};
  // Additive normalization only. Never swap noncommutative word factors.
  if(static_cast<unsigned>(out[1].first)<static_cast<unsigned>(out[0].first) ||
     (out[1].first==out[0].first &&
      static_cast<unsigned>(out[1].second)<static_cast<unsigned>(out[0].second))) {
    const auto temp=out[0]; out[0]=out[1]; out[1]=temp;
  }
  return out;
}
constexpr bool equal(Polynomial a,Polynomial b) noexcept {
  for(std::size_t i=0;i<2;++i)
    if(a[i].first!=b[i].first||a[i].second!=b[i].second||
       a[i].coefficient!=b[i].coefficient) return false;
  return true;
}
struct Position { std::uint16_t hash_row, hash_column, vm81_cell, cell_position; };
constexpr Position position(std::uint16_t n) noexcept {
  return {static_cast<std::uint16_t>(n/72U),
          static_cast<std::uint16_t>(n%72U),
          static_cast<std::uint16_t>(n/64U),
          static_cast<std::uint16_t>(n%64U)};
}
constexpr bool position_valid(std::uint16_t n) noexcept {
  if(n>=5184U) return false;
  const auto p=position(n);
  return 72U*p.hash_row+p.hash_column==n &&
         64U*p.vm81_cell+p.cell_position==n &&
         p.hash_row<72U && p.hash_column<72U &&
         p.vm81_cell<81U && p.cell_position<64U;
}
constexpr bool closed() noexcept {
  const auto base=source();
  if(!equal(quarter_turn(phase(3)),base)) return false;
  for(std::uint8_t k=0;k<4;++k) {
    if(!equal(quarter_turn(phase(k)),phase(static_cast<std::uint8_t>((k+1)%4))))
      return false;
    if(!equal(ordered_minor(phase(k)),ordered_minor(base)))
      return false;
  }
  for(std::uint16_t n=0;n<5184U;++n) if(!position_valid(n)) return false;
  return true;
}
static_assert(closed(), "ordered determinant, quarter-turn or 5184 coordinate closure failed");
} // namespace hhs::lane5::phase4
