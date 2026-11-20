"""Native C/Python parity for exact P9042 orbit, products, factors and block address."""
from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import unittest

from hhs_runtime.pass220.pass220_ptm_native_orbit_binding_v1 import (
    NativeOrbitError, NativeOrbitIndex,
)
from hhs_runtime.pass220.pass220_ptm_orbit_factor_index_v1 import (
    orbit, factors, composite_index,
)


@unittest.skipUnless(os.environ.get("HHS_PTM_ORBIT_NATIVE_LIB"),
                     "Build and supply HHS_PTM_ORBIT_NATIVE_LIB")
class TestNativeOrbitParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = NativeOrbitIndex(Path(os.environ["HHS_PTM_ORBIT_NATIVE_LIB"]))

    def test_orbits_and_integer_invariants(self):
        for start in (9041, 9042, 9043):
            with self.subTest(start=start):
                result = self.native.visit(start)
                self.assertEqual(tuple(row[2] for row in result["states"]), orbit(start))
                self.assertEqual(len(result["states"]), 185)
                self.assertTrue(result["native_integer_execution"])
                self.assertFalse(result["native_ncalc_execution"])

    def test_full_prime_factor_occurrence_parity(self):
        index = composite_index(9042)
        for start in (9041,9042,9043):
            with self.subTest(start=start):
                result = self.native.visit(start)
                actual = Counter(result["factor_positions"])
                expected = Counter(
                    (root,offset,state,side,prime,exponent)
                    for prime,positions in index["prime_factor_positions"].items()
                    for root,offset,state,side,exponent in positions if root==start
                )
                self.assertEqual(actual, expected)

    def test_native_block_addresses(self):
        self.assertEqual(self.native.address(185,0,0,0),0)
        self.assertEqual(self.native.address(185,184,184,8),308024)
        for row,col,cell in ((0,184,8),(4,6,2),(184,0,7)):
            self.assertEqual(self.native.address(185,row,col,cell),
                             9*(row*185+col)+cell)

    def test_full_9042_ordered_cell_roundtrip(self):
        for address in range(185 * 185 * 9):
            row, column, cell = self.native.decode_address(185, address)
            self.assertEqual((row, column, cell),
                             ((address // 9) // 185, (address // 9) % 185, address % 9))
            self.assertEqual(self.native.address(185, row, column, cell), address)

    def test_native_guards(self):
        for args in ((185,185,0,0),(185,0,185,0),(185,0,0,9)):
            with self.subTest(args=args):
                with self.assertRaises(NativeOrbitError):
                    self.native.address(*args)
        with self.assertRaises(NativeOrbitError):
            self.native.decode_address(185, 308025)
        with self.assertRaises(NativeOrbitError):
            self.native.decode_address(0, 0)
        with self.assertRaises(NativeOrbitError):
            self.native.decode_address(2**63, 0)
        with self.assertRaises(NativeOrbitError):
            self.native.visit(9042,max_states=1)
        for start in (0,-1,True,1.0,2**64):
            with self.subTest(start=start):
                with self.assertRaises(ValueError):
                    self.native.visit(start)


if __name__ == "__main__":
    unittest.main()
