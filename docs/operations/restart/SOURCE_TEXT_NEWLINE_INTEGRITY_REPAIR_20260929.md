# Source-text newline integrity repair — 2026-09-29

## Repository state

- repository: danonbrez/Holofractal_Harmonicode
- base main: 9cc8f89620183a90f9e269968ef75ee7476adeb8
- branch: agent/source-text-newline-integrity-20260929
- merge target: main
- authoritative-main verification: pending until integration

## Repeated defect class

Repository history records the same edit-format failure in independent Python, TypeScript, and C/C++ changes: a literal backslash+n byte pair was written where a physical newline was required. The malformed source then failed compilation or frontend build after the commit already existed.

The guard deliberately does not reject forward-slash+n data globally. Hash72 values, routes such as /novel/status, and formulas such as k/n can legitimately contain those bytes.

## Repair

- add hhs_runtime/hhs_source_text_integrity_v1.py;
- reject literal escaped-newline tokens that occur outside source strings, comments, and JavaScript regular-expression literals;
- scan Python, JavaScript/TypeScript, and C/C++ source surfaces;
- run the scan first inside hhs_commit_acceptance_gate_v1;
- retain local pre-commit enforcement through the existing acceptance-gate hook;
- add a lightweight push + pull-request workflow so GitHub/API-authored commits are checked even when no local hook runs;
- add regressions for the historical Python, TypeScript, and C/C++ shapes and negative tests for legitimate escapes and /n data.

## Validation

Completed before repository write:

- Python syntax compilation of the new scanner and regression module;
- synthetic pytest execution: 7 passed.

Required after repository write:

- python -m hhs_runtime.hhs_source_text_integrity_v1
- python -m pytest -q tests/test_hhs_source_text_integrity_v1.py
- pull-request HHS Source Text Integrity workflow
- inherited HHS Consensus Gate

## Restart

If interrupted, resume from the branch tip. Inspect the dedicated source-text-integrity workflow first. Repair any reported path/line/column at the producer; do not blanket-replace backslash+n inside quoted strings or forward-slash+n data.
