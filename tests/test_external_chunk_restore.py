"""Synthetic 255-sector boundary, partial write, and new-file recovery contracts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested
from mwt.region import RegionFile, SECTOR, external_chunk_path
from mwt.safety import BackupSet, BackupError, world_fingerprint
from test_release_fixtures import compound, string, nbt_bytes, write_region


def fixture(root: Path, spare: int = 32) -> tuple[WorldTranslator, Path, bytes]:
    world = root / "world"
    path = world / "region/r.0.0.mca"
    raw = nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}')))
    # A valid Byte_Array occupies the slot; the visible string alone is changed.
    name = b"Padding"
    overhead = 1 + 2 + len(name) + 4
    count = 255 * SECTOR - 5 - spare - len(raw) - overhead
    raw = raw[:-1] + b"\x07" + len(name).to_bytes(2, "big") + name + count.to_bytes(4, "big") + bytes(count) + raw[-1:]
    assert len(raw) + 5 == 255 * SECTOR - spare
    write_region(path, {0: (3, raw, False)})
    assert not RegionFile.read(path).chunks[0].external
    translator = WorldTranslator(merge_nested(DEFAULT_CONFIG, {
        "world_dir": str(world), "dry_run": False, "inherit_translate_py": False,
        "report_path": str(root / "report.json"),
        "runtime": {"backup_store": str(root / "backups"), "checkpoint_enabled": False},
    }))
    translator.final_translations = {"Hello sign": "Translated " + "x" * 100}
    return translator, path, path.read_bytes()


def test_boundary_and_restore(root: Path) -> None:
    for spare, external in [(0, True), (32, True), (1024, False)]:
        writer, path, original = fixture(root / str(spare), spare)
        world = path.parent.parent
        baseline = world_fingerprint(world)
        result = writer.apply_region_file(path)
        assert result["changed_chunks"] == 1
        opened = RegionFile.read(path)
        assert opened.chunks[0].external is external
        assert b"Translated " in opened.chunks[0].raw_nbt
        mcc = external_chunk_path(path, 0)
        assert mcc.exists() is external
        assert set(result["written_files"]) == ({str(path), str(mcc)} if external else {str(path)})
        writer.report["changed_files"] = [result]
        writer.refresh_report_counts()
        assert writer.report["changed_file_count"] == (2 if external else 1)
        # Older checkpoints lack the additive list and retain their region count.
        writer.report["changed_files"] = [{key: value for key, value in result.items() if key != "written_files"}]
        writer.refresh_report_counts()
        assert writer.report["changed_file_count"] == 1
        writer.report["changed_files"] = [result, result]
        writer.report["resource_packs"] = [{"zip_path": "pack.zip", "translated_files": 2}] * 2
        writer.refresh_report_counts()
        assert writer.report["changed_file_count"] == (3 if external else 2)
        backup = writer._run_backup
        assert backup is not None
        manifest = json.loads(backup.manifest_path.read_text())
        assert manifest["schemaVersion"] == (3 if external else 2)
        translated = path.read_bytes()
        payload = mcc.read_bytes() if external else None
        # Reopen the backup from disk, including after process restart.
        backup = BackupSet.open_existing(world, backup.backup_id, backup.store)
        recovery_id = backup.restore()
        assert path.read_bytes() == original and not mcc.exists()
        assert world_fingerprint(world) == baseline
        recovery = BackupSet.open_existing(world, recovery_id, backup.store)
        order = []
        import mwt.safety as safety
        replace = safety.os.replace
        def record_replace(source, destination):
            if Path(destination).suffix in {".mca", ".mcc"}:
                order.append(Path(destination).suffix)
            return replace(source, destination)
        with patch.object(safety.os, "replace", side_effect=record_replace):
            recovery.restore()
        assert path.read_bytes() == translated
        if external:
            assert mcc.read_bytes() == payload
            assert order.index(".mcc") < order.index(".mca")
        backup.restore()
        assert world_fingerprint(world) == baseline


def test_partial_write(root: Path) -> None:
    for failed_suffix in [".mcc", ".mca"]:
        writer, path, original = fixture(root / failed_suffix[1:])
        baseline = world_fingerprint(path.parent.parent)
        writes = []
        write = writer._write_world_bytes
        def fail(target, data):
            writes.append(target.suffix)
            if target.suffix == failed_suffix:
                raise OSError("synthetic interrupted write")
            return write(target, data)
        with patch.object(writer, "_write_world_bytes", side_effect=fail):
            try:
                writer.apply_region_file(path)
                raise AssertionError("write failure was not propagated")
            except OSError:
                pass
        assert writes[0] == ".mcc"
        assert path.read_bytes() == original  # Never publish a missing external pointer.
        backup = writer._run_backup
        assert backup is not None
        reopened = BackupSet.open_existing(path.parent.parent, backup.backup_id, backup.store)
        reopened.restore()
        assert world_fingerprint(path.parent.parent) == baseline


def test_restore_validation(root: Path) -> None:
    writer, path, _ = fixture(root)
    writer.apply_region_file(path)
    backup = writer._run_backup
    assert backup is not None
    mcc = external_chunk_path(path, 0)
    current = path.read_bytes()
    payload = mcc.read_bytes()
    other = path.parent / "protected.bin"
    other.write_bytes(b"untouched")
    mcc.unlink()
    mcc.symlink_to(other)
    try:
        backup.restore()
        raise AssertionError("symlink restore was accepted")
    except BackupError:
        pass
    assert path.read_bytes() == current and other.read_bytes() == b"untouched"
    mcc.unlink(); mcc.write_bytes(payload)
    document = json.loads(backup.manifest_path.read_text())
    for change in [{"restoreAction": "unknown"}, {"path": "protected.bin"}, {"path": "../c.0.0.mcc"}]:
        altered = json.loads(json.dumps(document))
        altered["files"][-1].update(change)
        backup.manifest_path.write_text(json.dumps(altered))
        try:
            backup.restore()
            raise AssertionError("invalid creation marker accepted")
        except BackupError:
            pass
        assert path.read_bytes() == current and mcc.read_bytes() == payload
    backup.manifest_path.write_text(json.dumps(document))
    backup.restore()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="pomi-external-chunk-") as temporary:
        root = Path(temporary)
        test_boundary_and_restore(root / "boundary")
        test_partial_write(root / "failure")
        test_restore_validation(root / "validation")
    print("EXTERNAL_CHUNK_RESTORE_PASSED (boundary3 / failure2 / validation4 / recovery)")


if __name__ == "__main__":
    main()
