# PomiTranslate

**World Translator for Minecraft** · 마인크래프트 Java Edition 월드의 텍스트를 번역하는 데스크톱 앱

<img src="assets/brand/wordmark/logo_wordmark_v1.png" alt="PomiTranslate" width="340" />

한국어 | [English](docs/README.en.md) | [日本語](docs/README.ja.md) | [简体中文](docs/README.zh.md)

해외 어드벤처 맵의 표지판, 책, 아이템 설명을 읽기 편한 언어로 바꾸고 싶을 때 사용합니다. 먼저 월드를 스캔하고, 번역할 문장을 검토한 다음, 선택한 AI 제공사 또는 직접 입력한 번역문으로 적용합니다.

대학생 **김현민**이 직접 쓰려고 만들기 시작한 개인 오픈소스 프로젝트입니다. 개인 시간과 제한된 예산으로 개발하고 있으며, 기업이 운영하는 상용 서비스나 유료 지원 상품은 아닙니다. 마스코트는 **Pomi**입니다.

> **개발 중:** macOS Apple Silicon의 격리된 개발 앱에서 주요 흐름을 확인했습니다. 서명된 정식 설치본, Windows/Linux 실기 검증, 실제 유료 번역의 최종 검증은 남아 있습니다. [현재 상태](docs/current-state.md) · [추후 작업](docs/follow-up-work.md)
>
> NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.

## 화면으로 보기

### 번역할 문장을 직접 검토

![후보 검색·유형 필터·직접 번역 편집 화면](docs/images/review.png)

검색과 유형·상태 필터로 문장을 찾고, 번역에서 제외하거나 직접 번역문을 입력할 수 있습니다. 같은 원문의 등장 위치도 확인합니다.

### 모델과 추론 방식 설정

![제공사·모델·추론 방식·키 저장 상태 화면](docs/images/settings.png)

OpenRouter 추론은 **모델 기본값 / 추론 끄기 / 직접 설정**으로 선택합니다. 모델 지원 정보 조회와 설정 저장을 분리하고, 하단에 저장·변경 취소를 고정했습니다.

<details>
<summary>실행 전 확인 화면</summary>

![추론·요청 수·예상 비용과 외부 전송 확인 화면](docs/images/run.png)

</details>

화면은 현재 제품 UI를 **합성 데이터**로 실행해 캡처했습니다. 표시된 모델·월드·비용은 소개용 예시이며 실제 사용량이나 해당 모델의 지원 보장이 아닙니다. [화면 정보](docs/images/README.md)

## 주요 기능

- **스캔부터 시작:** 월드를 수정하거나 번역 API를 호출하지 않고 후보와 지원 범위를 확인합니다.
- **검토와 직접 번역:** 검색, 필터, 제외, 직접 번역 입력을 제공합니다. 직접 번역만 적용하면 번역 API 요청이 필요하지 않습니다.
- **다양한 제공사:** OpenAI, Gemini, Anthropic, OpenRouter, Comet 및 Custom endpoint 설정을 제공합니다. 사용 가능한 모델은 제공사와 계정에 따라 달라집니다.
- **백업과 복원:** 쓰기 전 검증된 백업, 복원 전 recovery snapshot, 취소·재개와 결과 보고를 제공합니다.
- **리소스팩 ZIP:** 옵션으로 월드 내 `resources.zip`과 명시적으로 선택한 외부 ZIP의 언어 파일을 처리합니다.
- **로컬 데스크톱:** Tauri + Svelte 화면과 Python 코어를 사용합니다. UI 언어는 한국어·영어·일본어입니다.

## 사용 방법

1. Minecraft 또는 서버를 종료하고 **월드의 별도 복사본**을 만듭니다.
2. 앱의 **환경 설정**에서 제공사, 모델, 도착 언어와 필요한 번역 지시를 설정합니다. AI 번역을 사용할 때는 본인의 API 키를 입력해 저장합니다.
3. **월드 선택 → 월드 스캔**에서 복사본을 선택하고, 지원 범위와 경고를 확인합니다.
4. **후보 검토**에서 제외할 문장과 직접 번역문을 지정합니다.
5. **번역 진행**에서 대상·추론·외부 전송·예상 비용을 확인한 뒤 실행합니다.
6. **완료 결과**를 확인하고 게임에서 내용을 검토합니다. 되돌리려면 **백업 관리**에서 복원을 선택합니다.

추정 비용은 실제 청구 금액과 다를 수 있습니다. 추론 토큰·재시도·모델 라우팅 등의 비용이 추가될 수 있으므로 제공사 대시보드도 확인하세요. 자세한 설정·복원·CLI 안내는 [사용 안내](docs/user-guide.md)에 있습니다.

