#pragma once
// Candidate-only, exact 81x64 / 64x81 reciprocal offset views.
// Preserve VM5184 address authority, never mint Hash72 or Hash216.
#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
namespace hhs::pass220::offset_layer {
constexpr std::size_t cells=81, ops=64, count=cells*ops, phases=72;
constexpr std::size_t vm_address(std::size_t cell,std::size_t op){return 64*cell+op;}
constexpr std::size_t reciprocal_address(std::size_t cell,std::size_t op){return 81*op+cell;}
constexpr std::size_t to_reciprocal(std::size_t s){return reciprocal_address(s/64,s%64);}
constexpr std::size_t to_vm(std::size_t t){return vm_address(t%81,t/81);}
constexpr std::uint8_t phase(std::size_t x){return static_cast<std::uint8_t>(x%phases);}
constexpr std::uint8_t compose_phase(std::uint8_t a,std::uint8_t b){return phase(static_cast<std::size_t>(a)+b);}
constexpr std::uint8_t inverse_phase(std::uint8_t p){return phase(phases-p);}
static_assert(to_reciprocal(0)==0 && to_vm(5183)==5183);
static_assert(to_vm(to_reciprocal(1234))==1234);
using PhaseTensor=std::array<std::uint8_t,count>;
using SaturationMask=std::array<bool,count>;
struct CandidateLayer {
 PhaseTensor genesis{};  // Genesis-relative phase projection only; not full tensor identity
 PhaseTensor offsets{};  // indexed in VM5184 order
 SaturationMask active{};
};
inline bool saturated(const CandidateLayer& l){
 for(bool b:l.active)if(!b)return false;
 return true;
}
inline PhaseTensor project(const CandidateLayer& l){
 PhaseTensor out{};
 for(std::size_t s=0;s<count;++s){
  if(!l.active[s])throw std::invalid_argument("inactive offset cell");
  if(l.genesis[s]>=72||l.offsets[s]>=72)throw std::invalid_argument("invalid phase");
  out[s]=compose_phase(l.genesis[s],l.offsets[s]);
 }
 return out;
}
inline PhaseTensor reciprocal_view(const PhaseTensor& vm){
 PhaseTensor out{};
 for(std::size_t s=0;s<count;++s)out[to_reciprocal(s)]=vm[s];
 return out;
}
inline PhaseTensor vm_view(const PhaseTensor& reciprocal){
 PhaseTensor out{};
 for(std::size_t t=0;t<count;++t)out[to_vm(t)]=reciprocal[t];
 return out;
}
inline bool offset_unique(const CandidateLayer& candidate,const CandidateLayer& prior){
 // A necessary phase-level distinctness screen, not sufficient for full global identity.
 return candidate.offsets!=prior.offsets;
}
inline PhaseTensor relative_offsets(const CandidateLayer& from,const CandidateLayer& to){
 if(!saturated(from)||!saturated(to))throw std::invalid_argument("unsaturated layer");
 if(from.genesis!=to.genesis)throw std::invalid_argument("different genesis projection");
 PhaseTensor out{};
 for(std::size_t s=0;s<count;++s){
  if(from.offsets[s]>=72||to.offsets[s]>=72)throw std::invalid_argument("invalid phase");
  out[s]=compose_phase(to.offsets[s],inverse_phase(from.offsets[s]));
 }
 return out;
}
inline bool valid_candidate(const CandidateLayer& candidate,const CandidateLayer& genesis,
                            const CandidateLayer* prior=nullptr){
 if(!saturated(candidate)||candidate.genesis!=genesis.genesis)return false;
 for(std::size_t s=0;s<count;++s)
   if(candidate.offsets[s]>=72||candidate.genesis[s]>=72)return false;
 if(candidate.offsets==genesis.offsets)return false;
 if(prior&&!offset_unique(candidate,*prior))return false;
 return true;
}
}
