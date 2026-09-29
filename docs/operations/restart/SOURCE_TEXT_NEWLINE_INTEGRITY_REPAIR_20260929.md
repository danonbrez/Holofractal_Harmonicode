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

## Live repair-forward evidence

- PR: #661
- first live source-integrity PR run: 36613196354
- first live run scanned 3,883 source files and reported exactly two hits;
- genuine defect: hhs_backend/server.py had two FastAPI provider setdefault statements joined by a literal backslash+n token;
- false positive: applications/holofractal_harmonizer/src/visual-ide-state.mjs used legitimate nested JavaScript template literals containing newline escapes;
- repair-forward: server.py now contains a physical newline, and the scanner tracks nested JavaScript template literal/expression state;
- regression coverage now includes the nested-template case;
- repair head before this restart-record update: af065e332a85d6d69284180da2396d02377b970e;
- updated source-integrity and inherited consensus workflows were re-queued from that repaired lineage.

Do not revert the server.py physical newline or replace valid newline escapes inside quoted/template-string content.
