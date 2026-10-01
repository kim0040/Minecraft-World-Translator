# 추후 작업 — 2026-10-01

**Phase2 데스크톱 기능·macOS arm64 개발 환경 gate 완료 / Phase3 진행 중(COMP-01 완료) / release-ready 아님.** 이 문서는 미완 작업의 기준 목록이다. [최종 완료 증거](history/phase2-completion-2026-10-01.md)는 플랫폼·정식 배포 완료와 구분한다. 최신 구현은 [현재 상태](current-state.md), 범위별 증거는 [검증 이력](history/README.md)을 따른다.

2026-10-01 사용자 요청에 따른 [잔여 작업·Minecraft 호환성 확대 계획](compatibility-roadmap-2026-10-01.md)은 현재 코드의 버전/형식 공백과 실행 순서·완료 조건을 정리한 제안이다. Phase2 완료 후 Phase3에서 SNBT 명령·최신 component·혼합 버전 검증을 우선한다. 초기 계획 작성 자체는 지원 범위나 Phase 상태를 변경하지 않았으며, 후속 구현·최종 검증으로 Phase2 개발 환경 gate를 완료했다. 후속 요청의 [샘플·시작 복구·실제 provider 검증](history/sample-startup-validation-2026-10-01.md)을 추가했으며 게임 버전 전체 지원은 선언하지 않는다.

## 다음 작업의 우선순위와 완료 조건

| ID | 작업 | 현재 경계·선행 조건 | 완료 조건 |
| --- | --- | --- | --- |
| P2-API 완료 | 실제 provider 최소 E2E | 최소 E2E PASS: 합성3문장/1요청, provider-reported $0.0001484, world4+ZIP1 hash 차이0 복원 | 합성 world에서 mock 성공 후 최소 실제 번역; endpoint·요청/tokens/실제 cost·usage 전후 기록, verified backup/restore와 world4+ZIP1 baseline hash 차이0 |
| P2-START 완료 | startup 지연·무응답 복구 | 개발 환경 targeted/native PASS: hello30초/bootstrap60초 오류·cleanup·retry/cold Ready. 과거 blank 원인·clean-machine는 미확정 | 무응답/지연 sidecar·저장소 fixture, handshake/bootstrap deadline·오류 안내·소유 process cleanup; native 재시작 증거. write 전체에 무조건 timeout을 적용하지 않음 |
| P2-PARITY 완료 | 문서화한 Legacy 대체 범위 | 항상 백업·앱 관리 backup/checkpoint 유지, off/suffix/path 차이 명시 | 기존 안전 구현의 범위·literal import·legacy restore 검증. 동등 옵션/100% parity 아님, Legacy 유지 |
| P2-FINAL 완료 | 최종 Phase2 개발 환경 gate | Python20/frontend58/build/Rust28, browser86+수정 후 영향7 및 최종 native .mcc PASS | 검증·증거 재사용 경계 명시, docs/diff/secret/artifact review→완료 commit/push. 플랫폼/release gate 별도 |
| UX-NATIVE-01 | 네이티브 UX 후속의 macOS 확인 | 2026-10-01 구현·Linux Rust/browser94 PASS. [기록](history/native-ux-and-compat-2026-10-01.md) | Python 변경이 있으므로 sidecar 재빌드 후 macOS dev app에서 overlay 타이틀바·신호등·드래그 영역, 메뉴 라벨/단축키, ⌘Q 보호(작업 중), 폴더 drop, saves 목록, Dock 진행률/attention, 다크 시작 깜빡임을 확인하고 결함 수정 |
| UX-NATIVE-02 | 남은 네이티브 다듬기 | 미착수 | 사이드바 vibrancy(투명 창 필요 여부 결정), 후보 행 우클릭 메뉴(포함/제외/직접 번역/복사), 창 크기·위치 기억, Windows Mica/타이틀바 확인 |
| LEGAL-01 | 배포물 라이선스·고지 | source MIT 유지. Cargo192 metadata 미확인, 모든 OS 고지 미완 | target별 포함 목록·SBOM·전체 license/NOTICE·MPL source 안내·Python/native library 고지를 package에 동봉. 충돌 미해결이면 해당 배포 보류 |
| PLATFORM-01 | clean-machine·키체인 | macOS arm64 개발 앱·Local/Session 검증; OS keychain opt-in/Windows/Linux native 미완 | Python/Node/Rust 없는 각 목표 OS에서 설치·chooser·credential permission/import·restart·backup/restore 확인; macOS Intel 목표 결정 |
| RELEASE-01 | 서명·업데이트·설치 배포 | unsigned 개발 bundle이며 updater/release 미완 | 실제 credential 승인 후 signing/notarization, updater signature/rollback·data 유지·진행 중 write 처리 검증 |
| DOCS-01 | 문서·화면 유지 | 이번 서비스 소개·합성 screenshot·면책·개발 안내 정리 | 기능/지원/credential/가격 정책이 바뀔 때 소개·user-guide·privacy·support evidence와 화면을 같이 갱신; 목표를 검증된 기능으로 표시하지 않음 |

## 이번에 완료한 범위

- [x] 2026-10-01 후속: COMP-01 SNBT 명령(선행 `/`·문자열 컴포넌트 포함, 미해석 경고), Gemini thinking/사고 토큰/헤더 인증/잘림 처리, 서식 토큰 완전 일치 검사, 기본 창 크기 후보 표 원문 열 결함 수정, 데스크톱 셸·밀도·메뉴·drop·saves 목록·진행률·⌘Q 보호. Python22/Rust28/browser94, 실제 Gemini 13요청. [기록](history/native-ux-and-compat-2026-10-01.md)

