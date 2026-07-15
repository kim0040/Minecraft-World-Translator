from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import io
import json
import math
import os
import re
import shutil
import tempfile
import time
import tomllib
import zlib
from copy import deepcopy
from pathlib import Path
from typing import Any

from env_utils import load_dotenv_chain
from llm_backends import (
    LLMProviderClient,
    PROVIDER_SPECS,
    default_base_url,
    enhance_style_prompt,
    infer_provider,
    provider_choices,
    resolve_api_key,
    resolve_base_url,
    resolve_model,
)

try:
    from nbt import nbt
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing dependency: `nbt`.\n"
        "Install it first, for example:\n"
        "  python3 -m pip install nbtlib anvil-parser nbt"
    ) from exc


STYLE_PRESETS: dict[str, str] = {
    "neutral": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 자연스러운 {target_language}로 번역해라.
[스타일 규칙]
1. 게임 진행 정보와 퍼즐 힌트는 이해하기 쉽게 번역한다.
2. 고유명사, 인명, 제작자 이름, SNS 핸들, 브랜드명은 함부로 번역하지 말고 필요한 경우만 음역한다.
3. 특수 기호(§, \\n, {0}, %s, %% 등), JSON 구조, 키 이름은 절대 망가뜨리지 마라.
4. 결과물에는 설명 없이 번역 결과만 반환해라.
""".strip(),
    "casual": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 친근하고 캐주얼한 {target_language}로 번역해라.
[스타일 규칙]
1. 대사는 자연스럽고 읽기 쉽게 옮긴다.
2. 퍼즐 힌트나 시스템 안내는 의미 전달이 최우선이다.
3. 고유명사, 인명, 제작자 이름, SNS 핸들, 브랜드명은 함부로 번역하지 말고 필요한 경우만 음역한다.
4. 특수 기호(§, \\n, {0}, %s, %% 등), JSON 구조, 키 이름은 절대 망가뜨리지 마라.
5. 결과물에는 설명 없이 번역 결과만 반환해라.
""".strip(),
    "formal": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 차분하고 명료한 {target_language}로 번역해라.
[스타일 규칙]
1. 문체는 정돈되고 일관되게 유지한다.
2. 퍼즐 힌트나 시스템 안내는 의미 전달이 최우선이다.
3. 고유명사, 인명, 제작자 이름, SNS 핸들, 브랜드명은 함부로 번역하지 말고 필요한 경우만 음역한다.
4. 특수 기호(§, \\n, {0}, %s, %% 등), JSON 구조, 키 이름은 절대 망가뜨리지 마라.
5. 결과물에는 설명 없이 번역 결과만 반환해라.
""".strip(),
    "polite": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 친절하고 정중한 존댓말을 사용하는 {target_language}로 번역해라.
[스타일 규칙]
1. '~해요', '~습니다' 등의 존댓말을 사용하여 예의 바른 느낌을 준다.
2. 플레이어에게 다정하게 안내하는 느낌을 살린다.
3. 고유명사와 특수 기호는 의미를 훼손하지 않아야 한다.
4. 결과물에는 설명 없이 번역 결과만 반환해라.
""".strip(),
    "story": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 몰입감 넘치는 소설이나 이야기풍의 {target_language}로 번역해라.
[스타일 규칙]
1. 단순 직역을 피하고 상황과 인물의 감정이 느껴지도록 윤문한다.
2. 판타지나 어드벤처 소설에 나올 법한 수려하고 극적인 문체를 사용한다.
3. 하지만 시스템 안내 등 핵심 정보가 묻히지 않도록 주의한다.
4. 결과물에는 설명 없이 번역 결과만 반환해라.
""".strip(),
    "custom": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 {target_language}로 번역해라. 사용자의 추가 지시에 전적으로 따라라.
""".strip(),
}


DEFAULT_CONFIG: dict[str, Any] = {
    "world_dir": "",
    "report_path": "",
    "dry_run": False,
    "backup": True,
    "backup_suffix": ".bak_translate",
    "batch_size": 40,
    "temperature": 0.3,
    "inherit_translate_py": True,
    "translate_py_path": "./translate.py",
    "api": {
        "provider": "comet",
        "api_key": "",
        "base_url": "",
        "model": "",
        "request_timeout": 120,
        "rpm_limit": 0,
        "tpm_limit": 0,
    },
    "prompt": {
        "target_language": "한국어",
        "style_preset": "neutral",
        "style_prompt": "",
        "custom_system_prompt": "",
    },
    "scan": {
        "region_dirs": [
            "region",
            "entities",
            "DIM-1/region",
            "DIM-1/entities",
            "DIM1/region",
            "DIM1/entities",
        ],
        "skip_patterns": ["*.bak_translate"],
        "translate_signs": True,
        "translate_books": True,
        "translate_custom_names": True,
        "translate_item_names": True,
        "translate_lore": True,
        "translate_titles": True,
        "translate_filtered_titles": True,
        "translate_command_output": True,
        "skip_command_like_text": True,
        "component_translate_key_prefixes": [],
        "overrides": {},
    },
    "resource_pack": {
        "enabled": False,
        "zip_paths": [],
        "source_lang_files": ["en_us.json", "zh_cn.json"],
        "target_lang_file": "ko_kr.json",
        "skip_if_target_exists": False,
    },
    "runtime": {
        "checkpoint_enabled": True,
        "checkpoint_path": "",
        "resume_from_checkpoint": False,
        "continue_on_file_error": True,
        "max_batch_retries": 3,
        "max_file_write_retries": 2,
    },
}


class TextRef:
    def __init__(
        self,
        kind: str,
        *,
        tag: Any = None,
        obj: Any = None,
        key: str = "",
        path: str = "",
    ) -> None:
        self.kind = kind
        self.tag = tag
        self.obj = obj
        self.key = key
        self.path = path


class TranslationCancelled(RuntimeError):
    pass


def merge_nested(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_nested(result[key], value)
        else:
            result[key] = value
    return result


def load_toml_config(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent)) as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        if path.exists():
            shutil.copymode(path, tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


def write_bytes_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=str(path.parent)) as tmp:
            tmp.write(content)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        if path.exists():
            shutil.copymode(path, tmp_path)
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


