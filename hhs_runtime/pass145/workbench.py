from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import zipfile
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .canonical import canonical_json, hash72, sha256_bytes, stable_id, utc_now
from .errors import Pass145Error
from .service import HHS145Service

ENV_MODES = {"ISOLATED", "REFERENCE", "SNAPSHOT", "CLONE", "OVERLAY", "FEDERATION", "PIPELINE", "ENSEMBLE", "CONSENSUS", "NESTED_VM"}
SCRIPT_LANGUAGES = {"HHS_COMMAND", "HARMONICODE", "JSON_WORKFLOW", "JAVASCRIPT", "KNOWLEDGE_RULE", "API_COLLECTION", "LVM_MANIFEST"}
CAPABILITIES = {"QUERY", "SEARCH", "VALIDATE", "INGEST", "DATABASE_READ", "DATABASE_WRITE", "NETWORK", "FILESYSTEM_READ", "FILESYSTEM_WRITE", "NATIVE_RUNTIME", "INTER_SANDBOX", "LOCAL_API"}


class EnvironmentManager:
    def __init__(self, service: HHS145Service):
        self.service = service
        self.db = service.db

    def create(self, name: str, *, namespace: str | None = None, description: str = "", policy: Mapping[str, Any] | None = None, mode: str = "ISOLATED", parent_environment_id: str | None = None, parent_state_root_hash72: str | None = None) -> dict[str, Any]:
        mode = mode.upper()
        if mode not in ENV_MODES:
            raise Pass145Error("COMPOSITION_REJECTED", f"unsupported environment mode: {mode}", "ENVIRONMENT_CREATE")
        namespace = namespace or re.sub(r"[^a-z0-9_.-]+", "-", name.casefold()).strip("-") or "environment"
        policy_obj = {
            "default_isolation": True,
            "cross_environment": "DENY",
            "network": "DENY",
            "filesystem": "ENVIRONMENT_LOCAL_ONLY",
            "max_recursive_depth": 16,
            **dict(policy or {}),
        }
        identity = {"name": name, "namespace": namespace, "description": description, "policy": policy_obj, "mode": mode, "parent_environment_id": parent_environment_id, "parent_state_root_hash72": parent_state_root_hash72}
        env_id = stable_id("ENV", "hhs_pass145_environment_id_v1", identity)
        env_hash = hash72("hhs_pass145_environment_v1", identity)

        def apply(conn):
            if conn.execute("SELECT 1 FROM environments WHERE namespace=?", (namespace,)).fetchone():
                raise Pass145Error("DATABASE_COMMIT_FAILED", f"environment namespace already exists: {namespace}", "ENVIRONMENT_CREATE")
            now = utc_now()
            conn.execute(
                "INSERT INTO environments(environment_id,name,namespace,description,version,parent_environment_id,parent_state_root_hash72,mode,policy_json,frozen,archived,destroyed,environment_hash72,created_at,modified_at) VALUES(?,?,?,?,1,?,?,?,?,0,0,0,?,?,?)",
                (env_id, name, namespace, description, parent_environment_id, parent_state_root_hash72, mode, canonical_json(policy_obj), env_hash, now, now),
            )
            return {"status": "ENVIRONMENT_CREATED", "environment_id": env_id, "namespace": namespace, "environment_hash72": env_hash}

        return self.db.mutate("ENVIRONMENT_CREATE", identity, apply, receipt_type="ENVIRONMENT_RECEIPT")

    def inspect(self, environment_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM environments WHERE environment_id=? OR namespace=?", (environment_id, environment_id)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "environment not found", "ENVIRONMENT_INSPECT", environment_id)
        env = dict(row)
        env["policy"] = json.loads(env.pop("policy_json"))
        env["members"] = [dict(r) for r in self.db.conn.execute("SELECT member_type,member_id,access_mode,member_hash72 FROM environment_members WHERE environment_id=? ORDER BY member_type,member_id", (env["environment_id"],))]
        env["source_count"] = self.db.conn.execute("SELECT COUNT(*) FROM sources WHERE namespace=?", (env["namespace"],)).fetchone()[0]
        env["object_count"] = self.db.conn.execute("SELECT COUNT(*) FROM objects WHERE namespace=?", (env["namespace"],)).fetchone()[0]
        env["script_count"] = self.db.conn.execute("SELECT COUNT(*) FROM scripts WHERE environment_id=?", (env["environment_id"],)).fetchone()[0]
        env["lvm_count"] = self.db.conn.execute("SELECT COUNT(*) FROM lvms WHERE environment_id=?", (env["environment_id"],)).fetchone()[0]
        return env

    def list(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.conn.execute("SELECT environment_id,name,namespace,version,parent_environment_id,mode,frozen,archived,destroyed,environment_hash72 FROM environments ORDER BY name,environment_id")]

    def _assert_mutable(self, environment_id: str) -> dict[str, Any]:
        env = self.inspect(environment_id)
        if env["destroyed"]:
            raise Pass145Error("COMPOSITION_REJECTED", "environment is destroyed", "ENVIRONMENT_MUTATION", env["environment_id"])
        if env["frozen"]:
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "environment is frozen", "ENVIRONMENT_MUTATION", env["environment_id"])
        return env

    def set_frozen(self, environment_id: str, frozen: bool) -> dict[str, Any]:
        env = self.inspect(environment_id)

        def apply(conn):
            conn.execute("UPDATE environments SET frozen=?,version=version+1,modified_at=? WHERE environment_id=?", (1 if frozen else 0, utc_now(), env["environment_id"]))
            return {"status": "ENVIRONMENT_FROZEN" if frozen else "ENVIRONMENT_UNFROZEN", "environment_id": env["environment_id"]}

        return self.db.mutate("ENVIRONMENT_FREEZE" if frozen else "ENVIRONMENT_UNFREEZE", {"environment_id": env["environment_id"]}, apply, receipt_type="ENVIRONMENT_RECEIPT")

    def clone(self, environment_id: str, new_name: str, *, namespace: str | None = None, branch: bool = False) -> dict[str, Any]:
        parent = self.inspect(environment_id)
        root = self.db.database_root()
        created = self.create(new_name, namespace=namespace, description=f"{'Branch' if branch else 'Clone'} of {parent['name']}", policy=parent["policy"], mode="CLONE", parent_environment_id=parent["environment_id"], parent_state_root_hash72=root)
        child_id = created["result"]["environment_id"]
        child = self.inspect(child_id)

        def apply(conn):
            members = conn.execute("SELECT member_type,member_id,access_mode FROM environment_members WHERE environment_id=?", (parent["environment_id"],)).fetchall()
            for m in members:
                payload = {"environment_id": child_id, "member_type": m["member_type"], "member_id": m["member_id"], "access_mode": "COPY_ON_WRITE" if branch else m["access_mode"]}
                conn.execute("INSERT INTO environment_members(environment_id,member_type,member_id,access_mode,member_hash72) VALUES(?,?,?,?,?)", (child_id, m["member_type"], m["member_id"], payload["access_mode"], hash72("hhs_pass145_environment_member_v1", payload)))
            return {"status": "ENVIRONMENT_BRANCHED" if branch else "ENVIRONMENT_CLONED", "parent_environment_id": parent["environment_id"], "environment_id": child_id, "member_count": len(members)}

        copied = self.db.mutate("ENVIRONMENT_BRANCH" if branch else "ENVIRONMENT_CLONE", {"parent_environment_id": parent["environment_id"], "environment_id": child_id, "parent_state_root_hash72": root}, apply, receipt_type="ENVIRONMENT_RECEIPT")
        return {"created": created, "copied": copied, "environment": child}

    def add_member(self, environment_id: str, member_type: str, member_id: str, *, access_mode: str = "READ_WRITE") -> dict[str, Any]:
        env = self._assert_mutable(environment_id)
        member_type = member_type.upper()
        access_mode = access_mode.upper()
        if member_type not in {"SOURCE", "OBJECT", "SCRIPT", "LVM", "ENVIRONMENT", "API_COLLECTION", "SCHEMA"}:
            raise Pass145Error("COMPOSITION_REJECTED", f"unsupported member type {member_type}", "ENVIRONMENT_MEMBER")
        payload = {"environment_id": env["environment_id"], "member_type": member_type, "member_id": member_id, "access_mode": access_mode}
        member_hash = hash72("hhs_pass145_environment_member_v1", payload)

        def apply(conn):
            conn.execute("INSERT OR REPLACE INTO environment_members(environment_id,member_type,member_id,access_mode,member_hash72) VALUES(?,?,?,?,?)", (env["environment_id"], member_type, member_id, access_mode, member_hash))
            conn.execute("UPDATE environments SET version=version+1,modified_at=? WHERE environment_id=?", (utc_now(), env["environment_id"]))
            return {"status": "ENVIRONMENT_MEMBER_ADDED", **payload, "member_hash72": member_hash}

        return self.db.mutate("ENVIRONMENT_MEMBER_ADD", payload, apply, receipt_type="ENVIRONMENT_RECEIPT")

    def diff(self, left_id: str, right_id: str) -> dict[str, Any]:
        left = self.inspect(left_id)
        right = self.inspect(right_id)
        lset = {(m["member_type"], m["member_id"], m["access_mode"]) for m in left["members"]}
        rset = {(m["member_type"], m["member_id"], m["access_mode"]) for m in right["members"]}
        return {
            "schema": "HHS_PASS145_ENVIRONMENT_DIFF_V1",
            "left_environment_id": left["environment_id"],
            "right_environment_id": right["environment_id"],
            "only_left": sorted(lset - rset),
            "only_right": sorted(rset - lset),
            "common": sorted(lset & rset),
            "policy_equal": left["policy"] == right["policy"],
        }

    def merge(self, source_id: str, destination_id: str, *, resolutions: Mapping[str, str] | None = None) -> dict[str, Any]:
        source = self.inspect(source_id)
        destination = self._assert_mutable(destination_id)
        source_members = {(m["member_type"], m["member_id"]): m for m in source["members"]}
        dest_members = {(m["member_type"], m["member_id"]): m for m in destination["members"]}
        conflicts = []
        for key in sorted(set(source_members) & set(dest_members)):
            if source_members[key]["access_mode"] != dest_members[key]["access_mode"]:
                conflicts.append({"member_type": key[0], "member_id": key[1], "source_access": source_members[key]["access_mode"], "destination_access": dest_members[key]["access_mode"]})
        resolutions = dict(resolutions or {})
        unresolved = [c for c in conflicts if f"{c['member_type']}:{c['member_id']}" not in resolutions]
        if unresolved:
            return {"schema": "HHS_PASS145_ENVIRONMENT_MERGE_V1", "status": "MERGE_CONFLICT", "source_environment_id": source["environment_id"], "destination_environment_id": destination["environment_id"], "conflicts": conflicts, "unresolved": unresolved, "mutated": False}

        def apply(conn):
            added = 0
            for key, member in source_members.items():
                resolution = resolutions.get(f"{key[0]}:{key[1]}")
                if resolution == "DESTINATION":
                    continue
                access = member["access_mode"] if resolution != "READ_ONLY" else "READ_ONLY"
                payload = {"environment_id": destination["environment_id"], "member_type": key[0], "member_id": key[1], "access_mode": access}
                conn.execute("INSERT OR REPLACE INTO environment_members(environment_id,member_type,member_id,access_mode,member_hash72) VALUES(?,?,?,?,?)", (destination["environment_id"], key[0], key[1], access, hash72("hhs_pass145_environment_member_v1", payload)))
                added += 1
            conn.execute("UPDATE environments SET version=version+1,modified_at=? WHERE environment_id=?", (utc_now(), destination["environment_id"]))
            return {"status": "ENVIRONMENT_MERGED", "source_environment_id": source["environment_id"], "destination_environment_id": destination["environment_id"], "member_updates": added, "resolved_conflicts": conflicts}

        return self.db.mutate("ENVIRONMENT_MERGE", {"source_environment_id": source["environment_id"], "destination_environment_id": destination["environment_id"], "resolutions": resolutions}, apply, receipt_type="ENVIRONMENT_MERGE_RECEIPT")

    def archive(self, environment_id: str) -> dict[str, Any]:
        env = self.inspect(environment_id)

        def apply(conn):
            conn.execute("UPDATE environments SET archived=1,frozen=1,version=version+1,modified_at=? WHERE environment_id=?", (utc_now(), env["environment_id"]))
            return {"status": "ENVIRONMENT_ARCHIVED", "environment_id": env["environment_id"]}

        return self.db.mutate("ENVIRONMENT_ARCHIVE", {"environment_id": env["environment_id"]}, apply, receipt_type="ENVIRONMENT_RECEIPT")

    def destroy(self, environment_id: str, *, authority: str) -> dict[str, Any]:
        env = self.inspect(environment_id)
        if authority != "EXPLICIT_DESTROY_AUTHORITY":
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "explicit destroy authority required", "ENVIRONMENT_DESTROY", env["environment_id"])

        def apply(conn):
            conn.execute("UPDATE environments SET destroyed=1,archived=1,frozen=1,version=version+1,modified_at=? WHERE environment_id=?", (utc_now(), env["environment_id"]))
            return {"status": "ENVIRONMENT_DESTROYED_LOGICALLY", "environment_id": env["environment_id"], "ancestry_preserved": True, "receipts_preserved": True}

        return self.db.mutate("ENVIRONMENT_DESTROY", {"environment_id": env["environment_id"], "authority": authority}, apply, receipt_type="ENVIRONMENT_RECEIPT")

    def export(self, environment_id: str, path: str | Path) -> dict[str, Any]:
        env = self.inspect(environment_id)
        package = {
            "schema": "HHS_PASS145_ENVIRONMENT_PACKAGE_V1",
            "environment": {k: v for k, v in env.items() if k not in {"created_at", "modified_at"}},
            "scripts": [dict(r) for r in self.db.conn.execute("SELECT * FROM scripts WHERE environment_id=? ORDER BY script_id", (env["environment_id"],))],
            "lvms": [dict(r) for r in self.db.conn.execute("SELECT * FROM lvms WHERE environment_id=? ORDER BY lvm_id", (env["environment_id"],))],
        }
        package["package_hash72"] = hash72("hhs_pass145_environment_package_v1", package)
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(canonical_json(package) + "\n", encoding="utf-8")
        return {"status": "ENVIRONMENT_EXPORTED", "path": str(p), "package_hash72": package["package_hash72"], "sha256": sha256_bytes(p.read_bytes())}

    def import_package(self, path: str | Path, *, new_namespace: str | None = None) -> dict[str, Any]:
        p = Path(path).expanduser().resolve()
        try:
            package = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            raise Pass145Error("INGESTION_REJECTED", f"invalid environment package: {exc}", "ENVIRONMENT_IMPORT") from exc
        claimed = package.get("package_hash72")
        base = dict(package)
        base.pop("package_hash72", None)
        if claimed != hash72("hhs_pass145_environment_package_v1", base):
            raise Pass145Error("REPLAY_MISMATCH", "environment package hash mismatch", "ENVIRONMENT_IMPORT")
        source_env = package["environment"]
        namespace = new_namespace or f"{source_env['namespace']}-import"
        created = self.create(f"{source_env['name']} (import)", namespace=namespace, description=source_env.get("description", ""), policy=source_env.get("policy", {}), mode="SNAPSHOT", parent_environment_id=source_env.get("environment_id"), parent_state_root_hash72=source_env.get("environment_hash72"))
        child_id = created["result"]["environment_id"]
        for member in source_env.get("members", []):
            self.add_member(child_id, member["member_type"], member["member_id"], access_mode="READ_ONLY")
        return {"status": "ENVIRONMENT_IMPORTED", "environment_id": child_id, "source_package_hash72": claimed, "created": created}