### 실행·설치

현재는 개발 빌드를 기준으로 안내합니다. 정식 서명 설치본이나 모든 OS 지원이 완료됐다고 소개하지 않습니다. 소스 실행에는 Python 3.12, Node.js, pnpm, Rust 및 [Tauri 플랫폼 준비 항목](https://v2.tauri.app/start/prerequisites/)이 필요합니다.

```bash
git clone https://github.com/kim0040/Minecraft-World-Translator.git
cd Minecraft-World-Translator
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt pyinstaller==6.16.0
pnpm install --frozen-lockfile
pnpm desktop:dev
```

위 가상환경 활성화는 macOS/Linux 예시입니다. Windows 명령, toolchain 버전, 패키징과 기여 방법은 [개발 안내](docs/development.md)를 따릅니다. 완성된 패키지는 Python sidecar를 포함하는 구조지만, clean-machine 설치 검증은 아직 남아 있습니다.

## 지원 범위

표지판, 책, 커스텀 이름, 아이템 설명, 텍스트 디스플레이, 일부 명령 텍스트와 ZIP 리소스팩 언어 파일을 처리합니다. 검증한 **합성 형식**을 기준으로 하며 모든 Minecraft 버전·모드·월드의 텍스트를 찾는다는 뜻은 아닙니다.

Bedrock, `.mcr`, `.linear`, 알 수 없는 압축에는 쓰지 않습니다. 데이터팩, scoreboard, command storage, `level.dat`의 텍스트, playerdata 및 폴더형 리소스팩은 현재 번역 범위에 포함되지 않습니다. [지원 표](docs/support-matrix.md)

## 비용·개인정보·면책

앱 자체의 구매·구독·인앱 결제는 없습니다. **AI API 이용료는 선택한 제공사의 정책에 따라 사용자에게 발생할 수 있습니다.** 번역할 텍스트와 번역 지시는 선택한 API 제공사 또는 중계 서비스로 전송됩니다. 제공사별 보관·학습·개인정보 정책도 확인하세요.

API 키의 데스크톱 기본 저장 방식은 **로컬 암호화 SQLite + 별도 key 파일**입니다. 세션 전용과 OS 키체인은 선택 사항입니다. 같은 사용자 계정에서 두 파일을 모두 읽을 수 있는 프로세스까지 막는 보안은 아닙니다. [데이터·키 안내](docs/privacy.md)

이 소프트웨어는 **있는 그대로(AS IS)** 제공됩니다. 번역 정확도, 모든 월드와의 호환성, 데이터 보존, 중단 없는 이용을 보증하지 않습니다. 적용 법률이 허용하는 범위에서 작성자·기여자는 데이터 손실, 월드 손상, API 청구 및 사용으로 발생하는 손해에 책임을 부담하지 않습니다. [면책·권리 안내 전문](docs/disclaimer.md)과 [MIT 원문](LICENSE)을 확인하세요.

맵·리소스팩·번역본의 제3자 권리는 소프트웨어 라이선스와 별개입니다. 원작자의 허락 없이 재배포하지 마세요.

<details>
<summary>English safety notice</summary>

Back up your world before translating. PomiTranslate writes to the world files you select.

Text you choose to translate is sent to the API provider you select and may incur charges.

PomiTranslate has no purchase, subscription, or in-app payment.

</details>

## 기여자·문의

- **김현민** — 제작·유지보수 · [mini0227kim@gmail.com](mailto:mini0227kim@gmail.com)
- 버그·제안: [GitHub Issues](https://github.com/kim0040/Minecraft-World-Translator/issues)
- 기여: [CONTRIBUTING.md](CONTRIBUTING.md)

버그 보고에는 OS, 앱 버전, 재현 방법을 적어 주세요. API 키, 개인 월드, 비밀이 포함된 로그를 공개 Issue에 올리지 마세요. 답변·수정 일정이나 금전 보상을 약속하는 지원 서비스는 제공하지 않습니다.

## 라이선스·문서

프로젝트 소스는 기존 **[MIT License](LICENSE)**를 유지합니다. 의존성은 각각의 라이선스를 따르며 프로젝트 MIT로 다시 허가되는 것이 아닙니다. 검토한 범위에서 MIT 유지의 명백한 충돌은 발견하지 않았지만, 배포물별 고지·전체 플랫폼 의존성 검증은 정식 배포 전에 완료해야 합니다. [제3자 고지](THIRD_PARTY_NOTICES.md)

[문서 목차](docs/README.md) · [현재 상태](docs/current-state.md) · [추후 작업](docs/follow-up-work.md)
