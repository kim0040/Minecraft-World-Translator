# PomiTranslate

**World Translator for Minecraft** — 翻译 Minecraft Java Edition 世界文本的桌面应用

<img src="../assets/brand/wordmark/logo_wordmark_v1.png" alt="PomiTranslate" width="340" />

[한국어](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | 简体中文

玩海外冒险地图时，告示牌、书籍和物品说明常常读不懂，节奏也因此被打断。PomiTranslate 可以把这些文本换成你熟悉的语言。先扫描世界，确认要翻译的句子，再挑选需要的句子手动翻译或交给所选 AI 提供商翻译，最后在验证过的备份保护下写入世界。

这是一个由大学生 **김현민（Hyunmin Kim）** 为了自己使用而开始的无偿个人开源项目，依靠个人时间和有限预算维护，不是企业运营的商用服务，也不是付费支持产品。吉祥物是 **Pomi**。

> **开发中：** 已在 macOS Apple Silicon 的隔离开发应用中确认主要流程。签名正式安装包、Windows/Linux 实机验证以及真实付费翻译的最终验证尚未完成。[当前状态](current-state.md) · [后续工作](follow-up-work.md)
>
> NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## 工作方式

PomiTranslate 不会把世界复制到应用内，而是直接读取你选择的文件夹。整个过程分为五个阶段，扫描和检查阶段完全不会改动世界文件。

1. **选择世界** — 打开 Java Edition 世界文件夹（含 level.dat）或服务器根目录。应用会显示检测到的维度、数据格式（DataVersion）、世界内置资源包以及已保存的备份数量。Bedrock、旧版 `.mcr`、`.linear` 以及正被游戏或服务器占用的世界会在开始前被拦截。
2. **扫描** — 查找需要翻译的文本。此阶段不调用翻译 API，也不写入任何文件。应用会汇总唯一字符串数、出现位置总数、预计 API 请求数和文本类型，并把无法读取的区块或不受支持的格式原样保留，以警告形式提示。
3. **检查** — 通过搜索、排序和类型/状态筛选查看候选文本。可以排除不想翻译的句子，也可以为任意句子填写自己的译文。同一原文出现在多个位置时只翻译一次，再应用到所有位置。
4. **执行** — 确认目标世界、翻译语言、提供商与模型、要发送的字符串数、预计请求数与费用以及安全备份后开始。在所有翻译正常完成之前，世界原文件不会被改动。
5. **结果与恢复** — 查看已更改文件数、翻译/失败/保留原文的句子、使用的 token 和实际计费金额。需要撤销时，在备份管理中恢复到任意时间点；恢复前的状态也会保留为安全快照。

## 界面

### 亲自检查要翻译的句子

![候选搜索、类型筛选与手动翻译编辑界面](images/review.png)

用搜索和类型/状态筛选找到句子，可以将其排除出翻译范围，或直接填写自己的译文。还能查看同一原文出现的位置。`§` 格式代码以及 `%s`、`{0}` 等占位符会保留，以便在游戏内正常显示。

### 模型与推理设置

![提供商、模型、推理方式与密钥保存状态界面](images/settings.png)

OpenRouter 推理可在 **模型默认 / 关闭推理 / 自定义设置** 中选择。模型支持信息查询与设置保存相互独立，界面底部固定了保存和放弃更改区域。

<details>
<summary>执行前确认界面</summary>

![推理、请求数、预计费用与外部传输确认界面](images/run.png)

</details>

截图来自以 **合成数据** 运行当前产品 UI 的结果。图中的模型、世界和费用仅用于介绍，不代表真实用量或对特定模型的支持保证。[截图说明](images/README.md)

## 主要功能

### 扫描与检查

- 在不修改世界、不调用翻译 API 的前提下先查看候选文本和支持范围。
- 提供搜索、排序（世界顺序、原文顺序、出现频率、按类型）、类型/状态筛选以及批量加入或排除。
- 可以查看每个句子的出现位置并填写手动译文。只应用手动译文时，无需任何翻译 API 请求。
- 可以跳过已经使用目标语言书写的文本，减少重复翻译的费用。

### 提供商与模型

- 可配置 OpenAI、Gemini、Anthropic、OpenRouter、Comet 以及 Custom endpoint（OpenAI/Anthropic 兼容协议）。可用模型取决于提供商和账户。
- 查询模型列表，并在有价格信息时显示每百万 token 的价格。OpenRouter 会自动查询公开目录，该查询不会保存设置。
- OpenRouter 推理可选择模型默认、关闭或指定支持的强度。无法关闭推理的模型以及不受支持的强度无法保存。
- 可设置目标语言和文体（标准、亲切、正式、敬语、故事风、自定义系统提示词），并附加额外指示。润色指示文本属于单独的 AI 请求，可能产生费用。

### 安全写入与恢复

- 写入前把将要修改的文件保存为验证过的备份，恢复前的状态也会保留为 recovery snapshot。
- 扫描后世界若发生变化，指纹不再匹配，写入会被拒绝。游戏或服务器正在使用世界时，session.lock 冲突会中止写入。
- 指向世界外部的路径和符号链接资源包会在读取和发送 API 之前被拦截。
- 取消或失败时，已翻译的句子会被保留，重试只翻译剩余部分。提供商故障导致失败时，世界文件完全不会被改动。
- 无法读取的区块原样保留，并在结果中报告。

### 资源包 ZIP

- 可选处理世界内 `resources.zip` 以及明确选择的外部 ZIP（最多 16 个）中的语言文件。
- 外部 ZIP 在修改前也会备份，恢复时需要在设置中重新选择同一个 ZIP。暂不支持文件夹形式的资源包。

### 密钥与隐私

- API 密钥的默认保存方式是 **本地加密 SQLite + 独立 key 文件**。仅本次会话和 OS 密钥链为可选项。
- 已保存的密钥不会再次显示在界面上，也不会写入公开设置 JSON 或世界备份。
- 只有在用户点击导入按钮时才会访问 OS 密钥链，应用启动时不会自动读取。

### 桌面体验

- 使用 Tauri 2 + Svelte 5 界面和 Python 核心，不为 UI 打开 localhost 服务器。
- UI 语言为韩语、英语、日语，支持跟随系统、浅色和深色主题，可在视图菜单中放大 75–200%。**此中文 README 只是文档翻译，不代表中文 UI 已实现。**
- 同时提供使用同一核心的 CLI。桌面端保存的密钥与 CLI 的 keyring/环境变量不会自动共享。

## 使用方法

1. 关闭 Minecraft 或服务器，并创建 **世界的独立副本**。
2. 在 **环境设置** 中选择提供商、模型、目标语言和需要的翻译指示。使用 AI 翻译时，输入并保存自己的 API 密钥。
3. 在 **选择世界 → 扫描世界** 中打开副本，确认支持范围和警告。
4. 在 **候选检查** 中排除句子或填写手动译文。
5. 在 **翻译执行** 中确认目标、推理、外部传输和预计费用后开始。
6. 查看 **完成结果**，并在游戏中确认效果。需要撤销时，在 **备份管理** 中恢复。

费用估算可能与实际账单不同。推理 token、重试和模型路由费用不包含在估算中，请同时查看提供商后台。设置、恢复和 CLI 的详细说明见 [使用指南](user-guide.md)。

### 运行与安装

目前以开发构建为准，不宣称已有签名正式安装包或已完成所有 OS 支持。从源码运行需要 Python 3.12、Node.js 22.12 以上、pnpm 12.6.0、Rust toolchain 以及 [Tauri 平台准备项](https://v2.tauri.app/start/prerequisites/)。

```bash
git clone https://github.com/kim0040/PomiTranslate.git
cd PomiTranslate
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pyinstaller==6.16.0
pnpm install --frozen-lockfile
pnpm desktop:dev
```

上面的虚拟环境激活命令以 macOS/Linux 为例。Windows 命令、toolchain 版本和打包请参阅 [开发指南](development.md)，贡献步骤请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md)。打包后的应用包含 Python sidecar，但尚未完成 clean-machine 安装验证。

## 支持范围

可处理告示牌、书页与书名（含被过滤的书名）、实体与方块名称、物品名称与说明、文本展示、命令文本组件以及 ZIP 资源包语言文件。已验证的压缩格式为 gzip、zlib、无压缩、LZ4 和外部 `.mcc`。支持范围以 **合成格式** 为准：某一行通过只表示该形状的读写正确，并不代表能找出所有 Minecraft 版本、模组或世界中的全部文本。

扫描范围包括各维度的 `region`/`entities` 文件夹、世界内的 `resources.zip`，以及桌面端明确选择的外部 ZIP。数据包、scoreboard、command storage、`level.dat` 文本、playerdata 和文件夹形式资源包不在当前范围内。Bedrock、`.mcr`、`.linear` 和未知压缩格式不会被写入。[支持表](support-matrix.md)

## 费用、数据与免责声明

应用本身没有购买、订阅或内购。**AI API 费用会按所选提供商的政策由用户承担。** 你选择翻译的文本和翻译指示会发送到所选 API 提供商或中转服务。请同时确认各提供商的保留、训练和隐私政策。

桌面端 API 密钥的默认保存方式是 **本地加密 SQLite + 独立 key 文件**，仅本次会话和 OS 密钥链为可选项。这并不能防御同一用户账户下能同时读取两个文件的进程。[数据与密钥](privacy.md)

本软件按 **AS IS** 提供，不保证翻译准确性、与所有世界的兼容性、数据保全或不间断使用。在适用法律允许的范围内，作者和贡献者不对数据丢失、世界损坏、API 账单等使用造成的损害承担责任。请查看 [完整免责与权利说明](disclaimer.md) 和 [MIT 原文](../LICENSE)。

地图、资源包和译文涉及的第三方权利与软件许可证无关。未经原作者许可，请勿重新分发翻译内容。

## 开发与验证状态

已在 macOS Apple Silicon 开发应用中确认从世界选择到扫描、检查、执行、结果、恢复的主要流程，并用合成 fixture 检查各格式的读写。最新源码通过了相关的 frontend、browser、Rust 检查以及 provider 的 Python 检查，并生成了 unsigned debug 应用包。已注册真实 OpenRouter 密钥和模型并验证公开模型查询，但 **尚未执行真实付费翻译的端到端流程**。

目前处于 Phase 2 进行中，Phase 3 尚未开始。签名、notarization、updater、Windows/Linux clean-machine 安装、macOS Intel 以及 OS 密钥链 opt-in 的 native 验证仍然待办。准确的检查范围和剩余 gate 记录在 [当前状态](current-state.md) 和 [后续工作](follow-up-work.md)。

## 作者与联系方式

- **김현민（Hyunmin Kim）** — 制作与维护 · [mini0227kim@gmail.com](mailto:mini0227kim@gmail.com)
- 缺陷与建议：[GitHub Issues](https://github.com/kim0040/PomiTranslate/issues)
- 贡献：[CONTRIBUTING.md](../CONTRIBUTING.md)

报告缺陷时请附上 OS、应用版本和复现步骤。请勿在公开 Issue 中发布 API 密钥、私人世界或包含机密的日志。不承诺回复时间、修复排期或金钱补偿。

## 许可证与文档

项目源码保留原有 **[MIT License](../LICENSE)**。依赖各自遵循其许可证，不会因项目的 MIT 而被重新授权。在已审查的范围内未发现与保留 MIT 的明显冲突，但正式二进制发布前仍需完成各分发物的声明和全平台依赖验证。[第三方声明](../THIRD_PARTY_NOTICES.md)

[文档目录](README.md) · [当前状态](current-state.md) · [后续工作](follow-up-work.md)
