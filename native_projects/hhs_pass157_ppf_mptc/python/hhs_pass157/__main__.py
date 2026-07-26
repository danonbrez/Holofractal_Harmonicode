from __future__ import annotations
import json
import sys
from .executor import verify
from .parser import compile_membrane

def main() -> int:
    command = sys.argv[1] if len(sys.argv) > 1 else "verify"
    if command == "verify":
        print(json.dumps(verify(), sort_keys=True, separators=(",", ":")))
        return 0
    if command == "parse":
        source = " ".join(sys.argv[2:])
        print(json.dumps(compile_membrane(source), sort_keys=True, separators=(",", ":")))
        return 0
    if command == "repl":
        for line in sys.stdin:
            source = line.rstrip("\n")
            if source in {"quit", "exit"}:
                return 0
            print(json.dumps(compile_membrane(source), sort_keys=True, separators=(",", ":")))
        return 0
    print("usage: python -m hhs_pass157 [verify|parse SOURCE|repl]", file=sys.stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
