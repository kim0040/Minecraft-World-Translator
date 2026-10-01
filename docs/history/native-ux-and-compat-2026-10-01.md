# 네이티브 UX·Gemini·SNBT 개선 — 2026-10-01

사용자 요청: [전체 점검·계획](../review-and-plan-2026-10-01.md)에 따라 환경 변수의 Gemini 키(예산 약 US$3)를 필요 시 사용해 "최대한 개선". 이 기록은 그 구현과 검증 범위다.

## 판정

**Phase3 착수(COMP-01 완료) / 네이티브 UX 1차 구현 / macOS native 확인 대기 / release-ready 아님.** 작업 환경은 Linux cloud container(x86_64)이며 macOS 앱 실행·서명·설치는 하지 않았다. Native-only 동작(오버레이 타이틀바, 메뉴, ⌘Q 보호, 드래그&드롭, Dock 진행률)은 Rust 컴파일·Linux Rust 테스트와 브라우저 fixture 이벤트로만 확인했다.

## 변경

### 결함 수정 (점검 F1–F10)

| ID | 수정 |
| --- | --- |
| F1 | 후보 표 열 숨김을 viewport media query → 표 자체의 container query로 변경. 기본 창 1180×800에서 상세 패널을 열어도 원문 열 ≥200px |
| F2 | Gemini `thoughtsTokenCount`를 출력 토큰에 합산(제공사 과금 기준). thinking 파트는 번역문에서 제외 |
| F3 | → COMP-01 |
| F4 | 내용 영역 내부 스크롤로 바꾸고 단계/페이지 이동 시 맨 위로 |
| F5 | 진행 중 "예상 요청 횟수" 라벨 → "API 요청", 값 `done / total` |
| F6 | 미사용 `src/styles.css`, `src/lib/i18n.ts` 삭제, `theme-color` 갱신 |
| F7 | `RunEvent::ExitRequested`도 작업 중이면 `prevent_exit` + 창 표시 + 안내 |
| F8 | 변경 없음: 실패 결과의 행동은 backend resume 가능 여부를 그대로 따르는 기존 계약이 맞음 |
| F9 | 테마 적용 시 native 창 테마·배경색도 함께 설정 |
| F10 | Gemini 키를 URL 쿼리 대신 `x-goog-api-key` 헤더로 전송. `AQ.` 형식 키로 실제 확인 |

### Gemini

- 모델 목록의 `thinking` 플래그로 추론 metadata를 만든다. 3.x: `thinkingLevel`(flash/lite: minimal·low·medium·high, pro: low·high), 2.5: `thinkingBudget`(끄기=0). 끄기는 3.x에서 `minimal`. flash-lite 3.x는 budget 0을 거부(실측 400)하므로 3.x에는 budget을 보내지 않는다.
- 기존 추론 UI(모델 기본값/끄기/직접 설정)를 Gemini에도 노출. 설정 key `openrouter_reasoning`은 호환을 위해 그대로 쓴다.
- `maxOutputTokens`를 최소 32768로(사고 토큰 포함 한도라 잘림 방지, 실제 생성분만 과금). `finishReason=MAX_TOKENS`는 실패로 처리해 재시도·분할.
- 별칭 `flash`/`pro` → `gemini-flash-latest`/`gemini-pro-latest`(+`flash-lite`). 이전 `gemini-flash`/`gemini-pro`는 공개 목록에 없다.

### 서식 코드 검증 강화

`§` 코드·`%s`·`{0}`이 빠진 경우만 막던 검사를 **개수 완전 일치 + 새 토큰 금지**로 강화. 실제 Gemini flash-lite가 `§6Merchant §rof the Northern Gate`를 `§6북쪽 문§r의 §6상인`(색 코드 추가)으로 번역한 사례를 회귀 테스트로 고정. 같은 개수로 위치만 옮긴 번역은 허용한다.

### COMP-01 SNBT 명령

- `mwt/snbt.py`: 문자열 위치를 기록하는 SNBT parser. 작은/큰따옴표, 따옴표 없는 key/단어, escape(`\n`,`\t`,`\x`,`\u`,`\U`,`\N{}`), 후행 쉼표, typed array, 숫자·boolean·1.21.5 operation(`bool(...)`)을 처리. 바뀐 문자열만 원래 따옴표 형식으로 되돌려 써서 숫자·key 순서·selector·색상 값은 바이트 그대로 보존.
- 명령 패턴에 선행 `/`와 문자열 컴포넌트(`tellraw @a "..."`)를 추가. 기존에는 `/tellraw`로 저장된 명령 블록도 건너뛰고 있었다. 수집 결과가 바뀌므로 `EXTRACTOR_VERSION` 2→3(기존 스캔 계획 무효화).
- JSON·SNBT 모두 해석 실패 시 원본 유지 + `command_unparsed` 경고(파일·개수)를 스캔/결과 화면에 표시.
- support matrix에 `text.snbt_commands` 행 추가(합성 fixture 기준, 실제 게임 로드 아님).

### 네이티브 UX

