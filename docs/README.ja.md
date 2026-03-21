# Minecraft World Translator

[English](../README.md) | [한국어](./README.ko.md) | 日本語 | [简体中文](./README.zh.md)

Minecraft World Translator は、デスクトップ環境で手軽に Minecraft のワールドを翻訳できるツールです。ワールドのリージョン（region）ファイル（`.mca`）の内部データをスキャンするだけでなく、zip アーカイブ形式のリソースパック内の言語ファイルまで翻訳することが可能です。

本プロジェクトは、初心者の使いやすさを最優先に設計されています：

- ブラウザベースのローカル UI を通じて簡単に操作できます。
- お好みに応じて CLI（コマンドライン）からも実行できます。
- 既存の `translate.py` 設定をそのまま維持・適用できます。
- アプリのコードを書き換えることなく、複数の LLM プロバイダ間を自在に切り替えて利用できます。

ご質問やエラー報告は、以下の連絡先へお送りください：
`mini0227kim@gmail.com`

## 翻訳可能対象

- 看板のテキスト
- 本の内容
- 本のタイトル および `filtered_title`
- カスタム名（名札等の表示名）
- アイテム名および説明文（Lore）
- `tellraw`, `title`, `subtitle`, `actionbar` 内のテキスト
- リソースパック内の `lang/*.json` ファイル（オプション対応）

## 主な機能

- 日本語、英語、韓国語にローカライズされた Web UI
- ライト / ダークテーマの切り替え
- 「まずはスキャンから」を推奨する初心者向けの手軽なワークフロー
- 翻訳実行前のファイル数、予想トークン数、予想所要時間の提示機能（Estimation）
- 複数 LLM プロバイダへの切り替え対応：
  - `comet`
  - `openai`
  - `gemini`
  - `anthropic`
  - `openrouter`
  - OpenAI および Anthropic との互換性を持つ Custom API プロバイダへ完全対応
- 手動でのモデル設定と、各プロバイダのモデルカタログの取得機能
- スタイルプリセットや、AI アシストによる短い「スタイルメモ」の詳細プロンプト拡張機能
- 無料 API 利用者が対象外リクエストを弾くための RPM / TPM 制限設定オプション
- `translate.py` を経由した API キー、Base URL、モデル、レガシープロンプトの設定引き継ぎ
- 前もって翻訳対象を確認できるドライラン（Dry-run）スキャンモード
- ファイルを安全に書き換えるための実行前バックアップ機能
- 実行終了後の JSON 形式レポート生成

## プロジェクト構成

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

## システム要件

- Python 3.11 以上のバージョン
- LLM API を呼び出すためのインターネット接続環境
- 選択したプロバイダとして機能する有効な API キー
- バックアップファイルの保存に十分なディスク空き容量

## 最短の始め方

初心者の方に最もおすすめする手順は次の通りです：

1. Web UI を起動します。
2. ワールドフォルダのパスと API の設定を入力します。
3. まずは `スキャンのみ（Scan Only）` ボタンをクリックし、動作を確認します。
4. トークン数やテキストの量を見て問題がなければ、本翻訳を実行します。

### Web UI の一発起動 (macOS)

macOS では、以下のファイルをダブルクリックするだけで UI が起動します：

- [run_web_ui.command](./run_web_ui.command)

このランチャーは以下を自動で行います：

- `.venv` の自動生成 (未作成時)
- 必要な依存関係フレームワークのインストール
- すでに起動している Web UI があればブラウザで再利用して表示
- もしポート `8765` が使用中であれば、利用可能な別のポートを自動選定
- ローカル Web サーバーの開始
- デフォルトブラウザの自動起動

## OS 別インストールと実行

ツールを起動する前に、利用する API キーをローカルの `.env` ファイルに準備しておくことができます：

```bash
cp .env.example .env
```

その後、必要なキーだけ記入してください。`.env` 上のパスワードやシークレットキーは、Git にアップロードされない仕様になっています。

### Windows

