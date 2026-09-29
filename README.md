# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate wordmark](assets/brand/wordmark/logo_wordmark_v1.png)

English | [한국어](docs/README.ko.md) | [日本語](docs/README.ja.md) | [简体中文](docs/README.zh.md)

PomiTranslate is a free, open-source local utility designed to safely extract and localize player-visible text in Minecraft Java Edition worlds. The project mascot is Pomi, and the repository identifier remains `Minecraft-World-Translator`.

Both the CLI and the native Tauri desktop application share the same high-performance Python core via a lightweight packaged JSONL sidecar process. To ensure maximum safety, world files are only modified after automated backup verification succeeds. Scan Only mode performs full candidate extraction without making external API calls or modifying world data. Command selectors, resource location namespaces, coordinates, numbers, and formatting placeholders are strictly preserved.

![Pomi](assets/mascot/base/mascot_base_front_v1_512.png)

## What it translates

- Signs (both legacy single-sided lines and modern front/back texts)
- Books (pages, titles, and filtered titles)
- Custom names for entities, blocks, and containers
- Item display names and lore
- Raw JSON text components and modern 1.20.5+ item components
- Command feedback text (`tellraw`, `title`, `subtitle`, `actionbar`)
- Embedded resource pack language files (`resources.zip` -> `lang/*.json`), when enabled

![Scan first](assets/illustrations/docs/doc_scan_first_en_v1.png)

## Format Compatibility

Only region and compression formats thoroughly verified by automated regression fixtures are officially supported:

- **Region Compression**: Gzip, Zlib, uncompressed, and Minecraft 1.20.5+ LZ4 (`LZ4Block`)
- **External Chunks**: `c.<x>.<z>.mcc` chunk overflow files (compressed payload bytes)
- **Directory Layouts**: Standard dimensions, custom dimensions, and Paper-style sibling world directories containing `level.dat`

### Detected Unsupported Formats (Read-Only Safety)

To prevent data corruption, writing is automatically disabled when the following formats are detected:

- Bedrock Edition worlds
- Pre-Anvil legacy `.mcr` region files
- Third-party `.linear` compressed region formats
- Unknown or corrupted compression types (including compression ID 127)

See [docs/support-matrix.md](docs/support-matrix.md) for the complete format test matrix.

![Unsupported formats stop](assets/illustrations/docs/doc_unsupported_en_v1.png)

## Supported AI Providers

PomiTranslate officially supports OpenAI, Google Gemini, Anthropic, OpenRouter, and Custom (compatible endpoints). The Custom provider communicates using either the OpenAI Chat format or the Anthropic Messages format based on your specified Base URL. Legacy configuration profiles remain fully backward-compatible.

Prior to starting translation, PomiTranslate queries the provider's active model catalog to verify model IDs, display names, and context limits. If the selected model cannot be found in the catalog, execution safely halts before modifying any world files.

## Secret Management & Settings

API keys are encrypted and stored directly within your operating system keychain (macOS Keychain, Windows Credential Manager, or Linux Secret Service) under the service name `PomiTranslate`, identified by the provider name (e.g. `openrouter`). API keys are never stored in plain text, `settings.json`, SQLite files, log files, or git commits.

User configurations persist across application updates outside the installation directory:

- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate/settings.json` or `~/.local/share/PomiTranslate/settings.json`

Stored API keys can be deleted individually from the keychain at any time via the Settings screen.

![Text is sent to the provider you choose](assets/illustrations/docs/doc_api_notice_en_v1.png)

## Quick Start (CLI)

Python 3.12 is the recommended runtime for CLI usage. End users running the packaged desktop application do not need Python or development toolchains installed.

```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 1. Scan World (Scan Only)
Extract translatable candidates and inspect occurrence counts without API charges or world changes:

```bash
python mc_world_translator.py --world-dir "/path/to/world" --dry-run --report-path ./scan-report.json
```

### 2. Translate World
Execute translation using the verified scan report. Passing the scan fingerprint ensures that any unexpected modifications to the world between scan and run are safely rejected:

```bash
python mc_world_translator.py \
  --world-dir "/path/to/world" \
  --provider openrouter \
  --model "your-text-model" \
  --expect-fingerprint "<fingerprint from scan report>"
```

Omitting `--api-key` automatically retrieves the stored key from your OS keychain for that provider.

### 3. Restore from Backup
Easily restore your world to its verified pre-translation state:

```bash
python mc_world_translator.py --world-dir "/path/to/world" --restore-backup
```

Every write run automatically creates a versioned backup set. Restoration rolls back all modified files (including `entities` and enabled `resources.zip`), while preserving the current state as a safety recovery snapshot. Translation runs also abort immediately if Java Edition's `session.lock` is held by an active Minecraft client or server.

![Back up before writing](assets/illustrations/docs/doc_backup_first_en_v1.png)

## Desktop Application

Built with Tauri 2 and Svelte 5, the native desktop application provides a modern, intuitive interface equipped with built-in safety features:

- **Multilingual UI**: Seamlessly toggle between English, Korean, and Japanese display languages (independent of the target translation language).
- **Recent Worlds**: Conveniently track and reopen recent worlds with game DataVersion metadata.
- **Safety Pre-Checks**: Structural validation to detect read-only formats and active session locks before processing.
- **Candidate Review**: Filter, search, and sort translation candidates by frequency or category, with support for exclusions and custom manual translations.
- **Cost & Request Estimation**: Real-time lower-bound estimates for API request counts and token usage prior to execution.
- **Cooperative Cancellation & Resume**: Pause translation safely without losing progress. Checkpoints cache completed translations and resume remaining texts automatically.
- **Versioned Backups & Safe Restore**: Inspect backup history and roll back changes with automatic pre-restore safety snapshots.

Build from source:

```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```

Packaged installers include all native runtime binaries, so end users do not need Node.js, Python, or Rust installed.

## Local Web UI (Legacy Utility)

If you already have Python available, the lightweight web server `webui_server.py` is available at `http://127.0.0.1:8765`:

```bash
python webui_server.py
```

## Configuration File

Refer to [config.example.toml](config.example.toml) for available options. Keep `world_dir` empty until pointing to your target world, and do not put API keys in plain-text configuration files.

## Automated Testing

```bash
.venv/bin/python test_core.py
.venv/bin/python tests/test_release_fixtures.py
.venv/bin/python tests/test_providers.py
.venv/bin/python tests/test_brand_secrets.py
.venv/bin/python tests/test_desktop_entry.py
```

## Inquiries & Feedback

- Bugs and feature requests: `mini0227kim@gmail.com`
- Please include your operating system, provider, model ID, and relevant error logs. Do not share your API keys.

## License

PomiTranslate is licensed under the [MIT License](LICENSE).
