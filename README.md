# Minecraft World Translator

English | [한국어](./README.ko.md) | [日本語](./README.ja.md)

Minecraft World Translator is a desktop-friendly translation tool for Minecraft worlds. It scans world region files (`.mca`) and can also translate resource-pack language files inside zip archives.

The project is designed for beginners first:

- You can run it from a browser-based local UI.
- You can still use a CLI if you prefer.
- You can keep your existing `translate.py` settings.
- You can switch between multiple LLM providers without rewriting the app.

If you have questions or run into errors, contact: `mini0227kim@gmail.com`

## What It Can Translate

- Sign text
- Book pages
- Book titles and `filtered_title`
- Custom names
- Item names and lore
- Text inside `tellraw`, `title`, `subtitle`, and `actionbar`
- Optional resource-pack `lang/*.json` files

## Main Features

- Local web UI with English, Korean, and Japanese
- Light and dark themes
- Beginner-friendly workflow with scan-first operation
- Support for multiple providers:
  - `comet`
  - `openai`
  - `gemini`
  - `anthropic`
  - `openrouter`
- Manual model entry
- Model catalog lookup from the selected provider
- Prompt style presets:
  - `neutral`
  - `casual`
  - `formal`
  - `polite`
  - `story`
- AI-assisted style prompt expansion from a short note
- `translate.py` inheritance for API key, base URL, model, and legacy prompt
- Dry-run scan mode
- Backup support before writing changes
- JSON report output after each run

## Project Files

```text
minecraft-world-translator/
├── LICENSE
├── README.md
├── README.ko.md
├── README.ja.md
├── config.example.toml
├── llm_backends.py
├── mc_world_translator.py
├── requirements.txt
├── run_web_ui.command
├── webui_server.py
└── webui/
    ├── app.js
    ├── index.html
    └── styles.css
```

## System Requirements

- Python 3.11 or newer
- Internet access for LLM API calls
- A valid API key for the provider you want to use
- Enough disk space for backup files

## Quick Start

If you want the easiest path:

1. Open the web UI.
2. Fill in your world path and API settings.
3. Run `Scan Only` first.
4. If the result looks good, run the real translation.

### Fastest Web UI Start

On macOS, you can double-click:

- [run_web_ui.command](./run_web_ui.command)

That launcher will:

- create `.venv` if missing
- install dependencies if needed
- reuse an already-running local UI if one is found
- choose the next open port automatically if `8765` is busy
- start the local web server
- open your browser automatically

## Installation

Before running the tool, you can prepare a local `.env` file:

```bash
cp .env.example .env
```

Then fill in only the keys you need. `.env` is ignored by Git.

### Windows

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/).
2. Open PowerShell in the project folder.
3. Run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can temporarily allow local scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

1. Make sure `python3` is available.
2. Open Terminal in the project folder.
3. Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Or use:

- [run_web_ui.command](./run_web_ui.command)

If macOS blocks the launcher, right-click it and choose `Open` once.
If port `8765` is already being used, the launcher will try the next available port automatically.

### Linux

1. Make sure Python 3.11+ is installed.
2. Open a terminal in the project folder.
3. Run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On some distributions you may need:

```bash
sudo apt install python3-venv
```

## Running the Web UI

Start the local UI server:

```bash
python3 webui_server.py
```

Open:

- `http://127.0.0.1:8765`

Open the browser automatically:

```bash
python3 webui_server.py --open-browser
```

Change host and port:

```bash
python3 webui_server.py --host 0.0.0.0 --port 9000
```

If the default port is busy when using the one-click launcher, it will either reconnect to the existing UI or move to the next available port.

### What the Web UI Shows

- provider selection
- base URL and model settings
- model lookup button
- short style note + AI expansion
- grouped translation scope controls
- resource-pack settings
- live progress
- current file
- current activity
- translated batch count
- result JSON
- support contact email

## Running the CLI

### Dry Run

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

### Real Translation

```bash
python3 mc_world_translator.py --config config.example.toml
```

### Override Provider and Model

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --provider openrouter \
  --model openai/gpt-4.1
