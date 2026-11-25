import tempfile
import unittest
from pathlib import Path
from fileguard import snapshot, compare, sha256

class FileGuardTests(unittest.TestCase):
    def test_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("before")
            (root / "b.txt").write_text("remove")
            old = snapshot(root)
            (root / "a.txt").write_text("after")
            (root / "b.txt").unlink()
            (root / "c.txt").write_text("add")
            self.assertEqual(compare(old, snapshot(root)), {"added": ["c.txt"], "removed": ["b.txt"], "modified": ["a.txt"]})

    def test_manifest_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "manifest.json"
            manifest.write_text("{}")
            self.assertEqual(snapshot(root, manifest), {})

    def test_known_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "test.txt"
            file.write_bytes(b"abc")
            self.assertEqual(sha256(file), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

if __name__ == "__main__": unittest.main()
