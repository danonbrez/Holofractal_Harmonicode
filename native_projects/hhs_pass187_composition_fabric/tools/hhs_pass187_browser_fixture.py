#!/usr/bin/env python3
from __future__ import annotations

import argparse

from hhs_runtime.pass187.composition import CompositionAuthority
from hhs_runtime.pass187.composition_server import serve


def descriptor(logical_id: str, *, inputs=(), outputs=()):
    return CompositionAuthority.descriptor(
        logical_object_id=logical_id,
        object_class="browser_fixture",
        modality_set=["application"],
        content_identity=f"content:{logical_id}",
        source_identity=f"source:{logical_id}",
        provenance={"fixture": "pass187-browser"},
        owner_or_mutation_authority="browser-test",
        permissions=["connect", "read"],
        inputs=[{"name": name, "type": typ} for name, typ in inputs],
        outputs=[{"name": name, "type": typ} for name, typ in outputs],
        operations=["connect"],
        dependencies=[],
        state_schema={"type": "object"},
        state={"fixture": logical_id},
        compatible_egress_targets=["web-app", "project-bundle", "native-cli"],
    )


def seed(db: str) -> None:
    with CompositionAuthority(db, project_id="project.browser") as authority:
        if authority.objects():
            return
        authority.create_object(
            descriptor("browser.source", outputs=[("out", "value/exact")]),
            f"{1:072x}",
        )
        authority.create_object(
            descriptor("browser.target", inputs=[("in", "value/exact")]),
            f"{2:072x}",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--web-root",
        default="native_projects/hhs_pass187_composition_fabric/web",
    )
    ns = parser.parse_args()
    seed(ns.db)
    serve(ns.host, ns.port, ns.db, ns.web_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
