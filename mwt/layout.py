"""World layout detection. Unsupported editions and containers are not written."""

from __future__ import annotations

from pathlib import Path

STANDARD_REGION_DIRS = (
    "region",
    "entities",
    "DIM-1/region",
    "DIM-1/entities",
    "DIM1/region",
    "DIM1/entities",
)


def _is_relative_inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def discover_region_dirs(world_dir: Path) -> list[str]:
    root = world_dir.resolve()
    found: list[str] = []

    def add(relative: str) -> None:
        directory = root / relative
        if directory.is_dir() and relative not in found and _is_relative_inside(root, directory):
            found.append(relative)

    for relative in STANDARD_REGION_DIRS:
        add(relative)

    dimensions = root / "dimensions"
    if dimensions.is_dir():
        for namespace in sorted(path for path in dimensions.iterdir() if path.is_dir()):
            for dimension in sorted(path for path in namespace.iterdir() if path.is_dir()):
                for kind in ("region", "entities"):
                    add(f"dimensions/{namespace.name}/{dimension.name}/{kind}")

    for child in sorted(path for path in root.iterdir() if path.is_dir()):
        if child.name.startswith(".") or not (child / "level.dat").is_file():
            continue
        for relative in STANDARD_REGION_DIRS:
            add(f"{child.name}/{relative}")
        nested = child / "dimensions"
        if nested.is_dir():
            for namespace in sorted(path for path in nested.iterdir() if path.is_dir()):
                for dimension in sorted(path for path in namespace.iterdir() if path.is_dir()):
                    for kind in ("region", "entities"):
                        add(f"{child.name}/dimensions/{namespace.name}/{dimension.name}/{kind}")
    return found


def detect_write_blockers(world_dir: Path, *, recursive: bool = True) -> list[str]:
    root = world_dir.resolve()
    reasons: list[str] = []
    database = root / "db"
    if database.is_dir() and ((database / "CURRENT").is_file() or any(database.glob("MANIFEST*"))):
        reasons.append("bedrock")
    level = root / "level.dat"
    if level.is_file():
        header = level.read_bytes()[:2]
        if header != b"\x1f\x8b" and database.is_dir():
            if "bedrock" not in reasons:
                reasons.append("bedrock")
    if not recursive:
        return reasons
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.startswith(".pomi-") for part in path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix == ".mcr" and "mcr" not in reasons:
            reasons.append("mcr")
        elif suffix == ".linear" and "linear" not in reasons:
            reasons.append("linear")
    return reasons
