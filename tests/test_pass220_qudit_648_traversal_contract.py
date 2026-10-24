"""Pass 220 regression gate: Lo Shu spatial traversal over existing 648-byte VM81 ABI.

This test deliberately imports the established Pass 219 raw little-endian codec.
It does not mint Hash72/Hash216 authority or introduce normalization gates.
"""
import unittest

from hhs_runtime.pass219.vm81_rna_bigint_execution_binding_probe import (
    raw_le_to_words,
    words_to_raw_le,
    build_execution_cases,
    unpack_vm81_binding_words,
    VM81RNABigIntExecutionBindingProbeError,
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

    def test_typed_pass219_frames_preserve_native_register_semantics(self):
        """The spatial permutation is a view, not a rewrite of typed word offsets."""
        path = spatial_path()
        cases = build_execution_cases()
        self.assertEqual(len(cases), 12)
        for case in cases:
            with self.subTest(opcode=case["opcode"]):
                original = case["raw_bytes"]
                words = raw_le_to_words(original)
                spatial = dict(zip(path, words))
                recovered = tuple(spatial[address] for address in path)
                self.assertEqual(recovered, words)
                self.assertEqual(words_to_raw_le(recovered), original)
                decoded = unpack_vm81_binding_words(recovered)
                self.assertEqual(decoded["bigint"], case["bigint"])
                self.assertEqual(decoded["metadata"]["opcode"], case["opcode"])
                self.assertEqual(decoded["metadata"]["lane"], case["lane"])
                self.assertEqual(decoded["metadata"]["direction"], case["direction"])

    def test_native_little_endian_register_order_is_authoritative(self):
        words = (0x0102030405060708,) + (0,) * (WORD_COUNT - 1)
        raw = words_to_raw_le(words)
        self.assertEqual(raw[:8], bytes.fromhex("0807060504030201"))
        self.assertEqual(raw_le_to_words(raw), words)

    def test_spatial_path_does_not_bypass_typed_header_validation(self):
        case = build_execution_cases()[0]
        words = list(raw_le_to_words(case["raw_bytes"]))
        words[7] ^= 1
        path = spatial_path()
        spatial = dict(zip(path, words))
        recovered = tuple(spatial[address] for address in path)
        with self.assertRaises(VM81RNABigIntExecutionBindingProbeError):
            unpack_vm81_binding_words(recovered)

    def test_invalid_frame_length_rejected(self):
        for length in (0, BLOCK_BYTES - 1, BLOCK_BYTES + 1):
            with self.subTest(length=length):
                with self.assertRaises(Exception):
                    raw_le_to_words(bytes(length))


if __name__ == "__main__":
    unittest.main()
