import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from hhs_runtime.hhs_guarded_service_lean_proof_checker_v1 import (
    check_service_lean_proofs, ServiceLeanProofFailure,
)

class GuardedLeanAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        (self.root/"formal/lean").mkdir(parents=True)
        (self.root/"lean-toolchain").write_text("leanprover/lean4:v4.34.0\n")
        self.file=self.root/"formal/lean/Test.lean"
        self.file.write_text("theorem checked : True := by trivial\n")
        self.entry={"path":"formal/lean/Test.lean",
                    "source_sha256":hashlib.sha256(self.file.read_bytes()).hexdigest()}

    @patch("hhs_runtime.hhs_guarded_service_lean_proof_checker_v1.subprocess.run")
    def test_pinned_execution_required(self, run):
        run.side_effect=[
            type("Result",(),{"returncode":0,"stdout":"Lean (version 4.34.0, x86_64)"})(),
            type("Result",(),{"returncode":0,"stdout":""})(),
        ]
        result=check_service_lean_proofs([self.entry],repo_root=self.root)
        self.assertEqual(len(result),1)
        self.assertFalse(result[0]["canonical_mutation_authority"])
        self.assertEqual(run.call_count,2)

    def test_changed_source_rejected(self):
        with self.assertRaisesRegex(ServiceLeanProofFailure,"SOURCE_DRIFT"):
            check_service_lean_proofs([dict(self.entry,source_sha256="0"*64)],repo_root=self.root)

    def test_path_traversal_rejected(self):
        with self.assertRaisesRegex(ServiceLeanProofFailure,"PATH_INVALID"):
            check_service_lean_proofs([dict(self.entry,path="formal/lean/../Test.lean")],repo_root=self.root)

    @patch("hhs_runtime.hhs_guarded_service_lean_proof_checker_v1.subprocess.run")
    def test_failed_kernel_checker_rejected(self, run):
        run.side_effect=[
            type("Result",(),{"returncode":0,"stdout":"Lean (version 4.34.0, x86_64)"})(),
            type("Result",(),{"returncode":1,"stdout":"error"})(),
        ]
        with self.assertRaisesRegex(ServiceLeanProofFailure,"CHECK_FAILED"):
            check_service_lean_proofs([self.entry],repo_root=self.root)

    def test_manifest_required(self):
        with self.assertRaisesRegex(ServiceLeanProofFailure,"MANIFEST_REQUIRED"):
            check_service_lean_proofs([],repo_root=self.root)

if __name__=="__main__":
    unittest.main()
