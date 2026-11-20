"""Guard regression tests, including a real Git rename-bypass attempt."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools" / "check_admin_ingress_scope.py"
spec = importlib.util.spec_from_file_location("admin_scope", PATH)
guard = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = guard
spec.loader.exec_module(guard)

def diff(path, added):
    return ("diff --git a/" + path + " b/" + path + "\n"
            "--- a/" + path + "\n+++ b/" + path + "\n"
            "@@ -0,0 +1," + str(len(added)) + " @@\n"
            + "".join("+" + s + "\n" for s in added))

class TestAdminIngressScope(unittest.TestCase):
    def flagged(self, path, added):
        return {f.rule for f in guard.inspect_diff(diff(path, added))}

    def test_whole_upload_cap(self):
        self.assertIn("WHOLE_OBJECT_SIZE_CEILING",
                      self.flagged("hhs_backend/api/admin_upload.py", ["MAX_UPLOAD_BYTES = 16 * 1024 * 1024"]))

    def test_http_413(self):
        self.assertIn("SIZE_REJECTION",
                      self.flagged("hhs_backend/api/admin_upload.py", ["raise HTTPException(status_code=413)"]))

    def test_modality_allowlist(self):
        self.assertIn("MODALITY_ALLOWLIST",
                      self.flagged("hhs_backend/api/admin_hydration.py", ["ALLOWED_MODALITIES = {'text'}"]))

    def test_modality_rejection(self):
        self.assertIn("MODALITY_DENIAL",
                      self.flagged("hhs_backend/api/admin_ingress.py", ["raise ValueError('unsupported modality')"]))

    def test_bounded_transport_chunk_permitted(self):
        self.assertFalse(self.flagged("hhs_backend/api/admin_upload.py", ["MAX_CHUNK_BYTES = 4 * 1024 * 1024"]))

    def test_unrelated_file_unaffected(self):
        self.assertFalse(self.flagged("tools/image_downloader.py", ["MAX_FILE_BYTES = 10"]))

    def test_removed_restriction_unaffected(self):
        old = ("diff --git a/hhs_backend/api/admin_upload.py b/hhs_backend/api/admin_upload.py\n"
               "--- a/hhs_backend/api/admin_upload.py\n+++ b/hhs_backend/api/admin_upload.py\n"
               "@@ -1 +0,0 @@\n-MAX_UPLOAD_BYTES = 16\n")
        self.assertEqual(guard.inspect_diff(old), [])

    def test_real_git_rename_exposed(self):
        with tempfile.TemporaryDirectory() as d:
            def git(*args):
                return subprocess.check_output(["git", "-C", d, *args], text=True).strip()
            git("init", "-q")
            git("config", "user.email", "test@example.invalid")
            git("config", "user.name", "Test")
            folder = Path(d) / "hhs_backend" / "api"
            folder.mkdir(parents=True)
            (folder / "admin_upload.py").write_text("def upload(data):\n    return data\n")
            git("add", ".")
            git("commit", "-qm", "baseline")
            base = git("rev-parse", "HEAD")
            (folder / "admin_upload.py").rename(folder / "admin_knowledge.py")
            (folder / "admin_knowledge.py").write_text("MAX_UPLOAD_BYTES = 16\n")
            git("add", ".")
            git("commit", "-qm", "rename and narrow")
            head = git("rev-parse", "HEAD")
            changed = subprocess.check_output(
                ["git", "-C", d, "diff", "--no-renames", "--unified=0", base + "..." + head], text=True)
            self.assertIn("WHOLE_OBJECT_SIZE_CEILING", {f.rule for f in guard.inspect_diff(changed)})

if __name__ == "__main__":
    unittest.main()
