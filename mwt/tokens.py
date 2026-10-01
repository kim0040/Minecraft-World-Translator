"""Keep formatting tokens inside player-visible strings."""

from __future__ import annotations

import re

# printf-style arguments, {named} placeholders and Minecraft § formatting codes (§6, §l, §r, §x...).
_TOKEN = re.compile(r"%(?:\d+\$)?[sdif]|%%|\{[A-Za-z0-9_]+\}|§.")


def tokens_preserved(original: str, translated: str) -> bool:
    """Every token survives exactly as often as in the original, and none is invented.

    A dropped token loses formatting or an argument; an added one recolours other words (a model
    once answered ``§6Merchant §rof ...`` with two ``§6``) or consumes an argument that is not there.
    """
    expected: dict[str, int] = {}
    for token in _TOKEN.findall(original):
        expected[token] = expected.get(token, 0) + 1
    found: dict[str, int] = {}
    for token in _TOKEN.findall(translated):
        found[token] = found.get(token, 0) + 1
    return expected == found


def _without_trailing_reset(original: str, translated: str) -> str:
    """Drop a ``§r`` the model appended after the last character.

    Gemini 3.6–3.8 flash end most coloured lines with ``§r`` (measured 2026-10-01). A reset after
    the final character changes nothing on screen, so it is removed instead of costing the line
    its translation. A reset anywhere else would recolour the following words and is still refused.
    """
    stripped = translated.rstrip()
    trailing = translated[len(stripped):]
    # Only resets beyond those the original has; a moved original reset is a real token.
    while stripped.endswith("§r") and stripped.count("§r") > original.count("§r"):
        stripped = stripped[:-2].rstrip()
    return stripped + trailing if stripped else translated


def preserve_tokens(original: str, translated: str) -> str:
    if not isinstance(translated, str) or not translated:
        return original
    translated = _without_trailing_reset(original, translated)
    return translated if tokens_preserved(original, translated) else original
