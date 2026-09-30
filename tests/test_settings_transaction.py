"""Public settings validation, exact rollback, and Rust-only credential ownership."""
from __future__ import annotations

import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mwt.desktop_entry import handle
from mwt.userdata import load_user_settings, remember_user_settings, settings_path


def main() -> None:
    with tempfile.TemporaryDirectory() as root:
        data = Path(root) / "data"
        reports = Path(root) / "reports"
        responses: list[dict] = []
        def send(kind: str, payload: dict) -> dict:
            with patch("mwt.desktop_entry.emit", responses.append):
                handle({"v": 1, "id": "settings-fixture", "type": kind, "payload": payload}, reports, data)
            return responses[-1]["payload"]

        # Even a failed first save must recover to an empty snapshot, not merged defaults.
        before = load_user_settings(data)
        with patch("mwt.secrets.remember_api_key", side_effect=AssertionError("Rust key leaked to Python keyring")):
            saved = send("settings.set", {"credentialOwner": "rust", "provider": "openrouter", "model": "fixture", "uiLanguage": "en", "apiKey": "synthetic-do-not-persist"})["settings"]
        assert "synthetic-do-not-persist" not in settings_path(data).read_text()
        restored = send("settings.restore", {"credentialOwner": "rust", "settings": before, "expectedSettings": saved})
        assert restored["settings"] == before == load_user_settings(data)
        remember_user_settings({"model": "old", "ui_language": "ko", "unknownPreference": {"enabled": True}}, data)
        before_bytes = settings_path(data).read_bytes()
        for payload in [
            {"model": "changed", "uiLanguage": "unsupported"},
            {"model": "changed", "uiLanguage": "en", "batchSize": 0},
        ]:
            try:
                send("settings.set", {"credentialOwner": "rust", **payload})
            except ValueError:
                pass
            else:
                raise AssertionError("invalid settings accepted")
            assert settings_path(data).read_bytes() == before_bytes
        before = load_user_settings(data)
        saved = send("settings.set", {"credentialOwner": "rust", "model": "new", "uiLanguage": "en"})["settings"]
        restored = send("settings.restore", {"credentialOwner": "rust", "settings": before, "expectedSettings": saved})
        assert restored["settings"] == before
        assert load_user_settings(data) == before
        remember_user_settings({"model": "external-cli-change"}, data)
        for payload in [
            {"credentialOwner": "rust", "settings": before, "expectedSettings": saved},
            {"credentialOwner": "rust", "settings": {"apiKey": "secret"}, "expectedSettings": load_user_settings(data)},
            {"settings": before, "expectedSettings": load_user_settings(data)},
        ]:
            try:
                send("settings.restore", payload)
            except ValueError:
                pass
            else:
                raise AssertionError("unsafe rollback accepted")
            assert load_user_settings(data)["model"] == "external-cli-change"
        # Real simultaneous writers keep both disjoint updates; fixed .tmp names are
        # protected by the same lock used by rollback comparison and replacement.
        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(lambda index: remember_user_settings({f"writer_{index}": index}, data), range(24)))
        current = load_user_settings(data)
        assert all(current[f"writer_{index}"] == index for index in range(24))
    print("SETTINGS_TRANSACTION_PASSED")


if __name__ == "__main__":
    main()
