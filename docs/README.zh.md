# PomiTranslate

**World Translator for Minecraft** — 翻译 Minecraft Java Edition 世界文本的桌面应用。

[한국어](../README.md) | [English](README.en.md) | [日本語](README.ja.md) | 简体中文

用于翻译冒险地图中的告示牌、书籍和物品说明。先扫描、检查候选文本，再使用手动译文或所选 AI 提供商执行翻译。吉祥物是 Pomi。

这是大学生 **김현민（Hyunmin Kim）** 为自己使用而开始的免费个人开源项目，依靠个人时间和有限预算维护，并非付费支持或数据恢复服务。

> **开发中：** 已在 macOS Apple Silicon 开发应用和隔离数据中检查主要操作。正式签名发布、Windows/Linux 实机验证和真实付费翻译的最终验证尚未完成。[当前状态](current-state.md) · [后续工作](follow-up-work.md)
>
> NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## 界面

![候选搜索、排除与手动译文](images/review.png)

![模型、推理方式和密钥状态](images/settings.png)

截图来自当前 UI 和 **合成数据**。所示模型、世界和费用仅用于介绍，不代表真实使用量或支持保证。[截图说明](images/README.md)

## 使用方法与功能

1. 关闭 Minecraft/服务器，单独复制并备份世界。
2. 在设置中选择提供商、模型和目标语言。使用 AI 时保存自己的 API 密钥。
3. 选择世界副本并扫描，检查范围与警告。扫描不调用翻译 API，也不改写世界文件。
4. 搜索、筛选、排除候选文本或填写手动译文，并检查出现位置。
5. 执行前核对推理设置、请求和费用估算、外部数据发送信息。
6. 检查结果和游戏内效果，需要时在备份管理中恢复。

可以配置 OpenAI、Gemini、Anthropic、OpenRouter、Comet 和 Custom endpoint。可用模型取决于提供商与账户。OpenRouter 推理可选模型默认、允许时关闭或指定支持的强度。查询模型信息不会保存设置。

提供写入前验证备份、恢复前 recovery snapshot、取消/继续和结果报告。可以选择世界内 resources.zip 或明确指定的外部 ZIP 中的语言文件。**应用 UI 目前只有韩语、英语、日语；此中文 README 不表示中文 UI 已实现。**

目前主要通过源代码运行开发版，需要 Python3.12、Node/pnpm、Rust 和各平台的 Tauri 环境。[开发步骤](development.md) · [详细使用说明](user-guide.md)

当前不翻译数据包、scoreboard、command storage、playerdata、level.dat 文本或文件夹式资源包。Bedrock、.mcr、.linear 和未知压缩格式不可写入。[合成 fixture 支持表](support-matrix.md)不保证支持所有版本和地图。

## 费用、数据与免责声明

应用没有购买、订阅或内购，但第三方 AI API、推理和重试可能收费。所选文本和翻译指令会发送到提供商或中转服务。估算不是实际账单上限，请检查提供商费用和数据政策。

桌面密钥默认采用本地加密 SQLite 和独立 key 文件，另可选仅会话或 OS 密钥链。同一账户下能读取两个文件的进程不在此保护范围内。[数据与密钥](privacy.md)

软件按 **AS IS** 提供，不保证准确性、兼容性、数据保全或持续支持。在适用法律允许的范围内，作者和贡献者的责任按 [MIT 原文](../LICENSE)限制；不能依法排除的责任不在豁免范围内。[完整免责与权利说明](disclaimer.md)

MIT 不授权第三方 Minecraft 游戏资产、地图、资源包或商标。未经原作者许可，不要重新发布翻译地图。

## 作者与许可

**김현민** — 制作、维护 · [mini0227kim@gmail.com](mailto:mini0227kim@gmail.com)

[Issues](https://github.com/kim0040/Minecraft-World-Translator/issues) · [贡献说明](../CONTRIBUTING.md)

项目源码保留原有 MIT；依赖分别遵循自身许可。正式二进制发布的完整第三方声明和平台检查仍待完成。[第三方声明](../THIRD_PARTY_NOTICES.md) · [文档目录](README.md)
