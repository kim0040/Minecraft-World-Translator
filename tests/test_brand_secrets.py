"""Brand copy and secret storage use the shipped surfaces."""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mwt.desktop_entry import main
from mwt.notices import ABOUT, API_WARNING, BACKUP_WARNING, FIRST_LAUNCH, PRE_TRANSLATE, PRODUCT_NAME, SUBTITLE, UNOFFICIAL_NOTICE
from mwt.secrets import load_api_key, redact_log, remember_api_key, save_public_settings

REQUIRED = (PRODUCT_NAME, SUBTITLE, UNOFFICIAL_NOTICE, BACKUP_WARNING, API_WARNING)


def assert_contains(label: str, text: str) -> None:
    for phrase in REQUIRED:
        if phrase not in text:
            raise SystemExit(f"{label} is missing {phrase}")
    print(f"surface {label} ok")


def test_surfaces() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert_contains("README", readme)
    assert_contains("first-launch", FIRST_LAUNCH)
    assert_contains("pre-translate", PRE_TRANSLATE)
    assert_contains("about", ABOUT)
    assert "no purchase, subscription, or in-app payment" in ABOUT
    assert "no purchase, subscription, or in-app payment" in readme
    notices = subprocess.run(
        [sys.executable, "-m", "mwt.desktop_entry", "--notices"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    about = subprocess.run(
        [sys.executable, "-m", "mwt.desktop_entry", "--about"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert_contains("desktop first-launch", notices.stdout)
    assert_contains("desktop about", about.stdout)
    # The pre-translate confirmation is the text the desktop entry returns before a write.
    from io import StringIO
    from unittest.mock import patch

    with patch("sys.stdout", StringIO()) as stdout:
        main(["--notices"])
    assert_contains("entry first-launch", stdout.getvalue())


def test_secrets_stay_out_of_settings_and_logs() -> None:
    import keyring
    from keyring.backend import KeyringBackend

    class MemoryKeyring(KeyringBackend):
        priority = 1

        def __init__(self) -> None:
            self.values: dict[tuple[str, str], str] = {}

        def set_password(self, service: str, username: str, password: str) -> None:
            self.values[(service, username)] = password

        def get_password(self, service: str, username: str) -> str | None:
            return self.values.get((service, username))

        def delete_password(self, service: str, username: str) -> None:
            self.values.pop((service, username), None)

    keyring.set_keyring(MemoryKeyring())
    secret = "pomi-test-secret-9f3c"
    remember_api_key("openai", secret)
    assert load_api_key("openai") == secret
    with tempfile.TemporaryDirectory() as temp_dir:
        database = Path(temp_dir) / "settings.sqlite"
        settings_json = Path(temp_dir) / "settings.json"
        log_path = Path(temp_dir) / "app.log"
        save_public_settings(database, provider="openai", model="fixture")
        settings_json.write_text(json.dumps({"provider": "openai", "model": "fixture"}), encoding="utf-8")
        log_path.write_text(redact_log(f"using key {secret} for openai", secret), encoding="utf-8")
        dumped = database.read_bytes() + settings_json.read_bytes() + log_path.read_bytes()
        rows = sqlite3.connect(database).execute("SELECT provider, model FROM settings").fetchall()
        assert rows == [("openai", "fixture")]
        assert secret.encode("utf-8") not in dumped
        assert b"[redacted]" in log_path.read_bytes()
    print("secret absent from settings dump and log")


if __name__ == "__main__":
    test_surfaces()
    test_secrets_stay_out_of_settings_and_logs()
    print("BRAND_SECRETS_PASSED")
