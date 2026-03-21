# Minecraft World Translator

[English](../README.md) | [한국어](./README.ko.md) | [日本語](./README.ja.md) | 简体中文

Minecraft World Translator 是一款专为 Minecraft 地图设计的桌面级翻译工具。它不仅能扫描并翻译地图维度文件（`.mca`）内的文本，还能翻译位于 `.zip` 压缩包资源包内的语言文件。

专为新手设计的工具：

- 您可以通过浏览器本地启动一个简洁易用的 Web UI 进行操作。
- 习惯命令行的用户也可以直接使用强大的 CLI。
- 您可以保留并直接应用原本的 `translate.py` 旧配置。
- 无需修改应用程序源代码，就可以在多个大语言模型（LLM）提供商之间无缝切换。

如果您有任何疑问、建议或报告错误，请联系：
`mini0227kim@gmail.com`

## 支持翻译的内容

- 告示牌上的文字
- 书本内容
- 书本标题及 `filtered_title`
- 实体与物品的自定义名称
- 物品描述（Lore）
- 位于 `tellraw`、`title`、`subtitle` 和 `actionbar` 命令中的内部文本
- 资源包（Resource Pack）内的 `lang/*.json` 文件（可选）

## 主要功能

- 包含简体中文（即将添加）、英文、韩文和日文界面的本地 Web UI
- 支持明亮与暗黑主题切换
- 对新手极其友好的操作流：强烈建议“先扫描（Scan Only）”后翻译
- 翻译开始前自动预估：文件数量、预计消耗 Token 和预计剩余时间 (Estimation)
- 支持多家主流 LLM 提供商：
  - `comet`
  - `openai`
  - `gemini`
  - `anthropic`
  - `openrouter`
  - 完全兼容 OpenAI 和 Anthropic 接口格式的自定义 API (Custom API)
- 支持手动输入模型名称，或智能获取对应 API 提供商的模型目录列表
- 提供翻译风格预设（Style Presets），并支持利用 AI 扩写简短风格提示
- 免费层 API 速率保护：支持限制 RPM（每分钟请求数）与 TPM（每分钟 Token 数）
- 完全继承 `translate.py` 中的 API Key、Base URL、模型以及遗留的风格提示
- 空转扫描模式（Dry-run）：确保不会误改文件即可预览操作更改
- 安全机制：写入覆盖原始数据前自动完成备份
- 每次执行结束后自动生成详细的 JSON 报告输出

## 项目文件结构

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

## 系统运行要求

- Python 3.11 或更高版本
- 需要连接互联网以用于调用 LLM API
- 拥有要使用的 API 提供商提供的有效 API Key
- （备份选项启用时）用来存放备份文件的可用硬盘空间

## 快速入门指南

为新手整理的最推荐安全操作流程：

1. 启动 Web UI 客户端。
2. 配置您的地图文件夹路径与 API 设定。
3. 一定要先用 `仅扫描 (Scan Only)` 测试一次并预览提取进度。
4. 如果读取的文本规模和内容确认没问题，再点击按钮进行实质翻译。

### Web UI 一键快速启动 (适用于 macOS)

在 macOS 上，您可以双击以下启动器文件一键启动本程序：

- [run_web_ui.command](./run_web_ui.command)

这个启动器会自动帮您：

- 自动配置 `.venv` 虚拟环境（如果不存在的话）
- 安装所需环境依赖包
- 检查后台，如果当前已有运行的实例则直接打开网页复用
- 即使默认端口号 `8765` 被占用，也能自动寻找下一个空闲端口
- 启动本地服务器
- 自动打开您的系统默认浏览器进入控制台页面

## 不同系统的安装指南

在启动工具前，您可以在本地文件夹内存放一个 `.env` 配置文件来安全存储自己的凭据：

```bash
cp .env.example .env
```

只需在里面填好你需要的那一栏环境变量即可。您的 `.env` 文件已被 Git 忽略配置文件屏蔽，因此您的私密密钥永远不会被意外上传（安全保证）。

### Windows

