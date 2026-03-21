# Minecraft World Translator

[English](./README.md) | 한국어 | [日本語](./README.ja.md) | [简体中文](./README.zh.md)

Minecraft World Translator는 마인크래프트 월드를 데스크톱에서 손쉽게 번역할 수 있는 도구입니다. 월드의 리전(region) 파일(`.mca`) 내부를 스캔하며, zip 아카이브 내에 포함된 리소스팩의 언어 파일 또한 번역할 수 있습니다.

이 프로젝트는 초보자를 최우선으로 고려하여 설계되었습니다:

- 브라우저 기반의 로컬 UI를 통해 실행할 수 있습니다.
- 원한다면 CLI(커맨드 라인 인터페이스) 환경에서도 사용 가능합니다.
- 기존의 `translate.py` 설정을 그대로 유지하고 적용할 수 있습니다.
- 앱 코드를 수정하지 않고도 다양한 LLM 공급자를 자유롭게 전환할 수 있습니다.

문의 사항이나 오류가 발생한 경우 아래로 연락해 주세요:
`mini0227kim@gmail.com`

## 번역 지원 항목

- 표지판 텍스트
- 책 내용
- 책 제목 및 `filtered_title`
- 커스텀(사용자 지정) 이름
- 아이템 이름 및 설명(Lore)
- `tellraw`, `title`, `subtitle`, `actionbar` 내부의 텍스트
- 리소스팩 내 `lang/*.json` 파일 (선택 사항)

## 주요 기능

- 한국어, 영어, 일본어를 지원하는 로컬 웹 UI
- 라이트 및 다크 테마 지원
- '스캔 먼저 실행'을 권장하는 초보자 친화적 워크플로우
- 번역 전 예상 파일 수, 토큰 및 소요 시간 예측 (Estimation)
- 다양한 LLM 공급자 지원:
  - `comet`
  - `openai`
  - `gemini`
  - `anthropic`
  - `openrouter`
  - OpenAI 및 Anthropic 형식과 호환되는 커스텀 API 엔드포인트 지원
- 수동 모델 입력 및 선택한 공급자의 모델 카탈로그 조회 기능
- 프롬프트 스타일 프리셋 및 AI 기반 스타일 메모 자동 확장
- 무료 티어 API 사용자를 위한 RPM/TPM 제한 설정 지원
- API 키, 기본 URL, 모델 및 기존 프롬프트에 대한 `translate.py` 상속 지원
- 변경 사항을 미리 확인하는 스캔 전용 모드(Dry-run) 지원
- 변경 사항 적용 전 백업 지원
- 실행이 끝난 후 JSON 형식의 상세 리포트 출력

## 프로젝트 파일 구조

