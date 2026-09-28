"""Settings and model catalogs live outside the app install.

An update replaces the program files. This directory stays until the user
deletes it. API keys are not written here.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCHEMA = 1
SECRET_FIELDS = {"api_key", "apikey", "secret", "token", "password", "authorization"}


def user_data_dir(root: Path | None = None) -> Path:
    if root is not None:
        path = Path(root)
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "PomiTranslate"
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        path = Path(base) / "PomiTranslate"
    else:
        base = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
        path = Path(base) / "PomiTranslate"
    path.mkdir(parents=True, exist_ok=True)
    return path


def settings_path(root: Path | None = None) -> Path:
    return user_data_dir(root) / "settings.json"


def load_user_settings(root: Path | None = None) -> dict:
    path = settings_path(root)
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(loaded, dict):
        return {}
    return {key: value for key, value in loaded.items() if str(key).lower() not in SECRET_FIELDS}


def remember_user_settings(updates: dict, root: Path | None = None) -> dict:
    """Merge public preferences. Unknown keys already on disk are kept."""
    current = load_user_settings(root)
    for key, value in updates.items():
        if str(key).lower() in SECRET_FIELDS:
            continue
        current[key] = value
    current["schema"] = SCHEMA
    path = settings_path(root)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)
    return current


def _catalog_path(provider: str, root: Path | None = None) -> Path:
    safe = "".join(character if character.isalnum() or character in {"-", "_"} else "_" for character in provider)
    return user_data_dir(root) / "models" / f"{safe}.json"


def remember_model_catalog(provider: str, models: list[dict], root: Path | None = None) -> None:
    path = _catalog_path(provider, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"schema": SCHEMA, "provider": provider, "models": models}
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def load_model_catalog(provider: str, root: Path | None = None) -> list[dict]:
    path = _catalog_path(provider, root)
    if not path.is_file():
        return []
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    models = loaded.get("models") if isinstance(loaded, dict) else None
    if not isinstance(models, list):
        return []
    return [item for item in models if isinstance(item, dict) and "api_key" not in item]


def public_settings_from_config(config: dict) -> dict:
    api = config.get("api") or {}
    prompt = config.get("prompt") or {}
    return {
        "provider": api.get("provider", ""),
        "model": api.get("model", ""),
        "base_url": api.get("base_url", ""),
        "wire_format": api.get("wire_format", ""),
        "target_language": prompt.get("target_language", ""),
        "style_preset": prompt.get("style_preset", ""),
        "style_prompt": prompt.get("style_prompt", ""),
        "custom_system_prompt": prompt.get("custom_system_prompt", ""),
        "temperature": config.get("temperature", ""),
        "batch_size": config.get("batch_size", ""),
        "last_world_dir": config.get("world_dir", ""),
    }
