# Phase 2 진행·중단 기록 — 2026-09-30

## 최신 재개 상태

사용자 “이어서 해줘” 요청으로 재개했다. **Phase 2 진행 중 / Phase 3 미시작**. [최신 검증 기록](phase2-validation-2026-09-30.md)이 아래 중단/역사 기록보다 우선한다. Python 16 suites, frontend 47, browser 전체59 PASS; 최신 screenshot 28 및 새 수동 preview 1 targeted PASS, Rust21 PASS. Safe Python settings preview와 Comet 직접 선택을 구현했다. 최신 native 회귀/실제 API/최종 gate는 진행 중이며 Phase 완료 commit/push 없음.

## 최신 상태 — 사용자 요청으로 정리 후 중단

2026-09-30 **“일단 지금까지 한거 마무리해줘. 나중에 다시 이어서 하게”** 요청에 따라 작업을 정리하고 중단했다. **Phase 2 미완 / Phase 3 미시작**. `main` / `865b51d`의 기존 및 이번 WIP를 보존했고 commit/push는 하지 않았다. 최신 구현·검증 범위·실제 native mock/restore 증거·남은 gate·정확한 재개 순서는 [최신 인계·중단 기록](phase2-resume-2026-09-30.md)이 아래 역사 기록보다 우선한다. check 0 errors/0 warnings, frontend 46 PASS, Rust 21 PASS; native mock 및 복원 해시 확인. 최신 취소/리소스팩 변경의 native 재빌드와 실제 API는 남았다. 추가 API 비용 $0. 아래 이전 “진행 중/미검증/남음” 및 test 숫자는 당시 기록이며 최신 상태를 뜻하지 않는다.


상태: **사용자 요청으로 작업 중단 / Phase 2 미완 / Phase 3 미시작**.
제품 저장소는 `main`, committed HEAD `865b51d`다. 현재 구현과 이번 기록은 **미커밋 working tree**에 보존했다. Phase 완료 commit/push는 하지 않았다. 사용자의 마지막 중단 지시는 “지금까지 했던것만 계획에 기록으로 남기고 나중에 하게 멈춰주삼”이며, 기록 정리를 마친 뒤 구현·추가 테스트를 계속하지 않는다. 재개는 후속 사용자 요청 때 한다.

## 1. 최신 결정과 안전 경계

- API credential 기본은 **로컬 암호화 SQLite + 별도 설치별 무작위 master-key 파일**. session-only와 opt-in keychain 유지. 시작/상태 조회 때 기존 키체인을 자동으로 읽지 않는다. 평문 키를 JSON/로그/Git에 남기지 않는다.
- 검증 순서는 **static/unit → browser fixture UI → 실제 Python/JSONL → frontend production build → 마지막 sidecar/Tauri/native E2E**. 반복 UI 수정마다 앱 패키징을 하지 않는다.
- 화면은 폭과 높이 모두에 대응한다. desktop/320px/짧은 창/세로형/ultrawide/연속 resize/실제 200% zoom을 구분해 기록한다.
- CI 제한은 기존 `865b51d`에 push된 상태. 현재 Python 새 suite 추가는 WIP이며 feature push의 3 OS installer 자동 빌드는 하지 않는다.
- 유료 API 추가 비용 **$0**. 최종 최소 실제 API에 기존 추가 총 $1 상한(목표 $0.01–$0.10)을 유지한다. 아직 실제 API gate를 실행하지 않았다.
- 원본 sample world는 수정하지 않았다. write test는 temporary/generated world 또는 `/private/tmp/pomi-eval/` 복사본만 사용한다.

## 2. 구현해 둔 내용 — 최종 native 검증과 구분

### Credential·설정 저장·provider 경계

