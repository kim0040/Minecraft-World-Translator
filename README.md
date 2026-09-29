# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate wordmark](assets/brand/wordmark/logo_wordmark_v1.png)

English | [한국어](docs/README.ko.md) | [日本語](docs/README.ja.md) | [简体中文](docs/README.zh.md)

PomiTranslate is a free, open-source local application designed to safely extract, manage, and translate player-visible text in Minecraft Java Edition worlds. The project mascot is Pomi, and the repository identifier remains `Minecraft-World-Translator`.

Whether exploring foreign adventure maps, custom RPG realms, escape puzzles, or multi-dimensional server worlds, PomiTranslate enables players and map creators to localize in-game narratives into their native language without risking world data corruption. Both the command-line interface and the native desktop application share the exact same high-performance Python translation core through a packaged JSONL sidecar process that opens no external network listener ports.

![Pomi](assets/mascot/base/mascot_base_front_v1_512.png)

---

## Design Principles and Safety Guarantees

Minecraft world files store intricate data structures in Named Binary Tag (NBT) format across thousands of region chunks. Traditional regex replacements or crude NBT encoders frequently strip unknown tags, corrupt coordinate headers, and break custom command blocks. PomiTranslate operates on strict safety principles:

- **Byte-for-Byte NBT Preservation**: Unmodified chunks remain completely byte-identical down to the SHA-256 hash. When a text string is localized, only the modified Java UTF-8 payload is surgically updated in-place without re-serializing or corrupting neighboring tags.
- **Strict Format Protection**: Color and formatting codes (`§a`, `§l`, `§r`), newline escapes (`\n`), string formatting placeholders (`%s`, `{0}`), JSON component syntax, and command block arguments are protected by validation engines. If an LLM response alters formatting syntax, the original text is preserved and safely reported.
- **Scan-First Architecture**: Scan Only mode extracts all translatable strings across dimensions, deduplicates candidates, and generates a structured scan plan without sending any data to external APIs or altering world files.
- **Active Session Lock Detection**: PomiTranslate checks for Java Edition's `session.lock` file before every write operation. If the world is currently loaded in a running Minecraft client or server, all writes are blocked immediately.
- **Versioned Atomic Backups**: Before a single byte is changed, a verified multi-file backup set is created in the operating system application data folder. If a translation is interrupted or an API provider experiences an outage, nothing is partially written, and full pre-translation restoration is always one click away.

![Scan first](assets/illustrations/docs/doc_scan_first_en_v1.png)

---

## Supported In-Game Text Components

PomiTranslate traverses all dimensions (Overworld, Nether `DIM-1`, The End `DIM1`, and custom datapack dimensions) to extract player-facing strings:

| Component Type | In-Game Element | Extraction & Handling Details |
| :--- | :--- | :--- |
| **Signs** | Standing, hanging, and wall signs | Extracts legacy single-sided sign text (versions 1.8 through 1.19) as well as modern dual-sided front and back messages (version 1.20+). |
| **Books** | Book & Quill and Written Books | Translates titles, filtered titles, author metadata, and individual book pages containing plain text or structured JSON components. |
| **Item Metadata** | Weapons, tools, armor, and custom items | Extracts custom display names, lore lines, item components introduced in 1.20.5+ (`minecraft:custom_name`, `minecraft:lore`), and recursive hover/click event text. |
| **Containers** | Chests, barrels, shulker boxes, furnaces | Reads custom container names and recursively scans all nested inventory items across container slots. |
| **Entities & Blocks** | Mobs, NPCs, armor stands, custom blocks | Extracts custom names (`CustomName`) on living entities, armor stands, and named block entities. |
| **Display Entities** | Modern text displays (`text_display`) | Full support for 1.19.4+ text display entity components and billboard elements. |
| **Command Blocks** | Impulse, repeating, and chain command blocks | Surgically parses and extracts messages inside `/tellraw`, `/title`, `/subtitle`, and `/actionbar` commands, including deeply nested `execute ... run` subcommands, while keeping commands, selector targets (`@a`, `@p`), and coordinates completely untouched. |
| **Resource Packs** | In-world `resources.zip` | When enabled, scans and translates embedded client language files (`assets/<namespace>/lang/*.json` or `.lang`) and bundles them in the same backup set. |

---

## Region and Format Compatibility

PomiTranslate only writes to region formats verified by automated regression test fixtures:

### Supported Storage Formats
- **Region File Standard**: Minecraft Java Edition Anvil format (`.mca`) across all dimensions and entity storage folders (`entities/*.mca`).
- **Chunk Compression Formats**: Gzip, Zlib, Uncompressed raw bytes, and Minecraft 1.20.5+ LZ4 (`LZ4Block`).
- **Chunk Overflow Files**: External `.mcc` files (`c.<x>.<z>.mcc`) containing compressed overflow chunk data.
- **Directory Layouts**: Standard Vanilla singleplayer worlds, custom dimension directories, and Paper/Spigot multi-world sibling folder layouts sharing a root `level.dat`.

### Detected Unsupported Formats (Automatic Write-Lock)
To prevent irreversible world damage, writing is permanently disabled when any of the following formats are detected:
- **Bedrock Edition**: Worlds using Bedrock level structures or Mojang LevelDB (`.ldb`) storage.
- **Pre-Anvil Legacy Formats**: Pre-1.2 `.mcr` region files.
- **Third-Party Compression**: Third-party `.linear` Zstandard-compressed region files.
- **Corrupted / Unknown Algorithms**: Unknown compression algorithm headers (including compression type 127).

See [docs/support-matrix.md](docs/support-matrix.md) for the automated test matrix generated directly from fixture verification.

