from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146 import cli as authority_cli
from hhs_runtime.pass147 import cli as parent_cli
from .api import serve
from .service import HHS148Service


def default_db_path() -> Path:
    return Path(os.environ.get("HHS_DB_PATH", "~/.hhs/pass148/system.sqlite3")).expanduser()


def _render(value: Any, fmt: str) -> str:
    if fmt == "json": return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str)
    if fmt == "jsonl": return canonical_json(value)
    if fmt == "markdown": return "```json\n" + json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n```"
    if isinstance(value, dict): return "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v}" for k, v in value.items())
    return str(value)


def _json_object(value: str | None) -> dict[str, Any]:
    if not value: return {}
    if value.startswith("@"): value = Path(value[1:]).read_text(encoding="utf-8")
    parsed = json.loads(value)
    if not isinstance(parsed, dict): raise Pass145Error("SEMANTIC_INPUT_INVALID", "expected a JSON object", "SEMANTIC_CLI")
    return parsed


def _json_list(value: str | None) -> list[Any]:
    if not value: return []
    if value.startswith("@"): value = Path(value[1:]).read_text(encoding="utf-8")
    parsed = json.loads(value)
    if not isinstance(parsed, list): raise Pass145Error("SEMANTIC_INPUT_INVALID", "expected a JSON list", "SEMANTIC_CLI")
    return parsed


def _expression(args: argparse.Namespace) -> str:
    if getattr(args, "expression", None) is not None: return str(args.expression)
    if getattr(args, "expression_file", None): return Path(args.expression_file).read_text(encoding="utf-8")
    if getattr(args, "stdin", False): return sys.stdin.read()
    raise Pass145Error("SEMANTIC_SOURCE_INVALID", "provide --expression, --expression-file, or --stdin", "SEMANTIC_CLI")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hhs", description="HHS Pass 148 Native Semantic Authority Membrane")
    p.add_argument("--db", default=str(default_db_path()))
    p.add_argument("--format", choices=["json", "jsonl", "text", "markdown"], default="json")
    sub = p.add_subparsers(dest="command", required=True)
    for core in ("status", "version", "doctor", "capabilities"): sub.add_parser(core)
    semantic = sub.add_parser("semantic", help="native semantic authority membrane")
    ss = semantic.add_subparsers(dest="semantic_command", required=True)

    analyze = ss.add_parser("analyze")
    analyze.add_argument("--expression")
    analyze.add_argument("--expression-file")
    analyze.add_argument("--stdin", action="store_true")
    analyze.add_argument("--source-type", default="model_output", choices=["contract", "runtime", "documentation", "user_declaration", "model_output", "fiction", "control_engine"])
    analyze.add_argument("--source-reference", default="CLI_SUBMISSION")
    analyze.add_argument("--profile", default="HHS_NATIVE_TYPED_V1")
    analyze.add_argument("--scope", default="{}", help="JSON object or @path")
    analyze.add_argument("--governing-contract", action="append", default=[])

    doc = ss.add_parser("analyze-document")
    doc.add_argument("path")
    doc.add_argument("--source-type", default="documentation", choices=["contract", "runtime", "documentation", "user_declaration", "model_output", "fiction", "control_engine"])
    doc.add_argument("--source-reference")
    doc.add_argument("--profile", default="HHS_NATIVE_TYPED_V1")
    doc.add_argument("--governing-contract", action="append", default=[])

    derive = ss.add_parser("derive")
    derive.add_argument("--proposition", action="append", required=True)
    derive.add_argument("--rule", default="HHS_DELTA_SELF_NORMALIZATION_SUBSTITUTION_V1")
    derive.add_argument("--substitutions", default="{}", help="JSON object or @path")

    project = ss.add_parser("project")
    project.add_argument("--expression")
    project.add_argument("--expression-file")
    project.add_argument("--stdin", action="store_true")
    project.add_argument("--profile", required=True)
    project.add_argument("--assumption", action="append", default=[])

    classify = ss.add_parser("classify"); classify.add_argument("--proposition", required=True)
    show_prop = ss.add_parser("proposition"); show_prop.add_argument("proposition_id")
    show_drv = ss.add_parser("derivation"); show_drv.add_argument("derivation_id")

    promotion = ss.add_parser("promotion-request")
    promotion.add_argument("--source", required=True)
    promotion.add_argument("--target", required=True)
    promotion.add_argument("--governing-rule", required=True)
    promotion.add_argument("--dependency", action="append", default=[])
    promotion.add_argument("--scope", default="{}")

    evaluate = ss.add_parser("promotion-evaluate")
    evaluate.add_argument("promotion_request_id")
    group = evaluate.add_mutually_exclusive_group(required=True); group.add_argument("--authorize", action="store_true"); group.add_argument("--reject", action="store_true")
    evaluate.add_argument("--authority", choices=["A3", "A4"], default="A3")
    evaluate.add_argument("--rationale", required=True)

    rule = ss.add_parser("rule"); rs = rule.add_subparsers(dest="rule_command", required=True); show = rs.add_parser("show"); show.add_argument("rule_id")
    replay = ss.add_parser("replay"); replay.add_argument("target_id")
    audit = ss.add_parser("audit"); audit.add_argument("--dependency-scope", default="pass148")
    registry = ss.add_parser("registry"); rgs = registry.add_subparsers(dest="registry_command", required=True); rgs.add_parser("sync"); rgs.add_parser("audit")
    server = ss.add_parser("serve"); server.add_argument("--host", default="127.0.0.1"); server.add_argument("--port", type=int, default=8878); server.add_argument("--token")
    return p


def semantic_operation(args: argparse.Namespace) -> tuple[str, dict[str, Any]]:
    cmd = args.semantic_command
    if cmd == "analyze":
        return "SEMANTIC_ANALYZE", {"expression": _expression(args), "source_type": args.source_type, "source_reference": args.source_reference, "profile_id": args.profile, "declared_scope": _json_object(args.scope), "governing_contracts": list(args.governing_contract)}
    if cmd == "analyze-document":
        path = Path(args.path); return "SEMANTIC_DOCUMENT_ANALYZE", {"text": path.read_text(encoding="utf-8"), "name": path.name, "source_type": args.source_type, "source_reference": args.source_reference or str(path.resolve()), "profile_id": args.profile, "governing_contracts": list(args.governing_contract)}
    if cmd == "derive": return "SEMANTIC_DERIVE", {"proposition_ids": list(args.proposition), "rule_id": args.rule, "substitutions": _json_object(args.substitutions)}
    if cmd == "project": return "SEMANTIC_PROJECT", {"expression": _expression(args), "profile_id": args.profile, "assumptions": list(args.assumption)}
    if cmd in {"classify", "proposition"}: return "SEMANTIC_RETRIEVE", {"kind": "proposition", "target_id": args.proposition if cmd == "classify" else args.proposition_id}
    if cmd == "derivation": return "SEMANTIC_RETRIEVE", {"kind": "derivation", "target_id": args.derivation_id}
    if cmd == "promotion-request": return "SEMANTIC_PROMOTION_REQUEST", {"proposition_id": args.source, "target_class": args.target, "governing_rule": args.governing_rule, "dependency_set": list(args.dependency), "scope": _json_object(args.scope)}
    if cmd == "promotion-evaluate": return "SEMANTIC_PROMOTION_EVALUATE", {"promotion_request_id": args.promotion_request_id, "authorize": bool(args.authorize), "authority_level": args.authority, "rationale": args.rationale}
    if cmd == "rule": return "SEMANTIC_RULE_READ", {"rule_id": args.rule_id}
    if cmd == "replay": return "SEMANTIC_REPLAY", {"target_id": args.target_id}
    if cmd == "audit": return "SEMANTIC_AUDIT", {"dependency_scope": args.dependency_scope}
    if cmd == "registry": return ("SEMANTIC_REGISTRY_SYNC", {}) if args.registry_command == "sync" else ("SEMANTIC_AUDIT", {"registry_only": True})
    raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", f"unhandled semantic command: {cmd}", "SEMANTIC_CLI")


def semantic_request_from_argv(argv: list[str], *, stdin_text: str | None = None) -> tuple[str, dict[str, Any]]:
    parser = build_parser()
    supplied = list(argv)
    if supplied and supplied[0] == "semantic": supplied = supplied
    args = parser.parse_args(supplied)
    if args.command != "semantic": raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "not a semantic command", "SEMANTIC_CLI")
    if stdin_text is not None and getattr(args, "stdin", False):
        # Avoid replacing process stdin for external-agent API execution.
        args.expression = stdin_text; args.stdin = False
    return semantic_operation(args)


def _local_authority(db: str) -> tuple[str, str, str]:
    return authority_cli._ensure_device_authority(db)


def _execute(service: HHS148Service, db: str, operation: str, request: dict[str, Any]) -> Any:
    identity, grant, token = _local_authority(db)
    built = service.security.construct_path(identity, grant, token, operation, request)
    closed = service.security.execute_path(built["result"]["contract_id"], identity, token)
    return closed["result"]["result"]



def _dispatch_public(args: argparse.Namespace) -> Any:
    """Dispatch inherited Pass 147 public primitives through the Pass 148 service.

    This prevents an older public-registry service from becoming an alternate
    surface that cannot discover or boundary-wrap Pass 148 capabilities.
    """
    with HHS148Service(args.db) as service:
        if args.command in {"status", "version", "doctor", "capabilities"}:
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": args.command})
        if args.command == "surface":
            if args.surface_command == "sync":
                return _execute(service, args.db, "PUBLIC_REGISTRY_SYNC", {})
            request: dict[str, Any] = {"action": args.surface_command}
            if args.surface_command == "list":
                request.update({"filter_classification": args.classification, "surface_type": args.surface_type})
            if args.surface_command == "show":
                request = {"action": "describe", "identifier": args.capability_id}
            return _execute(service, args.db, "PUBLIC_DISCOVER", request)
        if args.command == "command":
            if not args.argv:
                raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "command argv required", "PUBLIC_COMMAND")
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "describe", "identifier": args.argv})
        if args.command == "api-contract":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "api", "path": args.path})
        if args.command == "schema":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "schema", "name": args.name})
        if args.command == "boundary":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "boundary", "target": args.target})
        if args.command == "error":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "error", "code": args.code})
        if args.command == "runtime":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "runtime_types"})
        if args.command == "examples":
            return _execute(service, args.db, "PUBLIC_DISCOVER", {"action": "examples"})
        if args.command == "docs":
            if args.docs_command == "install":
                return _execute(service, args.db, "PUBLIC_DOC_INSTALL", {})
            if args.docs_command == "query":
                return _execute(service, args.db, "PUBLIC_DOC_QUERY", {"question": args.question, "limit": args.limit})
            return service.db.source_search("", namespace="hhs-public-docs-v147", limit=200)
        if args.command == "agent":
            if args.agent_command == "bootstrap":
                issuer_identity, issuer_grant, issuer_token = _local_authority(args.db)
                return service.create_external_agent(issuer_identity, issuer_grant, issuer_token, args.name, capabilities=args.capability or None)
            if args.agent_command == "execute":
                agent_argv = list(args.argv)
                if agent_argv and agent_argv[0] == "--":
                    agent_argv = agent_argv[1:]
                return service.external_execute(args.identity, args.grant, args.token, agent_argv, stdin_text=args.stdin_text)
            rows = service.db.conn.execute(
                "SELECT profile_id,identity_id,grant_id,name,profile_hash72,active,created_at "
                "FROM external_agent_profiles ORDER BY created_at,profile_id"
            ).fetchall()
            return {"schema": "HHS_PASS148_EXTERNAL_AGENT_LIST_V1", "agents": [dict(row) for row in rows]}
        if args.command == "serve-public":
            identity, grant, token = _local_authority(args.db)
            serve(args.db, host=args.host, port=args.port, token=args.token, identity_id=identity, grant_id=grant, identity_token=token)
            return {"status": "SERVER_CLOSED"}
    raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "unhandled public command", "SEMANTIC_CLI")

def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    non_globals: list[str] = []
    skip = False
    for item in raw:
        if skip:
            skip = False
            continue
        if item in {"--db", "--format"}:
            skip = True
            continue
        non_globals.append(item)
    command = non_globals[0] if non_globals else None
    subcommand = non_globals[1] if len(non_globals) > 1 else None

    # Preserve the Pass 147 public alias while routing it through Pass 148.
    if command == "api" and subcommand == "describe":
        try:
            index = raw.index("api")
            raw[index] = "api-contract"
            command = "api-contract"
        except ValueError:
            pass
    if command == "receipt" and subcommand == "inspect":
        try:
            raw[raw.index("inspect")] = "show"
        except ValueError:
            pass
        return parent_cli.main(raw)

    public_commands = {
        "status", "version", "doctor", "capabilities", "surface", "command",
        "api-contract", "schema", "boundary", "error", "runtime", "examples",
        "docs", "agent", "serve-public",
    }
    if command in public_commands:
        try:
            args = parent_cli.build_parser().parse_args(raw)
            result = _dispatch_public(args)
            print(_render(result, args.format))
            return 0
        except Pass145Error as exc:
            fmt = "json"
            try:
                fmt = raw[raw.index("--format") + 1]
            except Exception:
                pass
            print(_render(exc.to_dict(), fmt), file=sys.stderr)
            return 2
        except KeyboardInterrupt:
            print(canonical_json({"ok": False, "error_code": "INTERRUPTED_EXECUTION"}), file=sys.stderr)
            return 130
        except Exception as exc:
            error = Pass145Error("SEMANTIC_CLI_INTERNAL_ERROR", str(exc), "SEMANTIC_CLI")
            print(_render(error.to_dict(), "json"), file=sys.stderr)
            return 3

    if command != "semantic":
        return parent_cli.main(raw)

    parser = build_parser()
    try:
        args = parser.parse_args(raw)
        with HHS148Service(args.db) as service:
            if args.semantic_command == "serve":
                identity, grant, token = _local_authority(args.db)
                serve(args.db, host=args.host, port=args.port, token=args.token, identity_id=identity, grant_id=grant, identity_token=token)
                return 0
            operation, request = semantic_operation(args)
            result = _execute(service, args.db, operation, request)
        print(_render(result, args.format))
        return 0 if not (
            isinstance(result, dict)
            and (result.get("ok") is False or str(result.get("status", "")).endswith(("FAILED", "REJECTED", "MISMATCH")))
        ) else 1
    except Pass145Error as exc:
        fmt = "json"
        try:
            fmt = raw[raw.index("--format") + 1]
        except Exception:
            pass
        print(_render(exc.to_dict(), fmt), file=sys.stderr)
        return 2
    except SystemExit as exc:
        return int(exc.code)
    except Exception as exc:
        error = Pass145Error("SEMANTIC_CLI_INTERNAL_ERROR", str(exc), "SEMANTIC_CLI")
        print(_render(error.to_dict(), "json"), file=sys.stderr)
        return 3


if __name__ == "__main__": raise SystemExit(main())
