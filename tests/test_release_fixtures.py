"""Fixture tests that drive the shipped WorldTranslator, region codec, and CLI safety path."""

from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nbt import nbt

from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested
from mwt.region import RegionFile, compress_payload, decompress_payload, external_chunk_path
from mwt.safety import world_fingerprint
from mwt.support_matrix import render_support_matrix

RESULTS: dict[str, bool] = {}
TRANSLATIONS = {
    "Hello sign": "Hola sign",
    "Front line": "Linea frontal",
    "Back line": "Linea trasera",
    "Filtered front": "Frente filtrado",
    "Page one": "Pagina uno",
    "Book Title": "Titulo",
    "Filtered Title": "Titulo filtrado",
    "Sword Name": "Nombre",
    "Lore line": "Linea de lore",
    "Component Name": "Nombre componente",
    "Item Name": "Nombre de objeto",
    "Component lore": "Lore componente",
    "Modern Title": "Titulo moderno",
    "Modern page": "Pagina moderna",
    "Writable page": "Pagina escribible",
    "Direct hello": "Hola directo",
    "Hello %s": "Hola",
    "Keep %s please": "Guarda %s por favor",
    "Hello adventurer": "Hola aventurero",
}


class TranslatorHandler(BaseHTTPRequestHandler):
    calls = 0

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        TranslatorHandler.calls += 1
        payload = json.loads(body["messages"][1]["content"])
        translated = {key: TRANSLATIONS.get(text, text) for key, text in payload.items()}
        raw = json.dumps({"choices": [{"message": {"content": json.dumps(translated)}}]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def start_responder() -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), TranslatorHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    return server, f"http://{host}:{port}/v1"


def nbt_bytes(*tags: nbt.TAG_Compound) -> bytes:
    root = nbt.NBTFile()
    root.name = ""
    for tag in tags:
        root.tags.append(tag)
    buffer = io.BytesIO()
    root.write_file(buffer=buffer)
    return buffer.getvalue()


def string(name: str, value: str) -> nbt.TAG_String:
    return nbt.TAG_String(name=name, value=value)


def compound(name: str, *tags: nbt.TAG) -> nbt.TAG_Compound:
    node = nbt.TAG_Compound(name=name)
    for tag in tags:
        node.tags.append(tag)
    return node


def string_list(name: str, values: list[str]) -> nbt.TAG_List:
    listing = nbt.TAG_List(name=name, type=nbt.TAG_String)
    for value in values:
        listing.append(nbt.TAG_String(value=value))
    return listing


def sign_tree() -> nbt.TAG_Compound:
    front = compound(
        "front_text",
        string_list("messages", ['{"text":"Front line"}', "minecraft:stone"]),
        string_list("filtered_messages", ["Filtered front"]),
    )
    back = compound("back_text", string_list("messages", ['{"text":"Back line"}']))
    legacy = compound(
        "sign",
        string("Text1", '{"text":"Hello sign"}'),
        string("Text2", "64"),
        front,
        back,
    )
    return legacy


def book_tree() -> nbt.TAG_Compound:
    return compound(
        "book",
        string_list("pages", ['{"text":"Page one"}']),
        string("title", "Book Title"),
        string("filtered_title", "Filtered Title"),
    )


def display_tree() -> nbt.TAG_Compound:
    lore = string_list("Lore", ['{"text":"Lore line"}'])
    return compound("display", string("Name", '{"text":"Sword Name"}'), lore)


def component_tree() -> nbt.TAG_Compound:
    title = compound("title", string("raw", "Modern Title"))
    page = compound("", string("raw", "Modern page"))
    pages = nbt.TAG_List(name="pages", type=nbt.TAG_Compound)
    pages.append(page)
    written = compound("minecraft:written_book_content", title, pages)
    writable_pages = string_list("pages", ["Writable page"])
    writable = compound("minecraft:writable_book_content", writable_pages)
    direct = compound("minecraft:custom_name", string("text", "Direct hello"))
    return compound(
        "components",
        string("minecraft:item_name", '{"text":"Item Name"}'),
        string_list("minecraft:lore", ['{"text":"Component lore"}']),
        direct,
        written,
        writable,
    )


def full_payload() -> bytes:
    commands = compound("commands")
    for name, command in (
        ("tellraw_block", 'tellraw @a {"text":"Keep %s please"}'),
        ("title_block", 'title @a title {"text":"Hello sign"}'),
        ("subtitle_block", 'title @a subtitle {"text":"Front line"}'),
        ("actionbar_block", 'title @a actionbar {"text":"Back line"}'),
    ):
        commands.tags.append(compound(name, string("Command", command)))
    broken = compound("placeholder", string("Text1", '{"text":"Hello %s"}'))
    return nbt_bytes(sign_tree(), book_tree(), display_tree(), component_tree(), commands, broken)


def untouched_payload() -> bytes:
    return nbt_bytes(compound("sign", string("Text1", '{"text":"Leave me"}')))


def write_region(path: Path, chunks: dict[int, tuple[int, bytes, bool]]) -> None:
    region = RegionFile.empty()
    for index, (compression, raw, external) in chunks.items():
        region.put_nbt(index, raw, compression=compression, external=external)
    data, mcc_files = region.build()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    for index, payload in mcc_files.items():
        external_chunk_path(path, index).write_bytes(payload)


def config_for(world: Path, report: Path, base_url: str, *, dry_run: bool, fingerprint: str = "") -> dict:
    return merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": dry_run,
            "report_path": str(report),
            "inherit_translate_py": False,
            "backup": True,
            "api": {"provider": "openai", "api_key": "test-key", "model": "fixture", "base_url": base_url},
            "runtime": {
                "checkpoint_enabled": False,
                "checkpoint_path": str(report.with_suffix(".checkpoint.json")),
                "expected_world_fingerprint": fingerprint,
            },
        },
    )


