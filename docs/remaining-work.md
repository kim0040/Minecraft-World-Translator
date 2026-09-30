# PomiTranslate 남은 작업 — 2026-09-30

기준 관측: `main` / `e70d27a`, 문서 갱신 전 clean. local feature ref도 같은 commit. 기존 `4c50a6e` 기반 목록은 아래 최신 인계로 대체한다.

이 문서는 요약이고, **실행 순서·검증 기록·안전 경계·명령은 [전체 인계](agent-handoff-2026-09-30.md)**가 기준이다. credential 변경은 [상세 저장 계획](credential-storage-plan.md)을 따른다.

## Phase 2 — 구현 존재, 완료 gate 미통과

- [ ] Rust 로컬 encrypted credential DB + 설치별 master key + 플랫폼 permission.
- [ ] local 기본 / session-only / opt-in keychain, 기존 키 가져오기·rollback, CLI 호환.
- [ ] keychain 상태 확인을 실제 secret read에서 metadata 조회로 변경.
- [ ] public provider/Custom endpoint 최종 Rust boundary 및 POMI_* 환경변수의 UI 설정 덮어쓰기 차단/계약 회귀.
- [ ] restore 후 result step이 남는 state/화면 문제 해결.
- [ ] 모든 페이지 기능·i18n·theme·responsive·keyboard 최종 확인.
- [ ] candidate 10k/100k 실제 virtual DOM·memory·latency. virtual range unit test와 구분.
- [ ] legacy Web UI 기능 parity 표와 gap 해소. 확인 전 삭제 금지.
- [ ] frontend/Python/Rust/sidecar/Tauri build 전체 gate.
- [ ] 14 screenshot inspection, 1440/1180/1024/840/320, 200%, dark.
- [ ] 실제 Tauri workflow, 최소 실제 provider 호출·usage/비용, backup/restore byte-identical.
- [ ] 문서/diff review 후 Phase 2 완료 commit → push.

이전 frontend/Python/Rust/build, browser 접근성·화면 검사, 실제 Tauri mock 번역/복원 기록은 있다. 최종 endpoint 수정 후 실제 provider 실행은 완료하지 않았다. 후속 paid API 추가 비용 기록은 $0이며 Phase 1 과거 비용과 구분한다. 이번 문서 작업에서는 테스트를 재실행하지 않았다.

현재 virtual table은 구현돼 있다. paging 200개와 bounded row DOM을 사용하는 코드가 있으나 100k 실제 성능 완료를 뜻하지 않는다. UI locale는 ko/en/ja이고 중국어 README와 중국어 UI는 별개다.

## Phase 3 — 미시작

- [ ] datapack visible text / command storage / scoreboard 조사, opt-in 지원과 detected/unsupported/preserved coverage.
- [ ] external pack ZIP/folder, source/target locale, overwrite/skip/fill/merge, collision·path 안전성.
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
- [ ] About/license/third-party notices/SBOM, 실제 version/commit 표시.
- [ ] macOS Apple Silicon/Windows x64/Linux x64 clean-machine; macOS Intel 목표 유지 시 별도.
- [ ] installer sidecar/dependencies/assets/data/chooser/credential/restart/update 확인.
- [ ] 실제 credential이 있을 때 signing/notarization/updater verification·rollback.
- [ ] docs/support matrix를 실제 근거와 일치시킨 뒤 Phase 3 commit → push.

## 배포와 안전

일반 feature push에 3 OS installer를 전부 돌리지 않는다. installer는 manual/tag, 수동 기본 Linux이며 최종 gate에 cross-platform 검증을 수행한다. 서명 credential 없으면 unsigned development build로 기록한다.

원본 sample write 금지. `/private/tmp/pomi-eval/` copy에서 hash snapshot·번역·restore 비교. 알 수 없는 형식이나 unreadable chunk/provider 실패를 성공으로 보고하지 않는다.

유료 최종 E2E는 기존 명시 허용 범위인 추가 총 $1 이하, 목표 $0.01–$0.10. mock 먼저, 마지막 최소 호출, 실제 endpoint·usage·비용 확인. 공개 release·서명 자격·사용자 월드 업로드는 별도 승인 없이 수행하지 않는다.

현재 release-ready가 아니다. Phase 2 최종 통합 검증, 새 credential 저장, Phase 3 및 플랫폼/서명 gate가 남아 있다.
