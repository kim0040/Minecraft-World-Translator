# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate ワードマーク](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | [한국어](README.ko.md) | 日本語 | [简体中文](README.zh.md)

PomiTranslate は Java Edition のワールドに見える文章を翻訳する、無料のローカルツールです。マスコットは Pomi です。GitHub のリポジトリ名は `Minecraft-World-Translator` のままです。

CLI とパッケージされたデスクトップ入口は同じ翻訳器を使います。翻訳は検証済みバックアップのあとだけワールドを変更します。Scan Only はプロバイダを呼ばず、ワールドのバイトも変えません。セレクタ、リソース位置、数値、座標、書式プレースホルダはそのまま残します。

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

## 翻訳する文章

- 古い看板と、前面・背面のある看板
- 本のページ、タイトル、フィルタされたタイトル
- カスタム名、アイテム名、説明
- 直接のテキストコンポーネントと 1.20.5+ のアイテムコンポーネント
- `tellraw`、`title`、`subtitle`、`actionbar` の文章
- 有効にしたときのリソースパック zip 内 `lang/*.json`

![先にスキャン](../assets/illustrations/docs/doc_scan_first_v1.png)

## 形式

フィクスチャを通過した範囲だけをサポートします。gzip、zlib、無圧縮、Minecraft 1.20.5+ の LZ4 (`LZ4Block`)、圧縮バイトだけの外部 `.mcc`、標準リージョン、カスタムディメンション、`level.dat` がある Paper 型の隣接ワールドです。

Bedrock、Anvil 以前の `.mcr`、`.linear`、id 127 を含む不明な圧縮は検出して書き込みません。一覧は [support-matrix.md](support-matrix.md) です。macOS Intel、Windows x64、Linux x64 はサポート対象のプラットフォームとして載せていません。

![未対応の形式は停止](../assets/illustrations/docs/doc_unsupported_v1.png)

## プロバイダと保存

使うプロバイダは OpenAI、Gemini、Anthropic、OpenRouter、Custom です。Custom は指定した URL に OpenAI チャット形式か Anthropic メッセージ形式を送ります。古い Comet 設定も読めます。

本番の翻訳前に、そのプロバイダのテキストモデル一覧を取得し、公開された id と名前、コンテキスト長を使います。選んだモデルが一覧になければ、ワールドを書く前に止まります。

API キーは OS キーチェーンのサービス名 `PomiTranslate` に保存します。アカウント名は `openrouter` のようなプロバイダ id です。キーは `settings.json`、SQLite、ログ、git に書きません。

公開設定はアプリを更新してもインストール先の外に残ります。

- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate` または `~/.local/share/PomiTranslate/settings.json`

![選んだプロバイダへ文章が送られる](../assets/illustrations/docs/doc_api_notice_v1.png)

## 実行

確認したランタイムは Python 3.12 です。パッケージされたデスクトップ入口は、利用者に Python の導入を求めません。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python mc_world_translator.py --world-dir "/path/to/world" --dry-run --report-path ./scan-report.json
```

スキャンで得たフィンガープリントを `--expect-fingerprint` に渡すと、その後にワールドが変わった翻訳は拒否されます。`--restore-backup` は、その実行が変更したすべてのファイルを戻します。

![書く前にバックアップ](../assets/illustrations/docs/doc_backup_first_v1.png)

`python -m mwt.desktop_entry` は標準入出力の JSONL で動き、ローカルポートを開きません。署名資格がないリリースは未署名ドラフトで止まり、署名検証はオフにしません。

Python がある環境では `python webui_server.py` でローカル UI を `127.0.0.1:8765` に開けます。パッケージ版はこのサーバを必要としません。

設定例は [config.example.toml](../config.example.toml) です。API キーはファイルに書かないでください。

問い合わせ: `mini0227kim@gmail.com`。API キーは送らないでください。ライセンスは MIT です。
