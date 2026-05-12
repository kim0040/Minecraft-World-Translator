"""Core functionality tests for Minecraft World Translator."""
import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mc_world_translator import WorldTranslator, DEFAULT_CONFIG, merge_nested, load_json_file


def create_test_config():
    """Create a minimal test configuration."""
    config = merge_nested(DEFAULT_CONFIG, {
        "world_dir": "/tmp/test_world",
        "dry_run": True,
        "backup": False,
        "scan": {
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
            "overrides": {}
        }
    })
    return config


def test_should_translate_text_filters():
    """Test the should_translate_text filtering logic."""
    config = create_test_config()
    translator = WorldTranslator(config)

    # === SHOULD TRANSLATE (returns True) ===
    # Normal English sentences
    assert translator.should_translate_text("Hello World") is True
    assert translator.should_translate_text("This is a puzzle hint") is True
    assert translator.should_translate_text("Turn left at the crossroads") is True

    # Korean text
    assert translator.should_translate_text("이것은 테스트입니다") is True
    assert translator.should_translate_text("좌회전하세요") is True

    # Japanese text
    assert translator.should_translate_text("これはテストです") is True
    assert translator.should_translate_text("左に曲がってください") is True

    # Chinese text
    assert translator.should_translate_text("这是测试") is True

    # Mixed languages with longer text
    assert translator.should_translate_text("Press the button to start the game") is True
    assert translator.should_translate_text("보물 상자를 찾아보세요") is True

    # 5+ char English (should pass even uppercase)
    assert translator.should_translate_text("Hello") is True
    assert translator.should_translate_text("START") is True
    assert translator.should_translate_text("GO TO") is True
    assert translator.should_translate_text("THE END") is True

    # === SHOULD NOT TRANSLATE (returns False) ===
    # Empty / whitespace
    assert translator.should_translate_text("") is False
    assert translator.should_translate_text("   ") is False
    assert translator.should_translate_text("\n\t") is False

    # Single special chars
    assert translator.should_translate_text("@") is False
    assert translator.should_translate_text("#") is False
    assert translator.should_translate_text("!") is False
    assert translator.should_translate_text("?") is False
    assert translator.should_translate_text(".") is False
    assert translator.should_translate_text(",") is False
    assert translator.should_translate_text("-") is False
    assert translator.should_translate_text("~") is False
    assert translator.should_translate_text("/") is False

    # Namespace prefixed (Minecraft / mod IDs)
    assert translator.should_translate_text("minecraft:stone") is False
    assert translator.should_translate_text("forge:modid") is False
    assert translator.should_translate_text("neoforge:something") is False
    assert translator.should_translate_text("fabric:something") is False
    assert translator.should_translate_text("kubejs:item_name") is False
    assert translator.should_translate_text("ftbquests:chapter") is False
    assert translator.should_translate_text("create:goggles") is False

    # Command-like
    assert translator.should_translate_text("/kill @p") is False
    assert translator.should_translate_text("/give @s minecraft:diamond") is False
    assert translator.should_translate_text("/tp @a 0 64 0") is False

    # Entity selectors
    assert translator.should_translate_text("@p") is False
    assert translator.should_translate_text("@a") is False
    assert translator.should_translate_text("@s") is False
    assert translator.should_translate_text("@e") is False

    # Pure numbers
    assert translator.should_translate_text("123") is False
    assert translator.should_translate_text("42") is False
    assert translator.should_translate_text("3.14") is False
    assert translator.should_translate_text("100%") is False

    # Noise patterns
    assert translator.should_translate_text("!!!") is False
    assert translator.should_translate_text("...") is False
    assert translator.should_translate_text("---") is False
    assert translator.should_translate_text("===") is False
    assert translator.should_translate_text("##") is False

    # 1-char alpha (non-CJK)
    assert translator.should_translate_text("A") is False
    assert translator.should_translate_text("x") is False

    # 2-3 char all-uppercase alpha
    assert translator.should_translate_text("HI") is False
    assert translator.should_translate_text("OK") is False
    assert translator.should_translate_text("NO") is False
    assert translator.should_translate_text("AB") is False
    assert translator.should_translate_text("HP") is False
    assert translator.should_translate_text("MP") is False

    # Roman numerals
    assert translator.should_translate_text("IV") is False
    assert translator.should_translate_text("IX") is False
    assert translator.should_translate_text("XLII") is False
    assert translator.should_translate_text("III") is False

    # Short uppercase with space
    assert translator.should_translate_text("A B") is False
    assert translator.should_translate_text("X Y") is False

    # Single CJK char (should be translated)
    assert translator.should_translate_text("한") is True
    assert translator.should_translate_text("あ") is True
    assert translator.should_translate_text("中") is True

    print("  [PASS] should_translate_text")


