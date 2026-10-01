# 현재 상태 — 2026-10-01

## 판정

**Phase2 진행 중 / Phase3 미시작 / release-ready 아님.** 개발 기준은 `main` / `9817d54` checkpoint다. 이후 추론·설정 개선과 문서 정리는 사용자 요청의 진행 저장으로 묶는다. 최신 commit/push 상태는 Git 기록으로 확인하며 Phase 완료 commit으로 취급하지 않는다.

최신 증거는 [설정·추론 UI/UX 개선](history/settings-ux-2026-10-01.md), 이전 증거는 [2026-10-01 재개·검증](history/phase2-resume-2026-10-01.md), 전체 backlog는 [남은 작업](follow-up-work.md)이다. 과거 중단 기록은 현재 실행 상태를 덮어쓰지 않는다.

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

## 문서·라이선스 정리

서비스 소개와 사용법은 root README, 자세한 실행·복원은 user-guide, 비용·키 저장은 privacy, 개인 프로젝트/보증·책임 제한은 disclaimer로 구분했다. 기여자는 김현민(mini0227kim@gmail.com)이다. 기존 MIT를 유지하고 제3자 metadata 검토·미확인 플랫폼/배포 고지를 legal 문서와 LEGAL-01에 기록했다. 날짜별 기록은 history, 의도적인 합성 소개 화면은 images에서 관리한다. 이번 문서 작업으로 유료 API·전체 matrix·installer 빌드를 실행하지 않았다.

## 현재 검증

| 영역 | 최신 증거 | 범위 |
| --- | --- | --- |
| Python | provider 관련 두 파일 PASS | 공개 모델 조회·cache·request mock; 전체19 suites는 UX 이전 증거 |
| Frontend | 관련4 files /28 PASS | reasoning/i18n/settings/settings-import; 전체50은 UX 이전 증거 |
| Browser | 관련30개 PASS (29+1 실행) | 설정/추론/키 관리/preflight/320·840·1440/axe; 전체71은 UX 이전 증거 |
| Type/build | 0 errors /0 warnings, production build PASS | 최종 UI source |
| Rust | 24 PASS | vault/routing 및 공개 조회 bypass 제한 |
| Packaging | sidecar + unsigned debug Eval app PASS (59.20 MiB) | 최신 macOS arm64, shared cache; clean-machine 검증 아님 |
| Native | 추론 저장/재시작/Run 요약/기본값 복원 PASS | 사용자 모델·저장된 키 유지; 합성 기준5파일 hash 차이0 |
| Real API | key/model 등록 완료, 실제 번역 E2E NOT RUN, 추가 비용 $0 | 모델 공개 GET200; 유료 번역·cost/restore는 미검증 |

최신 화면·정확한 패키지 hash와 targeted 범위는 설정 UI/UX 문서를 따른다. 기존 외부 ZIP manual run/restore·native 200% 확대와 전체 matrix는 이전 소스의 범위별 증거이며, 이번 소스의 전체 release gate PASS로 복사하지 않는다.

## 지원 경계와 남은 gate

스캔은 각 차원의 `region`/`entities`, 선택 시 월드 안의 일반 파일 `resources.zip`과 명시적으로 선택한 외부 ZIP이다. datapack, command storage, scoreboard, playerdata, level.dat visible text, folder pack/merge는 아직 스캔·번역 지원하지 않는다. 명시 선택 외부 ZIP은 구현 및 Python/browser 검증을 마쳤으며 native 번역/백업/복원 후 기준5파일 hash 차이0을 확인했다. [fixture 지원 표](support-matrix.md)의 supported는 해당 합성 형식을 통과했다는 뜻이며 모든 Java 버전/모든 실제 월드 지원은 아니다.

Legacy UI/launcher는 유지한다. [기능 비교](legacy-ui-parity.md)의 외부 팩·앱 관리 backup/checkpoint 대체 범위는 최종 Phase 계약 확인 전이며 기능 parity 완료로 표시하지 않는다.

실제 provider/usage/cost/restore, 남은 범위 결정과 최종 diff review 후에만 Phase2 **완료** commit → push한다. 사용자 요청의 현재 checkpoint 저장은 이 완료 판정과 구분한다. Phase 3 및 Windows/Linux clean-machine, signing/notarization/updater/release는 남아 있다. [CI 정책](ci-policy.md)은 main의 관련 Python 변경/PR만 자동 core 검사, installer manual/tag, 수동 기본 Linux다. 이번 작업은 CI를 dispatch하지 않았다.
