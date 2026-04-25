"""
terminal_hhsprog_v2.py

Native interactive terminal V2 for the HARMONICODE General Programming Environment.

Adds over V1
------------
1. Variables
   x = add 2 3
   y = mul $x 10

2. Pipes
   [3,1,2] | sort | sum
   [1,3,5,7] | search 5

3. Session save/load
   save session.hhsrun
   load session.hhsrun

4. Direct shortcuts
   + 2 3
   - 5 2
   * 3 7
   / 8 2

Every operation still routes through:
    parse -> AuditedRunner -> kernel audit -> Hash72 receipt -> output
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import shlex
import sys

from hhs_general_runtime_layer_v1 import AuditedRunner, DEFAULT_KERNEL_PATH, canonicalize_for_hash72
from hhs_program_format_and_cli_v1 import execute_program, load_json, verify_run_file, RUN_RESULT_FORMAT
from hhs_receipt_replay_verifier_v1 import HHSReceiptReplayVerifierV1


TERMINAL_FORMAT = "TERMINAL_HHSPROG_V2"


class HHSTerminalV2:
    def __init__(self, kernel_path: str | Path = DEFAULT_KERNEL_PATH):
        self.kernel_path = Path(kernel_path)
        self.runner = AuditedRunner(self.kernel_path)
        self.vars: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.last_output: Optional[Dict[str, Any]] = None
        self.running = True

    # ------------------------------------------------------------------
    # Parsing / values
    # ------------------------------------------------------------------

    def parse_value(self, token: str) -> Any:
        token = token.strip()

        if token == "_":
            return self.extract_result_value(self.last_output)

        if token.startswith("$"):
            name = token[1:]
            if name not in self.vars:
                raise KeyError(f"unknown variable: {name}")
            return self.vars[name]

        # JSON list/object/string/number
        if token.startswith("[") or token.startswith("{") or token.startswith('"'):
            return json.loads(token)

        # int / float string fallback; leave as string if not numeric
        try:
            if "." in token:
                return token  # keep decimal exact as string for Fraction downstream
            return int(token)
        except ValueError:
            return token

    @staticmethod
    def extract_result_value(output: Optional[Dict[str, Any]]) -> Any:
        if not output:
            return None
        if not output.get("ok"):
            return None
        result = output.get("result")
        if isinstance(result, dict):
            if "result" in result:
                return result["result"]
            if "__fraction__" in result:
                return result
        return result

    @staticmethod
    def unwrap_fraction_obj(x: Any) -> Any:
        if isinstance(x, dict) and "__fraction__" in x:
            n, d = x["__fraction__"]
            if d == 1:
                return n
            return f"{n}/{d}"
        if isinstance(x, list):
            return [HHSTerminalV2.unwrap_fraction_obj(v) for v in x]
        if isinstance(x, dict):
            return {k: HHSTerminalV2.unwrap_fraction_obj(v) for k, v in x.items()}
        return x

    def emit(self, payload: Dict[str, Any]) -> None:
        self.last_output = payload
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    def execute_op(self, op: str, *args: Any) -> Dict[str, Any]:
        out = self.runner.execute(
            op,
            *args,
            input_payload={
                "terminal": TERMINAL_FORMAT,
                "op": op,
                "args": canonicalize_for_hash72(args),
                "history_index": len(self.history),
                "vars": canonicalize_for_hash72(self.vars),
            },
        )
        record = {
            "kind": "operation",
            "op": op,
            "args": canonicalize_for_hash72(args),
            "output": out,
        }
        self.history.append(record)
        return out

    # ------------------------------------------------------------------
    # Operation command helpers
    # ------------------------------------------------------------------

    def run_operation_tokens(self, tokens: List[str]) -> Dict[str, Any]:
        if not tokens:
            return {"ok": False, "error": "empty operation"}

        shortcut = {
            "+": "ADD",
            "-": "SUB",
            "*": "MUL",
            "/": "DIV",
            "add": "ADD",
            "sub": "SUB",
            "mul": "MUL",
            "div": "DIV",
            "sum": "SUM",
            "sort": "SORT",
            "search": "BINARY_SEARCH",
        }

        cmd = tokens[0].lower()
        if cmd not in shortcut:
            return {"ok": False, "error": f"unknown operation: {tokens[0]}"}

        op = shortcut[cmd]
        args = [self.parse_value(t) for t in tokens[1:]]

        if op in {"ADD", "SUB", "MUL", "DIV"} and len(args) != 2:
            return {"ok": False, "error": f"{cmd} requires 2 args"}

        if op in {"SUM", "SORT"} and len(args) != 1:
            return {"ok": False, "error": f"{cmd} requires 1 JSON/list arg"}

        if op == "BINARY_SEARCH" and len(args) != 2:
            return {"ok": False, "error": "search requires list and target"}

        return self.execute_op(op, *args)

    # ------------------------------------------------------------------
    # Pipes
    # ------------------------------------------------------------------

    def run_pipe(self, line: str) -> Dict[str, Any]:
        parts = [p.strip() for p in line.split("|")]
        if not parts:
            return {"ok": False, "error": "empty pipe"}

        current = self.parse_value(parts[0])
        pipe_steps = []

        for raw_step in parts[1:]:
            tokens = shlex.split(raw_step)
            if not tokens:
                return {"ok": False, "error": "empty pipe step"}

            cmd = tokens[0].lower()

            if cmd == "sort":
                out = self.execute_op("SORT", current)
                current = self.extract_result_value(out)
                # SORT returns dict; use sorted list inside result
                if isinstance(current, dict) and "result" in current:
                    current = current["result"]

            elif cmd == "sum":
                out = self.execute_op("SUM", current)
                current = self.extract_result_value(out)

            elif cmd == "search":
                if len(tokens) != 2:
                    return {"ok": False, "error": "pipe search requires target"}
                target = self.parse_value(tokens[1])
                out = self.execute_op("BINARY_SEARCH", current, target)
                current = self.extract_result_value(out)

            else:
                # binary arithmetic pipe: current | add 2
                if cmd in {"add", "+", "sub", "-", "mul", "*", "div", "/"}:
                    if len(tokens) != 2:
                        return {"ok": False, "error": f"pipe {cmd} requires one rhs arg"}
                    rhs = self.parse_value(tokens[1])
                    op_tokens = [cmd, json.dumps(self.unwrap_fraction_obj(current)), str(rhs)]
                    out = self.run_operation_tokens(op_tokens)
                    current = self.extract_result_value(out)
                else:
                    return {"ok": False, "error": f"unknown pipe step: {cmd}"}

            pipe_steps.append({
                "step": raw_step,
                "output_ok": out.get("ok"),
                "receipt": out.get("receipt"),
            })

            if not out.get("ok"):
                return {
                    "ok": False,
                    "error": "pipe step quarantined",
                    "step": raw_step,
                    "output": out,
                    "pipe_steps": pipe_steps,
                }

        result = {
            "ok": True,
            "pipe_result": canonicalize_for_hash72(current),
            "pipe_steps": pipe_steps,
            "tip_hash72": self.runner.commitments.tip_hash72,
        }
        self.history.append({"kind": "pipe", "line": line, "result": result})
        return result

    # ------------------------------------------------------------------
    # Built-in commands
    # ------------------------------------------------------------------

    def cmd_help(self, args: List[str]) -> Dict[str, Any]:
        return {
            "ok": True,
            "terminal": TERMINAL_FORMAT,
            "commands": [
                "x = add 2 3",
                "y = mul $x 10",
                "[3,1,2] | sort | sum",
                "[1,3,5,7] | search 5",
                "+ 2 3 / - 5 2 / * 3 7 / / 8 2",
                "vars",
                "status",
                "ops",
                "run file.hhsprog",
                "verify file.hhsrun",
                "save file.hhsrun",
                "load file.hhsrun",
                "receipts",
                "chain",
                "quit / exit",
            ],
        }

    def cmd_status(self, args: List[str]) -> Dict[str, Any]:
        return {
            "ok": True,
            "kernel_path": str(self.kernel_path),
            "phase": self.runner.commitments.phase,
            "receipt_count": len(self.runner.commitments.receipts),
            "tip_hash72": self.runner.commitments.tip_hash72,
            "vars": canonicalize_for_hash72(self.vars),
            "chain": self.runner.commitments.verify_chain(),
        }

    def cmd_ops(self, args: List[str]) -> Dict[str, Any]:
        return {"ok": True, "operations": self.runner.registry.names()}

    def cmd_vars(self, args: List[str]) -> Dict[str, Any]:
        return {"ok": True, "vars": canonicalize_for_hash72(self.vars)}

    def cmd_receipts(self, args: List[str]) -> Dict[str, Any]:
        return {"ok": True, "receipts": [r.to_dict() for r in self.runner.commitments.receipts]}

    def cmd_chain(self, args: List[str]) -> Dict[str, Any]:
        report = HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.runner).to_dict()
        return {
            "ok": report["ok"],
            "chain": self.runner.commitments.verify_chain(),
            "replay": report,
        }

    def cmd_save(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return {"ok": False, "error": "save requires output path"}

        path = Path(args[0])
        payload = {
            "format": RUN_RESULT_FORMAT,
            "program_name": "TERMINAL_SESSION",
            "terminal_format": TERMINAL_FORMAT,
            "variables": canonicalize_for_hash72(self.vars),
            "operation_count_declared": len(self.history),
            "operation_count_executed": len(self.history),
            "results": self.history,
            "receipts": [r.to_dict() for r in self.runner.commitments.receipts],
            "chain": self.runner.commitments.verify_chain(),
            "replay": HHSReceiptReplayVerifierV1(self.kernel_path).verify_runner(self.runner).to_dict(),
            "storage_report": None,
            "all_ok": self.runner.commitments.verify_chain().get("ok") is True,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "ok": True,
            "saved": str(path),
            "receipt_count": len(self.runner.commitments.receipts),
            "tip_hash72": self.runner.commitments.tip_hash72,
        }

    def cmd_load(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return {"ok": False, "error": "load requires .hhsrun path"}

        path = Path(args[0])
        payload = load_json(path)
        if payload.get("format") != RUN_RESULT_FORMAT:
            return {"ok": False, "error": "not an HHS_RUN_RESULT_V1 file"}

        verify = HHSReceiptReplayVerifierV1(self.kernel_path).verify(
            payload.get("receipts", []),
            expected_tip_hash72=payload.get("chain", {}).get("tip_hash72"),
        ).to_dict()

        if not verify.get("ok"):
            return {"ok": False, "error": "session replay verification failed", "verify": verify}

        # Load variables only; receipt continuation remains intentionally explicit.
        self.vars = payload.get("variables", {}) or {}
        self.history.append({
            "kind": "session_load",
            "path": str(path),
            "verified_tip_hash72": verify.get("tip_hash72"),
        })

        return {
            "ok": True,
            "loaded": str(path),
            "loaded_variables": self.vars,
            "verified_tip_hash72": verify.get("tip_hash72"),
            "note": "variables loaded; new receipts continue in current terminal chain",
        }

    def cmd_run(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return {"ok": False, "error": "run requires .hhsprog path"}
        program = load_json(args[0])
        result = execute_program(program, kernel_path=self.kernel_path)
        self.history.append({"kind": "program_run", "path": args[0], "output": result})
        return result

    def cmd_verify(self, args: List[str]) -> Dict[str, Any]:
        if not args:
            return {"ok": False, "error": "verify requires .hhsrun path"}
        return verify_run_file(args[0], kernel_path=self.kernel_path)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def assign(self, name: str, rhs: str) -> Dict[str, Any]:
        out = self.dispatch(rhs, allow_assignment=False)
        if not out.get("ok"):
            return {
                "ok": False,
                "assignment": name,
                "error": "rhs failed",
                "rhs_output": out,
            }

        value = None
        if "pipe_result" in out:
            value = out["pipe_result"]
        else:
            value = self.extract_result_value(out)

        self.vars[name] = value
        return {
            "ok": True,
            "assigned": name,
            "value": canonicalize_for_hash72(value),
            "source_output": out,
        }

    def dispatch(self, line: str, *, allow_assignment: bool = True) -> Dict[str, Any]:
        line = line.strip()
        if not line:
            return {"ok": True, "noop": True}

        if allow_assignment and "=" in line and not line.startswith(("==", ">=", "<=")):
            lhs, rhs = line.split("=", 1)
            name = lhs.strip()
            if not name.replace("_", "").isalnum() or name[0].isdigit():
                return {"ok": False, "error": f"invalid variable name: {name}"}
            return self.assign(name, rhs.strip())

        if "|" in line:
            return self.run_pipe(line)

        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            return {"ok": False, "error": f"parse error: {exc}"}

        if not tokens:
            return {"ok": True, "noop": True}

        cmd = tokens[0].lower()
        args = tokens[1:]

        if cmd in {"quit", "exit"}:
            self.running = False
            return {"ok": True, "terminal": "closing"}

        builtins = {
            "help": self.cmd_help,
            "status": self.cmd_status,
            "ops": self.cmd_ops,
            "vars": self.cmd_vars,
            "receipts": self.cmd_receipts,
            "chain": self.cmd_chain,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "run": self.cmd_run,
            "verify": self.cmd_verify,
        }

        if cmd in builtins:
            try:
                return builtins[cmd](args)
            except Exception as exc:
                return {"ok": False, "error": type(exc).__name__, "message": str(exc)}

        return self.run_operation_tokens(tokens)

    def repl(self) -> None:
        print("TERMINAL_HHSPROG_V2 LOCKED SHELL")
        print("type 'help' for commands; 'exit' to close")
        while self.running:
            try:
                line = input("hhs> ")
            except EOFError:
                break
            out = self.dispatch(line)
            self.emit(out)


def main(argv: Optional[List[str]] = None) -> int:
    term = HHSTerminalV2()
    if argv and len(argv) > 0:
        out = term.dispatch(" ".join(argv))
        term.emit(out)
        return 0 if out.get("ok") else 1
    term.repl()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
