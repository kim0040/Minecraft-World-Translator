# Phase 2 최신 인계·중단 기록 — 2026-09-30

## 최신 재개 상태

사용자 “이어서 해줘” 요청으로 재개했다. **Phase 2 진행 중 / Phase 3 미시작**. [최신 검증 기록](phase2-validation-2026-09-30.md)이 아래 중단/역사 기록보다 우선한다. Python 16 suites, frontend 47, browser 전체59 PASS; 최신 screenshot 28 및 새 수동 preview 1 targeted PASS, Rust21 PASS. Safe Python settings preview와 Comet 직접 선택을 구현했다. 최신 native 회귀/실제 API/최종 gate는 진행 중이며 Phase 완료 commit/push 없음.

## 현재 상태와 작업 경계

사용자의 **“일단 지금까지 한거 마무리해줘. 나중에 다시 이어서 하게”** 요청에 따라 작업을 정리하고 중단했다. **Phase 2 미완 / Phase 3 미시작 / release readiness: development-ready (배포 gate 미완)**. 아래 최신 기록이 이 문서와 다른 문서의 과거 진행/중단 관측보다 우선한다. 새 기능이나 추가 native/API 검증은 재개 요청 때 진행한다.

- 제품 Git: `main`, HEAD `865b51d`. 기존 및 이번 modified/untracked WIP를 보존했다. reset/clean/branch 변경 없음. Phase 완료 조건을 충족하지 않아 **이번 commit/push 없음**.
- 추가 유료 API 비용 **$0**. 실제 API/기존 키/OS 키체인 접근 없음. localhost mock과 synthetic credential만 사용했다. 실제 API 추가 총 $1 상한(목표 $0.01–$0.10)은 다음 최종 gate에 유지한다.
- credential 정책: 기본 AES-256-GCM 암호화 local SQLite + 별도 설치별 random key, session-only, OS keychain opt-in. 자동 키체인 조회/자동 import 금지, 평문/전체 키 재표시 금지.
- browser-first 순서를 유지한다. 자동 검사/브라우저 UI → Python/JSONL → production frontend/sidecar → 마지막 native gate. UI 폭과 높이, 짧은 창·320px·200% zoom·dark·keyboard를 함께 검증한다.
- 보조 작업은 중단했다. localhost mock server(52973)는 종료했고 listener 없음 확인. 개인 browser/운영 앱/원본 월드는 종료하거나 수정하지 않았다. eval 앱이 열려 있다면 이전 unsigned build이며 비작업 상태다.

## 이번에 구현·수정한 범위

기존 Phase 2 화면과 vault 작업을 버리지 않고 이어서 수정했다. 자세한 이전 구현은 아래 역사 기록 및 `phase2-progress-2026-09-30.md`에 있다.

- production 데이터 경로를 유지하면서 alternate app identifier의 sidecar public 데이터는 자기 app-data `core/`로 격리했다. native export는 관리된 최신 보고서/공개 설정만 읽고 Save dialog로 JSON을 저장한다.
- 저장형 exact-source override, 후보별 우선순위/견적/manual filter, Recommended/Story presets, file write retries 및 continue-on-file-error, 공개 설정 import/export/reset, contact link와 경로 중복 표시를 정리했다.
- fresh bootstrap provider default 및 manual-only credential read 생략, single-instance/macOS Reopen 창 show/unminimize/focus를 수정했다.
- 실제 native 취소에서 발견한 결함 수정: 취소/쓰기 실패 보고서도 provider request/usage를 보존한다. 미완료 결과의 준비된 번역을 “번역문 준비”로 표시하고 sample이 실제 파일 적용을 단정하지 않도록 했다. **소스/회귀 검증 완료, 이 수정의 native 재빌드·재검증은 남음.**
- resource pack backup 경계 preflight를 API 호출 전에 수행한다. 외부 경로 및 symlink escape는 write를 거부한다. dry scan의 읽기와 구분한다. skip-existing-target을 scan/write에 일치시키고 invalid ZIP을 partial/failure로 보고한다.
- resource pack source locales, target locale, skip-existing-target 설정을 frontend/backend/import/export/scan fingerprint에 연결했다. 잘못된 파일명·경로·중복·source=target을 inline 검증한다. 기본 overwrite 정책을 보존하며 전체 locale 파일 교체 경고를 표시한다. **외부 ZIP/folder 선택 지원은 추가하지 않았다.**
- 위 구현의 Python 회귀 3개를 기존 제한된 CI에 등록했다. CI trigger 범위는 유지했고 workflow dispatch는 실행하지 않았다.
- 안전한 Python literal `translate.py` 설정 import는 **계획만 있고 미착수**다. 중단 직후 해당 parser 파일/심볼이 없음을 확인했다. 임의 Python 코드를 실행하는 방식으로 대체하지 않는다.

