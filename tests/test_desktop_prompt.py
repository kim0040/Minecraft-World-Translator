"""Rust-owned desktop prompt enhancement contracts; no provider calls are made."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import mwt.desktop_entry as entry
import mwt.desktop_prompt as desktop_prompt
from mwt.userdata import remember_user_settings, settings_path


def _prompt_body(**updates: object) -> dict:
    body: dict = {
        "credentialOwner": "rust",
        "provider": "openrouter",
        "model": "fixture-model",
        "apiKey": "synthetic-prompt-key",
        "targetLanguage": "한국어",
        "stylePreset": "story",
        "stylePrompt": "Keep the atmosphere adventurous.",
        "customSystemPrompt": "Preserve names and formatting.",
        "brief": "A light nautical tone for pirates.",
    }
    body.update(updates)
    return body


def _call_prompt(body: dict, data_dir: Path) -> None:
    entry.handle(
        {"v": 1, "id": "prompt-test", "type": "prompt.enhance", "payload": body},
        data_dir / "reports",
        data_dir,
    )


def test_prompt_enhance_uses_rust_resolved_draft_and_does_not_persist() -> None:
    poison = {
        "POMI_PROVIDER": "custom",
        "POMI_MODEL": "poison-model",
        "POMI_API_BASE": "https://poison.invalid/v1",
        "POMI_WIRE_FORMAT": "anthropic",
        "POMI_API_KEY": "synthetic-poison-key",
        "POMI_TARGET_LANGUAGE": "poison-language",
        "POMI_STYLE_PRESET": "poison-style",
    }
    configs: list[dict] = []

    def fake_enhance(config: dict, brief: str) -> str:
        configs.append(config)
        assert brief == "A light nautical tone for pirates."
        from llm_backends import LLMProviderClient

        LLMProviderClient.usage = {
            "prompt_tokens": 30,
            "completion_tokens": 40,
            "cost": 0.0002,
            "cost_reported": True,
        }
        return "Use playful nautical phrasing."

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "userdata"
        remember_user_settings(
            {
                "provider": "openai",
                "model": "saved-model",
                "base_url": "https://stale.invalid/v1",
                "target_language": "saved-language",
            },
            data_dir,
        )
        settings_file = settings_path(data_dir)
        before = settings_file.read_bytes()
        with patch.dict(os.environ, poison), patch.object(desktop_prompt, "enhance_style_prompt", fake_enhance), patch.object(
            entry, "emit"
        ) as emit:
            _call_prompt(_prompt_body(), data_dir)

        assert settings_file.read_bytes() == before, "prompt enhancement must not write public settings"
        config = configs[-1]
        assert config["api"]["provider"] == "openrouter"
        assert config["api"]["model"] == "fixture-model"
        assert config["api"]["base_url"] == "https://openrouter.ai/api/v1"
        assert config["api"]["wire_format"] == "openai"
        assert config["api"]["api_key"] == "synthetic-prompt-key"
        assert config["prompt"] == {
            "target_language": "한국어",
            "style_preset": "story",
            "style_prompt": "Keep the atmosphere adventurous.",
            "custom_system_prompt": "Preserve names and formatting.",
        }
        response = emit.call_args.args[0]
        assert response["type"] == "response.ok"
        assert response["payload"] == {
            "enhancedPrompt": "Use playful nautical phrasing.",
            "usage": {
                "prompt_tokens": 30,
                "completion_tokens": 40,
                "cost": 0.0002,
                "cost_reported": True,
            },
        }
        encoded = json.dumps(response, ensure_ascii=False)
        for secret_or_setting in (
            "synthetic-prompt-key",
            "synthetic-poison-key",
            "fixture-model",
            "openrouter",
            "https://openrouter.ai/api/v1",
        ):
            assert secret_or_setting not in encoded
    print("PASS desktop_prompt.rust_owned_draft_usage_and_no_settings_write")


def test_prompt_enhance_rejects_invalid_requests_before_calling_provider() -> None:
    invalid_bodies = [
        _prompt_body(brief="  "),
        _prompt_body(brief="x" * (desktop_prompt.MAX_BRIEF_CHARS + 1)),
        _prompt_body(credentialOwner="python"),
        _prompt_body(targetLanguage=""),
        _prompt_body(stylePreset="unknown"),
        _prompt_body(stylePrompt="x" * (desktop_prompt.MAX_STYLE_PROMPT_CHARS + 1)),
        _prompt_body(customSystemPrompt="x" * (desktop_prompt.MAX_CUSTOM_SYSTEM_PROMPT_CHARS + 1)),
        _prompt_body(provider="unknown-provider"),
        _prompt_body(provider="custom", baseUrl="file:///tmp/provider"),
        _prompt_body(provider="custom", baseUrl="https://user:pass@example.invalid/v1"),
        _prompt_body(apiKey=""),
    ]
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "userdata"
        remember_user_settings({"provider": "openai", "model": "saved-model"}, data_dir)
        with patch.object(desktop_prompt, "enhance_style_prompt") as enhance:
            for body in invalid_bodies:
                try:
                    _call_prompt(body, data_dir)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"Invalid prompt request was accepted: {body!r}")
            enhance.assert_not_called()
    print("PASS desktop_prompt.invalid_requests_rejected_before_provider")


def test_rust_owned_dry_scan_ignores_poisoned_pomi_environment() -> None:
    poison = {
        "POMI_PROVIDER": "custom",
        "POMI_MODEL": "poison-model",
        "POMI_API_BASE": "https://poison.invalid/v1",
        "POMI_WIRE_FORMAT": "anthropic",
        "POMI_API_KEY": "synthetic-poison-key",
        "POMI_TARGET_LANGUAGE": "poison-language",
        "POMI_STYLE_PRESET": "poison-style",
    }
    configs: list[dict] = []

    class CapturingTranslator:
        def __init__(self, config: dict, **_kwargs: object) -> None:
            configs.append(config)
            self._candidate_order: list[str] = []
            self.occurrences: dict = {}

        def run(self) -> dict:
            return {
                "status": "completed",
                "world_fingerprint": "fixture-world-fingerprint",
                "changed_files": [],
                "write_blockers": [],
                "candidate_text_count": 0,
                "candidate_preview": [],
                "errors": [],
                "warnings": [],
            }

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        world = root / "world"
        world.mkdir()
        data_dir = root / "userdata"
        remember_user_settings(
            {
                "provider": "openrouter",
                "model": "saved-model",
                "target_language": "한국어",
                "style_preset": "neutral",
            },
            data_dir,
        )
        body = {
            "credentialOwner": "rust",
            "worldDir": str(world),
            "provider": "openai",
            "model": "scan-draft-model",
            "apiKey": "synthetic-scan-key",
        }
        with (
            patch.dict(os.environ, poison),
            patch("mc_world_translator.WorldTranslator", CapturingTranslator),
            patch.object(entry, "_world_inspection", return_value={"validJavaWorld": True, "resourcePacks": []}),
            patch.object(entry, "_coverage", return_value=[]),
            patch.object(entry, "_estimate", return_value={"requests": 0}),
            patch.object(entry, "emit"),
        ):
            entry.handle(
                {"v": 1, "id": "scan-test", "type": "scan.start", "payload": body},
                root / "reports",
                data_dir,
            )

        config = configs[-1]
        assert config["api"]["provider"] == "openai"
        assert config["api"]["model"] == "scan-draft-model"
        assert config["api"]["base_url"] == "https://api.openai.com/v1"
        assert config["api"]["wire_format"] == "openai"
        assert config["api"]["api_key"] == "", "dry scans do not use credentials"
        assert config["prompt"]["target_language"] == "한국어"
        assert config["prompt"]["style_preset"] == "neutral"
        settings_file = settings_path(data_dir)
        assert "synthetic-scan-key" not in settings_file.read_text(encoding="utf-8")
    print("PASS desktop_prompt.rust_owned_dry_scan_ignores_pomi_environment")


def main() -> None:
    test_prompt_enhance_uses_rust_resolved_draft_and_does_not_persist()
    test_prompt_enhance_rejects_invalid_requests_before_calling_provider()
    test_rust_owned_dry_scan_ignores_poisoned_pomi_environment()


if __name__ == "__main__":
    main()
