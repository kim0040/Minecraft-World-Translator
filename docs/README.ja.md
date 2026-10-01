# PomiTranslate

**World Translator for Minecraft** — Minecraft Java Edition のワールド内テキストを翻訳するデスクトップアプリ。

[한국어](../README.md) | [English](README.en.md) | 日本語 | [简体中文](README.zh.md)

看板、本、アイテム説明などを読みやすい言語に変えるためのツールです。まずスキャンして候補を確認し、自分で入力した訳文または選択した AI API で翻訳を適用します。マスコットは Pomi です。

大学生の **김현민（Hyunmin Kim）** が自分で使うために始めた無料の個人オープンソースプロジェクトです。個人の時間と限られた予算で開発しており、有料のサポート・データ復旧サービスではありません。

> **開発中:** macOS Apple Silicon の開発アプリで主要な操作を確認しました。署名済み正式版、Windows/Linux の実機検証、実際の有料翻訳の最終検証は未完了です。[現状](current-state.md) · [今後の作業](follow-up-work.md)
>
> NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## 画面

![候補の検索・除外・手動翻訳](images/review.png)

![モデル・推論方式・キーの保存状態](images/settings.png)

現在の UI を **合成データ** で撮影した紹介用の画面です。表示された費用・モデル・ワールドは例であり、実際の利用量や対応保証ではありません。[画像の説明](images/README.md)

## 機能と使い方

1. Minecraft/サーバーを終了し、ワールドを別にコピー・バックアップします。
2. 環境設定で提供者・モデル・翻訳先言語を選びます。AI を使う場合は自分の API キーを保存します。
3. コピーしたワールドを選択してスキャンし、対応範囲と警告を確認します。スキャンは翻訳 API を呼ばず、ワールドファイルを書き換えません。
4. 候補を検索・フィルターして除外や手動翻訳を設定します。同じ原文の出現位置も確認できます。
5. 実行前に推論方式・費用見積り・外部送信先を確認して実行します。
6. 結果とゲーム内の動作を確認し、必要ならバックアップ管理から復元します。

OpenAI/Gemini/Anthropic/OpenRouter/Comet/Custom を設定できます。モデルはアカウントと提供者によって異なります。OpenRouter の推論はモデル既定・無効化・対応強度の指定から選べます。モデル情報の取得では設定を保存しません。

書き込み前の検証済みバックアップ、復元前の recovery snapshot、キャンセル・再開、任意の ZIP リソースパックの言語ファイル処理を提供します。UI は韓国語・英語・日本語です。

現在はソースからの開発実行が基本です。Python3.12、Node/pnpm、Rust と各 OS の Tauri 準備が必要です。[開発手順](development.md) · [詳細な使用案内](user-guide.md)

データパック、scoreboard、command storage、playerdata、level.dat のテキスト、フォルダー形式のパックは現在の対象外です。Bedrock、.mcr、.linear、未知の圧縮には書き込みません。[合成 fixture の対応表](support-matrix.md)はすべてのバージョン・マップの保証ではありません。

## 費用・データ・免責

アプリ自体に購入・定期購読・アプリ内決済はありませんが、AI API、推論、再試行などの費用が発生する場合があります。翻訳対象と指示は選択した API または中継サービスへ送信されます。見積りは請求額の上限ではありません。

キーの既定保存方式はローカル暗号化 SQLite と別の key ファイルです。セッション専用・OS キーチェーンは任意です。同じアカウントで両ファイルを読めるプロセスまでは保護しません。[データとキー](privacy.md)

本ソフトウェアは **AS IS** で提供され、正確性・互換性・データ保全・継続サポートを保証しません。適用法が許す範囲で、作者・貢献者の責任は [MIT 原文](../LICENSE)に従って制限されます。法的に排除できない責任を免除するものではありません。[免責・第三者の権利](disclaimer.md)

MIT は Minecraft のゲーム資産、マップ、パック、商標の権利を許諾しません。原作者の許可なく翻訳版を再配布しないでください。

## 作者・ライセンス

**김현민** — 制作・保守 · [mini0227kim@gmail.com](mailto:mini0227kim@gmail.com)

[Issues](https://github.com/kim0040/PomiTranslate/issues) · [貢献方法](../CONTRIBUTING.md)

プロジェクトソースは既存の MIT を維持します。依存関係はそれぞれのライセンスに従い、正式なバイナリ配布の告知・プラットフォーム検証は未完了です。[第三者の告知](../THIRD_PARTY_NOTICES.md) · [文書一覧](README.md)
