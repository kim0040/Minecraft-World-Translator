"""Verified backups and world fingerprints for the shipped write path."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

SKIP_DIR_NAMES = {".pomi-backups", ".pomi-translate", "__pycache__", ".venv"}
DATA_SUFFIXES = {".mca", ".mcc", ".mcr", ".linear", ".dat"}


class BackupError(RuntimeError):
    pass


class PlanInvalidated(RuntimeError):
    pass


def iter_data_files(world_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in world_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(world_dir).parts):
            continue
        if path.suffix.lower() in DATA_SUFFIXES or path.name == "level.dat":
            files.append(path)
    return sorted(files)


def world_fingerprint(world_dir: Path) -> str:
    digest = hashlib.sha256()
    root = world_dir.resolve()
    for path in iter_data_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BackupSet:
    """Copy world files, verify the copies, and only then allow a write."""

    def __init__(self, world_dir: Path, backup_id: str = "latest") -> None:
        self.world_dir = world_dir.resolve()
        self.root = self.world_dir / ".pomi-backups" / backup_id
        self.manifest_path = self.root / "manifest.json"
        self.entries: list[dict[str, str]] = []

    def add(self, path: Path) -> None:
        path = path.resolve()
        if not path.is_file():
            return
        relative = path.relative_to(self.world_dir).as_posix()
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        original = file_sha256(path)
        copied = file_sha256(destination)
        if original != copied:
            raise BackupError(f"Backup hash mismatch for {relative}")
        self.entries.append({"path": relative, "sha256": original, "size": str(path.stat().st_size)})
        self._write_manifest()

    def verify(self) -> None:
        if not self.entries:
            raise BackupError("No files were backed up")
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if payload.get("verified") is not True:
            raise BackupError("Backup manifest is not verified")
        for entry in payload["files"]:
            source = self.world_dir / entry["path"]
            copied = self.root / entry["path"]
            if file_sha256(source) != entry["sha256"] or file_sha256(copied) != entry["sha256"]:
                raise BackupError(f"Backup verification failed for {entry['path']}")

    def restore(self) -> None:
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        for entry in payload["files"]:
            source = self.root / entry["path"]
            destination = self.world_dir / entry["path"]
            if file_sha256(source) != entry["sha256"]:
                raise BackupError(f"Refusing to restore an unverified backup of {entry['path']}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            if file_sha256(destination) != entry["sha256"]:
                raise BackupError(f"Restore hash mismatch for {entry['path']}")

    def _write_manifest(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        document = {"verified": True, "files": self.entries}
        temporary = self.manifest_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(document, indent=2), encoding="utf-8")
        os.replace(temporary, self.manifest_path)
