#!/usr/bin/env python3
"""Fail-closed pinned causal import check under the actual hhs service identity.

Reports import provenance on failure without printing tokens, environment
contents, Python sys.path, or model payload. No installation or fallbacks.
"""
from __future__ import annotations

import importlib.metadata
import os
from pathlib import Path
import sys
import traceback


def _package_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "NOT_INSTALLED"


def verify_imports() -> bool:
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        import torch
        assert AutoTokenizer is not None and AutoModelForCausalLM is not None
        assert torch is not None
    except Exception:
        print("HHS_NATIVE_CAUSAL_IMPORT_READY=0", file=sys.stderr)
        print(f"python_executable={sys.executable}", file=sys.stderr)
        print(f"effective_uid={os.geteuid()}", file=sys.stderr)
        for name in ("transformers", "torch", "tokenizers", "huggingface-hub", "numpy"):
            print(f"installed_{name}={_package_version(name)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False
    print("HHS_NATIVE_CAUSAL_IMPORT_READY=1")
    return True


if __name__ == "__main__":
    sys.exit(0 if verify_imports() else 1)