def test_merge_nested():
    """Test nested dictionary merging."""
    base = {
        "a": 1,
        "b": {"c": 2, "d": 3},
        "e": [1, 2, 3]
    }
    override = {
        "b": {"c": 10},
        "f": 6
    }
    result = merge_nested(base, override)

    assert result["a"] == 1
    assert result["b"]["c"] == 10
    assert result["b"]["d"] == 3
    assert result["e"] == [1, 2, 3]
    assert result["f"] == 6

    # Original should not be mutated
    assert base["b"]["c"] == 2

    # Deep merge
    base2 = {"x": {"y": {"z": 1}}}
    override2 = {"x": {"y": {"w": 2}}}
    result2 = merge_nested(base2, override2)
    assert result2["x"]["y"]["z"] == 1
    assert result2["x"]["y"]["w"] == 2

    print("  [PASS] merge_nested")


def test_load_json_file():
    """Test JSON file loading."""
    # Non-existent file
    result = load_json_file(Path("/nonexistent/file.json"))
    assert result == {}

    # Valid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"key": "value", "nested": {"a": 1}}, f)
        temp_path = f.name

    try:
        result = load_json_file(Path(temp_path))
        assert result == {"key": "value", "nested": {"a": 1}}
    finally:
        os.unlink(temp_path)

    # Invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{invalid json content")
        temp_path = f.name

    try:
        result = load_json_file(Path(temp_path))
        assert result == {}
    finally:
        os.unlink(temp_path)

    print("  [PASS] load_json_file")


def test_extract_command_json():
    """Test command JSON extraction."""
    config = create_test_config()
    translator = WorldTranslator(config)

    # tellraw
    cmd = 'tellraw @a {"text":"Hello World"}'
    result = translator.extract_command_json(cmd)
    assert result is not None
    assert result[0] == 'tellraw @a '
    assert result[1] == '{"text":"Hello World"}'

    # tellraw with extra json
    cmd = 'tellraw @p {"text":"Click me","color":"gold"}'
    result = translator.extract_command_json(cmd)
    assert result is not None
    assert result[0] == 'tellraw @p '

    # title
    cmd = 'title @a title {"text":"Boss Fight"}'
    result = translator.extract_command_json(cmd)
    assert result is not None
    assert result[0] == 'title @a title '

    # subtitle
    cmd = 'title @a subtitle {"text":"Phase 2"}'
    result = translator.extract_command_json(cmd)
    assert result is not None

    # actionbar
    cmd = 'title @a actionbar {"text":"Score: 100"}'
    result = translator.extract_command_json(cmd)
    assert result is not None

    # Non-command
    cmd = 'say Hello World'
    result = translator.extract_command_json(cmd)
    assert result is None

    # Non-tellraw/title command
    cmd = 'give @s minecraft:diamond'
    result = translator.extract_command_json(cmd)
    assert result is None

    # Non-string input
    result = translator.extract_command_json(123)
    assert result is None

    print("  [PASS] extract_command_json")


def test_text_from_translate_key():
    """Test translate key to text conversion."""
    config = create_test_config()
    translator = WorldTranslator(config)
    translator.component_prefixes = ("brennenburg.",)

    # Basic key conversion
    assert translator.text_from_translate_key("brennenburg.prison1") == "prison1"
    assert translator.text_from_translate_key("brennenburg.prison_cell_1") == "prison cell 1"
    assert translator.text_from_translate_key("brennenburg.the_dark_hallway") == "the dark hallway"

    # No matching prefix
    assert translator.text_from_translate_key("other.key") == "other.key"

    # Empty prefix list
    translator.component_prefixes = ()
    assert translator.text_from_translate_key("brennenburg.prison1") == "brennenburg.prison1"

    print("  [PASS] text_from_translate_key")


