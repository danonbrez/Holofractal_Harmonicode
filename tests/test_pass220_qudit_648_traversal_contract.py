"""Pass 220 regression gate: Lo Shu spatial traversal over existing 648-byte VM81 ABI.

This test deliberately imports the established Pass 219 raw little-endian codec.
It does not mint Hash72/Hash216 authority or introduce normalization gates.
"""
import unittest

from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    raw_le_to_words,
    words_to_raw_le,
)

NUCLEI = ((8, 3, 4), (1, 5, 9), (6, 7, 2))
LO_SHU = ((4, 9, 2), (3, 5, 7), (8, 1, 6))
BLOCK_BYTES = 648
WORD_COUNT = 81


def position(matrix, value):
    return next(
        (row, col)
        for row, values in enumerate(matrix)
        for col, cell in enumerate(values)
        if cell == value
    )


def spatial_path():
    """Map ordered (g, l) positions to one-based VM81 spatial coordinates."""
    return tuple(
        tuple(3 * macro + local + 1 for macro, local in zip(
            position(NUCLEI, group), position(LO_SHU, cell)
        ))
        for group in range(1, 10)
        for cell in range(1, 10)
    )


class Pass220Qudit648TraversalTests(unittest.TestCase):
    def test_exact_coverage_and_order(self):
        path = spatial_path()
        self.assertEqual(len(path), WORD_COUNT)
        self.assertEqual(len(set(path)), WORD_COUNT)
        self.assertEqual(set(path), {
            (row, col) for row in range(1, 10) for col in range(1, 10)
        })
        self.assertEqual(path[0], (6, 2))
        self.assertEqual(path[9], (9, 8))
        self.assertEqual(path[-1], (4, 8))

    def test_existing_native_little_endian_round_trip(self):
        path = spatial_path()
        fixtures = (
            bytes(BLOCK_BYTES),
            bytes(index % 256 for index in range(BLOCK_BYTES)),
            bytes([255] * BLOCK_BYTES),
            bytes([128]) + bytes(BLOCK_BYTES - 2) + bytes([1]),
        )
        for original in fixtures:
            with self.subTest(first_byte=original[0], last_byte=original[-1]):
                words = raw_le_to_words(original)
                self.assertEqual(len(words), WORD_COUNT)
                spatial = dict(zip(path, words))
                reconstructed = words_to_raw_le(
                    tuple(spatial[address] for address in path)
                )
                self.assertEqual(reconstructed, original)

    def test_invalid_frame_length_rejected(self):
        for length in (0, BLOCK_BYTES - 1, BLOCK_BYTES + 1):
            with self.subTest(length=length):
                with self.assertRaises(Exception):
                    raw_le_to_words(bytes(length))


if __name__ == "__main__":
    unittest.main()
