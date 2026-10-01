# PomiTranslate 제품 저장소 에이전트 지침

작업 시작 시 다음을 읽는다:

1. 사용자 최신 요청과 상위 AGENTS.md.
2. `docs/verification-policy.md` — 검증 선택·증거 재사용·중단 규칙.
3. `docs/history/phase2-resume-2026-10-01.md`, `docs/current-state.md`, `docs/follow-up-work.md` (이전 중단 이력: `docs/history/phase2-pause-2026-10-01.md`).
4. `docs/PomiTranslate_Implementation_Plan_and_Agent_Instructions_v1.1.md`.

## 실행 계약

- 기존 Python/Tauri/Rust/Svelte 구조와 WIP를 보존한다. reset/clean/checkout으로 미완 작업을 없애지 않는다.
- 일반 수정은 affected tests만. 전체 viewport/axe/100k/screenshot/Python/Rust/package/API 반복은 최종 gate 또는 구체적인 남은 위험일 때만.
- `pnpm verify:plan`은 실행 없는 계획 확인. 소스 안정화→관련 검사→필요하면 마지막 전체 gate 순서. 같은 source의 유효 PASS를 재사용한다. 테스트 실행 중 source 수정 금지.
- UI-only는 browser/dev, Python 변경은 관련 fixture부터. 매 UI 수정에 sidecar clean/Tauri/installer build 금지. Native 최종 gate를 fixture PASS로 대체하지 않는다.
- 중단 요청 시 새 테스트/빌드/서버/유료 호출 금지. 소유 확인한 프로젝트 프로세스만 종료하고 인계를 갱신한다.
- Local encrypted DB+설치별 key 파일이 credential 기본, Session/OS keychain opt-in. keychain 자동 접근/import 없음. 평문 키는 화면/로그/채팅/파일/Git에 남기지 않는다.
- world write/restore는 합성/복사본에서 baseline SHA-256으로 비교한다. 원본 sample 쓰기 금지. 알 수 없는 결과를 성공으로 보고하지 않는다.
- 구현/자동 검사/native/실제 provider/release를 구분한다. Phase2 완료 전 Phase3 구현 시작 금지.
- 사용자 중간 저장 요청에 따른 checkpoint commit은 허용하지만 Phase complete라고 부르지 않는다. Phase 완료 commit은 검증→docs/diff review→commit→push 순서다.
- CI는 관련 main Python만 자동, installer manual/tag. 사용자 중단·중간 저장 push는 `[skip ci]`로 불필요 실행을 막는다. 공개 release/signing/upload는 기존 승인 경계를 따른다.

## 현재 재개 상태

2026-10-01 승인된 설정·추론 UI/UX 여섯 개선을 완료했다. 최신 증거는 `docs/history/settings-ux-2026-10-01.md`다. Phase2 진행 중/Phase3 미시작, 추가 API 비용$0. 관련 frontend28/browser30(29+1)/Rust24·Python provider 두 파일·build·native 저장/재시작/기본값 복원 PASS. 전체 matrix는 UX 이전 결과를 최신 PASS로 복사하지 않는다. 사용자의 OpenRouter key/model 직접 등록은 완료됐다. 실제 유료 provider usage-cost-restore, legacy 대체 계약, 과거 blank/clean-machine startup과 최종 gate가 남아 있다.

## 문서 정리 후 진입점

사용자 문서: README.md / docs/user-guide.md / docs/privacy.md / docs/disclaimer.md. 작업 상태: docs/current-state.md / docs/follow-up-work.md. 이력: docs/history/. 라이선스: THIRD_PARTY_NOTICES.md / docs/legal/. 소개용 합성 screenshot은 docs/images/에서 의도적으로 추적하며 일반 output·report·world·DB·key는 제외한다. 현재 진행 저장은 사용자 승인 checkpoint이고 Phase2 완료가 아니다.

원격 URL은 2026-10-01 기존/새 주소의 동일 main SHA를 확인한 `https://github.com/kim0040/PomiTranslate.git`다. 원격 rename을 새로 실행한 것이 아니다. 로컬 checkout 폴더와 내부 mwt 이름은 유지한다.
