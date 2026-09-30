"""Desktop scan preferences survive validation, persistence, extraction, and scan identity."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from nbt import nbt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mc_world_translator as core  # noqa: E402
from mc_world_translator import DEFAULT_CONFIG  # noqa: E402
from mwt import desktop_entry  # noqa: E402
from mwt.desktop_settings import normalize_scan_options  # noqa: E402
from mwt.userdata import load_user_settings, settings_path  # noqa: E402
from tests.test_release_fixtures import compound, nbt_bytes, string, write_region  # noqa: E402


def _synthetic_world(root: Path) -> Path:
    world = root / "synthetic-world"
    world.mkdir(parents=True)
    level = nbt.NBTFile()
    data = nbt.TAG_Compound(name="Data")
    data.tags.append(nbt.TAG_Int(name="DataVersion", value=4189))
    level.tags.append(data)
    level.write_file(filename=str(world / "level.dat"))
    write_region(
        world / "region" / "r.0.0.mca",
        {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)},
    )
    return world


def _settings_set(data_dir: Path, *, body: dict) -> dict:
    replies: list[dict] = []
    previous_emit = desktop_entry.emit
    desktop_entry.emit = replies.append
    try:
        desktop_entry.handle(
            {
                "v": 1,
                "id": "scan-settings",
                "type": "settings.set",
                "payload": {"credentialOwner": "rust", "provider": "openai", "model": "fixture", **body},
            },
            report_dir=data_dir / "reports",
            data_dir=data_dir,
        )
    finally:
        desktop_entry.emit = previous_emit
    assert replies and replies[-1]["type"] == "response.ok"
    return replies[-1]["payload"]["settings"]


def test_disabled_signs_are_not_extracted_and_postscan_keeps_choice(tmp_path: Path) -> None:
    world = _synthetic_world(tmp_path)
    data_dir = tmp_path / "userdata"

    saved = _settings_set(data_dir, body={"worldDir": str(world), "scanOptions": {"translate_signs": False}})
    assert saved["scan_options"] == normalize_scan_options({"translate_signs": False}, defaults=DEFAULT_CONFIG["scan"])

    # A later settings patch without scanOptions merges the stored selection instead of resetting it.
    saved = _settings_set(data_dir, body={"model": "fixture-model-change"})
    assert saved["scan_options"]["translate_signs"] is False

    report = desktop_entry._run_translator(
        world,
        dry_run=True,
        report_path=data_dir / "reports" / "scan.json",
        data_dir=data_dir,
        candidate_limit=200,
    )
    assert report["status"] == "completed"
    assert report["candidate_text_count"] == 0
    assert report["candidate_preview"] == []
    assert load_user_settings(data_dir)["scan_options"]["translate_signs"] is False


def test_scan_option_changes_invalidate_scope_but_model_changes_do_not(tmp_path: Path) -> None:
    data_dir = tmp_path / "userdata"
    initial = desktop_entry._scan_scope_fingerprint(data_dir)

    _settings_set(data_dir, body={"model": "new-model", "batchSize": 5})
    assert desktop_entry._scan_scope_fingerprint(data_dir) == initial

    _settings_set(data_dir, body={"scanOptions": {"translate_signs": False}})
    assert desktop_entry._scan_scope_fingerprint(data_dir) != initial

    changed_lists = normalize_scan_options({"region_dirs": ["region"]}, saved={"translate_signs": False})
    assert changed_lists["translate_signs"] is False
    assert changed_lists["region_dirs"] == ["region"]


def test_zero_temperature_and_retries_reach_core_config(tmp_path: Path) -> None:
    data_dir = tmp_path / "userdata"
    _settings_set(data_dir, body={"temperature": 0, "maxBatchRetries": 0})
    captured: dict = {}

    class CaptureTranslator:
        def __init__(self, config: dict, **_kwargs) -> None:
            captured["config"] = config
            self.occurrences = {}
            self._candidate_order = []

        def run(self) -> dict:
            return {"status": "completed", "candidate_text_count": 0}

    previous_translator = core.WorldTranslator
    core.WorldTranslator = CaptureTranslator
    try:
        desktop_entry._run_translator(
            tmp_path / "synthetic-world",
            dry_run=True,
            report_path=data_dir / "reports" / "scan.json",
            data_dir=data_dir,
        )
    finally:
        core.WorldTranslator = previous_translator

    assert captured["config"]["temperature"] == 0
    assert captured["config"]["runtime"]["max_batch_retries"] == 0


def test_invalid_scan_options_are_rejected_before_any_write(tmp_path: Path) -> None:
    data_dir = tmp_path / "userdata"
    _settings_set(data_dir, body={"scanOptions": {"translate_signs": True}})
    path = settings_path(data_dir)
    before_settings = path.read_bytes()
    before_files = {item.name: item.read_bytes() for item in data_dir.iterdir() if item.is_file()}

    def forbidden_key_write(*_args, **_kwargs):
        raise AssertionError("invalid scan options reached the credential writer")

    from mwt import secrets

    previous_remember_api_key = secrets.remember_api_key
    secrets.remember_api_key = forbidden_key_write
    try:
        invalid_payloads = (
            {"scanOptions": {"translate_signs": "false"}},
            {"scanOptions": {"mystery_category": True}},
            {"scanOptions": {"region_dirs": ["region", 7]}},
            {"scanOptions": {"skip_patterns": ["x" * 257]}},
            {"scan_options": {"translate_signs": False}},
        )
        for invalid in invalid_payloads:
            _expect_value_error(
                lambda: _settings_set(
                    data_dir,
                    body={"credentialOwner": "python", "apiKey": "synthetic-invalid-payload-key", **invalid},
                )
            )
            assert path.read_bytes() == before_settings
            assert {item.name: item.read_bytes() for item in data_dir.iterdir() if item.is_file()} == before_files
    finally:
        secrets.remember_api_key = previous_remember_api_key


def test_coverage_marks_disabled_standard_categories_without_fake_presence(tmp_path: Path) -> None:
    world = tmp_path / "coverage-world"
    world.mkdir(parents=True)
    (world / "level.dat").write_bytes(b"synthetic")
    items = desktop_entry._coverage(
        world,
        False,
        {"translate_signs": False, "translate_books": True, "translate_text_displays": False},
    )
    by_id = {item["id"]: item for item in items}

    assert by_id["regions"]["scanned"] and by_id["entities"]["scanned"]
    assert by_id["standard_signs"]["scanned"] is False
    assert by_id["standard_books"]["scanned"] is True
    assert by_id["standard_text_displays"]["scanned"] is False
    option_rows = [item for item in items if item.get("scopeOption")]
    assert len(option_rows) == 9
    assert all("present" not in item and "count" not in item for item in option_rows)


def _expect_value_error(action) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="pomi-scan-settings-") as temporary:
        root = Path(temporary)
        test_disabled_signs_are_not_extracted_and_postscan_keeps_choice(root / "extract")
        test_scan_option_changes_invalidate_scope_but_model_changes_do_not(root / "fingerprint")
        test_zero_temperature_and_retries_reach_core_config(root / "zero-values")
        test_invalid_scan_options_are_rejected_before_any_write(root / "validation")
        test_coverage_marks_disabled_standard_categories_without_fake_presence(root / "coverage")
    print("PASS desktop scan settings validation, extraction, scope fingerprint, persistence, coverage")


if __name__ == "__main__":
    main()
