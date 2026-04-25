# HHS General Programming Environment

Codex-ready repository scaffold for the Holofractal Harmonicode / HHS general programming environment.

This repo is intended to hold the full HHS runtime stack:

- authoritative kernel + Hash72 authority
- audited runner
- receipt/replay verifier
- state layer
- symbolic and macro algebra terminals
- GUI macro bootstrap
- input bridge
- physics observation adapter
- physics evolution operator
- smoke/regression tests

## Current handoff status

The full project bundle was packaged in ChatGPT as:

- `hhs-general-programming-environment.zip`
- `hhs-general-programming-environment.tar.gz`

To finish repository hydration, upload or extract that bundle into this repo root. The Codex configuration files in this repo tell Codex how to work once the source files are present.

## Expected layout

```text
hhs_runtime/
examples/
demo_reports/
docs/
tests/
scripts/
README.md
AGENTS.md
pyproject.toml
requirements.txt
```

## Local setup

```bash
python -m pip install -r requirements.txt
python hhs_runtime/hhs_runtime_smoke_tests_v1.py
python hhs_runtime/hhs_regression_suite_v1.py
python hhs_runtime/hhs_v1_bundle_runner.py
```

## Codex setup

1. Connect this GitHub repo in Codex.
2. Set setup command:

```bash
python -m pip install -r requirements.txt
```

3. Set test command:

```bash
python hhs_runtime/hhs_runtime_smoke_tests_v1.py && python hhs_runtime/hhs_regression_suite_v1.py
```

Codex cloud uses a sandbox with the repository preloaded, so the actual source files need to be committed to this repo before assigning implementation tasks.