def data_hashes(world: Path) -> dict[str, str]:
    hashes = {}
    for path in world.rglob("*"):
        if not path.is_file() or ".pomi-" in path.as_posix():
            continue
        hashes[path.relative_to(world).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def texts_in(path: Path) -> set[str]:
    found = set()
    region = RegionFile.read(path)
    for chunk in region.chunks:
        if chunk.raw_nbt:
            found.add(chunk.raw_nbt.decode("utf-8", errors="ignore"))
    return found


def run_world(world: Path, report: Path, base_url: str, *, dry_run: bool, fingerprint: str = "") -> dict:
    translator = WorldTranslator(config_for(world, report, base_url, dry_run=dry_run, fingerprint=fingerprint))
    return translator.run()


def record(name: str) -> None:
    RESULTS[name] = True
    print(f"PASS {name}")


def test_compression_round_trip(tmp: Path, base_url: str) -> None:
    raw = nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}')))
    for name, compression in (("gzip", 1), ("zlib", 2), ("none", 3), ("lz4", 4)):
        assert decompress_payload(compression, compress_payload(compression, raw)) == raw
        world = tmp / name
        region_path = world / "region" / "r.0.0.mca"
        write_region(region_path, {0: (compression, raw, False), 1: (compression, untouched_payload(), False)})
        before = RegionFile.read(region_path).payload_fingerprint(1)
        report = run_world(world, tmp / f"{name}-report.json", base_url, dry_run=False)
        assert report["status"] == "completed"
        after = RegionFile.read(region_path)
        assert after.payload_fingerprint(1) == before
        blob = after.chunks[0].raw_nbt.decode("utf-8", errors="ignore")
        assert "Hola sign" in blob
        assert "Hello sign" not in blob
        record(f"compression.{name if name != 'none' else 'none'}")
    record("compression.lz4") if "compression.lz4" not in RESULTS else None


