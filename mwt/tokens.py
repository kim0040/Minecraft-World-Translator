"""Keep formatting tokens inside player-visible strings."""

from __future__ import annotations

import re

_TOKEN = re.compile(r"%(?:\d+\$)?[sdif]|%%|\{[A-Za-z0-9_]+\}")


def preserve_tokens(original: str, translated: str) -> str:
    if not isinstance(translated, str) or not translated:
        return original
    required = _TOKEN.findall(original)
    if not required:
        return translated
    for token in required:
        if translated.count(token) < original.count(token):
            return original
    return translated
