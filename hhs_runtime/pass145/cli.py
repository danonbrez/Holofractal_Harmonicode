from __future__ import annotations

import argparse
import base64
import json
import os
import shlex
import sys
from pathlib import Path
from typing import Any

from .api import serve
from .canonical import canonical_json
from .database import HHS145Database
from .errors import Pass145Error
from .service import HHS145Service
from .workbench import APIWorkbench, EnvironmentManager, ExtensionManager, LVMEngine, ScriptWorkbench, WorkspaceManager

EXIT_OK = 0
EXIT_OPERATION_FAILED = 1
EXIT_USAGE = 2
EXIT_REJECTED = 3
EXIT_NOT_FOUND = 4
EXIT_INTEGRITY = 5


def default_db_path() -> Path:
    return Path(os.environ.get("HHS_DB_PATH", "~/.hhs/pass145/knowledge.sqlite3")).expanduser()


def _render(value: Any, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str)
    if fmt == "jsonl":
        if isinstance(value, list):
            return "\n".join(canonical_json(v) for v in value)
        return canonical_json(value)
    if fmt == "markdown":
        return "```json\n" + json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n```"
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            lines.append(f"{k}: {json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v}")
        return "\n".join(lines)
    return str(value)


def _print(value: Any, fmt: str) -> None:
    print(_render(value, fmt))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="hhs", description="HHS Pass 145 local Android/CLI knowledge platform")
    p.add_argument("--db", default=str(default_db_path()), help="canonical SQLite database path")
    p.add_argument("--format", choices=["json", "jsonl", "text", "markdown"], default="json")
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("status", "version", "doctor", "capabilities"):
        sub.add_parser(name)

    ing = sub.add_parser("ingest")
    ing_sub = ing.add_subparsers(dest="ingest_command", required=True)
    for name in ("file", "html", "javascript", "manifest"):
        q = ing_sub.add_parser(name)
        q.add_argument("path")
        q.add_argument("--namespace", default="default")
        q.add_argument("--mime-type")
        q.add_argument("--no-analyze", action="store_true")
    d = ing_sub.add_parser("directory")
    d.add_argument("path")
    d.add_argument("--namespace", default="default")
    d.add_argument("--recursive", action="store_true")
    d.add_argument("--no-analyze", action="store_true")
    st = ing_sub.add_parser("stdin")
    st.add_argument("--name", default="stdin.txt")
    st.add_argument("--mime-type", default="text/plain")
    st.add_argument("--namespace", default="default")
    st.add_argument("--no-analyze", action="store_true")

    source = sub.add_parser("source")
    source_sub = source.add_subparsers(dest="source_command", required=True)
    source_show = source_sub.add_parser("show")
    source_show.add_argument("source_id")
    source_show.add_argument("--raw-base64", action="store_true")
    source_export = source_sub.add_parser("export")
    source_export.add_argument("source_id")
    source_export.add_argument("path")

    object_cmd = sub.add_parser("object")
    object_sub = object_cmd.add_subparsers(dest="object_command", required=True)
    object_show = object_sub.add_parser("show")
    object_show.add_argument("object_id")

    q = sub.add_parser("query")
    q.add_argument("question")
    q.add_argument("--namespace")
    q.add_argument("--limit", type=int, default=100)
    s = sub.add_parser("search")
    s.add_argument("text")
    s.add_argument("--symbol", action="store_true")
    s.add_argument("--type", dest="object_type")
    s.add_argument("--source")
    s.add_argument("--namespace")
    s.add_argument("--limit", type=int, default=100)

    graph = sub.add_parser("graph")
    gsub = graph.add_subparsers(dest="graph_command", required=True)
    gt = gsub.add_parser("trace")
    gt.add_argument("object_id")
    gt.add_argument("--max-depth", type=int, default=16)
    gsub.add_parser("contradictions")

    analyze = sub.add_parser("analyze")
    asub = analyze.add_subparsers(dest="analyze_command", required=True)
    ac = asub.add_parser("changes")
    ac.add_argument("version_a")
    ac.add_argument("version_b")
    for name in ("contradictions", "definitions", "dependencies"):
        asub.add_parser(name)
    ar = asub.add_parser("relationships")
    ar.add_argument("object_id")

    val = sub.add_parser("validate")
    vsub = val.add_subparsers(dest="validate_command", required=True)
    vs = vsub.add_parser("source")
    vs.add_argument("source_id")
    vo = vsub.add_parser("object")
    vo.add_argument("object_id")
    vsub.add_parser("database")
    vr = vsub.add_parser("receipt")
    vr.add_argument("receipt_id", nargs="?")
    vre = vsub.add_parser("replay")
    vre.add_argument("source_id")

    protect = sub.add_parser("protect")
    psub = protect.add_subparsers(dest="protect_command", required=True)
    psub.add_parser("status")
    pq = psub.add_parser("quarantine")
    pq.add_argument("object_id")
    pr = psub.add_parser("release")
    pr.add_argument("object_id")

    replay = sub.add_parser("replay")
    rsub = replay.add_subparsers(dest="replay_command", required=True)
    ri = rsub.add_parser("ingestion")
    ri.add_argument("source_id")
    rl = rsub.add_parser("lvm")
    rl.add_argument("execution_id")

    receipt = sub.add_parser("receipt")
    rcsub = receipt.add_subparsers(dest="receipt_command", required=True)
    rs = rcsub.add_parser("show")
    rs.add_argument("receipt_id")
    rl = rcsub.add_parser("list")
    rl.add_argument("--limit", type=int, default=100)

    database = sub.add_parser("database")
    dsub = database.add_subparsers(dest="database_command", required=True)
    for name in ("status", "integrity", "compact", "migrate"):
        dsub.add_parser(name)

    backup = sub.add_parser("backup")
    bsub = backup.add_subparsers(dest="backup_command", required=True)
    bc = bsub.add_parser("create")
    bc.add_argument("path")
    bv = bsub.add_parser("verify")
    bv.add_argument("path")
    bi = bsub.add_parser("inspect")
    bi.add_argument("path")

    restore = sub.add_parser("restore")
    rsub2 = restore.add_subparsers(dest="restore_command", required=True)
    rp = rsub2.add_parser("preview")
    rp.add_argument("path")
    ra = rsub2.add_parser("apply")
    ra.add_argument("path")
    ra.add_argument("destination")
    ra.add_argument("--replace", action="store_true")

    workspace = sub.add_parser("workspace")
    wsub = workspace.add_subparsers(dest="workspace_command", required=True)
    wc = wsub.add_parser("create")
    wc.add_argument("name")
    wc.add_argument("--description", default="")
    wc.add_argument("--active-environment")
    wi = wsub.add_parser("inspect")
    wi.add_argument("workspace_id")
    wsub.add_parser("list")
    wa = wsub.add_parser("add")
    wa.add_argument("workspace_id")
    wa.add_argument("member_type")
    wa.add_argument("member_id")
    wact = wsub.add_parser("activate")
    wact.add_argument("workspace_id")
    wact.add_argument("environment_id")
    we = wsub.add_parser("export")
    we.add_argument("workspace_id")
    we.add_argument("path")

    api = sub.add_parser("api")
    apsub = api.add_subparsers(dest="api_command", required=True)
    apc = apsub.add_parser("create")
    apc.add_argument("name")
    apc.add_argument("collection")
    apc.add_argument("--environment")
    api_ins = apsub.add_parser("inspect")
    api_ins.add_argument("collection_id")
    ape = apsub.add_parser("execute")
    ape.add_argument("collection_id")
    ape.add_argument("request_name")
    ape.add_argument("--variables", default="{}")
    ape.add_argument("--secrets", default="{}")
    ape.add_argument("--allow-remote", action="store_true")
    apg = apsub.add_parser("generate")
    apg.add_argument("collection_id")
    apg.add_argument("request_name")
    apg.add_argument("--language", default="HHS_COMMAND")

    ext = sub.add_parser("extension")
    exsub = ext.add_subparsers(dest="extension_command", required=True)
    exi = exsub.add_parser("install")
    exi.add_argument("manifest")
    exs = exsub.add_parser("inspect")
    exs.add_argument("extension_id")
    exsub.add_parser("list")
    exu = exsub.add_parser("uninstall")
    exu.add_argument("extension_id")
    exu.add_argument("--authority", required=True)

    env = sub.add_parser("env")
    esub = env.add_subparsers(dest="env_command", required=True)
    ec = esub.add_parser("create")
    ec.add_argument("name")
    ec.add_argument("--namespace")
    ec.add_argument("--description", default="")
    ei = esub.add_parser("inspect")
    ei.add_argument("environment_id")
    esub.add_parser("list")
    for name in ("clone", "branch"):
        e = esub.add_parser(name)
        e.add_argument("environment_id")
        e.add_argument("new_name")
        e.add_argument("--namespace")
    ed = esub.add_parser("diff")
    ed.add_argument("left")
    ed.add_argument("right")
    em = esub.add_parser("merge")
    em.add_argument("source")
    em.add_argument("destination")
    em.add_argument("--resolutions")
    for name in ("freeze", "unfreeze", "archive"):
        e = esub.add_parser(name)
        e.add_argument("environment_id")
    ee = esub.add_parser("export")
    ee.add_argument("environment_id")
    ee.add_argument("path")
    eimp = esub.add_parser("import")
    eimp.add_argument("path")
    eimp.add_argument("--namespace")
    edel = esub.add_parser("destroy")
    edel.add_argument("environment_id")
    edel.add_argument("--authority", required=True)

    script = sub.add_parser("script")
    ssub = script.add_subparsers(dest="script_command", required=True)
    si = ssub.add_parser("import")
    si.add_argument("path")
    si.add_argument("--name")
    si.add_argument("--language", required=True)
    si.add_argument("--environment")
    si.add_argument("--capability", action="append", default=[])
    sp = ssub.add_parser("paste")
    sp.add_argument("name")
    sp.add_argument("--language", required=True)
    sp.add_argument("--environment")
    sp.add_argument("--capability", action="append", default=[])
    for name in ("validate", "run", "inspect"):
        x = ssub.add_parser(name)
        x.add_argument("script_id")
    sr = ssub.choices["run"]
    sr.add_argument("--input-json", default="{}")

    lvm = sub.add_parser("lvm")
    lsub = lvm.add_subparsers(dest="lvm_command", required=True)
    lc = lsub.add_parser("create")
    lc.add_argument("manifest")
    lc.add_argument("--environment")
    for name in ("run", "inspect"):
        x = lsub.add_parser(name)
        x.add_argument("lvm_id")
    lsub.choices["run"].add_argument("--input-json", default="{}")
    lr = lsub.add_parser("replay")
    lr.add_argument("execution_id")

    serve_p = sub.add_parser("serve")
    serve_p.add_argument("--host", default="127.0.0.1")
    serve_p.add_argument("--port", type=int, default=8765)
    serve_p.add_argument("--token")
    serve_p.add_argument("--static-root")
    sub.add_parser("shell")
    return p


def _dispatch(args: argparse.Namespace) -> Any:
    if args.command == "restore" and args.restore_command == "apply":
        return HHS145Database.restore_apply(args.path, args.destination, require_empty=not args.replace)
    if args.command == "serve":
        serve(args.db, host=args.host, port=args.port, token=args.token, static_root=args.static_root)
        return {"status": "SERVER_STOPPED"}
    with HHS145Service(args.db) as service:
        env = EnvironmentManager(service)
        scripts = ScriptWorkbench(service, env)
        lvms = LVMEngine(service, scripts, env)
        workspaces = WorkspaceManager(service)
        apis = APIWorkbench(service)
        extensions = ExtensionManager(service)
        if args.command == "status": return service.status()
        if args.command == "version": return service.version()
        if args.command == "doctor": return service.doctor()
        if args.command == "capabilities": return service.capabilities()
        if args.command == "ingest":
            if args.ingest_command in {"file", "html", "javascript", "manifest"}:
                forced = {"html": "text/html", "javascript": "text/javascript", "manifest": "application/vnd.hhs.manifest+json"}.get(args.ingest_command)
                return service.ingest_path(args.path, mime_type=args.mime_type or forced, namespace=args.namespace, analyze=not args.no_analyze)
            if args.ingest_command == "stdin":
                return service.ingest_bytes(sys.stdin.buffer.read(), name=args.name, mime_type=args.mime_type, namespace=args.namespace, source_kind="STDIN", acquisition={"method": "STDIN"}, analyze=not args.no_analyze)
            root = Path(args.path).expanduser().resolve()
            iterator = root.rglob("*") if args.recursive else root.glob("*")
            results = []
            for p in sorted(x for x in iterator if x.is_file()):
                try: results.append(service.ingest_path(p, namespace=args.namespace, analyze=not args.no_analyze))
                except Pass145Error as exc: results.append({"path": str(p), "error": exc.to_dict()})
            return {"status": "DIRECTORY_INGEST_COMPLETE", "root": str(root), "results": results}
        if args.command == "source":
            source = service.db.get_source(args.source_id, include_raw=True)
            if source is None:
                raise Pass145Error("PROVENANCE_INCOMPLETE", "source not found", "SOURCE", args.source_id)
            raw = source.pop("raw_bytes")
            if args.source_command == "export":
                destination = Path(args.path).expanduser().resolve()
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
                return {"status": "SOURCE_EXPORTED", "source_id": args.source_id, "path": str(destination), "byte_length": len(raw), "raw_sha256": source["raw_sha256"]}
            if args.raw_base64:
                source["raw_base64"] = base64.b64encode(raw).decode("ascii")
            return source
        if args.command == "object":
            obj = service.db.get_object(args.object_id)
            if obj is None:
                raise Pass145Error("PROVENANCE_INCOMPLETE", "object not found", "OBJECT", args.object_id)
            return obj
        if args.command == "query": return service.query(args.question, namespace=args.namespace, limit=args.limit)
        if args.command == "search": return service.search(args.text, symbol=args.symbol, object_type=args.object_type, source_id=args.source, namespace=args.namespace, limit=args.limit)
        if args.command == "graph":
            if args.graph_command == "trace": return service.graph_trace(args.object_id, max_depth=args.max_depth)
            return service.search("", object_type="CONTRADICTION")
        if args.command == "analyze":
            if args.analyze_command == "changes": return service.analyze_changes(args.version_a, args.version_b)
            if args.analyze_command == "relationships": return service.graph_trace(args.object_id)
            type_map = {"contradictions":"CONTRADICTION", "definitions":"DEFINITION"}
            if args.analyze_command in type_map: return service.search("", object_type=type_map[args.analyze_command])
            return {"schema":"HHS_PASS145_DEPENDENCY_ANALYSIS_V1", "relations":[json.loads(r[0]) for r in service.db.conn.execute("SELECT relation_json FROM relations WHERE relation_type='DEPENDS_ON' ORDER BY relation_id")]}
        if args.command == "validate":
            if args.validate_command == "source": return service.validate_source(args.source_id)
            if args.validate_command == "object":
                obj=service.db.get_object(args.object_id)
                if not obj: raise Pass145Error("PROVENANCE_INCOMPLETE","object not found","VALIDATION",args.object_id)
                return service.db.add_validation("OBJECT",args.object_id,"V4-V6","VALIDATED",{"object_hash72":obj["object_hash72"]})
            if args.validate_command == "database": return service.db.integrity_check()
            if args.validate_command == "receipt": return service.db.get_receipt(args.receipt_id) if args.receipt_id else service.db.verify_receipt_chain()
            return service.replay_ingestion(args.source_id)
        if args.command == "protect":
            if args.protect_command == "status": return {"database":service.db.integrity_check(),"quarantined_sources":service.db.conn.execute("SELECT COUNT(*) FROM sources WHERE quarantined=1").fetchone()[0],"quarantined_objects":service.db.conn.execute("SELECT COUNT(*) FROM objects WHERE quarantined=1").fetchone()[0]}
            return service.quarantine(args.object_id) if args.protect_command == "quarantine" else service.release_quarantine(args.object_id)
        if args.command == "replay": return service.replay_ingestion(args.source_id) if args.replay_command == "ingestion" else lvms.replay(args.execution_id)
        if args.command == "receipt":
            if args.receipt_command == "show":
                obj=service.db.get_receipt(args.receipt_id)
                if obj is None: raise Pass145Error("PROVENANCE_INCOMPLETE","receipt not found","RECEIPT",args.receipt_id)
                return obj
            return service.db.list_receipts(args.limit)
        if args.command == "database":
            if args.database_command in {"status","integrity"}: return service.status() if args.database_command == "status" else service.db.integrity_check()
            if args.database_command == "compact":
                before=service.db.path.stat().st_size if service.db.path.exists() else 0
                service.db.conn.execute("VACUUM")
                return {"status":"DATABASE_COMPACTED","before_bytes":before,"after_bytes":service.db.path.stat().st_size,"replay_critical_information_removed":False}
            return {"status":"DATABASE_SCHEMA_CURRENT","schema_id":service.db.meta("schema_id"),"schema_version":service.db.meta("schema_version")}
        if args.command == "backup":
            if args.backup_command == "create": return service.backup_create(args.path)
            return service.backup_verify(args.path)
        if args.command == "restore": return service.restore_preview(args.path)
        if args.command == "workspace":
            c=args.workspace_command
            if c=="create": return workspaces.create(args.name,description=args.description,active_environment_id=args.active_environment)
            if c=="inspect": return workspaces.inspect(args.workspace_id)
            if c=="list": return workspaces.list()
            if c=="add": return workspaces.add_member(args.workspace_id,args.member_type,args.member_id)
            if c=="activate": return workspaces.activate_environment(args.workspace_id,args.environment_id)
            return workspaces.export(args.workspace_id,args.path)
        if args.command == "api":
            c=args.api_command
            if c=="create": return apis.create_collection(args.name,json.loads(Path(args.collection).read_text(encoding="utf-8")),environment_id=args.environment)
            if c=="inspect": return apis.get(args.collection_id)
            if c=="execute": return apis.execute(args.collection_id,args.request_name,variables=json.loads(args.variables),secrets=json.loads(args.secrets),allow_remote=args.allow_remote)
            return apis.generate_client(args.collection_id,args.request_name,language=args.language)
        if args.command == "extension":
            c=args.extension_command
            if c=="install": return extensions.install(json.loads(Path(args.manifest).read_text(encoding="utf-8")))
            if c=="inspect": return extensions.inspect(args.extension_id)
            if c=="list": return extensions.list()
            return extensions.uninstall(args.extension_id,authority=args.authority)
        if args.command == "env":
            c=args.env_command
            if c=="create": return env.create(args.name,namespace=args.namespace,description=args.description)
            if c=="inspect": return env.inspect(args.environment_id)
            if c=="list": return env.list()
            if c in {"clone","branch"}: return env.clone(args.environment_id,args.new_name,namespace=args.namespace,branch=c=="branch")
            if c=="diff": return env.diff(args.left,args.right)
            if c=="merge": return env.merge(args.source,args.destination,resolutions=json.loads(Path(args.resolutions).read_text()) if args.resolutions else {})
            if c=="freeze": return env.set_frozen(args.environment_id,True)
            if c=="unfreeze": return env.set_frozen(args.environment_id,False)
            if c=="archive": return env.archive(args.environment_id)
            if c=="export": return env.export(args.environment_id,args.path)
            if c=="import": return env.import_package(args.path,new_namespace=args.namespace)
            return env.destroy(args.environment_id,authority=args.authority)
        if args.command == "script":
            c=args.script_command
            if c=="import":
                p=Path(args.path).expanduser().resolve(); return scripts.import_script(args.name or p.name,args.language,p.read_text(encoding="utf-8"),environment_id=args.environment,declared_capabilities=args.capability)
            if c=="paste": return scripts.import_script(args.name,args.language,sys.stdin.read(),environment_id=args.environment,declared_capabilities=args.capability)
            if c=="validate": return scripts.validate(args.script_id)
            if c=="run": return scripts.execute(args.script_id,inputs=json.loads(args.input_json))
            return scripts.get(args.script_id)
        if args.command == "lvm":
            c=args.lvm_command
            if c=="create": return lvms.create(json.loads(Path(args.manifest).read_text(encoding="utf-8")),environment_id=args.environment)
            if c=="run": return lvms.execute(args.lvm_id,json.loads(args.input_json))
            if c=="inspect": return lvms.get(args.lvm_id)
            return lvms.replay(args.execution_id)
        if args.command == "shell":
            print("HHS Pass 145 shell. Enter 'exit' to close.")
            while True:
                try: line=input("hhs> ")
                except EOFError: break
                if line.strip() in {"exit","quit"}: break
                if not line.strip(): continue
                try:
                    nested=build_parser().parse_args(["--db",args.db,"--format",args.format,*shlex.split(line)])
                    _print(_dispatch(nested),args.format)
                except Exception as exc: _print(exc.to_dict() if isinstance(exc,Pass145Error) else {"ok":False,"error":str(exc)},args.format)
            return {"status":"SHELL_CLOSED"}
    raise Pass145Error("QUERY_PLAN_FAILED","unhandled command","CLI")


def main(argv: list[str] | None = None) -> int:
    parser=build_parser()
    try:
        args=parser.parse_args(argv)
        result=_dispatch(args)
        _print(result,args.format)
        if isinstance(result,dict) and (result.get("ok") is False or str(result.get("status","")).endswith(("FAILED","REJECTED","MISMATCH"))): return EXIT_OPERATION_FAILED
        return EXIT_OK
    except Pass145Error as exc:
        fmt="json"
        if argv:
            try:
                i=argv.index("--format"); fmt=argv[i+1]
            except Exception: pass
        print(_render(exc.to_dict(),fmt),file=sys.stderr)
        if exc.code in {"PROVENANCE_INCOMPLETE"}: return EXIT_NOT_FOUND
        if exc.code in {"DATABASE_CORRUPT","REPLAY_MISMATCH"}: return EXIT_INTEGRITY
        return EXIT_REJECTED
    except KeyboardInterrupt:
        print(canonical_json({"ok":False,"error_code":"INTERRUPTED_EXECUTION"}),file=sys.stderr); return 130
    except Exception as exc:
        print(canonical_json({"ok":False,"error_code":type(exc).__name__,"description":str(exc)}),file=sys.stderr); return EXIT_OPERATION_FAILED

if __name__ == "__main__":
    raise SystemExit(main())
