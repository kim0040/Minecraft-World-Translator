# 현재 상태 — 2026-10-01

> **최신 결정 — 검증 최적화 후 중간 저장/중단:** 사용자 요청으로 실행 정책·명령을 반영하고 현재 WIP를 checkpoint commit/push한다. Phase2 완료 commit이 아니며 Phase3 미시작이다. [검증 실행 정책](verification-policy.md)과 아래 최적화 후속 기록을 우선한다. 테스트·개발 서버·Eval 앱은 종료됐으며 내일 재개 전 새 검사/빌드를 실행하지 않는다.

> **2026-10-01 중단 갱신:** [최신 중단·인계](phase2-pause-2026-10-01.md)가 아래 진행 기록보다 우선한다. 외부 ZIP/사용량 조회 후속 구현과 검증 시점, 재개 순서는 해당 문서를 따른다. [테스트 지연 조사](test-efficiency-audit-2026-10-01.md)도 기록했다. Phase2 미완/Phase3 미시작, commit/push 없음.

## 판정

**Phase 2 진행 중 / Phase 3 미시작 / release-ready 아님.** 현재 체크아웃은 `main`, HEAD `865b51d`이며 모든 기존 및 후속 미커밋 작업을 보존한다. Phase 완료 commit/push는 아직 없다.

최신 실행 증거와 정확한 다음 단계는 [2026-10-01 검증·인계](phase2-validation-2026-10-01.md), 전체 backlog는 [남은 작업](remaining-work.md)이다. 9월 30일의 중단·진행 문서는 당시 이력이며 현재 상태를 덮어쓰지 않는다.

## 구현한 제품

- Tauri 2 / Rust shell / Svelte 5 / TypeScript / Vite, 패키지된 Python JSONL sidecar. 기존 CLI와 같은 코어를 사용하며 desktop은 localhost 서버를 열지 않는다.
- World → Scan → Review → Run → Result, Backups / Settings / About 분리와 공통 shell·dialog·toasts.
- 고유 후보·발생 횟수·종류·좌표/청크, 검색·종류/포함/제외/직접 번역 필터·정렬·서버 paging·bulk·virtual table. 100k fixture에서 DOM과 페이지 캐시가 제한됨을 브라우저로 검증했다. 실제 100k 월드 전체 처리 성능은 별도다.
- model/provider/성능 변경은 scan 유지; 번역 범위/대상 언어 변경은 invalidation. 결과 상태·진행 event는 사용자 문구로 표시한다.
- 재개 요청의 최신 후보 제외·직접 번역을 우선 적용하며, 이전 클라이언트가 생략한 필드만 checkpoint로 보충한다. Native 회귀에서 변경 파일1/요청0/최신 번역문을 확인하고 대상4파일 byte-identical 복원했다.
- Collect → Translate → Write, provider fail-fast/circuit breaker, checkpoint·retry·cancel, 사용량·실패·경고 보고. 취소 뒤 늦게 도착한 응답 사용량도 최종 보고에 합산한다.
- NBT 원본 바이트 보존, Java modified UTF-8(NUL/CESU-8 emoji), nested component·extra/with/fallback/hover/click/container/text_display/command text 추출.
- 앱 데이터의 검증된 백업, legacy `.pomi-backups` 발견/복원, 복원 직전 recovery snapshot.
- 기본 credential은 Rust SQLite/AES-256-GCM + 별도 설치별 key 파일. Session과 opt-in OS keychain; 자동 keychain 읽기/import 없음. 저장된 키 전체는 UI에 반환하지 않는다. Local→Session 전환 시 stale local ciphertext 제거를 atomic metadata transaction으로 처리한다.
- 같은 계정으로 DB와 key 파일을 모두 읽는 프로세스까지 막는 설계는 아니다. Windows permission 코드는 target typecheck만 통과했으며 native 검증 전이다.
- OpenAI/Gemini/Anthropic/OpenRouter/Comet/Custom, provider endpoint 고정과 Custom wire format·URL 검증. CLI 환경변수 호환과 Rust-owned sidecar 환경변수 차단을 구분한다.
- 설정 그룹/disclosure, 종류별 scope 및 curated presets, 파일/key 규칙, global source overrides, performance/file retry/error 정책, 공개 JSON import/export/reset, literal `translate.py` 읽기 전용 preview, 명시적 확인 후 style helper.
- System/Light/Dark 및 ko/en/ja semantic i18n. 중국어 UI는 현재 제공하지 않는다.
- native View 메뉴의 75–200% 실제 WebView 확대. Cmd/Ctrl+0은 100%, Cmd/Ctrl+2는 200%. Dialog는 명시적 fixed 위치·동적 viewport 높이를 사용하고, native에서 보이지 않던 등장 애니메이션을 제거했다.
- alternate app identifier는 명시적인 sidecar data root로 격리한다. 테스트 설정·DB·키·월드가 production root로 흘러가지 않는다.
- 선택한 월드 밖으로 연결된 level/region/entity/resource pack은 읽기·API 전에 차단한다. resources.zip symlink는 내부 대상이어도 restore 경로 보존을 위해 차단한다. 큰 파일 지문/백업 해시는 스트리밍한다.

