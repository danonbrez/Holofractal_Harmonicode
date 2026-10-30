"""Real Git rename regression for every protected file and available gate."""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROTECTED = (
    "hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py",
    "hhs_runtime/hhs_hash72_signing_layer_v1.py",
)

def git(cwd, *args):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()

class RenameBypassRegression(unittest.TestCase):
    def test_each_protected_rename_is_rejected_by_both_available_gates(self):
        guards = [ROOT / "scripts/check_frozen_layer_preservation.py"]
        registry_guard = ROOT / "scripts/check_frozen_layer_registry.py"
        if registry_guard.exists():
            guards.append(registry_guard)
        with tempfile.TemporaryDirectory() as directory:
            cwd = pathlib.Path(directory)
            git(cwd, "init", "-q")
            git(cwd, "config", "user.name", "HHS CI")
            git(cwd, "config", "user.email", "ci@example.invalid")
            for path in PROTECTED:
                location = cwd / path
                location.parent.mkdir(parents=True, exist_ok=True)
                location.write_text(("same canonical contents\\n" * 20), encoding="utf-8")
            registry = ROOT / "contracts/frozen_layer_registry.v1.json"
            if registry.exists():
                target = cwd / "contracts/frozen_layer_registry.v1.json"
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(registry, target)
            git(cwd, "add", ".")
            git(cwd, "commit", "-qm", "base")
            base = git(cwd, "rev-parse", "HEAD")
            for protected_path in PROTECTED:
                with self.subTest(protected_path=protected_path):
                    git(cwd, "reset", "--hard", base)
                    git(cwd, "clean", "-fd")
                    renamed = protected_path + ".renamed"
                    git(cwd, "mv", protected_path, renamed)
                    git(cwd, "commit", "-qam", "rename protected")
                    head = git(cwd, "rev-parse", "HEAD")
                    for guard in guards:
                        with self.subTest(guard=guard.name):
                            command = [sys.executable, str(guard)]
                            if guard.name == "check_frozen_layer_preservation.py":
                                command += ["--base", base, "--head", head]
                            else:
                                command += [base, head]
                            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
                            self.assertEqual(result.returncode, 1,
                                msg=f"{guard.name} missed {protected_path}: {result.stdout} {result.stderr}")
                            self.assertIn(protected_path, result.stdout)

if __name__ == "__main__":
    unittest.main()
