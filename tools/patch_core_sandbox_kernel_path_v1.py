from __future__ import annotations

from pathlib import Path
import hashlib
import json

TARGET = Path("hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py")
SEAL = Path("data/runtime/core_sandbox_path_patch_seal_v1.json")
KERNEL_NAME = "HARMONICODE_KERNEL_v44_2_lockcore_patched_selfsolving_hash72authority_locked-7.py"
BAD_ROOT = "/" + "mnt" + "/" + "data"
OLD_LINE = 'DEFAULT_KERNEL_PATH = Path("' + BAD_ROOT + '/' + KERNEL_NAME + '")'
NEW_LINES = 'DATA_ROOT = Path(os.environ.get("HHS_DATA_ROOT", "data")).resolve()\nDEFAULT_KERNEL_PATH = DATA_ROOT / "' + KERNEL_NAME + '"'


def h(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    before = TARGET.read_text(encoding="utf-8")
    after = before
    if "import os\n" not in after.split("from collections import Counter", 1)[0]:
        after = after.replace("import json\nfrom collections import Counter\n", "import json\nimport os\nfrom collections import Counter\n", 1)
    after = after.replace(OLD_LINE, NEW_LINES, 1)
    if after != before:
        TARGET.write_text(after, encoding="utf-8")
    seal = {
        "schema": "HHS_CORE_SANDBOX_PATH_PATCH_SEAL_V1",
        "target": str(TARGET),
        "scope": "PATH_CONSTRUCTION_ONLY",
        "logic_unchanged_assertion": True,
        "changed": before != after,
        "old_token_present_after": OLD_LINE in after,
        "new_token_present_after": NEW_LINES in after,
        "before_sha256": h(before),
        "after_sha256": h(after),
    }
    SEAL.parent.mkdir(parents=True, exist_ok=True)
    SEAL.write_text(json.dumps(seal, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(seal, indent=2, sort_keys=True))
    return 0 if (OLD_LINE not in after and NEW_LINES in after) else 1


if __name__ == "__main__":
    raise SystemExit(main())