def test_collect_json_text_refs():
    """Test JSON text component reference collection."""
    config = create_test_config()
    translator = WorldTranslator(config)

    # Simple text component
    refs = []
    translator.collect_json_text_refs({"text": "Hello World"}, refs, "test")
    assert len(refs) == 1
    assert refs[0].kind == "json_text"
    assert refs[0].obj["text"] == "Hello World"

    # Nested components
    refs = []
    component = {
        "text": "",
        "extra": [
            {"text": "Bold text", "bold": True},
            {"text": "Normal text"}
        ]
    }
    translator.collect_json_text_refs(component, refs, "test")
    assert len(refs) == 2

    # Empty text should not be collected
    refs = []
    translator.collect_json_text_refs({"text": ""}, refs, "test")
    assert len(refs) == 0

    # Non-translatable text
    refs = []
    translator.collect_json_text_refs({"text": "minecraft:stone"}, refs, "test")
    assert len(refs) == 0

    print("  [PASS] collect_json_text_refs")


def test_patch_json_component():
    """Test JSON component patching with translations."""
    config = create_test_config()
    translator = WorldTranslator(config)

    translations = {
        "Hello World": "안녕하세요 세계",
        "Bold text": "굵은 텍스트",
    }

    # Simple patch
    node = {"text": "Hello World"}
    translator.patch_json_component(node, translations)
    assert node["text"] == "안녕하세요 세계"

    # Nested patch
    node = {
        "text": "",
        "extra": [
            {"text": "Bold text", "bold": True},
            {"text": "Normal text"}
        ]
    }
    translator.patch_json_component(node, translations)
    assert node["extra"][0]["text"] == "굵은 텍스트"
    assert node["extra"][1]["text"] == "Normal text"

    # No match should leave unchanged
    node = {"text": "Unchanged text"}
    translator.patch_json_component(node, translations)
    assert node["text"] == "Unchanged text"

    print("  [PASS] patch_json_component")


def test_serialize_text_component():
    """Test text component serialization."""
    from mc_world_translator import WorldTranslator

    component = {"text": "Hello", "bold": True}
    result = WorldTranslator.serialize_text_component(component)
    parsed = json.loads(result)
    assert parsed["text"] == "Hello"
    assert parsed["bold"] is True

    # Compact format (no spaces)
    assert ", " not in result
    assert ": " not in result

    print("  [PASS] serialize_text_component")


def test_config_normalization():
    """Test configuration normalization."""
    from mc_world_translator import normalize_config

    config = merge_nested(DEFAULT_CONFIG, {
        "world_dir": "/tmp/test_world",
        "batch_size": 50,
        "temperature": 0.5,
    })

    result = normalize_config(config, None)
    assert result["batch_size"] == 50
    assert result["temperature"] == 0.5
    assert "world_dir" in result

    print("  [PASS] config_normalization")


def test_default_config_completeness():
    """Test that DEFAULT_CONFIG has all required sections."""
    required_keys = [
        "world_dir", "report_path", "dry_run", "backup", "backup_suffix",
        "batch_size", "temperature", "inherit_translate_py", "translate_py_path",
        "api", "prompt", "scan", "resource_pack", "runtime",
    ]
    for key in required_keys:
        assert key in DEFAULT_CONFIG, f"Missing key: {key}"

    # API section
    api_keys = ["provider", "api_key", "base_url", "model", "request_timeout", "rpm_limit", "tpm_limit"]
    for key in api_keys:
        assert key in DEFAULT_CONFIG["api"], f"Missing api key: {key}"

    # Prompt section
    prompt_keys = ["target_language", "style_preset", "style_prompt", "custom_system_prompt"]
    for key in prompt_keys:
        assert key in DEFAULT_CONFIG["prompt"], f"Missing prompt key: {key}"

    # Scan section
    scan_keys = [
        "region_dirs", "skip_patterns", "translate_signs", "translate_books",
        "translate_custom_names", "translate_item_names", "translate_lore",
        "translate_titles", "translate_filtered_titles", "translate_command_output",
        "skip_command_like_text", "component_translate_key_prefixes", "overrides",
    ]
    for key in scan_keys:
        assert key in DEFAULT_CONFIG["scan"], f"Missing scan key: {key}"

    print("  [PASS] config_completeness")


