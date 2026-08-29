from __future__ import annotations

import json
import socket
import tempfile
import threading
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from hhs_runtime.pass187.adapters import http_get, read_file, run_process, unix_socket_roundtrip
from hhs_runtime.pass187.composition import (
    COMPLETION_CLASSIFICATION,
    CompositionAuthority,
    graph_to_harmonicode,
    parse_harmonicode,
)
from hhs_runtime.pass187.composition_server import Handler


class Pass187CompositionAcceptance(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "composition.sqlite3"
        self.a = CompositionAuthority(self.db, project_id="project.acceptance")
        self.receipt_counter = 1

    def tearDown(self) -> None:
        self.a.close()
        self.tmp.cleanup()

    def receipt(self) -> str:
        value = f"{self.receipt_counter:072x}"
        self.receipt_counter += 1
        return value

    def descriptor(
        self,
        logical_id: str,
        object_class: str,
        *,
        inputs: list[tuple[str, str]] | None = None,
        outputs: list[tuple[str, str]] | None = None,
        modalities: list[str] | None = None,
        state: dict | None = None,
        trusted: bool = True,
        targets: list[str] | None = None,
        source_identity: str | None = None,
    ) -> dict:
        return CompositionAuthority.descriptor(
            logical_object_id=logical_id,
            object_class=object_class,
            modality_set=modalities or [object_class],
            content_identity=f"content:{logical_id}:v1",
            source_identity=source_identity or f"source:{logical_id}",
            provenance={"test": "pass187", "logical_id": logical_id},
            owner_or_mutation_authority="owner.test",
            permissions=["connect", "compile", "read", "replace"],
            inputs=[{"name": name, "type": typ} for name, typ in (inputs or [])],
            outputs=[{"name": name, "type": typ} for name, typ in (outputs or [])],
            operations=["execute", "inspect"],
            dependencies=[],
            state_schema={"type": "object"},
            state=state or {"value": logical_id},
            compatible_egress_targets=targets or ["web-app", "project-bundle", "native-cli"],
            trusted=trusted,
        )

    def add(self, descriptor: dict) -> dict:
        return self.a.create_object(descriptor, self.receipt())

    def connect(
        self,
        edge_id: str,
        source: str,
        sport: str,
        target: str,
        tport: str,
        relationship: str = "LIVE",
        metadata: dict | None = None,
    ) -> dict:
        return self.a.connect(
            edge_id=edge_id,
            source_logical_object_id=source,
            source_port=sport,
            target_logical_object_id=target,
            target_port=tport,
            relationship=relationship,
            vm81_receipt_hash72=self.receipt(),
            metadata=metadata,
        )

    def test_all_twelve_normative_scenarios(self) -> None:
        # 1. Graphics -> animation -> video; unrelated object never reruns.
        self.add(self.descriptor("image", "image_layer", outputs=[("frame", "image/frame")], modalities=["image"]))
        self.add(self.descriptor("animation", "animation", inputs=[("frame", "image/frame")], outputs=[("video", "video/frame")], modalities=["animation", "video"]))
        self.add(self.descriptor("video", "video", inputs=[("video", "video/frame")], outputs=[("render", "video/render")], modalities=["video"]))
        self.add(self.descriptor("unrelated.scene", "scene_asset", outputs=[("asset", "scene/asset")], modalities=["scene"]))
        self.connect("edge.image.animation", "image", "frame", "animation", "frame")
        self.connect("edge.animation.video", "animation", "video", "video", "video")
        first = self.a.recompose(
            ["image"],
            self.receipt(),
            authority_scope="vm81:test",
            license_scope="license:test",
        )["result"]
        self.assertEqual(first["executed"], ["image", "animation", "video"])
        unrelated_before = first["execution_counts"]["unrelated.scene"]
        self.a.replace_object(
            "image",
            state_update={"pixels": "changed"},
            content_identity="content:image:v2",
            vm81_receipt_hash72=self.receipt(),
        )
        second = self.a.recompose(
            ["image"],
            self.receipt(),
            authority_scope="vm81:test",
            license_scope="license:test",
        )["result"]
        self.assertEqual(second["executed"], ["image", "animation", "video"])
        self.assertEqual(second["execution_counts"]["unrelated.scene"], unrelated_before)
        self.assertIn("unrelated.scene", second["unaffected"])

        # 2. Audio -> explicit envelope adapter -> motion; unrelated texture stays cached.
        self.add(self.descriptor("audio", "audio_track", outputs=[("pcm", "audio/pcm")], modalities=["audio"]))
        self.add(self.descriptor(
            "envelope.adapter",
            "adapter",
            inputs=[("pcm", "audio/pcm")],
            outputs=[("envelope", "control/envelope")],
            modalities=["audio", "control"],
        ))
        self.add(self.descriptor("motion", "animation_control", inputs=[("envelope", "control/envelope")], outputs=[("motion", "animation/motion")], modalities=["animation"]))
        self.add(self.descriptor("lighting.texture", "texture", outputs=[("texture", "image/texture")], modalities=["image"]))
        self.connect("edge.audio.adapter", "audio", "pcm", "envelope.adapter", "pcm")
        self.connect("edge.adapter.motion", "envelope.adapter", "envelope", "motion", "envelope")
        audio_run = self.a.recompose(
            ["audio"], self.receipt(), authority_scope="vm81:test", license_scope="license:test"
        )["result"]
        lighting_before = audio_run["execution_counts"]["lighting.texture"]
        self.a.replace_object(
            "audio",
            state_update={"sample_root": "new"},
            content_identity="content:audio:v2",
            vm81_receipt_hash72=self.receipt(),
        )
        audio_run2 = self.a.recompose(
            ["audio"], self.receipt(), authority_scope="vm81:test", license_scope="license:test"
        )["result"]
        self.assertEqual(audio_run2["executed"], ["audio", "envelope.adapter", "motion"])
        self.assertEqual(audio_run2["execution_counts"]["lighting.texture"], lighting_before)

        # 3. Editable document fans out to narration, captions, animation and reel.
        self.add(self.descriptor("document", "document", outputs=[("text", "text/plain")], modalities=["text"], state={"text": "first draft"}))
        self.add(self.descriptor("narration", "speech", inputs=[("text", "text/plain")], outputs=[("audio", "audio/pcm")], modalities=["audio", "text"]))
        self.add(self.descriptor("captions", "captions", inputs=[("text", "text/plain")], outputs=[("captions", "text/captions")], modalities=["text", "video"]))
        self.add(self.descriptor("doc.animation", "animation_script", inputs=[("text", "text/plain")], outputs=[("animation", "animation/data")], modalities=["animation", "text"]))
        self.add(self.descriptor(
            "reel",
            "video_project",
            inputs=[("audio", "audio/pcm"), ("captions", "text/captions"), ("animation", "animation/data")],
            outputs=[("mp4", "video/mp4")],
            modalities=["video", "audio", "text", "animation"],
        ))
        self.connect("edge.doc.narration", "document", "text", "narration", "text")
        self.connect("edge.doc.captions", "document", "text", "captions", "text")
        self.connect("edge.doc.animation", "document", "text", "doc.animation", "text")
        self.connect("edge.narration.reel", "narration", "audio", "reel", "audio")
        self.connect("edge.captions.reel", "captions", "captions", "reel", "captions")
        self.connect("edge.docanimation.reel", "doc.animation", "animation", "reel", "animation")
        doc_v1 = self.a.objects()["document"]["immutable_version_id"]
        self.a.replace_object(
            "document",
            state_update={"text": "second draft"},
            content_identity="content:document:v2",
            vm81_receipt_hash72=self.receipt(),
        )
        self.assertNotEqual(self.a.objects()["document"]["immutable_version_id"], doc_v1)
        self.assertEqual(self.a.objects()["document"]["state"]["text"], "second draft")

        # 4. Spreadsheet -> chart -> dashboard compiles a working web application.
        self.add(self.descriptor("sheet", "spreadsheet_range", outputs=[("table", "data/table")], modalities=["data"]))
        self.add(self.descriptor("chart", "chart", inputs=[("table", "data/table")], outputs=[("chart", "chart/spec")], modalities=["data", "graphics"]))
        self.add(self.descriptor("dashboard", "application", inputs=[("chart", "chart/spec")], outputs=[("app", "app/port")], modalities=["application", "data"]))
        self.connect("edge.sheet.chart", "sheet", "table", "chart", "table")
        self.connect("edge.chart.dashboard", "chart", "chart", "dashboard", "chart")
        web_path = self.root / "dashboard.html"
        compiled_web = self.a.compile_target("web-app", web_path, self.receipt())
        self.assertTrue(web_path.exists())
        self.assertIn("Compiled HHS composition application", web_path.read_text())
        self.assertEqual(compiled_web["result"]["artifact"]["target"], "web-app")

        # 5. Working application nests inside another while retaining independent states and shared ports.
        self.add(self.descriptor("child.app", "application", outputs=[("shared", "app/port")], modalities=["application"], state={"counter": 7}))
        self.add(self.descriptor("parent.app", "application", inputs=[("child", "app/port")], outputs=[("out", "app/port")], modalities=["application"], state={"counter": 2}))
        self.connect("edge.child.parent", "child.app", "shared", "parent.app", "child", relationship="NEST")
        self.assertEqual(self.a.objects()["child.app"]["state"]["counter"], 7)
        self.assertEqual(self.a.objects()["parent.app"]["state"]["counter"], 2)
        self.assertEqual(self.a.state()["edges"]["edge.child.parent"]["relationship"], "NEST")

        # 6. Executable Linux microphone-loopback evidence is admitted only through explicit adapter nodes.
        mic_evidence = run_process(["sh", "-c", "printf pcm-frame"])
        self.assertEqual(mic_evidence["stdout"], "pcm-frame")
        self.assertFalse(mic_evidence["canonical_mutation_authority"])
        self.add(self.descriptor(
            "microphone.loopback",
            "device",
            outputs=[("pcm", "audio/pcm")],
            modalities=["device", "audio"],
            source_identity=mic_evidence["evidence_hash72"],
        ))
        self.add(self.descriptor(
            "device.adapter",
            "adapter",
            inputs=[("pcm", "audio/pcm")],
            outputs=[("stream", "app/stream")],
            modalities=["device", "application"],
        ))
        self.add(self.descriptor("live.app", "application", inputs=[("stream", "app/stream")], outputs=[("out", "app/port")], modalities=["application", "device"]))
        self.connect("edge.mic.adapter", "microphone.loopback", "pcm", "device.adapter", "pcm")
        self.connect("edge.device.live", "device.adapter", "stream", "live.app", "stream")
        device_run = self.a.recompose(
            ["microphone.loopback"], self.receipt(), authority_scope="vm81:test", license_scope="license:test"
        )["result"]
        self.assertEqual(device_run["executed"], ["microphone.loopback", "device.adapter", "live.app"])

        # 7. Recorded manual workflow is parameterized and deterministically replayed structurally.
        seq_start = self.connect("edge.document.sheetref", "document", "text", "captions", "text", relationship="REFERENCE")["sequence"]
        recorded = self.a.record_template(
            "template.document-reference",
            seq_start,
            seq_start,
            self.receipt(),
            parameterize={"document": "source"},
        )
        self.assertIn("${source}", json.dumps(recorded["result"]))
        replay_a = self.a.template_replay_structure("template.document-reference", {"source": "document"})
        replay_b = self.a.template_replay_structure("template.document-reference", {"source": "document"})
        self.assertEqual(replay_a, replay_b)
        self.assertEqual(replay_a["operations"][0]["operation"], "REFERENCE")

        # 8. Reverse an admitted transform, then preserve transformed and prior lineages with a branch.
        before_reverse = self.a.objects()["document"]["immutable_version_id"]
        changed = self.a.replace_object(
            "document",
            state_update={"text": "branch transform"},
            content_identity="content:document:branch",
            vm81_receipt_hash72=self.receipt(),
        )
        transformed_id = changed["result"]["immutable_version_id"]
        self.a.branch("branch.transformed", self.receipt())
        self.a.reverse(changed["sequence"], self.receipt())
        restored_id = self.a.objects()["document"]["immutable_version_id"]
        self.assertEqual(restored_id, before_reverse)
        branch_projection = self.a.state()["branches"]["branch.transformed"]["projection"]
        self.assertEqual(
            branch_projection["objects"]["document"]["active_version_id"],
            transformed_id,
        )

        # 9. Ten-node chain incremental rebuild runs only affected closure.
        chain = [f"chain.{i}" for i in range(10)]
        for index, logical_id in enumerate(chain):
            self.add(self.descriptor(
                logical_id,
                "pipeline_node",
                inputs=[] if index == 0 else [("in", "chain/value")],
                outputs=[("out", "chain/value")],
                modalities=["data"],
            ))
            if index:
                self.connect(
                    f"edge.chain.{index-1}.{index}",
                    chain[index - 1],
                    "out",
                    logical_id,
                    "in",
                )
        baseline = self.a.recompose(
            [chain[0]], self.receipt(), authority_scope="vm81:test", license_scope="license:test"
        )["result"]
        unrelated_snapshot = baseline["execution_counts"]["unrelated.scene"]
        self.a.replace_object(
            chain[0],
            state_update={"value": "changed"},
            content_identity="content:chain.0:v2",
            vm81_receipt_hash72=self.receipt(),
        )
        chain_run = self.a.recompose(
            [chain[0]], self.receipt(), authority_scope="vm81:test", license_scope="license:test"
        )["result"]
        self.assertEqual(chain_run["executed"], chain)
        self.assertEqual(chain_run["execution_counts"]["unrelated.scene"], unrelated_snapshot)

        # 10. Same editable graph compiles to two target families without replacing project authority.
        bundle_path = self.root / "project.hhs.zip"
        compiled_bundle = self.a.compile_target("project-bundle", bundle_path, self.receipt())
        self.assertTrue(bundle_path.exists())
        self.assertEqual(compiled_bundle["result"]["artifact"]["target"], "project-bundle")
        self.assertEqual(self.a.state()["project_id"], "project.acceptance")

        # 11. Invalid and authority-bypassing connections fail closed.
        with self.assertRaises(ValueError):
            self.a.connect(
                edge_id="edge.invalid",
                source_logical_object_id="image",
                source_port="frame",
                target_logical_object_id="audio",
                target_port="missing",
                relationship="LIVE",
                vm81_receipt_hash72=self.receipt(),
            )
        with self.assertRaises(ValueError):
            self.a.replace_object(
                "image",
                state_update={"pixels": "unauthorized"},
                content_identity=None,
                vm81_receipt_hash72="0" * 72,
            )
        imported = self.descriptor(
            "external.untrusted",
            "file",
            outputs=[("bytes", "bytes")],
            modalities=["file"],
            trusted=False,
        )
        self.a.create_object(imported, self.receipt(), imported=True)
        self.assertFalse(self.a.objects()["external.untrusted"]["trusted"])

        # Explicit bounded feedback is accepted; unbounded feedback is rejected.
        self.add(self.descriptor("feedback.node", "control", inputs=[("in", "control/value")], outputs=[("out", "control/value")], modalities=["control"]))
        with self.assertRaises(ValueError):
            self.connect("feedback.bad", "feedback.node", "out", "feedback.node", "in", relationship="FEEDBACK")
        feedback = self.connect(
            "feedback.good",
            "feedback.node",
            "out",
            "feedback.node",
            "in",
            relationship="FEEDBACK",
            metadata={"max_iterations": 8},
        )
        self.assertEqual(feedback["result"]["edge"]["metadata"]["max_iterations"], 8)

        # 12. Cold restart reproduces graph, versions, caches, receipts, replay roots.
        harmonicode_before = graph_to_harmonicode(self.a.state())
        replay_before = self.a.replay()
        checkpoint_path = self.root / "checkpoint.sqlite3"
        checkpoint = self.a.checkpoint(checkpoint_path)
        recovered_path = self.root / "recovered.sqlite3"
        recovered = CompositionAuthority.recover(
            checkpoint_path,
            recovered_path,
            checkpoint["sha256"],
            checkpoint["events"],
            checkpoint["state_identity"],
        )
        try:
            self.assertEqual(recovered.replay(), replay_before)
            self.assertEqual(graph_to_harmonicode(recovered.state()), harmonicode_before)
            self.assertEqual(recovered.state()["cache"], self.a.state()["cache"])
            self.assertEqual(recovered.state()["objects"], self.a.state()["objects"])
        finally:
            recovered.close()

        final = self.a.status()
        self.assertEqual(final["classification"], COMPLETION_CLASSIFICATION)
        self.assertTrue(final["replay"]["valid"])
        self.assertTrue(final["harmonicode_roundtrip"])
        self.assertTrue(final["vm81_receipt_required_for_mutation"])
        self.assertFalse(final["independent_vm81_authority"])
        self.assertFalse(final["independent_hash72_clock"])
        self.assertFalse(final["browser_authority"])
        self.assertFalse(final["cache_authority"])
        self.assertFalse(final["compiled_artifact_authority"])
        self.assertFalse(final["floating_point_canonical_authority"])

    def test_harmonicode_ordering_float_rejection_and_tamper_detection(self) -> None:
        self.add(self.descriptor("A", "node", outputs=[("out", "value")]))
        self.add(self.descriptor("B", "node", inputs=[("in", "value")], outputs=[("out", "value")]))
        self.add(self.descriptor("C", "node", inputs=[("in", "value")]))
        self.connect("e1", "A", "out", "B", "in")
        self.connect("e2", "B", "out", "C", "in")
        state = self.a.state()
        text = graph_to_harmonicode(state)
        parsed = parse_harmonicode(text)
        self.assertEqual(parsed["edges"], state["edges"])
        self.assertNotEqual(
            state["edges"]["e1"]["expression"],
            "LIVE(B.in -> A.out, edge=e1)",
        )
        with self.assertRaises(ValueError):
            bad = self.descriptor("float.node", "node", state={"x": 1})
            bad["state"]["x"] = 1.25
            self.a.create_object(bad, self.receipt())

        event = self.a._connection.execute(
            "SELECT sequence,event_evidence_hash72 FROM events ORDER BY sequence LIMIT 1"
        ).fetchone()
        self.a._connection.execute(
            "UPDATE events SET event_evidence_hash72=? WHERE sequence=?",
            ("f" * 72, event["sequence"]),
        )
        self.a._connection.commit()
        self.assertFalse(self.a.replay()["valid"])
        self.a._connection.execute(
            "UPDATE events SET event_evidence_hash72=? WHERE sequence=?",
            (event["event_evidence_hash72"], event["sequence"]),
        )
        self.a._connection.commit()
        self.assertTrue(self.a.replay()["valid"])

    def test_linux_adapters_http_cli_sse_and_reversal_compensation(self) -> None:
        fixture = self.root / "fixture.txt"
        fixture.write_text("adapter-file")
        file_result = read_file(fixture)
        self.assertEqual(file_result["payload_size"], len("adapter-file"))
        self.assertFalse(file_result["canonical_mutation_authority"])

        process_result = run_process(["sh", "-c", "cat"], stdin=b"stdin-evidence")
        self.assertEqual(process_result["stdout"], "stdin-evidence")

        socket_path = str(self.root / "adapter.sock")
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind(socket_path)
        server_socket.listen(1)

        def socket_server() -> None:
            conn, _ = server_socket.accept()
            try:
                data = conn.recv(1024)
                conn.sendall(data[::-1])
            finally:
                conn.close()
                server_socket.close()

        thread = threading.Thread(target=socket_server)
        thread.start()
        try:
            socket_result = unix_socket_roundtrip(socket_path, b"abcdef")
        finally:
            thread.join(timeout=3)
        self.assertEqual(socket_result["response"], "fedcba")

        class EchoHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                body = b"http-evidence"
                self.send_response(200)
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            def log_message(self, format: str, *args) -> None:
                return

        http_server = ThreadingHTTPServer(("127.0.0.1", 0), EchoHandler)
        http_thread = threading.Thread(target=http_server.serve_forever, daemon=True)
        http_thread.start()
        try:
            http_result = http_get("127.0.0.1", http_server.server_address[1], "/")
        finally:
            http_server.shutdown()
            http_server.server_close()
            http_thread.join(timeout=3)
        self.assertEqual(http_result["body"], "http-evidence")

        self.add(self.descriptor("http.object", "object", outputs=[("out", "value")]))
        Handler.authority = self.a
        Handler.web_root = Path("native_projects/hhs_pass187_composition_fabric/web")
        api_server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        api_thread = threading.Thread(target=api_server.serve_forever, daemon=True)
        api_thread.start()
        try:
            base = f"http://127.0.0.1:{api_server.server_address[1]}"
            with urllib.request.urlopen(base + "/api/pass187/status", timeout=3) as response:
                status = json.loads(response.read())
            self.assertTrue(status["replay"]["valid"])
            request = urllib.request.Request(
                base + "/api/pass187/execute",
                data=json.dumps({"operation": "OBJECTS", "args": {}}).encode(),
                headers={"content-type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=3) as response:
                objects = json.loads(response.read())
            self.assertIn("http.object", objects["result"])
            with urllib.request.urlopen(base + "/api/pass187/events", timeout=3) as response:
                sse = response.read().decode()
            self.assertIn("event: candidate_graph_intent", sse)
            self.assertIn("event: authority_admission", sse)
            self.assertIn("event: runtime_execution", sse)
            self.assertIn("event: projection_update", sse)
            self.assertIn("event: receipt_commit", sse)
        finally:
            api_server.shutdown()
            api_server.server_close()
            api_thread.join(timeout=3)

        out = self.root / "cli.html"
        compiled = self.a.compile_target("web-app", out, self.receipt())
        with self.assertRaises(PermissionError) as caught:
            self.a.reverse(compiled["sequence"], self.receipt())
        self.assertIn("delete_artifact", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
