"""Byte-preserving NBT reader for Java Edition chunk data.

The ``nbt`` package this replaces could not read Java's modified UTF-8 (a supplementary
character such as an emoji is stored as two 3-byte surrogates, and NUL as ``C0 80``), and it
rebuilt every chunk from a parsed tree, so any detail it modelled differently changed the bytes.

This reader keeps the original bytes. It builds a tree of only the tags translation cares about
(compounds, lists and strings) and remembers where each string sits in the source. ``dump``
rewrites just the strings that were edited. Everything else, including numbers, arrays and tag
order, is copied verbatim, so an unedited chunk round-trips to identical bytes by construction.

Scalars are dropped below the first few levels to keep the scan fast. Those levels hold what a
location needs (``DataVersion``, a block entity's ``x y z``, an entity's ``Pos``).
"""

from __future__ import annotations

import struct

TAG_END = 0
TAG_COMPOUND_ID = 10
_FIXED_SIZE = {1: 1, 2: 2, 3: 4, 4: 8, 5: 4, 6: 8}
_MAX_DEPTH = 128
_SHALLOW = 3  # compounds at this depth or above keep their numbers

_U16 = struct.Struct(">H")
_I32 = struct.Struct(">i")
_SCALAR_FORMAT = {1: ">b", 2: ">h", 3: ">i", 4: ">q", 5: ">f", 6: ">d"}


class NbtError(ValueError):
    pass


def mutf8_decode(data: bytes) -> str:
    """Decode Java modified UTF-8. Raises UnicodeDecodeError for a lone surrogate."""
    if b"\xc0\x80" in data:
        data = data.replace(b"\xc0\x80", b"\x00")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        pass
    # Surrogate pairs written as two 3-byte sequences. Re-encoding as UTF-16 joins the pairs.
    text = data.decode("utf-8", "surrogatepass")
    return text.encode("utf-16-le", "surrogatepass").decode("utf-16-le")


def mutf8_encode(text: str) -> bytes:
    if text.isascii() and "\x00" not in text:
        return text.encode("ascii")
    out = bytearray()
    for char in text:
        code = ord(char)
        if code == 0:
            out += b"\xc0\x80"
        elif code < 0x80:
            out.append(code)
        elif code < 0x800:
            out += bytes((0xC0 | code >> 6, 0x80 | code & 0x3F))
        elif code < 0x10000:
            out += bytes((0xE0 | code >> 12, 0x80 | code >> 6 & 0x3F, 0x80 | code & 0x3F))
        else:
            code -= 0x10000
            for surrogate in (0xD800 | code >> 10, 0xDC00 | code & 0x3FF):
                out += bytes((0xE0 | surrogate >> 12, 0x80 | surrogate >> 6 & 0x3F, 0x80 | surrogate & 0x3F))
    return bytes(out)


class TAG_Number:
    """A kept top-level scalar. Read-only."""

    __slots__ = ("type_id", "value")

    def __init__(self, type_id: int, value: int | float) -> None:
        self.type_id = type_id
        self.value = value


class TAG_String:
    __slots__ = ("_source", "_start", "_end", "_value", "_edited", "undecodable")

    def __init__(self, source: bytes, start: int, end: int) -> None:
        self._source = source
        self._start = start
        self._end = end
        self._value: str | None = None  # decoded on first use; most strings are never read
        self._edited = False
        self.undecodable = False

    @property
    def value(self) -> str:
        if self._value is None:
            try:
                self._value = mutf8_decode(self._source[self._start : self._end])
            except UnicodeDecodeError:
                # Never expose bytes we cannot represent: an empty value is never a candidate.
                self._value = ""
                self.undecodable = True
        return self._value

    @value.setter
    def value(self, new: str) -> None:
        if self.value == new:
            return
        if self.undecodable:
            raise NbtError("A string that is not valid modified UTF-8 cannot be edited")
        self._value = new
        self._edited = True

    @property
    def edited(self) -> bool:
        return self._edited


class TAG_Compound(dict):
    """Maps tag name to a compound, list, string or (top level only) number."""

    def __init__(self, source: bytes = b"", name: str = "") -> None:
        super().__init__()
        self.name = name
        self._source = source

    def dump(self) -> bytes:
        return _rebuild(self._source, self)


class TAG_List(list):
    def __init__(self, element_type: int = 0) -> None:
        super().__init__()
        self.element_type = element_type


def _strings(node, out: list[TAG_String]) -> None:
    if isinstance(node, TAG_String):
        out.append(node)
    elif isinstance(node, dict):
        for child in node.values():
            _strings(child, out)
    elif isinstance(node, list):
        for child in node:
            _strings(child, out)


def _rebuild(source: bytes, root: TAG_Compound) -> bytes:
    edited: list[TAG_String] = []
    stack: list = [root]
    while stack:
        node = stack.pop()
        if isinstance(node, TAG_String):
            if node._edited:
                edited.append(node)
        elif isinstance(node, dict):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    if not edited:
        return source
    edited.sort(key=lambda tag: tag._start)
    parts: list[bytes] = []
    cursor = 0
    for tag in edited:
        payload = mutf8_encode(tag._value or "")
        if len(payload) > 0xFFFF:
            raise NbtError("A translated string is longer than NBT allows")
        # The two bytes before the payload are its length.
        parts.append(source[cursor : tag._start - 2])
        parts.append(_U16.pack(len(payload)))
        parts.append(payload)
        cursor = tag._end
    parts.append(source[cursor:])
    return b"".join(parts)


