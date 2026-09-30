"""Safe, read-only import of the public settings in a legacy ``translate.py``."""

from __future__ import annotations

import ast
from urllib.parse import urlsplit


MAX_SOURCE_BYTES = 1024 * 1024
MAX_ENDPOINT_CHARS = 2048
MAX_MODEL_CHARS = 256
MAX_SYSTEM_PROMPT_CHARS = 8000
_ERROR = "Invalid legacy translate.py settings"
_PUBLIC_NAMES = frozenset({"BASE_URL", "MODEL", "SYSTEM_PROMPT"})
_FIELD_LIMITS = {
    "BASE_URL": MAX_ENDPOINT_CHARS,
    "MODEL": MAX_MODEL_CHARS,
    "SYSTEM_PROMPT": MAX_SYSTEM_PROMPT_CHARS,
}
_PROMPT_WHITESPACE = frozenset({"\t", "\r", "\n"})


def _invalid() -> ValueError:
    # Do not include source text, parser errors, or literal values in exceptions.
    return ValueError(_ERROR)


def _contains_invalid_control(value: str, *, allowed_whitespace: frozenset[str] = frozenset()) -> bool:
    return any(
        (ord(char) < 0x20 and char not in allowed_whitespace)
        or 0x7F <= ord(char) <= 0x9F
        for char in value
    )


def _target_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        return set().union(*(_target_names(item) for item in target.elts))
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    return set()


def _safe_endpoint(value: str) -> bool:
    if not value or value != value.strip() or any(char.isspace() for char in value):
        return False
    if "?" in value or "#" in value:
        return False
    try:
        parsed = urlsplit(value)
        # Accessing .port validates malformed and out-of-range port numbers.
        parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme.lower() in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
    )


def _literal_string(name: str, node: ast.expr) -> str:
    try:
        value = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise _invalid() from None
    if type(value) is not str or not value or not value.strip():
        raise _invalid()
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        raise _invalid() from None
    if len(value) > _FIELD_LIMITS[name]:
        raise _invalid()
    if _contains_invalid_control(
        value,
        allowed_whitespace=_PROMPT_WHITESPACE if name == "SYSTEM_PROMPT" else frozenset(),
    ):
        raise _invalid()
    if name == "BASE_URL" and not _safe_endpoint(value):
        raise _invalid()
    return value


def parse_legacy_settings(source: object) -> dict[str, dict[str, str]]:
    """Return the supported public ``translate.py`` settings without executing code.

    Only top-level, single-name ``Assign`` and ``AnnAssign`` nodes are considered.
    API credentials and all paths are deliberately outside this import contract.
    """
    if type(source) is not str:
        raise _invalid()
    try:
        encoded = source.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        raise _invalid() from None
    if len(encoded) > MAX_SOURCE_BYTES or _contains_invalid_control(
        source, allowed_whitespace=_PROMPT_WHITESPACE
    ):
        raise _invalid()
    try:
        tree = ast.parse(source, mode="exec")
    except (SyntaxError, ValueError, TypeError, MemoryError, RecursionError):
        raise _invalid() from None

    found: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            targets = statement.targets
            if not any(_target_names(target) & _PUBLIC_NAMES for target in targets):
                continue
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                raise _invalid()
            name = targets[0].id
            value_node = statement.value
        elif isinstance(statement, ast.AnnAssign):
            if not (_target_names(statement.target) & _PUBLIC_NAMES):
                continue
            if not isinstance(statement.target, ast.Name):
                raise _invalid()
            name = statement.target.id
            value_node = statement.value
            if value_node is None:
                raise _invalid()
        else:
            continue

        if name not in _PUBLIC_NAMES:
            continue
        found[name] = _literal_string(name, value_node)

    if not found:
        raise _invalid()

    result: dict[str, dict[str, str]] = {}
    api: dict[str, str] = {}
    prompt: dict[str, str] = {}
    if "BASE_URL" in found:
        api.update({
            "provider": "custom",
            "wire_format": "openai",
            "base_url": found["BASE_URL"],
        })
    if "MODEL" in found:
        api["model"] = found["MODEL"]
    if "SYSTEM_PROMPT" in found:
        prompt["custom_system_prompt"] = found["SYSTEM_PROMPT"]
    if api:
        result["api"] = api
    if prompt:
        result["prompt"] = prompt
    return result
