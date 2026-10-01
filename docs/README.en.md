# PomiTranslate

**World Translator for Minecraft** — a desktop app that translates text in Minecraft Java Edition worlds

<img src="../assets/brand/wordmark/logo_wordmark_v1.png" alt="PomiTranslate" width="340" />

[한국어](../README.md) | English | [日本語](README.ja.md) | [简体中文](README.zh.md)

When an adventure map greets you with signs, books and item descriptions you cannot read, PomiTranslate turns that text into a language you know. Scan the world first to see what would be translated, review the candidates, then apply your own translations or send the rest to an AI provider you choose — with a verified backup taken before anything is written.

This is a free personal open-source project started by **Hyunmin Kim (김현민)**, a university student, for his own use. It is maintained with personal time and a limited budget, not as a commercial service or a paid support product. The mascot is Pomi.

> **In development:** the main flows have been exercised in an isolated development app on macOS Apple Silicon. Signed installers, clean-machine Windows/Linux validation and the final paid-translation workflow remain unfinished. [Current status](current-state.md) · [Follow-up work](follow-up-work.md)
>
> NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## How it works

PomiTranslate reads the folder you select directly; it does not copy the world into the app. Work proceeds in five steps, and the scan and review steps never change world files.

1. **Select a world** — open a Java Edition world folder (with level.dat) or a server root folder. The app shows the dimensions it found, the world's data format (DataVersion), an in-world resource pack and the number of stored backups. Bedrock worlds, legacy `.mcr`, `.linear` and worlds in use by a running game or server are blocked before anything starts.
2. **Scan** — find the text worth translating. This step calls no translation API and writes nothing. It summarizes unique strings, total occurrences, the estimated number of API requests and the text kinds it found, and reports unreadable chunks or unsupported formats as warnings while leaving the originals untouched.
3. **Review** — search, sort and filter candidates by kind or state. Exclude strings you do not want translated, or type your own translation for a string. A sentence used in several places is translated once and applied everywhere.
4. **Run** — check the target world, translation language, provider and model, the number of strings to send, the estimated request count and cost, and the safety backup, then start. World files stay untouched until every translation finishes successfully.
5. **Result and restore** — review changed files, translated/failed/kept strings, tokens used and reported cost. If you want to undo the run, restore any backup point from Backups; the state right before a restore is kept as a recovery snapshot.

## Screenshots

### Reviewing candidates

![Candidate search, kind filters and manual translation editing](images/review.png)

Search and filter by kind or state, exclude strings, or enter your own translation. You can also see where the same source text appears. Formatting codes such as `§` and placeholders such as `%s` or `{0}` are preserved so the game still renders them.

### Provider, model and reasoning

![Provider, model, reasoning mode and saved-key status](images/settings.png)

OpenRouter reasoning can follow the **model default**, be **turned off**, or use a **custom effort**. Model support lookup is separate from saving settings, and the save/discard bar stays pinned at the bottom.

<details>
<summary>Pre-run summary</summary>

![Reasoning, request count, estimated cost and external-transfer notice](images/run.png)

</details>

The screenshots were captured by running the current UI with **synthetic data**. The models, worlds and costs shown are illustrative; they are not evidence of actual usage or of support for a particular model. [Capture details](images/README.md)

## Features

### Scan and review

- Inspect candidates and coverage before anything is translated or written.
- Search, sort (world order, source text, frequency, kind), filter by kind or state, and include or exclude in bulk.
- See every occurrence of a string and enter manual translations. If you only apply manual translations, no translation API request is needed.
- Skip text already written in the target language to avoid paying for re-translation.

### Providers and models

- Configure OpenAI, Gemini, Anthropic, OpenRouter, Comet or a Custom endpoint (OpenAI/Anthropic-compatible wire formats). Available models depend on your provider and account.
- Look up model lists and, when pricing is known, the price per million tokens. OpenRouter's public catalog is fetched automatically, and this lookup does not save settings.
- Choose OpenRouter reasoning as model default, off, or a supported effort. Models that require reasoning cannot be turned off, and an unsupported effort cannot be saved.
- Set the target language and a style preset (neutral, casual, formal, polite, story or a custom system prompt), plus extra instructions. The style-brief helper is a separate AI request and may cost money.

### Safe writes and restore

- Changed files are stored in a verified backup before writing, and the state right before a restore is kept as a recovery snapshot.
- If the world changed after the scan, the fingerprint no longer matches and writing is refused. If the game or server is using the world, the session.lock conflict stops the write.
- Paths that point outside the selected world and symlinked resource packs are blocked before reading or sending anything to an API.
- Cancelling or failing keeps already translated strings, so a retry only asks for what is left. A provider outage leaves world files completely unchanged.
- Unreadable chunks are preserved as-is and reported in the result.

### Resource pack ZIPs

- Optionally translate language files in the in-world `resources.zip` and in up to 16 external ZIPs you select explicitly.
- External ZIPs are backed up before changes, and a restore requires selecting the same ZIP again in Settings. Folder-style packs are not supported yet.

### Keys and privacy

- Desktop credentials default to a **local encrypted SQLite vault plus a separate key file**. Session-only and OS-keychain modes are optional.
- Saved keys are never shown again in the UI and are not included in public settings JSON or world backups.
- The OS keychain is accessed only when you press the import button; the app does not read it automatically at startup.

### Desktop experience

