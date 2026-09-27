#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hhs_runtime.hhs_pass220_lane5_global_tool_hydration_v1 import (  # noqa: E402
    build_pass219_220_warm_tool_graph,
    cpp_manifest_lines,
    public_tool_graph,
    warm_pass219_220_tool_vector_store,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and optionally persist the Pass219/220 Lane5 warm-tool graph."
    )
    parser.add_argument("--repository-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--git-ref", default="HEAD")
    parser.add_argument("--state-root", type=Path)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-cpp-manifest", type=Path, required=True)
    args = parser.parse_args()

    if args.state_root is None:
        graph = build_pass219_220_warm_tool_graph(
            args.repository_root,
            git_ref=args.git_ref,
        )
        result = {
            "mode": "MANIFEST_ONLY",
            "graph": public_tool_graph(graph),
            "all_tools_warmed": False,
        }
    else:
        result = warm_pass219_220_tool_vector_store(
            args.repository_root,
            args.state_root,
            git_ref=args.git_ref,
        )
        graph = {
            **result["graph"],
            "_projection_bytes_by_tool_id_sha256": {},
        }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_cpp_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args.output_cpp_manifest.write_text(
        "\n".join(cpp_manifest_lines(graph)) + "\n",
        encoding="utf-8",
    )

    public = result["graph"]
    print(
        json.dumps(
            {
                "registered_service_count": public["registered_service_count"],
                "merged_pull_request_count": public["merged_pull_request_count"],
                "tool_count": public["tool_count"],
                "graph_root_sha256": public["graph_root_sha256"],
                "all_tools_warmed": bool(result.get("all_tools_warmed")),
                "lane5_selection_changed": bool(
                    result.get("lane5_selection_changed", False)
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
