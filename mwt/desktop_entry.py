"""Desktop/sidecar entry. Production speaks JSONL and does not open a localhost port."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from mwt.notices import ABOUT, FIRST_LAUNCH, PRE_TRANSLATE, payload
from mwt.safety import BackupSet, list_backup_sets


# A job stopped by the user, by an outage, or by a provider error keeps its translated strings
# in the checkpoint. Only these states may be continued.
RESUMABLE_STATUSES = {"cancelled", "needs_retry", "failed"}


def _settings_fingerprint(data_dir: Path) -> str:
    saved = _saved(data_dir)
    relevant = {
        key: saved.get(key, "")
        for key in (
            "provider",
            "model",
            "base_url",
            "wire_format",
            "target_language",
            "style_preset",
            "style_prompt",
            "custom_system_prompt",
            "temperature",
            "batch_size",
            "request_timeout",
            "rpm_limit",
            "tpm_limit",
            "max_batch_retries",
            "resource_pack_enabled",
        )
    }
    encoded = json.dumps(relevant, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _scan_plan_id(world_fingerprint: str, settings_fingerprint: str) -> str:
    return hashlib.sha256(f"scan-v1:{world_fingerprint}:{settings_fingerprint}".encode("utf-8")).hexdigest()


def _scan_plan_path(data_dir: Path, scan_plan_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", scan_plan_id):
        raise ValueError("Invalid scan plan ID")
    return data_dir / "scans" / f"{scan_plan_id}.json"


def _checkpoint_path(data_dir: Path, scan_plan_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{64}", scan_plan_id):
        raise ValueError("Invalid scan plan ID")
    return data_dir / "jobs" / f"{scan_plan_id}.checkpoint.json"


def _request_estimate(candidate_count: int, batch_size: int) -> int:
    """Translation batches across the whole world, so this is exact unless a provider call fails."""
    return -(-int(candidate_count) // max(1, int(batch_size))) if candidate_count else 0


def _candidate_record(source: str) -> dict:
    return {
        "id": hashlib.sha256(source.encode("utf-8")).hexdigest()[:20],
        "source": source,
        "kind": "world.text",
        "location": "",
    }


def _level_data_version(level_path: Path) -> int | None:
    try:
        from nbt import nbt

        document = nbt.NBTFile(filename=str(level_path))
        try:
            value = document["Data"]["DataVersion"].value
        except (KeyError, TypeError):
            value = document["DataVersion"].value
        return int(value)
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _world_inspection(world: Path, *, recursive_blockers: bool = True) -> dict:
    import os

    from mwt.layout import detect_write_blockers, discover_region_dirs
    from mwt.locking import world_is_in_use

    root = world.expanduser().resolve()
    if not root.is_dir():
        return {"validJavaWorld": False, "kind": "missing", "writeBlockers": ["missing"]}
    if not os.access(root, os.R_OK):
        return {"validJavaWorld": False, "kind": "unknown", "writeBlockers": ["not_readable"]}
    root_world = (root / "level.dat").is_file()
    try:
        child_worlds = sorted(
            child.name for child in root.iterdir() if child.is_dir() and (child / "level.dat").is_file()
        )
    except OSError:
        return {"validJavaWorld": False, "kind": "unknown", "writeBlockers": ["not_readable"]}
    blockers = detect_write_blockers(root, recursive=recursive_blockers)
    if world_is_in_use(root):
        blockers.append("world_in_use")
    if not os.access(root, os.R_OK | os.W_OK):
        blockers.append("not_writable")
    valid = bool(root_world or child_worlds) and "bedrock" not in blockers
    resource_packs = []
    if root_world and (root / "resources.zip").is_file():
        resource_packs.append(str(root / "resources.zip"))
    for child_name in child_worlds:
        resource_pack = root / child_name / "resources.zip"
        if resource_pack.is_file():
            resource_packs.append(str(resource_pack))
    world_roots = [root] if root_world else [root / name for name in child_worlds]
    data_versions = [
        {
            "world": item.name or item.as_posix(),
            "dataVersion": _level_data_version(item / "level.dat"),
        }
        for item in world_roots
    ]
    return {
        "validJavaWorld": valid,
        "kind": "java_world" if root_world else "server_root" if child_worlds else "unknown",
        "childWorlds": child_worlds,
        "regionDirs": discover_region_dirs(root),
        "resourcePacks": resource_packs,
        "dataVersions": data_versions,
        "writeBlockers": blockers,
    }


def _save_scan_plan(
    data_dir: Path,
    scan_plan_id: str,
    *,
    world_fingerprint: str,
    settings_fingerprint: str,
    candidates: list[str],
) -> None:
    path = _scan_plan_path(data_dir, scan_plan_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {
        "version": 1,
        "scanPlanId": scan_plan_id,
        "worldFingerprint": world_fingerprint,
        "settingsFingerprint": settings_fingerprint,
        "candidates": [_candidate_record(source) for source in candidates],
    }
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    os.replace(temporary, path)


def _load_scan_plan(data_dir: Path, scan_plan_id: str) -> dict:
    path = _scan_plan_path(data_dir, scan_plan_id)
    if not path.is_file():
        return {}
    loaded = json.loads(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _resume_candidate(data_dir: Path, world: Path) -> dict:
    from mwt.safety import world_fingerprint

    resolved_world = world.expanduser().resolve()
    if not resolved_world.is_dir():
        return {}
    jobs_dir = data_dir / "jobs"
    if not jobs_dir.is_dir():
        return {}
    current_settings = _settings_fingerprint(data_dir)
    preliminary: list[tuple[dict, dict, dict, dict]] = []
    for path in jobs_dir.glob("*.checkpoint.json"):
        try:
            checkpoint = json.loads(path.read_text(encoding="utf-8"))
            resume = checkpoint.get("resume") or {}
            report = checkpoint.get("report") or {}
            scan_plan_id = str(resume.get("scan_plan_id") or "")
            plan = _load_scan_plan(data_dir, scan_plan_id)
            if (
                checkpoint.get("version") != 2
                or report.get("status") not in RESUMABLE_STATUSES
                or Path(str(checkpoint.get("world_dir") or "")).expanduser().resolve() != resolved_world
                or plan.get("settingsFingerprint") != current_settings
                or plan.get("worldFingerprint") != resume.get("expected_world_fingerprint")
            ):
                continue
            preliminary.append((checkpoint, resume, report, plan))
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    if not preliminary:
        return {}

    current_world = world_fingerprint(resolved_world)
    candidates: list[dict] = []
    for checkpoint, resume, report, plan in preliminary:
        try:
            if checkpoint.get("world_fingerprint") != current_world:
                continue
            scan_plan_id = str(resume.get("scan_plan_id") or "")
            plan_candidates = [item for item in plan.get("candidates", []) if isinstance(item, dict)]
            id_by_source = {str(item.get("source")): str(item.get("id")) for item in plan_candidates}
            candidate_overrides = {
                id_by_source[source]: translated
                for source, translated in (resume.get("manual_overrides") or {}).items()
                if source in id_by_source and isinstance(translated, str)
            }
            candidates.append(
                {
                    "available": True,
                    "scanPlanId": scan_plan_id,
                    "fingerprint": str(resume.get("expected_world_fingerprint") or ""),
                    "candidateCount": len(plan_candidates),
                    "candidates": plan_candidates[:200],
                    "excludedCandidateIds": list(resume.get("excluded_candidate_ids") or []),
                    "candidateOverrides": candidate_overrides,
                    "savedAt": float(checkpoint.get("saved_at") or 0),
                    "backupSetId": str(report.get("backup_set_id") or ""),
                    "status": str(report.get("status") or ""),
                    "translatedCount": len(checkpoint.get("translation_cache") or {}),
                    "reason": next(
                        (str(item.get("message") or "") for item in report.get("errors", []) if isinstance(item, dict)),
                        "",
                    ),
                }
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            continue
    return max(candidates, key=lambda item: item["savedAt"], default={})


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
    progress_callback=None,
    candidate_limit: int = 0,
    excluded_candidate_ids: list[str] | None = None,
    cancel_check=None,
    api_key_override: str = "",
    allow_keyring_fallback: bool = True,
    manual_overrides: dict[str, str] | None = None,
    skip_provider_validation: bool = False,
    scan_plan_id: str = "",
    resume_from_checkpoint: bool = False,
    on_translation_failure: str = "stop",
) -> dict:
    import os

    from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested, remember_run_settings
    from mwt.secrets import load_api_key

    saved = _saved(data_dir)
    provider = os.environ.get("POMI_PROVIDER") or str(saved.get("provider") or "openai")
    model = os.environ.get("POMI_MODEL") or str(saved.get("model") or "")
    base_url = os.environ.get("POMI_API_BASE") or str(saved.get("base_url") or "")
    wire_format = os.environ.get("POMI_WIRE_FORMAT") or str(saved.get("wire_format") or "")
    api_key = "" if dry_run else (
        api_key_override
        or os.environ.get("POMI_API_KEY")
        or (load_api_key(provider) if allow_keyring_fallback else "")
        or ""
    )
    resource_pack_paths = []
    if bool(saved.get("resource_pack_enabled")):
        inspection = _world_inspection(world)
        resource_pack_paths = list(inspection.get("resourcePacks") or [])
    checkpoint_path = _checkpoint_path(data_dir, scan_plan_id) if scan_plan_id else report_path.with_suffix(".checkpoint.json")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    if scan_plan_id and not dry_run and not resume_from_checkpoint:
        checkpoint_path.unlink(missing_ok=True)
    config = merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": dry_run,
            "report_path": str(report_path),
            "temperature": float(saved.get("temperature") or DEFAULT_CONFIG["temperature"]),
            "batch_size": int(saved.get("batch_size") or DEFAULT_CONFIG["batch_size"]),
            "inherit_translate_py": False,
            "runtime": {
                "checkpoint_enabled": bool(scan_plan_id and not dry_run),
                "checkpoint_path": str(checkpoint_path),
                "resume_from_checkpoint": resume_from_checkpoint,
                "scan_plan_id": scan_plan_id,
                "expected_world_fingerprint": fingerprint,
                "data_dir": str(data_dir),
                "excluded_candidate_ids": excluded_candidate_ids or [],
                "skip_provider_validation": skip_provider_validation,
                "on_translation_failure": "skip" if on_translation_failure == "skip" else "stop",
                "max_batch_retries": int(
                    saved.get("max_batch_retries") or DEFAULT_CONFIG["runtime"]["max_batch_retries"]
                ),
            },
            "api": {
                "provider": provider,
                "api_key": api_key,
                "model": model,
                "base_url": base_url,
                "wire_format": wire_format,
                "request_timeout": int(
                    saved.get("request_timeout") or DEFAULT_CONFIG["api"]["request_timeout"]
                ),
                "rpm_limit": int(saved.get("rpm_limit") or 0),
                "tpm_limit": int(saved.get("tpm_limit") or 0),
            },
            "prompt": {
                "target_language": os.environ.get("POMI_TARGET_LANGUAGE") or saved.get("target_language") or "한국어",
                "style_preset": os.environ.get("POMI_STYLE_PRESET") or saved.get("style_preset") or "neutral",
                "style_prompt": str(saved.get("style_prompt") or ""),
                "custom_system_prompt": str(saved.get("custom_system_prompt") or ""),
            },
            "scan": {"overrides": manual_overrides or {}},
            "resource_pack": {
                "enabled": bool(resource_pack_paths),
                "zip_paths": resource_pack_paths,
            },
        },
    )
    translator = WorldTranslator(config, progress_callback=progress_callback, cancel_check=cancel_check)
    report = translator.run()
    if dry_run and candidate_limit:
        candidates = sorted(translator.candidate_texts)
        report["candidate_preview"] = [_candidate_record(source) for source in candidates[:candidate_limit]]
        report["_candidate_sources"] = candidates
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


def _settings_payload(data_dir: Path, provider: str = "", *, check_keyring: bool = True) -> dict:
    from mwt.secrets import load_api_key

    saved = _saved(data_dir)
    chosen = provider or str(saved.get("provider") or "")
    return {
        "settings": saved,
        "apiKeyStored": bool(check_keyring and chosen and load_api_key(chosen)),
        "localhostServer": False,
    }


def _bootstrap_payload(data_dir: Path, requested_world: str = "", *, check_keyring: bool = True) -> dict:
    from mwt.userdata import list_recent_worlds

    settings = _settings_payload(data_dir, check_keyring=check_keyring)
    selected = str(requested_world or settings["settings"].get("last_world_dir") or "")
    world = Path(selected).expanduser() if selected else None
    inspection = _world_inspection(world, recursive_blockers=False) if world else None
    valid_world = bool(world and inspection and inspection.get("validJavaWorld"))
    return {
        "notices": payload(),
        **settings,
        "worlds": list_recent_worlds(data_dir),
        "worldInspection": inspection,
        "backups": list_backup_sets(world) if valid_world else [],
        "resume": (_resume_candidate(data_dir, world) or {"available": False}) if valid_world else {"available": False},
    }


def handle(message: dict, report_dir: Path, data_dir: Path, cancel_path: Path | None = None) -> None:
    kind = message.get("type")
    request_id = message.get("id", "")
    body = message.get("payload") or {}
    world = Path(body.get("worldDir", "")).expanduser()
    if kind == "app.bootstrap":
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": _bootstrap_payload(
                    data_dir,
                    str(body.get("worldDir") or ""),
                    check_keyring=body.get("credentialOwner") != "rust",
                ),
            }
        )
        return
    if kind == "notices.get":
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": payload()})
        return
    if kind == "settings.get":
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": _settings_payload(
                    data_dir, check_keyring=body.get("credentialOwner") != "rust"
                ),
            }
        )
        return
    if kind == "settings.set":
        from mc_world_translator import DEFAULT_CONFIG, remember_run_settings
        from mwt.userdata import remember_user_settings

        saved = _saved(data_dir)
        provider = str(body.get("provider") or saved.get("provider") or "openai")
        def text_setting(camel_name: str, saved_name: str, default: str = "") -> str:
            if camel_name in body:
                return str(body.get(camel_name) or "")
            if saved_name in body:
                return str(body.get(saved_name) or "")
            return str(saved.get(saved_name) or default)

        def bounded_number(name: str, saved_name: str, default: float, minimum: float, maximum: float) -> float:
            raw = body.get(name, saved.get(saved_name, default))
            try:
                value = float(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid {name}") from exc
            if not minimum <= value <= maximum:
                raise ValueError(f"{name} must be between {minimum:g} and {maximum:g}")
            return value

        temperature = bounded_number("temperature", "temperature", DEFAULT_CONFIG["temperature"], 0, 2)
        batch_size = int(bounded_number("batchSize", "batch_size", DEFAULT_CONFIG["batch_size"], 1, 200))
        request_timeout = int(
            bounded_number("requestTimeout", "request_timeout", DEFAULT_CONFIG["api"]["request_timeout"], 5, 600)
        )
        rpm_limit = int(bounded_number("rpmLimit", "rpm_limit", 0, 0, 10000))
        tpm_limit = int(bounded_number("tpmLimit", "tpm_limit", 0, 0, 10000000))
        max_batch_retries = int(
            bounded_number(
                "maxBatchRetries",
                "max_batch_retries",
                DEFAULT_CONFIG["runtime"]["max_batch_retries"],
                0,
                10,
            )
        )
        config = {
            "world_dir": str(body.get("worldDir") or saved.get("last_world_dir") or ""),
            "temperature": temperature,
            "batch_size": batch_size,
            "api": {
                "provider": provider,
                "model": str(body.get("model") or saved.get("model") or ""),
                "base_url": str(body.get("baseUrl") or body.get("base_url") or saved.get("base_url") or ""),
                "wire_format": str(body.get("wireFormat") or body.get("wire_format") or saved.get("wire_format") or ""),
                "request_timeout": request_timeout,
                "rpm_limit": rpm_limit,
                "tpm_limit": tpm_limit,
            },
            "prompt": {
                "target_language": text_setting("targetLanguage", "target_language"),
                "style_preset": text_setting("stylePreset", "style_preset", "neutral"),
                "style_prompt": text_setting("stylePrompt", "style_prompt"),
                "custom_system_prompt": text_setting("customSystemPrompt", "custom_system_prompt"),
            },
            "runtime": {"max_batch_retries": max_batch_retries},
            "resource_pack": {
                "enabled": bool(body.get("resourcePackEnabled", saved.get("resource_pack_enabled", False)))
            },
        }
        supplied_key = str(body.get("apiKey") or "")
        remember_run_settings(config, data_dir, supplied_key or None)
        ui_language = str(body.get("uiLanguage") or saved.get("ui_language") or "ko")
        if ui_language not in {"ko", "en", "ja"}:
            raise ValueError("Unsupported interface language")
        remember_user_settings({"ui_language": ui_language}, data_dir)
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "remembered": True,
                    "apiKeyStored": bool(supplied_key) or _settings_payload(
                        data_dir,
                        provider,
                        check_keyring=body.get("credentialOwner") != "rust",
                    )["apiKeyStored"],
                    "settings": _saved(data_dir),
                    "localhostServer": False,
                },
            }
        )
        return
    if kind in {"worlds.list", "worlds.remember", "worlds.forget"}:
        from mwt.userdata import forget_recent_world, list_recent_worlds, remember_recent_world

        if kind == "worlds.remember":
            if not isinstance(body.get("worldDir"), str) or not body["worldDir"].strip() or not world.is_dir():
                raise ValueError("A valid world directory is required")
            worlds = remember_recent_world(world, data_dir)
        elif kind == "worlds.forget":
            if not isinstance(body.get("worldDir"), str) or not body["worldDir"].strip():
                raise ValueError("A world directory is required")
            worlds = forget_recent_world(world, data_dir)
        else:
            worlds = list_recent_worlds(data_dir)
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {"worlds": worlds, "localhostServer": False},
            }
        )
        return
    if kind == "world.inspect":
        emit({"v": 1, "id": request_id, "type": "response.ok", "payload": _world_inspection(world)})
        return
    if kind == "resume.status":
        candidate = _resume_candidate(data_dir, world)
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": candidate or {"available": False},
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
                    "api_key": str(body.get("apiKey") or "")
                    or os.environ.get("POMI_API_KEY")
                    or (load_api_key(provider) if body.get("credentialOwner") != "rust" else "")
                    or "",
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
        inspection = _world_inspection(world)
        if not inspection["validJavaWorld"]:
            emit(
                {
                    "v": 1,
                    "id": request_id,
                    "type": "response.error",
                    "error": {
                        "code": "WORLD_NOT_SUPPORTED",
                        "message": "Select a Minecraft Java world folder or a server root containing Java worlds.",
                        "details": inspection,
                        "recoverable": True,
                    },
                }
            )
            return
        report = _run_translator(
            world,
            dry_run=True,
            report_path=report_dir / "scan-report.json",
            data_dir=data_dir,
            candidate_limit=200,
            progress_callback=lambda event: emit(
                {"v": 1, "id": request_id, "type": "scan.progress", "payload": event}
            ),
            cancel_check=(lambda: cancel_path.is_file()) if cancel_path else None,
        )
        skipped = [
            item for item in report.get("changed_files", [])
            if item.get("skipped") in {"unsupported_compression", "parse_error", "file_error"}
        ]
        blockers = list(report.get("write_blockers") or [])
        blockers.extend(
            f"{item.get('skipped')}: {item.get('file', 'unknown file')}" for item in skipped
        )
        fingerprint = str(report.get("world_fingerprint", ""))
        settings_fingerprint = _settings_fingerprint(data_dir)
        scan_plan_id = _scan_plan_id(fingerprint, settings_fingerprint)
        candidate_sources = list(report.pop("_candidate_sources", []))
        if report.get("status") == "completed":
            _save_scan_plan(
                data_dir,
                scan_plan_id,
                world_fingerprint=fingerprint,
                settings_fingerprint=settings_fingerprint,
                candidates=candidate_sources,
            )
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "status": report.get("status"),
                    "candidateCount": report.get("candidate_text_count", 0),
                    "providerRequests": report.get("provider_requests", 0),
                    "fingerprint": fingerprint,
                    "scanPlanId": scan_plan_id,
                    "dryRun": True,
                    "localhostServer": False,
                    "preTranslate": PRE_TRANSLATE,
                    "writeBlockers": blockers,
                    "errors": report.get("errors", []),
                    "warnings": report.get("warnings", []),
                    "requestEstimate": _request_estimate(
                        report.get("candidate_text_count", 0), int(_saved(data_dir).get("batch_size") or 40)
                    ),
                    "candidates": report.get("candidate_preview", []),
                },
            }
        )
        return
    if kind == "candidates.page":
        scan_plan_id = str(body.get("scanPlanId") or "")
        plan = _load_scan_plan(data_dir, scan_plan_id)
        if not plan:
            raise ValueError("Scan plan was not found")
        offset = max(0, int(body.get("offset") or 0))
        limit = min(200, max(1, int(body.get("limit") or 100)))
        candidates = list(plan.get("candidates") or [])
        query = str(body.get("query") or "").strip().casefold()
        if query:
            candidates = [
                candidate
                for candidate in candidates
                if query in str(candidate.get("source") or "").casefold()
            ]
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "candidates": candidates[offset : offset + limit],
                    "offset": offset,
                    "total": len(candidates),
                    "hasMore": offset + limit < len(candidates),
                },
            }
        )
        return
    if kind in {"translate.start", "translate.resume"}:
        if kind == "translate.resume":
            resumable = _resume_candidate(data_dir, world)
            if not resumable:
                emit(
                    {
                        "v": 1,
                        "id": request_id,
                        "type": "response.error",
                        "error": {
                            "code": "RESUME_NOT_AVAILABLE",
                            "message": "The cancelled job no longer matches the world or translation settings.",
                            "recoverable": True,
                        },
                    }
                )
                return
            body = {
                **body,
                "fingerprint": resumable["fingerprint"],
                "scanPlanId": resumable["scanPlanId"],
                "excludedCandidateIds": resumable["excludedCandidateIds"],
                "candidateOverrides": resumable["candidateOverrides"],
            }
        fingerprint = str(body.get("fingerprint") or "")
        scan_plan_id = str(body.get("scanPlanId") or "")
        settings_fingerprint = _settings_fingerprint(data_dir)
        expected_plan_id = _scan_plan_id(fingerprint, settings_fingerprint) if fingerprint else ""
        if not fingerprint or not scan_plan_id:
            emit(
                {
                    "v": 1,
                    "id": request_id,
                    "type": "response.error",
                    "error": {
                        "code": "SCAN_REQUIRED",
                        "message": "Run Scan Only and review its result before translating.",
                        "recoverable": True,
                    },
                }
            )
            return
        stored_plan = _load_scan_plan(data_dir, scan_plan_id) if scan_plan_id else {}
        if (
            scan_plan_id != expected_plan_id
            or stored_plan.get("worldFingerprint") != fingerprint
            or stored_plan.get("settingsFingerprint") != settings_fingerprint
        ):
            emit(
                {
                    "v": 1,
                    "id": request_id,
                    "type": "response.error",
                    "error": {
                        "code": "PLAN_INVALIDATED",
                        "message": "Translation settings changed after Scan Only. Run the scan again.",
                        "recoverable": True,
                    },
                }
            )
            return
        excluded = [
            str(candidate_id)
            for candidate_id in body.get("excludedCandidateIds", [])
            if isinstance(candidate_id, str) and len(candidate_id) == 20
        ]
        known_candidate_ids = {
            str(candidate.get("id"))
            for candidate in stored_plan.get("candidates", [])
            if isinstance(candidate, dict)
        }
        if any(candidate_id not in known_candidate_ids for candidate_id in excluded):
            raise ValueError("An excluded candidate is not part of this scan plan")
        candidate_by_id = {
            str(candidate.get("id")): str(candidate.get("source"))
            for candidate in stored_plan.get("candidates", [])
            if isinstance(candidate, dict)
        }
        raw_overrides = body.get("candidateOverrides") or {}
        if not isinstance(raw_overrides, dict):
            raise ValueError("Candidate overrides must be an object")
        overrides_by_source: dict[str, str] = {}
        for candidate_id, translated in raw_overrides.items():
            if candidate_id not in candidate_by_id or not isinstance(translated, str):
                raise ValueError("A manual override is not part of this scan plan")
            cleaned = translated.strip()
            if not cleaned or len(cleaned) > 32_000:
                raise ValueError("A manual override is empty or too long")
            overrides_by_source[candidate_by_id[candidate_id]] = cleaned
        included_ids = known_candidate_ids.difference(excluded)
        overridden_ids = set(raw_overrides)
        manual_only = bool(included_ids) and included_ids.issubset(overridden_ids)
        report = _run_translator(
            world,
            dry_run=False,
            report_path=report_dir / "translate-report.json",
            fingerprint=fingerprint,
            data_dir=data_dir,
            excluded_candidate_ids=excluded,
            progress_callback=lambda event: emit(
                {"v": 1, "id": request_id, "type": "translate.progress", "payload": event}
            ),
            cancel_check=(lambda: cancel_path.is_file()) if cancel_path else None,
            api_key_override=str(body.get("apiKey") or ""),
            allow_keyring_fallback=body.get("credentialOwner") != "rust",
            manual_overrides=overrides_by_source,
            skip_provider_validation=manual_only,
            scan_plan_id=scan_plan_id,
            resume_from_checkpoint=kind == "translate.resume",
            on_translation_failure=str(body.get("failurePolicy") or "stop"),
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
                    "providerRequests": report.get("provider_requests", 0),
                    "backupSetId": report.get("backup_set_id", ""),
                    "preTranslate": PRE_TRANSLATE,
                    "localhostServer": False,
                    "errors": report.get("errors", []),
                    "warnings": report.get("warnings", []),
                    "translation": report.get("translation") or {},
                    "translationFailures": report.get("translation_failures", []),
                    "keptOriginalSamples": report.get("kept_original_samples", []),
                    "usage": report.get("usage") or {},
                },
            }
        )
        return
    if kind == "backups.list":
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {"backups": list_backup_sets(world), "localhostServer": False},
            }
        )
        return
    if kind == "restore.start":
        backup_id = str(body.get("backupSetId") or "latest")
        selected = BackupSet(world, backup_id)
        recovery_id = selected.restore()
        emit(
            {
                "v": 1,
                "id": request_id,
                "type": "response.ok",
                "payload": {
                    "status": "restored",
                    "backupSetId": selected.backup_id,
                    "recoverySetId": recovery_id,
                    "localhostServer": False,
                },
            }
        )
        return
    emit(
        {
            "v": 1,
            "id": request_id,
            "type": "response.error",
            "error": {"code": "UNKNOWN_MESSAGE", "message": f"Unknown message {kind}"},
        }
    )


def serve(report_dir: Path, data_dir: Path, cancel_path: Path | None = None) -> None:
    hello()
    for line in sys.stdin:
        if not line.strip():
            continue
        message: dict = {}
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("Protocol message must be an object")
            if message.get("v") != 1:
                raise ValueError("Unsupported protocol version")
            handle(message, report_dir, data_dir, cancel_path)
        except (json.JSONDecodeError, ValueError) as exc:
            emit(
                {
                    "v": 1,
                    "id": message.get("id", ""),
                    "type": "response.error",
                    "error": {"code": "INVALID_REQUEST", "message": str(exc), "recoverable": True},
                }
            )
        except Exception:
            emit(
                {
                    "v": 1,
                    "id": message.get("id", ""),
                    "type": "response.error",
                    "error": {
                        "code": "OPERATION_FAILED",
                        "message": "The operation failed. The world was not marked as completed.",
                        "recoverable": True,
                    },
                }
            )


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
    parser.add_argument("--cancel-file", default="")
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
        cancel_path = Path(args.cancel_file) if args.cancel_file else None
        serve(report_dir, data_dir, cancel_path)
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
