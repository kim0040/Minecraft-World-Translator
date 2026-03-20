from __future__ import annotations

import argparse
import ast
import fnmatch
import io
import json
import math
import os
import re
import shutil
import tempfile
import tomllib
import zlib
from copy import deepcopy
from pathlib import Path
from typing import Any

from openai import OpenAI

try:
    from nbt import nbt
except ImportError as exc:  # pragma: no cover - runtime dependency guard
    raise SystemExit(
        "Missing dependency: `nbt`.\n"
        "Install it first, for example:\n"
        "  python3 -m pip install nbtlib anvil-parser nbt"
    ) from exc


STYLE_PRESETS: dict[str, str] = {
    "dcinside": """
너는 마인크래프트 월드/맵 전문 번역가다.
사용자가 주는 텍스트를 {target_language}로 번역하되, 디씨인사이드 같은 인터넷 커뮤니티 말투를 적절히 섞어라.
[스타일 규칙]
1. 기본적으로 반말을 쓴다.
2. 너무 과하게 망가뜨리지 말고, 플레이 중 읽기 쉬운 선에서 익살스럽고 거친 느낌을 유지한다.
3. 게임 진행 정보, 퍼즐 힌트, UI 텍스트는 의미 전달이 최우선이다.
4. 고유명사, 인명, 제작자 이름, SNS 핸들, 브랜드명은 함부로 번역하지 말고 필요한 경우만 음역한다.
5. 특수 기호(§, \\n, {0}, %s, %% 등), JSON 구조, 키 이름은 절대 망가뜨리지 마라.
6. 원문이 이미 {target_language}면 문맥에 맞게 말투만 다듬어라.
7. 결과물에는 설명, 사족, 인사말 없이 번역 결과만 반환해라.
""".strip(),
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
        "api_key": "",
        "base_url": "",
        "model": "",
    },
    "prompt": {
        "target_language": "한국어",
        "style_preset": "dcinside",
        "style_prompt": "",
        "custom_system_prompt": "",
    },
    "scan": {
        "region_dirs": [
            "region",
            "entities",
            "DIM-1/region",
            "DIM-1/entities",
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


def load_legacy_translate_defaults(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
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

    return result


def normalize_config(config: dict[str, Any], config_path: Path | None) -> dict[str, Any]:
    result = deepcopy(config)

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
            if legacy_prompt and result["prompt"]["style_preset"] == "dcinside":
                result["prompt"]["custom_system_prompt"] = legacy_prompt

    api_key = result["api"]["api_key"] or os.getenv("OPENAI_API_KEY") or os.getenv("COMET_API_KEY", "")
    result["api"]["api_key"] = api_key

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
    else:
        result["world_dir"] = ""
        result["report_path"] = result["report_path"] or ""

    zip_paths: list[str] = []
    for zip_path in result["resource_pack"]["zip_paths"]:
        path_obj = Path(zip_path).expanduser()
        if not path_obj.is_absolute() and result["world_dir"]:
            path_obj = (world_dir / path_obj).resolve()
        zip_paths.append(str(path_obj))
    result["resource_pack"]["zip_paths"] = zip_paths

    return result


class BatchTranslator:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.cache: dict[str, str] = {}
        self.overrides: dict[str, str] = dict(config["scan"]["overrides"])
        self.client = OpenAI(
            api_key=config["api"]["api_key"],
            base_url=config["api"]["base_url"] or None,
        )

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
            batch = missing[start : start + batch_size]
            translated = self._translate_batch(batch, batch_size)
            for original, localized in translated.items():
                self.cache[original] = localized

        return {text: self.cache.get(text, text) for text in texts}

    def _translate_batch(self, texts: list[str], batch_size: int) -> dict[str, str]:
        payload = {str(i): text for i, text in enumerate(texts)}
        try:
            response = self.client.chat.completions.create(
                model=self.config["api"]["model"],
                messages=[
                    {"role": "system", "content": self.system_prompt()},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False, indent=2)},
                ],
                response_format={"type": "json_object"},
                temperature=float(self.config["temperature"]),
            )
            content = response.choices[0].message.content or "{}"
            parsed = json.loads(content)
            return {
                text: parsed.get(str(i), text)
                for i, text in enumerate(texts)
            }
        except Exception:
            if batch_size > 1:
                next_size = max(1, batch_size // 5)
                merged: dict[str, str] = {}
                for i in range(0, len(texts), next_size):
                    merged.update(self._translate_batch(texts[i : i + next_size], next_size))
                return merged
            return {text: text for text in texts}


class WorldTranslator:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.scan_config = config["scan"]
        self.component_prefixes = tuple(self.scan_config["component_translate_key_prefixes"])
        self.skip_patterns = tuple(self.scan_config["skip_patterns"])
        self.report: dict[str, Any] = {
            "world_dir": config["world_dir"],
            "dry_run": config["dry_run"],
            "changed_files": [],
            "resource_packs": [],
        }
        self.translator = None if config["dry_run"] else BatchTranslator(config)

    def run(self) -> dict[str, Any]:
        if self.config["resource_pack"]["enabled"]:
            self.translate_resource_packs()

        for file_path in self.iter_region_files():
            result = self.process_region_file(file_path)
            if result["changed_chunks"] > 0 or result.get("candidates", 0) > 0:
                self.report["changed_files"].append(result)

        self.report["changed_file_count"] = len(
            [item for item in self.report["changed_files"] if item["changed_chunks"] > 0]
        )
        self.report["candidate_file_count"] = len(self.report["changed_files"])
        self.write_report()
        return self.report

    def iter_region_files(self) -> list[Path]:
        world_dir = Path(self.config["world_dir"])
        files: list[Path] = []
        for rel_dir in self.scan_config["region_dirs"]:
            abs_dir = world_dir / rel_dir
            if not abs_dir.is_dir():
                continue
            for path in sorted(abs_dir.iterdir()):
                if not path.name.endswith(".mca"):
                    continue
                if any(fnmatch.fnmatch(path.name, pattern) for pattern in self.skip_patterns):
                    continue
                files.append(path)
        return files

    def should_translate_text(self, text: str) -> bool:
        if not isinstance(text, str):
            return False
        stripped = text.strip()
        if not stripped:
            return False
        if stripped == "@":
            return False
        if stripped.startswith("minecraft:") or stripped.startswith("forge:"):
            return False
        if self.scan_config["skip_command_like_text"] and stripped.startswith("/"):
            return False
        if stripped.startswith("@") and " " not in stripped:
            return False
        if all(not ch.isalpha() for ch in stripped):
            return False
        if len(stripped) <= 4 and all(ch in "IVXLCDM " or ch.isalpha() for ch in stripped):
            if stripped.upper() == stripped and " " in stripped:
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
                for hover_key, hover_value in hover_event.items():
                    self.collect_json_text_refs(hover_value, refs, f"{path}.hoverEvent.{hover_key}")

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
            elif ref.kind == "command_tag":
                updated = self.patch_command_component(ref.tag.value, translations)
                if updated != ref.tag.value:
                    ref.tag.value = updated
                    changed += 1
        return changed

    def process_region_file(self, path: Path) -> dict[str, Any]:
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
            return {
                "file": str(path),
                "changed_chunks": 0,
                "unique_texts": 0,
                "candidates": 0,
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

            with path.open("wb") as f:
                f.write(header_locations)
                f.write(header_timestamps)
                f.write(body)

        return {
            "file": str(path),
            "changed_chunks": changed_chunks,
            "unique_texts": len(unique_texts),
            "candidates": candidate_count,
        }

    def translate_resource_packs(self) -> None:
        if self.config["dry_run"]:
            for zip_path in self.config["resource_pack"]["zip_paths"]:
                self.report["resource_packs"].append(
                    {"zip_path": zip_path, "translated_files": 0, "candidates": 0, "dry_run": True}
                )
            return

        for zip_path_str in self.config["resource_pack"]["zip_paths"]:
            zip_path = Path(zip_path_str)
            result = self.translate_resource_pack_zip(zip_path)
            self.report["resource_packs"].append(result)

    def translate_resource_pack_zip(self, zip_path: Path) -> dict[str, Any]:
        import zipfile

        if not zip_path.exists():
            return {"zip_path": str(zip_path), "translated_files": 0, "candidates": 0, "skipped": "missing"}

        source_names = self.config["resource_pack"]["source_lang_files"]
        target_name = self.config["resource_pack"]["target_lang_file"]
        replacements: dict[str, bytes] = {}
        translated_files = 0
        candidate_count = 0

        with zipfile.ZipFile(zip_path, "r") as zf:
            names = zf.namelist()
            for source_name in source_names:
                targets = [name for name in names if name.endswith(source_name) and "/lang/" in name]
                for source_path in targets:
                    target_path = source_path[: -len(source_name)] + target_name
                    if self.config["resource_pack"]["skip_if_target_exists"] and target_path in names:
                        continue
                    try:
                        payload = json.loads(zf.read(source_path).decode("utf-8"))
                    except Exception:
                        continue
                    if not isinstance(payload, dict):
                        continue
                    texts = [value for value in payload.values() if isinstance(value, str) and self.should_translate_text(value)]
                    candidate_count += len(texts)
                    if not texts:
                        continue
                    translations = self.translator.translate_texts(texts)
                    translated_payload = {}
                    for key, value in payload.items():
                        if isinstance(value, str):
                            translated_payload[key] = translations.get(value, value)
                        else:
                            translated_payload[key] = value
                    replacements[target_path] = json.dumps(
                        translated_payload, ensure_ascii=False, indent=2
                    ).encode("utf-8")
                    translated_files += 1

        if replacements:
            self.backup_once(zip_path)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp_path = Path(tmp.name)

            import zipfile

            with zipfile.ZipFile(zip_path, "r") as src, zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as dst:
                written_targets = set()
                for info in src.infolist():
                    if info.filename in replacements:
                        dst.writestr(info.filename, replacements[info.filename])
                        written_targets.add(info.filename)
                    else:
                        dst.writestr(info, src.read(info.filename))
                for target_path, payload in replacements.items():
                    if target_path not in written_targets:
                        dst.writestr(target_path, payload)
            shutil.move(str(tmp_path), str(zip_path))

        return {
            "zip_path": str(zip_path),
            "translated_files": translated_files,
            "candidates": candidate_count,
        }

    def write_report(self) -> None:
        report_path = Path(self.config["report_path"])
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(self.report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Translate Minecraft world NBT texts and optional resource-pack language files."
    )
    parser.add_argument("--config", type=str, help="TOML config path")
    parser.add_argument("--world-dir", type=str, help="Minecraft world directory")
    parser.add_argument("--report-path", type=str, help="JSON report output path")
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
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config_path = Path(args.config).expanduser().resolve() if args.config else None
    loaded = load_toml_config(config_path)
    config = merge_nested(DEFAULT_CONFIG, loaded)
    config = apply_cli_overrides(config, args)
    config = normalize_config(config, config_path)

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
