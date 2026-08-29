from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from hhs_backend.api.pass191_repository_hydration_routes import (
    _encode_ref,
    _set_runtime_for_tests,
    router,
)
from hhs_runtime.core.hash72_digest_v1 import hash72_digest
from hhs_runtime.pass191.cli import build_parser, dispatch
from hhs_runtime.pass191.repository_hydration import RepositoryHydrationRuntime


def authority(index: int) -> dict[str, object]:
    state = hash72_digest({"domain": "P191_SURFACE_STATE"}, {"index": index})
    receipt = hash72_digest({"domain": "P191_SURFACE_RECEIPT"}, {"index": index})
    return {
        "runtime": {"state_hash72": state},
        "receipt": {"state_hash72": state, "receipt_hash72": receipt},
        "authority_audit": {
            "ok": True,
            "state_hash72": state,
            "receipt_hash72": receipt,
        },
    }


def build_fixture(root: Path) -> None:
    files = {
        "docs/pass191/HHS_PASS_191_GENESIS_TO_RUNTIME_FULL_REPOSITORY_HYDRATION_UNIVERSAL_INVARIANT_CLOSURE.md":
            "# universal\nG41\nxy != yx\n",
        "docs/genesis/GENESIS.md": "GENESIS\n",
        "docs/pass190/PASS_190.md": "Pass 190\n",
        "HHS_PASS_191_DYADIC_QUARTIC_PHASE_LATTICE_PROOF.md": "DQPL\n",
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(relative: str, value: object) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")

    write_json(
        "native_projects/hhs_pass190_operation_fabric/registry/HHS_OPERATION_REGISTRY_V1.json",
        {
            "schema": "HHS_OPERATION_REGISTRY_V1",
            "registry_hash216": "b" * 216,
            "operations": [
                {
                    "operation_id": "system.status",
                    "Hash216_identity": "a" * 216,
                    "implementation_status": "EXECUTABLE_VERIFIED",
                }
            ],
        },
    )
    write_json(
        "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
        "PASS_191_INTEGRATED_PROOF_SEARCH.json",
        {"theorem_decision": {"status": "OBSTRUCTED"}},
    )
    write_json(
        "native_projects/hhs_pass191_dyadic_quartic_phase_lattice/evidence/"
        "PASS_191_INTEGRATED_COMPLETION_RECEIPT.json",
        {
            "classification": "HHS_PASS_191_UNIFIED_MANIFOLD_VM81_PROOF_SEARCH_EXECUTED",
            "visited": 51648192,
            "exact_chain_hits": 837,
            "frontier_size": 16,
            "theorem_decision": {"status": "OBSTRUCTED"},
            "authority_path": ["Pass189", "Pass186", "Pass175", "Pass174", "Hash72"],
            "integrated_manifold_search_hash72": "c" * 72,
            "completion_hash72": "d" * 72,
        },
    )
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "p191surface@test.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Pass191 Surface Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=root, check=True)


class Pass191SurfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        build_fixture(self.root)
        self.runtime = RepositoryHydrationRuntime(self.root, self.root / ".state")
        _set_runtime_for_tests(self.runtime)
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        _set_runtime_for_tests(None)
        self.temp.cleanup()

    def test_openapi_preview_job_replay_and_report(self) -> None:
        status = self.client.get("/v1/hydration/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json()["singleton_vm81_authority"], "INHERITED")

        preview = self.client.post(
            "/v1/hydration/preview",
            json={"commit": "HEAD", "include_objects": False},
        )
        self.assertEqual(preview.status_code, 200)
        self.assertEqual(preview.json()["passes_linked"], 191)
        self.assertTrue(preview.json()["symmetry_valid"])

        created = self.client.post(
            "/v1/hydration/jobs",
            json={"commit": "HEAD", "authority_execution": authority(1)},
        )
        self.assertEqual(created.status_code, 200)
        job_id = created.json()["job_id"]
        resumed = self.client.post(
            f"/v1/hydration/jobs/{job_id}/resume",
            json={"authority_execution": authority(2)},
        )
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["stage"], "COMPLETED")

        verified = self.client.post(f"/v1/hydration/jobs/{job_id}/verify")
        self.assertEqual(verified.status_code, 200)
        self.assertTrue(verified.json()["ok"])

        replayed = self.client.post(f"/v1/hydration/jobs/{job_id}/replay")
        self.assertEqual(replayed.status_code, 200)
        self.assertTrue(replayed.json()["ok"])

        report = self.client.get(f"/v1/hydration/jobs/{job_id}/report")
        self.assertEqual(report.status_code, 200)
        self.assertIn("Pass 191 Repository Hydration", report.text)

        manifest = self.runtime.get_job(job_id)["manifest"]
        object_id = manifest["objects"][0]["hash216_identity"]
        ref = _encode_ref(object_id)
        obj = self.client.get(f"/v1/hydration/objects/{ref}")
        self.assertEqual(obj.status_code, 200)
        self.assertEqual(obj.json()["hash216_identity"], object_id)

    def test_websocket_exposes_typed_lifecycle_without_fabricating_commit(self) -> None:
        job = self.runtime.create_job({}, authority_execution=authority(1))
        with self.client.websocket_connect(f"/v1/hydration/ws/{job['job_id']}") as socket:
            snapshot = socket.receive_json()
            self.assertEqual(snapshot["event"], "SNAPSHOT")
            self.assertEqual(snapshot["stage"], "QUEUED")
            event = socket.receive_json()
            self.assertEqual(event["event"], "LIFECYCLE")
            self.assertEqual(event["stage"], "QUEUED")

    def test_registry_lineage_invariants_surfaces_and_assistant_tools(self) -> None:
        lineage = self.client.get("/v1/hydration/lineage/passes")
        self.assertEqual(lineage.status_code, 200)
        self.assertEqual(len(lineage.json()["records"]), 191)

        invariants = self.client.get("/v1/hydration/invariants")
        self.assertEqual(invariants.status_code, 200)
        self.assertEqual(len(invariants.json()["invariants"]), 10)

        surfaces = self.client.get("/v1/hydration/surfaces")
        self.assertEqual(surfaces.status_code, 200)
        self.assertIn("VISUAL_IDE", surfaces.json()["surfaces"])
        self.assertFalse(surfaces.json()["surface_specific_private_semantics"])

        tools = self.client.get("/v1/hydration/assistant-tools")
        self.assertEqual(tools.status_code, 200)
        self.assertTrue(tools.json()["read_only_first"])
        self.assertEqual(len(tools.json()["tools"]), 15)

        fn = self.client.get("/v1/hydration/functions/system.status")
        self.assertEqual(fn.status_code, 200)
        self.assertEqual(fn.json()["Hash216_identity"], "a" * 216)

    def test_cli_grammar_matches_harmonicode_surface(self) -> None:
        parser = build_parser()
        preview = parser.parse_args(
            [
                "--repository-root",
                str(self.root),
                "--state-root",
                str(self.root / ".cli-state"),
                "hydrate",
                "repository",
                "--preview",
            ]
        )
        result = dispatch(preview)
        self.assertEqual(result["passes_linked"], 191)

        lineage = parser.parse_args(
            [
                "--repository-root",
                str(self.root),
                "--state-root",
                str(self.root / ".cli-state"),
                "lineage",
                "passes",
            ]
        )
        self.assertEqual(len(dispatch(lineage)["records"]), 191)

        symmetry = parser.parse_args(
            [
                "--repository-root",
                str(self.root),
                "--state-root",
                str(self.root / ".cli-state"),
                "symmetry",
                "verify",
            ]
        )
        self.assertTrue(dispatch(symmetry)["valid"])

    def test_production_registration_and_visual_workspace_are_explicit(self) -> None:
        repository_root = Path(__file__).resolve().parents[1]
        server = (repository_root / "hhs_backend/visual_server.py").read_text(encoding="utf-8")
        workspace = (
            repository_root
            / "applications/holofractal_harmonizer/pass191-repository-hydration.html"
        ).read_text(encoding="utf-8")
        import_marker = (
            "from hhs_backend.api.pass191_repository_hydration_routes "
            "import router as pass191_repository_hydration_router"
        )
        include_marker = "app.include_router(pass191_repository_hydration_router)"
        federation_marker = "PUBLIC_API_REGISTRATION = register_public_api_federation(app)"
        self.assertIn(import_marker, server)
        self.assertIn(include_marker, server)
        self.assertLess(server.index(include_marker), server.index(federation_marker))
        self.assertIn('"pass191_repository_hydration_api": "/v1/hydration"', server)
        self.assertIn(
            '"pass191_repository_hydration_studio": "/pass191-repository-hydration.html"',
            server,
        )
        self.assertIn("Repository Hydration", workspace)
        self.assertIn("/v1/hydration/preview", workspace)
        self.assertIn("/v1/hydration/jobs", workspace)
        self.assertIn("Deterministic replay verified.", workspace)


if __name__ == "__main__":
    unittest.main()
