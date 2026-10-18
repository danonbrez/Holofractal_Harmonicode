#include "phase_gear_v2_ordered_source.hpp"
#include <cassert>
#include <stdexcept>
#include <string>
int main() {
  using namespace hhs::pass220::v2;
  const auto c=construct_source_locked(kCanonicalSource);
  assert(c.candidate_only);
  assert(c.gate_count[0]==0 && c.gate_count[1]==0);
  assert(c.gate_count[2]==18 && c.gate_count[3]==4);
  assert(c.parts[0].find("MatrixTimes(-180")!=std::string::npos);
  assert(c.parts[1].find("5*(x^2-1)")!=std::string::npos);
  assert(c.parts[2].find("0*x*y")!=std::string::npos);
  assert(c.parts[2].find("111*z*w")!=std::string::npos);
  assert(c.parts[3].find("x^8-x^7-x^6+x^2-1")!=std::string::npos);
  assert(c.parts[3].find("b^4*c^2-x*y")!=std::string::npos);
  const auto register_gates=split_top_level_gates(c.parts[2]);
  const auto polynomial_gates=split_top_level_gates(c.parts[3]);
  // The third and fourth components retain nested gates, so their
  // top-level chain remains one typed object until native AST parsing.
  assert(register_gates.size()==3);
  assert(polynomial_gates.size()==1);
  assert(register_gates[0].find("0*x*y")!=std::string::npos);
  assert(register_gates[2]=="0");
  assert(polynomial_gates[0].find("==")!=std::string::npos);
  const auto probe=split_top_level_gates("P==Q==R");
  assert(probe.size()==3 && probe[0]=="P" && probe[1]=="Q" && probe[2]=="R");
  bool failed=false;
  try { (void)construct_source_locked(std::string(kCanonicalSource)+" "); }
  catch(const std::invalid_argument&) { failed=true; }
  assert(failed);
  failed=false;
  try { (void)split_ordered_list("List((x,y],z)"); }
  catch(const std::invalid_argument&) { failed=true; }
  assert(failed);
  failed=false;
  try { (void)split_ordered_list("List(x,,y)"); }
  catch(const std::invalid_argument&) { failed=true; }
  assert(failed);
}