## 검증 결과 — 시점과 범위를 구분

| 항목 | 결과 | 증거 범위 / 다음 확인 |
| --- | --- | --- |
| 최종 `pnpm check` | PASS, 0 errors / 0 warnings | 최신 resource pack UI까지 포함 |
| Frontend unit | PASS, 46 tests / 9 files | 최신 locale validator/import 포함 |
| Browser 전체 | PASS, 52 tests / 47.2s | 이후 변경 전 전체 실행 |
| Browser 후속 targeted | PASS, World/About/manual map 6, result status 6, pack settings 1 | 전체 최신 suite 통과로 합산하지 않음; 다음에 전체 재실행 |
| Rust unit | PASS, 21 tests | native export/경로/창 처리 등 |
| Python baseline | PASS, 12/12 suites | 최신 취소/리소스팩 변경 전 |
| Python 추가 회귀 | PASS, preflight 6 cases; resource pack settings 4 cases; cancellation usage 1 case/2 subtests | 최신 15-script 전체 실행은 아직 NOT RUN |
| Frontend production / sidecar / Tauri debug build | PASS | 최신 취소/리소스팩 변경 전 build; 새 working tree 빌드 아님 |
| 실제 Tauri mock E2E | PASS, 아래 workflow | unsigned isolated eval app, 실제 유료 provider 아님 |
| Restore | PASS, 4/4 SHA256 byte-identical | synthetic world의 전체 4개 파일 |
| Native 취소 | PASS, changed files 0 / 4개 원본 해시 일치 | usage/준비 문구 결함 발견; 수정 후 native gate 남음 |
| Real API | NOT RUN, $0 | 최종 최소 provider/usage 검증 남음 |
| Windows/Linux clean machine / signing / release | NOT RUN | Windows target typecheck는 native 실행 증거가 아님 |
| 최종 `git diff --check` | PASS | 정리 후 재확인 |

### 실제 native mock workflow

파일 chooser → 월드 검사 → scan 3 source/3 occurrences → 검색 Shop 및 text_display filter(1 row)/초기화(3 rows) → Keep original 제외 → Welcome traveler 직접 번역 → Run(전송1/manual1/request1) → localhost mock 번역 → Result(번역2, 변경2 files, request1, usage120 input/20 output) → Backups verified → 복원 확인/busy/recovery snapshot → 원본과 4/4 해시 동일.

번역으로 바뀐 파일은 `region/r.0.0.mca`, `entities/r.0.0.mca`뿐이다. 제외 후보의 `region/r.1.0.mca`와 `level.dat`는 바뀌지 않았다. 재시작 후 local credential “저장됨” 및 빈 credential input, model/endpoint 유지 확인. fake credential 평문은 SQLite에 없고 DB0600/key directory0700을 확인했다. native 공개 Settings JSON 및 최신 cancelled report Save dialog를 확인했다. 지연 mock 실행의 progress/elapsed, 작업 중 close 안내, 취소 busy cleanup, 최종 파일 무변경을 확인했다.

`native-cancelled-report.json`은 수정 전 결함 재현 보고서다(usage 미보고). 고친 결과로 오인하지 않는다. 초기 cgWindowNotFound/Dock 도구 timeout은 앱 crash로 확정하지 않는다. startup 지연은 이후 실제 UI가 로드되어 workflow를 수행했지만 재현되면 추가 조사한다.

### UI 증거와 남은 확인

대표 14영역 screenshot(World empty/selected, Scan running/complete, Review/selected detail, Run confirm/progress, Result success/failed, Backups, Settings, About, dark Review) 및 320px Review를 직접 확인했다. 이전 Chrome 실제 200% zoom 증거는 유지한다. 최신 World/About 소규모 변경, prepared result 문구, resource pack controls는 최신 전체 screenshot/viewport inspection을 다시 해야 한다. 다음 최종 gate에서 1440×900, 1180×800, 1024×768, 840×620, 320px, 높이 변화, 200% zoom, dark, keyboard/a11y를 재확인한다.

