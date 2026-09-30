# 테스트·작업 지연 조사 — 2026-10-01

> **최신 결정 — 검증 최적화 후 중간 저장/중단:** 사용자 요청으로 실행 정책·명령을 반영하고 현재 WIP를 checkpoint commit/push한다. Phase2 완료 commit이 아니며 Phase3 미시작이다. [검증 실행 정책](verification-policy.md)과 아래 최적화 후속 기록을 우선한다. 테스트·개발 서버·Eval 앱은 종료됐으며 내일 재개 전 새 검사/빌드를 실행하지 않는다.

사용자 중단 요청 뒤 read-only로 설정·테스트 소스·기존 결과를 조사했다. **시간을 측정하려고 새 테스트를 돌리지 않았다.** 전체 작업 시간의 정확한 비중은 실행별 구조화 로그가 없어 산정하지 않는다.

## 판정

중요한 안전성 테스트는 유지할 필요가 있다. 다만 개발 중 전체 회귀·screenshot/axe·clean sidecar packaging을 반복한 실행 방식에는 줄일 수 있는 중복이 있다. 테스트 숫자가 많다는 사실만으로 쓸모없다고 판단하지 않으며, 발견한 실제 결함과 변경 영향에 따라 선택한다.

## 관측

| 관측 | 코드·실행 증거 | 처리 방향 |
| --- | --- | --- |
| 전체 browser 실행 | 이전64:56.7초, 이번67:3.5분. 후속 usage+ZIP4 targeted:7.5초 | 작업마다 full gate를 반복하지 않음. 이번 slowdown 원인은 프로파일링하지 않아 CPU/leak로 단정하지 않음 |
| 단일 worker | playwright.config.ts:6 workers1 | 리소스 안정성 유지. 느리다고 병렬 수부터 늘리지 않음 |
| viewport 반복 | screens.spec.ts:116 세 페이지×3폭, workflow.spec.ts:155 Review4폭, layout.spec.ts:12 Review5폭 | 초기/최종 responsive gate 유지, 작은 개별 변경은 해당 화면/대표폭만 |
| axe 전체 페이지 | screens result2/pages9/representative7 + layout viewports5/locales4: 전체 run에 약27 analyze calls | 의미 있는 a11y coverage지만 매 수정마다 모든 폭에서 반복할 필요 없음. changed screen대표폭→마지막 matrix |
| 결과 실패의 중복 boot/run | screens.spec.ts:82와94의 result-failed | localization/a11y와 행동 assertion을 하나의 시나리오에 통합 가능; 자동화 수정은 중단 후 미실행 |
| duplicate screenshots | screens.spec.ts:89/90,144/145,selected vs gate; 같은 page generic path와 numbered artifact 연속 촬영 | 한번 캡처해 두 이름으로 보존하거나 canonical artifact만. snapshot 비교 assertion 없는 수동 QA용 PNG임을 명시 |
| resize 중복 | workflow.spec.ts:170 draft resize와 layout.spec.ts:36 continuous21폭 | draft/focus 이동 회귀는 필요하나 경계 대표폭/왕복 위주로 묶을 수 있음 |
| 100k fixture | workflow.spec.ts:118 테스트 하나만 count100000, fixture초기전체생성 후 page로반환 | DOM/cache bounded 회귀는 사용자 필수 항목. 전체 tests가100k를 생성한다는 주장은 틀림; 관련 변경/최종 gate에서 실행 |
| 60초 fixture timer | fixture scan/translate run-progress는 unresolved operation상태 유지용. test는 progress를 본 뒤 종료 | 매 테스트가60초 기다리는 원인이 아님. 페이지 종료 시 timer소멸. 무작정 삭제하지 않음 |
| check 중복 | package.json build는 pnpm check를 자체실행 | 같은 소스에 check직후build면검사중복. build시각을 check결과로재사용 |
| sidecar clean | build-sidecar.mjs:25 항상 --clean --onefile. desktop:dev/build도 sidecar:build 선행 | UI-only는 frontend dev/브라우저로검사; Python변경최종nativegate에서만package. 개발증분/캐시 전략은 다음작업검토,현재script미수정 |
| 수정 중 실행 | 이전실행에ViteHMR/controldetach 실패 이력. 직전sidecar56초뒤Python수정으로22초재package | 소스를먼저고정하고검사/패키징. 실패원인해결없는무작정재실행금지 |

## 유지해야 하는 gate

- write 전 provider/plan 검사, backup 검증, restore byte-identical, checkpoint/resume 최신 review, unknown/partial/failed/cancelled 보고.
- credential 평문/OS자동접근 방지, provider endpoint/redirect 경계, crypto transaction/recovery.
- virtualization/count/filter 및 keyboard, 최소폭/짧은 높이/200%/dialog 접근성.

실제 native 재개 시 신규 exclude/manual이 이전 checkpoint에 덮여 다른 파일까지 수정되는 결함과 native200%에서 dialog가 안 보이는 결함을 잡았다. 따라서 모든 native/복원 검사를 제거하는 것은 목적에 맞지 않는다.

## 다음 실행 계약

1. 개발 루프: 수정→affected unit/backend test→affected browser scenario만. UI-only 작업은 sidecar/Tauri packaging없음.
2. 기능 묶음이 안정화되면 broadcheck/관련 통합을 한 번. source 수정 중 browser full run금지.
3. Phase 완료 후보에서만 full Python/frontend/Rust/browser matrix/screenshot inspection→frontend production→필요 sidecar→native E2E. 이미 동일소스검사가성공했다면반복하지않음.
4. Native에서 defect발견 시 수정→그defect와영향영역만재검증. 전역 safety/schema에영향있을때만full gate추가.
5. 정확한시간비교가필요하면다음실행에서JSON reporter/실행단위소스기준점/시간저장을먼저추가. 현재1분→3.5분원인과전체작업소요비율은미확정.

이번 중단에서는 테스트 삭제/worker증가/buildscript변경을 하지 않았다. 현재 구현·미검증 경계·재개 순서는 [중단 인계](phase2-pause-2026-10-01.md)를 따른다. CI는main관련Python만자동core,installer manual/tag(기본Linux). 이번CI dispatch없음.


## 후속 조치

사용자 추가 요청으로 policy/AGENTS와 tiered verifier, conservative evidence cache, sidecar incremental/explicit clean, result-failed 통합과 duplicate PNG copy를 구현했다. 위 조사 시점의 ‘script 미수정’은 역사 기록이다. [정책](verification-policy.md)을 적용하며 오늘 runtime 재실행 없이 syntax/plan만 확인했다. 새로운 harness 동작과 screenshot 회귀는 내일 targeted 검증으로 남겼다.
