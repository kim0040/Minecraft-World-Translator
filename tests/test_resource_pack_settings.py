"""Desktop resource-pack locale preferences validate, persist and reach the core."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mc_world_translator as core  # noqa: E402
from mwt import desktop_entry  # noqa: E402
from mwt.desktop_settings import (  # noqa: E402
    DEFAULT_RESOURCE_PACK_OPTIONS,
    normalize_resource_pack_options,
)
from mwt.userdata import load_user_settings, settings_path  # noqa: E402


def _settings_set(data_dir: Path, **payload: object) -> dict:
    replies: list[dict] = []
    with patch.object(desktop_entry, "emit", replies.append):
        desktop_entry.handle(
            {
                "v": 1,
                "id": "resource-pack-settings",
                "type": "settings.set",
                "payload": {"credentialOwner": "rust", **payload},
            },
            report_dir=data_dir / "reports",
            data_dir=data_dir,
        )
    if not replies or replies[-1]["type"] != "response.ok":
        raise AssertionError("settings.set did not return response.ok")
    return replies[-1]["payload"]["settings"]


class ResourcePackSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="pomi-resource-pack-settings-")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_defaults_patch_round_trip_and_bootstrap(self) -> None:
        data_dir = self.root / "userdata"
        self.assertEqual(normalize_resource_pack_options(), DEFAULT_RESOURCE_PACK_OPTIONS)

        configured = {
            "source_lang_files": ["en_us.json", "ja_jp.json"],
            "target_lang_file": "fr_fr.json",
            "skip_if_target_exists": True,
        }
        saved = _settings_set(data_dir, resourcePackOptions=configured)
        self.assertEqual(saved["resource_pack_options"], configured)

        # An unrelated update keeps options already saved on disk.
        saved = _settings_set(data_dir, model="synthetic-model")
        self.assertEqual(saved["resource_pack_options"], configured)
        self.assertEqual(
            desktop_entry._settings_payload(data_dir, check_keyring=False)["settings"]["resource_pack_options"],
            configured,
        )
        self.assertEqual(
            normalize_resource_pack_options(
                {"target_lang_file": "de_de.json"}, saved=configured
            ),
            {
                "source_lang_files": ["en_us.json", "ja_jp.json"],
                "target_lang_file": "de_de.json",
                "skip_if_target_exists": True,
            },
        )

        bootstrap = desktop_entry._bootstrap_payload(
            self.root / "fresh-userdata", check_keyring=False
        )
        self.assertEqual(
            bootstrap["settings"]["resource_pack_options"], DEFAULT_RESOURCE_PACK_OPTIONS
        )

    def test_invalid_options_are_atomic_and_checked_before_credential_write(self) -> None:
        data_dir = self.root / "userdata"
        _settings_set(data_dir, model="baseline")
        path = settings_path(data_dir)
        before = path.read_bytes()
        files_before = {item.name: item.read_bytes() for item in data_dir.iterdir() if item.is_file()}

        def forbidden_credential_write(*_args, **_kwargs) -> None:
            raise AssertionError("invalid resource-pack settings reached the credential writer")

        invalid_options = (
            {"unknown": True},
            {"source_lang_files": [f"lang_{index}.json" for index in range(17)]},
            {"source_lang_files": ["../en_us.json"]},
            {"source_lang_files": ["folder/en_us.json"]},
            {"source_lang_files": ["en_us.json", "en_us.json"]},
            {"source_lang_files": ["éé.json"]},
            {"source_lang_files": ["a" * 61 + ".json"]},
            {"source_lang_files": ["en..json"]},
            {"target_lang_file": "ko_kr.json", "source_lang_files": ["ko_kr.json"]},
            {"skip_if_target_exists": 1},
            {"source_lang_files": ["en_us.json", 2]},
        )
        from mwt import secrets

        with patch.object(secrets, "remember_api_key", forbidden_credential_write):
            for options in invalid_options:
                with self.subTest(options=options):
                    with self.assertRaises(ValueError):
                        desktop_entry.handle(
                            {
                                "v": 1,
                                "id": "invalid-resource-pack-settings",
                                "type": "settings.set",
                                "payload": {
                                    "credentialOwner": "python",
                                    "provider": "synthetic-provider",
                                    "model": "should-not-be-saved",
                                    "apiKey": "synthetic-invalid-test-key",
                                    "resourcePackOptions": options,
                                },
                            },
                            report_dir=data_dir / "reports",
                            data_dir=data_dir,
                        )
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual(
                        {item.name: item.read_bytes() for item in data_dir.iterdir() if item.is_file()},
                        files_before,
                    )

    def test_pack_options_change_both_fingerprints_but_model_keeps_scan_scope(self) -> None:
        data_dir = self.root / "userdata"
        scope_before = desktop_entry._scan_scope_fingerprint(data_dir)
        settings_before = desktop_entry._settings_fingerprint(data_dir)

        _settings_set(data_dir, model="synthetic-model")
        scope_after_model = desktop_entry._scan_scope_fingerprint(data_dir)
        self.assertEqual(scope_after_model, scope_before)
        settings_after_model = desktop_entry._settings_fingerprint(data_dir)
        self.assertNotEqual(settings_after_model, settings_before)

        _settings_set(
            data_dir,
            resourcePackOptions={
                "source_lang_files": ["en_us.json"],
                "target_lang_file": "ko_kr.json",
                "skip_if_target_exists": True,
            },
        )
        self.assertNotEqual(desktop_entry._scan_scope_fingerprint(data_dir), scope_before)
        self.assertNotEqual(
            desktop_entry._settings_fingerprint(data_dir),
            settings_after_model,
        )

    def test_run_passes_saved_resource_pack_options_to_core_translator(self) -> None:
        data_dir = self.root / "userdata"
        options = {
            "source_lang_files": ["en_us.json", "ja_jp.json"],
            "target_lang_file": "fr_fr.json",
            "skip_if_target_exists": True,
        }
        _settings_set(data_dir, resourcePackEnabled=True, resourcePackOptions=options)
        captured: dict = {}

        class CaptureTranslator:
            def __init__(self, config: dict, **_kwargs) -> None:
                captured["config"] = config

            def run(self) -> dict:
                return {"status": "completed", "candidate_text_count": 0}

        with (
            patch.object(core, "WorldTranslator", CaptureTranslator),
            patch.object(
                desktop_entry,
                "_world_inspection",
                return_value={"resourcePacks": ["/synthetic/world/resources.zip"]},
            ),
        ):
            desktop_entry._run_translator(
                self.root / "synthetic-world",
                dry_run=True,
                report_path=data_dir / "reports" / "scan.json",
                data_dir=data_dir,
            )

        self.assertEqual(captured["config"]["resource_pack"]["enabled"], True)
        self.assertEqual(captured["config"]["resource_pack"]["source_lang_files"], options["source_lang_files"])
        self.assertEqual(captured["config"]["resource_pack"]["target_lang_file"], options["target_lang_file"])
        self.assertEqual(
            captured["config"]["resource_pack"]["skip_if_target_exists"],
            options["skip_if_target_exists"],
        )
        self.assertEqual(load_user_settings(data_dir)["resource_pack_options"], options)


if __name__ == "__main__":
    unittest.main()
