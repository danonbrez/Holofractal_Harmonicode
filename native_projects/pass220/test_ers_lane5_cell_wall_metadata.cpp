#include "ers_lane5_cell_wall_metadata.hpp"
#include <cassert>
int main() {
 using namespace hhs::pass220;
 ERSMetadataView m{kERSRelations.data(), kERSRelations.size(),
    "1+1", "text", "source-transition-reference", 5, true, true};
 assert(valid_ers_metadata(m));
 assert(kPrimeRingAddresses[0]==2 && kPrimeRingAddresses[7]==19);
 assert(kPrimeResiduesMod8[6]==1 && kPrimeResiduesMod8[7]==3);
 assert(kLoShuHub==5 && kLoShuOuterRing[0]==8);
 assert(valid_prime_spin_index(7,7) && prime_spin_linear(7,7)==63);
 assert(!valid_prime_spin_index(8,0) && !valid_prime_spin_index(0,8));
 for (std::size_t p=0;p<8;++p)
   for (std::size_t s=0;s<8;++s)
     assert(valid_prime_spin_index(p,s));
 m.source_order_preserved = false;
 assert(!valid_ers_metadata(m));
 m.source_order_preserved = true;
 m.cell_address = 81;
 assert(!valid_ers_metadata(m));
 return 0;
}
