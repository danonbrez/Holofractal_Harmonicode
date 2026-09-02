#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from hhs_runtime.pass179.capture import capture_scene_png
from hhs_runtime.pass179.golden import lattice_run_scene, motion_5184_scene
from hhs_runtime.pass179.runtime import PASS179_GRAPHICS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scene", choices=["lattice-run", "motion-5184"])
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    scene = lattice_run_scene() if args.scene == "lattice-run" else motion_5184_scene()
    PASS179_GRAPHICS.commit_scene(scene)
    print(capture_scene_png(PASS179_GRAPHICS, scene.scene_id, args.destination))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
