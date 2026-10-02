# main 통합·잔여 작업 대조 — 2026-10-02

## 요청과 Git 통합

사용자 요청: 최신 원격 작업 브랜치의 변경을 main에 반영하고, 남은 작업을 코드와 대조해 갱신한다.

- 시작: clean `main` / `c26fcd7e78f9fb6c2d8c17dc398674a9e46705d0`.
- `git pull --ff-only origin main`: 이미 최신. 기존 fetch refspec은 main만 포함해 작업 브랜치를 숨겼다.
- 전체 heads 조회 후 `claude/review-and-plan-2026-10-01`을 fetch했다. fetch refspec을 전체 heads로 바꾸어 이후에도 작업 브랜치를 조회할 수 있게 했다.
- `git merge --ff-only origin/claude/review-and-plan-2026-10-01`: 충돌 없이 `e97261c67a6b183d7d0242a06e077deb1381bca4`까지 7개 commit/99개 파일 통합. 기존 commit과 작업 브랜치는 보존한다.
- 통합 후 이 기록과 상태 문서를 별도 정리 commit으로 저장한다. 최종 SHA·push 결과는 Git 기록을 따른다. Phase3 전체 완료 commit이나 공개 release가 아니다.

## 들어온 변경과 확인 근거

| 범위 | 코드 근거 | 판정·남은 경계 |
| --- | --- | --- |
| SNBT 명령 | `mwt/snbt.py`의 `parse`/`SnbtDocument.render`, `mwt/extract.py`의 `_walk_command`·EXTRACTOR_VERSION 3, `tests/test_snbt_commands.py` | COMP-01 구현·합성 fixture/E2E 기록. 실제 게임 버전 생성/로드는 COMP-04 |
| Gemini·서식 보호 | `llm_backends.py`의 thinking 설정·thoughtsTokenCount·헤더 인증·MAX_TOKENS·`_GEMINI_LEVEL_FLOOR`, `mwt/reasoning.py`, `mwt/tokens.py` | 기본 개선 구현. floor는 메모리 dict로 작업 간 영속화 없음. 가격표·부적합 모델 필터·용어/서식 인접 오류는 PROVIDER-01/QUALITY-01 |
| Native UX·월드 탐색 | `src-tauri/src/app_menu.rs`, `src/lib/native.ts`, `mwt/discovery.py`, shell/table/run/result CSS·motion | 메뉴·drop·saves·진행률·종료 보호·고정 shell·모션 구현. 최신 macOS native는 UX-NATIVE-01, 창 상태/우클릭/vibrancy/Mica는 UX-NATIVE-02 |
| 도움말·초기화·데이터 | HelpScreen/Tour/ResetDialog, `app.resetApp`, JSONL `prefs.set`/`app.reset`, `userdata.py`의 `reset_user_data`·`durable_write_text` | 구현됨. 설정 사본/손상 복구와 백업 유지. 모델 catalog는 atomic write만 제공하며 사본 복구 없음. OS 실제 폴더 열기·초기화/restart는 native gate |
| 라이선스·버전 | LicensesDialog, AboutScreen의 `appVersion`, `scripts/generate-licenses.mjs`, desktop build의 플랫폼별 고지 생성 | 앱 안 고지 뷰어·앱 버전 조회 구현. 실제 commit/SBOM 표시·target별 license 완전성·MPL source 안내 확인은 LEGAL-01 |
| 업데이트 | `updates.rs`, `lib.rs`의 `update_install` request gate, AppMaintenance, `tauri.conf.json` | 확인·알림·설치/재시작 경로 구현. 공개키 빈 값, latest.json 게시·실제 signed update/rollback·데이터 보존 검증은 RELEASE-01 |
| 화면 모드 | `public/theme-boot.js`, `startup_theme.rs`, app preferences·Settings 타일·보기 메뉴·OS 변경 추적 | 시스템/라이트/다크 구현. 후속 macOS/Windows 시작 깜빡임·타이틀바 색은 native 미확인 |

브랜치의 기록: Linux Python23/Rust30/frontend62/browser114 PASS 및 check/build, Gemini 합성 E2E. [후속 구현 기록](native-ux-and-compat-2026-10-01.md)과 [업데이트·데이터](../updates-and-data.md)의 당시 결과이며 이번에 실행한 테스트 결과가 아니다. Phase2 macOS 패키지/native 기록은 후속 source의 native 증거를 대신하지 않는다.

## 이번에 바로잡은 목록

- Phase3 미시작, JSON-only 명령 처리, 아직 COMP-01부터 시작해야 한다는 현재 요약을 COMP-01 완료/Phase3 진행 중으로 갱신했다. 과거 이력과 장기 설계는 보존한다.
- 공개 settings import/export/reset, 앱 전체 초기화·도움말·테마·고지 뷰어·앱 버전은 완료된 구현으로 분리했다. 사용자 font size/density·cache/TM 개별 삭제·commit/SBOM·실제 native는 남긴다.
- updater 전체를 미구현으로 부르지 않고 연결 구현과 실제 signed release 검증을 구분했다.
- 모델 catalog까지 설정과 동일한 사본 복구를 한다는 설명을 실제 atomic write/재조회 경계로 수정했다.
- 기존 20/58/28 및 macOS 패키지 hash의 Phase2 범위를 명시했다. 최신 Linux 기록을 새 macOS PASS로 승격하지 않는다.
- 제품 저장소 밖 상위 요약이 다음 작업을 잘못 안내하지 않도록 상위 workspace의 current-state와 계획서 현재 상태도 갱신했다. 상위 폴더는 제품 Git 저장소 밖이므로 해당 두 파일은 이 commit에 포함되지 않는다.

## 실제 남은 작업

기준 목록은 [추후 작업](../follow-up-work.md)이다. 우선 UX-NATIVE-01 → PROVIDER-01 → COMP-02/03/04 → QUALITY-01을 진행한다. COMP-05/06(pack·버전별 근거), CONTENT(datapack/storage/scoreboard/folder pack), DATA(occurrence/schema/SQLite), QUALITY(glossary/TM/비용), RECOVERY(crash/kill), 접근성·진단과 모듈 정리가 남아 있다. LEGAL-01/PLATFORM-01/RELEASE-01은 배포 완료 조건이며 최종 gate 대기다. U3 전면 화면 구조 변경은 당시 제안으로 보존한다.

이번 작업은 Git 이력·코드·문서 대조와 링크/diff 검사다. 테스트·빌드·앱 실행·유료 API·installer dispatch는 실행하지 않았다. 추가 API 비용0, 원본 world/credential 접근·변경0. 가져온 제3자 license 원문에는 trailing whitespace가 있어 통합 전체의 무제외 diff-check는 이를 보고한다. 원문을 보존하며 일반 코드/문서와 이번 정리 diff는 별도로 검사한다.

## 이번 통합 검사

- 정리 문서12개(상위 workspace2개 포함)의 로컬 링크 누락0.
- 이번 정리 diff-check PASS, 원문 license 파일을 제외한 전체 통합 코드/문서 diff-check PASS.
- 가져온 신규 파일의 world/DB/key/ZIP/app 등 runtime 경로 검출0, private-key/API-key 패턴 검출0. 패턴 검사는 완전한 비밀 검출 보장이 아니다.
- Luna Max 1개가 잔여 목록을 read-only 조사했고 Main이 SNBT parser·Gemini floor·설정/catalog 복구·업데이트 공개키/gate·About version/license 근거를 직접 확인했다.
- 대상 브랜치 tip이 main의 ancestor임을 확인했다. push 뒤 원격 main SHA와 작업 트리 상태를 확인한다.
