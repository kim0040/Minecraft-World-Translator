# Minecraft World Translator

English | [한국어](./docs/README.ko.md) | [日本語](./docs/README.ja.md) | [简体中文](./docs/README.zh.md)

Minecraft World Translator is a desktop-friendly translation tool designed for Minecraft worlds. It scans and translates text within world region files (`.mca`), and it can also translate resource pack language files located inside zip archives.

This project is built with beginners in mind:

- You can run the entire process through an easy-to-use, browser-based local UI.
- If you prefer the terminal, a robust CLI is also available.
- You can retain and apply your existing `translate.py` configurations.
- You can switch seamlessly between multiple LLM providers without modifying the application code.

If you have questions, feedback, or encounter errors, please contact:
`mini0227kim@gmail.com`

## What It Can Translate

- Sign text
- Book pages
- Book titles and `filtered_title`
- Custom entity and item names
- Item lore
- Text inside `tellraw`, `title`, `subtitle`, and `actionbar` commands
- Optional resource pack `lang/*.json` files

## Main Features

- Local web UI localized in English, Korean, and Japanese
- Light and dark themes
- Beginner-friendly workflow emphasizing a "scan-first" approach
- Pre-translation Scale and Time Estimators
- Support for multiple LLM providers:
  - `comet`
  - `openai`
  - `gemini`
  - `anthropic`
  - `openrouter`
  - Custom API endpoints fully compatible with OpenAI and Anthropic formats
- Manual model entry and intelligent model catalog lookup
- Prompt style presets and AI-assisted expansion for short style notes
- Rate Limit settings (RPM/TPM) for free-tier APIs
- `translate.py` inheritance for API key, base URL, model, and legacy prompts
- Dry-run scan mode to preview changes safely
- Automatic backup creation before applying modifications
- Detailed JSON report output after each execution

## Project Files

```text
minecraft-world-translator/
├── LICENSE
├── README.md
├── docs/
│   ├── README.ko.md
│   ├── README.ja.md
│   └── README.zh.md
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
- A valid API key for your chosen provider
- Sufficient disk space for creating backup files

## Quick Start

The easiest path for beginners:

1. Open the Web UI.
2. Fill in your world path and API settings.
3. Run `Scan Only` first to preview the extraction process.
4. If the results look correct, run the real translation.

### Fastest Web UI Start (macOS)

On macOS, you can simply double-click the launcher:

- [run_web_ui.command](./run_web_ui.command)

This launcher automates several steps:

- Creates a `.venv` virtual environment if it is missing
- Installs necessary dependencies
- Reuses an already-running local UI if one is found
- Automatically selects the next open port if `8765` is busy
- Starts the local web server
- Opens your default browser automatically

## Installation

Before running the tool, you can prepare a local `.env` file to securely store your credentials:

```bash
cp .env.example .env
```

Fill in only the keys you need. Your `.env` file is ignored by Git, ensuring your secrets remain safe.

### Windows

1. Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/windows/).
2. Open PowerShell in the project folder.
3. Run the following commands:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks script activation, you can temporarily bypass the execution policy:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

1. Ensure `python3` is installed.
2. Open Terminal in the project folder.
3. Run the following commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Alternatively, you can use the launcher:

- [run_web_ui.command](./run_web_ui.command)

If macOS security blocks the launcher, right-click the file and select `Open`. The launcher will automatically find an available port if the default port (`8765`) is occupied.

### Linux

1. Ensure Python 3.11+ is installed.
2. Open a terminal in the project folder.
3. Run the following commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On some distributions, you may need to install the virtual environment package first:

```bash
sudo apt install python3-venv
```

## Running the Web UI

To start the local UI server manually:

```bash
python3 webui_server.py
```

Then, open your browser and navigate to:

- `http://127.0.0.1:8765`

To open the browser automatically upon launch:

```bash
python3 webui_server.py --open-browser
```

To change the host address and port number:

```bash
python3 webui_server.py --host 0.0.0.0 --port 9000
```

When using the one-click launcher, if the default port is busy, the script will either reconnect to the existing UI or seamlessly transition to the next available port.

### What the Web UI Shows

- Provider selection menu
- Base URL and model configuration settings
- Interactive model catalog lookup
- AI-assisted expansion for short style notes
- Grouped translation scope controls
- Resource pack configuration
- Live progress indicators
- Active file status
- Current operational activity
- Translated batch counts
- Result JSON preview
- Contact information for support

## Running the CLI

### Dry Run

Preview changes without modifying any files:

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

### Real Translation

Apply changes to your world:

```bash
python3 mc_world_translator.py --config config.example.toml
```

### Override Provider and Model

Run with specific provider and model settings:

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --provider openrouter \
  --model openai/gpt-4.1
```

### List Available Models

View all models available for your selected provider:

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

You can also specify the provider directly in the command:

```bash
python3 mc_world_translator.py --provider openai --api-key "$OPENAI_API_KEY" --list-models
python3 mc_world_translator.py --provider gemini --api-key "$GEMINI_API_KEY" --list-models
python3 mc_world_translator.py --provider anthropic --api-key "$ANTHROPIC_API_KEY" --list-models
python3 mc_world_translator.py --provider openrouter --api-key "$OPENROUTER_API_KEY" --list-models
```

### Expand a Short Style Note

Let the AI build a comprehensive prompt from a brief description:

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "medieval horror tone, transliterate names, keep puzzle hints explicit"
```

## Configuration

Example configuration file:

