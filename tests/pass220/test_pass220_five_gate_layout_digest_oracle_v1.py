"""Independent Python standard-library oracle for the Pass220 layout-only digest."""
import hashlib
import unittest

SOURCE_SHA = "ceec282499ddaf48eba1d25b6313c407d9466d379e321b47f9a6b3f752c2a499"
DOMAIN = b"HHS-P220-GATE-LAYOUT-DECL-V1"
OFFSETS = (54, 139, 223, 229, 276)
DEPTHS = (3, 3, 1, 0, 1)
TERMINAL = "e74d56be94f6c1b5a1d19126c4d5acb3548d0ab2c41f9d5ee287f9a1d93bbe08"

def chain(source_hash=bytes.fromhex(SOURCE_SHA), genesis=bytes(32),
          offsets=OFFSETS, depths=DEPTHS):
    assert len(source_hash) == len(genesis) == 32
    assert len(offsets) == len(depths) == 5
    prior = genesis
    for index, (offset, depth) in enumerate(zip(offsets, depths)):
        address = bytes((index, offset >> 8, offset & 255, depth))
        prior = hashlib.sha256(DOMAIN + source_hash + prior + address).digest()
    return prior.hex()

class TestFiveGateLayoutOracle(unittest.TestCase):
    def test_terminal_reference(self):
        self.assertEqual(chain(), TERMINAL)

    def test_source_mismatch(self):
        self.assertNotEqual(chain(source_hash=bytes(32)), TERMINAL)

    def test_genesis_mismatch(self):
        self.assertNotEqual(chain(genesis=bytes([1]) + bytes(31)), TERMINAL)

    def test_source_address_swap(self):
        self.assertNotEqual(chain(offsets=(54, 223, 139, 229, 276)), TERMINAL)

    def test_depth_mutation(self):
        self.assertNotEqual(chain(depths=(3, 3, 1, 1, 1)), TERMINAL)

if __name__ == "__main__":
    unittest.main()
