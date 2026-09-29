"""Keep formatting tokens inside player-visible strings."""

from __future__ import annotations

import re

# printf-style arguments, {named} placeholders and Minecraft § formatting codes (§6, §l, §r, §x...).
_TOKEN = re.compile(r"%(?:\d+\$)?[sdif]|%%|\{[A-Za-z0-9_]+\}|§.")


def tokens_preserved(original: str, translated: str) -> bool:
    for token in set(_TOKEN.findall(original)):
        if translated.count(token) < original.count(token):
            return False
    return True


def preserve_tokens(original: str, translated: str) -> str:
    if not isinstance(translated, str) or not translated:
        return original
    return translated if tokens_preserved(original, translated) else original
