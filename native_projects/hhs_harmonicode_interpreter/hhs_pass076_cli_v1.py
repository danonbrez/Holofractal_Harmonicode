"""Context-independent CLI for Pass 076 canonical request envelopes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from .hhs_pass076_workspace_runtime_v1 import HHSNativeInterpreterWorkspaceRuntime


def run_request_file(path: str, *, state_path: str | None = None):
    state = json.loads(Path(state_path).read_text(encoding="utf-8")) if state_path else None
    runtime = HHSNativeInterpreterWorkspaceRuntime(initial_state=state)
    request = json.loads(Path(path).read_text(encoding="utf-8"))
    response = runtime.dispatch(request)
    return response, runtime.snapshot()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--state")
    parser.add_argument("--write-state")
    args = parser.parse_args()
    response, state = run_request_file(args.request, state_path=args.state)
    print(json.dumps(response, indent=2, sort_keys=True, ensure_ascii=False))
    if args.write_state:
        Path(args.write_state).write_text(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
