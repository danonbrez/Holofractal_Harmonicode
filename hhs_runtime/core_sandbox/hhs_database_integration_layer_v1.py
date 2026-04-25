"""
Core Sandbox Database Integration V1
===================================

Simple deterministic JSON persistence layer.
"""

import json
from pathlib import Path
from typing import Any, Dict


class HHSDatabase:
    def __init__(self, path: str):
        self.path = Path(path)

    def save(self, data: Dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2))

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text())