- 창: macOS `titleBarStyle: Overlay` + `hiddenTitle`, 신호등 위치 지정, 사이드바 상단 40px 드래그 영역, 툴바 드래그 영역. 창 제목 = `월드 이름 — PomiTranslate`.
- 셸: 창 크기 grid, 사이드바·툴바 고정, 내용만 스크롤, overscroll 없음. 모든 화면에 툴바(작업=단계 표시, 그 외=페이지 이름 + 현재 월드 칩).
- 밀도: 본문 13px, 컨트롤 30px, 큰 버튼 34px, radius 6–10px, 카드 그림자 제거, 버튼 축소 애니메이션 제거, 화살표 커서, 라벨 텍스트 선택 불가(입력·원문·경로·값은 선택 가능), 편집·선택 영역 밖 webview 기본 우클릭 메뉴 차단.
- 메뉴: 파일 → 월드 열기(⌘/Ctrl+O), 설정(⌘, — macOS 앱 메뉴), 편집 → 찾기(⌘/Ctrl+F). 라벨은 UI 언어를 따른다(`set_menu_labels`).
- OS 통합: 월드 폴더/`level.dat` 드래그&드롭, Minecraft saves 자동 목록(`worlds.discover`: 공식 런처·Prism/MultiMC·CurseForge, `level.dat` 이름·마지막 플레이·버전, 64KB 이하 PNG 아이콘, symlink·폴더 밖 차단, 읽기 전용), Dock/작업 표시줄 진행률, 백그라운드 완료 시 attention 요청. 창 호출은 순서 보장 큐로 늦은 호출이 새 상태를 덮지 않는다.
- 화면: 월드 화면에서 바로 **스캔 시작**, 스캔·실행 화면의 하단 고정 action bar, 실행 요약을 grouped rows로, 결과 수치를 한 줄 strip + 토큰/비용 rows로, 보고서 내보내기를 제목 옆 작은 버튼으로, 설정 저장 바를 창 하단 footer로(변경 시 강조), 정보 화면 중복 설명 제거, 추론 요약의 "모델 기본값" 중복 문구 제거.
- 새 capability: `core:window:allow-start-dragging/set-title/set-progress-bar/set-theme/set-background-color/request-user-attention`.

## 검증

| 검사 | 결과 | 경계 |
| --- | --- | --- |
| Python (CI 등록 전체) | 22/22 PASS | 기존 20 + `test_snbt_commands` + `test_world_discovery`. Linux Python 3.11 venv |
| Rust | 28 PASS, `cargo check` 경고 0 | Linux x86_64(webkit2gtk dev 설치). sidecar는 빌드용 placeholder만 사용, macOS 미실행 |
| Type/build | check 0/0, `pnpm build` PASS | |
| Frontend unit | 11 files / 58 PASS | |
| Browser | **94/94 PASS** 단일 전체 실행 | 기존 87 + `native.spec.ts` 7. Linux Chromium 1194, 로컬 실행 경로만 임시 config. axe 포함 |
| 실제 Gemini | 아래 표 | 합성 데이터만 전송 |

실제 Gemini 호출(키는 환경 변수에서 프로세스에만 전달, 출력·저장 안 함):

| 목적 | 모델 | 요청 | 결과 |
| --- | --- | --- | --- |
| 점검 | 3.5-flash-lite / 3.5-flash | 2 | flash: 사고 1,791 tokens 미집계 확인(F2) |
| thinkingConfig 지원 확인 | 3.5-flash, 3.5-flash-lite, 2.5-flash | 7 | 3.x `thinkingLevel` OK, 3.x-lite `thinkingBudget:0` → 400, 2.5 budget 0 OK |
| 수정 후 확인 | 3.5-flash 기본/끄기, 3.5-flash-lite | 3 | 기본 7.4초·출력+사고 1,374 집계 / 끄기 1.5초·58 / lite 1.2초 |
| SNBT E2E | 3.5-flash-lite | 1 | 합성 world 명령 블록4(SNBT3+give1): 번역 3, give 원본, 백업 verified, 복원 후 region = 백업 사본 hash 일치 |
| 모델 목록 | — | GET 수회(무료) | 생성 요청 아님 |

총 생성 요청 13회, 입력 약 1,000 / 출력(사고 포함) 약 3,600 tokens. Gemini는 비용을 응답에 보고하지 않아 정확한 금액은 unknown이며, 토큰 기준 수 센트 이하로 추정한다(예산 US$3 대비 미미).

## 남은 것

- **macOS native 확인(사용자 로컬 필요)**: 오버레이 타이틀바와 신호등 위치, 사이드바 드래그, 메뉴·단축키와 라벨 번역, ⌘Q 보호, 드래그&드롭, Dock 진행률/attention, 다크 시작 깜빡임. `pnpm sidecar:build` 후 `pnpm desktop:dev`(Python 변경 있음).
- 사이드바 vibrancy(반투명)는 투명 창·private API가 필요해 이번에 넣지 않았다.
- SNBT/명령 지원은 합성 fixture 기준이다. 1.21.5+로 실제 생성한 맵에서 게임 로드 확인은 COMP-04.
- Gemini 및 비 OpenRouter 제공사의 비용 추정(가격표)은 QUALITY 과제로 남는다.
