# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate 字标](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | 简体中文

PomiTranslate 是一款免费且开源的本地工具，专为安全提取并翻译 Minecraft Java 版世界内玩家可见文本而设计。项目吉祥物是 Pomi（波米），技术代码仓库名称保持为 `Minecraft-World-Translator`。

CLI 命令行工具与基于 Tauri 的桌面客户端共用同一套高性能 Python 核心引擎，两者通过轻量级的打包 JSONL 进程间通信协作。为确保最高级别的数据安全，只有在完成前置自动备份且校验无误后，翻译才会安全写入世界文件。仅扫描模式（Scan Only）绝不会调用外部 API，也不会更改任何世界字节。命令选择器、资源命名空间、坐标、数值、颜色格式代码及占位符均会原样完好保留。

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

## 支持翻译的文本类型

- 告示牌文本（包含旧版单面告示牌及新版双面正反面文本）
- 书本内容（页面正文、书名以及过滤书名）
- 实体与方块的自定义名称
- 物品显示名称及说明（Lore）
- 原始 JSON 文本组件与 1.20.5+ 物品组件
- 命令反馈输出文本（`tellraw`、`title`、`subtitle`、`actionbar` 等）
- 世界内置材质包（`resources.zip`）中的 `lang/*.json` 语言文件（启用选项时）

![先扫描](../assets/illustrations/docs/doc_scan_first_zh_v1.png)

## 格式兼容性与支持矩阵

PomiTranslate 仅正式支持已通过自动化测试套件（Test Fixtures）严格验证的数据格式：

- **区域压缩格式**：Gzip、Zlib、未压缩格式，以及 Minecraft 1.20.5+ LZ4（`LZ4Block`）
- **外部区块文件**：`c.<x>.<z>.mcc` 区块溢出文件（压缩字节数据）
- **目录结构**：标准维度目录、自定义维度，以及包含 `level.dat` 的 Paper/Spigot 风格服务器平行世界目录

### 自动识别并限制写入的不受支持格式（安全保护）

为防止存档损坏，当检测到以下格式时将自动禁止写入：

- Bedrock（基岩版）世界存档
- Anvil 格式之前的旧版 `.mcr` 区域文件
- 第三方非标准压缩格式 `.linear`
- 包含压缩代码 127 在内的未知或不受支持的压缩格式

完整格式支持清单请参见 [support-matrix.md](support-matrix.md)。

![不支持的格式会停止](../assets/illustrations/docs/doc_unsupported_zh_v1.png)

## 支持的 AI 供应商

官方支持的 AI 供应商包括 OpenAI、Google Gemini、Anthropic、OpenRouter 以及 Custom（自定义兼容端点）。自定义端点支持根据填写的 Base URL 自动匹配 OpenAI Chat 格式或 Anthropic Messages 协议格式。旧版配置参数亦保持良好向下兼容。

在正式启动翻译前，PomiTranslate 会自动拉取目标供应商的模型列表，核对模型 ID、名称和上下文长度。若所选模型未在列表中查得，系统将在写入世界前自动安全终止。

## 密钥安全与配置文件

用户输入的 API 密钥直接加密保存在操作系统专属安全密钥链（macOS Keychain、Windows 凭据管理器、Linux Secret Service）中，服务名为 `PomiTranslate`，账户名为供应商 ID（例如 `openrouter`）。API 密钥绝不会明文保存在 `settings.json`、SQLite 数据库、运行日志或 Git 提交记录中。

通用偏好设置在软件更新后仍完整保存在安装目录之外：

- macOS：`~/Library/Application Support/PomiTranslate/settings.json`
- Windows：`%APPDATA%\PomiTranslate\settings.json`
- Linux：`$XDG_DATA_HOME/PomiTranslate/settings.json` 或 `~/.local/share/PomiTranslate/settings.json`

用户可在桌面客户端的设置面板中随时单独清除保存在系统密钥链中的 API 密钥。

