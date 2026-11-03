"""Regression tests for the generated Claude Web package (standard library only)."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build_web_plugin as web


class BuildWebPluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "skills" / web.NAME
        self.plugin = self.root / "plugins" / web.NAME
        self.target = self.plugin / "skills" / web.NAME
        self.marketplace = self.root / ".claude-plugin/marketplace.json"
        self.patch = patch.multiple(
            web, ROOT=self.root, SOURCE=self.source, PLUGIN=self.plugin,
            TARGET=self.target, MARKETPLACE=self.marketplace,
        )
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.write(self.source / "SKILL.md",
                   '---\nname: code-animation-prompts\ndescription: "Create code animations."\n---\n'
                   'Read [the web guide](references/claude-web.md) and [video examples](references/video-examples.md).\n')
        self.write(self.source / "references/claude-web.md", "Use installed files.\n")
        self.write(self.source / "references/video-examples.md", "Links to original videos.\n")
        entries = [{"image": "still.jpg" if i < 193 else ""} for i in range(341)]
        self.write(self.source / "references/catalog.json",
                   json.dumps({"total": 341, "entries": entries}))
        self.write(self.source / "assets/style.md", "A style prompt.\n")
        self.write(self.source / "assets/example.mp4", "large video placeholder")
        self.write(self.source / "__pycache__/junk.pyc", "cache")
        self.write(self.source / ".DS_Store", "finder metadata")
        self.write(self.root / "LICENSE.md", "Original attribution and terms.\n")
        self.write(self.marketplace, json.dumps({
            "name": web.NAME, "owner": {"name": "Test owner"},
            "plugins": [{"name": web.NAME, "source": f"./plugins/{web.NAME}", "strict": True}],
        }))
        self.write(self.plugin / ".claude-plugin/plugin.json", json.dumps({
            "name": web.NAME, "version": "1.0.0", "description": "Test plugin",
            "author": {"name": "Test author"},
        }))
        self.write(self.plugin / "README.md", "Plugin readme.\n")
        self.write(self.plugin / "commands/animate.md", "---\ndescription: Animate.\n---\nUse the skill.\n")
        icon = self.plugin / "assets/icon.png"
        icon.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / "plugins" / web.NAME / "assets/icon.png", icon)

    @staticmethod
    def write(path: Path, text: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_build_excludes_videos_and_caches_and_preserves_bytes(self):
        result = web.build()
        self.assertEqual(result["files"], 10)
        self.assertTrue((self.target / "assets/style.md").is_file())
        self.assertFalse((self.target / "assets/example.mp4").exists())
        self.assertFalse((self.target / "__pycache__").exists())
        self.assertFalse((self.target / ".DS_Store").exists())
        self.assertEqual((self.plugin / "LICENSE.md").read_bytes(),
                         (self.root / "LICENSE.md").read_bytes())
        self.assertEqual(web.check(), result)

    def test_check_detects_drift_without_writing(self):
        web.build()
        generated = self.target / "assets/style.md"
        generated.write_text("unsynced edit", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from source"):
            web.check()
        self.assertEqual(generated.read_text(encoding="utf-8"), "unsynced edit")
        web.build()
        self.assertEqual(generated.read_bytes(), (self.source / "assets/style.md").read_bytes())

    def test_stale_files_require_explicit_prune(self):
        web.build()
        stale = self.target / "assets/old.md"
        self.write(stale, "old generated content")
        with self.assertRaisesRegex(ValueError, "--prune"):
            web.build()
        self.assertTrue(stale.exists())
        web.build(prune=True)
        self.assertFalse(stale.exists())
        web.check()

    def test_web_rejects_dot_source_and_accepts_dot_slash_subdir(self):
        data = json.loads(self.marketplace.read_text(encoding="utf-8"))
        data["plugins"][0]["source"] = "."
        self.write(self.marketplace, json.dumps(data))
        with self.assertRaisesRegex(ValueError, "relative ./plugins"):
            web.validate_manifests()
        data["plugins"][0]["source"] = f"./plugins/{web.NAME}"
        self.write(self.marketplace, json.dumps(data))
        web.validate_manifests()

    def test_symlinks_are_rejected(self):
        web.build()
        link = self.target / "assets/link.md"
        try:
            link.symlink_to(self.source / "assets/style.md")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks are not available on this host")
        with self.assertRaisesRegex(ValueError, "Symlinked"):
            web.check()


if __name__ == "__main__":
    unittest.main()
