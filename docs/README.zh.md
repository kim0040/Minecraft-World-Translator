# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate 字标](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | 简体中文

PomiTranslate 是一个免费的本地工具，用来翻译 Java 版世界里玩家能看见的文字。吉祥物是 Pomi。GitHub 仓库名仍是 `Minecraft-World-Translator`。

命令行和打包后的桌面入口使用同一个翻译器。只有在校验过的备份完成之后，翻译才会改写世界。Scan Only 不会请求供应商，也不会改变世界字节。选择器、资源位置、数字、坐标和格式占位符会保留。

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

## 会翻译的文字

- 旧告示牌，以及有正反面的告示牌
- 书页、标题和过滤标题
- 自定义名称、物品名称和说明
- 直接文本组件和 1.20.5+ 物品组件
- `tellraw`、`title`、`subtitle`、`actionbar` 中的文字
- 启用后，资源包 zip 里的 `lang/*.json`

![先扫描](../assets/illustrations/docs/doc_scan_first_zh_v1.png)

## 格式

只有夹具通过的范围才算支持：gzip、zlib、不压缩、Minecraft 1.20.5+ 的 LZ4（`LZ4Block`）、只含压缩字节的外部 `.mcc`、标准区域目录、自定义维度，以及带 `level.dat` 的 Paper 风格相邻世界。

Bedrock、Anvil 之前的 `.mcr`、`.linear`，以及包括 id 127 在内的未知压缩，只会识别并停止写入。清单见 [support-matrix.md](support-matrix.md)。macOS Intel、Windows x64 和 Linux x64 不列为已支持平台。

![不支持的格式会停止](../assets/illustrations/docs/doc_unsupported_zh_v1.png)

## 供应商与保存

产品供应商是 OpenAI、Gemini、Anthropic、OpenRouter 和 Custom。Custom 按你填写的地址使用 OpenAI 聊天格式或 Anthropic 消息格式。旧的 Comet 设置仍然可以读取。

正式翻译前会拉取该供应商的文本模型，并使用公布的 id、名称和上下文长度。所选模型不在列表中时，会在写入世界之前停止。

API 密钥保存在操作系统钥匙串中，服务名是 `PomiTranslate`，账户名是 `openrouter` 这样的供应商 id。密钥不会写入 `settings.json`、SQLite、日志或 git。

公开设置在更新后仍留在安装目录之外：

- macOS：`~/Library/Application Support/PomiTranslate/settings.json`
- Windows：`%APPDATA%\PomiTranslate\settings.json`
- Linux：`$XDG_DATA_HOME/PomiTranslate` 或 `~/.local/share/PomiTranslate/settings.json`

![文字会发到你选择的供应商](../assets/illustrations/docs/doc_api_notice_zh_v1.png)

## 运行

已测试的运行时是 Python 3.12。打包后的桌面入口不要求最终用户安装 Python。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python mc_world_translator.py --world-dir "/path/to/world" --dry-run --report-path ./scan-report.json
```

把扫描得到的指纹传给 `--expect-fingerprint` 后，世界若已改变，翻译会被拒绝。`--restore-backup` 会还原该次运行改过的全部文件。

![写入前先备份](../assets/illustrations/docs/doc_backup_first_zh_v1.png)

`python -m mwt.desktop_entry` 通过标准输入输出使用 JSONL，不会打开本地端口。没有签名凭据时，发布任务停在未签名草稿，并且不会关闭签名校验。

已有 Python 时可以用 `python webui_server.py` 在 `127.0.0.1:8765` 打开本地界面。打包后的应用不需要这个服务器。

示例配置是 [config.example.toml](../config.example.toml)。不要把 API 密钥写进文件。

联系：`mini0227kim@gmail.com`。不要发送 API 密钥。许可证为 MIT。