1. [python.org](https://www.python.org/downloads/windows/) から Python 3.11 以降をインストールします。
2. プロジェクトのフォルダを開き、PowerShell を起動します。
3. 次のコマンドを実行します：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

もし PowerShell がスクリプトの実行をブロックしてしまう場合は、以下のコマンドで制限を一時解除してください：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

1. ターミナル等で `python3` が問題なくインストールされているか確認します。
2. プロジェクトのフォルダでターミナルを開きます。
3. 次のコマンドを実行します：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

または、前述したスクリプトを利用することも可能です：

- [run_web_ui.command](./run_web_ui.command)

もし macOS 側がランチャーの実行をセキュリティの都合でブロックする場合は、右クリックメニューから「開く（Open）」を選んでください。デフォルトポートである `8765` が塞がっている場合は自動的に使用可能なポートに切り替わります。

### Linux

1. Python 3.11 以降がインストールされているか確認します。
2. フォルダ上でターミナルを起動します。
3. 次のコマンドを実行します：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

ディストリビューションによってはインストールコマンドが追加で必要になる場合があります：

```bash
sudo apt install python3-venv
```

## Web UI の起動と使用

ローカル UI サーバーを手動で起動する場合：

```bash
python3 webui_server.py
```

指定のアドレスへブラウザからアクセスします：

- `http://127.0.0.1:8765`

自動でブラウザを開くよう指定する場合：

- `python3 webui_server.py --open-browser`

ホストやポート番号を変更する場合：

- `python3 webui_server.py --host 0.0.0.0 --port 9000`

### Web UI の画面に表示されるもの

- LLM プロバイダの選択欄
- Base URL およびモデル設定オプション
- 全モデル一覧（カタログ）を取得・反映するボタン
- スタイル関連の短いメモから長文プロンプトを AI に作らせる機能
- ターゲット・スコープなどを絞るグループ化された詳細設定
- リソースパックの zip 参照や除外機能
- 全ファイルのリアルタイム進捗状況
- 現在読み込み・書き込み・通信中のファイル
- UI 内で行われている一連の動作の視覚表現
- 送信済みのバッチ単位数
- 結果を羅列した Result JSON パネルのプレビュー
- お問い合わせ情報・エラー報告先のリンク

## コマンドライン（CLI）からの実行

### テスト実行（スキャンのみのドライラン）

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

### 実際の書き換え（翻訳開始）

```bash
python3 mc_world_translator.py --config config.example.toml
```

### プロバイダとモデルの強制指定

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --provider openrouter \
  --model openai/gpt-4.1
```

### 利用可能なモデルカタログ一覧を取得

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

プロバイダ環境変数を指定しつつリストアップする応用例：

```bash
python3 mc_world_translator.py --provider openai --api-key "$OPENAI_API_KEY" --list-models
python3 mc_world_translator.py --provider gemini --api-key "$GEMINI_API_KEY" --list-models
python3 mc_world_translator.py --provider anthropic --api-key "$ANTHROPIC_API_KEY" --list-models
python3 mc_world_translator.py --provider openrouter --api-key "$OPENROUTER_API_KEY" --list-models
```

### 短いスタイルメモの詳細指示化

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "中世ホラーマップ風、固有名詞は音訳、ヒントは明確に"
```

## 構成設定（Configuration）

利用する設定ファイル例：

- [config.example.toml](./config.example.toml)

### 全体の（トップレベル）設定項目

- `world_dir`
  - 翻訳の対象とする Minecraft ワールドフォルダ
- `report_path`
  - 出力される JSON レポートのパス
- `dry_run`
  - 原本に書き込みを行わないスキャン用ドライラン
- `backup`
  - ファイルを上書きする前にバックアップを作成するか
- `backup_suffix`
  - バックアップ複製ファイルにつける拡張子
- `batch_size`
  - 1 回の API 通信で投げる文字列ブロックの数
- `temperature`
  - 生成モデルに設定する Temperature（温度）パラメータ
- `inherit_translate_py`
  - 古い `translate.py` の定数値設定を使い回すか
- `translate_py_path`
  - レガシー（旧）設定となる対象スクリプトのパス指定

### API セクション

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

- `rpm_limit`: 1分あたりの最大リクエスト回数 (Requests Per Minute) を制限します。無料枠の API 制限に引っかからないようにリクエストを自動で遅延させます。`0` は無制限を意味します。
- `tpm_limit`: 1分あたりの最大トークン使用量 (Tokens Per Minute) を制限します。予想トークン量をあらかじめ計算し自動待機を行うことで超過アクセスを防ぎます。`0` は無制限を意味します。

#### プロバイダ指定可能な値

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`
- `custom_openai` (UI での Custom API 用 / OpenAI プロトコル互換)
- `custom_anthropic` (UI での Custom API 用 / Anthropic プロトコル互換)

#### API キーの探索優先順位について

1. config 内で `api_key` に設定されている値
2. プロバイダ対応の環境変数
3. オプションがオンなら `translate.py` 内の変数

サポートされる主要環境変数：

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

これらはシェルから `export` しなくても、フォルダ上に `.env` を作って保存することが可能です。

### プロンプトセクション

```toml
[prompt]
target_language = "日本語"
style_preset = "neutral"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - 指定したい対象言語の名前ラベル
- `style_preset`
  - 翻訳のベースとなるスタイルテンプレートのプリセット
- `style_prompt`
  - プリセットの上に後から追加される独自ルールやトーン設定など
- `custom_system_prompt`
  - 他のプリセット等を完全に無視して設定される、強力なシステムプロンプト全体指定

### スキャン範囲の設定

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

この各スイッチによって、どこからどこまでを AI API に翻訳させるか細かく制御できます。

### リソースパックの設定について

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "ja_jp.json"
skip_if_target_exists = false
```

ZIP アーカイブとして同梱されているリソースパック内部の `lang` フォルダにある言語 JSON テーブルを翻訳したい場合のみ、オンにしてください。

#### リソースパック翻訳の具体的な使い方：
1. リソースパックがフォルダのままになっている場合は、まず `.zip` 形式に圧縮してください。
2. Web UI の指定欄に、この `.zip` ファイルの絶対パスを入力します。
3. リソースパックが基準としている元の言語ファイル名（例：`en_us.json`）を指定します。
4. 生成したいターゲット言語のファイル名（例：`ja_jp.json`）を指定します。
5. 翻訳を実行すると、テクスチャ等の画像ファイルを壊すことなく、ZIP 内の `assets/*/lang/` ディレクトリに翻訳済みの新しい JSON ファイルが安全に注入・保存されます。

## 初心者向け推奨ワークフロー

Minecraft ワールドの仕様に詳しくない場合、以下の運用手順を参考にしてください：

1. Web UI をブラウザで立ち上げる。
2. 使用しているプロバイダ、紐づく API キー、最適なモデルを入力する。
3. ローカルに置かれたワールドファイルの場所を入力する。
4. キャラクターの個性や激しい口調（文体）が必要なければ、スタイルプリセットは一旦 `neutral （ノーマル）` のままにする。
5. 重要なファイルのバックアップオプションを絶対にオンにする。
6. `スキャンのみ実行（Dry Run）` をまず押す。
7. スキャンが完了したら結果ビューアを開いて、想定した通りテキストが抽出されているか確認する。
8. 問題が全くなさそうなら、実行ボタン（翻訳本番）に切り替えて進める。

## 技術的仕様についてのメモ

- `.mca` ブロック領域やチャンクの構造を Python バインディングを使用して NBT ノードを再帰パースしています。
- `/kill @p` 的な純粋なゲーム機能用コマンドに見える文字列はヒューリスティクスによって除外可能です。
- リソースパックの変換プロセスにおいては、指定された zip レイヤー内の `lang/*.json` ルールのみを対象に働きます。
- LLM ベンダーごとに行われるフォーマットと API 制約の違いの分離・吸収は [llm_backends.py](./llm_backends.py) によって独自に実行されます。
- Web UI 自体はクラウドアプリではなく、ローカルサーバー経由であるためデータが外部に漏れることは（使用するプロバイダへの送信を除き）ありません。

## 安全な利用のために

- 本番環境で実行する前はバックアップ設定をオンにし続けるか、ワールドのコピーを用意してから着手してください。
- バックアップが破損するトラブルを防ぐためにも、必ず一度ドライラン（スキャン）で様子を見ることをおすすめします。
- 詳細設定から、過激な世界観のスタイルプロンプトを与えすぎると、本来ギミックで使われるヒントやキーアイテムの名前構造が破壊される危険性を伴います。
- **コードに関する注意点：** 本プロジェクトはバージョン1に向けて急速に開発されたため、一部のモジュール内にテスト用のレガシーコードや、現在は使われていない実験的なロジックの痕跡が残っている場合があります。

## トラブルシューティング（問題解決）

### `API key is missing` と出る場合

キーが意図した通り下記のどこかに指定されているか再点検してください：

- Web UI の対象フィールド
- `config.example.toml` ファイル
- マシンの環境変数リストまたは `.env` ファイル
- `translate.py` (下位互換利用の場合)

### `Model is missing` と出る場合

モデル未設定のままでは動作しません。直接文字列で打ち込むか `--list-models` を叩いて存在を確認してください。

### Web UI がうまくブラウザで開かない

- サーバーが `Python` 上で正常に起動し待機しているかログから確認してください。
- `http://127.0.0.1:8765` のアドレスに間違いがないかチェックしてください。
- 稀に別のタスクやソフトウェアが `8765` ポートを埋めてしまっている場合があります。別のポートでお試しください。

### 翻訳出力の結果が乱暴・クセが強い

次の対策を組み合わせてお試しください：

- プリセットの度合いを `neutral（ふつう）` か `polite（丁寧）` に落としてみる。
- システムの自動 AI メモ拡張機能を使う場合、トーンや雰囲気をもう少し慎重に指定してみる。
- 完全な統制が欲しい場合は、`custom_system_prompt` にてシステムから全部上塗りする。

### Windows スクリプトで起動トラブルが起こる

もしアクティベーション段階で止まったなら、PowerShell を使って一時的に許可をおろしてください：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## サポート・問い合わせ

質問、バグ報告、セットアップでのトラブルサポート等の相談窓口：

- `mini0227kim@gmail.com`

報告していただける際は、エラー解消速度向上のために以下の情報を併せてお送りください：

- 利用しているシステム OS 情報
- エラーが起きたプロバイダやモデルの名前
- CLI なのか Web UI なのか、どのようなアクションで再現したか
- ターミナル等に表示された赤文字のエラーやログ、エラーメッセージ（あれば必ず）

## ライセンス情報の明記

本プロジェクトのソースコードや成果物は MIT ライセンスの条件に基づき公開されています。

詳細は以下のドキュメントをお読みください：

- [LICENSE](./LICENSE)
