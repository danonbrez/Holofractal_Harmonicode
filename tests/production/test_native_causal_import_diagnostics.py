"""Dependency-scoped contract checks for production service-identity import diagnostics."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "tools/diagnose_native_causal_import.py"
WORKFLOW = ROOT / ".github/workflows/digitalocean-production-main.yml"


def test_probe_reports_traceback_and_preserves_nonzero_failure():
    source = PROBE.read_text(encoding="utf-8")
    ast.parse(source)
    assert "traceback.print_exc(file=sys.stderr)" in source
    assert "HHS_NATIVE_CAUSAL_IMPORT_READY=0" in source
    assert "HHS_NATIVE_CAUSAL_IMPORT_READY=1" in source
    assert "sys.exit(0 if verify_imports() else 1)" in source
    assert "pip install" not in source
    assert "subprocess" not in source


def test_workflow_runs_probe_as_hhs_and_keeps_pinned_provisioner():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert '/opt/hhs/venv/bin/python "$APP_ROOT/tools/provision_native_causal_model.py" --install' in workflow
    assert 'runuser -u hhs -- env PYTHONPATH="$APP_ROOT" \\' in workflow
    assert '/opt/hhs/venv/bin/python "$APP_ROOT/tools/diagnose_native_causal_import.py"; then' in workflow
    assert 'echo "Native causal dependencies not importable by hhs service identity"' in workflow


def test_failure_probe_captures_real_traceback_without_fallback(monkeypatch, capsys):
    import builtins
    import importlib.util
    spec = importlib.util.spec_from_file_location("native_causal_import_probe_test", PROBE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_import = builtins.__import__

    def failing_import(name, *args, **kwargs):
        if name == "transformers":
            raise ModuleNotFoundError("synthetic import failure from service environment")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", failing_import)
    assert module.verify_imports() is False
    output = capsys.readouterr()
    assert output.out == ""
    assert "HHS_NATIVE_CAUSAL_IMPORT_READY=0" in output.err
    assert "python_executable=" in output.err
    assert "ModuleNotFoundError: synthetic import failure" in output.err
    assert "HHS_NATIVE_CAUSAL_IMPORT_READY=1" not in output.err
