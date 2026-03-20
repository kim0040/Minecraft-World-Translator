# Minecraft World Translator

마인크래프트 월드 파일(`.mca`) 안에 들어 있는 텍스트와 선택적으로 리소스팩 언어 파일까지 번역하는 범용 번역기다.

이 도구는 다음 같은 텍스트를 대상으로 잡는다.

- 표지판 문구
- 책 페이지
- 책 제목과 `filtered_title`
- 커스텀 이름
- 아이템 이름과 Lore
- `tellraw`, `title`, `subtitle`, `actionbar` 내부 텍스트
- 리소스팩 `lang/*.json` 파일

## 특징

- API 키, `base_url`, 모델을 설정 파일이나 CLI 인자로 지정 가능
- 대상 언어를 자유롭게 변경 가능
- 말투/스타일 프리셋 지원
  - `dcinside`
  - `neutral`
  - `casual`
  - `formal`
- 추가 스타일 프롬프트 또는 전체 시스템 프롬프트 직접 지정 가능
- `translate.py`의 기존 설정값 상속 가능
- `dry-run`으로 실제 수정 없이 후보 텍스트만 스캔 가능
- 수정 전 원본 백업 가능
- 월드 번역과 리소스팩 번역을 하나의 도구에서 처리 가능

## 폴더 구성

```text
minecraft-world-translator/
├── README.md
├── config.example.toml
├── mc_world_translator.py
├── webui_server.py
└── requirements.txt
└── webui/
    ├── index.html
    ├── styles.css
    └── app.js
```

## 설치

Python 3.11+ 기준.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

`nbt` 계열 라이브러리가 필요하다. `requirements.txt`에 포함돼 있다.

## 가장 빠른 사용법

현재 이 작업 폴더 기준으로는 예제 설정 파일을 그대로 시작점으로 써도 된다.

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
python3 mc_world_translator.py --config config.example.toml
```

첫 번째 명령은 실제 수정 없이 후보 텍스트만 스캔한다.  
두 번째 명령은 실제 번역을 수행하고 월드 파일을 수정한다.

## 웹 UI 사용법

브라우저에서 설정하고 실행하고 싶다면 웹 UI를 쓸 수 있다.

```bash
python3 webui_server.py
```

기본 접속 주소:

- `http://127.0.0.1:8765`

자동으로 브라우저를 열고 싶다면:

```bash
python3 webui_server.py --open-browser
```

호스트/포트를 바꾸고 싶다면:

```bash
python3 webui_server.py --host 0.0.0.0 --port 9000
```

웹 UI에서 지원하는 것:

- 영어 / 한국어 / 일본어 인터페이스
- 라이트 / 다크 테마 전환
- 월드 경로, API, 모델, 프롬프트, 스타일 프리셋 설정
- 스캔 범위 on/off
- 리소스팩 zip 번역 설정
- 실시간 진행률, 현재 파일, 작업 로그, 결과 JSON 확인
- 현재 폼 설정 JSON 내보내기

주의:

- 웹 UI는 `로컬 서버`다. 외부에 배포하는 용도가 아니라, 현재 PC에서 번역기를 편하게 조작하기 위한 화면이다.
- API 키는 브라우저 저장소에 남기지 않는다. 새로고침 후 필요하면 다시 입력하면 된다.
- 실제 번역 전에는 웹 UI에서도 `스캔만 실행`을 먼저 돌리는 걸 권장한다.

## 설정 파일 설명

예제 파일: [config.example.toml](./config.example.toml)

주요 항목은 다음과 같다.

### 기본

- `world_dir`
  - 번역할 월드 폴더 경로
- `report_path`
  - 작업 결과 JSON 리포트 경로
- `dry_run`
  - `true`면 실제 수정 없이 스캔만 수행
- `backup`
  - `true`면 수정 전 백업 생성
- `backup_suffix`
  - 백업 파일 suffix
- `batch_size`
  - 한 번에 번역 API에 보낼 텍스트 수
- `temperature`
  - 번역 샘플링 값

### `translate.py` 상속

- `inherit_translate_py`
  - `true`면 `translate.py`에서 `API_KEY`, `BASE_URL`, `MODEL`, `SYSTEM_PROMPT`를 읽어 기본값으로 사용
