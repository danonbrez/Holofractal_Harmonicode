"""CLI client for the same Pass 074 canonical dispatcher used by the API and GUI."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from .hhs_native_workspace_project_v1 import HHSNativeWorkspaceRuntime


def run_request_file(path: str, *, state_path: str | None = None):
    state = None
    if state_path and Path(state_path).is_file():
        state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    runtime = HHSNativeWorkspaceRuntime(initial_state=state)
    request = json.loads(Path(path).read_text(encoding="utf-8"))
    response = runtime.dispatch(request)
    if state_path:
        Path(state_path).write_text(json.dumps(runtime.snapshot(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("--state")
    args = parser.parse_args()
    print(json.dumps(run_request_file(args.request, state_path=args.state), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
