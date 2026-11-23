import hashlib
import json
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from hhs_runtime.hhs_guarded_service_lean_proof_checker_v1 import (
    check_service_lean_proofs, service_lean_proof_binding, build_lean_cellwall_hydration_handoff, lookup_lane5_service_proof_binding, verify_lean_service_provenance_chain, lookup_live_lane5_database, verify_lane5_hydration_metadata, verify_lane5_database_against_repository_receipt, ServiceLeanProofFailure,
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

    def test_receipt_bound_to_service_and_rejects_mismatch(self):
        proof={"path":self.entry["path"],
               "source_sha256":self.entry["source_sha256"],
               "toolchain":"leanprover/lean4:v4.34.0",
               "checker_exit":0,"canonical_mutation_authority":False}
        bound=service_lean_proof_binding(
            service_name="native.example",manifest=[self.entry],
            checked_receipts=(proof,))
        self.assertEqual(bound["service_name"],"native.example")
        self.assertFalse(bound["signed_hash216_admission_verified"])
        self.assertFalse(bound["native_cpp_cell_wall_verified"])
        with self.assertRaisesRegex(ServiceLeanProofFailure,"RECEIPT_MISMATCH"):
            service_lean_proof_binding(
                service_name="native.example",manifest=[self.entry],
                checked_receipts=({**proof,"source_sha256":"0"*64},))

    def test_lean_cpp_lane5_handoff_fail_closed(self):
        proof={"path":self.entry["path"],"source_sha256":self.entry["source_sha256"],
               "toolchain":"leanprover/lean4:v4.34.0",
               "checker_exit":0,"canonical_mutation_authority":False}
        binding=service_lean_proof_binding(
            service_name="native.example",manifest=[self.entry],
            checked_receipts=(proof,))
        native={"service_name":"native.example","cpp_rna_cell_wall_routed":True,
                "canonical_admission_invoked":False,"inherited_hash216":"A"*216}
        node={"node_kind":"CAPABILITY","hash216":"B"*216}
        result=build_lean_cellwall_hydration_handoff(
            proof_binding=binding,native_candidate=native,hydration_node=node)
        self.assertFalse(result["signed_environmental_admission_verified"])
        with self.assertRaisesRegex(ServiceLeanProofFailure,"NATIVE_CANDIDATE_BOUNDARY"):
            build_lean_cellwall_hydration_handoff(
                proof_binding=binding,native_candidate={**native,"canonical_admission_invoked":True},
                hydration_node=node)
        with self.assertRaisesRegex(ServiceLeanProofFailure,"HASH216_CANDIDATE"):
            build_lean_cellwall_hydration_handoff(
                proof_binding=binding,native_candidate=native,
                hydration_node=dict(node,hash216="bad"))

    def test_real_lane5_search_api_contract(self):
        class KnowledgeSpy:
            def __init__(self, records):
                self.records = records
            def search(self, text, *, kinds, limit):
                self.last = (text, kinds, limit)
                return self.records
        binding={"service_name":"native.example","binding_sha256":"a"*64}
        row={"node_kind":"CONSTRUCTOR","source_path":"hhs/runtime/native.py",
             "name":"run","hash216":"Z"*216,"node_id":"constructor:run",
             "payload":{"candidate_only":True}}
        db=KnowledgeSpy([row])
        result=lookup_lane5_service_proof_binding(
            service_name="native.example",module="hhs.runtime.native",
            function="run",proof_binding=binding,knowledge_database=db)
        self.assertEqual(db.last,("run",("CAPABILITY","CONSTRUCTOR"),64))
        self.assertEqual(result["knowledge_hash216"],"Z"*216)
        self.assertFalse(result["canonical_hash216_signed"])
        with self.assertRaisesRegex(ServiceLeanProofFailure,"MISSING_OR_AMBIGUOUS"):
            lookup_lane5_service_proof_binding(
                service_name="native.example",module="hhs.runtime.native",
                function="run",proof_binding=binding,
                knowledge_database=KnowledgeSpy([row,row]))
        with self.assertRaisesRegex(ServiceLeanProofFailure,"IDENTITY_MISMATCH"):
            lookup_lane5_service_proof_binding(
                service_name="wrong",module="hhs.runtime.native",
                function="run",proof_binding=binding,knowledge_database=db)

    def test_native_provenance_chain_rejects_detached_receipt(self):
        proof={"service_name":"native.example","binding_sha256":"a"*64}
        registry={"name":"native.example","module":"native.runtime","function":"run"}
        lane5={"service_name":"native.example","proof_binding_sha256":"a"*64,
               "knowledge_hash216":"X"*216}
        receipt={"service_name":"native.example","knowledge_hash216":"X"*216,
                 "lean_binding_sha256":"a"*64,"cpp_rna_cell_wall_routed":True,
                 "receipt_identity":"native-fixture"}
        result=verify_lean_service_provenance_chain(
            proof_binding=proof,registry_descriptor=registry,
            lane5_binding=lane5,native_receipt=receipt)
        self.assertTrue(result["evidence_identity_consistent"])
        self.assertFalse(result["native_signature_cryptographically_verified"])
        for key, value, error in (
            ("service_name","other","SERVICE_MISMATCH"),
            ("knowledge_hash216","Y"*216,"ROOT_MISMATCH"),
            ("lean_binding_sha256","0"*64,"ROOT_MISMATCH"),
            ("cpp_rna_cell_wall_routed",False,"ROUTE_NOT_PROVEN"),
        ):
            with self.subTest(key=key), self.assertRaisesRegex(ServiceLeanProofFailure,error):
                verify_lean_service_provenance_chain(
                    proof_binding=proof,registry_descriptor=registry,
                    lane5_binding=lane5,native_receipt={**receipt,key:value})

    def test_readonly_hydrated_sqlite_search(self):
        db_path=self.root/"hydration.sqlite"
        con=sqlite3.connect(db_path)
        con.execute("CREATE TABLE knowledge_nodes (node_id TEXT,node_hash216 TEXT,"
                    "node_kind TEXT,name TEXT,source_path TEXT,payload_json TEXT)")
        con.execute("INSERT INTO knowledge_nodes VALUES (?,?,?,?,?,?)",
                    ("constructor:run","Z"*216,"CONSTRUCTOR","run",
                     "hhs/runtime/native.py",json.dumps({"candidate_only":True})))
        con.commit()
        con.close()
        binding={"service_name":"native.example","binding_sha256":"a"*64}
        result=lookup_live_lane5_database(
            database_path=db_path,service_name="native.example",
            module="hhs.runtime.native",function="run",proof_binding=binding)
        self.assertEqual(result["knowledge_hash216"],"Z"*216)
        self.assertFalse(result["canonical_hash216_signed"])
        with sqlite3.connect(db_path) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM knowledge_nodes").fetchone()[0],1)
        with self.assertRaisesRegex(ServiceLeanProofFailure,"MISSING_OR_AMBIGUOUS"):
            lookup_live_lane5_database(
                database_path=db_path,service_name="native.example",
                module="hhs.runtime.native",function="absent",proof_binding=binding)

    def test_hydration_roots_readonly_and_fail_closed(self):
        db_path=self.root/"hydration-roots.sqlite"
        with sqlite3.connect(db_path) as con:
            con.execute("CREATE TABLE hydration_metadata (key TEXT, value TEXT)")
            con.executemany("INSERT INTO hydration_metadata VALUES (?,?)",[
                ("projection_root_hash216","P"*216),
                ("source_dependency_graph_root_hash216","D"*216),
                ("candidate_only","true"),("execution_authority","false"),
                ("canonical_mutation_authority","false")])
        args={"database_path":db_path,"expected_projection_root_hash216":"P"*216,
              "expected_dependency_root_hash216":"D"*216}
        checked=verify_lane5_hydration_metadata(**args)
        self.assertTrue(checked["metadata_matches_expected_roots"])
        self.assertFalse(checked["hash216_signature_verified"])
        with self.assertRaisesRegex(ServiceLeanProofFailure,"PROJECTION_ROOT_MISMATCH"):
            verify_lane5_hydration_metadata(**dict(args,expected_projection_root_hash216="X"*216))
        with self.assertRaisesRegex(ServiceLeanProofFailure,"DEPENDENCY_ROOT_MISMATCH"):
            verify_lane5_hydration_metadata(**dict(args,expected_dependency_root_hash216="X"*216))
        with sqlite3.connect(db_path) as con:
            con.execute("UPDATE hydration_metadata SET value='true' WHERE key='execution_authority'")
        with self.assertRaisesRegex(ServiceLeanProofFailure,"AUTHORITY_METADATA_INVALID"):
            verify_lane5_hydration_metadata(**args)

    def test_receipt_source_schema_rejected(self):
        receipt=self.root/"receipt.json"
        receipt.write_text(json.dumps({"schema":"wrong"}))
        with self.assertRaisesRegex(ServiceLeanProofFailure,"RECEIPT_SCHEMA_INVALID"):
            verify_lane5_database_against_repository_receipt(
                database_path=self.root/"missing.sqlite",receipt_path=receipt)

    def test_receipt_inventory_matches_actual_sqlite(self):
        path=self.root/"inventory.sqlite"
        receipt_path=self.root/"inventory-receipt.json"
        tables=("repository_files","file_dependencies","knowledge_edges","hash216_positions")
        with sqlite3.connect(path) as con:
            con.execute("CREATE TABLE hydration_metadata (key TEXT, value TEXT)")
            con.executemany("INSERT INTO hydration_metadata VALUES (?,?)",(
                ("projection_root_hash216","P"*216),
                ("source_dependency_graph_root_hash216","D"*216),
                ("source_commit","f"*40),
                ("candidate_only","true"),
                ("execution_authority","false"),
                ("canonical_mutation_authority","false"),
            ))
            for table in tables:
                con.execute("CREATE TABLE "+table+" (id TEXT)")
            con.execute("CREATE TABLE knowledge_nodes (node_kind TEXT)")
        status={"schema":"HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_HASH216_DATABASE_1_69"}
        for name in (*tables,"capabilities","constructors"):
            status[name]=0
        receipt={
            "schema":"HHS_PASS_219_LANE5_REPOSITORY_HYDRATION_DATABASE_RECEIPT_1_69",
            "database_binary_is_source_authority":False,
            "database_status":status,
            "projection_root_hash216":"P"*216,
            "source_dependency_graph_root_hash216":"D"*216,
            "source_commit":"f"*40,
        }
        receipt_path.write_text(json.dumps(receipt))
        verified=verify_lane5_database_against_repository_receipt(
            database_path=path,receipt_path=receipt_path)
        self.assertTrue(verified["recorded_counts_verified"])
        self.assertFalse(verified["canonical_vm81_admission_verified"])
        status["constructors"]=1
        receipt_path.write_text(json.dumps(receipt))
        with self.assertRaisesRegex(ServiceLeanProofFailure,"COUNT_MISMATCH"):
            verify_lane5_database_against_repository_receipt(
                database_path=path,receipt_path=receipt_path)

    def test_manifest_required(self):
        with self.assertRaisesRegex(ServiceLeanProofFailure,"MANIFEST_REQUIRED"):
            check_service_lean_proofs([],repo_root=self.root)

if __name__=="__main__":
    unittest.main()