- `src-tauri/src/credentials/`: AES-256-GCM, nonce/AAD/provider 격리, SQLite 암호문과 public metadata, 별도 설치별 key 파일. local/session/선택적 keychain 및 명시적 기존 키 가져오기.
- Unix 사용자 전용 권한·소유자·symlink 검사·동시 생성/잠금. Windows current SID protected DACL, 생성 시점 SECURITY_ATTRIBUTES, handle 기반 owner/ACL/reparse/hardlink 검사, LockFileEx.
- `src-tauri/src/settings_transaction.rs`, `mwt/userdata.py`: public 설정 snapshot/compare-and-restore, credential metadata 실패 rollback, OS credential 보상 복구. 복구가 불확실하면 재입력까지 실행 차단.
- `src-tauri/src/provider_boundary.rs`, `mwt/desktop_provider.py`: 공개 provider canonical URL, explicit Custom endpoint 검사, Rust-owned request에서 `POMI_*` 환경변수가 UI 설정/목적지/키를 덮어쓰지 못하게 분리. CLI의 의도된 환경 설정은 유지.
- 키 삭제는 편집 중인 다른 설정을 저장하지 않으며, 삭제 실패를 성공으로 표시하지 않는다. 수동 번역만 실행하는 경우와 API credential 필요 여부를 구분한다.

### 후보 검토·결과·화면 상태

- Candidate paging 200개, 최대 12-page LRU, 100k fixture에서도 bounded virtual DOM. stale/out-of-order paging 폐기, 재시도, bulk 처리 중 query 변경 중단.
- 검색/kind/included/excluded/manual/sort와 filter/row count 일치. 8개 keyboard 명령, 좁은 창 detail dialog와 draft/focus 보존.
- restore 후 Result에 머무르지 않고 유효 Scan 단계로 초기화.
- estimate revision/signature로 이전 요청과 out-of-order 응답을 폐기. unavailable estimate를 무료/0건으로 표시하지 않음.
- 실제 결과 status별 설명·후속 action, 실패의 무변경 단정 제거, 실패 count label 및 detail 중복 제목 수정.
- coverage에서 region 파일 수와 문자열 수를 혼동하지 않도록 표기. About와 완료 결과에 근거 없는 실행/백업 단정 제거.
- 작업 중 창 닫기 요청은 전역 메시지로 알림. 내부 event name을 화면에 그대로 표시하지 않음.

### Settings·legacy 기능 복구

- `mwt/desktop_settings.py`, `src/lib/settings.ts`, `ScanScopeSettings.svelte`: 텍스트 category flags, all/none, command-like skip, region dirs/skip patterns/component prefixes. scope 변경은 scan invalidate, model 변경은 scan 유지. temperature/retry의 0 보존.
- Settings의 Scope/Performance/Application을 native disclosure로 정리. 잘못된 performance 값은 해당 영역을 열어 표시.
- 공개 설정 Export/Reset draft. API 키를 export하지 않고 Reset은 Save 전까지 draft만 변경.
- `mwt/desktop_prompt.py`와 `prompt.enhance` Rust/sidecar 경로: 스타일 brief 보조. 제공사·모델·전송/요금 확인 후 실행하며 결과는 미저장 prompt draft에 반영. 사용자 설정을 자동 저장하지 않음. 실제 paid 호출은 미실행.
- `src/lib/settings-import.ts`: schema 1 공개 설정 및 allowlisted legacy JSON import, endpoint/type/range/size 검사, secret/unknown fields 제외, 현재 UI language/world path 유지. 파일은 최대 1 MiB. 가져오기는 draft만 변경하며 키를 가져오지 않는다.
- 새 핵심 문자열은 ko/en/ja. 중국어 README는 중국어 UI 지원과 별개다.
- legacy UI/launcher는 삭제하지 않았다. [parity 감사](legacy-ui-parity.md)의 남은 차이를 재개 시 해결한다.

## 3. 실제 실행한 검사

