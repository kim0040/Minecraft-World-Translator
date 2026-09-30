"""AST-only, public-field legacy settings import contracts."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mwt.desktop_legacy_import import MAX_SOURCE_BYTES, parse_legacy_settings


ERROR = "Invalid legacy translate.py settings"


def _invalid(source: object) -> None:
    try:
        parse_legacy_settings(source)
    except ValueError as exc:
        assert str(exc) == ERROR
    else:
        raise AssertionError("invalid legacy settings were accepted")


def test_public_literal_assignments_and_shape() -> None:
    parsed = parse_legacy_settings(
        "BASE_URL: str = 'https://example.invalid/v1'\n"
        "MODEL = 'fixture-model'\n"
        "SYSTEM_PROMPT = '''Keep names\nand formatting.'''\n"
        "API_KEY = 'synthetic-secret'\n"
        "WORLD_DIR = '/private/world'\n"
        "CHECKPOINT_PATH = '/private/checkpoint.json'\n"
    )
    assert parsed == {
        "api": {
            "provider": "custom",
            "wire_format": "openai",
            "base_url": "https://example.invalid/v1",
            "model": "fixture-model",
        },
        "prompt": {"custom_system_prompt": "Keep names\nand formatting."},
    }
    serialized = repr(parsed)
    for forbidden in ("API_KEY", "api_key", "synthetic-secret", "WORLD_DIR", "/private/world", "CHECKPOINT_PATH"):
        assert forbidden not in serialized


def test_model_only_does_not_invent_provider() -> None:
    assert parse_legacy_settings("MODEL = 'fixture-model'\n") == {
        "api": {"model": "fixture-model"}
    }


def test_last_literal_assignment_wins_and_annotations_are_supported() -> None:
    parsed = parse_legacy_settings(
        "MODEL = 'first'\n"
        "MODEL: str = 'last'\n"
        "BASE_URL = 'https://first.invalid/v1'\n"
        "BASE_URL: str = 'http://localhost:8080/v1'\n"
    )
    assert parsed["api"] == {
        "provider": "custom",
        "wire_format": "openai",
        "base_url": "http://localhost:8080/v1",
        "model": "last",
    }


def test_nested_assignments_and_nonpublic_assignments_are_ignored() -> None:
    parsed = parse_legacy_settings(
        "MODEL = 'top-level'\n"
        "if True:\n"
        "    MODEL = build_model()\n"
        "    BASE_URL = 'https://nested.invalid/v1'\n"
        "API_KEY = read_secret()\n"
        "WORLD_DIR = choose_world()\n"
    )
    assert parsed == {"api": {"model": "top-level"}}


def test_python_code_is_parsed_but_never_executed() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        marker = Path(temp_dir) / "executed.txt"
        source = (
            f"__import__('pathlib').Path({str(marker)!r}).write_text('executed')\n"
            "MODEL = 'safe-model'\n"
        )
        assert parse_legacy_settings(source) == {"api": {"model": "safe-model"}}
        assert not marker.exists()

        dynamic = f"MODEL = __import__('pathlib').Path({str(marker)!r}).write_text('executed')\n"
        _invalid(dynamic)
        assert not marker.exists()


def test_recognized_dynamic_or_chained_assignments_fail_generically() -> None:
    for source in (
        "MODEL = make_model('secret-value')\n",
        "MODEL = BASE_URL = 'https://example.invalid/v1'\n",
        "MODEL: str\n",
        "MODEL = ''\n",
        "MODEL = '   '\n",
    ):
        try:
            parse_legacy_settings(source)
        except ValueError as exc:
            assert str(exc) == ERROR
            assert "secret-value" not in str(exc)
        else:
            raise AssertionError("unsupported recognized assignment was accepted")


def test_api_key_expression_is_ignored_without_evaluation_or_output() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        marker = Path(temp_dir) / "secret-read.txt"
        source = (
            f"API_KEY = __import__('pathlib').Path({str(marker)!r}).write_text('secret')\n"
            "MODEL = 'safe-model'\n"
        )
        parsed = parse_legacy_settings(source)
        assert parsed == {"api": {"model": "safe-model"}}
        assert not marker.exists()
        assert "API_KEY" not in repr(parsed)
        assert "secret" not in repr(parsed)


def test_base_url_rejects_unsafe_or_invalid_endpoints() -> None:
    for endpoint in (
        "ftp://example.invalid/v1",
        "https:///v1",
        "https://user@example.invalid/v1",
        "https://user:pass@example.invalid/v1",
        "https://example.invalid/v1?token=secret",
        "https://example.invalid/v1#fragment",
        "https://example.invalid/v1?",
        "https://example.invalid/v1#",
        "https://example.invalid:99999/v1",
        " https://example.invalid/v1",
        "https://example.invalid/v1 ",
    ):
        _invalid(f"BASE_URL = {endpoint!r}\n")


def test_value_limits_and_control_characters_are_enforced() -> None:
    _invalid("MODEL = " + repr("m" * 257) + "\n")
    _invalid("SYSTEM_PROMPT = " + repr("p" * 8001) + "\n")
    _invalid("BASE_URL = " + repr("https://example.invalid/" + "a" * 2048) + "\n")
    _invalid("MODEL = 'bad\x01value'\n")
    _invalid("SYSTEM_PROMPT = 'bad\x00prompt'\n")
    _invalid("#" + "a" * MAX_SOURCE_BYTES)
    _invalid("MODEL = '\ud800'\n")
    _invalid(None)
    _invalid(b"MODEL = 'bytes are not source text'\n")


def test_malformed_source_and_no_usable_assignments_fail_generically() -> None:
    for source in (
        "MODEL = 'unterminated\n",
        "API_KEY = 'synthetic-secret'\nWORLD_DIR = '/private/world'\n",
        "# no supported settings\n",
    ):
        try:
            parse_legacy_settings(source)
        except ValueError as exc:
            assert str(exc) == ERROR
            assert "synthetic-secret" not in str(exc)
            assert "/private/world" not in str(exc)
        else:
            raise AssertionError("source without usable public settings was accepted")


def test_preview_dispatch_has_no_storage_or_credential_side_effects() -> None:
    from unittest.mock import patch
    import json
    from mwt import desktop_entry
    from mwt.userdata import remember_user_settings, settings_path

    with tempfile.TemporaryDirectory() as directory:
        data = Path(directory) / "data"
        remember_user_settings({"provider": "openrouter", "model": "persisted"}, data)
        before = settings_path(data).read_bytes()
        replies = []
        with patch.object(desktop_entry, "emit", replies.append), patch("mwt.secrets.load_api_key", side_effect=AssertionError("preview must not read credentials")), patch("mwt.userdata.remember_user_settings", side_effect=AssertionError("preview must not save")):
            desktop_entry.handle({"v": 1, "id": "legacy-preview", "type": "settings.import_legacy", "payload": {"source": "MODEL = 'draft'\nAPI_KEY = 'synthetic-private-key'"}}, data / "reports", data)
        assert replies[-1]["payload"] == {"config": {"api": {"model": "draft"}}}
        assert "synthetic-private-key" not in json.dumps(replies)
        assert settings_path(data).read_bytes() == before
        assert not (data / "reports").exists()


def main() -> None:
    test_public_literal_assignments_and_shape()
    test_model_only_does_not_invent_provider()
    test_last_literal_assignment_wins_and_annotations_are_supported()
    test_nested_assignments_and_nonpublic_assignments_are_ignored()
    test_python_code_is_parsed_but_never_executed()
    test_recognized_dynamic_or_chained_assignments_fail_generically()
    test_api_key_expression_is_ignored_without_evaluation_or_output()
    test_base_url_rejects_unsafe_or_invalid_endpoints()
    test_value_limits_and_control_characters_are_enforced()
    test_malformed_source_and_no_usable_assignments_fail_generically()
    test_preview_dispatch_has_no_storage_or_credential_side_effects()
    print("LEGACY_SETTINGS_IMPORT_PASSED (11 cases)")


if __name__ == "__main__":
    main()
