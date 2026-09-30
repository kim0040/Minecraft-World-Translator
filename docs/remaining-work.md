# PomiTranslate 남은 작업 — 2026-10-01

> **최신 결정 — 검증 최적화 후 중간 저장/중단:** 사용자 요청으로 실행 정책·명령을 반영하고 현재 WIP를 checkpoint commit/push한다. Phase2 완료 commit이 아니며 Phase3 미시작이다. [검증 실행 정책](verification-policy.md)과 아래 최적화 후속 기록을 우선한다. 테스트·개발 서버·Eval 앱은 종료됐으며 내일 재개 전 새 검사/빌드를 실행하지 않는다.

> **2026-10-01 중단 갱신:** [최신 중단·인계](phase2-pause-2026-10-01.md)가 아래 진행 기록보다 우선한다. 외부 ZIP/사용량 조회 후속 구현과 검증 시점, 재개 순서는 해당 문서를 따른다. [테스트 지연 조사](test-efficiency-audit-2026-10-01.md)도 기록했다. Phase2 미완/Phase3 미시작, commit/push 없음.

현재 `main` / `865b51d`에 모든 WIP를 보존했다. **Phase 2 미완 / Phase 3 미시작**, 완료 commit/push 없음. [최신 검증·인계](phase2-validation-2026-10-01.md)가 과거 진행/중단 기록보다 우선한다.

## 내일 첫 작업 — 검증 최적화 후속

- [x] 빠른/최종/계획 명령, 성공 증거 재사용, incremental/clean sidecar 분리, 중복 screenshot/result-failed 통합, AGENTS/정책 갱신.
- [x] 문법·계획 출력·diff/link 확인. 실제 runner/Eval 앱/개발 포트 종료.
- [ ] 새 executor cache/invalidation/failed/interrupted/lock 및 화면 artifact mapping의 targeted runtime 검증. 오늘 테스트는 중단했으므로 NOT RUN.
- [ ] 이후 기존 Phase2 gate만 계속 진행. 도구 변경 때문에 unrelated 전체 검사를 반복하지 않는다.

## Phase 2 gate

- [x] compile/check/production build, Python 전체17 suites, frontend48, Rust23, sidecar package, unsigned isolated Tauri debug app.
- [x] 기본 local encrypted vault/session/opt-in keychain, atomic stale-key 제거·rollback·endpoint validation, 실제 합성 Local→Session→restart→Local 검증.
- [x] 브라우저 전체64 PASS/56.7초, 대표14 screenshot inspection, 모든 페이지·100k bounded DOM/cache·filter counts·keyboard·resize·dark·840/320/a11y.
- [x] isolated native mock scan/run/progress/cancel/backup/restore 및 원본4파일 byte-identical, public setting persistence와 native literal Python chooser preview.
- [x] 실제 native 200% 확대, 상세 입력/Tab/하단 닫기/ESC·복원 확인·설정 하단 actions. 대화상자 애니메이션 렌더링 결함 수정 후 재검증.
- [x] 재개 시 최신 검토 덮어쓰기 결함 수정. Python RED/GREEN, 최신 native 제외2/manual1/request0/changed1 및 원본4파일 복원 PASS.
- [x] 월드 외부 symlink 입력을 provider/읽기 전에 차단, 대형 데이터 스트리밍 해시, 자동 회귀6개.
- [ ] 실제 provider 최종 E2E 및 usage 전후/실제 cost/restore. 실제 API key는 사용자가 eval 앱에서 직접 입력·저장해야 함. 예산≤$1, 이번 추가비용$0.
- [x] Legacy arbitrary external ZIP 선택/scan/translate/verified backup/restore 구현과 Python/browser 검증.
- [ ] 최신 external ZIP native gate 및 app-managed backup/checkpoint 대체 차이 확인. Folder/merge는 Phase3 확장.
- [x] 최신 native 정상 종료→cold restart→Loading→Ready/최근 월드 경로 유지 확인.
- [ ] 이전 한 번의 지속 blank 원인과 clean-machine startup 안정성. 최신 재빌드 restart PASS를 전체 플랫폼 성능 gate로 확대 해석 금지.
- [ ] 최종 docs/diff/secret-artifact review → Phase2 완료 commit → push.
- [ ] 위 gate 이후에만 Phase3 구현 착수. legacy 제거/launcher 전환은 parity 충족 뒤.

## Phase 3 — 미시작

- [ ] datapack visible text / command storage / scoreboard 조사, opt-in 지원과 detected/unsupported/preserved coverage.
- [ ] external folder pack/fill/merge, collision·path 안전성. ZIP/source·target locale/overwrite·skip는 Phase2 구현, 최신 native gate가 남음.
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

[CI 실행 정책](ci-policy.md): UI/브라우저 테스트 변경은 Python CI를 시작하지 않는다. 일반 feature push에 3 OS installer를 전부 돌리지 않는다. installer는 manual/tag, 수동 기본 Linux이며 최종 gate에 cross-platform 검증을 수행한다. 서명 credential 없으면 unsigned development build로 기록한다.

원본 sample write 금지. `/private/tmp/pomi-eval/` copy에서 hash snapshot·번역·restore 비교. 알 수 없는 형식이나 unreadable chunk/provider 실패를 성공으로 보고하지 않는다.

유료 최종 E2E는 기존 명시 허용 범위인 추가 총 $1 이하, 목표 $0.01–$0.10. mock 먼저, 마지막 최소 호출, 실제 endpoint·usage·비용 확인. 공개 release·서명 자격·사용자 월드 업로드는 별도 승인 없이 수행하지 않는다.

현재 release-ready가 아니다. Phase2 actual provider·범위 계약·최종 검증과 Phase3·플랫폼/서명 gate가 남아 있다.