- [config.example.toml](./config.example.toml)

### Top-Level Settings

- `world_dir`
  - The path to the target Minecraft world folder.
- `report_path`
  - The destination path for the JSON output report.
- `dry_run`
  - Enables scan-only mode without writing files.
- `backup`
  - Creates backup files before writing modifications.
- `backup_suffix`
  - The file extension suffix used for backup duplicates.
- `batch_size`
  - The number of strings bundled per API request.
- `temperature`
  - The sampling temperature for the language model.
- `inherit_translate_py`
  - Reuses values from an existing `translate.py` file.
- `translate_py_path`
  - The path to the legacy configuration script.

### API Section

```toml
[api]
provider = "comet"
api_key = ""
base_url = "https://api.cometapi.com/v1"
model = ""
request_timeout = 120
rpm_limit = 0
tpm_limit = 0
```

- `rpm_limit`: Limits the Requests Per Minute. If the rate limit is reached, the translator will automatically delay the next API call to protect your free-tier limits. Set to `0` for unlimited.
- `tpm_limit`: Limits the Tokens Per Minute. Protects your quota by dynamically delaying requests based on token estimations. Set to `0` for unlimited.

#### Provider Values

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`
- `custom_openai` (UI support for OpenAPI compatible endpoints)
- `custom_anthropic` (UI support for Anthropic compatible endpoints)

#### API Key Resolution Order

1. The value defined in the TOML configuration file.
2. Provider-specific environment variables.
3. Inherited values from `translate.py` (if enabled).

Supported environment variables:

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

Instead of exporting these variables in the shell, you can conveniently store them in a local `.env` file.

### Prompt Section

```toml
[prompt]
target_language = "Korean"
style_preset = "neutral"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - The human-readable name of the target translation language.
- `style_preset`
  - Selects the base translation style template.
- `style_prompt`
  - Additional custom instructions appended after the preset.
- `custom_system_prompt`
  - Completely overrides the default system prompt and preset.

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

Use this section to precisely define which text segments should be translated.

### Resource Pack Section

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "ko_kr.json"
skip_if_target_exists = false
```

Enable this section only if you want to translate the language JSON files located inside a resource pack archive.

#### How to use Resource Pack Translation:
1. Compress your resource pack folder into a `.zip` file if it isn't already one.
2. Enter the absolute path to this `.zip` archive in the UI.
3. Define the source language filename the pack currently uses (e.g., `en_us.json`).
4. Define the target language filename you want to generate (e.g., `ko_kr.json` or `ja_jp.json`).
5. Run the translation. The app will automatically translate the text and safely inject the new JSON files back into your `.zip` archive under the correct `assets/*/lang/` directories without altering your textures.

## Beginner Workflow Recommendation

If you are unfamiliar with Minecraft's internal file structures, simply follow this workflow:

1. Launch the Web UI.
2. Select your provider, enter your API key, and specify the model.
3. Set the path to your world directory.
4. Leave the style preset on `neutral` unless you require a specific thematic tone.
5. Always keep the backup option enabled.
6. Run `Scan Only` first.
7. Review the extracted text and the progress logs panel.
8. If the scan results are accurate, proceed to run the real translation.

## Technical Notes

- The translation process works by scanning NBT data structures inside `.mca` region files.
- The tool precisely replaces only recognized user-facing text fields.
- Command-like strings (such as `/kill @p`) can be identified and intentionally skipped.
- Resource pack translation targets `lang/*.json` files inside zip archives.
- Provider-specific request formats are managed independently in [llm_backends.py](./llm_backends.py).
- The web UI functions as a local server, ensuring your data remains private and is not uploaded to a third-party cloud app.

## Safety Guidelines

- Always ensure the backup setting is active before your first full run.
- When working with important maps, execute tests on a copy of your world folder.
- Perform a dry run before applying significant real translations.
- Unusually aggressive or strict style prompts can inadvertently corrupt item names, conceal puzzle clues, or break tone consistency.
- **Note on Codebase:** Because this project evolved quickly to Version 1, you may encounter traces of legacy code, unused experimental logic, or leftover test constants in some modules.

## Troubleshooting

### `API key is missing` Error

Ensure your API key is correctly defined in one of the following locations:

- The Web UI input field
- The `config.example.toml` file
- Your system's environment variables
- The `translate.py` file (if inheriting configurations)

### `Model is missing` Error

Ensure you have provided a valid model identifier. You can enter it manually or use the `--list-models` command to view the supported catalog.

### Web UI Fails to Open

- Verify the server is running without errors in your console.
- Ensure you navigate to `http://127.0.0.1:8765`.
- Check if another application or script is currently occupying port `8765`.

### Translation Output is Too Aggressive or Inaccurate

Try these adjustments:

- Switch your preset to `neutral` or `formal`.
- If using the AI-assisted expansion, provide more specific and cautious directions.
- For total control, utilize the `custom_system_prompt` to override the AI's boundaries.

### Windows Script Activation Issues

If your scripts refuse to execute on Windows, run PowerShell with bypassed policies:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Support

For usage questions, bug reports, ideas, or feedback:

- `mini0227kim@gmail.com`

When submitting a report, please include the following to help expedite a resolution:

- Your operating system framework
- Your selected API provider
- The specific model name you are running
- Whether the issue occurred via the CLI or the Web UI
- The exact error messages or terminal logs (if applicable)

## License

This project is licensed under the MIT License.

For detailed conditions, see:

- [LICENSE](./LICENSE)
