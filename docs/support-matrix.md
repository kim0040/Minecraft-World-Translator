# PomiTranslate support matrix

This file is generated from fixture results. A format is supported only when its fixture passed.
Detected formats below are not writable.

Fixtures use small synthetic worlds. A passing row means that shape is read and written correctly.
It does not mean every player-visible text in a real world is found.

## Scope

Scanned: `region` and `entities` folders of each dimension, and `resources.zip` inside the world when enabled.
Not scanned: data packs, `data/*.dat` (command storage, scoreboard), `level.dat` and player data.

## Supported

- compression.gzip: supported
- compression.zlib: supported
- compression.none: supported
- compression.lz4: supported
- compression.external_mcc: supported
- text.legacy_sign: supported
- text.modern_sign: supported
- text.legacy_book: supported
- text.display_name_lore: supported
- text.item_components: supported
- text.direct_component: supported
- text.commands: supported
- text.resource_pack_lang: supported
- layout.custom_dimension: supported
- layout.paper_sibling: supported
- safety.scan_only: supported
- safety.backup_restore: supported
- safety.multi_file_restore: supported
- safety.plan_invalidation: supported
- safety.malformed_chunk: supported
- safety.world_write_lock: supported
- safety.cancel_resume_backup: supported

## Unsupported

- format.bedrock: unsupported
- format.mcr: unsupported
- format.linear: unsupported
- compression.127: unsupported
- compression.unknown: unsupported
- platform.macos_intel: unsupported
- platform.windows_x64: unsupported
- platform.linux_x64: unsupported