1. 在 [python.org](https://www.python.org/downloads/windows/) 安装版面下载并安装 Python 3.11 及以上版本。
2. 在项目根目录使用 PowerShell（管理员）或终端打开。
3. 运行如下指令：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

如果 PowerShell 拦截了虚拟环境激活脚本的执行，您可以临时降低允许级别：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

1. 确保系统支持 `python3` 调用。
2. 在项目下打开终端（Terminal）。
3. 运行如下指令：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

或者，您可以直接双击通过前文提到的启动器：

- [run_web_ui.command](./run_web_ui.command)

如果 macOS 的安全选项阻止了它的自动开启，您可以在它上面先点击鼠标右键，然后选择 `打开 (Open)` 让它强行通过安全过滤。

### Linux

1. 确保安装了 Python 3.11 或更新版。
2. 在项目目录下新建打开终端。
3. 运行以下操作：

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

在某些发行版上，如果没有装虚拟环境包，请提前使用此命令：

```bash
sudo apt install python3-venv
```

## 运行 Web UI 界面

如果您要在全手工模式下开启你的 UI 服务器端：

```bash
python3 webui_server.py
```

然后利用浏览器进入后台中心：

- `http://127.0.0.1:8765`

若要在启动时强制其唤醒浏览器进程：

```bash
python3 webui_server.py --open-browser
```

若想要更换局域网的接收主机地址或是端口号：

```bash
python3 webui_server.py --host 0.0.0.0 --port 9000
```

提示：如果使用了快捷启动器，当 `8765` 端口报错的时候它也会帮您寻找下一个备用端口开启服务。

### Web UI 运行控制台提供哪些主要展示信息

- 大语言模型（LLM）供应商直接选取菜单
- API Base URL 和使用模型的指定表单
- 模型全网云端名录一键智能检索（Model Catalog Lookup）
- 对简短的风格提示进行由 AI 协助的完整结构扩展
- 控制翻译作用范围的分组式详细设置
- 启用外挂资源包转换系统
- 当下翻译的全面实时进程与条状进度
- 目前锁定的交互区块及文件
- UI 控制后台即时的网络发信和保存动作交互展示
- 返回接收成功的翻译批量传输（Batch）块数统计
- 用于查错调试的结果 JSON 后台日志一览
- 用于寻求客服和开发协助支持的联系专区

## 使用命令行（CLI）直接启动功能

### 空转扫描模式（Dry Run 测试）

在不修改底层源文件的前提下安全获取统计资料：

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

### 实际写入与翻译

真正的覆写型实测模式：

```bash
python3 mc_world_translator.py --config config.example.toml
```

### 动态覆盖原配置文件中的模型预设

如果想不用修改文件而在 CLI 利用新平台强行替换 Provider：

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --provider openrouter \
  --model openai/gpt-4.1
```

### 调出选定平台可用模型列表检索清单

您可以查询在不一样的提供商那里能够直接发信使用的所有模型标识名称：

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

甚至可以在同一行快速插入临时设置的环境变量直接获取该公司的模型库：

```bash
python3 mc_world_translator.py --provider openai --api-key "$OPENAI_API_KEY" --list-models
python3 mc_world_translator.py --provider gemini --api-key "$GEMINI_API_KEY" --list-models
python3 mc_world_translator.py --provider anthropic --api-key "$ANTHROPIC_API_KEY" --list-models
python3 mc_world_translator.py --provider openrouter --api-key "$OPENROUTER_API_KEY" --list-models
```

### 通过扩展小短语实现长篇风格向导（Enhance Style Brief）

你可以用自己的母语输入短短的一行文字，程序会借助模型生成大片高质量的设定标准传达给真正的最终翻译进程：

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "氛围应该偏向中世纪恐怖，名字需要音译处理，且谜题暗示不能翻译的面目全非"
```

## 设置详解（Configuration）

主参考配置模板内容见：

- [config.example.toml](./config.example.toml)

### 全局（主）设定级选项 (Top-Level Settings)

- `world_dir`
  - 设定工具需要扫描以及修改对象所在的 Minecraft 地图游戏根录。
- `report_path`
  - 在运行结束阶段生成的 JSON 工作总结汇总输出路径。
- `dry_run`
  - 勾选与否则决定了核心转换是否只是在进行沙盒统计（不写改文件）。
- `backup`
  - 覆盖 `.mca` 等重要二进制块时，强制命令先拷贝留着备用副本的保护开关。
- `backup_suffix`
  - 生成上面说明的那个复刻版备份时挂在文件名末尾用来相互区分的尾号标签（通常为 `.bak_translate`）。
- `batch_size`
  - 合并多个句子的数组容量以进行批量翻译时，单次向 API 传输的独立字符串片段数量。
- `temperature`
  - 设定 LLM 温度值，温度越低翻译的语速内容更为集中、机器化与严谨化；较高的生成值会让其风格更随机也更活灵活现。
- `inherit_translate_py`
  - 保持兼容性用的开关。允许自动调用前身项目脚本的缓存配置。
- `translate_py_path`
  - 如果要继承原有脚本文本参数的话，旧设定文件所在的对应具体位置方向路线。

### API 接口及供应商参数配置

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

- `rpm_limit`: 限制每分钟内对服务器允许发起请求的最多次数 (Requests Per Minute)。它可以在使用免费通道遇到 429 报错机制的时候主动刹车、强制让进程休眠等待恢复。 `0` 表示不做拦截（开启无界限畅享调用）。
- `tpm_limit`: 限制每分钟允许的 Token 累计总量上限 (Tokens Per Minute)。通过预测单次通信包裹量与过去发出的体积计算智能迟滞时间，维护用户的配额指标。`0` 表示不被拦截（无界限畅享调用）。

#### 提供商选择种类 (Provider Values)

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`
- `custom_openai` (用于任何和 OpenAPI 通讯规范格式对齐的散户/第三方节点端)
- `custom_anthropic` (用于任何和 Anthropic API 格式完全相同的云侧路由接口)

#### 判定及取用 API Key 钥匙优先读取顺序规则说明

1. 位于对应 TOML 文本配置文件中的原始串代码（位于第一受信任排位）。
2. 在本机或系统环境变量中声明的值域。
3. 从过去保留开启前传的 `translate.py` 里读取继承的值（排在最末保护项）。

该支持所适配检索的运行环境内置变量有以下几个项：

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

所以很多时候只要使用 `.env` 环境脚本文件把对应账户名值固定存到该名称中，UI 就能不用手敲钥匙进行即插即用启动了。

### 语言风格与体系规范（Prompt 配置区）

```toml
[prompt]
target_language = "Chinese"
style_preset = "neutral"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - 使用我们常用的交流沟通语种标记您最终希望输出看到的界面语言标签。
- `style_preset`
  - 从项目默认支持的四五个主流文字腔调（例如：随和、正统讲究）中抽取底层逻辑提示词体系。
- `style_prompt`
  - 用户自行拼接在前方的预设体系之后单独加强补充的特定指示或者规则限制说明。
- `custom_system_prompt`
  - 当启用了这行，意味着上述的几个自带的提示流体框架格式会被全数无视推翻失效。系统直接按照您的此句最硬核指示运作系统机制。

### 定义操作范围 (Scan 设置区块)

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

可以由你把关在繁多的区块内容数据表里，究竟把哪一类的载体字库纳入工作转换机制内，关闭对应开关即是防漏安全与防污染的核心设置要领。

### 独立资源包内容对接应用

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "zh_cn.json"
skip_if_target_exists = false
```

如果您的整合包中带有自己的一套独立的资源材质包需要单独一并对应汉化或翻译语言内容，那么再启开该设置面板通道功能项。

#### 资源包选项开启及翻译方式的详尽指导说明：
1. 若你的材质包目前只是个纯粹解压展开的分装文件夹而已，请先利用桌面将它完整的变装成带 `.zip` 格式的压缩包裹形态。
2. 转回到工具的控制区域 UI，把这个资源压缩包 `.zip` 在您硬盘上的完整定位绝对路径录入进去通道里。
3. 把源头原始的参考模板指定好（通常材质库包一般会以类似 `en_us.json` 作为其主默认翻译文本名字体）。
4. 在下一栏位确立自己想要的终极生成覆盖所用的翻译后语言档案名字标签代码（例如：`zh_cn.json` 若要翻成简中语言包的话，或对应其它的繁中 `zh_tw.json`）。
5. 直接启动，系统就可以顺道把那段生成的翻译文档，完美重新打包封装回你的这个资源的 `.zip` 的特定对应分支 `assets/*/lang/` 子项，此过程中不会让任何里面的其余纹理或外观发生错误与崩塌变化。

## 最适合懵懂初级开发者的建议安全操作手法：

如果您面对成吨的文件架构完全不知道怎么动手才不留遗留风险的话，可谨守这个循序动作执行流转：

1. 打开我们引以为傲的 Web UI。
2. 选好用哪一家的引擎供给服务器，将口令填充并在 Model 项位明确使用的名称。
3. 丢入世界游戏存档夹路径链接。
4. 除非特别执着某种二次元扮演与语调气氛感，否则优先就让 Style Preset 停驻在最平庸标准的 `neutral (平白语态)`。
5. 这个绝对不要忘：开启最神圣的护城河保护选项 —— “修改前安全备份 (`backup`)”。
6. 动手第一个点选的一定必须是仅检测不出格的 “空转预览扫描 `Scan Only`” 执行探温动作。
7. 在它输出完整过程总结日志页面后查询进度框，看收集到的字符、物品文本是不是预估该有的对象。
8. 审查这步预判统计与模型测试确认无误匹配目标以后，再按大实操修改生效翻译处理真正的流程进行转换。

## 开发及硬核技术性内务机制解构

- 主转换的核心是使用对二进制的底层 `NBT` 数据节点解析的逆向注入手段来进行，它递归翻阅了存到 `.mca` 内的重重块区区块信息记录网络表。
- 为了保证不会将命令操作给全数瘫痪，系统只会主动向精准命中的人机交流文字界面属性参数里提取数据体。
- 如果它被探测出像类似 `/kill @p` 这等纯内部原生程序触发控制机制脚本句码结构，将被有选择地放逐略过不作为对象计算考量范围处理。
- 对应于刚才提到的资源文本包翻译流，实际上只关注位于 zip 包内且具有 `lang/*.json` 结尾特点的目标去实行翻译抓取置换。
- 处理不同 AI 各异的模型返回格式请求发信包格式与防范通信差集特征封装被统一解耦实装在控制中枢组件源 [llm_backends.py](./llm_backends.py) 实现。
- 虽然叫 Web UI，但是程序实际上是在本机自己的局域端口内进行的直接连结，不会让客户端用户您的安全游戏资料传到我们的外部三方非关联云服务器托管储存泄漏。

## 保证数据不被破坏的守护规则红线

- 未正式确定一切正确度走向的大型执行覆辙启动以前，永远确认自己把 Backup 控制项启用了没有。
- 若此时您试图触及或去修修改改珍贵的个人老旧珍藏存档数据体时，极其建议人工手动从别处复印留置下备份后对那份试验克隆品动手进行测控修正。
- 只有通过扫描（Scan/Dry run）的评估与判定才是决定真正上阵的重要核心关节点。
- 对其大加设定过于强烈的行文、限制太多过于变造文韵的古怪世界观风格指令，其实反而有可能非常严重地毁掉和颠覆里面需要严格解密的通关关键名词结构信息与通缉令重要标识点位描述，故在风格的定名使用时需要绝对极其的谨慎调配掌握。
- **关于代码库的重要声明：** 由于本项目正在快速朝着完整的 Version 1 世代迭代优化演进之中，程序库可能在局部分支区域中仍然潜伏存留有此前未清除干净用来调试的测试实验级残存逻辑记录特征或是冗余废代码留置踪迹（Legacy code leftovers）。

## 遇到未明意外障碍时的系统查错对策中心（Troubleshooting）

### 当您目击到 `API key is missing` 不存在的错误报错提示发生弹窗时

务必请排查下面是否存在你的填写真实凭据值疏漏或是错误配置等异常没接上的问题要素发生地：

- 审视在您当前挂接所在的 UI Web 操作平台上的表单有没有按实际打字输入过该类字码信息。
- 看一看放在启动处的 `config.example.toml` 中是否预留有了空栏没正确存入。
- 系统的全局大环境参数列表中存在没有（没成功写入环境值变量列表中）。
- 或者是使用了遗留老架构去调用翻译机制的 `translate.py` 中的参数栏里未配置正确。

### 弹出了 `Model is missing` （无明确指向该调遣的模型项目代号）错误反馈

这个必须指定，千万不可空置这部分名称栏。如果不知该怎么办的话可以按下列表搜集查询参数指令 `--list-models`，借此从云端取得当前接口拥有提供服务的名字索引以填入进去指定位置进行驱动。

### 如果那控制网页 UI 完全弹不起来死活进不去

- 翻找黑框终端后的运行反应情况，它那有没弹红色的异常信息报错停止反应了没有。
- 自己查验地址框是否正在正经访问到了正确的指向路径 `http://127.0.0.1:8765`。
- 去后台看看有没有那些迅雷、各种乱七八糟其它工具也同时默认把该用于监听控制通讯的 `8765` 这个特别通道也给全全封死霸占垄断住通道了，让工具再指定个通道。

### 返回生成的最终翻译成品文章简直粗鲁狂野过头不知所云胡诌出来甚至带嘲讽口语等极端离谱内容

通过采取下列综合干预手段尝试将 AI 逻辑的走偏行为拉近制约到温和状态框架内解决发散难题。

- 第一招是迅速将系统参数上提供的风格默认值拨动改变调回归平缓语感的预存组，如用 `neutral（老实本份正经型翻译模式）` ，或者是使用 `polite（极其友善尊敬型翻译模式）`去代替掉。
- 第二个招式是再你启动那系统协助短语一键拓写扩张大段向导词体系的功能（AI-assisted expansion）的时候，您输进去的要求语气务必更克制与精准点才行。
- 如果前两个还压制不住机器暴乱的话，那就只能使出终结大招利用自己直接接管的统摄设置，启动那能凌驾和无情压制一切原始系统提示语参数的高强命令强制管控配置槽点也就是调用： `custom_system_prompt` 这个来对系统施行全绝对统治替换掌控去逼迫其正常输出。

### 在使用大 Windows 系统自带激活外来运行脚本动作产生阻截的拦截权限麻烦错误

如果您的环境启动因为系统内建的强悍保安控制动作停止发生阻滞并弹报没权限运作开启指令信息时，则需要直接开 PowerShell 来对这道关卡权限去做出临时突破绕过。

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 咨询开发及相关功能协力协助支持体系获取解答求教

有对于机制不明白、遇上了诡异致命恶性逻辑崩溃阻滞或是有了非常优秀天马行空想要改进加入的特性等奇思妙想意见。都可以顺畅提交信息直接沟通对接。

- `mini0227kim@gmail.com`

而在去呈交相关意见与报错报告问题时，能带上以下几样详列说明附件和情况阐述会有利于极快大幅缩减修整除掉问题的确认判定周期：

- 使用操作的时候运行依靠在什么类别的核心系统基架下进行的操作过程（比如使用 MacOS 等系统记录信息项等）。
- 选择在呼叫启动的那一家背后提供提供发信算力的特定 API 供应商。
- 具体指向调遣命令工作翻译的明确全名代号所应用之模型叫什么。
- 出发错误事件的点是停留在手敲黑底白字的操作层端去发动的还是走入使用控制 UI 可视网页系统下崩溃引起的？
- 最后最重要的必附项目即附带那原封不动复印下来的那些导致抛出各种各样异常红字大异常错误的记录文本报告原文部分（如有截下发生报错的段落最好全贴上去附赠检查最好）。

## 免责声明与知识产权使用授权说明协议参考条款

这份全开放代码构建完成并公开流派传出的本开源主系列工具相关内容一切所衍生全部使用许可均处于基于 MIT License 法则条款之下运作生效的体系中进行授权和运转声明的完全免费共享物。

更多有关具体的权利保障条约明细部分详细参看以下位置文档档案内容内：

- [LICENSE](./LICENSE)
