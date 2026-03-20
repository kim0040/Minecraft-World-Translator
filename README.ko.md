# Minecraft World Translator

[English](./README.md) | 한국어 | [日本語](./README.ja.md)

Minecraft World Translator는 마인크래프트 월드와 리소스팩 텍스트를 번역하기 위한 로컬 도구다. 초보자도 웹 UI 기준으로 따라갈 수 있게 구성되어 있고, 숙련자는 CLI로도 바로 사용할 수 있다.

문의 및 오류 제보:

- `mini0227kim@gmail.com`

## 이 도구가 하는 일

- 월드 `.mca` 파일 안의 텍스트 추출
- 표지판, 책, 아이템 이름, Lore, title 계열 텍스트 번역
- 선택적으로 리소스팩 `lang/*.json` 번역
- 여러 LLM 공급자 전환
- 모델 목록 조회
- 짧은 스타일 메모를 더 자세한 프롬프트로 보강

## 지원 공급자

- `comet`
- `openai`
- `gemini`
- `anthropic`
- `openrouter`

## 빠른 시작

초보자라면 아래 흐름을 추천한다.

1. 웹 UI 실행
2. 공급자, API 키, 모델 입력
3. 월드 폴더 입력
4. `스캔만 실행`
5. 결과 확인
6. 문제 없으면 `실제 번역 실행`

## 운영체제별 설치

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

실행 정책 문제로 막히면:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

원터치 실행:

- [run_web_ui.command](./run_web_ui.command)

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

필요하면:

```bash
sudo apt install python3-venv
```

## 웹 UI 실행

```bash
python3 webui_server.py
```

접속 주소:

- `http://127.0.0.1:8765`

브라우저 자동 열기:

```bash
python3 webui_server.py --open-browser
```

## CLI 사용

드라이런:

```bash
python3 mc_world_translator.py --config config.example.toml --dry-run
```

실제 번역:

```bash
python3 mc_world_translator.py --config config.example.toml
```

모델 목록 조회:

```bash
python3 mc_world_translator.py --config config.example.toml --list-models
```

짧은 스타일 메모 보강:

```bash
python3 mc_world_translator.py \
  --config config.example.toml \
  --enhance-style-brief "중세 공포맵 느낌, 고유명사는 음역, 힌트는 명확하게"
```

## 설정 파일

예제:

- [config.example.toml](./config.example.toml)

핵심 항목:

- `world_dir`: 번역할 월드 폴더
- `report_path`: 리포트 저장 경로
- `dry_run`: 실제 수정 없이 스캔만
- `backup`: 백업 생성 여부
- `batch_size`: 한 번에 보낼 문장 수
- `[api].provider`: 공급자 선택
- `[api].model`: 모델 이름
- `[prompt].target_language`: 대상 언어
- `[prompt].style_preset`: 스타일 프리셋

환경변수 지원:

- `COMET_API_KEY`
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENROUTER_API_KEY`

## 초보자용 팁

- 처음에는 `neutral` 프리셋이 가장 안전하다.
- 반드시 `Scan Only`를 먼저 돌리는 편이 낫다.
- 백업은 켜둬라.
- 중요한 맵이면 원본 복사본에서 먼저 테스트해라.

## 기술 설명

- `.mca` 안의 NBT 데이터를 직접 읽어서 사용자 노출 텍스트를 찾는다.
- 실제 명령어처럼 보이는 문자열은 번역에서 제외할 수 있다.
- 리소스팩은 zip 내부 `lang/*.json`을 대상으로 처리한다.
- 공급자별 요청 형식은 [llm_backends.py](./llm_backends.py)에서 분리 처리한다.

## 문제 해결

`API key is missing`

- 웹 UI, 설정 파일, 환경변수, `translate.py` 중 하나에 키가 있어야 한다.

`Model is missing`

- 모델 이름을 직접 넣거나 `--list-models`를 써라.

웹 UI가 안 열림

- 서버가 켜져 있는지 확인
- 포트 충돌 확인
- 직접 `http://127.0.0.1:8765` 접속

## 라이선스

MIT License 적용.

- [LICENSE](./LICENSE)
