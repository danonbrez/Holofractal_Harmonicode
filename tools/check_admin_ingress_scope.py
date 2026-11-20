#!/usr/bin/env python3
"""Additive heuristic guard: no unauthorized narrowing of admin knowledge ingress."""
from __future__ import annotations
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass

SOURCE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx", ".c", ".cc", ".cpp", ".h", ".hpp")
SCOPE_TERMS = ("admin", "knowledge", "hydration", "pass174", "pass194", "vector", "upload", "ingress")
RULES = (
    ("WHOLE_OBJECT_SIZE_CEILING", re.compile(r"\b(?:MAX_(?:UPLOAD|FILE|PAYLOAD|DOCUMENT|SOURCE)_?(?:SIZE|BYTES)|(?:UPLOAD|FILE|PAYLOAD|DOCUMENT|SOURCE)_MAX_(?:SIZE|BYTES)|MAX_CONTENT_LENGTH)\b", re.I)),
    ("SIZE_REJECTION", re.compile(r"(?:HTTP_?413|status_code\s*=\s*413|RequestEntityTooLarge|PayloadTooLarge|(?:raise|reject|deny|throw).{0,100}(?:file.?size|upload.?size|payload.?size|too.?large))", re.I)),
    ("MODALITY_DENIAL", re.compile(r"(?:(?:unsupported|invalid|unknown|disallowed|forbidden)_(?:modality|file_?type|mime_?type)|(?:raise|reject|deny|throw).{0,100}(?:unsupported modality|file type not allowed|modality not allowed))", re.I)),
    ("MODALITY_ALLOWLIST", re.compile(r"\b(?:ALLOWED|SUPPORTED|ACCEPTED)_(?:MODALITIES|MIME_TYPES|FILE_TYPES|EXTENSIONS)\b", re.I)),
)

@dataclass(frozen=True)
class Finding:
    path: str
    new_line: int
    rule: str
    excerpt: str

def in_scope(path: str) -> bool:
    p = path.lower()
    return p.endswith(SOURCE_SUFFIXES) and any(term in p for term in SCOPE_TERMS)

def inspect_diff(diff: str) -> list[Finding]:
    findings = []
    path = ""
    new_line = 0
    hunk = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        m = hunk.match(line)
        if m:
            new_line = int(m.group(1))
            continue
        if line.startswith("+") and not line.startswith("+++"):
            value = line[1:]
            if in_scope(path) and not value.lstrip().startswith(("#", "//", "*", "/*", '"""')):
                for rule, pattern in RULES:
                    if pattern.search(value):
                        findings.append(Finding(path, new_line, rule, value.strip()[:180]))
            new_line += 1
        elif line.startswith(" "):
            new_line += 1
    return findings

def git_diff(base: str, head: str) -> str:
    return subprocess.check_output(
        ["git", "diff", "--no-ext-diff", "--no-renames", "--unified=0",
         "--diff-filter=ACMRT", f"{base}...{head}", "--"], text=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--diff-file")
    args = parser.parse_args(argv)
    if args.diff_file:
        with open(args.diff_file, encoding="utf-8") as f:
            diff = f.read()
    else:
        if not args.base:
            parser.error("--base required unless --diff-file is set")
        diff = git_diff(args.base, args.head)
    findings = inspect_diff(diff)
    for f in findings:
        print(f"::error file={f.path},line={f.new_line},title={f.rule}::{f.excerpt}")
    if findings:
        print("HHS_ADMIN_INGRESS_SCOPE_REVIEW_REQUIRED")
        return 1
    print("HHS_ADMIN_INGRESS_SCOPE_DIFF_GUARD=PASS (heuristic only)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
