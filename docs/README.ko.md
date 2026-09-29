# PomiTranslate

World Translator for Minecraft

NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

![PomiTranslate 워드마크](../assets/brand/wordmark/logo_wordmark_v1.png)

[English](../README.md) | 한국어 | [日本語](README.ja.md) | [简体中文](README.zh.md)

PomiTranslate는 Java Edition 월드의 플레이어에게 보이는 글을 번역하는 무료 로컬 도구입니다. 마스코트는 Pomi입니다. GitHub 저장소 이름은 `Minecraft-World-Translator`로 둡니다.

CLI와 Tauri 데스크톱 앱은 패키지된 JSONL sidecar를 통해 같은 번역기를 씁니다. 번역은 검증된 백업이 생긴 뒤에만 월드를 고칩니다. Scan Only는 공급자에 요청을 보내지 않고 월드 바이트도 바꾸지 않습니다. 선택자, 리소스 위치, 숫자, 좌표, 서식 자리표시자는 그대로 둡니다.

![Pomi](../assets/mascot/base/mascot_base_front_v1_512.png)

## 번역하는 글

- 옛 표지판과 앞면·뒷면이 있는 표지판
- 책 페이지, 제목, 필터된 제목
- 사용자 이름, 아이템 이름, 설명
- 직접 적은 텍스트 컴포넌트와 1.20.5+ 아이템 컴포넌트
- `tellraw`, `title`, `subtitle`, `actionbar` 명령의 글
- 옵션을 켰을 때 zip 안 리소스팩 `lang/*.json`

![먼저 스캔](../assets/illustrations/docs/doc_scan_first_v1.png)

## 형식

픽스처가 통과한 범위만 지원합니다.

- 리전 압축: gzip, zlib, 무압축, Minecraft 1.20.5+ LZ4 (`LZ4Block`)
- `c.<x>.<z>.mcc` 외부 청크. 파일에는 압축된 바이트만 있습니다.
- 표준 리전 폴더, 커스텀 차원, `level.dat`가 있는 Paper 스타일 형제 월드

발견만 하고 쓰지 않습니다.

- Bedrock
- Anvil 이전 `.mcr`
- `.linear`
- 127을 포함한 알 수 없는 압축

생성된 목록은 [support-matrix.md](support-matrix.md)입니다. macOS Intel, Windows x64, Linux x64는 지원 플랫폼으로 적지 않습니다. Linux 패키지 작업은 산출물을 만들 뿐, 그 플랫폼을 지원한다고 확인한 것은 아닙니다.

![지원하지 않는 형식은 멈춤](../assets/illustrations/docs/doc_unsupported_v1.png)

## 공급자

쓰는 공급자는 OpenAI, Gemini, Anthropic, OpenRouter, Custom입니다. Custom은 사용자가 적은 주소로 OpenAI 채팅 형식 또는 Anthropic 메시지 형식을 보냅니다. 예전 Comet 설정은 그대로 읽습니다.

실제 번역 전에 그 공급자의 텍스트 모델 목록을 가져와 공개된 id와 이름, 컨텍스트 길이를 사용합니다. 고른 모델이 목록에 없으면 월드를 쓰기 전에 멈춥니다.

## 키와 설정

API 키는 운영체제 키체인의 서비스 이름 `PomiTranslate`에 저장합니다. 계정 이름은 `openrouter` 같은 공급자 id입니다. 키는 `settings.json`, SQLite, 로그, git에 넣지 않습니다.

공개 설정은 앱을 업데이트해도 설치 폴더 밖에 남습니다.

- macOS: `~/Library/Application Support/PomiTranslate/settings.json`
- Windows: `%APPDATA%\PomiTranslate\settings.json`
- Linux: `$XDG_DATA_HOME/PomiTranslate` 또는 `~/.local/share/PomiTranslate/settings.json`

공급자별 모델 목록도 그 옆에 저장됩니다. 데스크톱 설정 화면에서 현재 공급자의 키를 키체인에서 삭제할 수 있습니다.

![선택한 공급자로 글이 전송됨](../assets/illustrations/docs/doc_api_notice_v1.png)

## 실행

테스트한 런타임은 Python 3.12입니다. 패키지된 데스크톱 진입점은 사용자에게 Python 설치를 요구하지 않습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

월드를 스캔합니다. 공급자를 호출하지 않고 월드도 바꾸지 않습니다.

