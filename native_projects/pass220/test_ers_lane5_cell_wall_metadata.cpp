#include "ers_lane5_cell_wall_metadata.hpp"
#include <cassert>
int main() {
 using namespace hhs::pass220;
 ERSMetadataView m{kERSRelations.data(), kERSRelations.size(),
    "1+1", "text", "source-transition-reference", 5, true, true};
 assert(valid_ers_metadata(m));
 m.source_order_preserved = false;
 assert(!valid_ers_metadata(m));
 m.source_order_preserved = true;
 m.cell_address = 81;
 assert(!valid_ers_metadata(m));
 return 0;
}