```

### List Available Models

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

Examples with direct provider selection:

```bash
python3 mc_world_translator.py --provider openai --api-key "$OPENAI_API_KEY" --list-models
python3 mc_world_translator.py --provider gemini --api-key "$GEMINI_API_KEY" --list-models
python3 mc_world_translator.py --provider anthropic --api-key "$ANTHROPIC_API_KEY" --list-models
python3 mc_world_translator.py --provider openrouter --api-key "$OPENROUTER_API_KEY" --list-models
```

### Expand a Short Style Note

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "medieval horror tone, transliterate names, keep puzzle hints explicit"
```

## Configuration

Example file:

- [config.example.toml](./config.example.toml)

### Top-Level Settings

- `world_dir`
  - Path to the target Minecraft world
- `report_path`
  - Output path for the JSON report
- `dry_run`
  - Scan only, do not write files
- `backup`
  - Create backup files before writing
- `backup_suffix`
  - Suffix used for backup copies
- `batch_size`
  - Number of strings per API request batch
- `temperature`
  - Sampling temperature
- `inherit_translate_py`
  - Reuse values from `translate.py`
- `translate_py_path`
  - Path to the legacy config file

### API Section

```toml
[api]
provider = "comet"
api_key = ""
base_url = "https://api.cometapi.com/v1"
model = ""
request_timeout = 120
```

#### Provider Values

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`

#### API Key Resolution Order

1. config value
2. provider-specific environment variable
3. inherited value from `translate.py`

Supported environment variables:

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

You can also store them in a local `.env` file instead of exporting them in the shell.

### Prompt Section

```toml
[prompt]
target_language = "한국어"
style_preset = "neutral"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - Human-readable target language label
- `style_preset`
  - Base translation style
- `style_prompt`
  - Additional instructions appended after the preset
- `custom_system_prompt`
  - Full override for the system prompt

### Scan Section

```toml
[scan]
translate_signs = true
translate_books = true
translate_custom_names = true
translate_item_names = true
translate_lore = true
translate_titles = true
translate_filtered_titles = true
translate_command_output = true
skip_command_like_text = true
component_translate_key_prefixes = []
```

Use this section to choose exactly what gets translated.

### Resource Pack Section

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "ko_kr.json"
skip_if_target_exists = false
```

Use this only if you also want to translate language files in a resource pack archive.

## Beginner Workflow Recommendation

If you are not comfortable with Minecraft world internals:

1. Start the web UI.
2. Set your provider, API key, and model.
3. Set the world path.
4. Keep the style preset on `neutral` unless you want a stronger tone.
5. Run `Scan Only`.
6. Review the result and the progress panel.
7. Keep backups enabled.
8. Run the real translation only after the scan looks correct.

## Technical Notes

- World translation works by scanning NBT data inside `.mca` region files.
- The tool rewrites only recognized user-facing text fields.
- Command-like strings such as `/kill @p` can be skipped intentionally.
- Resource-pack translation works on `lang/*.json` files inside zip archives.
- Provider-specific request formats are handled in [llm_backends.py](./llm_backends.py).
- The web UI is a local server, not a hosted cloud app.

## Safety Notes

- Always keep backups enabled for your first real run.
- Test on a copy of the world if the map is important.
- Run a dry run before doing a real translation.
- Strong style prompts can damage item names, puzzle clues, or tone consistency.

## Troubleshooting

### `API key is missing`

Set the correct key in:

- the web UI
- `config.example.toml`
- your environment variable
- or `translate.py`

### `Model is missing`

Enter a model manually or use `--list-models`.

### Web UI does not open

- Make sure the server is running
- open `http://127.0.0.1:8765`
- check whether another app is already using the port

### Translation looks too aggressive

Try:

- `neutral`
- `formal`
- a smaller custom style prompt

### Windows script activation issues

Use PowerShell with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Support

For questions, bug reports, or setup help:

- `mini0227kim@gmail.com`

Please include:

- your operating system
- your provider
- your model name
- what command or UI action you used
- the error message, if you have one

## License

This project is licensed under the MIT License.

See:

- [LICENSE](./LICENSE)