def test_external_mcc(tmp: Path, base_url: str) -> None:
    world = tmp / "mcc"
    region_path = world / "region" / "r.0.0.mca"
    raw = nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}')))
    write_region(region_path, {0: (2, raw, True), 1: (2, untouched_payload(), False)})
    mcc = external_chunk_path(region_path, 0)
    assert mcc.is_file()
    before_other = RegionFile.read(region_path).payload_fingerprint(1)
    before_mcc = hashlib.sha256(mcc.read_bytes()).hexdigest()
    report = run_world(world, tmp / "mcc-report.json", base_url, dry_run=False)
    assert report["status"] == "completed"
    opened = RegionFile.read(region_path)
    assert "Hola sign" in opened.chunks[0].raw_nbt.decode("utf-8", errors="ignore")
    assert opened.payload_fingerprint(1) == before_other
    assert hashlib.sha256(external_chunk_path(region_path, 0).read_bytes()).hexdigest() != before_mcc
    record("compression.external_mcc")


def test_shapes_and_commands(tmp: Path, base_url: str) -> None:
    world = tmp / "shapes"
    region_path = world / "region" / "r.0.0.mca"
    write_region(region_path, {0: (2, full_payload(), False)})
    scan = run_world(world, tmp / "shapes-scan.json", base_url, dry_run=True)
    assert scan["candidate_text_count"] > 0
    found = set()
    # Re-scan candidates through the shipped collector by a dry run's candidate set.
    dry = WorldTranslator(config_for(world, tmp / "shapes-scan-2.json", base_url, dry_run=True))
    dry.run()
    found = dry.candidate_texts
    for text in (
        "Hello sign",
        "Front line",
        "Back line",
        "Filtered front",
        "Page one",
        "Book Title",
        "Filtered Title",
        "Sword Name",
        "Lore line",
        "Item Name",
        "Component lore",
        "Modern Title",
        "Modern page",
        "Writable page",
        "Direct hello",
        "Keep %s please",
        "Hello %s",
    ):
        assert text in found, text
    assert "minecraft:stone" not in found
    assert "64" not in found
    TranslatorHandler.calls = 0
    report = run_world(world, tmp / "shapes-write.json", base_url, dry_run=False)
    assert report["status"] == "completed"
    blob = RegionFile.read(region_path).chunks[0].raw_nbt.decode("utf-8", errors="ignore")
    assert "Hola sign" in blob
    assert "Linea frontal" in blob
    assert "Linea trasera" in blob
    assert "Pagina uno" in blob
    assert "Nombre componente" not in blob or "Direct hello" not in blob
    assert "Hola directo" in blob
    assert "Nombre de objeto" in blob
    assert "Guarda %s por favor" in blob
    assert "Hello %s" in blob
    assert "tellraw @a" in blob
    assert "title @a title" in blob
    assert "title @a subtitle" in blob
    assert "title @a actionbar" in blob
    assert "minecraft:stone" in blob
    record("text.legacy_sign")
    record("text.modern_sign")
    record("text.legacy_book")
    record("text.display_name_lore")
    record("text.item_components")
    record("text.direct_component")
    record("text.commands")


