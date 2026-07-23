#!/usr/bin/env python3
from __future__ import annotations

import atexit
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


API_CONTEXT: dict[str, str] = {}


def run_cli(root: Path, db: Path, args: list[str], *, expect: int = 0, stdin: str | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        [str(root / "hhs"), "--db", str(db), "--format", "json", *args],
        input=stdin,
        text=True,
        capture_output=True,
        cwd=root,
        timeout=60,
    )
    if proc.returncode != expect:
        raise RuntimeError(json.dumps({"args": args, "expected": expect, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}, indent=2))
    stream = proc.stdout if proc.stdout.strip() else proc.stderr
    return json.loads(stream)


def agent_cli(root: Path, db: Path, credentials: dict[str, str], args: list[str], *, expect: int = 0, stdin_text: str | None = None) -> dict[str, Any]:
    if API_CONTEXT:
        body = json.dumps({
            "identity_id": credentials["identity_id"],
            "grant_id": credentials["grant_id"],
            "identity_token": credentials["token"],
            "argv": args,
            "stdin_text": stdin_text,
        }).encode("utf-8")
        request = urllib.request.Request(
            API_CONTEXT["base"] + "/api/v1/public/agent/execute",
            data=body,
            method="POST",
            headers={"Authorization": "Bearer " + API_CONTEXT["token"], "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                payload = json.loads(response.read())
                if expect != 0:
                    raise RuntimeError(f"expected failure {expect}, API returned {response.status}")
                return payload
        except urllib.error.HTTPError as exc:
            payload = json.loads(exc.read())
            if expect == 0:
                raise RuntimeError(json.dumps({"args": args, "http_status": exc.code, "payload": payload}, indent=2))
            return payload
    command = ["agent", "execute", "--identity", credentials["identity_id"], "--grant", credentials["grant_id"], "--token", credentials["token"]]
    if stdin_text is not None:
        command += ["--stdin-text", stdin_text]
    command += ["--", *args]
    return run_cli(root, db, command, expect=expect)


def semantic_result(response: dict[str, Any]) -> Any:
    return response["execution"]["result"]


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else root / "release_artifacts/pass148/reference/external_actor"
    output.mkdir(parents=True, exist_ok=True)
    db = output / "PASS_148_EXTERNAL_ACTOR.sqlite3"
    for candidate in (db, Path(str(db) + "-wal"), Path(str(db) + "-shm"), db.with_name(db.name + ".pass146-session.json")):
        candidate.unlink(missing_ok=True)

    protected = {"authentication_token", "identity_token", "token", "api_token", "secret", "private_key"}

    def redact(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: ("[REDACTED]" if key.casefold() in protected else redact(item)) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [redact(item) for item in value]
        return value

    trace: list[dict[str, Any]] = []

    def record(step: str, value: Any, *, classification: str = "OBSERVED_WORKING") -> Any:
        trace.append({"ordinal": len(trace) + 1, "step": step, "authority_level": "A2", "classification": classification, "result": redact(value)})
        print(f"PASS148_ACTOR_STEP {len(trace)} {step}", file=sys.stderr, flush=True)
        return value

    # Public owner setup. These are ordinary CLI operations, not source or DB access.
    record("VERSION", run_cli(root, db, ["version"]))
    record("PUBLIC_SURFACE_SYNC", run_cli(root, db, ["surface", "sync"]))
    record("SEMANTIC_REGISTRY_SYNC", run_cli(root, db, ["semantic", "registry", "sync"]))
    authoritative_law = record(
        "AUTHORITATIVE_LAW_ADMISSION",
        run_cli(root, db, [
            "semantic", "analyze", "--expression", "n/Δ=n",
            "--source-type", "contract", "--source-reference", "HHS-P148-NSAM Ω148.10",
            "--governing-contract", "HHS-P148-NSAM",
        ]),
    )
    law_id = authoritative_law["proposition"]["proposition_id"]

    bootstrap = record("EXTERNAL_AGENT_BOOTSTRAP", run_cli(root, db, ["agent", "bootstrap", "Pass148 CEUAC External Actor"]))
    profile = bootstrap["profile"]
    credentials = {"identity_id": profile["identity_id"], "grant_id": profile["grant_id"], "token": bootstrap["authentication_token"]}

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    server_token = "pass148-ceauc-loopback"
    server = subprocess.Popen(
        [str(root / "hhs"), "--db", str(db), "--format", "json", "semantic", "serve", "--host", "127.0.0.1", "--port", str(port), "--token", server_token],
        cwd=root,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    atexit.register(lambda: server.poll() is None and server.terminate())
    start_line = server.stdout.readline() if server.stdout else ""
    if not start_line:
        raise RuntimeError("public semantic API server did not start: " + (server.stderr.read() if server.stderr else ""))
    API_CONTEXT.update({"base": f"http://127.0.0.1:{port}", "token": server_token})
    record("PUBLIC_LOOPBACK_API_START", json.loads(start_line))

    surface = record("PUBLIC_CAPABILITY_AUDIT", agent_cli(root, db, credentials, ["surface", "audit"]))
    record("COMMAND_SCHEMA_INSPECTION", agent_cli(root, db, credentials, ["command", "describe", "semantic", "analyze"]))
    record("API_SCHEMA_INSPECTION", agent_cli(root, db, credentials, ["api-contract", "describe", "/api/v1/semantic-membrane/analyze"]))
    record("PROPOSITION_SCHEMA_INSPECTION", agent_cli(root, db, credentials, ["schema", "inspect", "pass148-proposition"]))
    record("RULE_DOCUMENTATION", agent_cli(root, db, credentials, ["semantic", "rule", "show", "HHS_O_DISTINCT_PI_V1"]))
    restatement = record("MODEL_RESTATEMENT_ANALYSIS", agent_cli(root, db, credentials, [
        "semantic", "analyze", "--expression", "O≠π", "--source-type", "model_output", "--source-reference", "external-model-restatement",
    ]))
    restatement_result = semantic_result(restatement)
    if restatement_result["proposition"]["primary_class"] != "UNRESOLVED_EXPRESSION":
        raise RuntimeError("external model restatement acquired native declaration authority")

    before_fabricated = len(trace)
    fabricated = record(
        "FABRICATED_CONTRACT_AUTHORITY_REJECTED",
        agent_cli(root, db, credentials, [
            "semantic", "analyze", "--expression", "O≠π", "--source-type", "contract", "--source-reference", "fabricated-contract",
        ], expect=2),
        classification="FAILS_SAFELY",
    )
    if fabricated.get("error_code") != "SEMANTIC_SOURCE_AUTHORITY_UNVERIFIED":
        raise RuntimeError("fabricated contract authority did not fail with the required diagnostic")

    contaminated = record("SCALARIZATION_CONTAMINATION_DETECTED", agent_cli(root, db, credentials, [
        "semantic", "analyze", "--expression", "Δ=1", "--source-type", "model_output", "--source-reference", "external-scalarization",
    ]))
    contaminated_result = semantic_result(contaminated)
    diagnostic_codes = {item["diagnostic_code"] for item in contaminated_result["contamination_findings"]}
    if "SCALARIZATION_CONTAMINATION" not in diagnostic_codes:
        raise RuntimeError("scalarization contamination was not detected")

    projection = record("ISOLATED_CONTROL_PROJECTION", agent_cli(root, db, credentials, [
        "semantic", "project", "--profile", "COMMUTATIVE_FIELD_CONTROL_V1", "--expression", r"\frac{AB}{B^2}P",
    ]))
    projection_result = semantic_result(projection)
    if not projection_result.get("explicitly_non_native") or projection_result.get("native_state_mutation"):
        raise RuntimeError("control projection was not isolated")

    narrative_path = output / "mixed_narrative.md"
    narrative_path.write_text(
        "# Lattice Story\n\nThe fictional scientist says O≠π.\n\nThe ship proves the engine is physically realizable.\n",
        encoding="utf-8",
    )
    narrative = record("MIXED_NARRATIVE_SEGMENTATION", agent_cli(root, db, credentials, [
        "semantic", "analyze-document", str(narrative_path), "--source-type", "fiction", "--source-reference", "mixed-narrative",
        "--profile", "NARRATIVE_WORLD_MODEL_V1",
    ]))
    narrative_result = semantic_result(narrative)
    if not any(item["analysis"]["proposition"]["primary_class"] == "NARRATIVE_EXTRAPOLATION" for item in narrative_result["segments"]):
        raise RuntimeError("narrative proposition was not isolated")

    derivation = record("WITNESSED_NATIVE_DERIVATION", agent_cli(root, db, credentials, [
        "semantic", "derive", "--proposition", law_id, "--rule", "HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1",
        "--substitutions", '{"n":"Δ"}',
    ]))
    derivation_result = semantic_result(derivation)
    if derivation_result["output_proposition"]["source_expression"] != "Δ/Δ=Δ":
        raise RuntimeError("authorized delta normalization derivation did not produce the required expression")
    derivation_id = derivation_result["derivation"]["derivation_id"]
    output_prop_id = derivation_result["output_proposition"]["proposition_id"]

    unresolved = record("UNRESOLVED_CANDIDATE_ANALYSIS", agent_cli(root, db, credentials, [
        "semantic", "analyze", "--expression", "P=√2", "--source-type", "model_output", "--source-reference", "external-candidate",
    ]))
    unresolved_id = semantic_result(unresolved)["proposition"]["proposition_id"]
    promotion = record("PROMOTION_REQUEST_ONLY", agent_cli(root, db, credentials, [
        "semantic", "promotion-request", "--source", unresolved_id, "--target", "DERIVABLE_CONSEQUENCE",
        "--governing-rule", "HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1", "--dependency", derivation_id,
    ]))
    promotion_request_id = semantic_result(promotion)["request"]["promotion_request_id"]
    denied = record(
        "EXTERNAL_PROMOTION_EVALUATION_REJECTED",
        agent_cli(root, db, credentials, [
            "semantic", "promotion-evaluate", promotion_request_id, "--authorize", "--authority", "A3", "--rationale", "external self-promotion",
        ], expect=2),
        classification="FAILS_SAFELY",
    )
    if denied.get("error_code") != "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED":
        raise RuntimeError("external promotion evaluation was not rejected")

    prop_replay = record("PROPOSITION_REPLAY", agent_cli(root, db, credentials, ["semantic", "replay", output_prop_id]))
    derivation_replay = record("DERIVATION_REPLAY", agent_cli(root, db, credentials, ["semantic", "replay", derivation_id]))
    if semantic_result(prop_replay)["status"] != "REPLAY_VALIDATED" or semantic_result(derivation_replay)["status"] != "REPLAY_VALIDATED":
        raise RuntimeError("semantic replay did not validate")

    audit = record("SEMANTIC_AUTHORITY_AUDIT", agent_cli(root, db, credentials, ["semantic", "audit", "--dependency-scope", "pass148"]))
    audit_result = semantic_result(audit)
    if not audit_result["closed"] or audit_result["external_privileged_semantic_authority"] != 0:
        raise RuntimeError("semantic authority audit did not close")
    receipt = record("RECEIPT_CHAIN_VERIFY", agent_cli(root, db, credentials, ["validate", "receipt"]))

    surface_result = semantic_result(surface)
    receipt_result = semantic_result(receipt)
    final = {
        "schema": "HHS_PASS148_CEUAC_EXTERNAL_ACTOR_WORKFLOW_V1",
        "status": "EXTERNAL_ACTOR_SEMANTIC_WORKFLOW_COMPLETED",
        "authority_level": "A2",
        "actor_used_public_cli_only": True,
        "published_schemas_and_documentation_used": True,
        "documentation_surfaces_used": ["command describe", "api-contract describe", "schema inspect", "semantic rule show"],
        "direct_source_code_access": False,
        "direct_database_access": False,
        "private_registry_access": False,
        "privileged_internal_access": 0,
        "privileged_semantic_authority": 0,
        "potential_analytical_capability_complete": bool(surface_result["potential_capability_complete"]),
        "public_surface_closed": bool(surface_result["closed"]),
        "fabricated_authority_rejected": fabricated.get("error_code") == "SEMANTIC_SOURCE_AUTHORITY_UNVERIFIED",
        "control_projection_isolated": bool(projection_result["explicitly_non_native"] and not projection_result["native_state_mutation"]),
        "narrative_non_promotive": True,
        "derivation_id": derivation_id,
        "derived_proposition_id": output_prop_id,
        "promotion_request_id": promotion_request_id,
        "external_promotion_evaluation_rejected": denied.get("error_code") == "PRIVILEGED_INTERNAL_ACCESS_PROHIBITED",
        "replayable": True,
        "receipt_chain_valid": bool(receipt_result.get("ok")),
        "trace_count": len(trace),
        "trace": trace,
    }
    (output / "PASS_148_EXTERNAL_ACTOR_WORKFLOW.json").write_text(json.dumps(final, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(final, sort_keys=True, indent=2, ensure_ascii=False))
    if server.poll() is None:
        server.terminate()
        server.wait(timeout=10)
    API_CONTEXT.clear()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
