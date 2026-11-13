"""Pass220 Lane5 native dyadic bridge syntax and non-bypass source contract."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "hhs_runtime/include/hhs_pass220_lane5_dyadic_virtual_bridge_v1.h"
SOURCE = ROOT / "hhs_runtime/cpp/hhs_pass220_lane5_dyadic_virtual_bridge_v1.cpp"


class NativeDyadicBridgeSourceTests(unittest.TestCase):
    def test_inherited_native_route_and_authority_boundary(self):
        header = HEADER.read_text(encoding="utf-8")
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('#include "hhs_pass220_i028_lane5_rna_g3_bridge_v1.h"', header)
        self.assertIn("hhs_exact_pass220_i028_lane5_rna_g3_route(", source)
        self.assertIn("parent.cpp_rna_cell_wall_routed != 1U", source)
        self.assertIn("parent.pqc_firewall_required_for_canonical_admission != 1U", source)
        self.assertIn("parent.signed_environmental_vm81_required != 1U", source)
        self.assertIn("parent.direct_vm81_bypass_authority != 0U", source)
        self.assertIn("candidate.candidate_only = 1U;", source)
        self.assertIn("std::memcpy(candidate.radix72_address, radix72_address, 72)", source)
        self.assertIn("candidate.signed_dyadic_exponent = exponent;", source)
        self.assertIn("*out = candidate;", source)
        self.assertNotIn("hhs_hash216_compute(", source)
        self.assertNotIn("hhs_hash72_mint(", source)

    def test_native_runtime_build_object_registration(self):
        make = (ROOT / "GNUmakefile").read_text(encoding="utf-8")
        self.assertIn("PASS220_LANE5_DYADIC_BRIDGE_SRC := ", make)
        self.assertIn("PASS169_RUNTIME_BINDING_SRCS += $(PASS220_LANE5_DYADIC_BRIDGE_OBJ)", make)
        self.assertIn("$(ABI_LIB): $(PASS220_LANE5_DYADIC_BRIDGE_OBJ)", make)
        self.assertIn("$(PASS220_LANE5_DYADIC_BRIDGE_OBJ): $(PASS220_LANE5_DYADIC_BRIDGE_SRC)", make)
        self.assertIn("$(CXX) $(CXXFLAGS) -fPIC -c $(PASS220_LANE5_DYADIC_BRIDGE_SRC)", make)

    @unittest.skipUnless(shutil.which("g++"), "g++ not available")
    def test_native_cpp_syntax_against_existing_headers(self):
        subprocess.run(
            ["g++", "-std=c++17", "-fsyntax-only", "-Wall", "-Wextra",
             "-I", str(ROOT / "hhs_runtime/include"), str(SOURCE)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )


if __name__ == "__main__":
    unittest.main()