def parse(data: bytes, *, keep_scalars: str = "top") -> TAG_Compound:
    """Read a chunk or ``level.dat`` payload. ``keep_scalars`` is ``"top"`` or ``"all"``."""
    try:
        return _parse(data, keep_scalars)
    except (struct.error, IndexError, RecursionError) as exc:
        raise NbtError(f"Truncated or malformed NBT: {exc}") from exc


def _parse(data: bytes, keep_scalars: str) -> TAG_Compound:
    if len(data) < 3 or data[0] != TAG_COMPOUND_ID:
        raise NbtError("NBT root is not a compound")
    keep_all = keep_scalars == "all"
    names: dict[bytes, str] = {}
    size = len(data)

    def name_at(pos: int) -> tuple[str, int]:
        (length,) = _U16.unpack_from(data, pos)
        raw = data[pos + 2 : pos + 2 + length]
        if len(raw) != length:
            raise NbtError("Truncated tag name")
        cached = names.get(raw)
        if cached is None:
            try:
                cached = mutf8_decode(raw)
            except UnicodeDecodeError:
                cached = raw.decode("utf-8", "replace")
            names[raw] = cached
        return cached, pos + 2 + length

    def read_string(pos: int) -> tuple[TAG_String, int]:
        (length,) = _U16.unpack_from(data, pos)
        end = pos + 2 + length
        if end > size:
            raise NbtError("Truncated string")
        return TAG_String(data, pos + 2, end), end

    def skip_array(pos: int, element_size: int) -> int:
        (count,) = _I32.unpack_from(data, pos)
        if count < 0:
            raise NbtError("Negative array length")
        end = pos + 4 + count * element_size
        if end > size:
            raise NbtError("Truncated array")
        return end

    def read_list(pos: int, depth: int) -> tuple[TAG_List, int]:
        element_type = data[pos]
        (count,) = _I32.unpack_from(data, pos + 1)
        pos += 5
        if count < 0:
            raise NbtError("Negative list length")
        result = TAG_List(element_type)
        if count == 0 or element_type == TAG_END:
            return result, pos
        if element_type in _FIXED_SIZE:
            if keep_all or (depth <= _SHALLOW and count == 3 and element_type in (5, 6)):
                fmt = _SCALAR_FORMAT[element_type]
                step = _FIXED_SIZE[element_type]
                for _ in range(count):
                    (value,) = struct.unpack_from(fmt, data, pos)
                    result.append(TAG_Number(element_type, value))
                    pos += step
            else:
                pos += count * _FIXED_SIZE[element_type]
        elif element_type == 8:
            for _ in range(count):
                tag, pos = read_string(pos)
                result.append(tag)
        elif element_type == 9:
            for _ in range(count):
                item, pos = read_list(pos, depth + 1)
                result.append(item)
        elif element_type == 10:
            for _ in range(count):
                item, pos = read_compound(pos, depth + 1, False)
                result.append(item)
        elif element_type in (7, 11, 12):
            width = {7: 1, 11: 4, 12: 8}[element_type]
            for _ in range(count):
                pos = skip_array(pos, width)
        else:
            raise NbtError(f"Unknown list element type {element_type}")
        if pos > size:
            raise NbtError("Truncated list")
        return result, pos

    def read_compound(pos: int, depth: int, top: bool = False) -> tuple[TAG_Compound, int]:
        if depth > _MAX_DEPTH:
            raise NbtError("NBT is nested too deeply")
        node = TAG_Compound(data)
        keep = keep_all or depth <= _SHALLOW
        while True:
            if pos >= size:
                raise NbtError("Compound was not closed")
            tag_type = data[pos]
            pos += 1
            if tag_type == TAG_END:
                return node, pos
            if tag_type in _FIXED_SIZE:
                if keep:
                    name, pos = name_at(pos)
                    fmt = _SCALAR_FORMAT[tag_type]
                    (value,) = struct.unpack_from(fmt, data, pos)
                    node[name] = TAG_Number(tag_type, value)
                else:
                    (length,) = _U16.unpack_from(data, pos)
                    pos += 2 + length
                pos += _FIXED_SIZE[tag_type]
                continue
            name, pos = name_at(pos)
            if tag_type == 8:
                node[name], pos = read_string(pos)
            elif tag_type == 10:
                node[name], pos = read_compound(pos, depth + 1, False)
            elif tag_type == 9:
                node[name], pos = read_list(pos, depth + 1)
            elif tag_type in (7, 11, 12):
                pos = skip_array(pos, {7: 1, 11: 4, 12: 8}[tag_type])
            else:
                raise NbtError(f"Unknown tag type {tag_type}")

    root_name, pos = name_at(1)
    root, end = read_compound(pos, 0, True)
    root.name = root_name
    if end > size:
        raise NbtError("Truncated NBT")
    return root
