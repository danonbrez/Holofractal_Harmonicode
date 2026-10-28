#pragma once
// Candidate-only ordered cell identity. No independent VM81/Hash72/Hash216 authority.
#include "hhs_pass220_saturated_offset_layer_v1.hpp"
#include <array>
#include <string>
#include <vector>
namespace hhs::pass220::polynomial_offset {
using namespace hhs::pass220::offset_layer;
struct CellWitness {
 std::size_t vm_address,reciprocal_address;
 std::string genesis_expression,polynomial_expression,orientation,constraint_ancestry;
};
struct WitnessLayer {
 CandidateLayer phase_layer;
 std::array<CellWitness,count> witnesses;
 std::string genesis_id;
};
inline bool complete(const WitnessLayer& l){
 if(!saturated(l.phase_layer)||l.genesis_id.empty())return false;
 for(std::size_t s=0;s<count;++s){
  const auto& c=l.witnesses[s];
  if(c.vm_address!=s||c.reciprocal_address!=to_reciprocal(s)||
    c.genesis_expression.empty()||c.polynomial_expression.empty()||
    c.orientation.empty()||c.constraint_ancestry.empty()||
    l.phase_layer.genesis[s]>=phases||l.phase_layer.offsets[s]>=phases)return false;
 }
 return true;
}
inline bool same_cell_identity(const CellWitness& a,const CellWitness& b){
 return a.vm_address==b.vm_address&&a.reciprocal_address==b.reciprocal_address&&
 a.genesis_expression==b.genesis_expression&&a.polynomial_expression==b.polynomial_expression&&
 a.orientation==b.orientation&&a.constraint_ancestry==b.constraint_ancestry;
}
inline bool same_resolved_candidate(const WitnessLayer& a,const WitnessLayer& b){
 if(a.genesis_id!=b.genesis_id||a.phase_layer.genesis!=b.phase_layer.genesis||
 a.phase_layer.offsets!=b.phase_layer.offsets)return false;
 for(std::size_t s=0;s<count;++s)if(!same_cell_identity(a.witnesses[s],b.witnesses[s]))return false;
 return true;
}
inline bool candidate_distinct(const WitnessLayer& a,const WitnessLayer& genesis,
 const std::vector<const WitnessLayer*>& admitted){
 if(!complete(a)||!complete(genesis)||a.genesis_id!=genesis.genesis_id||
 a.phase_layer.genesis!=genesis.phase_layer.genesis||same_resolved_candidate(a,genesis))return false;
 for(std::size_t s=0;s<count;++s)
  if(a.witnesses[s].genesis_expression!=genesis.witnesses[s].genesis_expression||
  a.witnesses[s].constraint_ancestry!=genesis.witnesses[s].constraint_ancestry)return false;
 for(const auto* prior:admitted){
  if(!prior||!complete(*prior)||prior->genesis_id!=a.genesis_id)return false;
  if(same_resolved_candidate(a,*prior))return false;
 }
 return true;
}
}
