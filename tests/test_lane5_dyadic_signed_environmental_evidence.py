"""Read-only inherited signed receipt cross-check; synthetic reports are tests only."""
from copy import deepcopy
from hashlib import sha256
import unittest

from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    SCHEMA, NEGATIVE_MODES, _digest,
)
from hhs_runtime.pass220.lane5_dyadic_signed_environmental_evidence import (
    cross_check_inherited_signed_environmental_evidence,
    canonical_dyadic_signed_binding_material,
)
from hhs_runtime.pass220.lane5_dyadic_virtual_register import decode_address


class SignedEvidenceCrosscheckTests(unittest.TestCase):
    def setUp(self):
        self.frame = bytes(range(256)) * 2 + bytes(range(136))
        assert len(self.frame) == 648
        self.fields = {
            "schema": "HHS_LANE5_DYADIC_NATIVE_CANDIDATE_ABI_FIELDS_V1",
            "radix72_address": decode_address(5183),
            "signed_dyadic_exponent_int64": -5,
            "phase_coordinate72": 36,
            "pass159_binding_sha256": "a" * 64,
            "candidate_only": True,
            "vm81_admitted": False,
            "canonical_hash_mutation": None,
        }
        flags = (
            "provider_available", "committed_exact", "committed_bytes_equal_source",
            "reencoded_bigint_exact", "reencoded_metadata_exact",
            "parent_hash216_verified", "child_hash216_verified",
            "inherited_rna_authority_invoked", "canonical_receipt_minted",
            "transition_verified", "child_identity_matches", "signature_verified",
            "environment_verified", "authority_handoff_exact",
        )
        rows = [
            {
                "status": 0,
                "signature_length": 1,
                "committed_raw_sha256": sha256(self.frame).hexdigest()
                if index == 0 else sha256(bytes([index]) * 648).hexdigest(),
                **{flag: True for flag in flags},
            }
            for index in range(12)
        ]
        self.report = {
            "schema": SCHEMA,
            "canonical_admission": {
                "native_probe_supplied": True,
                "positive_case_count": 12,
                "all_twelve_signed_environmental_commits_exact": True,
                "rows": rows,
            },
            "negative_admission": {
                "case_count": len(NEGATIVE_MODES),
                "rows": [
                    {"mode": mode, "failed_closed": True,
                     "committed_frame_zero": True, "canonical_receipt_minted": False}
                    for mode in NEGATIVE_MODES
                ],
            },
            "authority": {
                "existing_environmental_mutator_reused": True,
                **{key: False for key in (
                    "new_canonical_mutation_authority",
                    "new_canonical_receipt_authority",
                    "hash72_minting_authority_added",
                    "hash216_persistence_authority_added",
                    "floating_point_authority", "ordered_pq_qp_collapse",
                )},
            },
        }
        self.seal()

    def seal(self):
        self.report["report_sha256"] = _digest(
            {k: v for k, v in self.report.items() if k != "report_sha256"}
        )

    def test_cross_language_native_golden_vector(self):
        frame = bytearray(648)
        for index, word in enumerate((0x3ff0000000000000, 9, 9)):
            frame[index*8:(index+1)*8] = word.to_bytes(8, "little")
        fields = dict(self.fields,
                      radix72_address=tuple([71,70] + [0]*70),
                      signed_dyadic_exponent_int64=-5,
                      phase_coordinate72=36)
        material = canonical_dyadic_signed_binding_material(fields, bytes(frame))
        self.assertEqual(len(material["material"]), 197)
        self.assertEqual(material["candidate_frame_sha256"],
                         "309e1fea34ed8dc272a54356500b5c9629bbfe9c8bb0cda2b6b1a870fb6eccfe")
        self.assertEqual(material["material_sha256"],
                         "07a1c469e409e1c911cf5ddae73a3419e98d2df44356a8a05ecb72be53ae1788")

    def test_exact_dyadic_binding_material_no_unsigned_promotion(self):
        original = canonical_dyadic_signed_binding_material(self.fields, self.frame)
        expected_length = len(
            b"HHS/PASS220/LANE5/DYADIC/SIGNED-BINDING-MATERIAL/V1"
        ) + 1 + 72 + 8 + 1 + 32 + 32
        self.assertEqual(len(original["material"]), expected_length)
        self.assertEqual(original["material_sha256"], sha256(original["material"]).hexdigest())
        self.assertFalse(original["signed_by_inherited_environmental_authority"])
        self.assertFalse(original["included_in_inherited_signed_instruction"])
        self.assertFalse(original["canonical_vm81_admission"])
        variants = [
            (dict(self.fields, radix72_address=decode_address(5184)), self.frame),
            (dict(self.fields, signed_dyadic_exponent_int64=-4), self.frame),
            (dict(self.fields, phase_coordinate72=37), self.frame),
            (dict(self.fields, pass159_binding_sha256="b"*64), self.frame),
            (self.fields, b"Z" + self.frame[1:]),
        ]
        for fields, frame in variants:
            derived = canonical_dyadic_signed_binding_material(fields, frame)
            self.assertNotEqual(derived["material"], original["material"])
            self.assertNotEqual(derived["material_sha256"], original["material_sha256"])
        invalid = [
            dict(self.fields, signed_dyadic_exponent_int64=-(1 << 63)),
            dict(self.fields, phase_coordinate72=72),
            dict(self.fields, radix72_address=tuple([72] + [0]*71)),
            dict(self.fields, pass159_binding_sha256="z"*64),
            dict(self.fields, vm81_admitted=True),
        ]
        for fields in invalid:
            with self.assertRaises((ValueError, TypeError)):
                canonical_dyadic_signed_binding_material(fields, self.frame)

    def test_frame_match_not_dyadic_signed_proof(self):
        evidence = cross_check_inherited_signed_environmental_evidence(
            self.fields, self.frame, self.report
        )
        self.assertTrue(evidence["inherited_committed_frame_match"])
        self.assertFalse(evidence["dyadic_metadata_cryptographically_bound_to_signed_instruction"])
        self.assertFalse(evidence["dyadic_full_master_equation_admitted"])
        self.assertFalse(evidence["canonical_dyadic_hash216_receipt_verified"])

    def test_mismatched_frame_and_tampered_report_fail_closed(self):
        with self.assertRaises(ValueError):
            cross_check_inherited_signed_environmental_evidence(
                self.fields, b"X" * 648, self.report
            )
        report = deepcopy(self.report)
        report["canonical_admission"]["rows"][0]["signature_verified"] = False
        with self.assertRaises(ValueError):
            cross_check_inherited_signed_environmental_evidence(
                self.fields, self.frame, report
            )
        self.report["canonical_admission"]["rows"][0]["signature_verified"] = False
        self.seal()
        with self.assertRaises(ValueError):
            cross_check_inherited_signed_environmental_evidence(
                self.fields, self.frame, self.report
            )

    def test_negative_bypass_and_provenance_rejected(self):
        report = deepcopy(self.report)
        report["negative_admission"]["rows"][0]["canonical_receipt_minted"] = True
        report["report_sha256"] = _digest(
            {k: v for k, v in report.items() if k != "report_sha256"}
        )
        with self.assertRaises(ValueError):
            cross_check_inherited_signed_environmental_evidence(
                self.fields, self.frame, report
            )
        fields = dict(self.fields, pass159_binding_sha256="z" * 64)
        with self.assertRaises(ValueError):
            cross_check_inherited_signed_environmental_evidence(
                fields, self.frame, self.report
            )


if __name__ == "__main__":
    unittest.main()
