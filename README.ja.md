# Minecraft World Translator

[English](./README.md) | [한국어](./README.ko.md) | 日本語

Minecraft World Translator は、Minecraft ワールドとリソースパック内のテキストを翻訳するためのローカルツールです。初心者は Web UI から、慣れている人は CLI から使えます。

問い合わせ・エラー報告:

- `mini0227kim@gmail.com`

## このツールでできること

- ワールド `.mca` 内テキストの抽出
- 看板、本、アイテム名、Lore、title 系テキストの翻訳
- 必要に応じてリソースパック `lang/*.json` の翻訳
- 複数 LLM プロバイダの切り替え
- 利用可能モデル一覧の取得
- 短いスタイルメモから詳細な翻訳指示の生成

## 対応プロバイダ

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`

## 最短の使い方

初心者には次の流れを推奨します。

1. Web UI を起動
2. プロバイダ、API キー、モデルを入力
3. ワールドフォルダを設定
4. `スキャンのみ実行`
5. 結果を確認
6. 問題なければ `本翻訳を実行`

## OS 別セットアップ

実行前に `.env` ファイルを作っても構いません。

```bash
cp .env.example .env
```

必要なキーだけ記入してください。`.env` は Git に含まれない設定です。

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

PowerShell がブロックする場合:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

ワンタッチ起動:

- [run_web_ui.command](./run_web_ui.command)

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

必要なら:

```bash
sudo apt install python3-venv
```

## Web UI の起動

```bash
python3 webui_server.py
```

接続先:

- `http://127.0.0.1:8765`

ブラウザ自動起動:

```bash
python3 webui_server.py --open-browser
```

## CLI の使い方

ドライラン:

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

本翻訳:

```bash
python3 mc_world_translator.py --config config.example.toml
```

モデル一覧取得:

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

短いスタイルメモを補強:

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "中世ホラーマップ風、固有名詞は音訳、ヒントは明確に"
```

## 設定ファイル

例:

- [config.example.toml](./config.example.toml)

主な項目:

- `world_dir`: 対象ワールドフォルダ
- `report_path`: レポート保存先
- `dry_run`: 書き込みなしスキャン
- `backup`: バックアップ作成
- `batch_size`: 1 回の API 送信量
- `[api].provider`: プロバイダ選択
- `[api].model`: モデル名
- `[prompt].target_language`: 対象言語
- `[prompt].style_preset`: スタイルプリセット

環境変数:

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

これらはシェル環境変数でも、ローカル `.env` ファイルでも設定できます。

## 初心者向けメモ

- 最初は `neutral` が最も安全です。
- まず `Scan Only` を使ってください。
- バックアップは有効のままにしてください。
- 大事なマップはコピー上で先に試してください。

## 技術的な説明

- `.mca` 内の NBT データを読み、ユーザー表示向けテキストを探します。
- 生コマンドのような文字列は翻訳対象から除外できます。
- リソースパックは zip 内の `lang/*.json` を処理します。
- プロバイダごとの API フォーマットは [llm_backends.py](./llm_backends.py) で分離しています。

## トラブルシューティング

`API key is missing`

- Web UI、設定ファイル、環境変数、`translate.py` のいずれかにキーが必要です。

`Model is missing`

- モデル名を直接入力するか `--list-models` を使ってください。

Web UI が開かない

- サーバーが動いているか確認
- ポート競合を確認
- `http://127.0.0.1:8765` を直接開く

## ライセンス

MIT License を適用しています。

- [LICENSE](./LICENSE)
