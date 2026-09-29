# PomiTranslate

World Translator for Minecraft（マインクラフト ワールド翻訳ツール）

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.
（本ソフトウェアはMojangまたはMicrosoftによる公式マインクラフト製品ではなく、承認および関連もありません。）

ワールドを翻訳する前に、必ずバックアップを作成してください。PomiTranslateは指定されたワールドファイルに直接変更を書き込みます。

翻訳対象として選択したテキストは、設定したAIプロバイダーのAPIへ送信され、利用料金が発生する場合があります。

PomiTranslateには、購入、サブスクリプション、アプリ内課金は一切ありません。

![PomiTranslate ワードマーク](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | [한국어](README.ko.md) | 日本語 | [简体中文](README.zh.md)

PomiTranslateは、Minecraft Java Editionのワールドデータ内に存在するプレイヤー向けテキストを安全に抽出し、翻訳するための無料オープンソースツールです。プロジェクトのマスコットはPomiであり、GitHubリポジトリ名は`Minecraft-World-Translator`となっています。

海外のアドベンチャーマップ、カスタムRPGマップ、脱出パズル、大規模サーバーワールドなどを言語の壁なく母国語で快適に楽しむことができます。CLIおよびネイティブデスクトップアプリ（Tauri）は、軽量なパッケージ型JSONLサイドカープロセスを通じて全く同一の高性能Python翻訳コアを実行し、外部リスナーポートは一切開きません。

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

---

## 基本設計思想と安全性の保証

マインクラフトのワールドは、数千ものチャンクとリージョンファイルにまたがる複雑なNBT（Named Binary Tag）データ構造で管理されています。単純な正規表現置換や不完全なNBTエンコーダーを使用すると、座標ヘッダーの破損やコマンドブロックの消失など、取り返しのつかないデータ破壊を引き起こす危険性があります。PomiTranslateは徹底した安全性原則に基づいて動作します。

- **バイト単位のNBT完全性保護**: 変更されていないチャンクは、SHA-256ハッシュに至るまで元のデータと1バイトの違いもなく保持されます。テキストが翻訳された場合でも、周辺タグの再シリアライズを行わず、変更されたJava Modified UTF-8文字列ペイロードのみを所定の位置で正確に書き換えます（In-place update）。
- **ゲーム書式コードと構文の厳格保護**: マインクラフトのカラー・装飾コード（`§a`, `§l`, `§r`）、改行コード（`\n`）、フォーマット指定子（`%s`, `{0}`）、JSONコンポーネント構造、コマンドのセレクター（`@a`, `@p`）を保護エンジンが常時監視します。AIの返答によって書式が損なわれた場合、該当テキストは原文のまま維持され、ワールドの表示崩れを防ぎます。
- **Scan-First（スキャン優先）設計**: Scan Onlyモードでは、ワールド内のテキストを抽出・重複排除し、スキャン計画（Scan Plan）を作成します。この工程では外部APIを一切呼び出さず、ワールドファイルにも一切変更を加えません。
- **Java版 session.lock の検知**: 書き込み前に必ずワールド内の`session.lock`を確認します。マインクラフトやサーバーがワールドを実行中である場合、書き込み処理を即座にブロックします。
- **バージョン管理されたアトミックバックアップ**: ファイル書き換えの直前に、OSのアプリケーションデータ領域に完全なマルチファイルバックアップセットを自動生成します。API障害や中断が発生した場合でも中途半端な書き込みは行われず、復元直前の状態も復旧用スナップショットとして保護されます。

![スキャン優先](../assets/illustrations/docs/doc_scan_first_ja_v1.png)

---

## 抽出・翻訳に対応するテキストコンポーネント

オーバーワールド、ネザー（`DIM-1`）、エンド（`DIM1`）、カスタムディメンションを含むワールド全体を走査し、以下のテキスト要素を抽出します。

| コンポーネント分類 | 対象ゲーム内要素 | 抽出および処理仕様 |
| :--- | :--- | :--- |
| **看板 (Signs)** | 自立看板、吊り看板、壁看板 | バージョン1.8〜1.19のレガシー片面看板テキスト、および1.20以降の最新両面看板（前面・背面 `messages`）に完全対応 |
| **本 (Books)** | 本と羽根ペン、記入済みの本 | 本のタイトル、フィルター済みタイトル、著者名、プレーンテキストまたはJSONコンポーネントで構成された個別ページ |
| **アイテム情報** | 武器、防具、道具、カスタムアイテム | カスタム表示名（`display.Name`）、説明文（Lore）、1.20.5以降の最新アイテムコンポーネント（`minecraft:custom_name`, `minecraft:lore`）、ホバー／クリックイベントテキスト |
| **収納ブロック** | チェスト、シュルカーボックス、樽、かまど | チェスト自体のカスタム名、および内部スロットに格納されている全アイテムの再帰的スキャン |
| **エンティティ・ブロック** | MOB、NPC、防具立て、ブロック | 生物エンティティの名前（`CustomName`）、防具立てのテキスト、名前付きタイルエンティティ名 |
| **ディスプレイ要素** | テキストディスプレイ (`text_display`) | 1.19.4以降で追加されたテキストディスプレイエンティティのコンポーネントテキストに対応 |
| **コマンドブロック** | 衝撃型、反復型、鎖付きコマンドブロック | `/tellraw`、`/title`、`/subtitle`、`/actionbar` コマンド、および `execute ... run` でネストされたサブコマンド内のメッセージを抽出。座標やターゲットセレクターは完全に保護 |
| **リソースパック** | ワールド内 `resources.zip` | 有効化時、ワールドフォルダ内のリソースパック言語ファイル（`assets/<namespace>/lang/*.json` または `.lang`）を同時にスキャン・翻訳し、リージョンと同じバックアップセットで管理 |

---

## リージョンファイルおよび圧縮形式の互換性

自動回帰テストフィクスチャによって完全に検証された形式のみ、書き込みを許可しています。

### 公式対応形式
- **リージョンファイル標準**: Minecraft Java Edition Anvil形式（`.mca`）およびエンティティ保存フォルダ（`entities/*.mca`）
- **チャンク圧縮形式**: Gzip、Zlib、無圧縮（Uncompressed）、Minecraft 1.20.5+ LZ4（`LZ4Block`）
- **外部オーバーフローチャンク**: 大容量チャンク用の外部 `.mcc` ファイル（`c.<x>.<z>.mcc`）
- **ディレクトリ構成**: 標準バニラワールド、カスタムディメンションフォルダ、`level.dat`を共有するPaper/Spigotマルチワールド構成

### 非対応形式（検知時は自動的に書き込み禁止）
ワールドデータの破損を防ぐため、以下の形式が検知された場合は即座に書き込みを停止します。
- **Bedrock Edition**: 統合版レベル構造またはMojang LevelDB（`.ldb`）ファイル
- **Anvil以前の旧形式**: 1.2以前のレガシー `.mcr` リージョンファイル
- **サードパーティ圧縮形式**: 一部サーバーで採用されているZstandardベースの `.linear` リージョンファイル
- **未確認・破損した圧縮アルゴリズム**: 認識できない圧縮ヘッダー（圧縮タイプ127など）

詳細は [support-matrix.md](support-matrix.md) の自動生成サポート表をご参照ください。

![非対応形式の停止](../assets/illustrations/docs/doc_unsupported_ja_v1.png)

---

## 対応AIプロバイダーとキーチェーン保護

PomiTranslateは主要なLLMプロバイダーに対応しています。
- **OpenAI**: GPT-4o、GPT-4o-mini、および互換チャットモデル
- **Anthropic**: Claude 3.5 Sonnet、Claude 3.5 Haiku、Claude 3 Opus
- **Google Gemini**: Gemini 1.5 Pro、Gemini 1.5 Flash、Gemini 2.0 Flash
- **OpenRouter**: 多種多様なオープンソースおよび商用LLMへのアクセス
- **Custom (ローカル・互換エンドポイント)**: Ollama、vLLM、LM Studioなどの標準OpenAI ChatまたはAnthropic Messages形式に準拠するローカル推論サーバーとの連携

翻訳開始前にプロバイダーのアクティブなモデルカタログを取得し、指定されたモデルの存在とコンテキスト長を検証します。カタログに存在しないモデルの場合は安全のために書き込みを行わずに停止します。

### OSキーチェーンによる認証情報の保護
APIキーはプレーンテキスト、`settings.json`、SQLiteデータベース、ログファイル、Gitコミットなどに一切保存されません。
- **macOS**: Apple Keychain Services (`PomiTranslate`)
- **Windows**: Windows 資格情報マネージャー (`PomiTranslate`)
- **Linux**: Freedesktop Secret Service (DBus)

保存されたAPIキーは翻訳実行時にプロセスの標準入力（stdin）経由でのみメモリに渡され、設定画面からいつでも個別に削除できます。

設定ファイルの保存先:
- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate/settings.json`（または `~/.local/share/PomiTranslate/settings.json`）

![API通知](../assets/illustrations/docs/doc_api_notice_ja_v1.png)

---

## 3段階の翻訳ワークフロー

```
[フェーズ1: Scan Only（スキャン優先）]
ワールドファイル (.mca) ──> テキスト抽出 ──> 重複排除 ──> スキャン計画 & 指紋作成
（APIリクエスト0回、完全読み取り専用、候補検索・除外・直接編集に対応）

[フェーズ2: バッチ翻訳]
固有候補 ──> レート制限 & サーキットブレーカー ──> AIプロバイダー ──> チェックポイント
（書式保護、接続エラー時の安全停止、部分失敗時の安全な再開に対応）

[フェーズ3: アトミック書き込み]
検証済みバックアップ ──> session.lock確認 ──> リージョンパッチ書き込み ──> 完了
（NBTバイト単位更新、復元前安全スナップショット保持、ワンクリックロールバック）
```

---

## クイックスタート (CLI)

CLIの実行環境にはPython 3.12を推奨します。（配布用デスクトップアプリを使用する場合、Pythonやビルドツールの導入は不要です。）

```bash
# 仮想環境の構築
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 1. Scan Only (API呼び出しを行わずにテキスト抽出)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --dry-run \
  --report-path ./scan-report.json
```

### 2. ワールド翻訳の実行 (スキャン指紋による安全実行)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --target-language "ja" \
  --provider openrouter \
  --model "anthropic/claude-3.5-sonnet" \
  --style story \
  --expect-fingerprint "<スキャンレポート記載の指紋>"
```
*`--api-key` を省略すると、OSキーチェーンに保存されているキーを自動で使用します。*

### 3. バックアップからの復元
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --restore-backup
```

![書き込み前バックアップ](../assets/illustrations/docs/doc_backup_first_ja_v1.png)

---

## ネイティブデスクトップアプリ

Tauri 2とSvelte 5で構築されたデスクトップアプリは、快適で使いやすい操作画面を提供します。

- **多言語UIの即時切り替え**: 翻訳先の言語とは独立して、日本語・英語・韓国語の表示言語をワンクリックで変更できます。
- **候補確認テーブル**: 抽出されたテキストの出現回数、座標、ブロック／エンティティIDを確認し、特定の文字列を除外したり直接手動翻訳を入力できます。
- **リクエスト数と費用の見積もり**: バッチサイズに基づいた最小APIリクエスト数やトークン情報を事前に確認できます。
- **安全な中断と再開**: 処理を中断してもワールドを破損せず安全に停止し、チェックポイントを活用して未完了分のみを後から再開できます。
- **バックアップ一覧と復元**: 作成されたバックアップの履歴を確認し、いつでもワンクリックで変更前の状態に戻せます。

### ソースコードからのビルド
```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```

---

## 翻訳スタイルプリセット

マップのジャンルや世界観に合わせて6つの翻訳スタイルを選択できます。
- **標準 (`neutral`)**: 過度な脚色を行わず、正確でバランスの取れた標準的な翻訳（サバイバルマップ向け）
- **自然な会話体 (`casual`)**: NPCのセリフや会話に生動感を与える親しみやすい口語体スタイル
- **格式体 (`formal`)**: 石碑、日誌、歴史的記録物に適した重厚で引き締まった文体
- **丁寧体 (`polite`)**: チュートリアル、案内メッセージ、クエスト解説に適した丁寧な敬語（です・ます調）
- **ストーリー小説風 (`story`)**: ファンタジーやアドベンチャーマップの没入感を高める叙事詩的で豊かな文学表現
- **カスタム (`custom`)**: 独自の世界観や専門用語のルールを反映させるための自由記述プロンプト

---

## 自動テストの実行

```bash
# コア機能回帰テスト
.venv/bin/python test_core.py

# リリースフィクスチャ検証（圧縮、NBT、セッションロック、復元）
.venv/bin/python tests/test_release_fixtures.py

# プロバイダーAPIおよびキーチェーン設定テスト
.venv/bin/python tests/test_providers.py

# ブランド表記・秘密情報漏洩防止テスト
.venv/bin/python tests/test_brand_secrets.py

# デスクトップサイドカープロトコルテスト
.venv/bin/python tests/test_desktop_entry.py

# フロントエンド単体テスト
./node_modules/.bin/vitest run
```

---

## お問い合わせ・フィードバック

- バグ報告および機能要望: `mini0227kim@gmail.com`
- お問い合わせの際は、OS、使用プロバイダー、モデル名、該当するエラーログを添えてご連絡ください。（APIキーは絶対に送信しないでください。）

---

## ライセンス

PomiTranslateは [MITライセンス](../LICENSE) のもとで公開されています。
