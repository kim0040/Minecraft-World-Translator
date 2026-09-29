# PomiTranslate

World Translator for Minecraft（我的世界存档翻译工具）

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.
（非 Minecraft 官方产品。未经 Mojang 或 Microsoft 批准，亦与其无任何关联。）

在翻译存档之前，请务必进行备份。PomiTranslate 将直接向您所选定的存档文件写入翻译内容。

您选择翻译的文本将发送至所配置的 AI 提供商 API，可能会产生相应的使用费用。

PomiTranslate 不包含任何购买项、订阅或应用内付费。

![PomiTranslate 标识](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | 简体中文

PomiTranslate 是一款专为 Minecraft Java 版设计的免费开源本地工具，用于安全提取和翻译世界存档中对玩家可见的文本内容。项目吉祥物为 Pomi，代码仓库标识符保留为 `Minecraft-World-Translator`。

无论是游玩海外高质量冒险地图、自定义 RPG 剧情、解密密室，还是大型多维度服务器世界，PomiTranslate 都能帮助玩家和地图作者消除语言障碍，获得原生般的沉浸体验。命令行工具与原生桌面应用（基于 Tauri）均通过轻量级封装的 JSONL 子进程共享同一套高性能 Python 翻译核心，且绝不开启任何外部监听端口。

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

---

## 核心设计理念与安全保障

Minecraft 世界存档以高度复杂的 NBT（Named Binary Tag）树状结构保存在成千上万个区块和区域文件中。粗糙的正规表达式替换或不完善的 NBT 编码器极易导致坐标头损坏、自定义命令逻辑失效以及不可逆的数据破坏。PomiTranslate 严格遵循以下数据完整性准则：

- **字节级 NBT 完整性保留**：未经修改的区块在 SHA-256 哈希值上与原文件保持完全一致。当翻译文本时，系统绝不重新序列化周边标签，仅针对修改后的 Java Modified UTF-8 字符串载荷进行原地精准替换（In-place update）。
- **游戏格式代码与语法严密保护**：内置验证引擎实时监控 Minecraft 颜色/样式代码（`§a`, `§l`, `§r`）、换行转义（`\n`）、格式化占位符（`%s`, `{0}`）、JSON 组件结构以及命令目标选择器（`@a`, `@p`）。若 AI 返回内容破坏了语法，系统将自动保留原文并记录提示，杜绝游戏内渲染崩溃。
- **Scan-First（预扫描优先）架构**：Scan Only 模式将在完全不调用外部 API、不修改任何存档文件的前提下，提取跨维度的所有文本，进行全局去重并生成结构化扫描方案。
- **Java session.lock 活跃锁定检测**：在执行任何写入操作前，系统会自动检查世界文件夹内的 `session.lock`。若游戏客户端或服务器正在运行该存档，写入将被立即安全拦截。
- **带版本控制的原子备份与安全恢复**：在写入发生前，系统会在系统应用数据目录中创建经过验证的多文件备份集。即使发生网络异常，也不会残留任何半写入状态，且恢复前状态亦会被完整保存为应急快照。

![预先扫描](../assets/illustrations/docs/doc_scan_first_zh_v1.png)

---

## 支持提取的游戏内文本组件

系统全面扫描主世界、下界（`DIM-1`）、末地（`DIM1`）以及自定义数据包维度，精准提取以下要素：

| 组件分类 | 游戏内目标元素 | 提取与处理特性 |
| :--- | :--- | :--- |
| **告示牌 (Signs)** | 站立、悬挂及墙面告示牌 | 完美支持 1.8 至 1.19 版本的传统单面告示牌文本，以及 1.20+ 版本的最新双面告示牌（正面与背面 `messages`） |
| **书本 (Books)** | 书与笔、成书 | 完整翻译书名、过滤后书名、作者信息，以及包含纯文本或复杂 JSON 组件的各页面内容 |
| **物品元数据** | 武器、工具、防具、自定义物品 | 提取自定义显示名（`display.Name`）、说明文字（Lore）、1.20.5+ 新版物品组件（`minecraft:custom_name`, `minecraft:lore`）以及悬浮/点击事件内容 |
| **容器方块** | 箱子、潜影盒、木桶、熔炉等 | 读取容器自定义名称，并递归扫描所有内部储物槽位中的嵌套物品 |
| **实体与方块** | 生物、NPC、盔甲架、自定义方块 | 提取生物实体的自定义名称（`CustomName`）、盔甲架文本以及带名称的方块实体数据 |
| **展示实体** | 文本展示实体 (`text_display`) | 全面支持 1.19.4+ 引入的文本展示实体及其广告牌文本组件 |
| **命令方块** | 脉冲、循环、连锁命令方块 | 精准提取 `/tellraw`、`/title`、`/subtitle`、`/actionbar` 命令，以及通过 `execute ... run` 深度嵌套的子命令文本，坐标与目标选择器保持原样 |
| **存档内资源包** | 世界文件夹内的 `resources.zip` | 启用后可同时扫描并翻译内嵌客户端语言文件（`assets/<namespace>/lang/*.json` 或 `.lang`），并与区域文件统一归入同一套备份管理 |

---

## 区域文件与格式兼容性

仅当格式通过了严格的自动化测试夹具验证后，系统才允许写入：

### 官方支持格式
- **区域文件标准**：Minecraft Java 版 Anvil 格式（`.mca`）及实体存储文件夹（`entities/*.mca`）
- **区块压缩算法**：Gzip、Zlib、未压缩（Uncompressed）及 Minecraft 1.20.5+ LZ4（`LZ4Block`）
- **外部溢出分块**：用于存储大体积超额数据的外部 `.mcc` 文件（`c.<x>.<z>.mcc`）
- **目录布局支持**：原生单人世界、自定义数据包维度文件夹，以及共享 `level.dat` 的 Paper/Spigot 多世界分立文件夹

### 不受支持的格式（检测到时自动禁止写入）
为确保数据万无一失，一旦检测到以下格式，系统将立刻永久锁定为只读状态：
- **基岩版世界 (Bedrock)**：基岩版存档结构或 Mojang LevelDB（`.ldb`）文件
- **Anvil 之前的旧版格式**：1.2 版本以前的遗留 `.mcr` 区域文件
- **第三方压缩格式**：部分第三方服务器使用的 Zstandard 压缩 `.linear` 格式
- **未知或损坏的压缩算法**：无法识别的压缩标识头（包括压缩类型 127）

详情请参阅通过自动化测试生成的 [support-matrix.md](support-matrix.md)。

![不支持格式中止](../assets/illustrations/docs/doc_unsupported_zh_v1.png)

---

## 支持的 AI 提供商与系统密钥链安全

PomiTranslate 原生支持以下主流语言模型平台：
- **OpenAI**：GPT-4o、GPT-4o-mini 及兼容聊天模型
- **Anthropic**：Claude 3.5 Sonnet、Claude 3.5 Haiku、Claude 3 Opus
- **Google Gemini**：Gemini 1.5 Pro、Gemini 1.5 Flash、Gemini 2.0 Flash
- **OpenRouter**：一站式接入数百种优质开源及商用语言模型
- **Custom (本地/私有兼容端点)**：支持 Ollama、vLLM、LM Studio 等符合标准 OpenAI Chat 或 Anthropic Messages 协议的本地推理框架

在执行翻译前，系统会预先查询服务商的在线模型目录，核验模型存在性及上下文额度。目录中不存在的模型将在修改存档前被安全中止。

### 操作系统级密钥链安全
API 密钥绝不以明文形式保存于 `settings.json`、SQLite 文件、运行日志或 Git 提交记录中：
- **macOS**：Apple Keychain Services (`PomiTranslate`)
- **Windows**：Windows 凭据管理器 (`PomiTranslate`)
- **Linux**：Freedesktop Secret Service (DBus)

存储的密钥仅在分批翻译执行时通过子进程标准输入（stdin）传入内存，用户可在设置面板中随时单独删除。

用户设置配置文件路径：
- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate/settings.json`（或 `~/.local/share/PomiTranslate/settings.json`）

![API通知](../assets/illustrations/docs/doc_api_notice_zh_v1.png)

---

## 三阶段翻译工作流

```
[第一阶段: Scan Only (预检扫描)]
世界文件 (.mca) ──> 提取文本 ──> 全局去重 ──> 扫描计划与世界指纹
(API 请求 0 次，只读安全分析，支持候选搜索、过滤排除及手动校对)

[第二阶段: 批量并发翻译]
唯一候选文本 ──> 速率限制与熔断器 ──> AI 提供商 ──> 校验保存检查点
(严格保护格式代码，遇到连续错误自动保护性中止，断点自动续传)

[第三阶段: 原子级写入]
校验备份 ──> session.lock 锁定检查 ──> 补丁写入区域文件 ──> 完成
(字节级精准 NBT 替换，恢复前保留防护快照，支持一键安全还原)
```

---

## 快速上手 (CLI)

命令行运行推荐使用 Python 3.12 环境。（使用发行版桌面应用的用户无需安装 Python 或任何开发工具。）

```bash
# 配置虚拟环境
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 1. Scan Only (无 API 消耗安全提取)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --dry-run \
  --report-path ./scan-report.json
```

### 2. 执行世界翻译 (基于扫描指纹安全运行)
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --target-language "zh" \
  --provider openrouter \
  --model "anthropic/claude-3.5-sonnet" \
  --style story \
  --expect-fingerprint "<扫描报告中的指纹>"
```
*提示：若省略 `--api-key`，系统将自动使用已安全存入 OS 密钥链中的 API 密钥。*

### 3. 从备份还原世界
```bash
python mc_world_translator.py \
  --world-dir "/path/to/minecraft/saves/MyWorld" \
  --restore-backup
```

![写入前备份](../assets/illustrations/docs/doc_backup_first_zh_v1.png)

---

## 原生桌面应用

基于 Tauri 2 与 Svelte 5 构建的桌面客户端提供直观且现代化的用户体验：

- **多语言界面即时切换**：独立于翻译目标语言，随时切换简体中文、英文、韩文、日文显示界面。
- **候选文本校对表格**：直观查看提取文本的频次、坐标与方块/实体 ID，支持自定义排除翻译或录入人工翻译。
- **请求次数与成本预估**：在发送请求前清晰展示批处理估算请求次数与 Token 开销范围。
- **协作式取消与无损恢复**：取消时不会破坏存档数据，断点记录可自动接着翻译未完成条目。
- **历史备份管理器**：查看每次翻译生成的版本快照与文件改动清单，一键安全回滚。

### 从源码编译桌面应用
```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```

---

## 翻译风格预设

根据地图主题自由选择 6 种本地化风格：
- **标准 (`neutral`)**：客观、精准、平衡，适合普通生存世界与通用功能地图
- **自然对话 (`casual`)**：口语化自然表达，适合剧情对话丰富的角色互动与小游戏
- **庄重典雅 (`formal`)**：用词严谨、文雅端庄，适合历史古迹、碑文、日志记录
- **礼貌客气 (`polite`)**：亲切得体的敬语表达，适合教学向导、系统提示、任务引导
- **小说故事 (`story`)**：富于文学渲染力的史诗叙事风貌，极大增强奇幻冒险地图代入感
- **自定义 (`custom`)**：自由填写特定世界观规则、专有名词对照或特殊翻译要求

---

## 自动化测试运行

```bash
# 核心功能回归测试
.venv/bin/python test_core.py

# 格式夹具验证（压缩、NBT、会话锁、还原）
.venv/bin/python tests/test_release_fixtures.py

# 提供商 API 与密钥链设置测试
.venv/bin/python tests/test_providers.py

# 品牌规范与隐私防泄漏测试
.venv/bin/python tests/test_brand_secrets.py

# 桌面端侧车进程协议测试
.venv/bin/python tests/test_desktop_entry.py

# 前端单元测试
./node_modules/.bin/vitest run
```

---

## 咨询与反馈

- 问题反馈与功能建议：`mini0227kim@gmail.com`
- 提交反馈时请提供操作系统、所用提供商、模型名称以及相关日志记录。（请切勿提供您的私密 API 密钥。）

---

## 开源许可

PomiTranslate 基于 [MIT 许可协议](../LICENSE) 开源。
