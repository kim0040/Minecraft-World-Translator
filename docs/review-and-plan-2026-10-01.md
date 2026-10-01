# 전체 점검·UI/UX 진단·작업 계획 — 2026-10-01

사용자 요청: 문서상 남은 작업을 확인하고, 코드베이스 전체가 의도대로 동작하는지·UI/UX가 괜찮은지 분석해 개선안과 작업 계획을 세운다. “네이티브 앱 같지 않은 느낌”의 원인을 구체화한다. Gemini 키(환경 변수) 사용 허용, 예산 약 US$3.

**이 문서 작성 시점에는 조사·계획만 했다.** 이후 같은 날 사용자 요청으로 S0–S3 대부분과 S4 일부를 구현했다. 결과와 검증은 [네이티브 UX·Gemini·SNBT 개선](history/native-ux-and-compat-2026-10-01.md)을 따른다. 아래 표의 결함 설명은 수정 전 상태다.

## 1. 이번에 실제로 확인한 것

환경: Linux cloud container(x86_64), Python 3.11, Node 22, Chromium 1194. **macOS native/Tauri 앱 실행은 이 환경에서 할 수 없어 수행하지 않았다.**

| 검사 | 결과 | 경계 |
| --- | --- | --- |
| Python 20 suites (`test_core.py` + `tests/test_*.py`) | 20/20 PASS | Linux·Python 3.11 venv. CI는 3.12 |
| Type check (`pnpm check`) | 0 errors / 0 warnings | 현재 HEAD `c26fcd7` |
| Frontend unit (`pnpm test:frontend`) | 11 files / 58 PASS | |
| Browser E2E (Playwright, mock backend) | **87/87 PASS** (2.2분, 단일 전체 실행) — 단, F1처럼 assertion이 없는 시각 결함은 잡지 못함 | 로컬 Chromium 실행 경로만 임시 config로 바꿈. Linux 폰트 |
| 화면 직접 확인 | 기본 창 크기 1180×800, 최소 근처 900×640에서 전 화면 스크린샷 | mock data, light 위주 |
| 실제 Gemini 호출 | 2요청(번역 3문장씩) + 무료 모델 목록 1회 | 아래 F2 참조. 비용은 제공사 미보고, 토큰만 기록 |
| Rust 28 / native / installer | NOT_RUN | Linux에 Tauri webview 개발 환경 없음. 기존 macOS 증거 유지 |

Gemini 호출 기록(합성 3문장, API 키는 출력·저장하지 않음):

| 모델 | 지연 | prompt | 출력(앱 집계) | thoughts(미집계) | 결과 |
| --- | --- | --- | --- | --- | --- |
| gemini-3.5-flash-lite | 1.3초 | 76 | 58 | 0 | 정상, `§` 코드 보존 |
| gemini-3.5-flash | 9.3초 | 76 | 56 | **1,791** | 정상, 그러나 실제 과금 출력은 약 32배 |

`AQ.` 형식의 키도 현재 코드(`?key=` 쿼리)로 정상 동작했다. 제공사가 비용을 보고하지 않아 정확한 금액은 unknown이다. 총 토큰(입력 152, 출력+사고 약 1,905) 기준으로 1센트 미만으로 추정한다.

## 2. 기능 결함·위험 (확인된 것 우선)