| 검사 | 마지막 확인 결과 | 근거 범위 |
| --- | --- | --- |
| `pnpm check` | **PASS**, Svelte 0 errors/0 warnings, TypeScript PASS | import/disclosure 포함 현재 frontend |
| `pnpm test:frontend` | **8 files / 42 tests PASS** | formatter/status/progress/i18n/virtual/filter/LRU/scan scope/settings recovery/estimate/import |
| Rust `cargo test --locked --offline --manifest-path src-tauri/Cargo.toml --lib` | **19 PASS** | temp vault/metadata/rollback/provider boundary; 실제 OS keychain 테스트 아님 |
| Windows private filesystem target typecheck | **PASS** | 별도 temp crate, `x86_64-pc-windows-gnu`; Windows native 실행 **NOT RUN** |
| Python 기존 전체 실행 | **10 suites PASS** | core, release fixtures, brand secrets, desktop entry, providers, desktop provider, settings transaction, scan settings, reliability, extraction |
| Python 최신 추가/관련 재실행 | **PASS** | `test_desktop_prompt.py` 3 cases + desktop provider/desktop entry 재실행. prompt 추가 뒤 전체 11 suite를 하나의 실행으로 다시 돌린 것은 아님 |
| `pnpm test:browser` | **48 PASS / 37.1초** | 현재 source 고정 상태, 모든 페이지·status·48개 regression, fake credential/loopback fixture |
| frontend production build | 이전 PASS 기록, **최신 변경 후 NOT RUN** | prompt/disclosure/import 이후 재실행 필요 |
| 최신 packaged sidecar/Tauri/native E2E | **NOT RUN** | 과거 native mock 기록을 새 vault 성공으로 간주하지 않음 |
| 실제 provider·전후 usage·비용 | **NOT RUN**, 추가 $0 | mock token/cost는 실제 비용 아님 |

브라우저 회귀에는 axe 0 violations, 100k 후보 DOM<50, 제외/직접번역/kind/search counts, keyboard 8키, model 유지·target/category invalidate, secret 제외 export/import, reset 미저장 draft, style helper 확인, restore→Scan, 연속 resize draft/focus가 포함된다.

중간 47-test 실행은 **45 PASS / 2 FAIL**이었다. 실행 중 소스 수정/Vite HMR 때문에 control detach 및 resize dialog 대기가 발생했다. 렌더 대기를 보강한 targeted 2개가 통과했고, 이후 **소스를 수정하지 않은 최종 48개 전체 실행이 통과**했다. 중간 실패는 삭제하지 않고 원인/재검증을 남긴다.

## 4. UI 직접 점검과 실제 200%

`output/playwright/`의 World empty/selected, Scan running/complete, Review, Run confirm/progress, success/failed Result, Backups, Settings, About, dark Review 및 320px Review를 직접 열어 점검했다. 좁은 detail은 dialog로 열리고 desktop 후보 table은 가용 높이를 사용한다. 관찰한 화면에서 세로 한 글자/20px 입력/전체 가로 overflow는 없었다.

최종 48-test 실행 후 **새 Settings 1440 light와 Japanese 840 dark 이미지도 직접 확인**했다. Scope/Performance/Application disclosure, 가져오기/내보내기/저장 버튼, dark 입력 폭을 점검했다. focused skip-link/toast가 보이는 screenshot은 접근성 검사 상태이며 일반 정지 화면과 구분한다. **최종 코드의 selected-detail 이미지와 대표 14개 전부를 다시 수동 검토한 것은 아니므로 남은 gate로 유지**한다.

CUA로 별도 임시 프로필 Chrome의 **실제 browser zoom 200%**를 확인했다(Chrome 접근성 상태 `확대/축소: 200%`, 100% 기준 viewport 1440×769/DPR2). 후보 수동 입력→ESC→선택 행 focus 복귀→재열기 draft 유지, Review footer→Run→Result를 수행했다. 페이지/dialog scroll과 입력/닫기/action 접근 가능했다. CSS zoom/viewport 축소를 실제 확대 증거로 사용하지 않았다. 개인 Comet 탭은 조작하지 않았다.

