"""Explicit ZIP selections shared by desktop settings, scan plans and restore."""
from __future__ import annotations

from pathlib import Path
from mwt.safety import file_sha256


class ExternalPackUnavailable(ValueError):
    pass


def normalize_external_pack_paths(value: object) -> list[str]:
    if not isinstance(value, list) or len(value) > 16:
        raise ValueError('externalResourcePackPaths must be a list of at most 16 ZIP paths')
    result = []
    for value_path in value:
        if not isinstance(value_path, str) or not value_path.strip() or len(value_path) > 4096 or '\x00' in value_path:
            raise ValueError('External resource-pack path is invalid')
        text = value_path.strip()
        path = Path(text)
        if not path.is_absolute() or path.suffix.lower() != '.zip':
            raise ValueError('External resource packs require absolute ZIP paths')
        if text not in result:
            result.append(text)
    return result


def selected_pack_files(saved: dict) -> list[Path]:
    paths = normalize_external_pack_paths(saved.get('external_resource_pack_paths', []))
    result = []
    for text in paths:
        path = Path(text)
        if path.is_symlink() or not path.is_file():
            raise ExternalPackUnavailable('Selected external resource pack is missing or is a symbolic link')
        canonical = path.resolve(strict=True)
        if canonical not in result:
            result.append(canonical)
    return result


def pack_scope_signature(saved: dict) -> list[dict]:
    paths = normalize_external_pack_paths(saved.get('external_resource_pack_paths', []))
    if not saved.get('resource_pack_enabled'):
        return [{'path': path} for path in paths]
    result = []
    for path in selected_pack_files(saved):
        before = path.stat()
        digest = file_sha256(path)
        after = path.stat()
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ExternalPackUnavailable('External resource pack changed while checking the scan plan')
        parent = path.parent.stat()
        result.append({'path': str(path), 'sha256': digest, 'parentIdentity': f'{parent.st_dev}:{parent.st_ino}'})
    return result