![Unsupported formats stop](assets/illustrations/docs/doc_unsupported_en_v1.png)

---

## Supported AI Providers and Secret Management

PomiTranslate officially supports the following AI providers:
- **OpenAI**: GPT-4o, GPT-4o-mini, and compatible chat models.
- **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus.
- **Google Gemini**: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 2.0 Flash.
- **OpenRouter**: Comprehensive access to hundreds of open-source and commercial language models.
- **Custom (Self-Hosted / Compatible)**: Connect to local or private inference engines such as Ollama, vLLM, LM Studio, or custom reverse proxies using standard OpenAI Chat or Anthropic Messages wire formats.

Before any translation run begins, PomiTranslate queries the provider's active model catalog to verify model existence and context parameters. If the requested model is unavailable, execution safely halts before changing any world files.

### Operating System Keychain Security
API keys are never stored in plain text, `settings.json`, SQLite databases, application logs, or git commits. Keys are encrypted and managed directly by your operating system's native credential store:
- **macOS**: Apple Keychain Services (`PomiTranslate`)
- **Windows**: Windows Credential Manager (`PomiTranslate`)
- **Linux**: Freedesktop Secret Service API via DBus

Keys are passed to the isolated translation engine exclusively through process standard input (stdin) during active translation batches. Stored keys can be inspected or deleted individually at any time in the Settings view.

Application configurations are stored safely outside the installation directory:
- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate/settings.json` (or `~/.local/share/PomiTranslate/settings.json`)

![Text is sent to the provider you choose](assets/illustrations/docs/doc_api_notice_en_v1.png)

---

## The 3-Phase Translation Workflow

```
[Phase 1: Scan Only]
World Files (.mca) ──> Extract Candidates ──> Deduplicate ──> Scan Plan & Fingerprint
(Zero API requests, read-only inspection, candidate search and manual exclusion)

[Phase 2: Batched Translation]
Unique Strings ──> Throttle & Circuit Breaker ──> AI Provider ──> Validated Checkpoint
(Preserves formatting codes, retries transient network errors, protects against outages)

[Phase 3: Atomic Write]
Verified Backup ──> Check session.lock ──> Write Patched Chunks ──> Complete
(Byte-accurate NBT surgical update, instant pre-restore recovery snapshots available)
```

---

## Quick Start (CLI)

Python 3.12 is the standard runtime for command-line execution. (End users running the packaged desktop application do not need Python or development tools installed.)

```bash
# Clone the repository
git clone https://github.com/kim0040/Minecraft-World-Translator.git
cd Minecraft-World-Translator

# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 1. Scan Only (Inspect translatable strings without API calls)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --dry-run \
  --report-path ./scan-report.json
```

### 2. Translate World (Using verified scan plan)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --target-language "ko" \
  --provider openrouter \
  --model "anthropic/claude-3.5-sonnet" \
  --style story \
  --expect-fingerprint "<fingerprint-from-scan-report>"
```
*Note: If `--api-key` is omitted, PomiTranslate automatically retrieves your securely stored API key from the OS keychain.*

### 3. Restore World from Backup
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --restore-backup
```

![Back up before writing](assets/illustrations/docs/doc_backup_first_en_v1.png)

---

## Native Desktop Application

Built with Tauri 2 and Svelte 5, the PomiTranslate desktop app provides a responsive, accessible interface:

- **Multilingual Interface**: Instantly switch the user interface between English, Korean, and Japanese independently of the target translation language.
- **Candidate Review Table**: Search, filter, inspect occurrence locations (coordinates, block/entity ID, dimension), exclude specific texts, or input manual translations.
- **Cost & Request Estimator**: Computes lower-bound request counts and token usage prior to sending API requests.
- **Cooperative Cancellation & Resumption**: Cancel runs safely without corrupting world files; resumed jobs pick up uncompleted batches from disk checkpoints.
- **Backup Explorer**: View all versioned backups with timestamps, modified file counts, and one-click rollback.

### Building Desktop App from Source
```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```
Packaged binaries embed the Python sidecar and native dependencies; no external toolchains are required on client machines.

---

## Translation Style Presets

PomiTranslate offers six tailored localization styles:
- **Neutral (`neutral`)**: Balanced, accurate translation suitable for general worlds and survival builds.
- **Casual (`casual`)**: Natural, lively conversational style ideal for adventure maps, dialogues, and multiplayer minigames.
- **Formal (`formal`)**: Dignified, structured tone tailored for historical settings, monuments, chronicles, and announcements.
- **Polite (`polite`)**: Gentle, polite honorific style designed for tutorial guides, quest prompts, and instructional maps.
- **Story (`story`)**: Rich, immersive fantasy literature prose designed to capture atmospheric narrative tension without obscuring quest objectives.
- **Custom (`custom`)**: Apply your own custom prompt instructions tailored to specialized modpacks or fictional universes.

---

## Automated Test Suites

```bash
# Run core regression suite
.venv/bin/python test_core.py

# Run release format fixtures (compression, NBT, dimensions, session lock)
.venv/bin/python tests/test_release_fixtures.py

# Run provider API tests and keychain settings
.venv/bin/python tests/test_providers.py

# Run brand compliance and secret leakage tests
.venv/bin/python tests/test_brand_secrets.py

# Run desktop JSONL sidecar protocol tests
.venv/bin/python tests/test_desktop_entry.py

# Run frontend unit tests
./node_modules/.bin/vitest run
```

---

## Feedback and Inquiries

- Issues and inquiries: `mini0227kim@gmail.com`
- When submitting feedback, please provide your operating system, provider, model ID, and relevant log messages. Never include your private API keys.

---

## License

PomiTranslate is licensed under the [MIT License](LICENSE).