def test_iter_json_nodes():
    """Test JSON node iteration."""
    config = create_test_config()
    translator = WorldTranslator(config)

    # Simple dict
    node = {"text": "Hello", "extra": [{"text": "World"}]}
    nodes = list(translator._iter_json_nodes(node))
    assert len(nodes) == 2
    assert node in nodes

    # List
    node = [{"text": "A"}, {"text": "B"}]
    nodes = list(translator._iter_json_nodes(node))
    assert len(nodes) == 2

    # Nested
    node = {"a": {"b": {"c": "d"}}}
    nodes = list(translator._iter_json_nodes(node))
    assert len(nodes) == 3

    # Empty
    nodes = list(translator._iter_json_nodes("string"))
    assert len(nodes) == 0

    print("  [PASS] iter_json_nodes")


def test_apply_translations_comprehensive():
    """Test apply_translations with different ref types."""
    import json as json_mod
    from mc_world_translator import TextRef

    config = create_test_config()
    translator = WorldTranslator(config)

    translations = {
        "Hello World": "안녕하세요 세계",
        "Test Message": "테스트 메시지",
    }

    # Test plain_tag
    class FakeTag:
        def __init__(self, value):
            self.value = value

    refs = [TextRef("plain_tag", tag=FakeTag("Hello World"), path="test")]
    changed = translator.apply_translations(refs, translations)
    assert changed == 1
    assert refs[0].tag.value == "안녕하세요 세계"

    # Test json_text
    obj = {"text": "Hello World"}
    refs = [TextRef("json_text", obj=obj, key="text", path="test")]
    changed = translator.apply_translations(refs, translations)
    assert changed == 1
    assert obj["text"] == "안녕하세요 세계"

    # Test translate_key
    obj2 = {"text": {"translate": "test.key"}}
    config2 = merge_nested(DEFAULT_CONFIG, {
        "world_dir": "/tmp/test",
        "dry_run": True,
        "scan": {
            "component_translate_key_prefixes": ["test."],
            "overrides": {},
            "skip_command_like_text": True,
            "translate_signs": True,
            "translate_books": True,
            "translate_custom_names": True,
            "translate_item_names": True,
            "translate_lore": True,
            "translate_titles": True,
            "translate_filtered_titles": True,
            "translate_command_output": True,
        }
    })
    translator2 = WorldTranslator(config2)
    refs = [TextRef("translate_key", obj=obj2, key="text", path="test")]
    # text_from_translate_key("test.key") -> "key" (strips "test." prefix)
    translations2 = {"key": "변환된 텍스트"}
    changed = translator2.apply_translations(refs, translations2)
    assert changed == 1
    assert obj2["text"] == "변환된 텍스트"

    # Test no-op (no matching translation)
    obj3 = {"text": "No Match"}
    refs = [TextRef("json_text", obj=obj3, key="text", path="test")]
    changed = translator.apply_translations(refs, translations)
    assert changed == 0
    assert obj3["text"] == "No Match"

    print("  [PASS] apply_translations_comprehensive")


def test_hover_event_patching():
    """Test that hoverEvent commands are patched correctly."""
    config = create_test_config()
    translator = WorldTranslator(config)

    translations = {"Hover text": "호버 텍스트"}

    # Test patch_json_component with hoverEvent containing command
    node = {
        "text": "Click me",
        "hoverEvent": {
            "action": "show_text",
            "value": 'tellraw @a {"text":"Hover text"}'
        }
    }
    translator.patch_json_component(node, translations)
    assert 'Hover text' not in node["hoverEvent"]["value"] or "호버 텍스트" in node["hoverEvent"]["value"]

    # Test patch_json_component with hoverEvent containing text component
    node2 = {
        "text": "Click me",
        "hoverEvent": {
            "action": "show_text",
            "contents": {"text": "Hover text"}
        }
    }
    translator.patch_json_component(node2, translations)
    assert node2["hoverEvent"]["contents"]["text"] == "호버 텍스트"

    print("  [PASS] hover_event_patching")


if __name__ == "__main__":
    print("=== Core Functionality Tests ===\n")
    test_should_translate_text_filters()
    test_merge_nested()
    test_load_json_file()
    test_extract_command_json()
    test_text_from_translate_key()
    test_collect_json_text_refs()
    test_patch_json_component()
    test_serialize_text_component()
    test_config_normalization()
    test_default_config_completeness()
    test_iter_json_nodes()
    test_apply_translations_comprehensive()
    test_hover_event_patching()
    print("\n=== All tests passed! ===")