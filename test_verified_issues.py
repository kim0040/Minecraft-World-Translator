"""Tests for verified format, cache, resume, and config issues."""
from __future__ import annotations

import io
import math
import os
import tempfile
import zlib
from pathlib import Path

from nbt import nbt

from llm_backends import resolve_api_key
from mc_world_translator import (
    DEFAULT_CONFIG,
    BatchTranslator,
    WorldTranslator,
    checkpoint_status,
    matching_checkpoint_exists,
    merge_nested,
    normalize_config,
    project_dir,
)
from test_core import create_test_config
from webui_server import JobManager, is_non_loopback_bind


def _compound(name: str = "") -> nbt.TAG_Compound:
    tag = nbt.TAG_Compound()
    if name:
        tag.name = name
    return tag


def _add_string(parent: nbt.TAG_Compound, name: str, value: str) -> nbt.TAG_String:
    tag = nbt.TAG_String(name=name, value=value)
    parent.tags.append(tag)
    return tag


def _add_string_list(parent: nbt.TAG_Compound, name: str, values: list[str]) -> nbt.TAG_List:
    lst = nbt.TAG_List(name=name, type=nbt.TAG_String)
    for value in values:
        lst.append(nbt.TAG_String(value=value))
    parent.tags.append(lst)
    return lst


def _api_config() -> dict:
    return merge_nested(create_test_config(), {
        "dry_run": False,
        "batch_size": 1,
        "backup": False,
        "api": {
            "provider": "comet",
            "api_key": "test-key",
            "model": "test-model",
            "base_url": "http://127.0.0.1:9",
        },
        "runtime": {"max_batch_retries": 1, "checkpoint_enabled": False},
    })


def _nbt_bytes(root: nbt.NBTFile) -> bytes:
    buf = io.BytesIO()
    root.write_file(buffer=buf)
    return buf.getvalue()


def _region_bytes(*chunk_nbt: bytes | None) -> bytes:
    header = bytearray(4096)
    timestamps = bytearray(4096)
    body = bytearray()
    cursor = 2
    for idx, raw in enumerate(chunk_nbt):
        if raw is None:
            continue
        if raw == b"CORRUPT":
            payload = b"not-zlib"
            compression = 2
        else:
            payload = zlib.compress(raw)
            compression = 2
        full = (len(payload) + 1).to_bytes(4, "big") + bytes([compression]) + payload
        sectors = math.ceil(len(full) / 4096)
        header[idx * 4 : idx * 4 + 3] = cursor.to_bytes(3, "big")
        header[idx * 4 + 3] = sectors
        body.extend(full)
        body.extend(b"\x00" * (sectors * 4096 - len(full)))
        cursor += sectors
    return bytes(header) + bytes(timestamps) + bytes(body)


def test_collects_modern_sign_messages_and_patches():
    translator = WorldTranslator(create_test_config())
    sign = _compound()
    front = _compound("front_text")
    _add_string_list(front, "messages", [
        '{"text":"North Gate"}',
        '{"text":""}',
        '{"text":""}',
        '{"text":""}',
    ])
    back = _compound("back_text")
    _add_string_list(back, "messages", ['{"text":"Keep out adventurers"}'])
    _add_string_list(back, "filtered_messages", ['{"text":"Keep out adventurers"}'])
    sign.tags.extend([front, back])
    _add_string(sign, "Text1", '{"text":"Legacy line"}')

    refs = []
    translator.collect_tag_refs(sign, refs, "chunk#0")
    texts = translator.extract_unique_texts(refs)
    assert "North Gate" in texts
    assert "Keep out adventurers" in texts
    assert "Legacy line" in texts

    changed = translator.apply_translations(refs, {
        "North Gate": "북쪽 문",
        "Keep out adventurers": "모험가 출입 금지",
        "Legacy line": "구형 줄",
    })
    assert changed >= 3
    assert "북쪽 문" in front["messages"][0].value
    assert "모험가 출입 금지" in back["messages"][0].value
    assert "구형 줄" in sign["Text1"].value


