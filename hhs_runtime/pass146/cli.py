from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

from hhs_runtime.pass145.canonical import canonical_json
from hhs_runtime.pass145.errors import Pass145Error
from hhs_runtime.pass145 import cli as parent_cli
from .api import serve
from .service import HHS146Service


def default_db_path() -> Path:
    return Path(os.environ.get("HHS_DB_PATH", "~/.hhs/pass146/system.sqlite3")).expanduser()


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


def _security_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hhs security", description="HHS Pass 146 boundary-constructed execution security")
    sub = p.add_subparsers(dest="security_command", required=True)
    sub.add_parser("status")
    b = sub.add_parser("bootstrap-local")
    b.add_argument("--name", default="Local HHS Owner")

    ident = sub.add_parser("identity")
    isub = ident.add_subparsers(dest="identity_command", required=True)
    ic = isub.add_parser("create")
    ic.add_argument("name")
    ic.add_argument("--type", default="LOCAL_USER")
    ic.add_argument("--issuer-identity", required=True)
    ic.add_argument("--issuer-grant", required=True)
    ic.add_argument("--issuer-token", required=True)

    grant = sub.add_parser("grant")
    gsub = grant.add_subparsers(dest="grant_command", required=True)
    gc = gsub.add_parser("create")
    gc.add_argument("target_identity")
    gc.add_argument("--issuer-identity", required=True)
    gc.add_argument("--parent-grant", required=True)
    gc.add_argument("--issuer-token", required=True)
    gc.add_argument("--capability", action="append", default=[])
    gc.add_argument("--operation", action="append", default=[])
    gc.add_argument("--source", action="append", default=["*"])
    gc.add_argument("--destination", action="append", default=["LOCAL_RESULT"])
    gc.add_argument("--resource-policy", default="{}")
    gc.add_argument("--disclosure-policy", default="{}")

    path = sub.add_parser("path")
    psub = path.add_subparsers(dest="path_command", required=True)
    pc = psub.add_parser("construct")
    pc.add_argument("operation")
    pc.add_argument("request", help="JSON request object or @path")
    pc.add_argument("--identity", required=True)
    pc.add_argument("--grant", required=True)
    pc.add_argument("--token", required=True)
    pc.add_argument("--destination", default="{}")
    pc.add_argument("--parent-contract")
    pc.add_argument("--expires-after-sequences", type=int, default=32)
    pe = psub.add_parser("execute")
    pe.add_argument("contract_id")
    pe.add_argument("--identity", required=True)
    pe.add_argument("--token", required=True)
    pi = psub.add_parser("inspect")
    pi.add_argument("contract_id")
    pl = psub.add_parser("list")
    pl.add_argument("--limit", type=int, default=100)
    pr = psub.add_parser("replay")
    pr.add_argument("contract_id")

    peer = sub.add_parser("peer")
    peersub = peer.add_subparsers(dest="peer_command", required=True)
    pt = peersub.add_parser("trust")
    pt.add_argument("peer_id")
    pt.add_argument("public_key_b64")
    pt.add_argument("--issuer-identity", required=True)
    pt.add_argument("--issuer-grant", required=True)
    pt.add_argument("--issuer-token", required=True)
    pt.add_argument("--classification", action="append", default=["INTERNAL"])
    pt.add_argument("--destination", action="append", default=["*"])
    peersub.add_parser("list")
    pp = peersub.add_parser("public-identity")
    pp.add_argument("identity_id")

    msg = sub.add_parser("message")
    msub = msg.add_subparsers(dest="message_command", required=True)
    mi = msub.add_parser("inspect")
    mi.add_argument("message_id")
    mr = msub.add_parser("receive")
    mr.add_argument("message_id")
    mr.add_argument("--receiver-identity", required=True)
    mr.add_argument("--receiver-grant", required=True)
    mr.add_argument("--receiver-token", required=True)
    ma = msub.add_parser("admit")
    ma.add_argument("envelope", help="signed envelope JSON object or @path")
    ma.add_argument("--receiver-identity", required=True)
    ma.add_argument("--receiver-grant", required=True)
    ma.add_argument("--receiver-token", required=True)

    sv = sub.add_parser("serve")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8876)
    sv.add_argument("--token")
    return p


def _load_json_arg(value: str) -> dict[str, Any]:
    if value.startswith("@"):
        value = Path(value[1:]).read_text(encoding="utf-8")
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "JSON argument must be an object", "CLI")
    return parsed


