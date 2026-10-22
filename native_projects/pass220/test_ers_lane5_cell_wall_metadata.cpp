#include "ers_lane5_cell_wall_metadata.hpp"
#include <cassert>
int main() {
 using namespace hhs::pass220;
 ERSMetadataView m{kERSRelations.data(), kERSRelations.size(),
    "1+1", "text", "source-transition-reference", 5, true, true};
 assert(valid_ers_metadata(m));
 assert(kERSRelations[5].lhs=="3/4:2/5");
 FullCircuitCandidate routed{};
 routed.parent_hash216=std::string(216,'a');
 routed.inherited_linear5184[0]=5*64;
 routed.exact_bigint_digits[0]="11";
 ERSMetadataView bound{kERSRelations.data(),kERSRelations.size(),
    "11","text",routed.parent_hash216,5,true,true};
 assert(ers_source_matches_circuit(bound,routed));
 bound.source_payload="12";
 assert(!ers_source_matches_circuit(bound,routed));
 bound.source_payload="11";
 const std::string mismatched_ancestry(216,'b');
 bound.ancestry_reference=mismatched_ancestry;
 assert(!ers_source_matches_circuit(bound,routed));
 bound.ancestry_reference=routed.parent_hash216;

 HHSExactPass219Hash216TransitionViewV1 transition{};
 for (std::size_t i=0;i<216;++i) transition.transition_identity216[i]='a';
 assert(ers_transition_identity_matches(bound,&transition));
 transition.transition_identity216[100]='b';
 assert(!ers_transition_identity_matches(bound,&transition));
 transition.transition_identity216[100]='a';
 assert(!ers_transition_identity_matches(bound,nullptr));
 transition.transition_identity216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]='X';
 assert(!ers_transition_identity_matches(bound,&transition));
 transition.transition_identity216[HHS_EXACT_UQCEL_HASH216_TRIPLET_LEN]='\0';
 bound.ancestry_reference=std::string_view(routed.parent_hash216.data(),215);
 assert(!ers_transition_identity_matches(bound,&transition));
 bound.ancestry_reference=routed.parent_hash216;
 assert(ers_transition_identity_matches(bound,&transition));
 routed.inherited_linear5184[0]=4*64;
 assert(!ers_source_matches_circuit(bound,routed));

 assert(kPrimeRingAddresses[0]==2 && kPrimeRingAddresses[7]==19);
 assert(kPrimeResiduesMod8[6]==1 && kPrimeResiduesMod8[7]==3);
 assert(kLoShuHub==5 && kLoShuOuterRing[0]==4);
 assert(kHNANOuterAddresses[0]=="000" && kHNANOuterAddresses[7]=="011");
 assert(valid_hnan_ring_alignment());
 assert(valid_orthogonal_phase_gear());
 assert(kLaroneRotorPeriod==72 && kLaroneQuarterTurn==18 && kLaroneHalfTurn==36);
 for (std::size_t i=0;i<8;++i) {
   assert(orthogonal_gear_phase72(i)==kOrthogonalGearRegisters[i]);
   assert(orthogonal_gear_phase72(i+2)==
       (orthogonal_gear_phase72(i)+kLaroneQuarterTurn)%kLaroneRotorPeriod);
   assert(orthogonal_gear_phase72(i+4)==
       (orthogonal_gear_phase72(i)+kLaroneHalfTurn)%kLaroneRotorPeriod);
   assert(orthogonal_gear_phase72(i+8)==orthogonal_gear_phase72(i));
 }
 auto forged_addresses=kOrthogonalGearAddresses;
 forged_addresses[0]="000";
 assert(!valid_orthogonal_phase_gear(forged_addresses,kOrthogonalGearRegisters));
 auto forged_registers=kOrthogonalGearRegisters;
 forged_registers[1]=8;
 assert(!valid_orthogonal_phase_gear(kOrthogonalGearAddresses,forged_registers));
 forged_registers=kOrthogonalGearRegisters;
 forged_registers[3]=36;
 assert(!valid_orthogonal_phase_gear(kOrthogonalGearAddresses,forged_registers));
 for(std::size_t i=0;i<8;++i) {
   assert(kOrthogonalGearRegisters[i]==8+9*i);
   assert(kOrthogonalGearRegisters[i]%9==kOrthogonalGearResidue);
 }
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