def test_collects_data_component_item_and_book_text():
    translator = WorldTranslator(create_test_config())
    item = _compound()
    components = _compound("components")
    _add_string(components, "minecraft:custom_name", '{"text":"Excalibur Blade"}')
    _add_string_list(components, "minecraft:lore", ['{"text":"A legendary weapon"}'])
    book = _compound("minecraft:written_book_content")
    title = _compound("title")
    _add_string(title, "raw", "My Adventure Diary")
    _add_string(title, "filtered", "My Adventure Diary")
    book.tags.append(title)
    pages = nbt.TAG_List(name="pages", type=nbt.TAG_Compound)
    page = _compound()
    _add_string(page, "raw", '{"text":"Dear diary today"}')
    _add_string(page, "filtered", '{"text":"Dear diary today"}')
    pages.append(page)
    book.tags.append(pages)
    components.tags.append(book)
    item.tags.append(components)

    display = _compound("display")
    _add_string(display, "Name", '{"text":"Old Display Name"}')
    _add_string_list(display, "Lore", ['{"text":"Old lore line"}'])
    item.tags.append(display)

    refs = []
    translator.collect_tag_refs(item, refs, "chunk#0")
    texts = set(translator.extract_unique_texts(refs))
    assert "Excalibur Blade" in texts
    assert "A legendary weapon" in texts
    assert "My Adventure Diary" in texts
    assert "Dear diary today" in texts
    assert "Old Display Name" in texts
    assert "Old lore line" in texts

    translator.apply_translations(refs, {
        "Excalibur Blade": "엑스칼리버",
        "A legendary weapon": "전설의 무기",
        "My Adventure Diary": "모험 일기",
        "Dear diary today": "일기장 첫 줄",
        "Old Display Name": "옛 이름",
        "Old lore line": "옛 로어",
    })
    assert "엑스칼리버" in components["minecraft:custom_name"].value
    assert "전설의 무기" in components["minecraft:lore"][0].value
    assert components["minecraft:written_book_content"]["title"]["raw"].value == "모험 일기"
    assert "일기장 첫 줄" in components["minecraft:written_book_content"]["pages"][0]["raw"].value
    assert "옛 이름" in display["Name"].value


def test_failed_batch_does_not_cache_identity_or_complete_file():
    config = _api_config()
    batch = BatchTranslator(config)

    def boom(**_kwargs):
        raise RuntimeError("provider down")

    batch.client.translate_mapping = boom
    try:
        batch.translate_texts(["Hello adventurer"])
    except RuntimeError as exc:
        assert "provider down" in str(exc) or "failed" in str(exc).lower()
    else:
        raise AssertionError("Failed batch was accepted")
    assert "Hello adventurer" not in batch.cache

    with tempfile.TemporaryDirectory() as temp_dir:
        world = Path(temp_dir) / "world"
        region = world / "region"
        region.mkdir(parents=True)
        root = nbt.NBTFile()
        root.name = "Chunk"
        _add_string(root, "Text1", '{"text":"Hello adventurer"}')
        mca = region / "r.0.0.mca"
        mca.write_bytes(_region_bytes(_nbt_bytes(root)))
        job_config = merge_nested(config, {
            "world_dir": str(world),
            "report_path": str(Path(temp_dir) / "report.json"),
            "runtime": {
                "checkpoint_enabled": True,
                "checkpoint_path": str(Path(temp_dir) / "ckpt.json"),
                "continue_on_file_error": True,
                "max_batch_retries": 1,
            },
        })
        translator = WorldTranslator(job_config)
        translator.translator.client.translate_mapping = boom
        report = translator.run()
        assert str(mca.resolve()) not in translator.completed_region_files
        assert "Hello adventurer" not in translator.translator.cache
        assert report["status"] == "completed"
        assert translator.report["errors"]


