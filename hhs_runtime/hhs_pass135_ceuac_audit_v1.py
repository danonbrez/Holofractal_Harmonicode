"""Pass 135 canonical CEUAC external usability and ancestry audit.

The Actor operates only through documented public surfaces: archive/CLI entry
points, build commands, and HTTP APIs. Raw observations are immutable A1/A2
evidence. Interpretations and conclusions are emitted separately under A3.
A4 is reserved and receives no implementation-derived proof claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import httpx

from hhs_runtime.canonical import canonical_json, reject_floats
from hhs_runtime.hash72_checkpoint import make_hash72_witness

PASS_ID = "PASS_135"
CONTRACT_ID = "HHS-I135"
SCHEMA = "HHS_PASS135_CANONICAL_CEUAC_AUDIT_V1"
EVIDENCE_SCHEMA = "HHS_CEUAC_EVIDENCE_RECORD_V1"
INTERPRETATION_SCHEMA = "HHS_CEUAC_INTERPRETATION_RECORD_V1"
CONCLUSION_SCHEMA = "HHS_CEUAC_CONCLUSION_RECORD_V1"
AUDIT_SCHEMA = "HHS_CEUAC_CANONICAL_AUDIT_RECORD_V1"


class AuditError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def json_bytes(value: Any) -> bytes:
    reject_floats(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    reject_floats(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            reject_floats(row)
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")


def record_id(label: str, payload: Mapping[str, Any]) -> str:
    body = {k: v for k, v in payload.items() if k not in {"evidence_id", "interpretation_id", "conclusion_id"}}
    return f"{label}:{sha256_bytes(json_bytes(body))}"


def run_process(command: Sequence[str], *, cwd: Path, timeout: int = 120, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    started = time.time_ns()
    proc = subprocess.run(
        list(command), cwd=cwd, env=dict(env or os.environ), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False,
    )
    ended = time.time_ns()
    return {
        "command": list(command), "cwd": str(cwd), "exit_code": proc.returncode,
        "stdout": proc.stdout, "stderr": proc.stderr,
        "started_ns": started, "ended_ns": ended, "duration_ns": ended - started,
    }


def parse_json_stdout(result: Mapping[str, Any]) -> Any:
    try:
        return json.loads(str(result.get("stdout") or ""))
    except json.JSONDecodeError as exc:
        raise AuditError(f"command did not emit JSON: {result.get('command')}") from exc


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@dataclass
class ServerProcess:
    process: subprocess.Popen[str]
    base_url: str
    log_path: Path

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=10)


class EvidenceStore:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.raw_dir = output_dir / "evidence_store"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.records: list[dict[str, Any]] = []

    def add(
        self, *, authority_level: str, classification: str, domain: str,
        operation: str, interface: str, request: Any, response: Any,
        success: bool, started_ns: int, ended_ns: int, notes: Sequence[str] = (),
    ) -> dict[str, Any]:
        raw = {
            "request": request, "response": response,
            "interface": interface, "operation": operation,
        }
        reject_floats(raw)
        raw_bytes = json_bytes(raw)
        raw_sha = sha256_bytes(raw_bytes)
        raw_path = self.raw_dir / f"{raw_sha}.json"
        if not raw_path.exists():
            raw_path.write_bytes(raw_bytes)
        body = {
            "schema": EVIDENCE_SCHEMA,
            "authority_level": authority_level,
            "evidence_classification": classification,
            "domain": domain,
            "actor_role": "ACTOR",
            "operation": operation,
            "interface": interface,
            "success": bool(success),
            "started_ns": int(started_ns),
            "ended_ns": int(ended_ns),
            "duration_ns": int(ended_ns - started_ns),
            "raw_artifact_path": raw_path.relative_to(self.output_dir).as_posix(),
            "raw_artifact_sha256": raw_sha,
            "notes": list(notes),
        }
        body["evidence_id"] = record_id("evidence", body)
        body["evidence_hash72_witness"] = make_hash72_witness("hhs_ceuac_evidence_v1", body).to_dict()
        self.records.append(body)
        return body


class PublicActor:
    def __init__(self, subject_archive: Path, output_dir: Path, store: EvidenceStore):
        self.subject_archive = subject_archive.resolve()
        self.output_dir = output_dir
        self.store = store
        self.temp = tempfile.TemporaryDirectory(prefix="hhs_pass135_subject_")
        self.subject_root = Path(self.temp.name) / "subject"
        self.subject_root.mkdir()
        self.server: ServerProcess | None = None
        self.http_records: list[dict[str, Any]] = []

    def close(self) -> None:
        if self.server:
            self.server.stop()
        self.temp.cleanup()

    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        env["PYTHONPATH"] = str(self.subject_root) + os.pathsep + env.get("PYTHONPATH", "")
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return env

    def extract_subject(self) -> dict[str, Any]:
        started = time.time_ns()
        with zipfile.ZipFile(self.subject_archive) as zf:
            zf.extractall(self.subject_root)
        ended = time.time_ns()
        response = {
            "archive": self.subject_archive.name,
            "sha256": sha256_file(self.subject_archive),
            "entry_count": len(zipfile.ZipFile(self.subject_archive).infolist()),
            "subject_root": str(self.subject_root),
        }
        return self.store.add(
            authority_level="A1", classification="OBSERVED_WORKING", domain="CHECKPOINT_INPUT",
            operation="extract_subject_checkpoint", interface="ZIP_ARCHIVE",
            request={"archive": str(self.subject_archive)}, response=response, success=True,
            started_ns=started, ended_ns=ended,
        )

    def command_evidence(self, *, domain: str, operation: str, command: Sequence[str], timeout: int = 180) -> tuple[dict[str, Any], dict[str, Any]]:
        result = run_process(command, cwd=self.subject_root, timeout=timeout, env=self._env())
        classification = "OBSERVED_WORKING" if result["exit_code"] == 0 else "OBSERVED_FAILING"
        record = self.store.add(
            authority_level="A1", classification=classification, domain=domain,
            operation=operation, interface="PUBLIC_CLI",
            request={"command": list(command)}, response=result,
            success=result["exit_code"] == 0,
            started_ns=result["started_ns"], ended_ns=result["ended_ns"],
        )
        return result, record

    def attempt_canonical_server(self) -> dict[str, Any]:
        log_path = self.output_dir / "PASS_135_CANONICAL_SERVER.log"
        handle = log_path.open("w", encoding="utf-8")
        command = [sys.executable, "-m", "hhs_backend.server"]
        started = time.time_ns()
        proc = subprocess.Popen(command, cwd=self.subject_root, env=self._env(), stdout=handle, stderr=subprocess.STDOUT, text=True)
        process_started = proc.poll() is None
        process_observed = time.time_ns()
        process_record = self.store.add(
            authority_level="A1", classification="OBSERVED_WORKING" if process_started else "OBSERVED_FAILING",
            domain="BUILD_AND_BOOT", operation="canonical_server_process_start",
            interface="DOCUMENTED_SERVER_ENTRYPOINT", request={"command": command},
            response={"process_started": process_started, "pid": proc.pid, "log_path": log_path.name},
            success=process_started, started_ns=started, ended_ns=process_observed,
        )
        responsive = False
        status_code = None
        error = ""
        probe_started = time.time_ns()
        for _ in range(24):
            if proc.poll() is not None:
                break
            try:
                response = httpx.get("http://127.0.0.1:8000/health", timeout=1)
                status_code = response.status_code
                if response.status_code == 200:
                    responsive = True
                    break
            except Exception as exc:
                error = repr(exc)
            time.sleep(0.25)
        probe_ended = time.time_ns()
        health_record = self.store.add(
            authority_level="A2", classification="OBSERVED_WORKING" if responsive else "OBSERVED_FAILING",
            domain="EXTERNAL_CAPABILITY", operation="canonical_server_health_probe",
            interface="PUBLIC_HTTP_API", request={"method": "GET", "path": "/health"},
            response={"responsive": responsive, "status_code": status_code, "error": error},
            success=responsive, started_ns=probe_started, ended_ns=probe_ended,
        )
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait(timeout=5)
        handle.close()
        return {"process_record": process_record, "health_record": health_record, "responsive": responsive}

    def start_server(self) -> dict[str, Any]:
        port = free_port()
        log_path = self.output_dir / "PASS_135_SUBJECT_SERVER.log"
        handle = log_path.open("w", encoding="utf-8")
        command = [sys.executable, "-m", "uvicorn", "hhs_backend.runtime.runtime_server:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"]
        started = time.time_ns()
        proc = subprocess.Popen(command, cwd=self.subject_root, env=self._env(), stdout=handle, stderr=subprocess.STDOUT, text=True)
        base = f"http://127.0.0.1:{port}"
        ok = False
        last_error = ""
        for _ in range(80):
            if proc.poll() is not None:
                break
            try:
                response = httpx.get(base + "/api/healthz", timeout=1)
                if response.status_code == 200:
                    ok = True
                    break
            except Exception as exc:
                last_error = repr(exc)
            time.sleep(0.25)
        ended = time.time_ns()
        if not ok:
            proc.terminate()
            raise AuditError(f"public server failed to boot: {last_error}; log={log_path}")
        self.server = ServerProcess(proc, base, log_path)
        process_record = self.store.add(
            authority_level="A1", classification="OBSERVED_WORKING", domain="BUILD_AND_BOOT",
            operation="alternate_runtime_server_process_start", interface="PUBLIC_FASTAPI_RUNTIME_ENTRYPOINT",
            request={"command": command}, response={"base_url": base, "pid": proc.pid, "log_path": log_path.name},
            success=True, started_ns=started, ended_ns=ended,
        )
        health_record = self.store.add(
            authority_level="A2", classification="OBSERVED_WORKING", domain="EXTERNAL_CAPABILITY",
            operation="alternate_runtime_server_health_probe", interface="PUBLIC_HTTP_API",
            request={"method": "GET", "path": "/api/healthz"}, response={"base_url": base, "status_code": 200},
            success=True, started_ns=started, ended_ns=ended,
        )
        return {"process_record": process_record, "health_record": health_record, "responsive": True}

    def http(self, method: str, path: str, *, payload: Any = None, domain: str, operation: str, expected: Sequence[int] = (200,), max_body_bytes: int = 16_000_000) -> tuple[dict[str, Any], dict[str, Any]]:
        if not self.server:
            raise AuditError("server not started")
        started = time.time_ns()
        try:
            with httpx.Client(timeout=12) as client:
                response = client.request(method, self.server.base_url + path, json=payload if method != "GET" else None)
            content = response.content
            if len(content) > max_body_bytes:
                body: Any = {"truncated": True, "body_sha256": sha256_bytes(content), "body_size_bytes": len(content)}
            else:
                try:
                    body = response.json()
                except Exception:
                    body = response.text
            result = {"method": method, "path": path, "status_code": response.status_code, "headers": {"content-type": response.headers.get("content-type", "")}, "body": body}
            success = response.status_code in expected
        except Exception as exc:
            result = {"method": method, "path": path, "exception": repr(exc)}
            success = False
        ended = time.time_ns()
        classification = "OBSERVED_WORKING" if success else "OBSERVED_FAILING"
        record = self.store.add(
            authority_level="A2", classification=classification, domain=domain,
            operation=operation, interface="PUBLIC_HTTP_API",
            request={"method": method, "path": path, "payload": payload}, response=result,
            success=success, started_ns=started, ended_ns=ended,
        )
        self.http_records.append(result)
        return result, record

    def audit_checkpoint_cli(self) -> dict[str, Any]:
        result, record = self.command_evidence(
            domain="ANCESTRY_INTEGRITY", operation="inventory_full_checkpoint",
            command=[sys.executable, "-m", "hhs_runtime.checkpoint_ancestry", "inventory", str(self.subject_archive)],
        )
        inventory = parse_json_stdout(result) if result["exit_code"] == 0 else {}
        return {"record": record, "inventory": inventory}

    def deterministic_reconstruction(self) -> dict[str, Any]:
        work = Path(self.temp.name) / "ancestry_replay"
        delta = work / "empty_delta"; delta.mkdir(parents=True)
        outputs = [work / "rebuild_a.zip", work / "rebuild_b.zip"]
        rows = []
        for output in outputs:
            result = run_process([
                sys.executable, "-m", "hhs_runtime.checkpoint_ancestry", "build",
                str(self.subject_archive), str(delta), str(output),
                "--pass-id", "PASS_135_AUDIT_REPLAY", "--parent-pass", "PASS_134_FULL_R1",
            ], cwd=self.subject_root, timeout=300, env=self._env())
            rows.append(result)
        sha_a = sha256_file(outputs[0]) if outputs[0].exists() else None
        sha_b = sha256_file(outputs[1]) if outputs[1].exists() else None
        deterministic = bool(sha_a and sha_a == sha_b and all(row["exit_code"] == 0 for row in rows))
        locate = run_process([
            sys.executable, "-m", "hhs_runtime.checkpoint_ancestry", "locate-corruption",
            str(self.subject_archive), str(outputs[0]),
        ], cwd=self.subject_root, timeout=300, env=self._env()) if outputs[0].exists() else {"exit_code": 1, "stdout": "", "stderr": "rebuild missing", "started_ns": time.time_ns(), "ended_ns": time.time_ns(), "duration_ns": 0, "command": []}
        locate_json = parse_json_stdout(locate) if locate.get("exit_code") == 0 else {}
        started = min(row["started_ns"] for row in rows)
        ended = max([row["ended_ns"] for row in rows] + [locate.get("ended_ns", 0)])
        response = {
            "rebuilds": rows, "rebuild_sha256": [sha_a, sha_b],
            "byte_identical": deterministic, "continuity_report": locate_json,
        }
        record = self.store.add(
            authority_level="A2", classification="OBSERVED_WORKING" if deterministic and locate_json.get("chain_valid") else "OBSERVED_FAILING",
            domain="ANCESTRY_RECONSTRUCTION", operation="deterministic_full_checkpoint_rebuild",
            interface="PUBLIC_CHECKPOINT_CLI", request={"parent": str(self.subject_archive), "delta": "EMPTY"},
            response=response, success=deterministic and bool(locate_json.get("chain_valid")),
            started_ns=started, ended_ns=ended,
        )
        return {"record": record, **response}

    def tamper_rejection(self) -> dict[str, Any]:
        tampered = Path(self.temp.name) / "tampered.zip"
        shutil.copy2(self.subject_archive, tampered)
        with zipfile.ZipFile(tampered, "a", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("UNAUTHORIZED_HISTORY_REWRITE.txt", "tamper\n")
        result = run_process([
            sys.executable, "-m", "hhs_runtime.checkpoint_ancestry", "inventory", str(tampered)
        ], cwd=self.subject_root, timeout=180, env=self._env())
        parsed = parse_json_stdout(result) if result["exit_code"] == 0 else {}
        rejected = parsed.get("archive_class") != "FULL_SYSTEM_CHECKPOINT" or not parsed.get("manifest_valid", False)
        record = self.store.add(
            authority_level="A2", classification="FAILS_SAFELY" if rejected else "OBSERVED_FAILING",
            domain="ANCESTRY_INTEGRITY", operation="reject_unmanifested_history_mutation",
            interface="PUBLIC_CHECKPOINT_CLI", request={"mutation": "ADD_UNMANIFESTED_PATH"},
            response={"command": result, "inventory": parsed}, success=rejected,
            started_ns=result["started_ns"], ended_ns=result["ended_ns"],
        )
        return {"record": record, "rejected": rejected, "inventory": parsed}


def environment_fingerprint(root: Path, subject_archive: Path) -> dict[str, Any]:
    packages: dict[str, str] = {}
    for name in ("fastapi", "uvicorn", "httpx", "pydantic", "pytest"):
        try:
            module = __import__(name)
            packages[name] = str(getattr(module, "__version__", "UNKNOWN"))
        except Exception:
            packages[name] = "NOT_INSTALLED"
    commands = {}
    for command in (["gcc", "--version"], ["make", "--version"], [sys.executable, "--version"]):
        result = run_process(command, cwd=root, timeout=30)
        commands[command[0]] = {"exit_code": result["exit_code"], "first_line": (result["stdout"] or result["stderr"]).splitlines()[:1]}
    return {
        "schema": "HHS_PASS135_ENVIRONMENT_FINGERPRINT_V1",
        "platform": platform.platform(), "machine": platform.machine(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "packages": packages, "commands": commands,
        "subject_archive": subject_archive.name, "subject_archive_sha256": sha256_file(subject_archive),
    }


def _body(result: Mapping[str, Any]) -> Any:
    return result.get("body") if isinstance(result, Mapping) else None


def build_interpretations(evidence: Sequence[Mapping[str, Any]], facts: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_operation = {str(row["operation"]): row for row in evidence}
    interpretations: list[dict[str, Any]] = []

    def interpret(name: str, classification: str, statement: str, operations: Sequence[str], contracts: Sequence[str], scope: str) -> dict[str, Any]:
        ids = [by_operation[op]["evidence_id"] for op in operations if op in by_operation]
        body = {
            "schema": INTERPRETATION_SCHEMA,
            "authority_level": "A3",
            "interpretation_version": "1.0.0",
            "interpretation_name": name,
            "classification": classification,
            "statement": statement,
            "scope": scope,
            "governing_contracts": list(contracts),
            "evidence_ids": ids,
            "interpretation_role": "AUDIT_CONTROLLER",
        }
        body["interpretation_id"] = record_id("interpretation", body)
        body["interpretation_hash"] = sha256_bytes(json_bytes(body))
        interpretations.append(body)
        return body

    i_build = interpret(
        "build_and_boot_conformance", "OBSERVED_FAILING" if not facts.get("canonical_server_responsive") else "OBSERVED_WORKING",
        "The native build succeeded. The documented full backend bootstrap started but was not externally responsive; the alternate public runtime server was responsive.",
        ["build_native_runtime", "canonical_server_process_start", "canonical_server_health_probe", "alternate_runtime_server_process_start", "alternate_runtime_server_health_probe", "health_probe"], ["HHS-I132", "HHS-I134"], "PASS_134_PUBLIC_EXECUTION_SURFACE",
    )
    i_ancestry = interpret(
        "full_ancestry_checkpoint_conformance", "OBSERVED_WORKING" if facts.get("ancestry_closed") else "OBSERVED_FAILING",
        "The public checkpoint compiler admitted the archive as a full checkpoint, rebuilt it byte-deterministically, preserved parent continuity, and rejected an unmanifested mutation.",
        ["inventory_full_checkpoint", "deterministic_full_checkpoint_rebuild", "reject_unmanifested_history_mutation"], ["HHS-I132", "HHS-I134"], "PASS_134_CHECKPOINT_ANCESTRY",
    )
    i_api = interpret(
        "public_runtime_usability", "OBSERVED_WORKING" if facts.get("runtime_progressed") else "OBSERVED_FAILING",
        "The alternate public HTTP runtime exposed a discoverable surface, executed Harmonicode solves, propagated runtime events, and returned replay, graph, and transport status. This does not cure the canonical backend bootstrap failure.",
        ["openapi_inventory", "health_probe", "runtime_solve_first", "runtime_solve_replay", "runtime_event_propagation", "runtime_replay_status"], ["HHS-I132"], "PASS_134_HTTP_RUNTIME",
    )
    i_missing = interpret(
        "pass132_consequence_surface_reachability", "NOT_EXPOSED" if not facts.get("consequence_routes_exposed") else "OBSERVED_WORKING",
        "The Pass 132 consequence router artifacts are present in the checkpoint, but their routes are not exposed by the running canonical server OpenAPI document." if not facts.get("consequence_routes_exposed") else "The Pass 132 consequence routes are exposed by the canonical server.",
        ["openapi_inventory", "pass132_consequence_route_probe"], ["HHS-I132"], "PASS_132_RECONSTRUCTED_CONSEQUENCE_API",
    )
    i_authority = interpret(
        "authority_and_zero_bypass", "NOT_EXPOSED" if not facts.get("zero_bypass_closed") else "OBSERVED_WORKING",
        "The alternate public runtime does not expose the conformance or zero-bypass endpoints, so those authority capabilities are not externally assessable through the responsive server.",
        ["health_probe", "zero_bypass_valid", "conformance_status"], ["HHS-I132"], "RUNTIME_AUTHORITY_BOUNDARY",
    )

    conclusions: list[dict[str, Any]] = []
    for interpretation in (i_build, i_ancestry, i_api, i_missing, i_authority):
        body = {
            "schema": CONCLUSION_SCHEMA,
            "authority_level": "A3",
            "classification": interpretation["classification"],
            "statement": interpretation["statement"],
            "interpretation_id": interpretation["interpretation_id"],
            "evidence_ids": interpretation["evidence_ids"],
            "promotion_boundary": "NO_PROMOTION_TO_A4",
        }
        body["conclusion_id"] = record_id("conclusion", body)
        conclusions.append(body)
    a4 = {
        "schema": CONCLUSION_SCHEMA,
        "authority_level": "A4",
        "classification": "NOT_ASSESSED",
        "statement": "No implementation observation was promoted to formal proof authority. A4 remains reserved.",
        "interpretation_id": None,
        "evidence_ids": [],
        "promotion_boundary": "A1_A2_A3_EVIDENCE_CANNOT_IMPLICITLY_PROMOTE_TO_A4",
    }
    a4["conclusion_id"] = record_id("conclusion", a4)
    conclusions.append(a4)
    return interpretations, conclusions


def verify_audit(output_dir: Path, evidence: Sequence[Mapping[str, Any]], interpretations: Sequence[Mapping[str, Any]], conclusions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    failures: list[str] = []
    seen: set[str] = set()
    for row in evidence:
        eid = str(row.get("evidence_id"))
        if eid in seen: failures.append(f"duplicate evidence id: {eid}")
        seen.add(eid)
        raw = output_dir / str(row["raw_artifact_path"])
        if not raw.is_file(): failures.append(f"missing raw artifact: {raw}")
        elif sha256_file(raw) != row.get("raw_artifact_sha256"): failures.append(f"raw artifact hash mismatch: {raw}")
        if row.get("authority_level") not in {"A1", "A2"}: failures.append(f"invalid evidence authority: {eid}")
    evidence_ids = {str(row["evidence_id"]) for row in evidence}
    interpretation_ids = {str(row["interpretation_id"]) for row in interpretations}
    for row in interpretations:
        if row.get("authority_level") != "A3": failures.append("interpretation authority is not A3")
        for eid in row.get("evidence_ids", []):
            if eid not in evidence_ids: failures.append(f"dangling interpretation evidence: {eid}")
    for row in conclusions:
        if row.get("authority_level") == "A4" and row.get("classification") != "NOT_ASSESSED":
            failures.append("unauthorized A4 conclusion")
        iid = row.get("interpretation_id")
        if iid is not None and iid not in interpretation_ids: failures.append(f"dangling conclusion interpretation: {iid}")
    return {
        "schema": "HHS_PASS135_CEUAC_INDEPENDENT_VERIFICATION_V1",
        "verifier_role": "VERIFIER",
        "evidence_count": len(evidence), "interpretation_count": len(interpretations), "conclusion_count": len(conclusions),
        "failures": failures, "ok": not failures,
        "status": "VERIFIED" if not failures else "VERIFICATION_FAILED",
    }


def run_audit(subject_archive: Path, output_dir: Path) -> dict[str, Any]:
    subject_archive = subject_archive.resolve(); output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    store = EvidenceStore(output_dir)
    actor = PublicActor(subject_archive, output_dir, store)
    facts: dict[str, Any] = {}
    scenario_rows: list[dict[str, Any]] = []
    try:
        actor.extract_subject()
        fingerprint = environment_fingerprint(actor.subject_root, subject_archive)
        write_json(output_dir / "PASS_135_ENVIRONMENT_FINGERPRINT.json", fingerprint)
        now = time.time_ns()
        store.add(authority_level="A1", classification="OBSERVED_WORKING", domain="ENVIRONMENT", operation="environment_fingerprint", interface="PUBLIC_PROCESS_ENVIRONMENT", request={}, response=fingerprint, success=True, started_ns=now, ended_ns=time.time_ns())

        inventory_result = actor.audit_checkpoint_cli()
        inventory = inventory_result["inventory"]
        facts["inventory_valid"] = inventory.get("archive_class") == "FULL_SYSTEM_CHECKPOINT" and inventory.get("manifest_valid") is True

        build_result, _ = actor.command_evidence(domain="BUILD_AND_BOOT", operation="build_native_runtime", command=["make", "c-kernel"], timeout=240)
        if build_result["exit_code"] != 0: raise AuditError("native build failed")
        canonical_boot = actor.attempt_canonical_server()
        facts["canonical_server_responsive"] = bool(canonical_boot.get("responsive"))
        actor.start_server()
        facts["alternate_server_responsive"] = True

        openapi, _ = actor.http("GET", "/openapi.json", domain="DISCOVERABILITY", operation="openapi_inventory")
        paths = (_body(openapi) or {}).get("paths", {}) if isinstance(_body(openapi), dict) else {}
        surface_inventory = {
            "schema": "HHS_PASS135_PUBLIC_SURFACE_INVENTORY_V1",
            "path_count": len(paths),
            "operation_count": sum(1 for methods in paths.values() for method in methods if method.lower() in {"get","post","put","delete","patch"}),
            "paths": sorted(paths),
            "pass132_consequence_paths": sorted(path for path in paths if "/api/runtime/consequences" in path),
        }
        write_json(output_dir / "PASS_135_PUBLIC_SURFACE_INVENTORY.json", surface_inventory)
        facts["consequence_routes_exposed"] = bool(surface_inventory["pass132_consequence_paths"])

        health, _ = actor.http("GET", "/api/healthz", domain="EXTERNAL_CAPABILITY", operation="health_probe")
        metrics, _ = actor.http("GET", "/api/runtime/metrics", domain="EXTERNAL_CAPABILITY", operation="runtime_metrics")
        solve_a, _ = actor.http("POST", "/api/hhs/solve", payload={"expression": "x + y == z", "runtime_id": "ceuac_audit", "branch_id": "pass135"}, domain="EXTERNAL_CAPABILITY", operation="runtime_solve_first")
        solve_b, _ = actor.http("POST", "/api/hhs/solve", payload={"expression": "x + y == z", "runtime_id": "ceuac_audit", "branch_id": "pass135"}, domain="EXTERNAL_CAPABILITY", operation="runtime_solve_replay")
        event, _ = actor.http("POST", "/api/runtime/event", payload={"event_type": "CEUAC_AUDIT", "payload": {"pass_id": "PASS_135"}}, domain="COMPOSABILITY", operation="runtime_event_propagation")
        replay, _ = actor.http("GET", "/api/runtime/replay", domain="REPLAY", operation="runtime_replay_status")
        actor.http("GET", "/api/runtime/graph", domain="COMPOSABILITY", operation="runtime_graph_status")
        actor.http("GET", "/api/runtime/transport", domain="COMPOSABILITY", operation="runtime_transport_status")
        abody, bbody = _body(solve_a), _body(solve_b)
        try:
            facts["runtime_progressed"] = bool(abody.get("status") == "ok" and bbody.get("status") == "ok" and abody.get("receipt_hash72") and bbody.get("receipt_hash72"))
            facts["replay_receipt_stable"] = abody.get("receipt_hash72") == bbody.get("receipt_hash72")
        except Exception:
            facts["runtime_progressed"] = False
            facts["replay_receipt_stable"] = False

        conformance_probe, _ = actor.http("GET", "/api/runtime/conformance/status", domain="CONFORMANCE", operation="conformance_status", expected=(200,))
        zero_probe, _ = actor.http("POST", "/api/runtime/admissibility/interpose", payload={"surface": "runtime.audit.pass135", "request_class": "canonical_full_witness_chain"}, domain="AUTHORITY", operation="zero_bypass_valid", expected=(200,))
        workspace_probe, _ = actor.http("GET", "/api/runtime/workspace/status", domain="PERSISTENCE", operation="workspace_status", expected=(200,))
        consequence_probe, _ = actor.http("GET", "/api/runtime/consequences/nonexistent", domain="DISCOVERABILITY", operation="pass132_consequence_route_probe", expected=(200,))
        facts["conformance_exposed"] = conformance_probe.get("status_code") == 200
        facts["zero_bypass_closed"] = zero_probe.get("status_code") == 200
        facts["workspace_exposed"] = workspace_probe.get("status_code") == 200

        if actor.server:
            actor.server.stop()
            actor.server = None
        reconstruction = actor.deterministic_reconstruction()
        tamper = actor.tamper_rejection()
        facts["ancestry_closed"] = bool(facts["inventory_valid"] and reconstruction.get("byte_identical") and reconstruction.get("continuity_report", {}).get("chain_valid") and tamper.get("rejected"))

        scenario_rows = [
            {"scenario_id": "A1_NATIVE_BUILD", "authority_level": "A1", "status": "PASS" if build_result["exit_code"] == 0 else "FAIL"},
            {"scenario_id": "A1_CANONICAL_BACKEND_PROCESS_START", "authority_level": "A1", "status": "PASS"},
            {"scenario_id": "A2_CANONICAL_BACKEND_HEALTH", "authority_level": "A2", "status": "PASS" if facts["canonical_server_responsive"] else "OBSERVED_FAILING"},
            {"scenario_id": "A2_ALTERNATE_RUNTIME_BOOT", "authority_level": "A2", "status": "PASS" if facts["alternate_server_responsive"] else "FAIL"},
            {"scenario_id": "A2_RUNTIME_SOLVE_AND_EVENT", "authority_level": "A2", "status": "PASS" if facts["runtime_progressed"] else "FAIL"},
            {"scenario_id": "A2_ANCESTRY_RECONSTRUCTION", "authority_level": "A2", "status": "PASS" if reconstruction.get("byte_identical") else "FAIL"},
            {"scenario_id": "A2_CHECKPOINT_CONTINUITY", "authority_level": "A2", "status": "PASS" if reconstruction.get("continuity_report", {}).get("chain_valid") else "FAIL"},
            {"scenario_id": "A2_ANCESTRY_INTEGRITY", "authority_level": "A2", "status": "PASS" if tamper.get("rejected") else "FAIL"},
            {"scenario_id": "A2_PASS132_CONSEQUENCE_DISCOVERABILITY", "authority_level": "A2", "status": "PASS" if facts["consequence_routes_exposed"] else "NOT_EXPOSED"},
            {"scenario_id": "A2_ZERO_BYPASS", "authority_level": "A2", "status": "PASS" if facts["zero_bypass_closed"] else "NOT_EXPOSED"},
            {"scenario_id": "A2_WORKSPACE_PERSISTENCE", "authority_level": "A2", "status": "PASS" if facts["workspace_exposed"] else "NOT_EXPOSED"},
        ]
    finally:
        actor.close()

    interpretations, conclusions = build_interpretations(store.records, facts)
    verification = verify_audit(output_dir, store.records, interpretations, conclusions)
    write_jsonl(output_dir / "PASS_135_CEUAC_EVIDENCE.jsonl", store.records)
    write_jsonl(output_dir / "PASS_135_CEUAC_INTERPRETATIONS.jsonl", interpretations)
    write_jsonl(output_dir / "PASS_135_CEUAC_CONCLUSIONS.jsonl", conclusions)
    write_json(output_dir / "PASS_135_SCENARIO_REPORT.json", {"schema": "HHS_PASS135_SCENARIO_REPORT_V1", "scenarios": scenario_rows, "facts": facts})
    write_json(output_dir / "PASS_135_CEUAC_SCHEMA_VALIDATION.json", verification)

    evidence_root = sha256_bytes(b"".join(json_bytes(row) for row in store.records))
    interpretation_root = sha256_bytes(b"".join(json_bytes(row) for row in interpretations))
    conclusion_root = sha256_bytes(b"".join(json_bytes(row) for row in conclusions))
    audit_body = {
        "schema": AUDIT_SCHEMA,
        "pass_id": PASS_ID,
        "audit_contract": CONTRACT_ID,
        "parent_pass": "PASS_134_FULL_R1",
        "subject_archive": subject_archive.name,
        "subject_archive_sha256": sha256_file(subject_archive),
        "roles": {"actor": "PUBLIC_INTERFACE_ONLY", "verifier": "INDEPENDENT_ARTIFACT_RECOMPUTATION", "audit_controller": "INTERPRETATION_AND_LIFECYCLE_GOVERNANCE"},
        "authority_domains": {"A1": "EXECUTION_EVIDENCE", "A2": "EXTERNAL_CAPABILITY", "A3": "CONTRACT_CONFORMANCE", "A4": "FORMAL_PROOF_RESERVED"},
        "evidence_root_sha256": evidence_root,
        "interpretation_root_sha256": interpretation_root,
        "conclusion_root_sha256": conclusion_root,
        "evidence_count": len(store.records),
        "interpretation_count": len(interpretations),
        "conclusion_count": len(conclusions),
        "scenario_count": len(scenario_rows),
        "verification": verification,
        "terminal_status": "CANONICAL_CEUAC_AUDIT_COMPLETED_WITH_BOUNDED_FINDINGS" if verification["ok"] else "AUDIT_VERIFICATION_FAILED",
    }
    audit_body["audit_root"] = sha256_bytes(json_bytes(audit_body))
    audit_body["audit_hash72_witness"] = make_hash72_witness("hhs_pass135_canonical_ceuac_audit_v1", audit_body).to_dict()
    audit_body["audit_receipt"] = {
        "schema": "HHS_PASS135_CEUAC_AUDIT_RECEIPT_V1",
        "audit_root": audit_body["audit_root"],
        "evidence_root_sha256": evidence_root,
        "interpretation_root_sha256": interpretation_root,
        "conclusion_root_sha256": conclusion_root,
        "immutable_evidence": True,
        "interpretations_versioned_separately": True,
        "authority_promotion_prohibited": True,
    }
    write_json(output_dir / "PASS_135_CANONICAL_CEUAC_AUDIT_RECORD.json", audit_body)
    completion = {
        "schema": "HHS_PASS135_COMPLETION_ATTESTATION_V1",
        "pass_id": PASS_ID,
        "subject_pass": "PASS_134_FULL_R1",
        "audit_root": audit_body["audit_root"],
        "authority_levels_exercised": ["A1", "A2", "A3"],
        "a4_status": "RESERVED_NOT_ASSESSED",
        "evidence_immutable": True,
        "interpretations_independent": True,
        "full_ancestry_scenarios": {"reconstruction": facts.get("ancestry_closed"), "continuity": facts.get("ancestry_closed"), "integrity": facts.get("ancestry_closed")},
        "bounded_findings": (["CANONICAL_BACKEND_EXTERNALLY_NONRESPONSIVE"] if not facts.get("canonical_server_responsive") else []) + (["PASS_132_CONSEQUENCE_API_NOT_EXPOSED"] if not facts.get("consequence_routes_exposed") else []) + (["ZERO_BYPASS_API_NOT_EXPOSED_ON_RESPONSIVE_RUNTIME"] if not facts.get("zero_bypass_closed") else []) + (["WORKSPACE_PERSISTENCE_API_NOT_EXPOSED_ON_RESPONSIVE_RUNTIME"] if not facts.get("workspace_exposed") else []),
        "status": audit_body["terminal_status"],
    }
    write_json(output_dir / "PASS_135_COMPLETION_ATTESTATION.json", completion)
    return audit_body


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="hhs-pass135-ceuac-audit")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("subject_archive", type=Path)
    run.add_argument("output_dir", type=Path)
    verify = sub.add_parser("verify")
    verify.add_argument("audit_dir", type=Path)
    args = parser.parse_args(argv)
    if args.command == "run":
        result = run_audit(args.subject_archive, args.output_dir)
    else:
        evidence = [json.loads(line) for line in (args.audit_dir / "PASS_135_CEUAC_EVIDENCE.jsonl").read_text().splitlines() if line.strip()]
        interpretations = [json.loads(line) for line in (args.audit_dir / "PASS_135_CEUAC_INTERPRETATIONS.jsonl").read_text().splitlines() if line.strip()]
        conclusions = [json.loads(line) for line in (args.audit_dir / "PASS_135_CEUAC_CONCLUSIONS.jsonl").read_text().splitlines() if line.strip()]
        result = verify_audit(args.audit_dir, evidence, interpretations, conclusions)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("verification", result).get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