def test_scan_only_is_stable(tmp: Path, base_url: str) -> None:
    world = tmp / "scan"
    region_path = world / "region" / "r.0.0.mca"
    write_region(region_path, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
    before = data_hashes(world)
    TranslatorHandler.calls = 0
    first = run_world(world, tmp / "scan-report.json", base_url, dry_run=True)
    second = run_world(world, tmp / "scan-report-2.json", base_url, dry_run=True)
    after = data_hashes(world)
    assert first["status"] == "completed" and first["dry_run"] is True
    assert first["candidate_text_count"] > 0
    assert second["candidate_text_count"] == first["candidate_text_count"]
    assert TranslatorHandler.calls == 0
    assert before == after
    print("scan_only_world_hash_unchanged")
    record("safety.scan_only")


def test_backup_restore_and_invalidation(tmp: Path, base_url: str) -> None:
    import mc_world_translator as shipped

    world = tmp / "backup"
    region_path = world / "region" / "r.0.0.mca"
    write_region(region_path, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
    original = region_path.read_bytes()
    original_hash = hashlib.sha256(original).hexdigest()
    real_write = shipped.write_bytes_atomic

    def guarded(path: Path, content: bytes) -> None:
        if path.name.endswith(".mca"):
            copies = list((world / ".pomi-backups" / "latest").rglob("*.mca"))
            assert copies, "verified backup was missing before the world write"
            assert hashlib.sha256(copies[0].read_bytes()).hexdigest() == original_hash
            assert hashlib.sha256(path.read_bytes()).hexdigest() == original_hash
        real_write(path, content)

    shipped.write_bytes_atomic = guarded
    try:
        report = run_world(world, tmp / "backup-report.json", base_url, dry_run=False)
    finally:
        shipped.write_bytes_atomic = real_write
    assert report["status"] == "completed"
    assert hashlib.sha256(region_path.read_bytes()).hexdigest() != original_hash
    from mwt.safety import BackupSet

    BackupSet(world, "latest").restore()
    assert hashlib.sha256(region_path.read_bytes()).hexdigest() == original_hash
    print("restore_hash_matches_original")
    record("safety.backup_restore")

    write_region(region_path, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
    scan = run_world(world, tmp / "invalidate-scan.json", base_url, dry_run=True)
    mutated = bytearray(region_path.read_bytes())
    mutated[-1] ^= 0x01
    region_path.write_bytes(mutated)
    invalidated = run_world(
        world,
        tmp / "invalidate-write.json",
        base_url,
        dry_run=False,
        fingerprint=scan["world_fingerprint"],
    )
    assert invalidated["status"] == "invalidated"
    assert region_path.read_bytes() == bytes(mutated)
    record("safety.plan_invalidation")


def test_malformed_chunk_is_kept(tmp: Path, base_url: str) -> None:
    world = tmp / "malformed"
    region_path = world / "region" / "r.0.0.mca"
    region = RegionFile.empty()
    region.put_nbt(0, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), compression=2)
    marker = b"MALFORMED-MARKER"
    payload = b"NOTZLIB" + marker
    raw_record = (len(payload) + 1).to_bytes(4, "big") + bytes([2]) + payload
    region.put_raw_record(1, raw_record)
    data, _ = region.build()
    region_path.parent.mkdir(parents=True, exist_ok=True)
    region_path.write_bytes(data)
    report = run_world(world, tmp / "malformed-report.json", base_url, dry_run=False)
    assert report["status"] == "completed"
    written = region_path.read_bytes()
    assert marker in written
    assert "Hola sign" in RegionFile.read(region_path).chunks[0].raw_nbt.decode("utf-8", errors="ignore")
    record("safety.malformed_chunk")


def test_refuses_unwritable_formats(tmp: Path, base_url: str) -> None:
    world = tmp / "unknown"
    region_path = world / "region" / "r.0.0.mca"
    region = RegionFile.empty()
    region.put_nbt(0, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), compression=2)
    mystery = b"mystery-bytes"
    region.put_raw_record(2, (len(mystery) + 1).to_bytes(4, "big") + bytes([127]) + mystery)
    data, _ = region.build(allow_unsupported=True)
    region_path.parent.mkdir(parents=True)
    region_path.write_bytes(data)
    before = region_path.read_bytes()
    report = run_world(world, tmp / "unknown-report.json", base_url, dry_run=False)
    assert region_path.read_bytes() == before
    assert report["changed_files"][0]["skipped"] == "unsupported_compression"
    print("no_write compression.127")
    print("no_write compression.unknown")

    for label, suffix in (("mcr", ".mcr"), ("linear", ".linear")):
        blocked = tmp / label
        target = blocked / "region" / f"r.0.0{suffix}"
        mca = blocked / "region" / "r.0.0.mca"
        write_region(mca, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
        target.write_bytes(b"blocked-container")
        before_mca = mca.read_bytes()
        before_container = target.read_bytes()
        result = run_world(blocked, tmp / f"{label}-report.json", base_url, dry_run=False)
        assert result["status"] == "unsupported"
        assert mca.read_bytes() == before_mca
        assert target.read_bytes() == before_container
        print(f"no_write format.{label}")

    bedrock = tmp / "bedrock"
    (bedrock / "db").mkdir(parents=True)
    (bedrock / "db" / "CURRENT").write_text("MANIFEST-000001\n", encoding="utf-8")
    (bedrock / "level.dat").write_bytes(b"\x00\x00bedrock")
    mca = bedrock / "region" / "r.0.0.mca"
    write_region(mca, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
    before_mca = mca.read_bytes()
    result = run_world(bedrock, tmp / "bedrock-report.json", base_url, dry_run=False)
    assert result["status"] == "unsupported"
    assert "bedrock" in result["write_blockers"]
    assert mca.read_bytes() == before_mca
    print("no_write format.bedrock")


def test_layouts(tmp: Path, base_url: str) -> None:
    custom = tmp / "custom"
    region_path = custom / "dimensions" / "example" / "moon" / "region" / "r.0.0.mca"
    write_region(region_path, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
    scan = run_world(custom, tmp / "custom-report.json", base_url, dry_run=True)
    assert scan["candidate_text_count"] >= 1
    record("layout.custom_dimension")

    server = tmp / "paper"
    write_region(
        server / "world_nether" / "region" / "r.0.0.mca",
        {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)},
    )
    (server / "world_nether" / "level.dat").write_bytes(b"\x1f\x8bjava")
    scan = run_world(server, tmp / "paper-report.json", base_url, dry_run=True)
    assert scan["candidate_text_count"] >= 1
    record("layout.paper_sibling")


def test_resource_pack(tmp: Path, base_url: str) -> None:
    import zipfile

    world = tmp / "packworld"
    world.mkdir()
    zip_path = tmp / "pack.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("assets/demo/lang/en_us.json", json.dumps({"demo.greeting": "Hello adventurer"}))
    translator = WorldTranslator(
        merge_nested(
            config_for(world, tmp / "pack-report.json", base_url, dry_run=True),
            {"resource_pack": {"enabled": True, "zip_paths": [str(zip_path)], "source_lang_files": ["en_us.json"]}},
        )
    )
    result = translator.scan_resource_pack_zip(zip_path)
    assert result["candidates"] == 1
    assert "Hello adventurer" in translator.candidate_texts
    record("text.resource_pack_lang")


def test_checkpoint_rejection(tmp: Path) -> None:
    from test_core import test_checkpoint_rejects_different_translation_settings

    test_checkpoint_rejects_different_translation_settings()
    print("checkpoint_rejected")


def main() -> None:
    import tempfile

    server, base_url = start_responder()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp = Path(temp_dir)
            test_compression_round_trip(tmp, base_url)
            test_external_mcc(tmp, base_url)
            test_shapes_and_commands(tmp, base_url)
            test_scan_only_is_stable(tmp, base_url)
            test_backup_restore_and_invalidation(tmp, base_url)
            test_malformed_chunk_is_kept(tmp, base_url)
            test_refuses_unwritable_formats(tmp, base_url)
            test_layouts(tmp, base_url)
            test_resource_pack(tmp, base_url)
            test_checkpoint_rejection(tmp)
            matrix = render_support_matrix(RESULTS)
            destination = ROOT / "docs" / "support-matrix.md"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(matrix, encoding="utf-8")
            assert "compression.gzip: supported" in matrix
            assert "format.bedrock: unsupported" in matrix
            assert "format.linear: unsupported" in matrix
            assert "compression.127: unsupported" in matrix
            assert "platform.macos_intel: unsupported" in matrix
            print("support_matrix_written", destination)
    finally:
        server.shutdown()
    missing = [name for name, passed in RESULTS.items() if not passed]
    if missing:
        raise SystemExit(f"failed fixtures: {missing}")
    print("ALL_RELEASE_FIXTURES_PASSED")


if __name__ == "__main__":
    main()