def test_custom_system_prompt_does_not_append_extra_style():
    config = merge_nested(_api_config(), {
        "prompt": {
            "custom_system_prompt": "CUSTOM_ONLY_PROMPT",
            "style_prompt": "SHOULD_NOT_APPEAR",
            "style_preset": "neutral",
        },
    })
    prompt = BatchTranslator(config).system_prompt()
    assert "CUSTOM_ONLY_PROMPT" in prompt
    assert "SHOULD_NOT_APPEAR" not in prompt
    assert "추가 스타일 지시" not in prompt

    preset_config = merge_nested(_api_config(), {
        "prompt": {
            "custom_system_prompt": "",
            "style_prompt": "EXTRA_STYLE_LINE",
            "style_preset": "neutral",
        },
    })
    preset_prompt = BatchTranslator(preset_config).system_prompt()
    assert "EXTRA_STYLE_LINE" in preset_prompt


def test_api_key_prefers_env_over_translate_py_and_ignores_other_providers():
    saved = {key: os.environ.get(key) for key in ("COMET_API_KEY", "OPENAI_API_KEY")}
    try:
        os.environ.pop("COMET_API_KEY", None)
        os.environ["OPENAI_API_KEY"] = "openai-wrong-key"
        with tempfile.TemporaryDirectory() as temp_dir:
            legacy = Path(temp_dir) / "translate.py"
            legacy.write_text("API_KEY = 'from-translate-py'\n", encoding="utf-8")
            world = Path(temp_dir) / "world"
            world.mkdir()
            base = merge_nested(DEFAULT_CONFIG, {
                "world_dir": str(world),
                "inherit_translate_py": True,
                "translate_py_path": str(legacy),
                "api": {"provider": "comet", "api_key": "", "base_url": "", "model": ""},
            })
            inherited = normalize_config(base, None)
            assert inherited["api"]["api_key"] == "from-translate-py"
            assert resolve_api_key("comet", "") == ""

            os.environ["COMET_API_KEY"] = "from-env"
            from_env = normalize_config(base, None)
            assert from_env["api"]["api_key"] == "from-env"

            toml_cfg = merge_nested(base, {"api": {"api_key": "from-toml"}})
            from_toml = normalize_config(toml_cfg, None)
            assert from_toml["api"]["api_key"] == "from-toml"
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_resume_requires_matching_checkpoint():
    with tempfile.TemporaryDirectory() as temp_dir:
        world = Path(temp_dir) / "world"
        world.mkdir()
        payload = {
            "config": {
                "world_dir": str(world),
                "dry_run": False,
                "api": {"provider": "comet", "api_key": "x", "model": "m"},
                "runtime": {"resume_from_checkpoint": True, "checkpoint_enabled": True},
            }
        }
        try:
            JobManager().create_job(payload)
        except ValueError as exc:
            assert "checkpoint" in str(exc).lower()
        else:
            raise AssertionError("Resume without a matching checkpoint started a job")

        config = merge_nested(_api_config(), {
            "world_dir": str(world),
            "dry_run": False,
            "runtime": {
                "checkpoint_enabled": True,
                "checkpoint_path": str(Path(temp_dir) / "ckpt.json"),
                "resume_from_checkpoint": False,
            },
        })
        first = WorldTranslator(config)
        first.completed_region_files.add(str(world / "region/r.0.0.mca"))
        first.save_checkpoint()
        assert matching_checkpoint_exists(first.config)
        assert checkpoint_status(first.config)["resumable"] is True

        mismatch = merge_nested(first.config, {"prompt": {"target_language": "日本語"}})
        assert matching_checkpoint_exists(mismatch) is False


def test_export_and_backup_off_i18n_keys():
    app_js = Path(__file__).resolve().parent / "webui" / "app.js"
    text = app_js.read_text(encoding="utf-8")
    assert "function stripSecretsFromPayload" in text
    assert 'copy.api.api_key = ""' in text
    assert "stripSecretsFromPayload(buildPayload(false))" in text
    assert "confirmContinueNoBackup" in text
    assert 't(draft.backup ? "confirmContinue" : "confirmContinueNoBackup")' in text
    assert 't(draft.backup ? "confirmContinue" : "translateButton")' not in text
    assert "state.checkpointResumable" in text
    assert "/api/checkpoint-status" in text