실제 zoom 검증의 임시 Chrome/Node/Vite는 이전에 종료했고 최종 browser suite의 서버도 실행 종료됐다. 중단 기록 시 loopback 5197/5198 listener가 없음을 확인했다. `ps`는 현재 sandbox에서 거부돼 전 시스템 process 부재를 주장하지 않는다. read-only native setup 조사 worker는 사용자 중단 요청 때 interrupt했다.

## 5. 재개할 때 먼저 할 일

1. `git status --short --untracked-files=all`, branch/log/diff/stat/diff-check/reflog로 WIP 확인. `main` HEAD `865b51d`; local feature ref는 `e70d27a`이므로 WIP를 두고 branch를 무작정 바꾸지 않는다. reset/clean 금지.
2. 이 문서 → 인계 → credential/browser-first 계획 → legacy parity를 읽는다. 아래 초기/과거 문서보다 이 중단 기록이 우선한다.
3. **native data isolation부터 조사**: Rust `exchange_sidecar()`는 Tauri app-data 기반 report/cancel 경로를 쓰지만 sidecar args에 `--data-dir`를 전달하지 않는다. Python `main()`은 args가 없으면 사용자 `PomiTranslate` 기본 data root를 사용한다. **eval app identifier 변경만으로 settings/scan/backup 격리가 충분하다고 가정하지 말 것.** 테스트 운영 데이터/실제 credential을 읽거나 바꾸지 않는 경로를 확정한 뒤 native 실행한다. 이 문제는 발견·기록만 했고 아직 수정하지 않았다.
4. legacy parity 잔여 공백: named Story/Recommended scope presets, persistent global overrides, external resource pack/locale/overwrite controls, report 접근/export, 안전한 public `translate.py` 설정 대체, Comet 직접 선택 및 contact link, app-managed checkpoint/backup/write-retry 정책. 외부 pack/override 확장은 Phase 3 backlog와 연결하되 parity 충족 없이 legacy를 제거하지 않는다.
5. 최종 selected-detail/대표 screenshot 수동 검사 → 필요한 수정/영향 테스트 → `pnpm build` → sidecar packaging → Tauri debug app. Python/protocol/native가 변경됐으므로 과거 sidecar/app을 현재 산출물로 쓰지 않는다.
6. 현재 vault의 restart/store/update/delete/metadata-only 조회와 실제 native world chooser/scan/search/filter/exclude/manual/run/progress/result/backups/restore/close/cancel을 test-copy에서 수행. hash snapshot/예상 변경 파일/restore byte-identical 확인.
7. 마지막 실제 provider 최소 호출, canonical endpoint, 전후 usage/실제 비용 기록. 키체인은 명시적 import 또는 opt-in 실행 때만 접근. 개인 기존 키를 dummy로 덮어쓰지 않는다.
8. docs/diff review → **Phase 2 완료 검증 후에만 commit → push**. 이후 Phase 3. Phase 3 구현은 아직 시작하지 않았다.

## 6. 보존과 배포 판단

- 제품 source 및 docs의 modified/untracked 파일을 그대로 보존했다. 이번 중단 문서는 local filesystem에만 있고 새 commit/push는 없다.
- 대표 screenshot/test artifacts는 ignored `output/playwright/`; 임시 world/별도 typecheck crate는 Git 밖. 다른 머신에서 fixture로 재생성해야 한다.
- Windows/Linux native permission/clean-machine, signing/notarization/updater 및 공개 release는 NOT RUN. 서명 credential을 임의 생성하거나 검증을 우회하지 않는다.
- 현재 **release-ready 아님**. Phase 2 final/native/provider/parity gate 및 Phase 3가 남아 있다. Phase 3 전체 backlog는 [remaining-work](remaining-work.md)와 [인계](agent-handoff-2026-09-30.md)에 보존했다.
