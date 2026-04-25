"""
terminal_hhsprog_v5_macro_algebra.py

Macro-capable symbolic algebra terminal for HARMONICODE.

Adds over V4
------------
1. Algebra-native macro definitions
   DEF NAME(arg1,arg2) := expression

2. Macro calls
   CALL NAME(value1,value2)
   NAME(value1,value2)

3. Nested macro expansion
   DEF DOUBLE(x) := x + x
   DEF QUAD(x) := DOUBLE(DOUBLE(x))
   CALL QUAD(3)

4. Symbolic gate macros
   DEF PLASTIC_GATE() := Π2((b²-b)^2)/((c²-b²)*a²)==b²

5. Hash72 committed expansion traces
   source_hash72
   macro_hash72
   expansion_hash72
   call_receipt

Execution model
---------------
macro source -> canonical symbolic macro -> call expansion -> symbolic commit
-> AuditedRunner receipt -> replayable Hash72 chain
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import re
import sys

from hhs_general_runtime_layer_v1 import AuditedRunner, DEFAULT_KERNEL_PATH
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1
from hhs_program_format_and_cli_v1 import verify_run_file, RUN_RESULT_FORMAT, load_json
from terminal_hhsprog_v4_symbolic import HHSSymbolicParserV1


TERMINAL_FORMAT = "TERMINAL_HHSPROG_V5_MACRO_ALGEBRA"


@dataclass(frozen=True)
class HHSMacroDefinition:
    name: str
    params: List[str]
    body: str
    normalized_body: str
    macro_hash72: str
    source_hash72: str
    symbolic_hash72: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class HHSMacroCallTrace:
    name: str
    args: List[str]
    bindings: Dict[str, str]
    raw_body: str
    expanded_source: str
    nested_expansions: List[Dict[str, Any]]
    macro_hash72: str
    expansion_hash72: str
    receipt: Optional[Dict[str, Any]]
    ok: bool
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HHSMacroError(RuntimeError):
    pass


class HHSMacroRegistryV1:
    def __init__(self, runner: AuditedRunner):
        self.runner = runner
        self.parser = HHSSymbolicParserV1(runner.authority)
        self.macros: Dict[str, HHSMacroDefinition] = {}

    @staticmethod
    def parse_signature(sig: str) -> Tuple[str, List[str]]:
        m = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*", sig)
        if not m:
            raise HHSMacroError(f"invalid macro signature: {sig}")
        name = m.group(1)
        raw_params = m.group(2).strip()
        params = [] if not raw_params else [p.strip() for p in raw_params.split(",")]
        return name, params

    @staticmethod
    def split_args(arg_source: str) -> List[str]:
        args: List[str] = []
        cur = []
        depth = 0
        for ch in arg_source:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            if ch == "," and depth == 0:
                args.append("".join(cur).strip())
                cur = []
            else:
                cur.append(ch)
        tail = "".join(cur).strip()
        if tail:
            args.append(tail)
        return args

    @staticmethod
    def parse_call_source(source: str) -> Tuple[str, List[str]]:
        src = source.strip()
        if src.upper().startswith("CALL "):
            src = src[5:].strip()
        m = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*", src, re.DOTALL)
        if not m:
            raise HHSMacroError(f"invalid macro call: {source}")
        return m.group(1), HHSMacroRegistryV1.split_args(m.group(2).strip())

    def define(self, source: str) -> HHSMacroDefinition:
        src = source.strip()
        if src.upper().startswith("DEF "):
            src = src[4:].strip()
        if ":=" not in src:
            raise HHSMacroError("macro definition requires :=")
        sig, body = src.split(":=", 1)
        name, params = self.parse_signature(sig)
        body = body.strip()

        parsed = self.parser.parse(body)
        source_hash = self.runner.authority.commit(
            {"macro_definition_source": source},
            domain="HHS_MACRO_SOURCE",
        )
        macro_core = {
            "name": name,
            "params": params,
            "body": body,
            "normalized_body": parsed["normalized_source"],
            "symbolic_hash72": parsed["symbolic_hash72"],
        }
        macro_hash = self.runner.authority.commit(macro_core, domain="HHS_MACRO_DEFINITION")

        macro = HHSMacroDefinition(
            name=name,
            params=params,
            body=body,
            normalized_body=parsed["normalized_source"],
            macro_hash72=macro_hash,
            source_hash72=source_hash,
            symbolic_hash72=parsed["symbolic_hash72"],
        )
        self.macros[name] = macro

        self.runner.execute(
            "SUM",
            [1],
            input_payload={
                "terminal": TERMINAL_FORMAT,
                "form": "MACRO_DEFINITION",
                "macro": macro.to_dict(),
            },
        )
        return macro

    @staticmethod
    def substitute_params(body: str, bindings: Dict[str, str]) -> str:
        out = body
        for param, value in sorted(bindings.items(), key=lambda kv: len(kv[0]), reverse=True):
            out = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(param)}(?![A-Za-z0-9_])", f"({value})", out)
        return out

    def expand_nested_once(self, source: str, depth: int) -> Tuple[str, List[Dict[str, Any]], bool]:
        expansions: List[Dict[str, Any]] = []
        changed = False

        for name in sorted(self.macros.keys(), key=len, reverse=True):
            pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*\(")
            match = pattern.search(source)
            if not match:
                continue

            start_name = match.start()
            start_args = source.find("(", match.start())
            depth_count = 0
            end = None
            for i in range(start_args, len(source)):
                if source[i] == "(":
                    depth_count += 1
                elif source[i] == ")":
                    depth_count -= 1
                    if depth_count == 0:
                        end = i
                        break
            if end is None:
                raise HHSMacroError(f"unclosed nested macro call: {name}")

            call_src = source[start_name:end + 1]
            trace = self.expand_call(call_src, depth=depth + 1, commit=False)
            source = source[:start_name] + f"({trace.expanded_source})" + source[end + 1:]
            expansions.append(trace.to_dict())
            changed = True
            break

        return source, expansions, changed

    def expand_call(self, source: str, *, depth: int = 0, commit: bool = True, max_depth: int = 16) -> HHSMacroCallTrace:
        if depth > max_depth:
            raise HHSMacroError("macro expansion depth exceeded")

        name, args = self.parse_call_source(source)
        if name not in self.macros:
            raise HHSMacroError(f"unknown macro: {name}")

        macro = self.macros[name]
        if len(args) != len(macro.params):
            raise HHSMacroError(f"{name} expected {len(macro.params)} args, got {len(args)}")

        bindings = dict(zip(macro.params, args))
        expanded = self.substitute_params(macro.body, bindings)
        nested: List[Dict[str, Any]] = []

        while True:
            expanded, new_nested, changed = self.expand_nested_once(expanded, depth)
            nested.extend(new_nested)
            if not changed:
                break

        expansion_hash = self.runner.authority.commit(
            {
                "macro_hash72": macro.macro_hash72,
                "name": name,
                "args": args,
                "bindings": bindings,
                "expanded_source": expanded,
                "nested": nested,
            },
            domain="HHS_MACRO_EXPANSION",
        )

        receipt = None
        ok = True
        err = ""

        if commit:
            out = self.runner.execute(
                "SUM",
                [1],
                input_payload={
                    "terminal": TERMINAL_FORMAT,
                    "form": "MACRO_CALL",
                    "macro_hash72": macro.macro_hash72,
                    "expansion_hash72": expansion_hash,
                    "source": source,
                    "expanded_source": expanded,
                    "bindings": bindings,
                    "nested": nested,
                },
            )
            receipt = out.get("receipt")
            ok = bool(out.get("ok"))
            err = "" if ok else out.get("reason", "macro call audit failed")

        return HHSMacroCallTrace(
            name=name,
            args=args,
            bindings=bindings,
            raw_body=macro.body,
            expanded_source=expanded,
            nested_expansions=nested,
            macro_hash72=macro.macro_hash72,
            expansion_hash72=expansion_hash,
            receipt=receipt,
            ok=ok,
            error=err,
        )


class HHSMacroAlgebraTerminalV5:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.kernel_path = Path(kernel_path)
        self.runner = AuditedRunner(self.kernel_path)
        self.parser = HHSSymbolicParserV1(self.runner.authority)
        self.registry = HHSMacroRegistryV1(self.runner)
        self.symbolic_forms: Dict[str, Dict[str, Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self.running = True
        self.install_builtin_macros()

    def install_builtin_macros(self) -> None:
        builtins = [
            "DEF CLOSURE(a,b,c) := c^2-a^2==b^2",
            "DEF RECIP_LOCK(x,y) := x==1/y==(-y)",
            "DEF PLASTIC_GATE() := Π2((b²-b)^2)/((c²-b²)*a²)==b²==ρ^4",
            "DEF CUBIC_NORMALIZE(delta) := (delta*ρ^-1)==1==a²",
            "DEF LOSHU() := List(List(4,9,2),List(3,5,7),List(8,1,6))",
        ]
        for src in builtins:
            try:
                self.registry.define(src)
            except Exception:
                pass

    def commit_symbolic(self, source: str) -> Dict[str, Any]:
        parsed = self.parser.parse(source)
        out = self.runner.execute(
            "SUM",
            [1],
            input_payload={
                "terminal": TERMINAL_FORMAT,
                "form": "SYMBOLIC_COMMIT",
                "parsed": parsed,
            },
        )
        payload = {
            "ok": bool(out.get("ok")),
            "form_type": parsed["structure"]["form"],
            "source": source,
            "normalized_source": parsed["normalized_source"],
            "source_hash72": parsed["source_hash72"],
            "symbolic_hash72": parsed["symbolic_hash72"],
            "structure": parsed["structure"],
            "receipt": out.get("receipt"),
        }
        self.symbolic_forms[parsed["symbolic_hash72"]] = payload
        self.history.append(payload)
        return payload

    def help(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "terminal": TERMINAL_FORMAT,
            "syntax": [
                "DEF NAME(a,b) := expression",
                "CALL NAME(x,y)",
                "NAME(x,y)",
                "paste symbolic equation directly",
                "macros",
                "showmacro NAME",
                "expand NAME(args)",
                "forms",
                "status",
                "chain",
                "save file.hhsrun",
                "load file.hhsrun",
            ],
        }

    def dispatch(self, line: str) -> Dict[str, Any]:
        src = line.strip()
        if not src:
            return {"ok": True, "noop": True}

        parts = src.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in {"quit", "exit"}:
            self.running = False
            return {"ok": True, "terminal": "closing"}

        if cmd == "help":
            return self.help()

        if cmd == "status":
            return {
                "ok": True,
                "phase": self.runner.commitments.phase,
                "receipt_count": len(self.runner.commitments.receipts),
                "macro_count": len(self.registry.macros),
                "symbolic_form_count": len(self.symbolic_forms),
                "tip_hash72": self.runner.commitments.tip_hash72,
                "chain": self.runner.commitments.verify_chain(),
            }

        if cmd == "chain":
            report = HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.runner).to_dict()
            return {"ok": report["ok"], "replay": report, "chain": self.runner.commitments.verify_chain()}

        if cmd == "macros":
            return {"ok": True, "macros": {k: v.to_dict() for k, v in self.registry.macros.items()}}

        if cmd == "showmacro":
            if not arg:
                return {"ok": False, "error": "showmacro requires name"}
            if arg not in self.registry.macros:
                return {"ok": False, "error": f"unknown macro: {arg}"}
            return {"ok": True, "macro": self.registry.macros[arg].to_dict()}

        if cmd == "forms":
            return {"ok": True, "forms": list(self.symbolic_forms.values())}

        if cmd == "expand":
            try:
                trace = self.registry.expand_call(arg, commit=False)
                return {"ok": True, "expansion": trace.to_dict()}
            except Exception as exc:
                return {"ok": False, "error": type(exc).__name__, "message": str(exc)}

        if cmd == "save":
            if not arg:
                return {"ok": False, "error": "save requires path"}
            payload = {
                "format": RUN_RESULT_FORMAT,
                "program_name": "TERMINAL_MACRO_ALGEBRA_SESSION",
                "terminal_format": TERMINAL_FORMAT,
                "macros": {k: v.to_dict() for k, v in self.registry.macros.items()},
                "symbolic_forms": list(self.symbolic_forms.values()),
                "history": self.history,
                "receipts": [r.to_dict() for r in self.runner.commitments.receipts],
                "chain": self.runner.commitments.verify_chain(),
                "replay": HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.runner).to_dict(),
                "all_ok": self.runner.commitments.verify_chain().get("ok") is True,
            }
            Path(arg).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            return {"ok": True, "saved": arg, "tip_hash72": self.runner.commitments.tip_hash72}

        if cmd == "load":
            if not arg:
                return {"ok": False, "error": "load requires path"}
            payload = load_json(arg)
            verify = HHSReceiptReplayVerifierV1(self.kernel_path).verify(
                payload.get("receipts", []),
                expected_tip_hash72=payload.get("chain", {}).get("tip_hash72"),
            ).to_dict()
            if not verify.get("ok"):
                return {"ok": False, "error": "replay verification failed", "verify": verify}
            for name, macro in payload.get("macros", {}).items():
                self.registry.macros[name] = HHSMacroDefinition(**macro)
            for form in payload.get("symbolic_forms", []):
                if "symbolic_hash72" in form:
                    self.symbolic_forms[form["symbolic_hash72"]] = form
            return {"ok": True, "loaded": arg, "verify": verify}

        if cmd == "verify":
            if not arg:
                return {"ok": False, "error": "verify requires path"}
            return verify_run_file(arg, kernel_path=self.kernel_path)

        if src.upper().startswith("DEF ") or (":=" in src and re.match(r"[A-Za-z_][A-Za-z0-9_]*\s*\(", src)):
            try:
                macro = self.registry.define(src)
                payload = {"ok": True, "defined_macro": macro.to_dict()}
                self.history.append(payload)
                return payload
            except Exception as exc:
                return {"ok": False, "error": type(exc).__name__, "message": str(exc)}

        if src.upper().startswith("CALL ") or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*", src, re.DOTALL):
            name = src[5:].strip().split("(", 1)[0] if src.upper().startswith("CALL ") else src.split("(", 1)[0].strip()
            if name in self.registry.macros:
                try:
                    trace = self.registry.expand_call(src)
                    expanded_commit = self.commit_symbolic(trace.expanded_source)
                    payload = {
                        "ok": trace.ok and expanded_commit.get("ok"),
                        "macro_call": trace.to_dict(),
                        "expanded_symbolic_commit": expanded_commit,
                    }
                    self.history.append(payload)
                    return payload
                except Exception as exc:
                    return {"ok": False, "error": type(exc).__name__, "message": str(exc)}

        try:
            return self.commit_symbolic(src)
        except Exception as exc:
            return {"ok": False, "error": type(exc).__name__, "message": str(exc), "source": src}

    def repl(self) -> None:
        print("TERMINAL_HHSPROG_V5_MACRO_ALGEBRA LOCKED SHELL")
        print("define/call algebra macros directly; type 'help'")
        while self.running:
            try:
                line = input("hhsΛ> ")
            except EOFError:
                break
            print(json.dumps(self.dispatch(line), indent=2, ensure_ascii=False))


def main(argv: Optional[List[str]] = None) -> int:
    term = HHSMacroAlgebraTerminalV5()
    if argv and len(argv) > 0:
        out = term.dispatch(" ".join(argv))
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out.get("ok") else 1
    term.repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