- A Tauri 2 + Svelte 5 shell with a Python core; the desktop app opens no localhost server for its UI.
- Korean, English and Japanese UI, with system, light and dark themes. The View menu zooms the interface from 75% to 200%.
- Feels like a desktop app: unified macOS title bar, fixed sidebar and toolbar with only the content scrolling, menu shortcuts (`Cmd/Ctrl+O` open world, `Cmd+,` settings, `Cmd/Ctrl+F` find), drag a world folder onto the window, a list of worlds from your Minecraft saves folders (with icons), Dock/taskbar progress, and quit protection while a job runs.
- Command blocks: `tellraw`/`title` text is read in both JSON and Java 1.21.5+ SNBT form; only changed strings are rewritten in their original quoting, and unreadable commands are kept and reported.
- A CLI built on the same core. Keys saved in the desktop app and the CLI's keyring/environment variables are not shared automatically.

## Usage

1. Close Minecraft or the server and make an independent **copy of the world**.
2. In Settings, choose the provider, model and target language, and add any translation instructions. When using AI translation, enter and save your own API key.
3. In **Select world → Scan**, open the copy and read the coverage and warnings.
4. In **Review**, exclude strings and enter manual translations.
5. In **Run**, check the target, reasoning, external transfer and estimated cost, then start.
6. Review the **Result** and verify the text in game. To undo, restore from **Backups**.

Cost estimates can differ from the actual bill. Reasoning tokens, retries and model routing are not included in the estimate, so check your provider dashboard as well. The [user guide](user-guide.md) covers settings, restore and CLI usage in more detail.

### Running from source

Development builds are the current reference; there is no signed installer and not every OS has been validated. Running from source needs Python 3.12, Node.js 22.12 or newer, pnpm 12.6.0, a Rust toolchain and the [Tauri platform prerequisites](https://v2.tauri.app/start/prerequisites/).

```bash
git clone https://github.com/kim0040/PomiTranslate.git
cd PomiTranslate
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pyinstaller==6.16.0
pnpm install --frozen-lockfile
pnpm desktop:dev
```

The activation command above is for macOS/Linux. Windows commands, toolchain versions and packaging are in the [development guide](development.md); contribution steps are in [CONTRIBUTING.md](../CONTRIBUTING.md). The packaged design embeds a Python sidecar, but clean-machine installation has not been validated yet.

## Support scope

PomiTranslate handles signs, book pages and titles (including filtered titles), entity and block names, item names and lore, text displays, command text components and ZIP resource-pack language files. Verified compression formats are gzip, zlib, none, LZ4 and external `.mcc`. Support is based on **synthetic fixtures**: a passing row means that shape is read and written correctly, not that every text in every Minecraft version, mod or world will be found.

The scan covers the `region` and `entities` folders of each dimension, the in-world `resources.zip`, and external ZIPs selected explicitly on desktop. Data packs, scoreboards, command storage, `level.dat` text, player data and folder-style resource packs are outside the current scope. Bedrock, `.mcr`, `.linear` and unknown compression are never written. [Support matrix](support-matrix.md)

## Costs, data and disclaimer

The app itself has no purchase, subscription or in-app payment. **AI API usage may cost you money under your provider's terms.** The text you choose to translate and your translation instructions are sent to the API provider or relay service you select. Check each provider's retention, training and privacy policies.

Desktop credentials default to a **local encrypted SQLite vault plus a separate key file**; session-only and OS-keychain modes are optional. This does not protect against processes that can read both files under your user account. [Data and key handling](privacy.md)

The software is provided **AS IS**, without guarantees of translation accuracy, compatibility with every world, data preservation or uninterrupted use. To the extent permitted by applicable law, the author and contributors accept no liability for data loss, world corruption, API charges or other damage arising from use. See the [full disclaimer and rights notice](disclaimer.md) and the [MIT license text](../LICENSE).

Third-party rights in maps, resource packs and translations are separate from the software license. Do not redistribute translated content without the original creator's permission.

## Development and verification status

The main flows — world selection, scan, review, run, result and restore — have been exercised in a macOS Apple Silicon development app, and synthetic fixtures check reading and writing per format. On the latest source, the relevant frontend, browser, Rust and provider Python checks passed, and an unsigned debug app bundle was produced. A real OpenRouter key and model were registered and the public model lookup was verified, but **the actual paid translation end-to-end run has not been executed yet**.

Phase 2 is in progress and Phase 3 has not started. Signing, notarization and the updater, clean-machine Windows/Linux installation, macOS Intel and native validation of the OS-keychain opt-in remain. Exact check scopes and remaining gates are tracked in [Current status](current-state.md) and [Follow-up work](follow-up-work.md).

## Contributor and contact

- **김현민 / Hyunmin Kim** — creator and maintainer · [mini0227kim@gmail.com](mailto:mini0227kim@gmail.com)
- Bugs and suggestions: [GitHub Issues](https://github.com/kim0040/PomiTranslate/issues)
- Contributing: [CONTRIBUTING.md](../CONTRIBUTING.md)

When reporting a bug, include your OS, app version and reproduction steps. Do not post API keys, private worlds or logs containing secrets in a public issue. No response schedule, fix timeline or financial compensation is promised.

## License and documentation

The project source keeps its existing **[MIT License](../LICENSE)**. Dependencies keep their own licenses and are not relicensed by the project's MIT. No obvious conflict with keeping MIT was found in the reviewed scope, but per-artifact notices and full platform dependency verification must be completed before a final binary release. [Third-party notices](../THIRD_PARTY_NOTICES.md)

[Documentation index](README.md) · [Current status](current-state.md) · [Follow-up work](follow-up-work.md)