```text
minecraft-world-translator/
├── LICENSE
├── README.md
├── README.ko.md
├── README.ja.md
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

## 시스템 요구 사항

- Python 3.11 이상
- LLM API 호출을 위한 인터넷 연결
- 사용하려는 공급자의 유효한 API 키
- 백업 파일을 저장할 수 있는 충분한 디스크 여유 공간

## 빠른 시작

초보자에게 가장 추천하는 간단한 방법입니다:

1. 웹 UI를 엽니다.
2. 월드 경로와 API 설정을 입력합니다.
3. 먼저 `스캔만 실행 (Scan Only)`을 작동시킵니다.
4. 결과가 문제없어 보인다면, 실제 번역을 실행합니다.

### 가장 빠른 웹 UI 실행 (macOS)

macOS에서는 다음 파일을 더블 클릭하여 바로 실행할 수 있습니다:

- [run_web_ui.command](./run_web_ui.command)

이 런처는 다음 작업을 자동으로 수행합니다:

- `.venv` 가 없다면 새로 생성
- 필요한 패키지(dependency)가 없다면 설치
- 이미 실행 중인 로컬 UI가 있다면 재사용
- `8765` 포트가 사용 중이면 다음으로 사용 가능한 포트 자동 선택
- 로컬 웹 서버 시작
- 시스템 기본 브라우저 자동 실행

## 설치 방법

도구를 실행하기 전에, 다음과 같이 로컬 `.env` 파일을 준비해 두시면 편리합니다:

```bash
cp .env.example .env
```

그런 다음 문서 내에서 필요한 키값만 채워주세요. `.env` 파일은 Git에 업로드(추적)되지 않으므로 안전합니다.

### Windows

1. [python.org](https://www.python.org/downloads/windows/)에서 Python 3.11 이상의 버전을 설치합니다.
2. 프로젝트 폴더에서 PowerShell을 엽니다.
3. 다음 명령어를 실행합니다:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

만약 PowerShell이 스크립트 실행(Activation)을 차단한다면, 일시적으로 로컬 스크립트 실행을 허용할 수 있습니다:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

1. `python3` 가 설치되어 있는지 확인합니다.
2. 프로젝트 폴더에서 터미널을 엽니다.
3. 다음 명령어를 실행합니다:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

또는 다음 런처를 사용할 수 있습니다:

- [run_web_ui.command](./run_web_ui.command)

만약 macOS 자체에서 런처 실행을 차단한다면, 해당 파일을 우클릭한 후 `열기(Open)`를 한 번 눌러주시면 됩니다. 기본 포트인 `8765`가 이미 사용 중이라면, 런처가 자동으로 다른 사용 가능한 포트를 찾아 실행합니다.

### Linux

1. Python 3.11 버전 이상이 설치되어 있는지 확인합니다.
2. 프로젝트 폴더에서 터미널을 엽니다.
3. 다음 명령어를 실행합니다:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

일부 배포판의 경우 아래 명령어가 추가로 필요할 수 있습니다:

```bash
sudo apt install python3-venv
```

## 웹 UI 실행 방법

로컬 UI 서버 시작:

```bash
python3 webui_server.py
```

주소창에 입력:

- `http://127.0.0.1:8765`

브라우저 창을 자동으로 열며 실행하려면:

- `python3 webui_server.py --open-browser`

호스트 이름과 포트 번호를 변경하려면:

- `python3 webui_server.py --host 0.0.0.0 --port 9000`

원클릭 런처 사용 시 기본 포트가 이미 사용 중이라면, 기존에 열려 있는 UI에 재연결하거나 빈 포트로 자동으로 전환하여 실행합니다.

### 웹 UI 화면 구성 항목

- 공급자 선택
- API Base URL 및 모델 설정
- 모델 카탈로그 목록 조회 버튼
- 짧은 스타일 메모 작성 및 AI 자동 확장
- 범위(Scope) 설정 관련 컨트롤 그룹
- 리소스팩 관련 설정
- 실시간 작업 진행 상태 표시
- 현재 작업 중인 파일 명시
- 현재 활동 유형 단계 표시
- 번역된 배치(Batch) 작업 개수 집계 표시
- 작업 결과물을 담은 Result JSON 뷰어
- 문의처 이메일 패널

## CLI 실행 방법

### 테스트 모드 (Dry Run)

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

### 실제 번역 실행

```bash
python3 mc_world_translator.py --config config.example.toml
```

### 공급자 및 모델 강제 지정

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --provider openrouter \
  --model openai/gpt-4.1
```

### 사용 가능 모델 목록 조회

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

공급자를 직접 지정하여 사용할 수 있는 명령어 예시입니다:

```bash
python3 mc_world_translator.py --provider openai --api-key "$OPENAI_API_KEY" --list-models
python3 mc_world_translator.py --provider gemini --api-key "$GEMINI_API_KEY" --list-models
python3 mc_world_translator.py --provider anthropic --api-key "$ANTHROPIC_API_KEY" --list-models
python3 mc_world_translator.py --provider openrouter --api-key "$OPENROUTER_API_KEY" --list-models
```

### 스타일 메모 자동 확장 (Enhance)

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "고딕 공포 풍 톤 유지, 이름은 음역하기, 퍼즐 힌트는 가급적 직관적으로"
```

## 환경 설정 (Configuration)

예제 파일 경로:

- [config.example.toml](./config.example.toml)

### 최상위 항목 설정 (Top-Level Settings)

- `world_dir`
  - 번역 대상인 마인크래프트 월드 폴더 경로
- `report_path`
  - 리포트가 저장될 JSON 출력 경로
- `dry_run`
  - `스캔만 실행` 옵션 (실제 파일 쓰기를 하지 않음)
