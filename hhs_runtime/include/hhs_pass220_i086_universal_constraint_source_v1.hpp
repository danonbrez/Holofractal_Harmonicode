#ifndef HHS_PASS220_I086_UNIVERSAL_CONSTRAINT_SOURCE_V1_HPP
#define HHS_PASS220_I086_UNIVERSAL_CONSTRAINT_SOURCE_V1_HPP
#include <cstddef>
#include <cstdint>
#include <string_view>
namespace hhs::lane5::reciprocal_nesting {
// Exact UTF-8 source text: NOT host scalar, commutative algebra, or admission.
inline constexpr std::string_view kUniversalConstraint = u8R"HHS(((a^2*(x/y*y/x==(x*y)/z^4)+a^2*(z/w*w/z==(z*w)/x^4)==b^2*x^2*z^2)/(x*y+z*w==c^2-a^2)==(c^2-b^2)/a^2+x+y-z-w+x*y+y^2-z*w-w^2)AB/-P⁴=((P²-pq)((p+q)/(q-p)P)(p/q)(q/p))P⁴/-BA==u(-³⁶)/yx==u⁷²/xy)HHS";
enum class BoundaryKind : std::uint8_t { Open, Close, Equality, Gate };
struct Boundary { BoundaryKind kind{}; std::size_t byte_offset{}; std::uint32_t depth{}; };
template <typename Sink>
bool scan_boundaries(std::string_view source, Sink&& sink) {
    std::uint32_t depth=0;
    for(std::size_t i=0;i<source.size();++i) {
        if(source[i]=='(') { sink(Boundary{BoundaryKind::Open,i,depth}); ++depth; }
        else if(source[i]==')') {
            if(depth==0) return false;
            --depth; sink(Boundary{BoundaryKind::Close,i,depth});
        } else if(source[i]=='=') {
            const bool gate=(i+1<source.size() && source[i+1]=='=');
            sink(Boundary{gate?BoundaryKind::Gate:BoundaryKind::Equality,i,depth});
            if(gate) ++i;
        }
    }
    return depth==0;
}
} // namespace hhs::lane5::reciprocal_nesting
#endif