## 다음 에이전트의 재개 순서

1. 사용자 재개 요청 후 이 문서 → `agent-handoff-2026-09-30.md` → `legacy-ui-parity.md` → 구현 계획서를 읽는다. `git status`, branch/log/diff/stat를 다시 확인하고 WIP를 보존한다. 현 브랜치는 main이며 최초 지시의 오래된 feature branch로 자동 전환하지 않는다.
2. `pnpm check`, `pnpm test:frontend`, `pnpm test:browser` 및 아래 Python 15개 script를 **최신 working tree**에서 실행한다. 최신 취소/locale 설정의 통합 회귀와 전체 suite를 먼저 확인한다.
3. 안전한 literal Python 설정 import 설계/구현, Comet 직접 선택과 Custom 대체 계약, 외부 pack ZIP/folder 지원 및 backup 경계, app-managed backup/checkpoint의 legacy 차이를 정리한다. global override/presets/report export/contact/locale controls는 다시 처음부터 만들지 않는다. legacy UI/launcher는 parity 확정 전 유지한다.
4. 최신 screenshot/viewport/zoom/dark/keyboard 검증 후 frontend production → sidecar → unsigned isolated Tauri build. 최신 취소 usage/report 및 resource pack 설정 native persistence/scan invalidation을 포함해 재확인한다.
5. 최소 실제 provider E2E와 전후 usage/cost 기록, 원본 복사본의 변경 파일 및 restore byte-identical, 남은 Phase 2 gate·docs/diff review를 완료한다. 모두 통과 후 Phase 2 commit → push.
6. 이후 Phase 3: 보수적인 datapack visible text/command storage/external packs, occurrence 제어와 전체 locations query, glossary/TM/revision 및 필요한 SQLite 계층, 검증 가능한 pricing/비용 추정, Minecraft 다양한 format/오류 fixtures, macOS/Windows/Linux clean-machine 및 signing/release gate. 미검증 지원을 supported로 쓰지 않는다. Phase 3 완료 후 검증 → commit → push.

### Python 재실행 명령

제품 저장소 루트의 Python 3.12 `.venv`를 사용한다. 모든 script 성공 여부를 개별 기록하며 실패 상태로 Phase 완료 처리하지 않는다.

```sh
for test_script in test_core.py tests/test_release_fixtures.py tests/test_brand_secrets.py tests/test_desktop_entry.py tests/test_providers.py tests/test_desktop_provider.py tests/test_settings_transaction.py tests/test_scan_settings.py tests/test_desktop_prompt.py tests/test_desktop_parity.py tests/test_resource_pack_settings.py tests/test_resource_pack_preflight.py tests/test_cancelled_usage.py tests/test_reliability.py tests/test_extraction.py; do
  .venv/bin/python "$test_script" || break
done
```

### 테스트 자료와 데이터 경로

