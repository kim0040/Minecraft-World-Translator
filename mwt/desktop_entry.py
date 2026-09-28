"""Desktop/sidecar entry. Production speaks JSONL and does not open a localhost port."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from mwt.notices import ABOUT, FIRST_LAUNCH, PRE_TRANSLATE, payload
from mwt.safety import BackupSet


def _run_translator(world: Path, *, dry_run: bool, report_path: Path, fingerprint: str = "") -> dict:
    import os

    from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested

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
            },
            "api": {
                "provider": "openai",
                "api_key": os.environ.get("POMI_API_KEY", ""),
                "model": os.environ.get("POMI_MODEL", "fixture"),
                "base_url": os.environ.get("POMI_API_BASE", "https://api.openai.com/v1"),
            },
        },
    )
    return WorldTranslator(config).run()


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
                "capabilities": ["scan", "translate", "restore", "region.lz4", "region.external_chunk"],
                "notices": payload(),
            },
        }
    )


def handle(message: dict, report_dir: Path) -> None:
    kind = message.get("type")
    request_id = message.get("id", "")
    body = message.get("payload") or {}
    world = Path(body.get("worldDir", "")).expanduser()
    if kind == "notices.get":
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": payload()})
        return
    if kind == "scan.start":
        report = _run_translator(world, dry_run=True, report_path=report_dir / "scan-report.json")
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


def serve(report_dir: Path) -> None:
    hello()
    for line in sys.stdin:
        if not line.strip():
            continue
        handle(json.loads(line), report_dir)


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
    args = parser.parse_args(argv)
    report_dir = Path(args.report_dir) if args.report_dir else Path.cwd() / ".pomi-reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    if args.notices:
        print(FIRST_LAUNCH)
        return
    if args.about:
        print(ABOUT)
        return
    if args.jsonl:
        serve(report_dir)
        return
    if args.scan:
        report = _run_translator(Path(args.scan), dry_run=True, report_path=report_dir / "scan-report.json")
        print(json.dumps({"localhostServer": False, "dryRun": True, **report}, ensure_ascii=False))
        return
    if args.translate:
        report = _run_translator(
            Path(args.translate),
            dry_run=False,
            report_path=report_dir / "translate-report.json",
            fingerprint=args.fingerprint,
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
