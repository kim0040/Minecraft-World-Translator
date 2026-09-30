"""Resource-pack backup path preflight runs before any provider request."""

from __future__ import annotations

import gzip
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mc_world_translator as core  # noqa: E402
from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested  # noqa: E402
from mwt.safety import BackupError, BackupSet  # noqa: E402


class ProviderSpy:
    calls: list[str] = []
    request_count = 0
    usage: dict = {}

    def __init__(self, _config: dict) -> None:
        self.model_info = {}

    @classmethod
    def reset_counters(cls) -> None:
        cls.calls = []
        cls.request_count = 0
        cls.usage = {}

    def try_refresh_text_models(self) -> None:
        type(self).calls.append("refresh")

    def translate_mapping(self, values: dict, **_kwargs) -> dict[str, str]:
        type(self).calls.append("translate")
        type(self).request_count += 1
        return {key: f"translated:{value}" for key, value in values.items()}


def _world(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "level.dat").write_bytes(gzip.compress(b"synthetic Java world"))
    return path


def _resource_pack(path: Path) -> bytes:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "assets/demo/lang/en_us.json",
            json.dumps({"demo.greeting": "Hello pack"}),
        )
    return path.read_bytes()


def _config(world: Path, pack: Path, report: Path, *, dry_run: bool = False) -> dict:
    return merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": dry_run,
            "report_path": str(report),
            "backup": True,
            "inherit_translate_py": False,
            "resource_pack": {
                "enabled": True,
                "zip_paths": [str(pack)],
                "source_lang_files": ["en_us.json"],
                "target_lang_file": "ko_kr.json",
                "skip_if_target_exists": False,
            },
            "runtime": {
                "checkpoint_enabled": False,
                "checkpoint_path": str(report.with_suffix(".checkpoint.json")),
                "backup_store": str(report.parent / "backup-store"),
                "max_batch_retries": 1,
                "concurrency": 1,
            },
            "api": {
                "provider": "openai",
                "api_key": "synthetic-test-key",
                "model": "synthetic-test-model",
                "base_url": "https://example.invalid/v1",
            },
        },
    )