- `translate_py_path`
  - 상속할 `translate.py` 경로

이 방식은 기존에 쓰던 번역 설정을 그대로 재사용하고 싶을 때 유용하다.

### API

```toml
[api]
api_key = ""
base_url = ""
model = ""
```

- 비워두면 다음 순서로 채운다.
  1. 설정 파일 값
  2. 환경변수 `OPENAI_API_KEY` 또는 `COMET_API_KEY`
  3. `translate.py` 상속값

### 프롬프트 / 스타일

```toml
[prompt]
target_language = "한국어"
style_preset = "dcinside"
style_prompt = ""
custom_system_prompt = ""
```

- `target_language`
  - 예: `한국어`, `일본어`, `English`, `繁體中文`
- `style_preset`
  - 기본 스타일 프리셋
- `style_prompt`
  - 프리셋 뒤에 추가 지시를 덧붙임
- `custom_system_prompt`
  - 이 값을 넣으면 프리셋을 무시하고 완전한 시스템 프롬프트로 사용

### 스캔 범위

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
component_translate_key_prefixes = ["brennenburg."]
```

- 켜고 끄면서 어떤 텍스트를 번역할지 조절할 수 있다.
- `skip_command_like_text = true`면 `/kill @p` 같은 실제 명령어는 번역하지 않는다.
- `component_translate_key_prefixes`는 `{"translate":"brennenburg.some_key"}` 같은 키를 텍스트로 바꿔 번역해야 할 때 사용한다.

### 강제 치환

```toml
[scan.overrides]
prison1 = "감옥1"
```

모델이 자꾸 그대로 두는 문자열이나, 프로젝트 고유 용어를 강제로 맞추고 싶을 때 쓴다.

### 리소스팩 번역

```toml
[resource_pack]
enabled = false
zip_paths = ["./resources.zip"]
source_lang_files = ["en_us.json", "zh_cn.json"]
target_lang_file = "ko_kr.json"
skip_if_target_exists = false
```

- `enabled = true`면 지정한 zip 내부 `lang` 파일도 같이 번역한다.
- 상대 경로는 `world_dir` 기준으로 처리된다.

## CLI 인자

```bash
python3 mc_world_translator.py --help
```

주요 인자:

- `--config`
- `--world-dir`
- `--report-path`
- `--api-key`
- `--base-url`
- `--model`
- `--target-language`
- `--style-preset`
- `--style-prompt`
- `--custom-system-prompt`
- `--batch-size`
- `--temperature`
- `--dry-run`
- `--no-backup`
- `--resource-pack-zip`

## 예시

### 1. 한국어 자연체로 번역

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --style-preset neutral
```

### 2. 일본어로 번역

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --target-language 日本語 \
  --style-preset casual
```

### 3. 리소스팩 zip도 같이 번역

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enable-resource-pack-translation \
  --resource-pack-zip ../Trip\ to\ BrennenBurg\ REMAKE/resources.zip
```

### 4. 완전 커스텀 프롬프트 사용

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --custom-system-prompt "너는 마인크래프트 공포맵 전문 번역가다. 일본어 텍스트를 한국어 존댓말로 옮기고, 퍼즐 힌트는 명확하게 유지해라."
```

## 출력 파일

- 리포트 JSON
  - 기본값: `world_dir/translation_report.json`
- 백업 파일
  - 기본값: 원본 파일명 + `.bak_translate`

## 주의

- 월드 파일은 바이너리라서 잘못 건드리면 맵이 깨질 수 있다.
- 실제 적용 전에는 반드시 `--dry-run`을 먼저 돌리는 걸 권장한다.
- 커스텀 스타일이 너무 과하면 책 제목이나 아이템 이름까지 과하게 망가질 수 있다.
  - 이런 경우 `style_preset = "neutral"` 또는 `[scan.overrides]`를 같이 쓰는 편이 낫다.
- 멀티에서 쓰려면 호스트 월드와 리소스팩, 버전, 필요한 모드/옵티파인 조건을 따로 맞춰야 한다.

## Git 저장

이 폴더만 따로 Git 저장소로 관리하는 걸 권장한다.

```bash
git init
git add .
git commit -m "Add reusable Minecraft world translator"
```