def _find_global(argv: list[str], name: str, default: str) -> str:
    try:
        return argv[argv.index(name) + 1]
    except (ValueError, IndexError):
        return default


def _without_globals(argv: list[str]) -> list[str]:
    out = []
    skip = False
    for i, value in enumerate(argv):
        if skip:
            skip = False
            continue
        if value in {"--db", "--format"}:
            skip = True
            continue
        out.append(value)
    return out




def _session_path(db: str) -> Path:
    p = Path(db).expanduser().resolve()
    return p.with_name(p.name + ".pass146-session.json")

def _ensure_device_authority(db: str) -> tuple[str, str, str]:
    env_values = (os.environ.get("HHS_IDENTITY_ID"), os.environ.get("HHS_GRANT_ID"), os.environ.get("HHS_IDENTITY_TOKEN"))
    if all(env_values):
        return env_values  # type: ignore[return-value]
    session = _session_path(db)
    if session.is_file():
        data = json.loads(session.read_text(encoding="utf-8"))
        return str(data["identity_id"]), str(data["grant_id"]), str(data["token"])
    with HHS146Service(db) as service:
        count = service.security.status()["counts"]["security_identities"]
        if count:
            raise Pass145Error("IDENTITY_UNRESOLVED", "local security identity exists but no session credential is available", "CLI_BOUNDARY")
        created = service.security.bootstrap_local_owner("Local Device CLI")
    data = {"identity_id": created["result"]["identity_id"], "grant_id": created["result"]["grant_id"], "token": created["authentication_token"]}
    session.parent.mkdir(parents=True, exist_ok=True)
    session.write_text(canonical_json(data), encoding="utf-8")
    os.chmod(session, 0o600)
    return data["identity_id"], data["grant_id"], data["token"]

