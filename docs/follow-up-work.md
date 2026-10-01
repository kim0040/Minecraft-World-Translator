# 추후 작업 — 2026-10-01

**Phase2 진행 중 / Phase3 미시작 / release-ready 아님.** 이 문서는 미완 작업의 기준 목록이다. 문서 정리와 현재 개선 저장은 checkpoint이며 Phase2 완료나 정식 배포를 뜻하지 않는다. 최신 구현은 [현재 상태](current-state.md), 범위별 증거는 [검증 이력](history/README.md)을 따른다.

## 다음 작업의 우선순위와 완료 조건

| ID | 작업 | 현재 경계·선행 조건 | 완료 조건 |
| --- | --- | --- | --- |
| P2-API | 실제 provider 최소 E2E | 사용자 OpenRouter key/model 등록 완료. 실제 유료 번역은 미실행 | 합성 world에서 mock 성공 후 최소 실제 번역; endpoint·요청/tokens/실제 cost·usage 전후 기록, verified backup/restore와 world4+ZIP1 baseline hash 차이0 |
| P2-START | startup 지연·무응답 복구 | 과거 지속 blank 원인은 확정되지 않음. 최근 cold restart Ready는 확인 | 무응답/지연 sidecar·저장소 fixture, handshake/bootstrap deadline·오류 안내·소유 process cleanup; native 재시작 증거. write 전체에 무조건 timeout을 적용하지 않음 |
| P2-PARITY | legacy backup/checkpoint 대체 계약 | desktop은 앱 관리 backup/checkpoint; legacy off/suffix/path와 차이 | 사용자 범위 결정, 대체/미지원 명시, 필요한 migration·설명과 workflow 검증. parity 전 legacy 제거 금지 |
| P2-FINAL | 최종 Phase2 gate | 최신 UX는 targeted PASS; 이전 전체 matrix는 다른 source | 최종 후보에 맞는 검사 선택·유효 PASS 재사용, 잔여 위험 검증, docs/diff/secret/artifact review 후 Phase 완료 commit/push |
| LEGAL-01 | 배포물 라이선스·고지 | source MIT 유지. Cargo192 metadata 미확인, 모든 OS 고지 미완 | target별 포함 목록·SBOM·전체 license/NOTICE·MPL source 안내·Python/native library 고지를 package에 동봉. 충돌 미해결이면 해당 배포 보류 |
| PLATFORM-01 | clean-machine·키체인 | macOS arm64 개발 앱·Local/Session 검증; OS keychain opt-in/Windows/Linux native 미완 | Python/Node/Rust 없는 각 목표 OS에서 설치·chooser·credential permission/import·restart·backup/restore 확인; macOS Intel 목표 결정 |
| RELEASE-01 | 서명·업데이트·설치 배포 | unsigned 개발 bundle이며 updater/release 미완 | 실제 credential 승인 후 signing/notarization, updater signature/rollback·data 유지·진행 중 write 처리 검증 |
| DOCS-01 | 문서·화면 유지 | 이번 서비스 소개·합성 screenshot·면책·개발 안내 정리 | 기능/지원/credential/가격 정책이 바뀔 때 소개·user-guide·privacy·support evidence와 화면을 같이 갱신; 목표를 검증된 기능으로 표시하지 않음 |

## 이번에 완료한 범위

- [x] 승인된 추론/설정 여섯 UI/UX 개선과 고정 sidebar/savebar.
- [x] 모델 공개 조회와 설정 저장 분리, default/disable/custom·지원 강도·캐시/오류 상태.
- [x] 관련 frontend28/browser30(29+1)/Rust24·Python provider 두 파일·최종 build·native 저장/재시작/기본값 복원. [정확한 범위](history/settings-ux-2026-10-01.md)
- [x] 외부 ZIP manual run/backup/restore와 물리 변경 파일 집계 수정. 이전 native 기준5파일 hash 차이0.
- [x] 검증 executor/cache/invalidation/cancel/lock 후속 및 screenshot 중복 통합. 이전 최적화 증거를 보존한다.
- [x] README 서비스 소개·사용법·실제 UI 화면, contributor·MIT·면책/개인정보·제3자 검토 문서.
- [x] 과거 인계를 history로 이동하고 현재 상태와 미완 작업을 분리; runtime/world/DB/key/report 생성물 Git 제외.

이전 전체19 Python/50 frontend/71 browser PASS는 UX 이전 소스의 이력이다. 위 targeted PASS를 전체 matrix·actual provider·release-ready로 확대하지 않는다. 실제 key 등록과 공개 models GET은 유료 번역 품질·정확한 청구의 검증을 대신하지 않는다.

## Phase 3 — 미시작

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

원본 sample 쓰기 금지. 합성 또는 복사본에서 SHA-256 baseline을 기록하고 쓰기·복원 전후를 비교한다. 추가 실제 API 비용은 현재 $0이다. 실제 E2E의 기존 허용 예산은 추가 총 $1 이하(목표 $0.01–$0.10)이며 mock 먼저·최소 호출 원칙을 따른다. 이 문서 정리는 유료 실행을 새로 시작하는 요청이 아니다.

[CI 정책](ci-policy.md)에 따라 일반 문서/UI 변경은 Python CI를 시작하지 않으며 installer는 manual/tag이다. 이번 사용자 요청에 따른 진행 저장은 `[skip ci]` checkpoint로 기록한다. Phase2 완료 push와 구분한다. 공개 release·서명 자격·사용자 world upload는 별도 확인 없이 하지 않는다.

맵 재배포·상표·의존성 권리는 [면책 안내](disclaimer.md)와 [라이선스 검토](legal/license-review.md)를 따른다. 미검증을 완료라고 쓰지 않고 충돌을 발견하면 기록·해결한 뒤 해당 배포를 재개한다.
