# 검증 실행 정책 — 2026-10-01

이 정책은 사용자 요청인 검증 최적화와 웹 우선 개발을 실행 규칙으로 만든다. [최신 인계](phase2-pause-2026-10-01.md), [남은 작업](remaining-work.md), [이유·근거](test-efficiency-audit-2026-10-01.md)와 함께 읽는다. **이미 성공한 동일 검사 재실행은 기본 동작이 아니다.**

## 에이전트 필수 규칙

1. 시작 시 git status/log/diff와 최신 인계를 읽고 기존 WIP를 보존한다. 이전 test 숫자를 현재 source PASS로 복사하지 않는다.
2. 수정하기 전에 영향을 받는 레이어와 필요한 검사만 정한다. 사소한 문구/문서/스타일 수정 때문에 전체 Python/Rust/native/API gate를 실행하지 않는다.
3. 먼저 구현을 안정화한다. 검사 중 source 변경 금지. failed 원인을 해결한 뒤 관련 검사만 다시 돌린다. 무작정 전체 재실행을 하지 않는다.
4. 소스·명령·설정·도구·환경이 같고 이전 PASS가 유효하면 재사용한다. source 변경, dependency/toolchain/browser/sandbox/test data 변화, 경과시간 만료나 잔여 위험이 있으면 해당 증거를 무효화한다. 오류/중단/RUNNING 기록은 PASS로 재사용 금지.
5. 여러 화면 폭, 모든 locale/dark/axe, 100k, 전체 screenshot은 초기 설계 변경 또는 최종 gate에만 묶어서 실행한다. 일반 개발 루프는 해당 화면·대표 폭·실패 regression만.
6. UI-only는 browser/dev. sidecar packaging은 Python/dependencies/packaging 변경이 있거나 artifact가 없을 때만. Tauri/native는 마지막 gate 및 native-only 결함 재현/수정에 필요할 때만. 실제 API는 mock 성공 뒤 기존 승인 예산 내 최소 호출이다.
7. Phase 전체 완료 후보에서 관련 전체 gate를 한번 수행한다. 같은 입력 PASS를 이미 얻었다면 다시 돌려 시간을 소모하지 않는다. Phase status와 implemented/tested/native/release-ready를 구분한다.
8. 중단 요청 시 새 테스트·서버·빌드를 시작하지 않는다. 정확한 소유 PID/cwd를 확인해 프로젝트 작업만 종료한다. 공용 MCP/사용자 다른 앱을 종료하지 않는다. 진행/미완 증거를 기록하고 중단한다.

## 실행 선택표

| 변경 | 개발 중 최소 검사 | 최종에만 추가 |
| --- | --- | --- |
| 문서/에이전트 정책 | diff/link/명령 계획 확인 | 앱 전체 검사 없음 |
| UI 문구·스타일·폭 | check 또는 build 한번 + 해당 browser scenario/폭 | broad layout/axe/screenshots |
| candidate state/virtual/filter | 관련 frontend unit + 해당 browser workflow | 100k와 keyboard/full matrix |
| Python scan/NBT/backup/provider | 관련 Python fixture/JSONL contract | 전체 Python 및 실제 copy restore hash |
| vault/routing/Rust | 관련 Rust unit·합성 boundary | native credential transition/permissions |
| 패키징/dependencies/native | 필요한 package + 해당 native smoke | clean final package/플랫폼 release gate |

## 명령 — 실행을 명시적으로 선택

