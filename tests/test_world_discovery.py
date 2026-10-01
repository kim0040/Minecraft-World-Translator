"""The world list reads launcher saves folders without writing or leaving them."""

from __future__ import annotations

import gzip
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from mwt.discovery import discover_worlds, saves_dirs  # noqa: E402
from test_extraction import _name, root, w_compound, w_int, w_string  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16


def w_long(name: str, value: int) -> bytes:
    return bytes([4]) + _name(name) + struct.pack(">q", value)


def make_world(saves: Path, folder: str, *, name: str, played: int, icon: bytes | None = PNG) -> Path:
    world = saves / folder
    (world / "region").mkdir(parents=True)
    level = root(
        w_compound(
            "Data",
            w_string("LevelName", name),
            w_long("LastPlayed", played),
            w_int("DataVersion", 4556),
            w_compound("Version", w_string("Name", "1.21.11")),
        )
    )
    (world / "level.dat").write_bytes(gzip.compress(level))
    if icon is not None:
        (world / "icon.png").write_bytes(icon)
    return world


def main() -> None:
    with tempfile.TemporaryDirectory() as raw:
        home = Path(raw)
        official = home / "Library" / "Application Support" / "minecraft" / "saves"
        prism = home / "Library" / "Application Support" / "PrismLauncher" / "instances" / "Pack" / "minecraft" / "saves"
        older = make_world(official, "Old Save", name="Old adventure", played=1_000_000)
        newer = make_world(prism, "Roguefire", name="Roguefire §6Map", played=2_000_000, icon=b"not a png")
        (official / "not-a-world").mkdir()
        (official / "loose.txt").write_text("x")
        outside = make_world(home / "elsewhere", "Escaped", name="Escaped", played=3_000_000)
        (official / "link").symlink_to(outside, target_is_directory=True)
        before = {path: path.read_bytes() for path in home.rglob("*") if path.is_file()}

        dirs = saves_dirs(home, platform="darwin", env={})
        assert dirs == [official, prism], dirs
        assert saves_dirs(home, platform="linux", env={}) == []
        result = discover_worlds(dirs)
        names = [item["name"] for item in result["worlds"]]
        assert names == ["Roguefire §6Map", "Old adventure"], names  # newest first, the symlink skipped
        first, second = result["worlds"]
        assert first["path"] == str(newer) and first["icon"] is None, "a file that is not a PNG is not an icon"
        assert second["path"] == str(older) and second["icon"].startswith("data:image/png;base64,")
        assert second["dataVersion"] == 4556 and second["versionName"] == "1.21.11"
        assert (first["lastPlayed"], second["lastPlayed"]) == (2_000, 1_000), "seconds, like the recent-world list"
        after = {path: path.read_bytes() for path in home.rglob("*") if path.is_file()}
        assert after == before, "discovery must not write anything"
    print("WORLD_DISCOVERY_PASSED")


if __name__ == "__main__":
    main()