- `backup`
  - 실제 쓰기 전 백업 파일 생성 여부
- `backup_suffix`
  - 백업 복사본에 사용될 파일 확장자
- `batch_size`
  - 한 번에 전송할 문자열 배치 사이즈
- `temperature`
  - 언어 모델의 Temperature 값
- `inherit_translate_py`
  - 기존 `translate.py` 파일의 값을 불러와 재사용할지 여부
- `translate_py_path`
  - 레거시(기존) 설정 파일의 경로

### API 설정 섹션

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

- `rpm_limit`: 분당 최대 API 호출 횟수(Requests Per Minute)를 제한합니다. 무료 API 사용 시 설정한 횟수를 넘지 않도록 자동으로 요청 간격을 조절합니다. `0`은 시스템의 최대 속도로 진행된다는 의미입니다(제한 없음).
- `tpm_limit`: 분당 토큰 사용량(Tokens Per Minute)을 제한합니다. 배치(Batch)의 예상 토큰량을 계산하여 한도를 넘지 않도록 보호합니다. `0`은 제한 없음을 의미합니다.

#### 적용 가능한 공급자 (Provider Values)

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`
- `custom_openai` (UI를 통한 오픈 API 호환 포맷 지원)
- `custom_anthropic` (UI를 통한 Anthropic 호환 포맷 지원)

#### API 키 탐색 순서 (API Key Resolution Order)

1. TOML 설정 파일 내부의 값을 가장 우선시합니다.
2. 공급자별 고유 환경변수를 탐색합니다.
3. 상속이 켜져있을 경우 `translate.py` 안의 값을 탐색합니다.

지원하는 운영 환경변수 목록:

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

시스템 셸 대신 로컬 `.env` 파일에 저장해서 사용하는 것도 가능합니다.

### 프롬프트 설정 섹션

```toml
[prompt]
target_language = "한국어"
style_preset = "neutral"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - 사람이 알아볼 수 있는 대상 언어 이름 지정
- `style_preset`
  - 기본 번역 분위기 프리셋 설정
- `style_prompt`
  - 프리셋 뒤에 덧붙여질 추가 스타일 관련 요구 사항
- `custom_system_prompt`
  - 기본 제공 프롬프트와 프리셋을 전부 덮어쓸 전체 시스템 프롬프트 (강제 교체)

### 스캔 범위 섹션

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

이 섹션을 설정하여 정확히 어느 텍스트들을 번역의 대상으로 삼을 것인지 지정할 수 있습니다.