## 현재 검증

| 영역 | 최신 증거 | 범위 |
| --- | --- | --- |
| Python | 전체 17 suites PASS | core, fixtures, reliability, extraction, desktop, 경로 차단 |
| Frontend | 9 files / 48 tests PASS | formatter/virtual/state/settings/candidates |
| Browser | 전체 64 tests PASS (56.7초) | 동일 제품 UI fixture, responsive/keyboard/100k/filter/a11y |
| Type/build | check 0 errors/0 warnings, production build PASS | test entry와 production entry 구분 |
| Rust | 23 tests PASS | vault/rollback/routing/export/data root |
| Packaging | sidecar + unsigned debug eval app PASS (59.17 MiB) | macOS Apple Silicon local development build |
| Native | mock run/cancel/restore, 최신 검토 resume, credential mode/restart, literal chooser PASS | 합성·격리 데이터, 실제 provider 검증 아님 |
| Zoom | 실제 native 200% 상세 입력·Tab·닫기·ESC·복원 확인·설정 actions 확인 | CSS zoom/DPR 대체 아님 |
| Real API | NOT RUN, 추가 비용 $0 | eval의 실제 key 직접 등록 필요 |

브라우저의 14개 대표 screenshot을 생성하고 직접 점검했다. 1440×900/1180×800/1024×768/840×620/320px, ultrawide/세로/짧은 높이/연속 resize, dark와 keyboard 검사가 포함된다. Native의 정확한 실행/복원 기록은 최신 검증 문서를 따른다.

## 지원 경계와 남은 gate

스캔은 각 차원의 `region`/`entities`, 선택 시 월드 안의 일반 파일 `resources.zip`과 명시적으로 선택한 외부 ZIP이다. datapack, command storage, scoreboard, playerdata, level.dat visible text, folder pack/merge는 아직 스캔·번역 지원하지 않는다. 명시 선택 외부 ZIP은 구현 및 Python/browser 검증을 마쳤으며 최신 native gate는 남아 있다. [fixture 지원 표](support-matrix.md)의 supported는 해당 합성 형식을 통과했다는 뜻이며 모든 Java 버전/모든 실제 월드 지원은 아니다.

Legacy UI/launcher는 유지한다. [기능 비교](legacy-ui-parity.md)의 외부 팩·앱 관리 backup/checkpoint 대체 범위는 최종 Phase 계약 확인 전이며 기능 parity 완료로 표시하지 않는다.

실제 provider/usage/cost/restore, 남은 범위 결정과 최종 diff review 후에만 Phase 2 commit → push한다. Phase 3 및 Windows/Linux clean-machine, signing/notarization/updater/release는 남아 있다. [CI 정책](ci-policy.md)은 main의 관련 Python 변경/PR만 자동 core 검사, installer manual/tag, 수동 기본 Linux다. 이번 작업은 CI를 dispatch하지 않았다.
