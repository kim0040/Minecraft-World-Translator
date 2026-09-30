"""World aliases must not read or translate data outside the selected world."""
from __future__ import annotations

import gzip
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested
from mwt.desktop_entry import _world_inspection
from mwt.layout import detect_write_blockers, discover_region_dirs
from mwt.safety import file_sha256, world_fingerprint


class WorldPathBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pomi-world-boundary-")
        self.root = Path(self.temp.name)
        self.world = self.root / "world"
        self.world.mkdir()
        (self.world / "level.dat").write_bytes(gzip.compress(b"synthetic Java world"))
        self.outside = self.root / "outside.dat"
        self.outside.write_bytes(b"outside synthetic data must not be read")

    def tearDown(self):
        self.temp.cleanup()

    def link(self, source, target):
        try:
            source.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(str(exc))

    def test_external_resource_pack_is_blocked_before_read_with_pack_on_or_off(self):
        self.link(self.world / "resources.zip", self.outside)
        original_open = Path.open

        def guarded_open(path, *args, **kwargs):
            if path.resolve() == self.outside:
                self.fail("external data was opened")
            return original_open(path, *args, **kwargs)

        with patch.object(Path, "open", guarded_open):
            inspection = _world_inspection(self.world)
            self.assertIn("unsafe_path", inspection["writeBlockers"])
            self.assertEqual(inspection["resourcePacks"], [])
            with self.assertRaisesRegex(ValueError, "outside the selected world"):
                world_fingerprint(self.world)
            for enabled in (False, True):
                config = merge_nested(DEFAULT_CONFIG, {
                    "world_dir": str(self.world), "dry_run": True, "inherit_translate_py": False,
                    "report_path": str(self.root / "scan.json"),
                    "resource_pack": {"enabled": enabled, "zip_paths": [str(self.world / "resources.zip")]},
                })
                report = WorldTranslator(config).run()
                self.assertEqual(report["status"], "unsupported")
                self.assertEqual(report.get("provider_requests", 0), 0)
                self.assertEqual(report["candidate_text_count"], 0)

    def test_external_region_or_entity_file_never_enters_collection(self):
        for kind in ("region", "entities"):
            with self.subTest(kind=kind):
                folder = self.world / kind
                folder.mkdir()
                self.link(folder / "r.0.0.mca", self.outside)
                config = merge_nested(DEFAULT_CONFIG, {"world_dir": str(self.world), "dry_run": True})
                translator = WorldTranslator(config)
                with self.assertRaisesRegex(ValueError, "outside the selected world"):
                    translator.iter_region_files()
                self.assertIn("unsafe_path", detect_write_blockers(self.world))
                (folder / "r.0.0.mca").unlink()

    def test_external_directory_is_reported_and_not_discovered(self):
        folder = self.root / "outside-region"
        folder.mkdir()
        (folder / "r.0.0.mca").write_bytes(b"outside region")
        self.link(self.world / "region", folder)
        self.assertIn("unsafe_path", detect_write_blockers(self.world))
        self.assertNotIn("region", discover_region_dirs(self.world))

    def test_external_level_dat_is_not_opened_by_inspection(self):
        (self.world / "level.dat").unlink()
        self.link(self.world / "level.dat", self.outside)
        inspection = _world_inspection(self.world)
        self.assertIn("unsafe_path", inspection["writeBlockers"])
        self.assertIsNone(inspection["dataVersions"][0]["dataVersion"])

    def test_server_plugin_link_does_not_block_or_change_world_fingerprint(self):
        server = self.root / "server"
        server.mkdir()
        self.world.rename(server / "world")
        plugin = self.root / "plugin"
        plugin.mkdir()
        (plugin / "cache.dat").write_bytes(b"cache before")
        self.link(server / "plugins", plugin)
        before = world_fingerprint(server)
        (plugin / "cache.dat").write_bytes(b"cache after")
        self.assertEqual(before, world_fingerprint(server))
        self.assertNotIn("unsafe_path", detect_write_blockers(server))

    def test_regular_world_hash_is_compatible_and_streams_large_files(self):
        contents = b"synthetic block" * 250000
        large = self.world / "large.dat"
        large.write_bytes(contents)
        expected = hashlib.sha256()
        for path in sorted([self.world / "level.dat", large]):
            expected.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
        with patch.object(Path, "read_bytes", side_effect=AssertionError("unbounded file read")):
            self.assertEqual(world_fingerprint(self.world), expected.hexdigest())
            self.assertEqual(file_sha256(large), hashlib.sha256(contents).hexdigest())


if __name__ == "__main__":
    unittest.main()