```bash
python mc_world_translator.py --world-dir "/path/to/world" --dry-run --report-path ./scan-report.json
```

스캔을 확인한 뒤 번역합니다. 그 사이 월드가 바뀌면 지문이 맞지 않아 거절됩니다.

```bash
python mc_world_translator.py \
  --world-dir "/path/to/world" \
  --provider openrouter \
  --model "your-text-model" \
  --expect-fingerprint "<스캔 리포트의 지문>"
```

`--api-key`를 비우면 그 공급자에 이미 저장된 키를 씁니다. `--list-models`는 공급자가 돌려준 텍스트 모델을 출력합니다.

검증된 최신 백업을 되돌립니다.

```bash
python mc_world_translator.py --world-dir "/path/to/world" --restore-backup
```

쓰기 실행마다 버전별 백업 세트를 만듭니다. 복구는 `entities`와 활성화한 월드 내부 `resources.zip`을 포함해 그 실행이 고친 모든 파일을 되돌리며, 현재 파일도 먼저 recovery 백업으로 보존합니다. Minecraft 또는 서버가 Java Edition `session.lock`을 잡고 있으면 쓰기를 시작하지 않습니다.

![쓰기 전에 백업](../assets/illustrations/docs/doc_backup_first_v1.png)

## 데스크톱 앱

데스크톱 앱은 Tauri 2와 Svelte 5로 구성됩니다. 한국어·영어·일본어 UI, 최근 월드 선택, DataVersion 정보, 구조 기반 호환성 상태, Scan Only, 후보 검색·필터·제외·직접 번역, 공급자·요청 제한 설정, 월드 내부 `resources.zip` 번역, 진행·취소, 조건이 맞는 취소 작업의 명시적 재개, 버전별 백업 기록, 복원 전 recovery 백업을 제공합니다. UI 언어는 번역 대상 언어와 별도입니다. localhost 포트를 열지 않습니다. 현재 월드 지문, scan plan, 번역 설정, 검증 백업 세트가 모두 일치할 때만 재개를 제안합니다.

소스에서 네이티브 앱을 빌드합니다.

```bash
pnpm install --frozen-lockfile
pnpm sidecar:build
pnpm exec tauri build
```

sidecar 빌드에는 Python 3.12와 PyInstaller 6.16.0이 필요합니다. 패키지 설치 후 사용자는 Python, Node, Rust를 설치할 필요가 없습니다.

## 데스크톱 프로토콜

`python -m mwt.desktop_entry`는 표준 입력과 출력으로 JSONL을 주고받습니다. 로컬 포트를 열지 않습니다. `--notices`와 `--about`은 안전 안내를 출력합니다. `--scan`과 `--translate`는 CLI와 같은 코어를 씁니다.

GitHub Actions는 Linux, macOS, Windows에서 PyInstaller sidecar와 서명되지 않은 Tauri 패키지를 만듭니다. clean-machine 설치와 릴리스 smoke를 통과하기 전에는 지원 플랫폼으로 적지 않습니다. 서명 자격이 없으면 서명된 릴리스를 공개하지 않습니다.

## 로컬 웹 UI

Python이 이미 있을 때 `webui_server.py`를 쓸 수 있습니다. 기본 주소는 `127.0.0.1:8765`입니다. 패키지된 앱은 이 서버가 없어도 됩니다.

```bash
python webui_server.py
```

macOS에서는 `run_web_ui.command`가 가상환경을 만들고 브라우저를 엽니다.

## 설정 파일

필드는 [config.example.toml](../config.example.toml)에 있습니다. `world_dir`은 비워 두고, 자신의 월드를 지정할 때만 채웁니다. API 키는 이 파일에 넣지 않습니다.

## 테스트

```bash
.venv/bin/python test_core.py
.venv/bin/python tests/test_release_fixtures.py
.venv/bin/python tests/test_providers.py
.venv/bin/python tests/test_brand_secrets.py
.venv/bin/python tests/test_desktop_entry.py
```

릴리스 픽스처 결과가 지원 표의 출처입니다.

## 문의

질문과 버그: `mini0227kim@gmail.com`

운영체제, 공급자, 모델, CLI인지 데스크톱 진입점인지, 오류 글을 적어 주세요. API 키는 보내지 마세요.

## 라이선스

MIT. [LICENSE](../LICENSE)를 봅니다.
