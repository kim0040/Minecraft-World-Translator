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


def preserve_tokens(original: str, translated: str) -> str:
    if not isinstance(translated, str) or not translated:
        return original
    return translated if tokens_preserved(original, translated) else original
