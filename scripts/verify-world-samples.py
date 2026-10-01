"""Offline scan, byte preservation and copy-only write/restore checks for local samples.

Samples and results belong under ignored output/. Standalone regions are not full
world saves, and passing this command never promotes a whole Minecraft version.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mc_world_translator import DEFAULT_CONFIG, WorldTranslator, merge_nested
from llm_backends import LLMProviderClient
from mwt import nbtio
from mwt.region import RegionError, RegionFile
from mwt.safety import world_fingerprint


def hashes(root: Path) -> dict[str, str]:
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    result = {}
    for path in paths:
        if not path.is_file() or any(part.startswith(".pomi-") for part in path.parts):
            continue
        if path.is_symlink():
            raise ValueError("Sample must contain only regular files")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        result[path.name if root.is_file() else str(path.relative_to(root))] = digest.hexdigest()
    return result


def inspect_regions(world: Path) -> dict:
    versions, compressions = Counter(), Counter()
    unreadable_regions = []
    chunks = preserved = malformed = unsupported = command_json = command_non_json = 0
    for path in sorted(world.rglob("*.mca")):
        try:
            region = RegionFile.read(path)
        except (RegionError, OSError, ValueError) as exc:
            unreadable_regions.append({"file": str(path.relative_to(world)), "error": str(exc)})
            continue
        for chunk in region.chunks:
            if chunk.empty:
                continue
            chunks += 1
            compressions[str(chunk.compression)] += 1
            malformed += int(chunk.malformed)
            unsupported += int(chunk.unsupported)
            if not chunk.raw_nbt:
                continue
            parsed = nbtio.parse(chunk.raw_nbt, keep_scalars="all")
            assert parsed.dump() == chunk.raw_nbt, "Unedited NBT changed"
            preserved += 1
            data = parsed.get("DataVersion")
            versions[str(data.value) if data is not None else "unknown"] += 1
            stack = [parsed]
            while stack:
                node = stack.pop()
                if isinstance(node, nbtio.TAG_Compound):
                    command = node.get("Command")
                    if isinstance(command, nbtio.TAG_String):
                        # Count syntax evidence, not translated-text coverage.
                        probe = object.__new__(WorldTranslator)
                        extracted = probe.extract_command_json(command.value)
                        if extracted:
                            try:
                                json.loads(extracted[1])
                                command_json += 1
                            except json.JSONDecodeError:
                                command_non_json += 1
                    stack.extend(value for _, value in node.items())
                elif isinstance(node, nbtio.TAG_List):
                    stack.extend(node)
    return {
        "chunks": chunks, "unchangedNbtByteIdentical": preserved,
        "malformedChunks": malformed, "unsupportedChunks": unsupported,
        "dataVersions": dict(versions), "compressions": dict(compressions),
        "recognizedJsonCommands": command_json, "recognizedNonJsonCommands": command_non_json,
        "unreadableRegionFiles": unreadable_regions,
    }


def run_sample(source: Path, destination: Path) -> dict:
    source = source.resolve(strict=True)
    original = hashes(source)
    destination.mkdir(parents=True, exist_ok=False)
    world = destination / "world"
    if source.is_file():
        if source.suffix != ".mca":
            raise ValueError("Single-file input must be an Anvil region")
        (world / "region").mkdir(parents=True)
        shutil.copyfile(source, world / "region" / "r.0.0.mca")
    else:
        shutil.copytree(source, world, symlinks=False)
        for path in world.rglob("*"):
            if path.is_file():
                path.chmod(0o600)
    baseline = hashes(world)
    (destination / "baseline.json").write_text(json.dumps(baseline, indent=2))
    structure = inspect_regions(world)
    config = merge_nested(DEFAULT_CONFIG, {
        "world_dir": str(world), "dry_run": True, "inherit_translate_py": False,
        "report_path": str(destination / "scan.json"), "backup": True,
        "api": {"provider": "openai", "api_key": "offline-fixture", "model": "offline-fixture"},
        "runtime": {"checkpoint_enabled": False, "backup_store": str(destination / "backups")},
        "resource_pack": {"enabled": (world / "resources.zip").is_file(), "zip_paths": [str(world / "resources.zip")] if (world / "resources.zip").is_file() else []},
    })
    scan = WorldTranslator(config)
    scanned = scan.run()
    assert scanned["provider_requests"] == 0
    assert hashes(world) == baseline, "Scan Only modified the copy"
    sources = list(scan._candidate_order)
    summary = {
        "source": str(source), "completeWorldSave": (world / "level.dat").is_file(),
        "sourceFileCount": len(original), "sourceBytes": sum(path.stat().st_size for path in ([source] if source.is_file() else source.rglob("*")) if path.is_file()),
        **structure, "scanStatus": scanned["status"], "uniqueCandidates": len(sources),
        "occurrences": sum(item.get("count", 0) for item in scan.occurrences.values()),
        "scanNoWrite": True, "providerRequests": 0, "gameLoad": "NOT_RUN",
    }
    if sources:
        selected = [text for text in sources if len(text) < 500][:12]
        assert selected, "No bounded translation candidate was available"
        overrides = {text: ("검증 " + text if text in selected else text) for text in sources}
        config = merge_nested(config, {
            "dry_run": False, "report_path": str(destination / "translation.json"),
            "scan": {"overrides": overrides},
            "runtime": {"expected_world_fingerprint": world_fingerprint(world)},
        })
        writer = WorldTranslator(config)
        # A missed override is an error, never an accidental paid/network request.
        with patch.object(LLMProviderClient, "translate_mapping", side_effect=AssertionError("Network requests forbidden")):
            report = writer.run()
        assert report["provider_requests"] == 0
        changed = [name for name, digest in hashes(world).items() if baseline.get(name) != digest]
        assert changed and writer._run_backup is not None, "No text was actually written"
        try:
            after_structure = inspect_regions(world)
            assert after_structure["dataVersions"] == structure["dataVersions"], "Chunk versions changed"
            reopen = WorldTranslator(merge_nested(config, {
                "dry_run": True, "report_path": str(destination / "reopen.json"),
                "scan": {"skip_target_language_text": False},
                "runtime": {"expected_world_fingerprint": ""},
            }))
            reopen.run()
            assert all(overrides[text] in reopen._candidate_order for text in selected), "Written translations were not found on reopen"
        finally:
            writer._run_backup.restore()
        assert hashes(world) == baseline, "Restore did not return all files to baseline"
        summary.update({
            "writeRestore": "PASS", "selectedSources": len(selected),
            "changedFiles": len(changed), "writeStatus": report["status"],
            "restoreHashDifferences": 0, "backupSetId": writer._run_backup.backup_id,
        })
    else:
        summary.update({"writeRestore": "NOT_APPLICABLE_NO_CANDIDATES", "changedFiles": 0})
    assert hashes(source) == original, "Original sample was modified"
    summary["originalHashDifferences"] = 0
    (destination / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", action="append", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    ignored_root = (ROOT / "output").resolve()
    if not output.is_relative_to(ignored_root):
        parser.error("Output must be under the repository's ignored output/ directory")
    if any(output.is_relative_to(source.resolve()) or source.resolve().is_relative_to(output) for source in args.sample):
        parser.error("Output and originals must be separate directories")
    output.mkdir(parents=True, exist_ok=False)
    summaries = []
    for index, source in enumerate(args.sample):
        summaries.append(run_sample(source, output / f"sample-{index:02d}"))
        print(json.dumps(summaries[-1], ensure_ascii=False), flush=True)
    (output / "summary.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