class ScriptWorkbench:
    def __init__(self, service: HHS145Service, environments: EnvironmentManager | None = None):
        self.service = service
        self.db = service.db
        self.environments = environments or EnvironmentManager(service)

    def import_script(self, name: str, language: str, source_text: str, *, environment_id: str | None = None, declared_capabilities: Sequence[str] = (), entrypoints: Sequence[str] = (), execution_policy: str = "DENY_BY_DEFAULT", parent_script_id: str | None = None) -> dict[str, Any]:
        language = language.upper()
        if language not in SCRIPT_LANGUAGES:
            raise Pass145Error("INGESTION_REJECTED", f"unsupported script language: {language}", "SCRIPT_IMPORT")
        caps = sorted(set(c.upper() for c in declared_capabilities))
        unknown = sorted(set(caps) - CAPABILITIES)
        if unknown:
            raise Pass145Error("CAPABILITY_OVERBROAD", f"unknown capabilities: {unknown}", "SCRIPT_IMPORT")
        if environment_id:
            self.environments._assert_mutable(environment_id)
        source_hash = hash72("hhs_pass145_script_source_v1", source_text)
        normalized = source_text.replace("\r\n", "\n").replace("\r", "\n")
        normalized_hash = hash72("hhs_pass145_script_normalized_v1", normalized)
        version = 1
        if parent_script_id:
            parent = self.db.conn.execute("SELECT version FROM scripts WHERE script_id=?", (parent_script_id,)).fetchone()
            if not parent:
                raise Pass145Error("PROVENANCE_INCOMPLETE", "parent script not found", "SCRIPT_IMPORT", parent_script_id)
            version = int(parent[0]) + 1
        identity = {"name": name, "language": language, "source_hash72": source_hash, "normalized_hash72": normalized_hash, "environment_id": environment_id, "version": version, "parent_script_id": parent_script_id}
        script_id = stable_id("SCR", "hhs_pass145_script_id_v1", identity)

        def apply(conn):
            conn.execute(
                "INSERT INTO scripts(script_id,environment_id,name,language,source_text,source_hash72,normalized_hash72,entrypoints_json,declared_capabilities_json,resolved_dependencies_json,validation_state,test_state,execution_policy,version,parent_script_id,receipt_root,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?, ?,?,?,?,?,?)",
                (script_id, environment_id, name, language, source_text, source_hash, normalized_hash, canonical_json(list(entrypoints)), canonical_json(caps), canonical_json([]), "UNVALIDATED", "NOT_RUN", execution_policy, version, parent_script_id, None, utc_now()),
            )
            return {"status": "SCRIPT_IMPORTED", "script_id": script_id, "source_hash72": source_hash, "normalized_hash72": normalized_hash, "version": version}

        result = self.db.mutate("SCRIPT_IMPORT", identity, apply, receipt_type="SCRIPT_IMPORT_RECEIPT")
        if environment_id:
            self.environments.add_member(environment_id, "SCRIPT", script_id)
        return result

    def get(self, script_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM scripts WHERE script_id=?", (script_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "script not found", "SCRIPT", script_id)
        out = dict(row)
        for field in ("entrypoints_json", "declared_capabilities_json", "resolved_dependencies_json"):
            out[field.removesuffix("_json")] = json.loads(out.pop(field))
        return out

    def validate(self, script_id: str) -> dict[str, Any]:
        script = self.get(script_id)
        source = script["source_text"]
        language = script["language"]
        diagnostics: list[dict[str, Any]] = []
        dependencies: list[str] = []
        requested = set(script["declared_capabilities"])
        inferred: set[str] = set()
        try:
            if language in {"JSON_WORKFLOW", "KNOWLEDGE_RULE", "API_COLLECTION", "LVM_MANIFEST"}:
                parsed = json.loads(source)
                if language == "JSON_WORKFLOW" and not isinstance(parsed, (list, dict)):
                    diagnostics.append({"severity": "ERROR", "code": "SCRIPT_SCHEMA_INVALID", "message": "workflow must be an object or array"})
            elif language == "JAVASCRIPT":
                if re.search(r"\b(fetch|XMLHttpRequest|WebSocket)\b", source):
                    inferred.add("NETWORK")
                if re.search(r"\b(require\s*\(|process\.|(?:child_process|fs)\b)", source):
                    inferred.update({"NATIVE_RUNTIME", "FILESYSTEM_READ"})
                # Balanced delimiter validation without execution.
                stack: list[str] = []
                pairs = {")": "(", "]": "[", "}": "{"}
                quote = None
                escaped = False
                for idx, ch in enumerate(source):
                    if quote:
                        if escaped:
                            escaped = False
                        elif ch == "\\":
                            escaped = True
                        elif ch == quote:
                            quote = None
                        continue
                    if ch in "'\"`":
                        quote = ch
                    elif ch in "([{":
                        stack.append(ch)
                    elif ch in ")]}":
                        if not stack or stack.pop() != pairs[ch]:
                            diagnostics.append({"severity": "ERROR", "code": "SCRIPT_SYNTAX_ERROR", "message": f"unbalanced delimiter at offset {idx}"})
                            break
                if stack or quote:
                    diagnostics.append({"severity": "ERROR", "code": "SCRIPT_SYNTAX_ERROR", "message": "unclosed delimiter or string"})
            elif language == "HHS_COMMAND":
                for line_no, line in enumerate(source.splitlines(), 1):
                    if not line.strip() or line.lstrip().startswith("#"):
                        continue
                    try:
                        parts = shlex.split(line)
                    except ValueError as exc:
                        diagnostics.append({"severity": "ERROR", "code": "SCRIPT_SYNTAX_ERROR", "line": line_no, "message": str(exc)})
                        continue
                    if not parts or parts[0] not in {"query", "search", "validate", "status", "ingest"}:
                        diagnostics.append({"severity": "ERROR", "code": "SCRIPT_COMMAND_REJECTED", "line": line_no, "message": f"unsupported command: {parts[0] if parts else ''}"})
                    if parts and parts[0] == "ingest":
                        inferred.update({"INGEST", "DATABASE_WRITE", "FILESYSTEM_READ"})
                    else:
                        inferred.add("DATABASE_READ")
            elif language == "HARMONICODE":
                from hhs_runtime.harmonicode_interpreter_v1 import interpret
                interpreted = interpret(source)
                dependencies.append(interpreted.receipt.receipt_hash72)
                inferred.add("NATIVE_RUNTIME")
        except Exception as exc:
            diagnostics.append({"severity": "ERROR", "code": "SCRIPT_VALIDATION_EXCEPTION", "message": str(exc)})
        undeclared = sorted(inferred - requested)
        if undeclared:
            diagnostics.append({"severity": "ERROR", "code": "CAPABILITY_UNDECLARED", "message": f"inferred but undeclared capabilities: {undeclared}"})
        validation_state = "VALIDATED" if not any(d["severity"] == "ERROR" for d in diagnostics) else "RUNTIME_REJECTED"
        result_payload = {"script_id": script_id, "validation_state": validation_state, "diagnostics": diagnostics, "declared_capabilities": sorted(requested), "inferred_capabilities": sorted(inferred), "resolved_dependencies": dependencies}

        def apply(conn):
            conn.execute("UPDATE scripts SET validation_state=?,resolved_dependencies_json=? WHERE script_id=?", (validation_state, canonical_json(dependencies), script_id))
            return result_payload

        return self.db.mutate("SCRIPT_VALIDATE", {"script_id": script_id, "source_hash72": script["source_hash72"]}, apply, receipt_type="SCRIPT_VALIDATION_RECEIPT")

    def execute(self, script_id: str, *, inputs: Mapping[str, Any] | None = None, timeout_seconds: int = 5, max_output_bytes: int = 1_000_000) -> dict[str, Any]:
        script = self.get(script_id)
        if script["validation_state"] != "VALIDATED":
            self.validate(script_id)
            script = self.get(script_id)
        if script["validation_state"] != "VALIDATED":
            raise Pass145Error("RUNTIME_REJECTED", "script is not validated", "SCRIPT_EXECUTION", script_id)
        if timeout_seconds <= 0 or timeout_seconds > 60:
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "timeout must be 1..60 seconds", "SCRIPT_EXECUTION")
        pre = self.db.database_root()
        language = script["language"]
        source = script["source_text"]
        output: Any
        if language == "HHS_COMMAND":
            output = self._execute_hhs_commands(source)
        elif language == "JSON_WORKFLOW":
            output = self._execute_json_workflow(json.loads(source))
        elif language == "JAVASCRIPT":
            output = self._execute_javascript(source, inputs or {}, timeout_seconds, max_output_bytes)
        elif language == "HARMONICODE":
            from hhs_runtime.harmonicode_interpreter_v1 import interpret
            from hhs_runtime.harmonicode_constraint_solver_v1 import solve_interpreter_result
            interpreted = interpret(source)
            solved = solve_interpreter_result(interpreted)
            output = {"interpreter": interpreted.to_dict(), "solver": solved.to_dict()}
        elif language in {"KNOWLEDGE_RULE", "API_COLLECTION", "LVM_MANIFEST"}:
            output = {"status": "DECLARATIVE_OBJECT_LOADED", "value": json.loads(source)}
        else:
            raise Pass145Error("RUNTIME_REJECTED", f"execution adapter unavailable for {language}", "SCRIPT_EXECUTION", script_id)
        post = self.db.database_root()
        deterministic_payload = {"script_id": script_id, "input": dict(inputs or {}), "output": output, "status": "EXECUTION_COMPLETED"}
        execution_hash = hash72("hhs_pass145_script_execution_v1", deterministic_payload)
        execution_id = stable_id("EXE", "hhs_pass145_script_execution_id_v1", {**deterministic_payload, "pre_state_root_hash72": pre, "post_state_root_hash72": post, "occurrence": int(self.db.meta("transaction_sequence") or 0) + 1})

        def apply(conn):
            conn.execute("INSERT INTO executions(execution_id,execution_type,target_id,input_json,output_json,status,pre_state_root_hash72,post_state_root_hash72,execution_hash72,receipt_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (execution_id, "SCRIPT", script_id, canonical_json(dict(inputs or {})), canonical_json(output), "EXECUTION_COMPLETED", pre, post, execution_hash, None, utc_now()))
            conn.execute("UPDATE scripts SET test_state='EXECUTED' WHERE script_id=?", (script_id,))
            return {"status": "SCRIPT_EXECUTED", "execution_id": execution_id, "execution_hash72": execution_hash, "output": output}

        return self.db.mutate("SCRIPT_EXECUTE_RECORD", {"script_id": script_id, "execution_hash72": execution_hash}, apply, receipt_type="SCRIPT_EXECUTION_RECEIPT")

    def _execute_hhs_commands(self, source: str) -> list[dict[str, Any]]:
        results = []
        for line_no, line in enumerate(source.splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = shlex.split(line)
            command, args = parts[0], parts[1:]
            if command == "status":
                result = self.service.status()
            elif command == "query":
                result = self.service.query(" ".join(args))
            elif command == "search":
                result = self.service.search(" ".join(args))
            elif command == "validate" and len(args) == 1:
                result = self.service.validate_source(args[0])
            elif command == "ingest" and len(args) == 1:
                result = self.service.ingest_path(args[0])
            else:
                raise Pass145Error("RUNTIME_REJECTED", f"invalid HHS command at line {line_no}", "SCRIPT_EXECUTION")
            results.append({"line": line_no, "command": command, "result": result})
        return results

    def _execute_json_workflow(self, workflow: Any) -> list[dict[str, Any]]:
        steps = workflow.get("steps", []) if isinstance(workflow, dict) else workflow
        if not isinstance(steps, list) or len(steps) > 1024:
            raise Pass145Error("RESOURCE_BOUNDED", "workflow step bound invalid", "SCRIPT_EXECUTION")
        results = []
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                raise Pass145Error("RUNTIME_REJECTED", f"workflow step {index} must be object", "SCRIPT_EXECUTION")
            op = str(step.get("op", "")).upper()
            if op == "QUERY":
                result = self.service.query(str(step.get("question", "")), namespace=step.get("namespace"))
            elif op == "SEARCH":
                result = self.service.search(str(step.get("text", "")), namespace=step.get("namespace"))
            elif op == "VALIDATE_SOURCE":
                result = self.service.validate_source(str(step["source_id"]))
            else:
                raise Pass145Error("RUNTIME_REJECTED", f"unsupported workflow op: {op}", "SCRIPT_EXECUTION")
            results.append({"index": index, "op": op, "result": result})
        return results

    @staticmethod
    def _execute_javascript(source: str, inputs: Mapping[str, Any], timeout_seconds: int, max_output_bytes: int) -> dict[str, Any]:
        node = shutil.which("node")
        if not node:
            raise Pass145Error("PLATFORM_INCOMPATIBLE", "Node.js sandbox adapter unavailable", "SCRIPT_EXECUTION")
        wrapper = r'''
const vm = require('vm');
const input = JSON.parse(process.argv[1]);
const source = process.argv[2];
const sandbox = Object.create(null);
sandbox.input = input;
sandbox.output = null;
sandbox.console = Object.freeze({log: (...args) => { sandbox.output = args; }});
Object.freeze(sandbox.console);
const context = vm.createContext(sandbox, {name: 'hhs-pass145', codeGeneration: {strings: false, wasm: false}});
const script = new vm.Script(`"use strict";\n${source}\n;JSON.stringify({output: globalThis.output ?? null});`, {filename: 'imported.js'});
const value = script.runInContext(context, {timeout: Number(process.env.HHS_JS_TIMEOUT_MS), breakOnSigint: true});
process.stdout.write(value);
'''
        env = {"PATH": os.environ.get("PATH", ""), "HHS_JS_TIMEOUT_MS": str(timeout_seconds * 1000)}
        try:
            proc = subprocess.run([node, "--max-old-space-size=32", "-e", wrapper, canonical_json(dict(inputs)), source], capture_output=True, text=False, timeout=timeout_seconds + 1, env=env)
        except subprocess.TimeoutExpired as exc:
            raise Pass145Error("RESOURCE_BOUNDED", "JavaScript execution timeout", "SCRIPT_EXECUTION") from exc
        if proc.returncode:
            raise Pass145Error("RUNTIME_REJECTED", proc.stderr.decode("utf-8", errors="replace")[:4000], "SCRIPT_EXECUTION")
        if len(proc.stdout) > max_output_bytes:
            raise Pass145Error("RESOURCE_BOUNDED", "JavaScript output bound reached", "SCRIPT_EXECUTION")
        try:
            return {"mode": "SANDBOX_EXECUTION", "network": "DENIED", "filesystem": "DENIED", "native_runtime": "DENIED", "result": json.loads(proc.stdout.decode("utf-8"))}
        except json.JSONDecodeError as exc:
            raise Pass145Error("RUNTIME_REJECTED", "JavaScript sandbox returned invalid output", "SCRIPT_EXECUTION") from exc


class LVMEngine:
    def __init__(self, service: HHS145Service, scripts: ScriptWorkbench | None = None, environments: EnvironmentManager | None = None):
        self.service = service
        self.db = service.db
        self.environments = environments or EnvironmentManager(service)
        self.scripts = scripts or ScriptWorkbench(service, self.environments)

    def create(self, manifest: Mapping[str, Any], *, environment_id: str | None = None) -> dict[str, Any]:
        validated = self.validate_manifest(manifest)
        name = str(manifest.get("name", "LVM"))
        version = int(manifest.get("version", 1))
        identity = {"name": name, "version": version, "manifest": validated, "environment_id": environment_id}
        lvm_id = str(manifest.get("lvm_id") or stable_id("LVM", "hhs_pass145_lvm_id_v1", identity))
        final_manifest = {**validated, "lvm_id": lvm_id, "name": name, "version": version, "environment_id": environment_id}
        manifest_hash = hash72("hhs_pass145_lvm_manifest_v1", final_manifest)

        def apply(conn):
            conn.execute("INSERT INTO lvms(lvm_id,environment_id,name,version,manifest_json,manifest_hash72,receipt_root,created_at) VALUES(?,?,?,?,?,?,?,?)", (lvm_id, environment_id, name, version, canonical_json(final_manifest), manifest_hash, None, utc_now()))
            return {"status": "LVM_CREATED", "lvm_id": lvm_id, "manifest_hash72": manifest_hash}

        result = self.db.mutate("LVM_CREATE", {"manifest_hash72": manifest_hash, "environment_id": environment_id}, apply, receipt_type="LVM_RECEIPT")
        if environment_id:
            self.environments.add_member(environment_id, "LVM", lvm_id)
        return result

    def get(self, lvm_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM lvms WHERE lvm_id=?", (lvm_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "LVM not found", "LVM", lvm_id)
        out = dict(row)
        out["manifest"] = json.loads(out.pop("manifest_json"))
        return out

    def validate_manifest(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        components = list(manifest.get("components", []))
        if not components or len(components) > 4096:
            raise Pass145Error("COMPOSITION_REJECTED", "LVM requires 1..4096 components", "LVM_VALIDATE")
        ids = [str(c.get("id", "")) for c in components]
        if any(not x for x in ids) or len(ids) != len(set(ids)):
            raise Pass145Error("COMPOSITION_REJECTED", "component IDs must be nonempty and unique", "LVM_VALIDATE")
        allowed_types = {"CONST", "QUERY", "SEARCH", "VALIDATE_SOURCE", "SCRIPT", "NESTED_LVM", "JOIN", "SELECT"}
        for c in components:
            if str(c.get("type", "")).upper() not in allowed_types:
                raise Pass145Error("COMPOSITION_REJECTED", f"unsupported LVM component: {c.get('type')}", "LVM_VALIDATE")
        edges = [dict(e) for e in manifest.get("edges", [])]
        graph: dict[str, list[str]] = {i: [] for i in ids}
        indegree = {i: 0 for i in ids}
        for e in edges:
            a, b = str(e.get("from")), str(e.get("to"))
            if a not in graph or b not in graph:
                raise Pass145Error("COMPOSITION_REJECTED", "edge endpoint missing", "LVM_VALIDATE")
            graph[a].append(b)
            indegree[b] += 1
        queue = deque(sorted(i for i, d in indegree.items() if d == 0))
        order = []
        while queue:
            n = queue.popleft()
            order.append(n)
            for nxt in sorted(graph[n]):
                indegree[nxt] -= 1
                if indegree[nxt] == 0:
                    queue.append(nxt)
        cyclic = len(order) != len(ids)
        cycle_policy = dict(manifest.get("cycle_policy", {}))
        if cyclic:
            max_iterations = int(cycle_policy.get("max_iterations", 0))
            if max_iterations <= 0 or max_iterations > 1024:
                raise Pass145Error("COMPOSITION_REJECTED", "cycle requires bounded max_iterations 1..1024", "LVM_VALIDATE")
        max_depth = int(manifest.get("resource_policy", {}).get("max_recursive_depth", 16))
        if max_depth <= 0 or max_depth > 128:
            raise Pass145Error("RESOURCE_BOUND_UNRESOLVED", "LVM recursive depth must be 1..128", "LVM_VALIDATE")
        return {
            **dict(manifest),
            "components": components,
            "edges": edges,
            "execution_order": order if not cyclic else ids,
            "topology": "BOUNDED_CYCLE" if cyclic else "ACYCLIC_COMPOSITION",
            "resource_policy": {"max_recursive_depth": max_depth, "max_components": 4096, **dict(manifest.get("resource_policy", {}))},
            "failure_policy": manifest.get("failure_policy", "HALT_AND_RECEIPT"),
            "replay_policy": manifest.get("replay_policy", "DETERMINISTIC"),
        }

    @staticmethod
    def _deterministic_projection(value: Any) -> Any:
        """Remove execution-envelope identities while preserving logical results.

        Nested LVMs return transaction receipts from real execution.  Those receipt
        identities must remain in the stored trace, but they are occurrence-specific
        and therefore cannot define semantic replay equality.
        """
        volatile = {
            "transaction_id", "receipt_id", "receipt_hash72", "sequence",
            "pre_state_root_hash72", "post_state_root_hash72", "execution_id",
            "created_at", "modified_at", "receipt_tip", "tip_receipt_id",
            "transaction_sequence", "database_root_hash72",
            "query_result_hash72", "search_result_hash72",
            "validation_result_hash72", "replay_receipt_hash72",
            "execution_hash72", "query_plan_receipt", "query_result_receipt",
        }
        if isinstance(value, dict):
            return {
                key: LVMEngine._deterministic_projection(item)
                for key, item in sorted(value.items())
                if key not in volatile
            }
        if isinstance(value, list):
            return [LVMEngine._deterministic_projection(item) for item in value]
        if isinstance(value, tuple):
            return [LVMEngine._deterministic_projection(item) for item in value]
        return value

    def execute(self, lvm_id: str, inputs: Mapping[str, Any] | None = None, *, _depth: int = 0, _ancestry: tuple[str, ...] = ()) -> dict[str, Any]:
        lvm = self.get(lvm_id)
        manifest = lvm["manifest"]
        max_depth = int(manifest["resource_policy"]["max_recursive_depth"])
        if _depth >= max_depth:
            raise Pass145Error("RESOURCE_BOUNDED", "LVM recursive depth reached", "LVM_EXECUTION", lvm_id)
        if lvm_id in _ancestry:
            if manifest.get("topology") != "BOUNDED_CYCLE":
                raise Pass145Error("COMPOSITION_REJECTED", "unbounded recursive LVM cycle", "LVM_EXECUTION", lvm_id)
        values: dict[str, Any] = {"$input": dict(inputs or {})}
        traces: list[dict[str, Any]] = []
        components = {str(c["id"]): c for c in manifest["components"]}
        pre = self.db.database_root()
        for index, component_id in enumerate(manifest["execution_order"]):
            component = components[component_id]
            ctype = str(component["type"]).upper()
            resolved_input = self._resolve_value(component.get("input", "$input"), values)
            try:
                if ctype == "CONST":
                    output = component.get("value")
                elif ctype == "QUERY":
                    question = str(component.get("question") or resolved_input)
                    output = self.service.query(question, namespace=component.get("namespace"))
                elif ctype == "SEARCH":
                    text = str(component.get("text") or resolved_input)
                    output = self.service.search(text, namespace=component.get("namespace"))
                elif ctype == "VALIDATE_SOURCE":
                    output = self.service.validate_source(str(component.get("source_id") or resolved_input))
                elif ctype == "SCRIPT":
                    output = self.scripts.execute(str(component["script_id"]), inputs=resolved_input if isinstance(resolved_input, dict) else {"value": resolved_input})
                elif ctype == "NESTED_LVM":
                    output = self.execute(str(component["lvm_id"]), resolved_input if isinstance(resolved_input, dict) else {"value": resolved_input}, _depth=_depth + 1, _ancestry=_ancestry + (lvm_id,))
                elif ctype == "JOIN":
                    output = [self._resolve_value(v, values) for v in component.get("inputs", [])]
                elif ctype == "SELECT":
                    source = self._resolve_value(component.get("source"), values)
                    path = str(component.get("path", ""))
                    output = source
                    for part in [p for p in path.split(".") if p]:
                        output = output[int(part)] if isinstance(output, list) else output[part]
                else:
                    raise Pass145Error("RUNTIME_REJECTED", f"unsupported component type: {ctype}", "LVM_EXECUTION", component_id)
                status = "COMPONENT_COMPLETED"
            except Pass145Error as exc:
                output = exc.to_dict()
                status = "COMPONENT_FAILED"
                traces.append({"index": index, "component_id": component_id, "component_type": ctype, "status": status, "input": resolved_input, "output": output})
                if manifest.get("failure_policy") != "CONTINUE_WITH_FAILURE_OBJECT":
                    raise
            values[component_id] = output
            traces.append({"index": index, "component_id": component_id, "component_type": ctype, "status": status, "input": resolved_input, "output": output})
        outputs = {name: self._resolve_value(ref, values) for name, ref in dict(manifest.get("outputs", {"result": manifest["execution_order"][-1]})).items()}
        post = self.db.database_root()
        deterministic_payload = {
            "lvm_id": lvm_id,
            "inputs": self._deterministic_projection(dict(inputs or {})),
            "outputs": self._deterministic_projection(outputs),
            "trace": self._deterministic_projection(traces),
            "depth": _depth,
            "status": "LVM_EXECUTION_COMPLETED",
        }
        execution_hash = hash72("hhs_pass145_lvm_execution_v1", deterministic_payload)
        execution_id = stable_id("EXE", "hhs_pass145_lvm_execution_id_v1", {**deterministic_payload, "pre_state_root_hash72": pre, "post_state_root_hash72": post, "occurrence": int(self.db.meta("transaction_sequence") or 0) + 1})

        def apply(conn):
            conn.execute("INSERT INTO executions(execution_id,execution_type,target_id,input_json,output_json,status,pre_state_root_hash72,post_state_root_hash72,execution_hash72,receipt_id,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)", (execution_id, "LVM", lvm_id, canonical_json(dict(inputs or {})), canonical_json({"outputs": outputs, "trace": traces}), "LVM_EXECUTION_COMPLETED", pre, post, execution_hash, None, utc_now()))
            return {"status": "LVM_EXECUTION_COMPLETED", "execution_id": execution_id, "execution_hash72": execution_hash, "outputs": outputs, "trace": traces}

        return self.db.mutate("LVM_EXECUTE_RECORD", {"lvm_id": lvm_id, "execution_hash72": execution_hash}, apply, receipt_type="LVM_EXECUTION_RECEIPT")

    @staticmethod
    def _resolve_value(value: Any, values: Mapping[str, Any]) -> Any:
        if isinstance(value, str) and value.startswith("$"):
            ref = value[1:]
            if ref == "input":
                return values["$input"]
            if "." in ref:
                root, path = ref.split(".", 1)
                current = values[root]
                for part in path.split("."):
                    current = current[int(part)] if isinstance(current, list) else current[part]
                return current
            return values[ref]
        if isinstance(value, list):
            return [LVMEngine._resolve_value(v, values) for v in value]
        if isinstance(value, dict):
            return {k: LVMEngine._resolve_value(v, values) for k, v in value.items()}
        return value

    def replay(self, execution_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM executions WHERE execution_id=? AND execution_type='LVM'", (execution_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "LVM execution not found", "LVM_REPLAY", execution_id)
        original = dict(row)
        rerun = self.execute(original["target_id"], json.loads(original["input_json"]))
        reproduced = rerun["result"]["execution_hash72"] == original["execution_hash72"]
        return {"schema": "HHS_PASS145_LVM_REPLAY_V1", "status": "REPLAY_VALIDATED" if reproduced else "REPLAY_MISMATCH", "original_execution_id": execution_id, "replay_execution_id": rerun["result"]["execution_id"], "execution_hash_equal": reproduced}

class WorkspaceManager:
    def __init__(self, service: HHS145Service):
        self.service = service
        self.db = service.db

    def create(self, name: str, *, description: str = "", owner_authority: str = "LOCAL_OWNER", default_policy: Mapping[str, Any] | None = None, active_environment_id: str | None = None, dependencies: Sequence[str] = (), tags: Sequence[str] = ()) -> dict[str, Any]:
        identity = {
            "name": name,
            "description": description,
            "owner_authority": owner_authority,
            "default_policy": {"mutation": "EXPLICIT", "export": "ALLOWED", "secrets": "REFERENCE_ONLY", **dict(default_policy or {})},
            "active_environment_id": active_environment_id,
            "dependencies": sorted(set(dependencies)),
            "tags": sorted(set(tags)),
        }
        workspace_id = stable_id("WSP", "hhs_pass145_workspace_id_v1", identity)
        workspace_hash = hash72("hhs_pass145_workspace_v1", identity)

        def apply(conn):
            if active_environment_id and not conn.execute("SELECT 1 FROM environments WHERE environment_id=?", (active_environment_id,)).fetchone():
                raise Pass145Error("PROVENANCE_INCOMPLETE", "active environment not found", "WORKSPACE_CREATE", active_environment_id)
            now = utc_now()
            conn.execute(
                "INSERT INTO workspaces(workspace_id,name,description,version,owner_authority,default_policy_json,active_environment_id,dependencies_json,tags_json,workspace_hash72,root_receipt,created_at,modified_at) VALUES(?,?,?,1,?,?,?,?,?,?,?,?,?)",
                (workspace_id, name, description, owner_authority, canonical_json(identity["default_policy"]), active_environment_id, canonical_json(identity["dependencies"]), canonical_json(identity["tags"]), workspace_hash, None, now, now),
            )
            return {"status": "WORKSPACE_CREATED", "workspace_id": workspace_id, "workspace_hash72": workspace_hash}

        return self.db.mutate("WORKSPACE_CREATE", identity, apply, receipt_type="WORKSPACE_RECEIPT")

    def inspect(self, workspace_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM workspaces WHERE workspace_id=?", (workspace_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "workspace not found", "WORKSPACE_INSPECT", workspace_id)
        out = dict(row)
        for field in ("default_policy_json", "dependencies_json", "tags_json"):
            out[field.removesuffix("_json")] = json.loads(out.pop(field))
        out["members"] = [dict(r) for r in self.db.conn.execute("SELECT member_type,member_id,member_hash72 FROM workspace_members WHERE workspace_id=? ORDER BY member_type,member_id", (workspace_id,))]
        return out

    def list(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.conn.execute("SELECT workspace_id,name,description,version,owner_authority,active_environment_id,workspace_hash72 FROM workspaces ORDER BY name,workspace_id")]

    def add_member(self, workspace_id: str, member_type: str, member_id: str) -> dict[str, Any]:
        self.inspect(workspace_id)
        member_type = member_type.upper()
        if member_type not in {"PROJECT", "ENVIRONMENT", "SCRIPT", "SCHEMA", "DATASET", "DOCUMENT", "API_COLLECTION", "LVM", "RECEIPT", "EXPORT", "DEPLOYMENT_PROFILE", "AUDIT_POLICY"}:
            raise Pass145Error("COMPOSITION_REJECTED", f"unsupported workspace member type: {member_type}", "WORKSPACE_MEMBER")
        payload = {"workspace_id": workspace_id, "member_type": member_type, "member_id": member_id}
        member_hash = hash72("hhs_pass145_workspace_member_v1", payload)

        def apply(conn):
            conn.execute("INSERT OR IGNORE INTO workspace_members(workspace_id,member_type,member_id,member_hash72) VALUES(?,?,?,?)", (workspace_id, member_type, member_id, member_hash))
            conn.execute("UPDATE workspaces SET version=version+1,modified_at=? WHERE workspace_id=?", (utc_now(), workspace_id))
            return {"status": "WORKSPACE_MEMBER_ADDED", **payload, "member_hash72": member_hash}

        return self.db.mutate("WORKSPACE_MEMBER_ADD", payload, apply, receipt_type="WORKSPACE_RECEIPT")

    def activate_environment(self, workspace_id: str, environment_id: str) -> dict[str, Any]:
        self.inspect(workspace_id)
        if not self.db.conn.execute("SELECT 1 FROM environments WHERE environment_id=?", (environment_id,)).fetchone():
            raise Pass145Error("PROVENANCE_INCOMPLETE", "environment not found", "WORKSPACE_ACTIVATE", environment_id)

        def apply(conn):
            conn.execute("UPDATE workspaces SET active_environment_id=?,version=version+1,modified_at=? WHERE workspace_id=?", (environment_id, utc_now(), workspace_id))
            return {"status": "WORKSPACE_ENVIRONMENT_ACTIVATED", "workspace_id": workspace_id, "environment_id": environment_id}

        return self.db.mutate("WORKSPACE_ACTIVATE_ENVIRONMENT", {"workspace_id": workspace_id, "environment_id": environment_id}, apply, receipt_type="WORKSPACE_RECEIPT")

    def export(self, workspace_id: str, path: str | Path) -> dict[str, Any]:
        workspace = self.inspect(workspace_id)
        package = {"schema": "HHS_PASS145_WORKSPACE_PACKAGE_V1", "workspace": {k: v for k, v in workspace.items() if k not in {"created_at", "modified_at"}}}
        package["package_hash72"] = hash72("hhs_pass145_workspace_package_v1", package)
        p = Path(path).expanduser().resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(canonical_json(package) + "\n", encoding="utf-8")
        return {"status": "WORKSPACE_EXPORTED", "path": str(p), "package_hash72": package["package_hash72"], "sha256": sha256_bytes(p.read_bytes())}


class APIWorkbench:
    def __init__(self, service: HHS145Service):
        self.service = service
        self.db = service.db

    def create_collection(self, name: str, collection: Mapping[str, Any], *, environment_id: str | None = None) -> dict[str, Any]:
        requests = list(collection.get("requests", []))
        if not requests or len(requests) > 4096:
            raise Pass145Error("INGESTION_REJECTED", "API collection requires 1..4096 requests", "API_COLLECTION")
        for request in requests:
            if str(request.get("method", "GET")).upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"}:
                raise Pass145Error("INGESTION_REJECTED", "unsupported API method", "API_COLLECTION")
            if not request.get("url"):
                raise Pass145Error("INGESTION_REJECTED", "API request URL required", "API_COLLECTION")
        payload = {"schema": "HHS_PASS145_API_COLLECTION_V1", "name": name, "environment_id": environment_id, "variables": dict(collection.get("variables", {})), "requests": requests, "tests": list(collection.get("tests", [])), "capabilities": sorted(set(collection.get("capabilities", ["LOCAL_API"])))}
        collection_hash = hash72("hhs_pass145_api_collection_v1", payload)
        collection_id = stable_id("API", "hhs_pass145_api_collection_id_v1", payload)

        def apply(conn):
            conn.execute("INSERT INTO api_collections(collection_id,environment_id,name,collection_json,collection_hash72,created_at) VALUES(?,?,?,?,?,?)", (collection_id, environment_id, name, canonical_json(payload), collection_hash, utc_now()))
            return {"status": "API_COLLECTION_CREATED", "collection_id": collection_id, "collection_hash72": collection_hash}

        return self.db.mutate("API_COLLECTION_CREATE", {"collection_hash72": collection_hash}, apply, receipt_type="API_COLLECTION_RECEIPT")

    def get(self, collection_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM api_collections WHERE collection_id=?", (collection_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "API collection not found", "API_COLLECTION", collection_id)
        out = dict(row)
        out["collection"] = json.loads(out.pop("collection_json"))
        return out

    @staticmethod
    def _substitute(value: Any, variables: Mapping[str, str]) -> Any:
        if isinstance(value, str):
            return re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", lambda m: variables.get(m.group(1), m.group(0)), value)
        if isinstance(value, list):
            return [APIWorkbench._substitute(x, variables) for x in value]
        if isinstance(value, dict):
            return {k: APIWorkbench._substitute(v, variables) for k, v in value.items()}
        return value

    def execute(self, collection_id: str, request_name: str, *, variables: Mapping[str, str] | None = None, secrets: Mapping[str, str] | None = None, allow_remote: bool = False, timeout_seconds: int = 15, max_response_bytes: int = 4 * 1024 * 1024) -> dict[str, Any]:
        import urllib.error
        import urllib.parse
        import urllib.request

        collection = self.get(collection_id)["collection"]
        request = next((r for r in collection["requests"] if r.get("name") == request_name), None)
        if not request:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "API request not found", "API_EXECUTION", request_name)
        combined = {**{str(k): str(v) for k, v in collection.get("variables", {}).items()}, **dict(variables or {}), **dict(secrets or {})}
        resolved = self._substitute(request, combined)
        parsed = urllib.parse.urlparse(resolved["url"])
        loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
        if parsed.scheme not in {"http", "https"}:
            raise Pass145Error("DISCLOSURE_PATH_INVALID", "API scheme rejected", "API_EXECUTION")
        if not loopback and (not allow_remote or "NETWORK" not in collection.get("capabilities", [])):
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "remote API capability not admitted", "API_EXECUTION")
        body = resolved.get("body")
        data = None if body is None else (body if isinstance(body, str) else canonical_json(body)).encode("utf-8")
        headers = {str(k): str(v) for k, v in dict(resolved.get("headers", {})).items()}
        req = urllib.request.Request(resolved["url"], data=data, headers=headers, method=str(resolved.get("method", "GET")).upper())
        try:
            with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
                raw = response.read(max_response_bytes + 1)
                if len(raw) > max_response_bytes:
                    raise Pass145Error("RESOURCE_BOUNDED", "API response bound reached", "API_EXECUTION")
                result = {"status": response.status, "headers": dict(response.headers.items()), "body_text": raw.decode("utf-8", errors="replace"), "elapsed_class": "BOUNDED"}
        except urllib.error.HTTPError as exc:
            raw = exc.read(max_response_bytes + 1)
            result = {"status": exc.code, "headers": dict(exc.headers.items()), "body_text": raw.decode("utf-8", errors="replace"), "http_error": True}
        result_payload = {"collection_id": collection_id, "request_name": request_name, "request": {k: v for k, v in resolved.items() if k not in {"headers"}}, "response": result, "secret_values_persisted": False}
        result_payload["execution_hash72"] = hash72("hhs_pass145_api_execution_v1", result_payload)
        return result_payload

    def generate_client(self, collection_id: str, request_name: str, *, language: str = "HHS_COMMAND") -> dict[str, Any]:
        collection = self.get(collection_id)["collection"]
        request = next((r for r in collection["requests"] if r.get("name") == request_name), None)
        if not request:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "API request not found", "API_GENERATE", request_name)
        language = language.upper()
        method = str(request.get("method", "GET")).upper()
        url = str(request["url"])
        headers = dict(request.get("headers", {}))
        body = request.get("body")
        if language == "PYTHON":
            code = "import json, urllib.request\n"
            code += f"url = {url!r}\nheaders = {headers!r}\n"
            code += f"body = {body!r}\ndata = None if body is None else json.dumps(body).encode('utf-8')\n"
            code += f"request = urllib.request.Request(url, data=data, headers=headers, method={method!r})\n"
            code += "with urllib.request.urlopen(request, timeout=15) as response:\n    print(response.read().decode('utf-8'))\n"
        elif language == "JAVASCRIPT":
            code = f"const response = await fetch({json.dumps(url)}, {{method:{json.dumps(method)}, headers:{json.dumps(headers)}, body:{'undefined' if body is None else 'JSON.stringify('+json.dumps(body)+')'}}});\nconsole.log(await response.text());\n"
        elif language == "HHS_COMMAND":
            code = canonical_json({"schema": "HHS_API_REQUEST_COMMAND_V1", "method": method, "url": url, "headers": headers, "body": body, "timeout_seconds": 15, "validate_response": True})
        else:
            raise Pass145Error("INGESTION_REJECTED", "unsupported generated client language", "API_GENERATE")
        return {"schema": "HHS_PASS145_GENERATED_CLIENT_V1", "language": language, "source": code, "source_hash72": hash72("hhs_pass145_generated_client_v1", code), "secrets_embedded": False}


class ExtensionManager:
    REQUIRED = {"identity", "version", "publisher", "source_hash", "requested_capabilities", "supported_runtime_versions", "entrypoints", "schemas", "migrations", "tests", "uninstall_behavior"}

    def __init__(self, service: HHS145Service):
        self.service = service
        self.db = service.db

    def install(self, manifest: Mapping[str, Any]) -> dict[str, Any]:
        missing = sorted(self.REQUIRED - set(manifest))
        if missing:
            raise Pass145Error("INGESTION_REJECTED", f"extension manifest missing fields: {missing}", "EXTENSION_INSTALL")
        caps = set(str(c).upper() for c in manifest.get("requested_capabilities", []))
        unknown = sorted(caps - (CAPABILITIES | {"LOCAL_API"}))
        if unknown:
            raise Pass145Error("CAPABILITY_OVERBROAD", f"extension capabilities unsupported: {unknown}", "EXTENSION_INSTALL")
        if manifest.get("direct_canonical_database_access"):
            raise Pass145Error("CAPABILITY_OVERBROAD", "extensions may not mutate canonical storage directly", "EXTENSION_INSTALL")
        payload = {**dict(manifest), "requested_capabilities": sorted(caps), "least_privilege": True, "direct_canonical_database_access": False}
        manifest_hash = hash72("hhs_pass145_extension_manifest_v1", payload)
        extension_id = stable_id("EXT", "hhs_pass145_extension_id_v1", {"identity": payload["identity"], "version": payload["version"], "manifest_hash72": manifest_hash})

        def apply(conn):
            conn.execute("INSERT INTO extensions(extension_id,manifest_json,manifest_hash72,admitted,created_at) VALUES(?,?,?,?,?)", (extension_id, canonical_json(payload), manifest_hash, 1, utc_now()))
            return {"status": "EXTENSION_ADMITTED", "extension_id": extension_id, "manifest_hash72": manifest_hash}

        return self.db.mutate("EXTENSION_INSTALL", {"manifest_hash72": manifest_hash}, apply, receipt_type="EXTENSION_RECEIPT")

    def inspect(self, extension_id: str) -> dict[str, Any]:
        row = self.db.conn.execute("SELECT * FROM extensions WHERE extension_id=?", (extension_id,)).fetchone()
        if not row:
            raise Pass145Error("PROVENANCE_INCOMPLETE", "extension not found", "EXTENSION", extension_id)
        out = dict(row)
        out["manifest"] = json.loads(out.pop("manifest_json"))
        return out

    def list(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self.db.conn.execute("SELECT extension_id,manifest_hash72,admitted,created_at FROM extensions ORDER BY extension_id")]

    def uninstall(self, extension_id: str, *, authority: str) -> dict[str, Any]:
        ext = self.inspect(extension_id)
        if authority != "EXPLICIT_EXTENSION_UNINSTALL":
            raise Pass145Error("AUTHORITY_INSUFFICIENT", "explicit extension uninstall authority required", "EXTENSION_UNINSTALL", extension_id)

        def apply(conn):
            conn.execute("UPDATE extensions SET admitted=0 WHERE extension_id=?", (extension_id,))
            return {"status": "EXTENSION_UNINSTALLED_LOGICALLY", "extension_id": extension_id, "manifest_preserved": True, "uninstall_behavior": ext["manifest"]["uninstall_behavior"]}

        return self.db.mutate("EXTENSION_UNINSTALL", {"extension_id": extension_id, "authority": authority}, apply, receipt_type="EXTENSION_RECEIPT")
