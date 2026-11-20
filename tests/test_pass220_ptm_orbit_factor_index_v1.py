"""Regression tests for uploaded P=9042 and P=1..31 orbit evidence."""
import unittest
from hhs_runtime.pass220 import pass220_ptm_orbit_factor_index_v1 as indexed

class TestPtmOrbitFactorIndex(unittest.TestCase):
    def test_original_generator_and_native_boundary(self):
        r=indexed.receipt()
        self.assertEqual(indexed.GENERATOR,
            "(((3*x+1)^2+(3*x+1)/2^y+41)/List(x-1==z,x==(z+w)/(2*(x^2-z*w)),x+1==w))^List(-2,1,2)")
        self.assertEqual(r["native_ncalc_execution"],"NOT_EXECUTED")

    def test_three_complete_9042_orbits(self):
        a=indexed.composite_index()
        self.assertEqual(tuple(map(len,a["orbits"])),(185,185,185))
        self.assertEqual(a["state_occurrences"],555)
        self.assertEqual(a["distinct_states"],207)
        self.assertEqual(len(a["suffix"]),168)
        self.assertEqual(a["suffix"][0],19318)
        self.assertEqual(len(a["prime_suffixes"]),34)
        self.assertTrue(all(seq[-1]==1 for seq in a["orbits"]))
        self.assertTrue(all(
            b==(a//2 if a%2==0 else 3*a+1)
            for seq in a["orbits"] for a,b in zip(seq,seq[1:])
        ))

    def test_prime_and_product_counts(self):
        a=indexed.composite_index()
        self.assertEqual(a["all_primes_count"],1123)
        self.assertEqual(a["direct_count"],33)
        self.assertEqual(a["factor_count"],124)
        self.assertEqual(a["combined_count"],124)
        self.assertEqual(a["missing_count"],999)
        self.assertEqual(a["shared_suffix_prime_factor_count"],119)
        self.assertEqual(sum(a["prime_factor_positions"][p][0][4]>0 for p in a["prime_factor_positions"]),
                         len(a["prime_factor_positions"]))

    def test_exact_neighbouring_product(self):
        for n in indexed.orbit(9042):
            self.assertEqual((n-1)*(n+1),n*n-1)
        self.assertEqual(9041*9043,9042**2-1)

    def test_small_orbit_motif_index(self):
        b=indexed.motif_index()
        self.assertEqual(b["orbit_entries"],578)
        self.assertEqual(b["ordered_blocks"],29632)
        self.assertEqual(b["nine_cell_positions"],266688)
        self.assertEqual(b["distinct_states"],141)
        self.assertEqual(b["distinct_motifs"],6633)
        self.assertEqual(b["repeated_multi_orbit_motifs"],5956)

    def test_input_guard_and_prime_arithmetic(self):
        for bad in (0,-1,1.0,True):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):indexed.orbit(bad)
        self.assertEqual(indexed.factors(9042),{2:1,3:1,11:1,137:1})
        self.assertTrue(indexed.prime(9041))
        self.assertTrue(indexed.prime(9043))

if __name__=="__main__":
    unittest.main()
