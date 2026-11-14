"""Read-only inherited signed receipt cross-check; synthetic reports are tests only."""
from copy import deepcopy
from hashlib import sha256
import unittest

from hhs_runtime.pass219.vm81_rna_bigint_environment_admission_probe import (
    SCHEMA, NEGATIVE_MODES, _digest,
)
from hhs_runtime.pass220.lane5_dyadic_signed_environmental_evidence import (
    cross_check_inherited_signed_environmental_evidence,
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