### 리소스팩 섹션

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "ko_kr.json"
skip_if_target_exists = false
```

번역하고자 하는 리소스팩 압축파일(zip) 내부의 언어 파일까지 처리하고자 할 때만 이 설정들을 켜주세요.

#### 리소스팩 번역 기능 사용 방법:
1. 대상 리소스팩이 폴더 형태라면 먼저 `.zip` 파일로 압축하세요.
2. 웹 UI에서 이 `.zip` 파일의 절대 경로를 입력란에 작성합니다.
3. 리소스팩이 기준 언어로 채택하고 있는 원본 파일명(주로 `en_us.json`)을 넣습니다.
4. 번역 결과를 저장할 새로운 목표 언어 파일명(예: `ko_kr.json`)을 지정합니다.
5. 번역을 실행하면 프로그램이 텍스처 파일들은 건드리지 않고, 내부의 `assets/*/lang/` 경로에 안전하게 번역된 새 JSON 파일들을 주입해 줍니다.

## 초보자를 위한 추천 작업 순서

개발 도구에 익숙하지 않거나 마인크래프트 월드 구조를 모르는 경우 다음을 권장합니다:

1. 웹 UI를 실행합니다.
2. 사용하려는 공급자, API 키, 사용할 모델을 기입합니다.
3. 월드의 폴더 경로를 입력합니다.
4. 더 강한 문체나 개성이 필요하지 않다면 프롬프트 스타일 프리셋은 `neutral (평범하게)`로 유지합니다.
5. 먼저 `스캔만 실행`을 눌러 작동시킵니다.
6. 스캔이 끝나면 결과물이나 진행 패널의 기록들을 점검해 봅니다.
7. 백업 옵션은 끄지 말고 무조건 켜둡니다.
8. 스캔을 통해 추출된 데이터가 정상적일 때, 그때 실제 번역 본 작업을 실행하시면 됩니다.

## 기술적인 내용

- 월드 번역은 `.mca` 압축 파일을 까서 그 안의 NBT 데이터를 수정하는 방식입니다.
- 인식할 수 있는 사용자 노출 텍스트 부분만을 찾아 덮어씁니다.
- `/kill @p` 와 같이 마인크래프트 순수 명령어처럼 보이는 구문은 고의적으로 스킵시킬 수 있습니다.
- 리소스팩 번역은 zip 파일 안에 들어있는 `lang/*.json` 파일에 동작합니다.
- 공급자마다 요구하는 API 포맷에 대한 차벽 대응 처리는 [llm_backends.py](./llm_backends.py) 에 정의되어 있습니다.
- 제공되는 웹 UI는 클라우드 기반 웹앱 형태가 아닌, 컴퓨터 내부에서 돌아가는 구조입니다.

## 주의 사항

- 첫 번째 메인 실행 전에는 항상 백업 옵션이 켜져 있는지 확인하세요.
- 만약 중요한 맵을 손대고 있다면, 되도록 원본보다 복사본 위에서 테스트하세요.
- 실제 번역 실행에 앞서 `스캔만 실행` 테스트를 먼저 돌려보시길 권장합니다.
- 너무 디테일하고 강한 스타일 프롬프트는 아이템의 고유명사를 망치거나 퍼즐의 힌트를 숨겨버릴 우려가 있으니 신중하게 사용하세요.
- **코드베이스 참고 사항:** 이 프로젝트는 빠른 속도로 버전 1을 향해 개발되었기 때문에, 일부 모듈 내부에 개발 초기 테스트에 사용된 레거시(잔재) 코드나 사용되지 않는 실험적 논리가 남아있을 수 있습니다.

## 문제 발생 및 해결 방안

### `API key is missing` 에러 발생 시

다음 중 한 곳에라도 올바른 키를 세팅해 주세요:

- 웹 UI 페이지 입력란
- `config.example.toml`
- 사용자 환경 변수 (env)
- 또는 `translate.py` 파일 속 내용

### `Model is missing` 에러 발생 시

직접 사용할 모델을 시스템 프롬프트나 입력칸에 기입하거나 `--list-models` 명령어를 사용하여 모델 목록을 확인하세요.

### 웹 UI가 전혀 안 열려요

- 콘솔 뒤쪽에서 서버가 올바르게 실행 중인지 점검하세요.
- `http://127.0.0.1:8765` 주소가 맞는지 확인하세요.
- 혹시 시스템 안의 다른 앱이 `8765` 포트를 사용 중인지 체크하세요.

### 번역체가 너무 오만하거나/거칠게 나올 때

다음 방법을 복합적으로 사용해 보세요:

- 프리셋을 `neutral (평범)`이나 `polite (친절한 존댓말)`로 바꿉니다.
- 짧은 스타일 메모 보강(확장) 사용 시 조금 더 세세하게 작성하세요.
- `custom_system_prompt`로 완전히 통제가 가능한지 확인하세요.

### Windows 스크립트 실행 오류 발생 (Activation)

아래 명령어를 통해 Windows PowerShell의 보안 설정 스크립트 블락을 통과시킬 수 있습니다:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 문의 및 지원

기타 기능 관련 질문, 버그 및 오류 보고사항은 아래로 연락해 주세요:

- `mini0227kim@gmail.com`

보고 시 다음 내용을 포함해 주시면 문제 해결이 수월해집니다:

- 사용 중인 운영체제(OS)
- 사용하는 API 공급자의 종류 (OpenAI, Gemini 등)
- 사용 중인 모델 이름
- CLI 또는 웹 UI 중 어느 것을 구동 중 겪은 문제 인지
- (있다면) 표출되는 오류 메시지의 내용 등

## 라이선스

본 프로젝트의 라이선스는 MIT License를 따릅니다.

자세한 내용은 다음을 참고하세요:

- [LICENSE](./LICENSE)
