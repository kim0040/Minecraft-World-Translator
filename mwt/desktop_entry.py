"""Desktop/sidecar entry. Production speaks JSONL and does not open a localhost port."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mwt.notices import ABOUT, FIRST_LAUNCH, PRE_TRANSLATE, payload
from mwt.safety import BackupSet


def _saved(data_dir: Path) -> dict:
    from mwt.userdata import load_user_settings

    return load_user_settings(data_dir)


def _run_translator(
    world: Path,
    *,
    dry_run: bool,
    report_path: Path,
    fingerprint: str = "",
    data_dir: Path,
) -> dict:
    import os

    from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested, remember_run_settings
    from mwt.secrets import load_api_key

    saved = _saved(data_dir)
    provider = os.environ.get("POMI_PROVIDER") or str(saved.get("provider") or "openai")
    model = os.environ.get("POMI_MODEL") or str(saved.get("model") or "")
    base_url = os.environ.get("POMI_API_BASE") or str(saved.get("base_url") or "")
    wire_format = os.environ.get("POMI_WIRE_FORMAT") or str(saved.get("wire_format") or "")
    api_key = os.environ.get("POMI_API_KEY") or load_api_key(provider) or ""
    config = merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": dry_run,
            "report_path": str(report_path),
            "inherit_translate_py": False,
            "runtime": {
                "checkpoint_enabled": False,
                "checkpoint_path": str(report_path.with_suffix(".checkpoint.json")),
                "expected_world_fingerprint": fingerprint,
                "data_dir": str(data_dir),
            },
            "api": {
                "provider": provider,
                "api_key": api_key,
                "model": model,
                "base_url": base_url,
                "wire_format": wire_format,
            },
            "prompt": {
                "target_language": os.environ.get("POMI_TARGET_LANGUAGE") or saved.get("target_language") or "한국어",
                "style_preset": os.environ.get("POMI_STYLE_PRESET") or saved.get("style_preset") or "neutral",
            },
        },
    )
    report = WorldTranslator(config).run()
    remember_run_settings(config, data_dir, None)
    return report


def emit(message: dict) -> None:
    sys.stdout.write(json.dumps(message, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def hello() -> None:
    emit(
        {
            "v": 1,
            "type": "system.hello",
            "payload": {
                "productName": "PomiTranslate",
                "subtitle": "World Translator for Minecraft",
                "protocolVersion": 1,
                "localhostServer": False,
                "capabilities": [
                    "scan",
                    "translate",
                    "restore",
                    "settings",
                    "models",
                    "region.lz4",
                    "region.external_chunk",
                ],
                "providers": ["openai", "gemini", "anthropic", "openrouter", "custom"],
                "notices": payload(),
            },
        }
    )


def _settings_payload(data_dir: Path, provider: str = "") -> dict:
    from mwt.secrets import load_api_key

    saved = _saved(data_dir)
    chosen = provider or str(saved.get("provider") or "")
    return {
        "settings": saved,
        "apiKeyStored": bool(chosen and load_api_key(chosen)),
        "localhostServer": False,
    }


def handle(message: dict, report_dir: Path, data_dir: Path) -> None:
    kind = message.get("type")
    request_id = message.get("id", "")
    body = message.get("payload") or {}
    world = Path(body.get("worldDir", "")).expanduser()
    if kind == "notices.get":
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": payload()})
        return
    if kind == "settings.get":
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": _settings_payload(data_dir)})
        return
    if kind == "settings.set":
        from mc_world_translator import remember_run_settings

        saved = _saved(data_dir)
        provider = str(body.get("provider") or saved.get("provider") or "openai")
        config = {
            "world_dir": str(body.get("worldDir") or saved.get("last_world_dir") or ""),
            "temperature": body.get("temperature", saved.get("temperature", "")),
            "batch_size": body.get("batchSize", saved.get("batch_size", "")),
            "api": {
                "provider": provider,
                "model": str(body.get("model") or saved.get("model") or ""),
                "base_url": str(body.get("baseUrl") or body.get("base_url") or saved.get("base_url") or ""),
                "wire_format": str(body.get("wireFormat") or body.get("wire_format") or saved.get("wire_format") or ""),
            },
            "prompt": {
                "target_language": str(
                    body.get("targetLanguage") or body.get("target_language") or saved.get("target_language") or ""
                ),
                "style_preset": str(body.get("stylePreset") or body.get("style_preset") or saved.get("style_preset") or ""),
                "style_prompt": str(body.get("stylePrompt") or body.get("style_prompt") or saved.get("style_prompt") or ""),
                "custom_system_prompt": str(body.get("customSystemPrompt") or saved.get("custom_system_prompt") or ""),
            },
        }
        supplied_key = str(body.get("apiKey") or "")
        remember_run_settings(config, data_dir, supplied_key or None)
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "remembered": True,
                    "apiKeyStored": bool(supplied_key) or _settings_payload(data_dir, provider)["apiKeyStored"],
                    "settings": _saved(data_dir),
                    "localhostServer": False,
                },
            }
        )
        return
    if kind == "models.list":
        import os

        from mc_world_translator import DEFAULT_CONFIG, merge_nested
        from llm_backends import LLMProviderClient
        from mwt.secrets import load_api_key

        saved = _saved(data_dir)
        provider = str(body.get("provider") or saved.get("provider") or "openai")
        config = merge_nested(
            DEFAULT_CONFIG,
            {
                "inherit_translate_py": False,
                "runtime": {"data_dir": str(data_dir)},
                "api": {
                    "provider": provider,
                    "api_key": os.environ.get("POMI_API_KEY") or load_api_key(provider) or "",
                    "model": str(body.get("model") or saved.get("model") or ""),
                    "base_url": str(body.get("baseUrl") or os.environ.get("POMI_API_BASE") or saved.get("base_url") or ""),
                    "wire_format": str(body.get("wireFormat") or saved.get("wire_format") or ""),
                },
            },
        )
        try:
            models = LLMProviderClient(config).try_refresh_text_models()
        except Exception as exc:
            emit(
                {
                    "v": 1,
                    "id": request_id,
                    "type": "response.error",
                    "error": {"code": "MODELS_FAILED", "message": str(exc)},
                }
            )
            return
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {"provider": provider, "models": models, "localhostServer": False},
            }
        )
        return
    if kind == "scan.start":
        report = _run_translator(world, dry_run=True, report_path=report_dir / "scan-report.json", data_dir=data_dir)
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "status": report.get("status"),
                    "candidateCount": report.get("candidate_text_count", 0),
                    "providerRequests": report.get("provider_requests", 0),
                    "fingerprint": report.get("world_fingerprint", ""),
                    "dryRun": True,
                    "localhostServer": False,
                    "preTranslate": PRE_TRANSLATE,
                },
            }
        )
        return
    if kind == "translate.start":
        report = _run_translator(
            world,
            dry_run=False,
            report_path=report_dir / "translate-report.json",
            fingerprint=str(body.get("fingerprint", "")),
            data_dir=data_dir,
        )
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "status": report.get("status"),
                    "candidateCount": report.get("candidate_text_count", 0),
                    "changedFileCount": report.get("changed_file_count", 0),
                    "preTranslate": PRE_TRANSLATE,
                    "localhostServer": False,
                },
            }
        )
        return
    if kind == "restore.start":
        BackupSet(world, "latest").restore()
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": {"status": "restored", "localhostServer": False}})
        return
    emit(
        {
            "v": 1,
            "id": request_id,
            "type": "response.error",
            "error": {"code": "UNKNOWN_MESSAGE", "message": f"Unknown message {kind}"},
        }
    )


def serve(report_dir: Path, data_dir: Path) -> None:
    hello()
    for line in sys.stdin:
        if not line.strip():
            continue
        handle(json.loads(line), report_dir, data_dir)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="PomiTranslate desktop entry")
    parser.add_argument("--notices", action="store_true")
    parser.add_argument("--about", action="store_true")
    parser.add_argument("--scan", type=str)
    parser.add_argument("--translate", type=str)
    parser.add_argument("--fingerprint", default="")
    parser.add_argument("--restore", type=str)
    parser.add_argument("--jsonl", action="store_true")
    parser.add_argument("--report-dir", default="")
    parser.add_argument("--data-dir", default="")
    args = parser.parse_args(argv)
    from mwt.userdata import user_data_dir

    report_dir = Path(args.report_dir) if args.report_dir else Path.cwd() / ".pomi-reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    data_dir = Path(args.data_dir).expanduser() if args.data_dir else user_data_dir()
    if args.notices:
        print(FIRST_LAUNCH)
        return
    if args.about:
        print(ABOUT)
        return
    if args.jsonl:
        serve(report_dir, data_dir)
        return
    if args.scan:
        report = _run_translator(
            Path(args.scan),
            dry_run=True,
            report_path=report_dir / "scan-report.json",
            data_dir=data_dir,
        )
        print(json.dumps({"localhostServer": False, "dryRun": True, **report}, ensure_ascii=False))
        return
    if args.translate:
        report = _run_translator(
            Path(args.translate),
            dry_run=False,
            report_path=report_dir / "translate-report.json",
            fingerprint=args.fingerprint,
            data_dir=data_dir,
        )
        print(json.dumps({"localhostServer": False, "preTranslate": PRE_TRANSLATE, **report}, ensure_ascii=False))
        return
    if args.restore:
        BackupSet(Path(args.restore), "latest").restore()
        print(json.dumps({"status": "restored", "localhostServer": False}))
        return
    hello()


if __name__ == "__main__":
    main()