| ID | 심각도 | 내용 | 근거 | 제안 |
| --- | --- | --- | --- | --- |
| F1 | **높음** | **기본 창 크기(1180×800)에서 후보 검토 표의 “원문” 열이 폭 0으로 사라진다.** 상세 패널(360px)이 열린 상태에서 고정 폭 열(52+150+210+112px)이 표 폭을 넘음. 가장 중요한 열이 기본 크기에서 안 보임 | 스크린샷 `review.png`/`review-selected.png`(1180). `CandidateTable.svelte`는 `table-layout: fixed` + **viewport** media query만 사용 | 표 폭 기준 container query로 열 숨김/축소, 원문 열 최소 폭(예: 200px) 보장. browser test가 편집기 폭만 검사하므로 원문 열 폭 assertion 추가 |
| F2 | **높음** | **Gemini thinking 모델의 사고 토큰이 사용량에 집계되지 않는다.** `usageMetadata.thoughtsTokenCount`를 무시해 결과 화면 토큰·향후 비용 추정이 과소. Gemini에는 추론 제어가 없어(OpenRouter 전용) 3문장에 9.3초·1,791 사고 토큰. 기본 `maxOutputTokens` 4096에서 40개 batch는 사고 토큰 때문에 응답 잘림(MAX_TOKENS)→재시도·분할 위험 | 실제 호출 위 표. `llm_backends.py` `record_usage`, `_complete_gemini` | 사고 토큰을 completion에 합산(또는 별도 표시). Gemini `thinkingConfig`를 기존 추론 UI(기본/끄기/강도)에 연결. `finishReason=MAX_TOKENS` 명시 처리 |
| F3 | 높음(호환성) | 1.21.5+ SNBT 형식 `tellraw/title`이 **경고 없이** 건너뛰어진다. `json.loads` 실패 시 `return`만 하므로 coverage/보고서에도 안 나타남 | `mwt/extract.py` `_walk_command` | 기존 계획 COMP-01. 그 전에라도 “명령 N개 감지, 형식 미지원으로 미처리” 경고를 추가하면 조용한 누락을 막음 |
| F4 | 중간 | 단계/페이지 이동 시 스크롤 위치가 유지된다. 실행 화면 하단에서 시작하면 결과 화면 제목이 sticky header 밑에 가려진 채 열림 | `result-success.png`. `goStep/goto`에 scroll reset 없음 | 내부 스크롤 컨테이너 도입(U2)과 함께 이동 시 top + 제목 focus |
| F5 | 낮음 | 번역 진행 중 “예상 요청 횟수” 라벨 아래 값이 “API 요청 진행: 1 / 1” — 라벨과 값 불일치. 사이드바 경과 0초 vs 본문 1초 | `RunScreen.svelte:101` | 라벨을 “API 요청”으로, 경과 시간 출처 하나로 통일 |
| F6 | 낮음 | 사용하지 않는 구 파일: `src/styles.css`(구 녹색 테마), `src/lib/i18n.ts`(구 번역 사전). `index.html` theme-color도 구 값 | import 없음 확인 | 삭제. 혼동·검색 노이즈 제거 |
| F7 | 확인 필요 | 창 닫기(CloseRequested)는 작업 중 차단하지만, **macOS ⌘Q(앱 종료)** 는 `RunEvent::ExitRequested`를 처리하지 않아 쓰기 도중 종료될 가능성 | `src-tauri/src/lib.rs` run handler는 Reopen만 처리 | native에서 재현 확인 후 ExitRequested도 같은 gate로 막고 확인 시트 표시 |
| F8 | 낮음 | 실패 결과의 행동이 “처음부터 다시 스캔” 하나. 일시적 제공사 오류면 캐시를 쓰는 “다시 시도/이어서 번역”이 더 싸고 자연스러움 | `result-failed.png` | 상태별 primary action 재검토 |
| F9 | 낮음 | Tauri 창 `backgroundColor`가 light 고정 → 다크 모드 시작 시 흰 화면 깜빡임 가능 | `tauri.conf.json` | 시스템 테마에 맞춰 창 배경/테마 설정 |
| F10 | 낮음(보안 위생) | Gemini 키를 URL 쿼리(`?key=`)로 전송. 오류 메시지는 redaction되지만 프록시/네트워크 로그에 남을 수 있음 | `llm_backends.py` | `x-goog-api-key` 헤더로 변경 (AQ. 형식 포함 동작 확인 필요) |

이 밖에 Python 코어·백업/복원·credential·startup 경로는 기존 테스트가 모두 통과했고, 코드 읽기로 새로운 데이터 손상 경로는 찾지 못했다.

## 3. “네이티브 앱 같지 않다”의 원인

현재 UI는 정돈되어 있고 접근성(키보드 grid, axe, 다국어, 다크)이 강점이다. 아쉬움의 원인은 디자인 품질보다 **웹 페이지의 관습을 그대로 쓴 것**이다.

