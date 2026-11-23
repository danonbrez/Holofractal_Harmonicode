import unittest
from hhs_runtime.hhs_pass220_transcription_hydration_membrane_v1 import transcribe_candidate, verify_transcription_candidate

class TranscriptionTests(unittest.TestCase):
    def test_reversible_typed_address(self):
        encoder = lambda raw: b"RNA" + raw[::-1]
        decoder = lambda raw: raw[3:][::-1]
        result = transcribe_candidate("123456789012345678901234567890", index5184=5183,
                                      encode=encoder, decode=decoder)
        self.assertEqual((result["cell81"],result["operation64"]), (80,63))
        self.assertEqual((result["hash72_major"],result["hash72_minor"]),(71,71))
        self.assertEqual([x["operator"] for x in result["ordered_register"]],
                         ["p","pP","pq","P","Pp","Pq","q","qp"])
        self.assertEqual(result["ingress_sha256"], result["egress_sha256"])
        self.assertFalse(result["signed_hash216_admission_verified"])
        self.assertFalse(result["canonical_mint_authority"])

    def test_window_generation_and_replay(self):
        codec = lambda x: b"RNA" + x[::-1]
        inverse = lambda x: x[3:][::-1]
        record = transcribe_candidate("123456789012345678901234567890",index5184=5183,
                                      encode=codec,decode=inverse)
        self.assertEqual(record["window_proof"]["window"]["difference_of_squares"], "1")
        self.assertEqual(record, verify_transcription_candidate(record,encode=codec,decode=inverse))
        mutated = dict(record)
        mutated["window_proof_sha256"] = "0"*64
        with self.assertRaisesRegex(ValueError,"REPLAY_MISMATCH"):
            verify_transcription_candidate(mutated,encode=codec,decode=inverse)

    def test_zero_roundtrip_is_legal(self):
        result = transcribe_candidate("0",index5184=0,encode=lambda x:x,decode=lambda x:x)
        self.assertEqual(result["ordered_register"][0]["operand"], "-1")
        self.assertEqual(result["ordered_register"][6]["operand"], "1")

    def test_reject_lossy_encoder(self):
        with self.assertRaisesRegex(ValueError,"TRANSCRIPTION_NOT_REVERSIBLE"):
            transcribe_candidate("101",index5184=10,encode=lambda x:b"x",decode=lambda x:b"100")

    def test_reject_noncanonical_bigint(self):
        for txt in ("01","-0","+1","1.0"," 1",""):
            with self.subTest(txt=txt), self.assertRaises(ValueError):
                transcribe_candidate(txt,index5184=10,encode=lambda x:x,decode=lambda x:x)

    def test_reject_incorrect_address(self):
        for addr in (-1,5184,1.5,True):
            with self.subTest(addr=addr), self.assertRaises(ValueError):
                transcribe_candidate("1",index5184=addr,encode=lambda x:x,decode=lambda x:x)

if __name__ == "__main__":
    unittest.main()
