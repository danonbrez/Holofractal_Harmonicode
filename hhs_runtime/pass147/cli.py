from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass146 import cli as parent_cli
from .api import serve
from .service import HHS147Service


def default_db_path() -> Path:
    return Path(os.environ.get("HHS_DB_PATH", "~/.hhs/pass147/system.sqlite3")).expanduser()


def _render(value: Any, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str)
    if fmt == "jsonl":
        return canonical_json(value)
    if fmt == "markdown":
        return "```json\n" + json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n```"
    if isinstance(value, dict):
        return "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v}" for k, v in value.items())
    return str(value)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hhs", description="HHS Pass 147 functionally complete procedurally external public environment")
    p.add_argument("--db", default=str(default_db_path()))
    p.add_argument("--format", choices=["json", "jsonl", "text", "markdown"], default="json")
    sub = p.add_subparsers(dest="command", required=True)
    for core in ("status", "version", "doctor", "capabilities"):
        sub.add_parser(core)

    surface = sub.add_parser("surface", help="inspect the canonical public capability registry")
    ss = surface.add_subparsers(dest="surface_command", required=True)
    sl = ss.add_parser("list"); sl.add_argument("--classification"); sl.add_argument("--type", dest="surface_type")
    sd = ss.add_parser("show"); sd.add_argument("capability_id")
    ss.add_parser("graph"); ss.add_parser("audit"); ss.add_parser("sync")

    command = sub.add_parser("command", help="inspect a public CLI contract")
    cs = command.add_subparsers(dest="command_command", required=True)
    cd = cs.add_parser("describe"); cd.add_argument("argv", nargs=argparse.REMAINDER)

    api = sub.add_parser("api-contract", help="inspect public API contracts")
    aps = api.add_subparsers(dest="api_contract_command", required=True)
    ad = aps.add_parser("describe"); ad.add_argument("path", nargs="?")

    schema = sub.add_parser("schema", help="inspect public schemas")
    schs = schema.add_subparsers(dest="schema_command", required=True)
    shi = schs.add_parser("inspect"); shi.add_argument("name", nargs="?")

    boundary = sub.add_parser("boundary", help="explain a boundary operation or admitted contract")
    bs = boundary.add_subparsers(dest="boundary_command", required=True)
    be = bs.add_parser("explain"); be.add_argument("target")

    error = sub.add_parser("error", help="explain stable errors")
    es = error.add_subparsers(dest="error_command", required=True)
    ee = es.add_parser("explain"); ee.add_argument("code")

    runtime = sub.add_parser("runtime", help="inspect canonical public runtime types")
    rs = runtime.add_subparsers(dest="runtime_command", required=True); rs.add_parser("types")
    sub.add_parser("examples")

    docs = sub.add_parser("docs", help="manage and query the local public documentation corpus")
    ds = docs.add_subparsers(dest="docs_command", required=True)
    ds.add_parser("install")
    dq = ds.add_parser("query"); dq.add_argument("question"); dq.add_argument("--limit", type=int, default=50)
    ds.add_parser("list")

    agent = sub.add_parser("agent", help="create and operate a procedurally external agent")
    ags = agent.add_subparsers(dest="agent_command", required=True)
    ab = ags.add_parser("bootstrap"); ab.add_argument("name"); ab.add_argument("--capability", action="append", default=[])
    ae = ags.add_parser("execute"); ae.add_argument("--identity", required=True); ae.add_argument("--grant", required=True); ae.add_argument("--token", required=True); ae.add_argument("--stdin-text"); ae.add_argument("argv", nargs=argparse.REMAINDER)
    ags.add_parser("list")

    sp = sub.add_parser("serve-public"); sp.add_argument("--host", default="127.0.0.1"); sp.add_argument("--port", type=int, default=8877); sp.add_argument("--token")
    return p


def _local_authority(db: str) -> tuple[str, str, str]:
    return parent_cli._ensure_device_authority(db)


def _public_operation(service: HHS147Service, db: str, operation: str, request: dict[str, Any]) -> Any:
    identity, grant, token = _local_authority(db)
    built = service.security.construct_path(identity, grant, token, operation, request)
    closed = service.security.execute_path(built["result"]["contract_id"], identity, token)
    return closed["result"]["result"]


def _dispatch(args: argparse.Namespace) -> Any:
    with HHS147Service(args.db) as service:
        if args.command in {"status", "version", "doctor", "capabilities"}:
            return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": args.command})
        if args.command == "surface":
            if args.surface_command == "sync": return _public_operation(service, args.db, "PUBLIC_REGISTRY_SYNC", {})
            request = {"action": args.surface_command}
            if args.surface_command == "list": request.update({"filter_classification": args.classification, "surface_type": args.surface_type})
            if args.surface_command == "show": request = {"action": "describe", "identifier": args.capability_id}
            return _public_operation(service, args.db, "PUBLIC_DISCOVER", request)
        if args.command == "command":
            if not args.argv: raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "command argv required", "PUBLIC_COMMAND")
            return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "describe", "identifier": args.argv})
        if args.command == "api-contract": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "api", "path": args.path})
        if args.command == "schema": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "schema", "name": args.name})
        if args.command == "boundary": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "boundary", "target": args.target})
        if args.command == "error": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "error", "code": args.code})
        if args.command == "runtime": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "runtime_types"})
        if args.command == "examples": return _public_operation(service, args.db, "PUBLIC_DISCOVER", {"action": "examples"})
        if args.command == "docs":
            if args.docs_command == "install": return _public_operation(service, args.db, "PUBLIC_DOC_INSTALL", {})
            if args.docs_command == "query": return _public_operation(service, args.db, "PUBLIC_DOC_QUERY", {"question": args.question, "limit": args.limit})
            return service.db.source_search("", namespace="hhs-public-docs-v147", limit=200)
        if args.command == "agent":
            if args.agent_command == "bootstrap":
                issuer_identity, issuer_grant, issuer_token = _local_authority(args.db)
                return service.create_external_agent(issuer_identity, issuer_grant, issuer_token, args.name, capabilities=args.capability or None)
            if args.agent_command == "execute":
                argv = list(args.argv)
                if argv and argv[0] == "--": argv = argv[1:]
                return service.external_execute(args.identity, args.grant, args.token, argv, stdin_text=args.stdin_text)
            rows = service.db.conn.execute("SELECT profile_id,identity_id,grant_id,name,profile_hash72,active,created_at FROM external_agent_profiles ORDER BY created_at,profile_id").fetchall()
            return {"schema": "HHS_PASS147_EXTERNAL_AGENT_LIST_V1", "agents": [dict(r) for r in rows]}
        if args.command == "serve-public":
            identity, grant, token = _local_authority(args.db)
            serve(args.db, host=args.host, port=args.port, token=args.token, identity_id=identity, grant_id=grant, identity_token=token)
            return {"status": "SERVER_CLOSED"}
    raise Pass145Error("PUBLIC_PRIMITIVE_MISSING", "unhandled Pass 147 command", "CLI")


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    public_commands = {"status", "version", "doctor", "capabilities", "surface", "command", "api-contract", "schema", "boundary", "error", "runtime", "examples", "docs", "agent", "serve-public"}
    cleaned = [x for x in raw if x not in []]
    non_globals = []
    skip = False
    for x in raw:
        if skip: skip = False; continue
        if x in {"--db", "--format"}: skip = True; continue
        non_globals.append(x)
    command = non_globals[0] if non_globals else None
    subcommand = non_globals[1] if len(non_globals) > 1 else None
    if command == "api" and subcommand == "describe":
        idx = raw.index("api"); raw[idx] = "api-contract"; command = "api-contract"
    elif command == "receipt" and subcommand == "inspect":
        idx = raw.index("inspect"); raw[idx] = "show"; return parent_cli.main(raw)
    if command not in public_commands:
        return parent_cli.main(raw)
    parser = build_parser()
    try:
        args = parser.parse_args(raw)
        result = _dispatch(args)
        print(_render(result, args.format))
        return 0
    except Pass145Error as exc:
        fmt = "json"
        try: fmt = raw[raw.index("--format") + 1]
        except Exception: pass
        print(_render(exc.to_dict(), fmt), file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print(canonical_json({"ok": False, "error_code": "INTERRUPTED_EXECUTION"}), file=sys.stderr); return 130
    except Exception as exc:
        print(canonical_json({"ok": False, "error_code": type(exc).__name__, "description": str(exc)}), file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())