- [x] 신규 .mcc 생성 경계·백업·중간 write 실패·recovery roundtrip와 물리 파일 집계 수정. 최종 native 변경2/API0/원래2파일 복원 hash 차이0.
- [x] Legacy 대체 범위와 최종 개발 환경 gate 정리. SourceOverrides 오류 해소 시 입력창 닫힘 수정, Python20/frontend58/browser 영향7 PASS.

- [x] 실제 샘플6개에서9435청크 읽기·NBT byte-identical·원본 보존. Roguefire 복사본12후보 쓰기/reopen/전체117파일 복원 hash 차이0. 공개5개는 후보0으로 쓰기 검증 대상이 아님.
- [x] startup 절대 deadline·오류·재시도와 무응답 native cleanup, frontend58/browser-startup5/Rust28/build 및 Python 영향 검사.
- [x] 합성3문장 실제 OpenRouter 번역1회, 입력391/출력108 tokens, provider 비용$0.0001484, 실제 backup/restore world4+ZIP1 hash 차이0.
- [x] 승인된 추론/설정 여섯 UI/UX 개선과 고정 sidebar/savebar.
- [x] 모델 공개 조회와 설정 저장 분리, default/disable/custom·지원 강도·캐시/오류 상태.
- [x] 관련 frontend28/browser30(29+1)/Rust24·Python provider 두 파일·최종 build·native 저장/재시작/기본값 복원. [정확한 범위](history/settings-ux-2026-10-01.md)
- [x] 외부 ZIP manual run/backup/restore와 물리 변경 파일 집계 수정. 이전 native 기준5파일 hash 차이0.
- [x] 검증 executor/cache/invalidation/cancel/lock 후속 및 screenshot 중복 통합. 이전 최적화 증거를 보존한다.
- [x] README 서비스 소개·사용법·실제 UI 화면, contributor·MIT·면책/개인정보·제3자 검토 문서.
- [x] 과거 인계를 history로 이동하고 현재 상태와 미완 작업을 분리; runtime/world/DB/key/report 생성물 Git 제외.

이전 전체19 Python/50 frontend/71 browser PASS는 UX 이전 소스의 이력이다. 위 targeted PASS를 전체 matrix·actual provider·release-ready로 확대하지 않는다. 실제 최소 E2E와 공개 models GET은 전체 번역 품질·모든 제공사·최종 청구서 검증을 대신하지 않는다.

## Phase 3 — 진행 중

- [x] COMP-01 SNBT 명령 텍스트(합성 fixture·실제 Gemini 합성 world E2E). 1.21.5+ 실제 생성 맵의 게임 로드는 COMP-04.

- [ ] datapack visible text / command storage / scoreboard 조사, opt-in 지원과 detected/unsupported/preserved coverage.
- [ ] external folder pack/fill/merge, collision·path 안전성. ZIP/source·target locale/overwrite·skip는 Phase2 구현, native gate PASS.
- [ ] occurrence별 include/exclude와 전체 위치 lazy query.
- [ ] scan/override/checkpoint/resume schema migration.
- [ ] candidate/occurrence/glossary/TM/job history SQLite 범위·indexes·migration/rollback.
- [ ] world/global glossary와 규칙·revision·import/export/delete.
- [ ] revision/context-aware TM, world 격리, 잘못된 번역 무효화·편집·삭제.
- [ ] provider 가격·시각 기반 token/cost low/high 추정과 실제 usage 비교, resume 남은 분량.
- [ ] Java 버전/압축/entities/dimensions/large/corrupt/mixed/emoji/NUL compatibility.
- [ ] crash/kill 뒤 interrupted 복구, consistency 검사, 사용자 restore/resume/discard.
- [ ] 자연스러운 core/desktop 모듈 분리, CLI·legacy 설정 호환.
- [ ] screen reader/high contrast, font size/density, diagnostics redaction, cache/TM 삭제·settings export/reset.
- [ ] About에 배포물별 third-party notices/SBOM 연결, 실제 version/commit 표시. 소스 MIT·제3자 검토 문서는 작성했지만 binary license gate는 미완이다.
- [ ] macOS Apple Silicon/Windows x64/Linux x64 clean-machine; macOS Intel 목표 유지 시 별도.
- [ ] installer sidecar/dependencies/assets/data/chooser/credential/restart/update 확인.
- [ ] 실제 credential이 있을 때 signing/notarization/updater verification·rollback.
- [ ] docs/support matrix를 실제 근거와 일치시킨 뒤 Phase 3 commit → push.

## 실행·비용·배포 경계

원본 sample 쓰기 금지. 합성 또는 복사본에서 SHA-256 baseline을 기록하고 쓰기·복원 전후를 비교한다. 추가 실제 API 비용은 이번 제공사 응답 기준 $0.0001484다. 실제 E2E의 기존 허용 예산은 추가 총 $1 이하(목표 $0.01–$0.10)이며 mock 먼저·최소 호출 원칙을 따른다. 최소 E2E는 완료했고 같은 입력의 유료 호출을 반복하지 않는다.

[CI 정책](ci-policy.md)에 따라 일반 문서/UI 변경은 Python CI를 시작하지 않으며 installer는 manual/tag이다. 이전 진행 저장은 `[skip ci]` checkpoint였다. 이번 Phase2 완료 push의 Python/CI 변경은 자동 core 검사의 대상이며 installer/release dispatch는 하지 않는다. 공개 release·서명 자격·사용자 world upload는 별도 확인 없이 하지 않는다.

맵 재배포·상표·의존성 권리는 [면책 안내](disclaimer.md)와 [라이선스 검토](legal/license-review.md)를 따른다. 미검증을 완료라고 쓰지 않고 충돌을 발견하면 기록·해결한 뒤 해당 배포를 재개한다.
