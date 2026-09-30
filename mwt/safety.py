"""Verified backups and world fingerprints for the shipped write path."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SKIP_DIR_NAMES = {".pomi-backups", ".pomi-translate", "__pycache__", ".venv"}
DATA_SUFFIXES = {".mca", ".mcc", ".mcr", ".linear", ".dat"}


class BackupError(RuntimeError):
    pass


class ExternalTargetError(BackupError):
    pass


class PlanInvalidated(RuntimeError):
    pass


def iter_data_files(world_dir: Path) -> list[Path]:
    from mwt.layout import world_data_roots

    root = world_dir.resolve()
    files: list[Path] = []
    for data_root in world_data_roots(root):
        if not data_root.resolve().is_relative_to(root):
            raise ValueError("World data source is outside the selected world")
        for path in data_root.rglob("*"):
            if any(part in SKIP_DIR_NAMES for part in path.relative_to(root).parts):
                continue
            if path.suffix.lower() not in DATA_SUFFIXES and path.name not in {"level.dat", "resources.zip"}:
                continue
            if not path.resolve().is_relative_to(root):
                raise ValueError("World data source is outside the selected world")
            if path.is_file():
                files.append(path)
    return sorted(files)


def world_fingerprint(world_dir: Path) -> str:
    digest = hashlib.sha256()
    root = world_dir.resolve()
    for path in iter_data_files(root):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        digest.update(b"\0")
    return digest.hexdigest()


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def legacy_backup_store(world_dir: Path) -> Path:
    """Where releases before the app-data store kept backups: inside the world folder."""
    return world_dir.resolve() / ".pomi-backups"


def backup_store(world_dir: Path, data_dir: Path) -> Path:
    """One folder per world under the app data directory.

    Backups next to the world travel with it when the folder is zipped or shared, and vanish
    when it is deleted. The key is the resolved path, so two worlds with the same name stay apart.
    """
    resolved = world_dir.resolve()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", resolved.name).strip("-.")[:40] or "world"
    key = hashlib.sha256(str(resolved).encode("utf-8")).hexdigest()[:10]
    return data_dir / "backups" / f"{slug}-{key}"


class BackupSet:
    """Copy world files, verify the copies, and only then allow a write."""

    def __init__(self, world_dir: Path, backup_id: str = "latest", store: Path | None = None, *, external_files: list[Path] | None = None) -> None:
        self.world_dir = world_dir.resolve()
        # Only explicitly selected ZIP files may become external write targets.
        # A manifest cannot grant itself permission to overwrite an arbitrary path.
        self.external_files: dict[str, str] = {}
        for path in external_files or []:
            selected = Path(path).expanduser()
            if selected.is_symlink() or not selected.is_file() or selected.suffix.lower() != ".zip":
                raise ExternalTargetError("External resource pack must be an existing regular ZIP file")
            resolved = selected.resolve(strict=True)
            if resolved.is_relative_to(self.world_dir):
                continue
            self.external_files[str(resolved)] = self._parent_identity(resolved)
        self.store = Path(store) if store is not None else legacy_backup_store(self.world_dir)
        if backup_id == "latest":
            pointer = self.store / "latest.json"
            if pointer.is_file():
                backup_id = str(json.loads(pointer.read_text(encoding="utf-8"))["backupSetId"])
        if not re.fullmatch(r"[A-Za-z0-9_-]+", backup_id):
            raise BackupError("Invalid backup set ID")
        self.backup_id = backup_id
        self.root = self.store / backup_id
        self.manifest_path = self.root / "manifest.json"
        self.entries: list[dict[str, str]] = []
        self._written: set[str] = set()

    @classmethod
    def new(cls, world_dir: Path, *, kind: str = "translation", store: Path | None = None, external_files: list[Path] | None = None) -> "BackupSet":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_id = f"{stamp}-{uuid.uuid4().hex[:12]}-{kind}"
        return cls(world_dir, backup_id, store, external_files=external_files)

    @classmethod
    def find(cls, world_dir: Path, backup_id: str, stores: list[Path], *, external_files: list[Path] | None = None) -> "BackupSet":
        """Open a backup by id from the first store that has it."""
        for store in stores:
            candidate = cls(world_dir, backup_id, store, external_files=external_files)
            if candidate.manifest_path.is_file():
                return candidate
        raise BackupError("Backup set was not found")

    @classmethod
    def open_existing(cls, world_dir: Path, backup_id: str, store: Path | None = None, *, external_files: list[Path] | None = None) -> "BackupSet":
        backup = cls(world_dir, backup_id, store, external_files=external_files)
        if not backup.manifest_path.is_file():
            raise BackupError("Backup set for resume was not found")
        payload = json.loads(backup.manifest_path.read_text(encoding="utf-8"))
        if payload.get("verified") is not True:
            raise BackupError("Backup set for resume is not verified")
        backup.entries = backup._validated_manifest_entries(payload)
        for entry in backup.entries:
            if "externalTarget" in entry:
                backup._target(entry)
        backup._written = {entry["path"] for entry in backup.entries}
        backup.verify()
        return backup

    def publish_latest(self) -> None:
        self.verify()
        pointer = self.store / "latest.json"
        pointer.parent.mkdir(parents=True, exist_ok=True)
        temporary = pointer.with_suffix(".json.tmp")
        temporary.write_text(json.dumps({"backupSetId": self.backup_id}), encoding="utf-8")
        os.replace(temporary, pointer)

    def external_targets(self) -> list[Path]:
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        return [Path(entry["externalTarget"]) for entry in self._validated_manifest_entries(payload) if "externalTarget" in entry]

    def add(self, path: Path) -> None:
        if path.is_symlink():
            raise BackupError("Symbolic links cannot be backed up as writable targets")
        path = path.resolve()
        if not path.is_file():
            return
        external = not path.is_relative_to(self.world_dir)
        if external:
            relative = self._external_archive_path(path)
            target = {"externalTarget": str(path), "externalParentId": self._parent_identity(path)}
            self._target({"path": relative, **target})
        else:
            relative = path.relative_to(self.world_dir).as_posix()
            target = {}
        for entry in self.entries:
            if entry["path"] == relative:
                if entry.get("externalTarget") != target.get("externalTarget"):
                    raise BackupError("Backup target collides with an existing entry")
                return
        destination = self.root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        original = file_sha256(path)
        copied = file_sha256(destination)
        if original != copied:
            raise BackupError(f"Backup hash mismatch for {relative}")
        self.entries.append({"path": relative, "sha256": original, "size": str(path.stat().st_size), **target})
        self._write_manifest()

    def verify(self) -> None:
        if not self.entries:
            raise BackupError("No files were backed up")
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        if payload.get("verified") is not True:
            raise BackupError("Backup manifest is not verified")
        for entry in self._validated_manifest_entries(payload):
            copied = self.root / entry["path"]
            if not copied.is_file() or file_sha256(copied) != entry["sha256"]:
                raise BackupError(f"Backup verification failed for {entry['path']}")
            if entry["path"] in self._written:
                continue
            source = self._target(entry)
            if file_sha256(source) != entry["sha256"]:
                raise BackupError(f"Backup verification failed for {entry['path']}")

    def mark_written(self, paths: list[Path]) -> None:
        """Remember files this run has already replaced so later verifies do not expect the pre-write bytes."""
        for path in paths:
            resolved = path.resolve()
            self._written.add(resolved.relative_to(self.world_dir).as_posix() if resolved.is_relative_to(self.world_dir) else self._external_archive_path(resolved))

    def restore(self, recovery_store: Path | None = None) -> str:
        """Put the backed-up files back. The files they replace are kept as a recovery set first."""
        payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        entries = self._validated_manifest_entries(payload)
        if not payload.get("verified") or not entries:
            raise BackupError("Refusing to restore an unverified backup set")
        for entry in entries:
            source = self.root / entry["path"]
            # Validate every destination before creating recovery files or replacing any file.
            self._target(entry)
            if not source.is_file() or file_sha256(source) != entry["sha256"]:
                raise BackupError(f"Refusing to restore an unverified backup of {entry['path']}")

        recovery = BackupSet.new(self.world_dir, kind="recovery", store=recovery_store or self.store,
                                 external_files=[Path(path) for path in self.external_files])
        for entry in entries:
            current = self._target(entry)
            if current.is_file():
                recovery.add(current)
        if recovery.entries:
            recovery.publish_latest()
        for entry in entries:
            source = self.root / entry["path"]
            destination = self._target(entry)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(f".{destination.name}.pomi-restore-{uuid.uuid4().hex}.tmp")
            try:
                shutil.copy2(source, temporary)
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
            if file_sha256(destination) != entry["sha256"]:
                raise BackupError(f"Restore hash mismatch for {entry['path']}")
        return recovery.backup_id if recovery.entries else ""

    @staticmethod
    def _parent_identity(path: Path) -> str:
        info = path.parent.stat()
        return f"{info.st_dev}:{info.st_ino}"

    @staticmethod
    def _external_archive_path(path: Path) -> str:
        return "__external_packs__/" + hashlib.sha256(str(path).encode("utf-8")).hexdigest() + "/pack.zip"

    def _target(self, entry: dict[str, str]) -> Path:
        selected = entry.get("externalTarget")
        if selected is None:
            return self.world_dir / entry["path"]
        path = Path(selected)
        if (selected not in self.external_files or path.is_symlink() or not path.is_file()
                or str(path.resolve(strict=True)) != selected
                or self._parent_identity(path) != entry.get("externalParentId")
                or self.external_files[selected] != entry.get("externalParentId")):
            raise ExternalTargetError("External resource pack is unavailable or not explicitly selected for restore")
        return path

    def _validated_manifest_entries(self, payload: dict) -> list[dict[str, str]]:
        files = payload.get("files")
        if not isinstance(files, list):
            raise BackupError("Backup manifest file list is invalid")
        world_root = self.world_dir.resolve()
        backup_root = self.root.resolve()
        entries: list[dict[str, str]] = []
        seen: set[str] = set()
        for raw in files:
            if not isinstance(raw, dict):
                raise BackupError("Backup manifest entry is invalid")
            relative_text = raw.get("path")
            digest = raw.get("sha256")
            size = raw.get("size")
            if not isinstance(relative_text, str) or not isinstance(digest, str) or not isinstance(size, str):
                raise BackupError("Backup manifest entry fields are invalid")
            relative = PurePosixPath(relative_text)
            if (
                relative.is_absolute()
                or not relative.parts
                or any(part in {"", ".", ".."} for part in relative.parts)
                or relative.parts[0] in SKIP_DIR_NAMES
                or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or not size.isdigit()
                or relative_text in seen
            ):
                raise BackupError("Backup manifest path or hash is invalid")
            backup_path = (self.root / Path(*relative.parts)).resolve()
            external_target = raw.get("externalTarget")
            external_parent = raw.get("externalParentId")
            if external_target is not None:
                if (not isinstance(external_target, str) or not Path(external_target).is_absolute()
                        or Path(external_target).suffix.lower() != ".zip"
                        or Path(external_target).is_relative_to(world_root)
                        or relative_text != self._external_archive_path(Path(external_target))
                        or not isinstance(external_parent, str) or not re.fullmatch(r"\d+:\d+", external_parent)):
                    raise BackupError("External backup target is invalid")
            elif external_parent is not None:
                raise BackupError("External backup target is invalid")
            world_path = (self.world_dir / Path(*relative.parts)).resolve()
            if not backup_path.is_relative_to(backup_root) or (external_target is None and not world_path.is_relative_to(world_root)):
                raise BackupError("Backup manifest path escapes its allowed root")
            seen.add(relative_text)
            entry = {"path": relative_text, "sha256": digest, "size": size}
            if external_target is not None:
                entry.update(externalTarget=external_target, externalParentId=external_parent)
            entries.append(entry)
        return entries

    def _write_manifest(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        document = {
            "schemaVersion": 2,
            "backupSetId": self.backup_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "verified": True,
            "files": self.entries,
        }
        temporary = self.manifest_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(document, indent=2), encoding="utf-8")
        os.replace(temporary, self.manifest_path)


def list_backup_sets(world_dir: Path, stores: list[Path] | None = None) -> list[dict]:
    """Backups of a world from the app store and, for older runs, from inside the world folder."""
    locations = stores if stores is not None else [legacy_backup_store(world_dir)]
    result = []
    seen: set[str] = set()
    for store in locations:
        if not store.is_dir():
            continue
        for manifest in store.glob("*/manifest.json"):
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                backup_id = manifest.parent.name
                if not re.fullmatch(r"[A-Za-z0-9_-]+", backup_id) or backup_id in seen:
                    continue
                seen.add(backup_id)
                files = data.get("files", [])
                result.append({
                    "backupSetId": backup_id,
                    "createdAt": data.get("createdAt") or datetime.fromtimestamp(manifest.stat().st_mtime, timezone.utc).isoformat(),
                    "fileCount": len(files),
                    "verified": data.get("verified") is True,
                    "kind": "recovery" if backup_id.endswith("-recovery") else "translation",
                    "sizeBytes": sum(int(item.get("size", 0)) for item in files if str(item.get("size", "")).isdigit()),
                    "inWorldFolder": store.resolve() == legacy_backup_store(world_dir),
                    "externalTargets": [item["externalTarget"] for item in files if isinstance(item, dict) and isinstance(item.get("externalTarget"), str)],
                })
            except (OSError, ValueError, TypeError):
                continue
    return sorted(result, key=lambda item: item["createdAt"], reverse=True)