![文字会发到你选择的供应商](../assets/illustrations/docs/doc_api_notice_zh_v1.png)

## 快速上手 (CLI)

命令行模式推荐运行环境为 Python 3.12。使用打包发布的桌面端独立安装包时，最终用户无需在电脑上预先安装 Python 或任何开发工具链。

```bash
# 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 1. 扫描世界 (Scan Only)
在不调用 API 且不改写世界的前提下，提取候选文本并统计出现频次：

```bash
python mc_world_translator.py --world-dir "/path/to/world" --dry-run --report-path ./scan-report.json
```

### 2. 执行翻译
检查扫描报告后启动正式翻译。通过 `--expect-fingerprint` 传入指纹校验；若世界数据在此期间发生任何意外变动，将自动拒绝写入以确保数据安全：

```bash
python mc_world_translator.py \
  --world-dir "/path/to/world" \
  --provider openrouter \
  --model "your-text-model" \
  --expect-fingerprint "<扫描报告中提供的指纹>"
```

省略 `--api-key` 参数时，程序将自动读取系统密钥链中已存储的该供应商密钥。

### 3. 安全还原 (Restore)
如遇意外状况，可随时将世界安全还原至校验过的最新备份点：

```bash
python mc_world_translator.py --world-dir "/path/to/world" --restore-backup
```

每次写入均会自动生成带版本标记的备份集合。还原操作将完整回滚所有已变更文件（包括 `entities` 和已启用的材质包 `resources.zip`），并将当前状态作为安全快照额外归档。当 Minecraft 或服务器正占用 Java 版 `session.lock` 锁定时，写入操作将自动拒绝启动。

![写入前先备份](../assets/illustrations/docs/doc_backup_first_zh_v1.png)

## 桌面客户端

基于 Tauri 2 与 Svelte 5 构建的现代化原生桌面客户端具备多重安全防护与便捷功能：

- **多语言界面**：完整支持简体中文、英语、韩语和日语界面语言切换（与翻译目标语言完全解耦）
- **最近世界管理**：便捷记录与快速打开最近处理的世界，显示游戏 DataVersion 元数据
- **前置安全诊断**：自动基于数据结构诊断格式兼容性并检测只读与会话锁定状态
- **候选文本审查**：按频次或类型过滤搜索待翻文本，支持排除指定词条或手动输入自定义翻译（覆盖 AI 翻译）
- **费用与请求预估**：根据分批大小实时估算最小 API 请求次数与 Token/费用范围
- **安全取消与智能断点续传**：随时安全暂停任务，已翻译文本将持久化缓存，续传时仅请求未完成内容
- **历史备份管理**：查看历史版本备份详情，支持带还原前快照的可靠一键恢复

从源代码构建：

```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```

打包生成的可执行文件内嵌所有原生二进制支持库，最终用户无需安装 Node.js、Python 或 Rust 即可直接使用。

## 本地 Web UI (辅助工具)

如果您的电脑中已配置好 Python 环境，可使用内置轻量级服务 `webui_server.py` 在浏览器中访问（`http://127.0.0.1:8765`）：

```bash
python webui_server.py
```

## 配置文件规范

配置参数详情请参见 [config.example.toml](../config.example.toml)。`world_dir` 仅在指向实际目标世界时填入，切勿将 API 密钥以明文形式写入配置文件。

## 自动化测试

```bash
.venv/bin/python test_core.py
.venv/bin/python tests/test_release_fixtures.py
.venv/bin/python tests/test_providers.py
.venv/bin/python tests/test_brand_secrets.py
.venv/bin/python tests/test_desktop_entry.py
```

## 问题反馈与支持

- Bug 报告及功能建议：`mini0227kim@gmail.com`
- 咨询时请附上您的操作系统、使用的 AI 供应商与模型、以及错误日志。（出于安全考虑，切勿随信发送 API 密钥。）

## 开源许可证

本项目基于 [MIT License](../LICENSE) 开源许可证发布。
