"""Integration probes for base-owned policy protection using real Git commits."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ".github/workflows/hhs-frozen-layer-trusted-base.yml"
POLICY = (
    "contracts/frozen_layer_registry.v1.json",
    "scripts/check_frozen_layer_preservation.py",
    "scripts/check_frozen_layer_registry.py",
    ".github/workflows/hhs-frozen-layer-source-guard.yml",
    WORKFLOW,
    "tests/test_frozen_layer_trusted_policy_integrity.py",
)
NATIVE = (
    "hhs_runtime/core_sandbox/hhs_general_runtime_layer_v1.py",
    "hhs_runtime/hhs_hash72_signing_layer_v1.py",
)


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def policy_shell():
    """Execute the actual workflow enforcement step, not a duplicate predicate."""
    source = (ROOT / WORKFLOW).read_text(encoding="utf-8")
    match = re.search(
        r"      - name: Enforce base-owned frozen policy\n"
        r"        env:\n(?:          .*\n)+"
        r"        run: \|\n(?P<run>(?:          .*\n|\n)+?)"
        r"(?=      - name: |\Z)",
        source,
    )
    if match is None:
        raise AssertionError("trusted-base enforcement step missing or changed")
    return textwrap.dedent(match.group("run"))


class TrustedPolicyIntegrity(unittest.TestCase):
    def test_every_policy_mutation_is_denied(self):
        shell = policy_shell()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            git(root, "config", "user.name", "HHS CI")
            git(root, "config", "user.email", "ci@example.invalid")
            for path in POLICY:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dest)
            for path in NATIVE:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("native preserved\n", encoding="utf-8")
            git(root, "add", ".")
            git(root, "commit", "-qm", "trusted base")
            base = git(root, "rev-parse", "HEAD")
            env = {**os.environ, "BASE_SHA": base}
            for path in POLICY:
                for change in ("modify", "rename", "delete"):
                    with self.subTest(path=path, change=change):
                        git(root, "reset", "--hard", base)
                        git(root, "clean", "-fd")
                        if change == "modify":
                            with (root / path).open("a", encoding="utf-8") as stream:
                                stream.write("\n# untrusted change\n")
                        else:
                            dest = root / (path + ".renamed")
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            git(root, "mv", path, str(dest.relative_to(root)))
                        if change == "delete":
                            git(root, "rm", "-q", "--", path)
                        git(root, "add", "-A")
                        git(root, "commit", "-qm", "untrusted candidate")
                        head = git(root, "rev-parse", "HEAD")
                        git(root, "reset", "--hard", base)
                        result = subprocess.run(
                            ["bash", "-e", "-o", "pipefail", "-c", shell],
                            cwd=root, env={**env, "HEAD_SHA": head},
                            capture_output=True, text=True,
                        )
                        self.assertEqual(
                            result.returncode, 1,
                            f"{path} {change}: {result.stdout} {result.stderr}",
                        )
                        self.assertIn("FROZEN_POLICY_MODIFICATION:", result.stdout)
                        self.assertIn(path, result.stdout)


    def test_unrelated_newline_filename_is_allowed(self):
        shell = policy_shell()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            git(root, "config", "user.name", "HHS CI")
            git(root, "config", "user.email", "ci@example.invalid")
            for path in POLICY:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, dest)
            for path in NATIVE:
                dest = root / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text("native preserved\n", encoding="utf-8")
            git(root, "add", ".")
            git(root, "commit", "-qm", "trusted base")
            base = git(root, "rev-parse", "HEAD")
            name = "unrelated\nfilename.txt"
            (root / name).write_text("allowed\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "unrelated newline path")
            head = git(root, "rev-parse", "HEAD")
            git(root, "reset", "--hard", base)
            result = subprocess.run(
                ["bash", "-e", "-o", "pipefail", "-c", shell],
                cwd=root, env={**os.environ, "BASE_SHA": base, "HEAD_SHA": head},
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