- `pnpm verify:plan`: check/frontend/browser-smoke 명령과 source fingerprint만 표시. **테스트 실행 없음**.
- `node scripts/verify.mjs <profile...>`: 선택 profile 계획만. `--run`을 붙일 때 실행.
- `pnpm verify:ui`: check + frontend + 6개 주요 browser smoke. scope가 더 좁으면 직접 해당 unit/test file 또는 Playwright `--grep`만 실행한다. UI-only에도 이 묶음을 항상 전부 요구하지 않는다.
- `pnpm verify:final`: check/frontend/Python19/Rust/browser 전체. **Phase 완료 후보에서만**. Native/paid API/installer는 포함하지 않는다.
- profiles: `check`, `frontend`, `browser-smoke`, `browser-layout`, `browser-final`, `python-final`, `rust-final`.
- `--force`: toolchain/browser/환경/dependencies 변경, 남은 구체적 위험 또는 최종 cold check 때문에 기존 PASS 재사용을 배제해야 할 때만.
- `pnpm desktop:dev:ui`: 이미 필요한 sidecar가 준비된 UI-only native dev. Python 변경 뒤에는 이 명령으로 stale sidecar를 검증하지 않는다.
- `pnpm sidecar:build`: PyInstaller dependency cache를 유지하는 incremental package. `pnpm sidecar:build:clean`: 명시 clean package.
- `pnpm desktop:build`: release 후보 clean sidecar 후 Tauri build. 일반 개발용/매 수정용 명령이 아니다.
- `pnpm build` 자체가 check를 수행한다. 같은 source에서 check 직후 build를 할 경우 중복 check를 피하도록 순서를 정한다.

## 성공 기록 재사용 계약

`scripts/verify.mjs`는 profile 입력(source/test/config/lock/명령/OS/arch/Node) SHA-256, 실행 시 toolchain( Python installed package names/versions 포함), 시작/성공/실패 상태와 소요시간을 `output/verification/evidence.json`에 기록한다. 해당 profile의 정확한 fingerprint/toolchain과 24시간 이내 PASS만 재사용한다. source가 실행 도중 바뀌면 PASS로 저장하지 않는다. lock은 중복 실행을 거부하고 SIGINT/SIGTERM은 자신이 시작한 프로세스 그룹만 종료한다. 강제 종료 후 stale lock은 기록된 PID의 명령/cwd가 없는지 확인한 뒤 제거한다.

- **기존 과거 PASS를 이 cache에 수동 등록하지 않는다.** 당시 exact fingerprint가 없으므로 최초 실행 증거로 소급하지 않는다.
- cache는 실행 비용 절약 도구이며 모든 환경 변화를 자동 탐지하는 증명 시스템이 아니다. browser/permissions/네트워크/sandbox/node_modules 변경은 에이전트가 판단해 `--force` 또는 영향 검사 직접 실행.
- 수동 GUI/native/API/restore 증거는 별도 기록하며 cache로 대체하지 않는다. source/package/world baseline/app identifier/결과 시점을 함께 남긴다.
- `output/verification/`, test worlds/DB/keys/build/screenshots는 Git 제외. commit 이후 같은 source 검사 PASS는 재사용할 수 있으며 commit hash가 바뀌었다는 이유만으로 full suite를 반복하지 않는다.
- 이번 사용자 중단 요청에서는 **syntax와 계획 출력만 확인**했고 새 executor의 실제 run/cache/invalidation/cancel/lock 및 최적화된 screenshot suite의 runtime는 내일 targeted 검증한다. 현재 CLI가 모든 OS에서 검증됐다고 주장하지 않는다.

## 실제로 줄인 반복

1. `result-failed`를 두 번 boot/run하던 browser case를 한 번으로 통합하고 상태/다음 행동/axe/screenshot assertion은 유지했다.
2. 같은 page를 generic/번호 경로로 두 번 캡처하던 부분은 이번 실행의 단일 PNG를 복사해 두 이름을 보존한다. 이전 파일을 가져와 fresh screenshot처럼 보이지 않는다.
3. 기본 sidecar script의 무조건 `--clean`을 제거하고 명시적인 clean 명령을 분리했다.
4. 전체 실행만 있던 명령에 plan/smoke/final과 conservative evidence reuse를 추가했다. 리소스 문제를 고려해 Playwright workers1을 유지했다.

## 내일 첫 후속 검사

executor의 source/명령/실패/중단/cache/lock 동작을 임시 합성 command runner로 targeted 검증하고, `screens.spec.ts`의 result success/failure·대표 화면 PNG 매핑만 확인한다. 구현 변화가 없는 unrelated 전체 gate를 이 최적화 검증 때문에 다시 돌리지 않는다. 이후 [기존 Phase2 잔여](remaining-work.md)를 이어간다.