| 영역 | 지금 | 네이티브에서 기대하는 것 |
| --- | --- | --- |
| 창 크롬 | OS 기본 타이틀바 + 긴 제목 “PomiTranslate — World Translator for Minecraft”. 타이틀바 아래 다시 로고 | macOS: 투명 타이틀바(overlay)·신호등 버튼이 사이드바 위에, 사이드바 반투명(vibrancy). Windows: Mica. 제목은 현재 월드 이름 |
| 스크롤 | 문서 전체가 스크롤(고무줄 튕김, 스크롤바가 창 전체) | 고정 shell, 콘텐츠 영역만 스크롤, overscroll 없음 |
| 밀도·크기 | 본문 14px, 컨트롤 40px, 큰 버튼 48px, 카드 radius 16 + 그림자 | macOS 13px·컨트롤 28–32px·radius 6–8, 그림자 대신 구분선/grouped list |
| 마우스 | 버튼에 `cursor: pointer`, 모든 글자 드래그 선택, 우클릭 시 webview 기본 메뉴, 클릭 시 버튼 축소 애니메이션 | 화살표 커서, UI 크롬 텍스트 선택 불가(본문·원문은 선택 가능), 앱 고유 우클릭 메뉴 |
| 메뉴·단축키 | 메뉴는 기본 + 보기(확대) 뿐. 앱 단축키 없음 | 파일(월드 열기 ⌘O, 최근 월드), 편집(찾기 ⌘F), 설정 ⌘,, 번역 시작/취소, 사이드바 토글, 도움말 |
| OS 통합 | 폴더 선택 대화상자만 | 월드 폴더 드래그&드롭, **Minecraft saves 자동 감지 + 월드 icon.png 썸네일 목록**, 완료 시스템 알림, Dock/작업표시줄 진행률, 닫기·종료 확인 시트, 창 크기/위치 기억, Finder/탐색기에서 백업·보고서 보기 |
| 정보 구조 | 웹 wizard(5단계 stepper). 스캔 화면은 버튼 하나, 실행 화면은 긴 폼 맨 아래 시작 버튼, 결과는 카드 8개, 보고서 내보내기 버튼이 제목과 설명 사이 | 작업 공간 하나 + 툴바. 읽기 전용 스캔은 월드 선택 시 자동, 실행은 요약 시트, 결과는 한 줄 요약 + 상세 펼치기 |
| 설정 | 긴 한 페이지 + 항상 떠 있는 저장 바(“저장된 설정과 같습니다”) | 탭(일반/제공사/번역/고급) 또는 별도 설정 창. 저장 바는 변경이 있을 때만 |
| 문구 | 안내문이 길고 중복(정보 화면 설명 2회, 각 화면 lead 2줄) | 짧은 라벨 + 필요할 때만 도움말 |

## 4. 개선 제안 (우선순위)

### U1 즉시 고칠 결함 (Phase 상태 변경 없음, 유지보수 수정)
F1·F4·F5·F6·F9, F2의 사고 토큰 집계, F10 헤더 전환. 모두 작고 범위가 명확하다.

### U2 네이티브 기반 (구조는 유지, 느낌을 바꿈)
1. 창: macOS overlay 타이틀바 + 사이드바 vibrancy, Windows Mica, 드래그 영역, 창 제목을 월드 이름으로. 창 상태 기억.
2. 스크롤 모델: `100dvh` 고정 shell, 콘텐츠 내부 스크롤, `overscroll-behavior: none`, 이동 시 top.
3. 밀도 토큰: 13px 본문, 32px 기본 컨트롤, radius 축소, 카드 그림자 제거(구분선), 버튼 scale 애니메이션 제거, 화살표 커서, `user-select` 정책.
4. 메뉴/단축키와 우클릭 메뉴(후보 행: 제외/포함/직접 번역/원문 복사).
5. OS 통합: 드래그&드롭, saves 자동 감지·썸네일, 알림·진행률, 닫기/⌘Q 확인 시트(F7).