class ExternalPackBackupTests(unittest.TestCase):
    def test_selected_zip_and_world_restore_with_recovery(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pomi-external-backup-") as temporary:
            root = Path(temporary)
            world = _world(root / "world")
            pack = root / "packs" / "selected.zip"
            original_pack = _resource_pack(pack)
            original_world = (world / "level.dat").read_bytes()
            backup = BackupSet.new(world, store=root / "store", external_files=[pack])
            backup.add(world / "level.dat")
            backup.add(pack)
            backup.publish_latest()
            pack.write_bytes(b"translated pack")
            (world / "level.dat").write_bytes(b"translated world")
            backup.mark_written([pack, world / "level.dat"])
            backup.verify()
            opened = BackupSet.open_existing(world, backup.backup_id, root / "store", external_files=[pack])
            recovery_id = opened.restore()
            self.assertEqual(pack.read_bytes(), original_pack)
            self.assertEqual((world / "level.dat").read_bytes(), original_world)
            recovery = BackupSet.find(world, recovery_id, [root / "store"], external_files=[pack])
            recovery.restore()
            self.assertEqual(pack.read_bytes(), b"translated pack")
            self.assertEqual((world / "level.dat").read_bytes(), b"translated world")

    def test_manifest_cannot_authorize_unselected_or_missing_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pomi-external-refusal-") as temporary:
            root = Path(temporary)
            world = _world(root / "world")
            pack = root / "packs" / "selected.zip"
            _resource_pack(pack)
            backup = BackupSet.new(world, store=root / "store", external_files=[pack])
            backup.add(world / "level.dat")
            backup.add(pack)
            backup.publish_latest()
            (world / "level.dat").write_bytes(b"current world")
            unselected = BackupSet.find(world, backup.backup_id, [root / "store"])
            with self.assertRaisesRegex(BackupError, "not explicitly selected"):
                unselected.restore()
            self.assertEqual((world / "level.dat").read_bytes(), b"current world")
            pack.unlink()
            with self.assertRaisesRegex(BackupError, "unavailable"):
                backup.restore()
            self.assertFalse(pack.exists())
            self.assertEqual((world / "level.dat").read_bytes(), b"current world")
            self.assertEqual(len(list((root / "store").glob("*-recovery"))), 0)

    def test_replaced_parent_or_symlink_refused_before_world_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pomi-external-root-") as temporary:
            root = Path(temporary)
            world = _world(root / "world")
            pack = root / "packs" / "selected.zip"
            _resource_pack(pack)
            backup = BackupSet.new(world, store=root / "store", external_files=[pack])
            backup.add(world / "level.dat")
            backup.add(pack)
            backup.publish_latest()
            (world / "level.dat").write_bytes(b"current world")
            pack.parent.rename(root / "original-packs")
            _resource_pack(pack)
            reopened = BackupSet.find(world, backup.backup_id, [root / "store"], external_files=[pack])
            with self.assertRaisesRegex(BackupError, "unavailable"):
                reopened.restore()
            self.assertEqual((world / "level.dat").read_bytes(), b"current world")
            pack.unlink()
            try:
                pack.symlink_to(root / "original-packs" / "selected.zip")
            except (OSError, NotImplementedError) as exc:
                self.skipTest(f"symlink creation is unavailable: {exc}")
            with self.assertRaisesRegex(BackupError, "unavailable"):
                backup.restore()
            self.assertEqual((world / "level.dat").read_bytes(), b"current world")


class ResourcePackPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pomi-pack-preflight-")
        self.root = Path(self.temporary.name)
        # The provider client is created by WorldTranslator.__init__, before run().
        self.provider_patch = patch.object(core, "LLMProviderClient", ProviderSpy)
        self.provider_patch.start()

    def tearDown(self) -> None:
        self.provider_patch.stop()
        self.temporary.cleanup()

    def test_explicit_external_zip_translation_and_verified_restore(self) -> None:
        world = _world(self.root / "world")
        pack = self.root / "external" / "selected.zip"
        original = _resource_pack(pack)
        config = _config(world, pack, self.root / "report.json")
        config["runtime"]["authorized_external_pack_paths"] = [str(pack)]
        report = WorldTranslator(config).run()
        self.assertEqual(report["status"], "completed")
        self.assertEqual(report["provider_requests"], 1)
        translated = pack.read_bytes()
        self.assertNotEqual(translated, original)
        with zipfile.ZipFile(pack) as archive:
            self.assertEqual(json.loads(archive.read("assets/demo/lang/ko_kr.json")),
                             {"demo.greeting": "translated:Hello pack"})
        backup = BackupSet.find(world, report["backup_set_id"], [self.root / "backup-store"], external_files=[pack])
        recovery_id = backup.restore()
        self.assertEqual(pack.read_bytes(), original)
        recovery = BackupSet.find(world, recovery_id, [self.root / "backup-store"], external_files=[pack])
        recovery.restore()
        self.assertEqual(pack.read_bytes(), translated)

    def test_missing_explicit_zip_fails_before_any_provider_request(self) -> None:
        world = _world(self.root / "world")
        pack = self.root / "external" / "missing.zip"
        config = _config(world, pack, self.root / "report.json")
        config["runtime"]["authorized_external_pack_paths"] = [str(pack)]
        with self.assertRaisesRegex(BackupError, "existing regular ZIP"):
            WorldTranslator(config).run()
        self.assertEqual(ProviderSpy.calls, [])

    def test_multiple_selected_zips_translate_and_restore_together(self) -> None:
        world = _world(self.root / "world")
        packs = [self.root / "external" / f"pack-{index}.zip" for index in range(2)]
        originals = [_resource_pack(pack) for pack in packs]
        config = _config(world, packs[0], self.root / "report.json")
        config["resource_pack"]["zip_paths"] = [str(pack) for pack in packs]
        config["runtime"]["authorized_external_pack_paths"] = [str(pack) for pack in packs]
        result = WorldTranslator(config).run()
        self.assertEqual(result["status"], "completed")
        for pack, original in zip(packs, originals):
            self.assertNotEqual(pack.read_bytes(), original)
        backup = BackupSet.find(world, result["backup_set_id"], [self.root / "backup-store"], external_files=packs)
        backup.restore()
        self.assertEqual([pack.read_bytes() for pack in packs], originals)

    def test_pack_change_during_translation_stops_all_writes(self) -> None:
        world = _world(self.root / "world")
        pack = self.root / "external" / "selected.zip"
        _resource_pack(pack)
        original_world = (world / "level.dat").read_bytes()
        config = _config(world, pack, self.root / "report.json")
        config["runtime"]["authorized_external_pack_paths"] = [str(pack)]
        changed = b""
        def change_at_write(event):
            nonlocal changed
            if event.get("event") == "phase_start" and event.get("phase") == "write":
                with zipfile.ZipFile(pack, "a") as archive:
                    archive.comment = b"user edited during API request"
                changed = pack.read_bytes()
        result = WorldTranslator(config, progress_callback=change_at_write).run()
        self.assertEqual(result["status"], "invalidated")
        self.assertTrue(result["errors"])
        self.assertEqual(result["changed_file_count"], 0)
        self.assertEqual(pack.read_bytes(), changed)
        self.assertEqual((world / "level.dat").read_bytes(), original_world)

    def test_external_pack_is_rejected_before_provider_and_kept_byte_identical(self) -> None:
        world = _world(self.root / "world")
        external_pack = self.root / "external" / "resource-pack.zip"
        original = _resource_pack(external_pack)
        translator = WorldTranslator(
            _config(world, external_pack, self.root / "report.json")
        )

        with patch.object(core, "LLMProviderClient", ProviderSpy):
            with self.assertRaisesRegex(ValueError, "outside the selected world"):
                translator.run()

        self.assertEqual(ProviderSpy.calls, [])
        self.assertEqual(external_pack.read_bytes(), original)

    def test_symlink_resolved_outside_world_is_rejected(self) -> None:
        world = _world(self.root / "world")
        external_pack = self.root / "external" / "resource-pack.zip"
        original = _resource_pack(external_pack)
        linked_pack = world / "linked-resource-pack.zip"
        try:
            linked_pack.symlink_to(external_pack)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink creation is unavailable: {exc}")

        translator = WorldTranslator(
            _config(world, linked_pack, self.root / "report.json")
        )
        with patch.object(core, "LLMProviderClient", ProviderSpy):
            with self.assertRaisesRegex(ValueError, "outside the selected world"):
                translator.run()

        self.assertEqual(ProviderSpy.calls, [])
        self.assertEqual(external_pack.read_bytes(), original)

    def test_dry_run_can_scan_external_pack_without_provider_requests(self) -> None:
        world = _world(self.root / "world")
        external_pack = self.root / "external" / "resource-pack.zip"
        original = _resource_pack(external_pack)
        translator = WorldTranslator(
            _config(world, external_pack, self.root / "report.json", dry_run=True)
        )

        with patch.object(core, "LLMProviderClient", ProviderSpy):
            report = translator.run()

        self.assertEqual(report["status"], "completed")
        self.assertEqual(report["candidate_text_count"], 1)
        self.assertEqual(ProviderSpy.calls, [])
        self.assertEqual(external_pack.read_bytes(), original)

    def test_inside_world_pack_runs_and_is_backed_up(self) -> None:
        world = _world(self.root / "world")
        pack = world / "resources.zip"
        _resource_pack(pack)
        translator = WorldTranslator(
            _config(world, pack, self.root / "report.json")
        )

        with patch.object(core, "LLMProviderClient", ProviderSpy):
            report = translator.run()

        self.assertEqual(report["status"], "completed")
        self.assertEqual(ProviderSpy.calls, ["refresh", "translate"])
        self.assertEqual(report["provider_requests"], 1)
        self.assertTrue(report["backup_set_id"])
        with zipfile.ZipFile(pack) as archive:
            translated = json.loads(archive.read("assets/demo/lang/ko_kr.json"))
        self.assertEqual(translated["demo.greeting"], "translated:Hello pack")

    def test_existing_target_skip_matches_scan_and_write_without_translation(self) -> None:
        world = _world(self.root / "world")
        pack = world / "resources.zip"
        _resource_pack(pack)
        with zipfile.ZipFile(pack, "a") as archive:
            archive.writestr("assets/demo/lang/ko_kr.json", '{"demo.greeting":"Existing text"}')
        original = pack.read_bytes()
        for dry_run in (True, False):
            config = _config(world, pack, self.root / "report.json", dry_run=dry_run)
            config["resource_pack"]["skip_if_target_exists"] = True
            report = WorldTranslator(config).run()
            self.assertEqual(report["candidate_text_count"], 0)
            self.assertEqual(report["provider_requests"], 0)
            self.assertNotIn("translate", ProviderSpy.calls)
            self.assertEqual(pack.read_bytes(), original)

    def test_invalid_zip_scan_reports_partial_and_the_failure(self) -> None:
        world = _world(self.root / "world")
        pack = world / "resources.zip"
        pack.write_bytes(b"invalid ZIP fixture")
        report = WorldTranslator(_config(world, pack, self.root / "report.json", dry_run=True)).run()
        self.assertEqual(report["status"], "partial")
        self.assertTrue(report["errors"])
        self.assertEqual(pack.read_bytes(), b"invalid ZIP fixture")


if __name__ == "__main__":
    unittest.main()
