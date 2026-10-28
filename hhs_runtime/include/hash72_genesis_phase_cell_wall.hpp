#pragma once
// Pass 220 candidate-only Genesis-relative phase reconstruction.
// No canonical hash, VM81 admission, or persistence authority.
#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
namespace hhs::pass220::genesis {
constexpr std::size_t spinor = 4, reciprocalLoShu = 18, side = spinor * reciprocalLoShu, cells = side * side;
static_assert(cells == 5184);
constexpr std::uint8_t mod72(int n) { return static_cast<std::uint8_t>((n % 72 + 72) % 72); }
constexpr std::uint8_t reciprocal(std::uint8_t n) { return mod72(-int(n)); }
constexpr std::uint8_t compose(std::uint8_t a, std::uint8_t b) { return mod72(int(a)+int(b)); }
constexpr std::size_t address(std::size_t sr, std::size_t lr, std::size_t sc, std::size_t lc) {
  return (sr*18+lr)*72 + (sc*18+lc);
}
struct Candidate {
  std::array<std::uint8_t,72> genesisRows{}, genesisCols{}, rowOffsets{}, colOffsets{};
  std::string sourceHash72;
  bool valid() const {
    if (sourceHash72.size()!=72) return false;
    for (auto p : {&genesisRows,&genesisCols,&rowOffsets,&colOffsets})
      for (auto x : *p) if (x>=72) return false;
    return true;
  }
  std::uint8_t at(std::size_t r,std::size_t c) const {
    if (!valid() || r>=72 || c>=72) throw std::invalid_argument("invalid phase candidate");
    return compose(compose(genesisRows[r],rowOffsets[r]),
                   reciprocal(compose(genesisCols[c],colOffsets[c])));
  }
  std::array<std::uint8_t,5184> reconstruct() const {
    if (!valid()) throw std::invalid_argument("invalid phase candidate");
    std::array<std::uint8_t,5184> result{};
    for (std::size_t r=0;r<72;++r)
      for (std::size_t c=0;c<72;++c) result[r*72+c]=at(r,c);
    return result;
  }
};
// The 5184 phase addresses are not automatically the inherited VM5184
// s=64*c+o addresses. A separately checked bridge is required.
}