def _input_evidence(argv: list[str]) -> dict[str, Any]:
    files = []
    for value in argv:
        p = Path(value).expanduser()
        if p.is_file():
            raw = p.read_bytes()
            files.append({"path": str(p.resolve()), "byte_length": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    return {"files": files}

def _execute_inherited_through_boundary(argv: list[str], db: str) -> Any:
    identity, grant, token = _ensure_device_authority(db)
    request: dict[str, Any] = {"argv": argv, "classification": "INTERNAL", "input_evidence": _input_evidence(argv)}
    if len(argv) >= 2 and ((argv[0] == "ingest" and argv[1] == "stdin") or (argv[0] == "script" and argv[1] == "paste")):
        request["stdin_text"] = sys.stdin.read()
    with HHS146Service(db) as service:
        constructed = service.security.construct_path(identity, grant, token, "RUN_CLI_COMMAND", request)
        closed = service.security.execute_path(constructed["result"]["contract_id"], identity, token)
        return closed["result"]["result"]

def _delegate_parent(argv: list[str], db: str, fmt: str) -> int:
    clean = _without_globals(argv)
    return parent_cli.main(["--db", db, "--format", fmt, *clean])


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    db = _find_global(argv, "--db", str(default_db_path()))
    fmt = _find_global(argv, "--format", "json")
    clean = _without_globals(argv)
    command = clean[0] if clean else None
    try:
        if command != "security":
            if command == "serve":
                parent_args = parent_cli.build_parser().parse_args(["--db", db, "--format", fmt, *clean])
                if getattr(parent_args, "static_root", None):
                    raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "static-root serving is not exposed by the Pass 146 security API", "CLI_BOUNDARY")
                identity, grant, identity_token = _ensure_device_authority(db)
                serve(db, host=parent_args.host, port=parent_args.port, token=parent_args.token, identity_id=identity, grant_id=grant, identity_token=identity_token)
                return 0
            if command == "shell":
                print("HHS Pass 146 boundary shell. Every command is independently admitted. Enter 'exit' to close.")
                while True:
                    try:
                        line = input("hhs146> ")
                    except EOFError:
                        break
                    if line.strip() in {"exit", "quit"}:
                        break
                    if not line.strip():
                        continue
                    main(["--db", db, "--format", fmt, *shlex.split(line)])
                return 0
            result = _execute_inherited_through_boundary(clean, db)
            print(_render(result, fmt))
            if isinstance(result, dict) and (result.get("ok") is False or str(result.get("status", "")).endswith(("FAILED", "REJECTED", "MISMATCH"))):
                return 1
            return 0
        args = _security_parser().parse_args(clean[1:])
        if args.security_command == "serve":
            identity, grant, identity_token = _ensure_device_authority(db)
            serve(db, host=args.host, port=args.port, token=args.token, identity_id=identity, grant_id=grant, identity_token=identity_token)
            return 0
        with HHS146Service(db) as service:
            e = service.security
            if args.security_command == "status":
                result = e.status()
            elif args.security_command == "bootstrap-local":
                session = _session_path(db)
                if e.status()["counts"]["security_identities"]:
                    if not session.is_file():
                        raise Pass145Error("IDENTITY_UNRESOLVED", "security authority exists but the local one-time credential session is unavailable", "SECURITY_BOOTSTRAP")
                    session_data = json.loads(session.read_text(encoding="utf-8"))
                    result = {"result": {"status": "LOCAL_SECURITY_OWNER_ALREADY_BOOTSTRAPPED", "identity_id": session_data["identity_id"], "grant_id": session_data["grant_id"]}, "authentication_token_returned_once": False}
                else:
                    result = e.bootstrap_local_owner(args.name)
                    session.parent.mkdir(parents=True, exist_ok=True)
                    session.write_text(canonical_json({"identity_id": result["result"]["identity_id"], "grant_id": result["result"]["grant_id"], "token": result["authentication_token"]}), encoding="utf-8")
                    os.chmod(session, 0o600)
            elif args.security_command == "identity":
                result = e.create_identity(args.issuer_identity, args.issuer_grant, args.issuer_token, args.name, identity_type=args.type)
            elif args.security_command == "grant":
                result = e.create_grant(args.issuer_identity, args.parent_grant, args.issuer_token, args.target_identity, capabilities=args.capability, operations=args.operation, sources=args.source, destinations=args.destination, resource_policy=_load_json_arg(args.resource_policy), disclosure_policy=_load_json_arg(args.disclosure_policy))
            elif args.security_command == "path":
                if args.path_command == "construct":
                    result = e.construct_path(args.identity, args.grant, args.token, args.operation, _load_json_arg(args.request), destination=_load_json_arg(args.destination), parent_contract_id=args.parent_contract, expires_after_sequences=args.expires_after_sequences)
                elif args.path_command == "execute":
                    result = e.execute_path(args.contract_id, args.identity, args.token)
                elif args.path_command == "inspect":
                    result = e.get_contract(args.contract_id)
                elif args.path_command == "list":
                    result = e.list_contracts(args.limit)
                else:
                    result = e.replay_path(args.contract_id)
            elif args.security_command == "peer":
                if args.peer_command == "trust":
                    result = e.trust_peer(args.issuer_identity, args.issuer_grant, args.issuer_token, args.peer_id, args.public_key_b64, classifications=args.classification, destinations=args.destination)
                elif args.peer_command == "list":
                    result = e.list_trusted_peers()
                else:
                    result = e.identity_public_record(args.identity_id)
            elif args.security_command == "message":
                if args.message_command == "inspect":
                    result = e.inspect_message(args.message_id)
                elif args.message_command == "receive":
                    result = e.receive_message(args.message_id, args.receiver_identity, args.receiver_grant, args.receiver_token)
                else:
                    envelope = _load_json_arg(args.envelope)
                    source_peer = str(envelope.get("source_peer", ""))
                    destination_peer = str(envelope.get("destination_peer", ""))
                    classification = str(envelope.get("scope", {}).get("classification", "INTERNAL")).upper()
                    constructed = e.construct_path(args.receiver_identity, args.receiver_grant, args.receiver_token, "RECEIVE_PROPAGATION", {"envelope": envelope, "source_peer": source_peer, "destination_peer": destination_peer, "classification": classification}, destination={"kind": "PEER", "id": destination_peer})
                    result = e.execute_path(constructed["result"]["contract_id"], args.receiver_identity, args.receiver_token)
            else:
                raise Pass145Error("BOUNDARY_CONSTRUCTION_FAILED", "unhandled security command", "CLI")
        print(_render(result, fmt))
        if isinstance(result, dict) and (result.get("ok") is False or str(result.get("status", "")).endswith(("FAILED", "REJECTED", "MISMATCH"))):
            return 1
        return 0
    except Pass145Error as exc:
        print(_render(exc.to_dict(), fmt), file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print(canonical_json({"ok": False, "error_code": "INTERRUPTED_EXECUTION"}), file=sys.stderr)
        return 130
    except Exception as exc:
        print(canonical_json({"ok": False, "error_code": type(exc).__name__, "description": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
