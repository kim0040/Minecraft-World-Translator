# 사용자 문서·문자 에셋·스크린샷 현지화 — 2026-10-02

사용자 요청: 확장된 언어에 맞춰 README와 문자가 들어간 에셋을 일관되게 현지화하고, 언어별 제품 화면을 새로 캡처해 관련 문서를 갱신한 뒤 main에 commit/push한다.

## 기준과 범위

- 시작: clean `main` / `cc383e9`. 상위/제품 AGENTS, 구현 계약, 검증 정책, 최신 통합·상태·후속 문서를 확인했다.
- 실제 `LOCALES`는 **ko/en/ja**다. 중국어 간체 README는 기존 문서 언어이며 중국어 UI 구현으로 설명하지 않는다. 번역 도착 언어는 별도 자유 입력이다.
- README/사용 안내/개인정보/면책은 ko/en/ja/zh에 같은 언어 전환과 현지화된 사용자 문서 링크를 제공한다. 개발·지원 표·상태·법적 검토는 한국어 문서로 남기고 링크에서 안내한다.
- 제품명 PomiTranslate, Pomi, 공식 부제 World Translator for Minecraft, 공식 비공식 제품 고지·MIT/제3자 원문, 모델 ID·코드·원문 텍스트는 보존한다.

## 변경

- 영어 메인과 한국어·일본어·중국어 README의 소개 이미지·스크린샷·안내를 언어별로 연결했다. 사용 안내/개인정보/면책에 영어·일본어·중국어판 9개를 추가했다.
- 기존 잘못된 “실제 유료 E2E 미실행” 문구는 제한된 기존 OpenRouter/DeepSeek 검증과 최신 native·전체 가격/품질 미검증을 구분하도록 수정했다. 이번 작업에서 API를 호출한 것이 아니다.
- [`assets/localization.json`](../../assets/localization.json)에서 공유4/스캔4/백업4/API4/미지원4의 문구와 줄바꿈을 관리한다. [`generator`](../../scripts/generate-localized-assets.mjs)는 SVG20개를 생성하며 PNG20개도 같은 SVG로 렌더했다. 기존 Pomi 픽셀은 변경하지 않았다. 언어 없는 안내4개는 이번 한국어 PNG의 호환 별칭으로 갱신했다.
- 영어 API 안내는 “번역된 텍스트”가 아니라 **선택한 원문과 번역 지시**를 전송한다고 수정했다. 중국어 공유 이미지에 문서 언어와 실제 UI 언어의 차이를 표시했다.
- 합성 fixture에 검증된 `locale` 진입값과 언어별 도착 언어/수동 번역 예시를 추가했다. 기본 ko와 기존 scenario 동작을 유지한다.
- `scripts/capture-docs.playwright.js`로 UI 언어 3개×검토/설정/실행3장의 PNG9개를 생성했다. 화면 전환·폰트·저장 알림이 끝난 뒤 캡처한다. 기존 한국어 image URL3개도 이번 캡처의 별칭으로 갱신했다.
- 실제 캡처에서 영어 후보 상태 배지의 긴 Manual Translation이 잘리는 것을 확인해 좁은 행 배지만 **Manual**로 수정했다. 전체 필터·입력 설명은 유지한다. 수정 뒤 관련 캡처를 갱신했다.
- [`현지화 관리`](../localization.md), [`이미지 안내`](../images/README.md), [`화면 manifest`](../images/manifest.json), [`에셋 manifest`](../../assets/localization-manifest.json)에 재생성 명령·입력/출력 hash·지원 언어·별칭을 기록했다.

## 이번 검증

| 검사 | 결과·범위 |
| --- | --- |
| Svelte/TypeScript | 로컬 `svelte-check --tsconfig ./tsconfig.json` 오류0/경고0, `tsc --noEmit` PASS |
| i18n | 로컬 Vitest `tests/frontend/i18n.test.ts` 1파일/3 PASS. key set·모든 언어 값·변수 치환 |
| 실제 UI 캡처 | 최신 Svelte UI를 macOS Playwright/Chromium에서 1440×980/light로 캡처9장. 문서 lang·수동 번역·가로 overflow 확인, 외부 요청0, scan/translation/restore 실행0, 실제 API0 |
| 문자 에셋 | SVG20개 최신 여부 PASS. 렌더된 text bounds가 이미지 안에 있으며 본문/제목과 마스코트 영역을 확인. 중국어 각주 추가 후 해당 공유 이미지 재렌더. 최종20개 갤러리 시각 검토 |
| 파일 무결성 | 화면9개·SVG/PNG40개 hash와 한국어 호환 별칭3+4 byte-identical PASS |
| 문서·Git | 현지화 문서 링크·이미지 연결·공식 고지·diff·추적 범위를 최종 확인하고 main에 commit/push. 최종 SHA는 Git 기록을 따른다 |

설치된 pnpm launcher가 응답 없이 대기해 그 두 실행만 중단하고, 저장소에 이미 있는 동일 `svelte-check`/TypeScript/Vitest를 Node로 직접 실행했다. 의존성·lock/toolchain은 변경하지 않았다. 일반 `output/` 갤러리·trace·cache와 runtime world/DB/key는 Git에 추가하지 않는다.

## 완료 경계

문서/에셋/언어별 소개 화면 작업의 완료이며 **Phase3 또는 release 완료가 아니다**. Python/Rust 전체 검사·native/sidecar/installer rebuild·유료 provider 검사·공개 release/signing/updater dispatch는 이번 범위가 아니어서 실행하지 않았다. 원본 world·실제 credential 접근/변경0, 추가 API 비용$0. 최신 native·플랫폼·배포 gate는 [추후 작업](../follow-up-work.md)에 남아 있다.

Luna Max 작업자4개(일본어·중국어 문서, 문자 에셋, 개인정보/면책)가 독립 범위를 처리했고 Main이 실제 카탈로그·핵심 문구·렌더/캡처·hash·diff를 확인했다. 요청된 GPT-5.6 Luna는 callable 모델에 없어 GPT-6 Luna Max를 사용했다. 사용자 요청대로 main에 저장하며 별도 tag/release는 만들지 않는다.