def load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_legacy_translate_defaults(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    names = {"API_KEY", "BASE_URL", "MODEL", "SYSTEM_PROMPT"}
    values: dict[str, str] = {}

    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in names:
            continue
        try:
            values[target.id] = ast.literal_eval(node.value)
        except Exception:
            continue

    return values


def apply_cli_overrides(config: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    result = deepcopy(config)

    if args.world_dir:
        result["world_dir"] = args.world_dir
    if args.report_path:
        result["report_path"] = args.report_path
    if args.provider:
        result["api"]["provider"] = args.provider
    if args.api_key:
        result["api"]["api_key"] = args.api_key
    if args.base_url:
        result["api"]["base_url"] = args.base_url
    if args.model:
        result["api"]["model"] = args.model
    if args.target_language:
        result["prompt"]["target_language"] = args.target_language
    if args.style_preset:
        result["prompt"]["style_preset"] = args.style_preset
    if args.style_prompt:
        result["prompt"]["style_prompt"] = args.style_prompt
    if args.custom_system_prompt:
        result["prompt"]["custom_system_prompt"] = args.custom_system_prompt
    if args.batch_size is not None:
        result["batch_size"] = args.batch_size
    if args.temperature is not None:
        result["temperature"] = args.temperature
    if args.dry_run:
        result["dry_run"] = True
    if args.no_backup:
        result["backup"] = False
    if args.resource_pack_zip:
        result["resource_pack"]["zip_paths"] = args.resource_pack_zip
        result["resource_pack"]["enabled"] = True
    if args.enable_resource_pack_translation:
        result["resource_pack"]["enabled"] = True
    if args.disable_resource_pack_translation:
        result["resource_pack"]["enabled"] = False
    if getattr(args, "resume", False):
        result["runtime"]["resume_from_checkpoint"] = True

    return result


def normalize_config(config: dict[str, Any], config_path: Path | None) -> dict[str, Any]:
    result = deepcopy(config)
    project_dir = Path(__file__).resolve().parent
    load_dotenv_chain(
        project_dir / ".env",
        project_dir.parent / ".env",
    )

    translate_py_path = Path(result["translate_py_path"])
    if not translate_py_path.is_absolute() and config_path is not None:
        translate_py_path = (config_path.parent / translate_py_path).resolve()
    else:
        translate_py_path = translate_py_path.resolve()

    if result.get("inherit_translate_py", True):
        legacy = load_legacy_translate_defaults(translate_py_path)
        if not result["api"]["api_key"]:
            result["api"]["api_key"] = legacy.get("API_KEY", "")
        if not result["api"]["base_url"]:
            result["api"]["base_url"] = legacy.get("BASE_URL", "")
        if not result["api"]["model"]:
            result["api"]["model"] = legacy.get("MODEL", "")
        if not result["prompt"]["custom_system_prompt"] and not result["prompt"]["style_prompt"]:
            legacy_prompt = legacy.get("SYSTEM_PROMPT", "").strip()
            if legacy_prompt and result["prompt"]["style_preset"] == "custom":
                result["prompt"]["custom_system_prompt"] = legacy_prompt

    provider = infer_provider(result["api"].get("provider"), result["api"].get("base_url", ""))
    if provider not in PROVIDER_SPECS:
        raise ValueError(f"Unsupported provider: {provider}")
    result["api"]["provider"] = provider

    result["api"]["base_url"] = resolve_base_url(provider, result["api"]["base_url"])
    result["api"]["model"] = resolve_model(provider, result["api"]["model"])

    result["api"]["api_key"] = resolve_api_key(provider, result["api"]["api_key"])

    world_dir_raw = str(result["world_dir"]).strip()
    if world_dir_raw:
        world_dir = Path(world_dir_raw).expanduser()
        if not world_dir.is_absolute() and config_path is not None:
            world_dir = (config_path.parent / world_dir).resolve()
        else:
            world_dir = world_dir.resolve()
        result["world_dir"] = str(world_dir)

        report_path = result["report_path"] or str(world_dir / "translation_report.json")
        report_path = Path(report_path).expanduser()
        if not report_path.is_absolute():
            report_path = (world_dir / report_path).resolve()
        result["report_path"] = str(report_path)
        checkpoint_path = result["runtime"]["checkpoint_path"] or str(world_dir / ".translation_checkpoint.json")
        checkpoint_path = Path(checkpoint_path).expanduser()
        if not checkpoint_path.is_absolute():
            checkpoint_path = (world_dir / checkpoint_path).resolve()
        else:
            checkpoint_path = checkpoint_path.resolve()
        result["runtime"]["checkpoint_path"] = str(checkpoint_path)
    else:
        result["world_dir"] = ""
        result["report_path"] = result["report_path"] or ""
        result["runtime"]["checkpoint_path"] = result["runtime"]["checkpoint_path"] or ""

    zip_paths: list[str] = []
    for zip_path in result["resource_pack"]["zip_paths"]:
        path_obj = Path(zip_path).expanduser()
        if not path_obj.is_absolute() and result["world_dir"]:
            path_obj = (world_dir / path_obj).resolve()
        zip_paths.append(str(path_obj))
    result["resource_pack"]["zip_paths"] = zip_paths

    return result


class BatchTranslator:
    def __init__(
        self,
        config: dict[str, Any],
        progress_callback: Any = None,
        cancel_check: Any = None,
        initial_cache: dict[str, str] | None = None,
    ) -> None:
        self.config = config
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        self.cache: dict[str, str] = dict(initial_cache or {})
        self.overrides: dict[str, str] = dict(config["scan"]["overrides"])
        self.client = LLMProviderClient(config)
        self.rpm_limit = int(config["api"].get("rpm_limit", 0))
        self.tpm_limit = int(config["api"].get("tpm_limit", 0))
        self.last_request_time = 0.0

    def throttle(self, batch_size: int) -> None:
        if self.rpm_limit <= 0 and self.tpm_limit <= 0:
            return
        
        now = time.time()
        delay = 0.0
        if self.rpm_limit > 0:
            delay = max(delay, 60.0 / self.rpm_limit)
        
        if self.tpm_limit > 0:
            estimated_tokens = batch_size * 50
            delay = max(delay, (estimated_tokens / self.tpm_limit) * 60.0)
            
        elapsed = now - self.last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request_time = time.time()

    def emit(self, event: str, **payload: Any) -> None:
        if self.progress_callback is not None:
            self.progress_callback({"event": event, **payload})

    def ensure_not_cancelled(self) -> None:
        if self.cancel_check is not None and self.cancel_check():
            raise TranslationCancelled("Translation was cancelled by the user.")

    def system_prompt(self) -> str:
        prompt_config = self.config["prompt"]
        if prompt_config["custom_system_prompt"]:
            base = prompt_config["custom_system_prompt"].strip()
        else:
            preset = STYLE_PRESETS[prompt_config["style_preset"]]
            base = preset.format(target_language=prompt_config["target_language"])

        extra = prompt_config["style_prompt"].strip()
        if extra:
            base = f"{base}\n\n[추가 스타일 지시]\n{extra}"

        return (
            f"{base}\n\n"
            "반드시 JSON 형식으로 반환해라. 키(Key)는 그대로 두고 값(Value)만 번역해라."
        )

    def translate_texts(self, texts: list[str]) -> dict[str, str]:
        self.ensure_not_cancelled()
        missing: list[str] = []
        for text in texts:
            if text in self.cache:
                continue
            if text in self.overrides:
                self.cache[text] = self.overrides[text]
            else:
                missing.append(text)

        if not missing:
            return {text: self.cache[text] for text in texts}

        batch_size = max(1, int(self.config["batch_size"]))
        for start in range(0, len(missing), batch_size):
            self.ensure_not_cancelled()
            batch = missing[start : start + batch_size]
            translated = self._translate_batch(batch, batch_size)
            for original, localized in translated.items():
                self.cache[original] = localized

        return {text: self.cache.get(text, text) for text in texts}

    def _translate_batch(self, texts: list[str], batch_size: int) -> dict[str, str]:
        payload = {str(i): text for i, text in enumerate(texts)}
        max_retries = max(1, int(self.config["runtime"]["max_batch_retries"]))
        for attempt in range(1, max_retries + 1):
            self.ensure_not_cancelled()
            try:
                self.throttle(len(texts))
                self.emit("translation_batch_start", batch_size=len(texts), attempt=attempt, max_attempts=max_retries)
                parsed = self.client.translate_mapping(
                    payload,
                    system_prompt=self.system_prompt(),
                    temperature=float(self.config["temperature"]),
                )
                self.emit("translation_batch_done", batch_size=len(texts), attempt=attempt)
                return {
                    text: parsed.get(str(i), text)
                    for i, text in enumerate(texts)
                }
            except TranslationCancelled:
                raise
            except Exception as exc:
                self.emit(
                    "translation_batch_error",
                    batch_size=len(texts),
                    attempt=attempt,
                    max_attempts=max_retries,
                    message=str(exc),
                )
                if attempt < max_retries:
                    time.sleep(min(1.5 * attempt, 4.0))

        if batch_size > 1:
            next_size = max(1, batch_size // 5)
            merged: dict[str, str] = {}
            for i in range(0, len(texts), next_size):
                self.ensure_not_cancelled()
                merged.update(self._translate_batch(texts[i : i + next_size], next_size))
            return merged
        return {text: text for text in texts}


class WorldTranslator:
    def __init__(
        self,
        config: dict[str, Any],
        progress_callback: Any = None,
        cancel_check: Any = None,
    ) -> None:
        self.config = config
        self.scan_config = config["scan"]
        self.runtime_config = config["runtime"]
        self.component_prefixes = tuple(self.scan_config["component_translate_key_prefixes"])
        self.skip_patterns = tuple(self.scan_config["skip_patterns"])
        self.progress_callback = progress_callback
        self.cancel_check = cancel_check
        self.checkpoint_path = Path(self.runtime_config["checkpoint_path"]) if self.runtime_config["checkpoint_path"] else None
        self.resume_from_checkpoint = bool(self.runtime_config["resume_from_checkpoint"])
        self.completed_region_files: set[str] = set()
        self.completed_resource_pack_paths: set[str] = set()
        self.translation_cache: dict[str, str] = {}
        self.candidate_texts: set[str] = set()
        self.file_errors: list[dict[str, Any]] = []
        self.report: dict[str, Any] = {
            "world_dir": config["world_dir"],
            "dry_run": config["dry_run"],
            "provider": config["api"]["provider"],
            "model": config["api"]["model"],
            "status": "running",
            "changed_files": [],
            "resource_packs": [],
            "errors": [],
        }
        self.load_checkpoint()
        self.translator = None if config["dry_run"] else BatchTranslator(
            config,
            progress_callback=self.emit,
            cancel_check=self.is_cancelled,
            initial_cache=self.translation_cache,
        )

    def emit(self, event: str, **payload: Any) -> None:
        if self.progress_callback is not None:
            self.progress_callback({"event": event, **payload})

    def is_cancelled(self) -> bool:
        return bool(self.cancel_check is not None and self.cancel_check())

    def ensure_not_cancelled(self) -> None:
        if self.is_cancelled():
            self.report["status"] = "cancelled"
            self.save_checkpoint()
            raise TranslationCancelled("Translation was cancelled by the user.")

    def checkpoint_config_fingerprint(self) -> str:
        """Identify settings that would make a resumed translation inconsistent."""
        relevant_config = {
            "world_dir": self.config["world_dir"],
            "dry_run": self.config["dry_run"],
            "batch_size": self.config["batch_size"],
            "temperature": self.config["temperature"],
            "api": {
                "provider": self.config["api"]["provider"],
                "base_url": self.config["api"]["base_url"],
                "model": self.config["api"]["model"],
            },
            "prompt": self.config["prompt"],
            "scan": self.config["scan"],
            "resource_pack": self.config["resource_pack"],
        }
        encoded = json.dumps(relevant_config, ensure_ascii=False, sort_keys=True).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def checkpoint_payload(self) -> dict[str, Any]:
        self.refresh_report_counts()
        return {
            "version": 2,
            "world_dir": self.config["world_dir"],
            "provider": self.config["api"]["provider"],
            "model": self.config["api"]["model"],
            "dry_run": self.config["dry_run"],
            "config_fingerprint": self.checkpoint_config_fingerprint(),
            "completed_region_files": sorted(self.completed_region_files),
            "completed_resource_pack_paths": sorted(self.completed_resource_pack_paths),
            "translation_cache": self.translator.cache if self.translator is not None else self.translation_cache,
            "candidate_texts": sorted(self.candidate_texts),
            "report": self.report,
            "saved_at": time.time(),
        }

    def load_checkpoint(self) -> None:
        if not self.resume_from_checkpoint or self.checkpoint_path is None:
            return
        checkpoint = load_json_file(self.checkpoint_path)
        if not checkpoint:
            return
        if checkpoint.get("world_dir") != self.config["world_dir"]:
            self.emit("checkpoint_ignored", reason="world_dir")
            return
        if checkpoint.get("config_fingerprint") != self.checkpoint_config_fingerprint():
            self.emit("checkpoint_ignored", reason="settings")
            return
        self.completed_region_files = set(checkpoint.get("completed_region_files", []))
        self.completed_resource_pack_paths = set(checkpoint.get("completed_resource_pack_paths", []))
        self.translation_cache = dict(checkpoint.get("translation_cache", {}))
        self.candidate_texts = set(checkpoint.get("candidate_texts", []))
        saved_report = checkpoint.get("report")
        if isinstance(saved_report, dict):
            self.report.update(saved_report)
            self.report["status"] = "running"
        self.emit(
            "checkpoint_loaded",
            completed_region_files=len(self.completed_region_files),
            completed_resource_packs=len(self.completed_resource_pack_paths),
        )

    def clear_checkpoint(self) -> None:
        if self.checkpoint_path is not None and self.checkpoint_path.exists():
            try:
                self.checkpoint_path.unlink()
            except FileNotFoundError:
                pass

    def save_checkpoint(self) -> None:
        if not self.runtime_config["checkpoint_enabled"] or self.checkpoint_path is None:
            return
        write_text_atomic(
            self.checkpoint_path,
            json.dumps(self.checkpoint_payload(), ensure_ascii=False, indent=2),
        )

    def refresh_report_counts(self) -> None:
        self.report["changed_file_count"] = len(
            [item for item in self.report["changed_files"] if item.get("changed_chunks", 0) > 0]
        )
        self.report["candidate_file_count"] = len(
            [item for item in self.report["changed_files"] if item.get("candidates", 0) > 0]
        )
        self.report["candidate_text_count"] = len(self.candidate_texts)

    def run(self) -> dict[str, Any]:
        world_dir = Path(self.config["world_dir"]).resolve()
        if not world_dir.exists() or not world_dir.is_dir():
            msg = f"World directory not found or invalid: {world_dir}"
            self.emit("file_error", file=str(world_dir), message=msg)
            self.report["status"] = "failed"
            self.report["error"] = msg
            return self.report

        try:
            if self.config["resource_pack"]["enabled"]:
                self.ensure_not_cancelled()
                self.emit("resource_pack_start")
                self.translate_resource_packs()
                self.emit(
                    "resource_pack_done",
                    count=len(self.report["resource_packs"]),
                    candidate_text_count=len(self.candidate_texts),
                )

            region_files = self.iter_region_files()
            pending_files = [path for path in region_files if str(path) not in self.completed_region_files]
            total_files = len(pending_files)
            self.emit(
                "scan_start",
                total_files=total_files,
                skipped_completed=len(region_files) - total_files,
            )
            for index, file_path in enumerate(pending_files, start=1):
                self.ensure_not_cancelled()
                self.emit("file_start", index=index, total=total_files, file=str(file_path))
                try:
                    result = self.process_region_file(file_path)
                except TranslationCancelled:
                    raise
                except Exception as exc:
                    result = {
                        "file": str(file_path),
                        "changed_chunks": 0,
                        "unique_texts": 0,
                        "candidates": 0,
                        "skipped": "file_error",
                        "error": str(exc),
                    }
                    self.file_errors.append(result)
                    self.report["errors"].append(result)
                    self.emit("file_error", file=str(file_path), message=str(exc))
                    if not self.runtime_config["continue_on_file_error"]:
                        raise

                if result.get("skipped") not in {"file_error", "parse_error"}:
                    self.completed_region_files.add(str(file_path))
                if result["changed_chunks"] > 0 or result.get("candidates", 0) > 0 or result.get("skipped"):
                    self.report["changed_files"].append(result)
                self.save_checkpoint()
                self.emit(
                    "file_done",
                    index=index,
                    total=total_files,
                    file=str(file_path),
                    changed_chunks=result["changed_chunks"],
                    candidates=result.get("candidates", 0),
                    candidate_text_count=len(self.candidate_texts),
                    skipped=result.get("skipped", ""),
                )

            self.refresh_report_counts()
            self.report["status"] = "completed"
            self.write_report()
            self.clear_checkpoint()
            self.emit(
                "done",
                changed_file_count=self.report["changed_file_count"],
                candidate_file_count=self.report["candidate_file_count"],
                candidate_text_count=self.report["candidate_text_count"],
                error_count=len(self.report["errors"]),
            )
            return self.report
        except TranslationCancelled:
            self.report["status"] = "cancelled"
            self.refresh_report_counts()
            self.write_report()
            self.save_checkpoint()
            self.emit(
                "cancelled",
                changed_file_count=self.report.get("changed_file_count", 0),
                candidate_file_count=self.report.get("candidate_file_count", 0),
                candidate_text_count=self.report.get("candidate_text_count", 0),
            )
            return self.report
        except Exception as exc:
            error_entry = {
                "scope": "run",
                "message": str(exc) or exc.__class__.__name__,
            }
            self.report["status"] = "failed"
            self.report["errors"].append(error_entry)
            self.refresh_report_counts()
            self.write_report()
            self.save_checkpoint()
            self.emit("fatal_error", message=error_entry["message"])
            raise

    def iter_region_files(self) -> list[Path]:
        world_dir = Path(self.config["world_dir"]).resolve()
        files: list[Path] = []
        seen: set[Path] = set()
        for configured_dir in self.scan_config.get("region_dirs", []):
            directory = Path(str(configured_dir)).expanduser()
            directory = directory.resolve() if directory.is_absolute() else (world_dir / directory).resolve()
            if directory != world_dir and world_dir not in directory.parents:
                raise ValueError(f"Configured region directory is outside the world folder: {configured_dir}")
            if not directory.is_dir():
                continue
            for path in sorted(directory.glob("*.mca")):
                relative_path = path.relative_to(world_dir).as_posix()
                if any(
                    fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(relative_path, pattern)
                    for pattern in self.skip_patterns
                ):
                    continue
                resolved_path = path.resolve()
                if resolved_path not in seen:
                    seen.add(resolved_path)
                    files.append(resolved_path)
        return files

    _SKIP_NAMESPACE_PREFIXES = (
        "minecraft:", "forge:", "neoforge:", "fabric:",
        "mod:", "kubejs:", "ftbquests:", "chipped:",
        "tconstruct:", "mekanism:", "thermal:", "botania:",
        "create:", "immersiveengineering:",
    )

    _NOISE_PATTERNS = re.compile(
        r"^(?:"
        r"[0-9]+(?:\.[0-9]+)?%?"       # pure numbers like "42", "3.14", "100%"
        r"|[\u2000-\u2BFF\u2600-\u27BF\uFE30-\uFE4F\uFFF0-\uFFFF]+"  # symbols
        r"|\.{2,}"                      # ellipsis-like dots "..."
        r"|-{2,}"                       # dashes "---"
        r"|={2,}"                       # equals "=="
        r"|#{1,3}"                      # hash markers
        r")$",
    )

    def should_translate_text(self, text: str) -> bool:
        if not isinstance(text, str):
            return False
        stripped = text.strip()
        if not stripped:
            return False

        if stripped in ("@", "#", "!", "?", ".", ",", "-", "~", "/"):
            return False

        if stripped.startswith(self._SKIP_NAMESPACE_PREFIXES):
            return False

        if self.scan_config["skip_command_like_text"] and stripped.startswith("/"):
            return False

        if stripped.startswith("@") and " " not in stripped:
            return False

        if all(not ch.isalpha() for ch in stripped):
            return False

        if self._NOISE_PATTERNS.match(stripped):
            return False

        has_alpha = any(ch.isalpha() for ch in stripped)
        has_cjk = any(
            "\uac00" <= ch <= "\ud7a3"   # Hangul
            or "\u4e00" <= ch <= "\u9fff" # CJK Unified
            or "\u3040" <= ch <= "\u309f" # Hiragana
            or "\u30a0" <= ch <= "\u30ff" # Katakana
            for ch in stripped
        )

        if not has_alpha and not has_cjk:
            return False

        if len(stripped) == 1:
            return has_cjk

        if len(stripped) <= 3 and not has_cjk:
            if stripped.isupper():
                return False

        if len(stripped) <= 4 and not has_cjk:
            all_upper_alpha = all(ch.isupper() or ch in " .-" for ch in stripped)
            if all_upper_alpha and " " in stripped:
                return False
            is_roman = all(ch in "IVXLCDM " for ch in stripped)
            if is_roman and stripped.strip():
                return False

        return True

    @staticmethod
    def parse_nbt_bytes(raw_nbt: bytes) -> nbt.NBTFile:
        return nbt.NBTFile(buffer=io.BytesIO(raw_nbt))

    @staticmethod
    def dump_nbt_bytes(root: nbt.NBTFile) -> bytes:
        buf = io.BytesIO()
        root.write_file(buffer=buf)
        return buf.getvalue()

    @staticmethod
    def load_chunk_payload(data: bytes, sector_offset: int) -> tuple[int, bytes, int]:
        byte_offset = sector_offset * 4096
        if byte_offset + 5 > len(data):
            raise ValueError("Chunk offset out of bounds")
        length = int.from_bytes(data[byte_offset : byte_offset + 4], "big")
        if length <= 1 or byte_offset + 4 + length > len(data):
            raise ValueError("Invalid chunk length")
        compression = data[byte_offset + 4]
        payload = data[byte_offset + 5 : byte_offset + 4 + length]
        return compression, payload, length

    @staticmethod
    def decompress_payload(compression: int, payload: bytes) -> bytes:
        if compression == 1:
            import gzip

            return gzip.decompress(payload)
        if compression == 2:
            return zlib.decompress(payload)
        if compression == 3:
            return payload
        raise ValueError(f"Unsupported compression type: {compression}")

    @staticmethod
    def compress_payload(compression: int, raw_nbt: bytes) -> bytes:
        if compression == 1:
            import gzip

            return gzip.compress(raw_nbt)
        if compression == 2:
            return zlib.compress(raw_nbt)
        if compression == 3:
            return raw_nbt
        raise ValueError(f"Unsupported compression type: {compression}")

    @staticmethod
    def parse_text_component(raw: str) -> Any:
        return json.loads(raw)

    @staticmethod
    def serialize_text_component(component: Any) -> str:
        return json.dumps(component, ensure_ascii=False, separators=(",", ":"))

    def backup_once(self, path: Path) -> None:
        if not self.config["backup"]:
            return
        backup_path = path.with_name(path.name + self.config["backup_suffix"])
        if not backup_path.exists():
            shutil.copy2(path, backup_path)

    def extract_command_json(self, command: str) -> tuple[str, str] | None:
        if not isinstance(command, str):
            return None

        match = re.match(r"^(tellraw\s+\S+\s+)([\[{].*)$", command)
        if match:
            return match.group(1), match.group(2)
        match = re.match(r"^(title\s+\S+\s+(?:title|subtitle|actionbar)\s+)([\[{].*)$", command)
        if match:
            return match.group(1), match.group(2)
        return None

    def text_from_translate_key(self, key: str) -> str:
        for prefix in self.component_prefixes:
            if key.startswith(prefix):
                tail = key[len(prefix) :]
                return tail.replace("_", " ").replace(".", " ")
        return key

    def collect_json_text_refs(self, node: Any, refs: list[TextRef], path: str) -> None:
        if isinstance(node, dict):
            text_value = node.get("text")
            if isinstance(text_value, str) and self.should_translate_text(text_value):
                refs.append(TextRef("json_text", obj=node, key="text", path=path))
            elif (
                isinstance(text_value, dict)
                and set(text_value.keys()) == {"translate"}
                and isinstance(text_value.get("translate"), str)
                and any(text_value["translate"].startswith(prefix) for prefix in self.component_prefixes)
            ):
                refs.append(TextRef("translate_key", obj=node, key="text", path=path))

            if self.scan_config["translate_command_output"]:
                click_event = node.get("clickEvent")
                if isinstance(click_event, dict) and isinstance(click_event.get("value"), str):
                    self.collect_command_refs(click_event["value"], refs, f"{path}.clickEvent.value")

            hover_event = node.get("hoverEvent")
            if isinstance(hover_event, dict):
                hover_value = hover_event.get("value")
                if self.scan_config["translate_command_output"] and isinstance(hover_value, str):
                    self.collect_command_refs(hover_value, refs, f"{path}.hoverEvent.value")
                for hover_key, hover_item in hover_event.items():
                    if hover_key == "value":
                        continue
                    self.collect_json_text_refs(hover_item, refs, f"{path}.hoverEvent.{hover_key}")

            for key, value in node.items():
                if key in {"text", "clickEvent", "hoverEvent"}:
                    continue
                self.collect_json_text_refs(value, refs, f"{path}.{key}")
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                self.collect_json_text_refs(item, refs, f"{path}[{idx}]")

    def collect_command_refs(self, command: str, refs: list[TextRef], path: str) -> None:
        extracted = self.extract_command_json(command)
        if not extracted:
            return
        _, json_part = extracted
        try:
            component = json.loads(json_part)
        except json.JSONDecodeError:
            return
        self.collect_json_text_refs(component, refs, path)

    def collect_tag_refs(self, tag: Any, refs: list[TextRef], path: str) -> None:
        if isinstance(tag, nbt.TAG_Compound):
            for key, value in tag.items():
                child_path = f"{path}/{key}"
                if isinstance(value, nbt.TAG_String):
                    raw = value.value
                    is_sign = key in {"Text1", "Text2", "Text3", "Text4"} and self.scan_config["translate_signs"]
                    is_custom_name = key == "CustomName" and self.scan_config["translate_custom_names"]
                    is_item_name = "/display/Name" in child_path and self.scan_config["translate_item_names"]
                    if is_sign or is_custom_name or is_item_name:
                        try:
                            component = self.parse_text_component(raw)
                        except json.JSONDecodeError:
                            if self.should_translate_text(raw):
                                refs.append(TextRef("plain_tag", tag=value, path=child_path))
                        else:
                            self.collect_json_text_refs(component, refs, child_path)
                            refs.append(TextRef("json_tag", tag=value, path=child_path))
                    elif key == "Command" and self.scan_config["translate_command_output"]:
                        self.collect_command_refs(raw, refs, child_path)
                        refs.append(TextRef("command_tag", tag=value, path=child_path))
                    elif key == "title" and self.scan_config["translate_titles"]:
                        if self.should_translate_text(raw):
                            refs.append(TextRef("plain_tag", tag=value, path=child_path))
                    elif key == "filtered_title" and self.scan_config["translate_filtered_titles"]:
                        if self.should_translate_text(raw):
                            refs.append(TextRef("plain_tag", tag=value, path=child_path))
                    else:
                        self.collect_tag_refs(value, refs, child_path)
                else:
                    self.collect_tag_refs(value, refs, child_path)
        elif isinstance(tag, nbt.TAG_List):
            for idx, item in enumerate(tag):
                child_path = f"{path}/{idx}"
                if isinstance(item, nbt.TAG_String):
                    raw = item.value
                    is_page = "/pages/" in child_path and self.scan_config["translate_books"]
                    is_lore = "/display/Lore/" in child_path and self.scan_config["translate_lore"]
                    if is_page or is_lore:
                        try:
                            component = self.parse_text_component(raw)
                        except json.JSONDecodeError:
                            if self.should_translate_text(raw):
                                refs.append(TextRef("plain_tag", tag=item, path=child_path))
                        else:
                            self.collect_json_text_refs(component, refs, child_path)
                            refs.append(TextRef("json_tag", tag=item, path=child_path))
                else:
                    self.collect_tag_refs(item, refs, child_path)

    def extract_unique_texts(self, refs: list[TextRef]) -> list[str]:
        ordered: list[str] = []
        seen: set[str] = set()

        def add_text(value: str) -> None:
            if self.should_translate_text(value) and value not in seen:
                seen.add(value)
                ordered.append(value)

        for ref in refs:
            if ref.kind == "plain_tag":
                add_text(ref.tag.value)
            elif ref.kind == "json_text":
                add_text(ref.obj[ref.key])
            elif ref.kind == "translate_key":
                add_text(self.text_from_translate_key(ref.obj[ref.key]["translate"]))
            elif ref.kind in {"json_tag", "command_tag"}:
                raw = ref.tag.value if ref.kind != "command_tag" else self.extract_command_json(ref.tag.value)
                if ref.kind == "command_tag":
                    if raw is None:
                        continue
                    raw_json = raw[1]
                else:
                    raw_json = raw
                try:
                    component = json.loads(raw_json)
                except json.JSONDecodeError:
                    continue
                stack = [component]
                while stack:
                    current = stack.pop()
                    if isinstance(current, dict):
                        text_value = current.get("text")
                        if isinstance(text_value, str):
                            add_text(text_value)
                        elif (
                            isinstance(text_value, dict)
                            and set(text_value.keys()) == {"translate"}
                            and isinstance(text_value.get("translate"), str)
                            and any(text_value["translate"].startswith(prefix) for prefix in self.component_prefixes)
                        ):
                            add_text(self.text_from_translate_key(text_value["translate"]))
                        for value in current.values():
                            if isinstance(value, (dict, list)):
                                stack.append(value)
                    elif isinstance(current, list):
                        stack.extend(current)

        return ordered

    def patch_json_component(self, node: Any, translations: dict[str, str]) -> None:
        if isinstance(node, dict):
            text_value = node.get("text")
            if isinstance(text_value, str):
                translated = translations.get(text_value)
                if translated:
                    node["text"] = translated
            elif (
                isinstance(text_value, dict)
                and set(text_value.keys()) == {"translate"}
                and isinstance(text_value.get("translate"), str)
                and any(text_value["translate"].startswith(prefix) for prefix in self.component_prefixes)
            ):
                source = self.text_from_translate_key(text_value["translate"])
                translated = translations.get(source)
                if translated:
                    node["text"] = translated

            if self.scan_config["translate_command_output"]:
                click_event = node.get("clickEvent")
                if isinstance(click_event, dict) and isinstance(click_event.get("value"), str):
                    click_event["value"] = self.patch_command_component(click_event["value"], translations)

                hover_event = node.get("hoverEvent")
                if isinstance(hover_event, dict) and isinstance(hover_event.get("value"), str):
                    hover_event["value"] = self.patch_command_component(hover_event["value"], translations)

            for key, value in list(node.items()):
                if isinstance(value, (dict, list)):
                    self.patch_json_component(value, translations)
        elif isinstance(node, list):
            for item in node:
                self.patch_json_component(item, translations)

    def patch_command_component(self, command: str, translations: dict[str, str]) -> str:
        extracted = self.extract_command_json(command)
        if not extracted:
            return command
        prefix, raw_json = extracted
        try:
            component = json.loads(raw_json)
        except json.JSONDecodeError:
            return command
        self.patch_json_component(component, translations)
        return prefix + self.serialize_text_component(component)

    def apply_translations(self, refs: list[TextRef], translations: dict[str, str]) -> int:
        changed = 0
        handled_json_text_ids: set[int] = set()
        handled_translate_key_ids: set[int] = set()

        for ref in refs:
            if ref.kind == "plain_tag":
                original = ref.tag.value
                translated = translations.get(original)
                if translated and translated != original:
                    ref.tag.value = translated
                    changed += 1
            elif ref.kind == "json_tag":
                component = self.parse_text_component(ref.tag.value)
                before = self.serialize_text_component(component)
                self.patch_json_component(component, translations)
                after = self.serialize_text_component(component)
                if after != before:
                    ref.tag.value = after
                    changed += 1
                for child_ref in refs:
                    if child_ref.kind == "json_text" and id(child_ref.obj) in {
                        id(n) for n in self._iter_json_nodes(component)
                    }:
                        handled_json_text_ids.add(id(child_ref))
                    elif child_ref.kind == "translate_key" and id(child_ref.obj) in {
                        id(n) for n in self._iter_json_nodes(component)
                    }:
                        handled_translate_key_ids.add(id(child_ref))
            elif ref.kind == "command_tag":
                updated = self.patch_command_component(ref.tag.value, translations)
                if updated != ref.tag.value:
                    ref.tag.value = updated
                    changed += 1
                for child_ref in refs:
                    if child_ref.kind in {"json_text", "translate_key"}:
                        try:
                            extracted = self.extract_command_json(ref.tag.value)
                            if extracted:
                                cmd_component = json.loads(extracted[1])
                                for node in self._iter_json_nodes(cmd_component):
                                    if id(child_ref.obj) == id(node):
                                        if child_ref.kind == "json_text":
                                            handled_json_text_ids.add(id(child_ref))
                                        else:
                                            handled_translate_key_ids.add(id(child_ref))
                        except (json.JSONDecodeError, Exception):
                            pass
            elif ref.kind == "json_text" and id(ref.obj) not in handled_json_text_ids:
                original = ref.obj.get(ref.key, "")
                if isinstance(original, str):
                    translated = translations.get(original)
                    if translated and translated != original:
                        ref.obj[ref.key] = translated
                        changed += 1
            elif ref.kind == "translate_key" and id(ref.obj) not in handled_translate_key_ids:
                translate_val = ref.obj.get(ref.key, {})
                if isinstance(translate_val, dict) and "translate" in translate_val:
                    source = self.text_from_translate_key(translate_val["translate"])
                    translated = translations.get(source)
                    if translated:
                        ref.obj[ref.key] = translated
                        changed += 1

        return changed

    def _iter_json_nodes(self, node: Any):
        if isinstance(node, dict):
            yield node
            for value in node.values():
                yield from self._iter_json_nodes(value)
        elif isinstance(node, list):
            for item in node:
                yield from self._iter_json_nodes(item)

    def process_region_file(self, path: Path) -> dict[str, Any]:
        self.ensure_not_cancelled()
        if path.stat().st_size < 8192:
            return {"file": str(path), "changed_chunks": 0, "unique_texts": 0, "candidates": 0, "skipped": "small"}

        data = path.read_bytes()
        locations = data[:4096]
        timestamps = data[4096:8192]

        changed_chunks = 0
        unique_texts: set[str] = set()
        candidate_count = 0
        parse_error = False
        entries: list[tuple[int, bytes, int]] = []

        for idx in range(1024):
            self.ensure_not_cancelled()
            loc = locations[idx * 4 : idx * 4 + 4]
            sector_offset = int.from_bytes(loc[:3], "big")
            sector_count = loc[3]
            if sector_offset == 0 or sector_count == 0:
                entries.append((0, b"", 0))
                continue

            try:
                compression, payload, length = self.load_chunk_payload(data, sector_offset)
                raw_nbt = self.decompress_payload(compression, payload)
                root = self.parse_nbt_bytes(raw_nbt)
            except Exception:
                parse_error = True
                break

            refs: list[TextRef] = []
            self.collect_tag_refs(root, refs, f"{path.name}#{idx}")
            texts = self.extract_unique_texts(refs)
            unique_texts.update(texts)
            candidate_count += len(texts)

            if texts and not self.config["dry_run"]:
                translations = self.translator.translate_texts(texts)
                local_changes = self.apply_translations(refs, translations)
            else:
                local_changes = 0

            if local_changes > 0:
                changed_chunks += 1
                raw_nbt = self.dump_nbt_bytes(root)
                payload = self.compress_payload(compression, raw_nbt)
                length = len(payload) + 1

            full_chunk = length.to_bytes(4, "big") + bytes([compression]) + payload
            timestamp = int.from_bytes(timestamps[idx * 4 : idx * 4 + 4], "big")
            entries.append((length, full_chunk, timestamp))

        if parse_error:
            self.candidate_texts.update(unique_texts)
            return {
                "file": str(path),
                "changed_chunks": 0,
                "unique_texts": len(unique_texts),
                "candidates": candidate_count,
                "skipped": "parse_error",
            }

        if changed_chunks > 0 and not self.config["dry_run"]:
            self.backup_once(path)
            header_locations = bytearray(4096)
            header_timestamps = bytearray(timestamps)
            body = bytearray()
            sector_cursor = 2

            for idx, (length, chunk_bytes, timestamp) in enumerate(entries):
                if length == 0:
                    continue
                needed_sectors = math.ceil(len(chunk_bytes) / 4096)
                header_locations[idx * 4 : idx * 4 + 3] = sector_cursor.to_bytes(3, "big")
                header_locations[idx * 4 + 3] = needed_sectors
                header_timestamps[idx * 4 : idx * 4 + 4] = timestamp.to_bytes(4, "big")
                body.extend(chunk_bytes)
                padding = needed_sectors * 4096 - len(chunk_bytes)
                if padding:
                    body.extend(b"\x00" * padding)
                sector_cursor += needed_sectors

            final_bytes = bytes(header_locations) + bytes(header_timestamps) + bytes(body)
            last_error: Exception | None = None
            for attempt in range(1, max(1, int(self.runtime_config["max_file_write_retries"])) + 1):
                try:
                    write_bytes_atomic(path, final_bytes)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
                    self.emit("file_write_retry", file=str(path), attempt=attempt, message=str(exc))
                    time.sleep(min(0.5 * attempt, 2.0))
            if last_error is not None:
                raise last_error

        self.candidate_texts.update(unique_texts)
        return {
            "file": str(path),
            "changed_chunks": changed_chunks,
            "unique_texts": len(unique_texts),
            "candidates": candidate_count,
        }

    def translate_resource_packs(self) -> None:
        for zip_path_str in self.config["resource_pack"]["zip_paths"]:
            self.ensure_not_cancelled()
            if zip_path_str in self.completed_resource_pack_paths:
                self.emit("resource_pack_skipped", zip_path=zip_path_str, reason="checkpoint")
                continue
            zip_path = Path(zip_path_str)
            try:
                result = (
                    self.scan_resource_pack_zip(zip_path)
                    if self.config["dry_run"]
                    else self.translate_resource_pack_zip(zip_path)
                )
            except TranslationCancelled:
                raise
            except Exception as exc:
                result = {
                    "zip_path": str(zip_path),
                    "translated_files": 0,
                    "candidates": 0,
                    "skipped": "resource_pack_error",
                    "error": str(exc),
                }
                self.report["errors"].append(result)
                self.emit("file_error", file=str(zip_path), message=str(exc))
                if not self.runtime_config["continue_on_file_error"]:
                    raise
            self.report["resource_packs"].append(result)
            if result.get("skipped") not in {"missing", "resource_pack_error"}:
                self.completed_resource_pack_paths.add(zip_path_str)
            self.save_checkpoint()

    def resource_pack_language_files(self, names: list[str]) -> list[tuple[str, str]]:
        """Return language files once, in configured source-language priority order."""
        found: list[tuple[str, str]] = []
        seen: set[str] = set()
        for source_name in self.config["resource_pack"]["source_lang_files"]:
            for name in names:
                if name in seen or name.rsplit("/", 1)[-1] != source_name or "/lang/" not in name:
                    continue
                seen.add(name)
                found.append((name, source_name))
        return found

    def scan_resource_pack_zip(self, zip_path: Path) -> dict[str, Any]:
        import zipfile

        self.ensure_not_cancelled()
        if not zip_path.exists():
            return {
                "zip_path": str(zip_path),
                "translated_files": 0,
                "candidates": 0,
                "dry_run": True,
                "skipped": "missing",
            }

        candidate_texts: set[str] = set()
        source_files = 0
        with zipfile.ZipFile(zip_path, "r") as zf:
            for source_path, _ in self.resource_pack_language_files(zf.namelist()):
                self.ensure_not_cancelled()
                try:
                    payload = json.loads(zf.read(source_path).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(payload, dict):
                    continue
                source_files += 1
                candidate_texts.update(
                    value for value in payload.values() if isinstance(value, str) and self.should_translate_text(value)
                )

        self.candidate_texts.update(candidate_texts)
        return {
            "zip_path": str(zip_path),
            "translated_files": 0,
            "source_files": source_files,
            "candidates": len(candidate_texts),
            "dry_run": True,
        }

    def translate_resource_pack_zip(self, zip_path: Path) -> dict[str, Any]:
        import zipfile

        self.ensure_not_cancelled()
        if not zip_path.exists():
            return {"zip_path": str(zip_path), "translated_files": 0, "candidates": 0, "skipped": "missing"}

        target_name = self.config["resource_pack"]["target_lang_file"]
        replacements: dict[str, bytes] = {}
        translated_files = 0
        candidate_texts: set[str] = set()

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            for source_path, source_name in self.resource_pack_language_files(names):
                self.ensure_not_cancelled()
                target_path = source_path[: -len(source_name)] + target_name
                if target_path in replacements:
                    continue
                if self.config["resource_pack"]["skip_if_target_exists"] and target_path in names:
                    continue
                try:
                    payload = json.loads(zf.read(source_path).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                if not isinstance(payload, dict):
                    continue
                texts = list(
                    dict.fromkeys(
                        value for value in payload.values() if isinstance(value, str) and self.should_translate_text(value)
                    )
                )
                candidate_texts.update(texts)
                if not texts:
                    continue
                translations = self.translator.translate_texts(texts)
                translated_payload = {
                    key: translations.get(value, value) if isinstance(value, str) else value
                    for key, value in payload.items()
                }
                replacements[target_path] = json.dumps(
                    translated_payload, ensure_ascii=False, indent=2
                ).encode("utf-8")
                translated_files += 1

        self.candidate_texts.update(candidate_texts)

        if replacements:
            self.backup_once(zip_path)
            tmp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".zip", dir=str(zip_path.parent)) as tmp:
                    tmp_path = Path(tmp.name)
                with zipfile.ZipFile(zip_path, "r") as src, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as dst:
                    dst.comment = src.comment
                    written_targets = set()
                    for info in src.infolist():
                        self.ensure_not_cancelled()
                        if info.filename in replacements:
                            dst.writestr(info, replacements[info.filename])
                            written_targets.add(info.filename)
                        else:
                            dst.writestr(info, src.read(info.filename))
                    for target_path, payload in replacements.items():
                        self.ensure_not_cancelled()
                        if target_path not in written_targets:
                            dst.writestr(target_path, payload)
                shutil.copymode(zip_path, tmp_path)
                with tmp_path.open("rb") as tmp_file:
                    os.fsync(tmp_file.fileno())
                os.replace(tmp_path, zip_path)
            except Exception:
                if tmp_path is not None:
                    tmp_path.unlink(missing_ok=True)
                raise

        return {
            "zip_path": str(zip_path),
            "translated_files": translated_files,
            "candidates": len(candidate_texts),
        }

    def write_report(self) -> None:
        report_path = Path(self.config["report_path"])
        write_text_atomic(
            report_path,
            json.dumps(self.report, ensure_ascii=False, indent=2),
        )


def list_models_for_config(config: dict[str, Any]) -> list[dict[str, Any]]:
    client = LLMProviderClient(config)
    return client.list_models()


def enhance_style_prompt_for_config(config: dict[str, Any], brief: str) -> str:
    return enhance_style_prompt(config, brief)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Translate Minecraft world NBT texts and optional resource-pack language files."
    )
    parser.add_argument("--config", type=str, help="TOML config path")
    parser.add_argument("--world-dir", type=str, help="Minecraft world directory")
    parser.add_argument("--report-path", type=str, help="JSON report output path")
    parser.add_argument(
        "--provider",
        type=str,
        choices=provider_choices(),
        help="LLM provider override",
    )
    parser.add_argument("--api-key", type=str, help="API key override")
    parser.add_argument("--base-url", type=str, help="Base URL override")
    parser.add_argument("--model", type=str, help="Model override")
    parser.add_argument("--target-language", type=str, help="Target language, e.g. 한국어")
    parser.add_argument(
        "--style-preset",
        type=str,
        choices=sorted(STYLE_PRESETS),
        help="Style preset override",
    )
    parser.add_argument("--style-prompt", type=str, help="Additional style instructions")
    parser.add_argument("--custom-system-prompt", type=str, help="Full custom system prompt")
    parser.add_argument("--batch-size", type=int, help="Translation batch size")
    parser.add_argument("--temperature", type=float, help="Sampling temperature")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, do not call API or write files")
    parser.add_argument("--resume", action="store_true", help="Resume from the last saved checkpoint if it exists")
    parser.add_argument("--no-backup", action="store_true", help="Do not create backup files")
    parser.add_argument(
        "--resource-pack-zip",
        action="append",
        help="Resource pack zip path to translate; repeatable",
    )
    parser.add_argument(
        "--enable-resource-pack-translation",
        action="store_true",
        help="Enable resource-pack zip translation from config",
    )
    parser.add_argument(
        "--disable-resource-pack-translation",
        action="store_true",
        help="Disable resource-pack zip translation even if config enables it",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available models for the selected provider and exit",
    )
    parser.add_argument(
        "--enhance-style-brief",
        type=str,
        help="Expand a short style brief into a more detailed prompt using the configured provider/model",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve() if args.config else None
    loaded = load_toml_config(config_path)
    config = merge_nested(DEFAULT_CONFIG, loaded)
    config = apply_cli_overrides(config, args)
    try:
        config = normalize_config(config, config_path)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    if args.list_models:
        try:
            models = list_models_for_config(config)
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps({"provider": config["api"]["provider"], "models": models}, ensure_ascii=False, indent=2))
        return

    if args.enhance_style_brief:
        if not config["api"]["api_key"]:
            raise SystemExit("API key is missing. Set it in config, environment, or translate.py defaults.")
        if not config["api"]["model"]:
            raise SystemExit("Model is missing. Set it in config or translate.py defaults.")
        try:
            enhanced = enhance_style_prompt_for_config(config, args.enhance_style_brief)
        except Exception as exc:
            raise SystemExit(str(exc)) from exc
        print(enhanced)
        return

    if not config["world_dir"]:
        raise SystemExit("`world_dir` is required. Set it in config or pass --world-dir.")
    if not config["dry_run"]:
        if not config["api"]["api_key"]:
            raise SystemExit("API key is missing. Set it in config, environment, or translate.py defaults.")
        if not config["api"]["model"]:
            raise SystemExit("Model is missing. Set it in config or translate.py defaults.")

    translator = WorldTranslator(config)
    report = translator.run()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