- Git 밖: `/private/tmp/pomi-eval/resume-20260930/`; synthetic `Native workflow world`, `before.json`, native exports, mock script/log/config. 원본 `sample/` 미변경. generated DB/월드/키/보고서/빌드 파일은 Git에 추가하지 않는다.
- 이전 eval unsigned bundle: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app` (latest source와 다름).
- isolated identifier `app.pomitranslate.eval20260930r1`; public data `~/Library/Application Support/app.pomitranslate.eval20260930r1/core`, credential/report는 eval app-data root. production `app.pomitranslate.desktop`의 기존 public `PomiTranslate` 경로와 credential 경로는 유지한다.
- mock endpoint 127.0.0.1:52973은 종료했다. 재개 시 temp mock script를 확인하고 명시적으로 다시 실행한다. OS 키체인이나 실제 사용자 credential을 자동 조회하지 않는다.

---

# 아래는 재개 중 작성한 역사 기록

아래의 “진행 중/남음” 및 이전 숫자는 당시 시점 기록이다. 현재 상태는 위 최신 중단 기록만 사용한다.

# Phase 2 재개 기록 — 2026-09-30

사용자의 “오케이 나머지 작업도 이제 이어서 하자” 요청으로 재개했다. 과거 중단 기록은 역사 기록이며 현재는 진행 중이다. Phase 2 완료 gate 전, Phase 3 미시작. `main` / `865b51d`의 기존 WIP를 보존했다. 아직 새 commit/push 없음.

## 이번 구현

- Rust sidecar launch에 명시적 `--data-dir`. production identifier는 기존 `PomiTranslate` public settings/scan/job/backup 경로를 유지한다. alternate identifier는 자기 app-data의 `core/`만 사용한다. credential/report는 원래 Tauri app-data를 유지한다. `sidecar_paths.rs`와 2개 경로 회귀.
- 추천/스토리 범위 preset 복구. Story는 item name/lore off, 파일 규칙과 desktop text-display 선택은 보존한다. legacy Recommended와 All은 같은 category 설정이다.
- 저장형 exact-source 번역, per-candidate 우선, estimate/manual filter 연결. global map 변경은 scan scope를 바꾸지 않고 resume translation fingerprint를 바꾼다. map은 5,000쌍·각 32k chars·1 MiB 제한, 원문 key exact, target outer whitespace trim. 후보별 수정은 global map에 자동 저장하지 않는다.
- file write attempts 1–10 및 continue-on-file-error public settings/UI/import/export. 기본 true/2. 실패 파일은 기존 결과의 partial/failed에 보고한다.
- native JSON 저장 대화상자를 통한 공개 설정/최신 scan 및 translation report export. renderer가 report 파일 경로나 destination을 지정하지 않는다. 관리된 report는 다음 실행에 덮어쓰므로 최신 보고서라고 표시한다. browser fixture의 download와 native dialog 검증은 구분한다.
- 공통 오류의 “월드 무변경” 단정 제거, 현재 월드의 recent 목록 중복 path 제거, 기존 contact link 복구. manual-only native 요청은 credential read를 생략하며 core가 실제 manual coverage를 독립 검증한다.
- i18n Python 검사에 양쪽 quotation 지원. 새 native fresh bootstrap에서 빈 provider가 credential 조회를 실패시키는 결함 발견 후 Python default OpenAI 및 keychain 무접근 회귀 추가.

## 실행 증거와 실패 기록

- `pnpm check`: PASS 0 error/0 warning; 최신 `pnpm build`: PASS; frontend 8 files / **44 PASS**.
- browser: 첫 확장 실행 **50/51 PASS** (새 테스트가 Lore label을 잘못 지정). label 수정 및 selected-detail 검증 추가 후 **52 PASS / 47.2s**. 이후 World path/About contact 및 manual map prototype 보호 영향 대상 browser 6개 PASS.
- Rust: 경로 2 regression 포함 **21 PASS**; native export 명령 compile PASS. 이후 manual-only read 생략 변경은 native build에 포함했다.
- Python 12-suite run: **11/12 PASS**. prompt fixture가 `_estimate={}`를 반환하여 `requests` lookup 실패. fixture 수정 후 prompt 3 case PASS; 수정 후 최신 전체 12 suite 단일 실행 12/12 PASS.
- sidecar package PASS. fresh default 수정 후 재패키징 PASS.
- 별도 `app.pomitranslate.eval20260930r1` / `PomiTranslate Eval.app` unsigned debug build PASS(59.08 MiB). 최초 앱 실행에서 빈 provider 때문에 `Unsupported credential provider` 발견. 수정 후 native fresh startup/notice/world inspection/local credential save 상태 확인. 전체 native E2E는 아직 진행 중. 앱 창이 열렸다는 사실을 E2E 성공으로 간주하지 않는다.
- 대표 14 영역의 최신 자동 생성 screenshot을 직접 확인했다: World empty/selected, Scan running/complete, Review/selected-detail, Run confirm/progress, Result success/failed, Backups, Settings, About, dark Review. 320 Review도 확인했다. World/About 후속 소규모 변경은 새 이미지 확인 필요. 실제 200% zoom은 이전 기록의 증거를 유지하며 새 UI 영향도 확인한다.
- 추가 실제 API 비용 **$0**. mock/synthetic world만 사용, 원본 sample 미변경.

## 테스트 위치 및 재개 지점

- Git 밖: `/private/tmp/pomi-eval/resume-20260930/` (synthetic 3-source world, before hashes, isolated Tauri config, mock server/log).
- mock loopback `127.0.0.1:52973`, 실행 session은 현재 root 실행 기록 참조. 개인 browser/운영 앱을 종료하지 않는다.
- native public data는 `~/Library/Application Support/app.pomitranslate.eval20260930r1/core`, credential/report는 같은 eval app root. production data와 공유하지 않는다.
- 남은 순서: 실제 native chooser/scan/filter/exclude/manual/run/progress/result/export/restart/vault/backup/restore/hash → 최소 real provider/usage/cost → 남은 legacy parity의 실제 계약 검토 → docs/diff/gate → Phase 2 commit/push → Phase 3.
- external pack/locale/merge 및 안전한 literal `translate.py` 설정 import는 아직 남았다. backup/checkpoint는 현재 항상 켜진 앱 관리 정책이며 legacy opt-out/path/suffix와의 의도적 차이를 최종 parity 판단 전에 명시한다. legacy UI/launcher는 유지한다.

## Native gate 진행 기록 (추가)

- 파일 선택 대화상자에서 테스트 폴더를 선택하고 Java 월드/DataVersion/backup count를 표시했다. 최초 Go-to-folder 탐색에서 Open 비활성 상태가 지속되어 취소 후 재열기로 선택 성공; 아직 앱 결함으로 단정하지 않는다.
- Custom localhost/mock model/synthetic credential을 Settings에서 저장하고 `API 키 저장됨`, 입력 필드 비움 상태 확인. 실제 키/키체인 무접근. 테스트 값은 production 계정과 분리된다.
- Scan 화면 진입 후 자동 제어에서 `cgWindowNotFound`. 평가 앱 프로세스는 존재했고 crash report는 발견되지 않았다. 원인을 앱 crash로 확정하지 않는다. Dock 조회가 도구 내부 timeout으로 장시간 대기했으므로 같은 호출은 반복하지 않는다.
- macOS 재활성화 및 single-instance 재실행에서 main window `show`/`unminimize`/focus를 추가하고 재빌드 중. 창 재접속, scan/run/restore/hash/export, restart credential retention은 아직 PASS 아님.
- 외부 resource pack은 현재 안전한 백업 경계에서 실패가 API 호출 뒤 발생할 수 있는 문제를 발견했다. provider 호출 전 preflight 거부 회귀를 구현 중. 외부 folder/ZIP 지원 자체는 완료 아님.

## Native workflow 확인 (2026-09-30 추가)

- latest unsigned eval build: PASS (59.07 MiB). startup/readiness는 지연 후 성공했다. custom protocol/boot 실패로 확정하지 않는다. 최신 Rust 21 PASS.
- 실제 chooser→world inspection→scan(3 source/3 occurrences)→검색 Shop/type text_display(1 row)→초기화(3 rows)→Keep original 제외→Welcome traveler 직접 번역→Run(전송1/manual1/request1)→mock API1→completed/2 changed files/sample/120in20out→Backups/verified→restore confirmation/busy→recovery snapshot 표시 PASS.
- 번역 후 원본 snapshot 대비 변경 파일은 `region/r.0.0.mca`, `entities/r.0.0.mca` 2개만. 제외된 `region/r.1.0.mca`와 level.dat 무변경. restore 후 4/4 파일 SHA256 byte-identical.
- 재시작 후 localhost model/endpoint 및 `API 키 저장됨`, secure input 비움 상태 확인. 실제 키/키체인 접근 없음.
- native Save dialog로 Git 밖 `native-settings.json` 저장 및 JSON/secret omission 확인 PASS. Save dialog 중 도구가 user changed 상태를 반환해 새 state 확인 후 다시 진행했다.
- mock-only 비용 $0. native progress phase/close guard/cancel, 최신 report Save, 실제 API/usage는 추가 검증 중.

- native 지연 mock 재실행에서 `문장 번역 진행: 0 / 3`, 요청 `0 / 1`, failed0 및 elapsed의 실제 progress 표시 확인. 작업 중 close click에 창 유지와 `취소하거나 완료된 뒤 창을 닫아 주세요` 안내 확인. 취소 click 후 disabled cancel/busy cleanup 상태 확인; 최종 cancelled/hash는 확인 중.
