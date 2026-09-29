"""Render the support matrix from fixture results. Unverified rows stay unsupported."""

from __future__ import annotations

VERIFIED_WHEN_PASSING = (
    "compression.gzip",
    "compression.zlib",
    "compression.none",
    "compression.lz4",
    "compression.external_mcc",
    "text.legacy_sign",
    "text.modern_sign",
    "text.legacy_book",
    "text.display_name_lore",
    "text.item_components",
    "text.direct_component",
    "text.commands",
    "text.resource_pack_lang",
    "layout.custom_dimension",
    "layout.paper_sibling",
    "safety.scan_only",
    "safety.backup_restore",
    "safety.multi_file_restore",
    "safety.plan_invalidation",
    "safety.malformed_chunk",
    "safety.world_write_lock",
    "safety.cancel_resume_backup",
)

ALWAYS_UNSUPPORTED = (
    "format.bedrock",
    "format.mcr",
    "format.linear",
    "compression.127",
    "compression.unknown",
    "platform.macos_intel",
    "platform.windows_x64",
    "platform.linux_x64",
)


def render_support_matrix(results: dict[str, bool]) -> str:
    lines = [
        "# PomiTranslate support matrix",
        "",
        "This file is generated from fixture results. A format is supported only when its fixture passed.",
        "Detected formats below are not writable.",
        "",
        "## Supported",
        "",
    ]
    for name in VERIFIED_WHEN_PASSING:
        if results.get(name) is True:
            lines.append(f"- {name}: supported")
        else:
            lines.append(f"- {name}: unsupported")
    lines.extend(["", "## Unsupported", ""])
    for name in ALWAYS_UNSUPPORTED:
        lines.append(f"- {name}: unsupported")
    lines.append("")
    return "\n".join(lines)