### U3 정보 구조 재구성 (목업 승인 후)
- 월드 선택 화면 = Minecraft 런처처럼 썸네일 목록. 선택하면 읽기 전용 스캔 자동 실행(이미 API 0, 쓰기 0).
- 검토 화면을 메인 작업 공간으로: 사이드바 | 후보 목록 | 인스펙터(접기 가능). 툴바에 월드 이름·상태·“번역…” 버튼.
- 번역 실행 = 확인 시트(대상 수·예상 비용·백업 안내 + 시작). 진행은 툴바/하단 진행 영역에 표시하고 목록에 번역문이 채워짐.
- 결과 = 요약 한 줄 + 상세(토큰/비용/실패 목록) 펼치기 + 보고서 내보내기는 “더보기” 메뉴.
- 설정 = 탭 구조, 저장 바는 dirty일 때만.
- 마스코트는 빈 상태·정보 화면에서만 사용.

### U4 기능·품질
- Gemini thinking 제어를 추론 UI에 연결, 비 OpenRouter 제공사의 가격(날짜 명시) 기반 추정.
- 서식 코드(`§`) 위치 보존 품질 점검: 실제 호출에서 `§6Merchant §rof the Northern Gate` → `§6북쪽 성문의 §r상인`처럼 색이 다른 단어로 이동. 금지는 아니지만 프롬프트/검증 개선 후보.
- 모험 맵의 대사 다수가 datapack `.mcfunction`에 있으므로 CONTENT(datapack) 우선순위를 COMP-02 이후로 당길지 검토.

## 5. 작업 계획

AGENTS.md 순서(Phase2 완료 → COMP-01부터)를 유지하되, 기본 창 크기에서 보이는 결함과 사용량 과소 집계는 먼저 고친다.

| 단계 | 내용 | 검증(정책 준수) | Gemini 예산 |
| --- | --- | --- | --- |
| S0 | U1 결함 수정(F1·F2 집계·F4·F5·F6·F9·F10) | 관련 frontend unit, 해당 browser scenario(1180/1100/840 review, run/result), Python provider test. F7은 macOS에서 사용자 확인 필요 | 사고 토큰 집계 확인 1–2요청 (< $0.01) |
| S1 | COMP-01 SNBT 명령 + 미처리 명령 경고(F3) | extraction/release fixture, 결정적 mock, 합성 world write→reopen→restore hash | 합성 world 실제 E2E 1회 (< $0.05) |
| S2 | U2 네이티브 기반 1–3(창·스크롤·밀도) | check/build + browser layout 대표 폭, 마지막에 macOS native 확인(사용자 로컬) | 0 |
| S3 | U2 4–5(메뉴·단축키·드래그·saves 감지·알림·종료 확인) | Rust unit + browser + native 수동 | 0 |
| S4 | U3 정보 구조 재구성 — 먼저 HTML 목업으로 승인 | 화면별 browser workflow, 최종에 전체 browser/axe 한 번 | 0 |
| S5 | U4 + COMP-02/03 | 관련 fixture | 모델 비교(100문장 내외, thinking off/low) < $0.30 |
| 이후 | CONTENT(datapack), DATA/QUALITY(용어집·TM), RECOVERY, PLATFORM/LEGAL/RELEASE | 기존 follow-up-work 완료 조건 | 필요 시 |

예산 US$3 중 계획 사용량은 합계 약 US$0.5 이하이고 나머지는 예비다. 유료 호출은 mock 성공 뒤 최소 호출로만 하고, 매번 요청 수·토큰·(가능하면) 비용을 기록한다.

### 결정이 필요한 것
1. UI 방향: **U2(구조 유지 + 네이티브 느낌) 먼저 → U3는 목업 확인 후**를 권장한다. 한 번에 U3까지 가면 browser test 대부분을 다시 써야 한다.
2. 플랫폼 우선순위: 창 크롬·vibrancy는 OS별로 다르다. macOS를 1순위로 하고 Windows는 Mica/기본 타이틀바로 맞추는 것을 권장한다.
3. S0을 COMP-01보다 먼저 할지 — 권장: 먼저(작고, 기본 창 크기에서 바로 보이는 결함).