def test_click_event_and_hover_event_json_strings():
    translator = WorldTranslator(create_test_config())
    node = {
        "text": "Click this button",
        "click_event": {
            "action": "run_command",
            "command": 'tellraw @a {"text":"Opened the chest"}',
        },
        "hover_event": {
            "action": "show_text",
            "value": '{"text":"Hover hint text"}',
        },
    }
    refs = []
    translator.collect_json_text_refs(node, refs, "test")
    texts = translator.extract_unique_texts(refs)
    assert "Opened the chest" in texts
    assert "Hover hint text" in texts

    translator.apply_translations(refs, {
        "Opened the chest": "상자를 열었다",
        "Hover hint text": "호버 힌트",
        "Click this button": "이 버튼을 클릭",
    })
    assert node["text"] == "이 버튼을 클릭"
    assert "상자를 열었다" in node["click_event"]["command"]
    assert "호버 힌트" in node["hover_event"]["value"]


def test_dry_run_does_not_write_into_world():
    with tempfile.TemporaryDirectory() as temp_dir:
        world = Path(temp_dir) / "AdventureWorld"
        (world / "region").mkdir(parents=True)
        config = merge_nested(create_test_config(), {
            "world_dir": str(world),
            "dry_run": True,
            "report_path": "",
            "runtime": {"checkpoint_enabled": True, "checkpoint_path": ""},
        })
        normalized = normalize_config(config, None)
        report_path = Path(normalized["report_path"]).resolve()
        checkpoint_path = Path(normalized["runtime"]["checkpoint_path"]).resolve()
        world_resolved = world.resolve()
        assert world_resolved not in report_path.parents
        assert world_resolved not in checkpoint_path.parents
        assert "translation_reports" in str(report_path)
        assert report_path.is_relative_to(project_dir() / "translation_reports")

        translator = WorldTranslator(normalized)
        translator.run()
        assert not (world / "translation_report.json").exists()
        assert not (world / ".translation_checkpoint.json").exists()
        assert report_path.exists()
        report_path.unlink(missing_ok=True)
        checkpoint_path.unlink(missing_ok=True)
        reports_dir = report_path.parent
        if reports_dir.exists() and not any(reports_dir.iterdir()):
            reports_dir.rmdir()


def test_bad_chunk_is_skipped_and_good_chunk_is_counted():
    translator = WorldTranslator(create_test_config())
    with tempfile.TemporaryDirectory() as temp_dir:
        root = nbt.NBTFile()
        root.name = "Chunk"
        _add_string(root, "Text1", '{"text":"Village notice board"}')
        path = Path(temp_dir) / "r.0.0.mca"
        path.write_bytes(_region_bytes(_nbt_bytes(root), b"CORRUPT"))
        result = translator.process_region_file(path)
        assert result["candidates"] >= 1
        assert result.get("skipped") != "parse_error"
        assert result.get("skipped_chunks", 0) >= 1
        assert any(err.get("reason") == "parse_error" for err in result.get("chunk_errors", []))
        assert "Village notice board" in translator.candidate_texts


def test_timestamped_backup_when_suffix_exists():
    config = merge_nested(create_test_config(), {
        "dry_run": False,
        "backup": True,
        "backup_suffix": ".bak_translate",
        "world_dir": "/tmp",
    })
    translator = WorldTranslator(config)
    with tempfile.TemporaryDirectory() as temp_dir:
        target = Path(temp_dir) / "r.0.0.mca"
        target.write_bytes(b"original-v1")
        translator.backup_once(target)
        first = Path(str(target) + ".bak_translate")
        assert first.read_bytes() == b"original-v1"
        target.write_bytes(b"translated-v2")
        translator.backup_once(target)
        stamped = list(Path(temp_dir).glob("r.0.0.mca.bak_translate.*"))
        assert stamped
        assert stamped[0].read_bytes() == b"translated-v2"
        assert first.read_bytes() == b"original-v1"


def test_non_loopback_bind_is_warned():
    assert is_non_loopback_bind("0.0.0.0") is True
    assert is_non_loopback_bind("127.0.0.1") is False
    assert is_non_loopback_bind("localhost") is False
