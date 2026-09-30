# PomiTranslate 후속 에이전트 인계 — Phase 2 복구·완료, Phase 3, credential 변경

작성일: 2026-09-30 (Asia/Seoul)\
이 문서는 이전 대화 없이 다음 에이전트가 이어서 작업하기 위한 실행 계약이다. 최초 요청은 계획·문서 갱신이었고, 이후 사용자가 문서 commit/push를 요청했다. 이번 문서 전용 commit은 Phase 2 완료를 뜻하지 않는다. 구현·유료 호출은 수행하지 않았다. 사용자가 후속 구현을 요청하면 아래 순서로 진행한다.

## 1. 읽기 순서와 우선순위

1. 프로젝트 루트 `AGENTS.md` 및 사용자 최신 지시.
2. 이 인계 문서.
3. [credential 저장 변경 계획](credential-storage-plan.md).
4. [개정된 구현 계획](PomiTranslate_Implementation_Plan_and_Agent_Instructions_v1.1.md). 프로젝트 루트에도 원본이 있으며, 이 저장소의 사본만으로 원격 인계 가능하다.
5. [현재 코드 상태](current-state.md), [남은 작업](remaining-work.md), [fixture 지원 표](support-matrix.md).

2026-09-30 결정: 데스크톱 credential 기본 저장을 **로컬 암호화 DB + 별도 설치별 암호화 키 파일**로 변경할 계획이다. 키체인은 선택 기능으로 유지한다. 이전 문서의 “OS 키체인에만 저장” 요구보다 이 변경이 우선한다. 평문 API 키 저장 금지는 유지한다. 상세 threat model과 migration은 credential 계획을 따른다.

## 2. 저장소와 실제 Git 상태

```text
프로젝트 루트: /Volumes/DevSSD/Developer/Projects/General/PomiTranslate
제품 저장소:   /Volumes/DevSSD/Developer/Projects/General/PomiTranslate/reference/Minecraft-World-Translator
원격:          origin / https://github.com/kim0040/Minecraft-World-Translator.git
계획한 작업 브랜치: feat/pomitranslate-desktop-app
```

문서 작성 직전 실제 확인:

- 체크아웃 브랜치 `main`.
- HEAD `e70d27a`; 로컬 `main`, `origin/main`, `feat/pomitranslate-desktop-app`가 같은 commit을 가리킴. 원격 ref는 fetch하지 않은 로컬 관측값이다.
- `git status --short` 비어 있음, `git diff --check` 통과.
- Phase 2 화면·frontend test가 tracked 상태다. desktop baseline은 `7c96dba`, virtual helper는 `34ea90d`, virtual UI/test 및 endpoint 수정은 `fa7c82d` history에 있다.
- reflog에는 feature branch와 main 사이의 checkout/fast-forward가 기록돼 있다.

이전 대화의 “미커밋 Phase 2 WIP / feature branch”는 현재 파일 상태와 다르다. **Phase 2 코드가 commit에 있다는 사실은 Phase 2 완료 gate 통과를 뜻하지 않는다.** 기존 commit을 완료 commit으로 소급해서 보고하지 않는다. 왜 상태가 바뀌었는지 추정하지 않는다.

후속 시작 명령(제품 저장소에서):

```bash
git status --short --untracked-files=all
git branch --show-current
git log --oneline --decorate -15
git diff --stat
git diff
git diff --check
git show --stat 34ea90d
git reflog -15
```

현재 WIP·브랜치를 먼저 확인하고 feature branch 사용 여부를 결정한다. reset --hard, checkout ., clean -fd, 기존 파일 재작성으로 인계를 시작하지 않는다. 프로젝트 루트 자체는 Git 저장소가 아니다. 제품 저장소 docs에 인계·credential 계획·개정된 구현 계획·과거 test baseline 사본을 함께 포함해 문서 전용 commit/push한다. 다른 머신에서는 이 저장소 docs만으로 인계 내용을 읽을 수 있다. 로컬 루트의 에셋 원본과 ignored screenshot/test copy는 별도이며 Git에 포함하지 않는다. 실제 push 여부는 Git 원격 ref로 확인한다.

## 3. 유지할 기반과 완료된 코어 작업

Python core, Tauri 2, Rust shell, Svelte 5, TypeScript/Vite, JSONL sidecar, fixture, backup, app state를 유지한다. 처음부터 만들지 않는다.

Phase 0: Collect → Translate → Write, provider 오류 분류/circuit breaker/Retry-After, needs_retry·partial·failed, checkpoint 재시도, unreadable/unwritable 경고, token guard, usage/request 집계. 주요 과거 commit `46c27d9`, `08d9e39`.

Phase 1: `mwt/nbtio.py` byte preservation와 Java modified UTF-8(NUL/CESU-8 emoji), `mwt/extract.py` nested component/extra/with/fallback/hover/click/container/text_display/command 추출, candidate kind/location/count, server paging/filter, scan scope 분리, 앱 데이터 backup 및 legacy `.pomi-backups`, 전역 batching/동시 요청. 현재 history `c6489a7`.

과거 sample 검증 기록: 4,315 chunks, 후보 477·발생 6,308, 예상/실제 12 requests, scan 약 1.7초·실제 provider 번역 약 49.1초. 이 값은 해당 sample과 이전 검증 기록이며 모든 월드에 대한 보장이나 현 HEAD의 새 벤치마크가 아니다.

## 4. Phase 2 현재 구현

코드에 존재하는 주요 구조:

- `src/App.svelte`: shell/route/overlay 중심으로 분리.
- `src/screens/`: World, Scan, Review, Run, Result, Backups, Settings, About.
- `src/components/`: Sidebar, Stepper, CandidateTable, CandidateDetail 등.
- `src/lib/app.svelte.ts`: 작업 state/비즈니스 동작.
- `src/lib/candidates.svelte.ts`: paging/filter와 page 요청 관리.
- `src/lib/api.ts`: backend 호출 queue. 단일 sidecar의 BUSY race 대응.
- `src/lib/workflow.ts`, `format.ts`, `theme.ts`, i18n ko/en/ja.
- virtual window, 200개 단위 조회, keyboard 이동/include toggle/editor 진입.
- Settings validation, System/Light/Dark, responsive, dialog focus/ARIA.
- `tests/frontend/`: api, candidates, format, i18n, virtual, workflow tests 및 fixture init.

Phase 2에서 발견·수정했던 버그:

- sidecar 동시 호출 BUSY: frontend backend queue 추가. 취소는 queue에 막히지 않아야 함.
- concurrent provider 실패 circuit breaker: lock 안에서 abort 공유, throttle 후 abort 확인.
- Custom → 공개 provider 변경 시 숨은 localhost URL 유지: Settings 기본 URL/wire 재설정, 공개 provider 저장 시 baseUrl 생략, backend canonical 기본 URL 적용. 코드와 provider regression test가 있음.

마지막 endpoint 수정 이후 전체 실제 provider E2E는 완료하지 않았다. Rust credential 주입 시 최종 endpoint/provider 검증까지 충분한지는 별도 조사해야 한다. frontend validation만으로 보호했다고 판단하지 않는다.

추가로 소스에서 확인한 위험 경로: `_run_translator()`가 `POMI_PROVIDER`, `POMI_MODEL`, `POMI_API_BASE`, `POMI_WIRE_FORMAT` 환경변수를 저장된 UI 설정보다 우선한다 (`mwt/desktop_entry.py`). 데스크톱에서 환경변수가 provider/host를 조용히 바꿔 credential과 목적지가 어긋나지 않도록 explicit request context/환경 정리/boundary validation을 설계한다. CLI의 의도된 env override와는 구분하며, env를 주입한 실제 계약 테스트가 필요하다.

## 5. 검증 기록과 한계

다음은 이전 작업 세션에서 기록한 결과다. **이번 문서 작업에서는 재실행하지 않았다.** HEAD가 바뀌었으므로 최종 gate에서 필요한 전체 검증을 다시 수행한다.

| 항목 | 이전 기록 | 현재 완료 판정 |
| --- | --- | --- |
| pnpm check / build | 0 error·warning / PASS | 최종 변경 후 재검증 |
| frontend tests | 6 files, 22 tests PASS | 현 파일 수·결과 재확인 |
| Python core/extraction/brand/desktop/providers/reliability/release fixtures | PASS | endpoint 수정 후 full suite 재검증 |
| Rust tests | 4 PASS | vault 변경 후 재검증 |
| sidecar / Tauri debug app build | PASS | unsigned development build |
| browser UI | 14 대표 screenshot, 1440/1180/1024/840/320, effective 200%, dark, keyboard | 재설계 후 변경 화면 다시 확인 |
| accessibility | review/dark/settings/dialog axe 0; keyboard/editor/ESC focus 확인 | screen reader·전체 실기 gate 남음 |
| 실제 Tauri local mock E2E | scan → review → manual/exclude → run → backup → restore 성공 | paid integration과는 구분 |
| restore hash | 117/117 files byte-identical, 추가 파일 없음 | 새 write 변경 후 반복 |
| 이번 후속 작업 paid API | $0 기록 | 실제 호출/전후 usage 기록 미완료 |

실제 Tauri local mock 실행: MASTER→관리자(수동), Extinguisher→[번역] Extinguisher(mock), 2 translated·2 changed files·1 request, 100 input/50 output mock tokens. Mock usage는 실제 제공사 비용으로 계산하지 않는다.

실제 API라고 생각했던 두 번째 실행은 숨은 Custom localhost endpoint를 호출한 것으로 확인됐다. 따라서 **실제 OpenRouter 성공으로 기록하면 안 된다.** 복원은 다시 수행했다. endpoint 수정 후 앱 rebuild는 성공했지만 최종 paid E2E는 중단됐다.

남은 로컬 증거(영속 보장 없음):

```text
copy: /private/tmp/pomi-eval/phase2-20260929-2218/Roguefire
hash: /private/tmp/pomi-eval/phase2-20260929-2218/before.sha256
app:  /Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate.app
shots: <repo>/output/playwright/ (ignored)
```

문서 작성 시 copy 디렉터리·app bundle·14개 대표 screenshot 파일의 존재를 확인했다. hash와 app이 현 HEAD 산출물인지까지 재검증하지 않았다. `output/playwright`는 Git 밖에 있으므로 다른 머신에 전달되지 않는다. 후속 에이전트는 fixture로 재생성한다.

기존 mock endpoint: `127.0.0.1:52831/v1`, `127.0.0.1:53320/v1`. 이전 exec session 54421/72765, Vite session 18162는 과거 식별자일 뿐이다. 재사용 전 listener/PID/command/cwd를 확인한다. 다른 앱·Router/MCP 프로세스를 종료하지 않는다. 실제 API gate는 mock 서버를 끄고 canonical host를 검증해 재발을 막는다.

## 6. 다음 실행 순서 — Phase 2 우선

### 2-A. 기준선·빌드·실제 상태 복구

- Git/WIP 조사, 문서와 소스 불일치 기록.
- package scripts 기준 `pnpm check`, `pnpm test:frontend`, `pnpm build`.
- 오류가 나면 기존 화면 구조를 유지하며 수정. Svelte rune/import/prop/i18n/backend type/browser API 확인.
- 원본 sample을 복사하고 테스트 copy에 hash snapshot 생성.

### 2-B. credential 저장 변경 구현

- [credential 계획](credential-storage-plan.md)의 vault와 mode/migration을 구현.
- 상태 확인 때문에 키체인을 읽는 동작 제거. 새 local default에서 startup/Settings/scan의 keychain 접근 0회 증명.
- Rust boundary에서 공개 provider/Custom host를 검증한 뒤 키 주입.
- CLI/legacy 호환, permission, 오류, restart, privacy/i18n 문구까지 완료.
- 새 crypto/storage 기능 검증 없이 기존 키를 자동 이동·삭제하지 않는다.

### 2-C. 남은 UI/기능 회귀 확인

- **복원 후 workflow step**: `restore()`가 `resetJob()`을 호출하지만 step을 바꾸지 않음. Result 내용만 비고 step은 result로 남는 UX를 조사·수정. 복원 후 world/scan 등 유효한 단계로 돌아가야 함.
- World: metadata 의미, path 중복 제거, dimensions/resource/backup/blocker/resume.
- Scan: API 0·write 0 고지, 실제 파일 progress/elapsed/cancel, 종류·occurrence·request·coverage.
- Review: 충분한 공간, search/kind/included/excluded/manual/sort, server filter와 row count 일치, bulk include/exclude, manual editor 폭.
- Virtualization: 10k/100k fixture에서 제한된 DOM·memory·응답을 실측. ArrowUp/Down, PageUp/Down, Home/End, Enter, Space 및 offscreen focus/selection.
- Run: world/language/provider/model/include/manual/requests/tokens/cost/backup 요약, 수집→번역→쓰기, 취소·닫기 응답.
- Result: completed/partial/needs_retry/failed/cancelled/invalidated/unsupported를 사람이 이해할 문구로 매핑. usage/warnings/reason/samples/retry/backup/restore.
- Backups: 날짜/world/files/verified/type/legacy/recovery, restore 확인·busy·성공 메시지.
- Settings/About: 새 credential UX, inline validation, 그룹·advanced disclosure, branding/version/license/privacy/coverage/diagnostics.
- raw backend event/status/error enum이 그대로 UI에 노출되지 않아야 함.
- ko/en/ja missing key 0. 중국어 UI는 현재 미구현; README 중국어와 혼동 금지. 추가한다면 핵심 키 전부 채우고 검사.

### 2-D. legacy parity audit

`webui/`, `webui_server.py`, `run_web_ui.command`와 desktop/CLI를 비교한 기능표를 남긴다. parity가 부족한 동안 legacy 삭제·archive 금지.

소스에서 확인한 실제 차이: legacy의 설정 Reset/Export, prompt enhancer, translate.py 경로/상속, report-path picker, 세부 category scope/preset이 desktop UI에 동등하게 노출되지 않는다. desktop은 `inherit_translate_py=False`, 고정 reports 경로, resource-pack/skip-target 중심 scope이며 settings footer는 Save/Delete뿐이다. 계획서의 CLI/JSON report/설정 상속 계약과 비교해서 각각 구현 또는 승인된 범위 변경으로 처리한다.

추가 조사할 잠재 차이(아직 확정 미지원 목록은 아님): Comet/Custom wire, 직접 번역, 스타일 프롬프트 보조, 세부 scope/preset, skip_patterns/component prefixes, 외부 pack/locale/merge, translate.py import, report/checkpoint/continue-on-file-error/write retry, backup 옵션, 설정 export/reset, detailed timeline/current file/report 접근. backend에 있다는 이유만으로 desktop UI parity라고 하지 않는다.

빠진 기능은 desktop에 구현하거나 사용자가 수용한 명시적 범위 변경으로 해결한다. 안전 기본값이 필요한 옵션은 고급 UI와 안내로 제공한다. launcher는 기능 parity 확인 후 desktop 기준으로 정리한다.

### 2-E. 최종 Phase 2 gate

- 아래 frontend/Python/Rust/build 모두 성공.
- 모든 페이지, 실제 backend 연결, dark/system/light.
- 1440×900, 1180×800, 1024×768, 840×620, 최소 320px 접근 가능.
- 200% zoom: footer/dialog/detail/버튼 접근, overlap/clipping 없음. effective CSS viewport만 검사했다면 그 방법을 명시.
- keyboard 전체 workflow, focus visible/trap/restore/ESC/tab/labels/live/progress/reduced motion.
- 14 screenshot: 01-world-empty, 02-world-selected, 03-scan-running, 04-scan-complete, 05-review, 06-review-selected, 07-run-confirm, 08-run-progress, 09-result-success, 10-result-failed, 11-backups, 12-settings, 13-about, 14-dark-review. 실제 렌더링 확인.
- 자동 회귀: count/row mismatch, excluded/manual filter, model 변경 scan 유지·target 변경 invalidate, raw event/status 비노출, editor 폭, 대규모 virtual DOM, partial/failed.
- 실제 Tauri: 앱 기동→copy 선택→검사/scan→search/kind→exclude/manual→run/progress/result→backup/restore→byte-identical.
- 실제 provider 최소 호출: endpoint 확인, token/usage/실제 비용 기록, 실패는 실패로 남김. 저장된 keychain 키를 사용하려면 opt-in migration에 의한 1회 접근 가능.
- 번역 후 예상 파일만 변경, restore 후 전체 대상 hash·file list 차이 0.
- 문서 갱신→diff review→**Phase 2 완료 시에만 commit→push**. 미완 gate가 있으면 완료 commit 금지.

## 7. Phase 3 — Phase 2 gate와 commit/push 이후

### 3-A. 지원 scope

실제 sample에서 datapack, command storage, scoreboard, external pack의 visible text와 internal id/state/function logic를 구분해 조사한다.

- 기본 standard NBT 유지. Datapack visible text / command storage / external packs는 opt-in.
- datapack advancements/item/loot/tellraw/title/JSON components 및 function command를 schema/명령 기반으로 추출. 모든 문자열 일괄 번역 금지.
- command_storage_*.dat는 알려진 text component/schema만 처리. unknown은 detected/unsupported/preserved로 보고.
- scoreboard internal objective/team/id와 표시 이름 구분. 지원 근거 전에는 translated라고 표시하지 않음.
- coverage에서 발견됨·검사됨·선택 안 됨·미지원 구분. 실제 세지 않은 detected count를 만들지 않음.
- 외부 pack ZIP/folder, locale skip/overwrite/fill/merge, namespace collision, backup/write boundary, ZIP slip/symlink/path traversal 검증.

### 3-B. occurrence와 데이터 계층

- candidate → occurrence id 정규화, 특정 위치만 exclude해도 다른 위치 번역.
- scan plan/override/checkpoint/resume schema revision·migration 함께 설계.
- 첫 몇 위치만 payload, `모든 위치 보기`는 lazy paging/query. 현재 5곳 제한을 전체 locations로 오해하지 않음.
- 100k+ candidate/occurrence, TM, glossary, job history에 SQLite 도입 검토. credential vault만 구현했다고 전체 data layer 완료라고 하지 않음.
- transaction, migration backup/rollback, update compatibility, indexes/query perf 검증.

### 3-C. 번역 품질과 추정

- glossary source/target/context/case/exact/contains, world/global 구분·revision·import/export/delete.
- TM key: source+target+정규화 prompt policy/style+glossary revision+필요한 context/schema/segmentation revision. 모델 독립 재사용 여부를 명시적으로 설계.
- world 격리 기본, 잘못된 오래된 번역 invalidate/edit/delete, deterministic manual 우선순위.
- 공급자/model pricing·조회 시각으로 estimated input/output 및 low/high cost. 근거 없으면 `추정 불가`, $0으로 위장 금지.
- 실제 usage와 예상값 비교, 재개는 남은 분량 기준, provider requests와 TM hits 별도 집계.

### 3-D. 안전·호환성·배포

- modern Java 여러 버전, region/entities/Nether/End/custom dimensions, gzip/zlib/none/LZ4/external .mcc, large world, corrupted/unreadable/mixed chunks, emoji/NUL.
- unknown compression/NBT/write permission/token guard/provider/partial write를 silent skip하지 않음.
- kill/power/sidecar crash → interrupted detection, checkpoint/backup consistency, 사용자 복원/재개/폐기, 중복 과금 안내.
- clean-machine: macOS Apple Silicon, Windows x64, Linux x64. macOS Intel 지원 목표가 유지되면 별도 검증. CI build와 실제 clean startup 구분.
- sidecar/Python dependency/assets/app-data/backup/credential/chooser/startup, dev absolute path 없음.
- 서명 credential 없으면 unsigned development artifact와 blocked release gate로 기록. 임의 키 생성·signature verification disable 금지.
- updater signing/rollback, Apple notarization, Windows signing, SBOM/third-party notices, startup/update/migration.
- `mc_world_translator.py`, `desktop_entry.py`를 translation/scan/extract/nbt/backup/report/jobs 단위로 자연스럽게 분리. 대규모 rewrite 금지.
- VoiceOver/NVDA/high contrast 등 미완 접근성, diagnostics path/secret redaction, cache/TM 삭제와 설정 export/reset도 완료 범위에 포함.
- docs/support matrix를 supported/partial/experimental/unsupported로 실제 증거에 맞춤.
- Phase 3: 구현→테스트→실제 확인→docs→diff review→commit→push. cross-platform 최종 gate를 생략하지 않음.

## 8. 검증 명령과 비용·데이터 경계

제품 저장소의 Python 3.12 `.venv`를 사용한다. 설치 상태와 package scripts는 실행 전 확인한다.

```bash
pnpm check
pnpm test:frontend
pnpm build
.venv/bin/python test_core.py
.venv/bin/python tests/test_extraction.py
.venv/bin/python tests/test_brand_secrets.py
.venv/bin/python tests/test_desktop_entry.py
.venv/bin/python tests/test_providers.py
.venv/bin/python tests/test_reliability.py
.venv/bin/python tests/test_release_fixtures.py
cargo test --locked --manifest-path src-tauri/Cargo.toml
pnpm sidecar:build
pnpm tauri build --debug --bundles app
```

`test_release_fixtures.py`는 support matrix를 생성할 수 있으므로 실행 후 diff를 검토한다. build-cache 경로가 sandbox 밖이면 허용된 `/Volumes/DevSSD/Developer/Temp/Build` 또는 `/private/tmp`를 사용한다.

안전 copy 원본 예:

```text
/Volumes/DevSSD/Developer/Projects/General/PomiTranslate/sample/[1.21.10] Roguefire v1.1
```

원본 write 금지. `/private/tmp/pomi-eval/` copy만 변경한다. 전후 hash와 restore hash를 보관한다. 원본이나 번역 텍스트를 외부로 불필요하게 업로드하지 않는다.

실제 API 추가 테스트 비용 총 상한 $1, 목표 $0.01–$0.10 이하. mock 먼저, 마지막 최소 호출. 이전 지시에서 이 예산 내 최종 E2E는 명시적으로 허용됐지만 이번 문서 작업에는 호출하지 않는다. budget/승인 범위가 바뀌면 최신 지시를 따른다. 키 값은 로그·화면·git·답변에 출력하지 않는다. 저장된 account `openrouter`, 모델 예 `xiaomi/mimo-v2.6-flash`; 존재나 사용 가능 여부는 실제 확인 전 보장하지 않는다.

기존 Custom mock credential이 테스트 중 저장됐을 수 있다. 키 값을 읽어서 조사하지 않는다. 사용자 항목과 구분하고 삭제를 자동 수행하지 않는다.

CI: Python main push/PR + 관련 paths. Installer manual/tag, 수동 기본 Linux. 일반 feature push마다 3 OS installer 실행 금지. 전체 플랫폼은 최종 gate에만. signing/public release/world upload는 별도 명시 승인 없이 실행하지 않는다.

## 9. 에이전트 작업·보고 계약

- 메인: 아키텍처·통합·핵심 diff·최종 검증·완료 판단.
- AGENTS의 Luna Max 선택적 위임 준수. 좁은 read-only 조사나 독립적인 작은 구현만 위임. 파일 소유 범위 지정, 서로 같은 state/backend 파일 동시 수정 금지.
- progress는 중요한 PASS/FAIL/남은 gate를 간결히, 진행 중 60초 이상 무보고 금지.
- 실패를 고치기 전 완료로 부르지 않음. “코드 있음”과 “실제 검증됨”을 분리.
- 후속 인계에는 변경 파일, commit/branch/WIP, 실행 명령·결과·산출물, 비용 누계, 미완 gate, 다음 1단계를 기록.

최종 사용자 보고 형식:

```text
Completed: Phase별 구현
Git: Phase 2 hash / Phase 3 hash (없으면 미완)
Tests: Python / Frontend / Rust / Tauri E2E / Real API / Restore
UI: 각 viewport / 200% / dark / keyboard
API cost: 실제 비용과 확인 방법
Remaining limitations: 미구현·미검증·외부 차단 구분
Release readiness: ready / development-ready / blocked + 근거
Delegation: 사용한 worker와 Main 검증 요약
```

현재 판단: **Phase 2 미완, Phase 3 미시작, development-ready 수준의 개발 산출물 기록만 있음.** 새 credential 저장은 미구현이고 최종 paid integration·legacy parity·플랫폼 release gate가 남아 있으므로 ready라고 선언하지 않는다.

## 10. 다음 에이전트에게 전달할 시작 문구

```text
PomiTranslate 작업을 이어서 진행해줘.
제품 저장소는 /Volumes/DevSSD/Developer/Projects/General/PomiTranslate/reference/Minecraft-World-Translator 이다.
먼저 프로젝트 AGENTS와 docs/agent-handoff-2026-09-30.md, docs/credential-storage-plan.md를 읽고 Git/WIP 상태를 확인해줘.
기존 Phase 2 화면과 Phase 0/1 core를 보존하고, 새 로컬 암호화 credential 저장 계획을 포함해 Phase 2를 검증까지 완료해줘.
완료 gate를 통과한 뒤 docs/diff review → Phase 2 commit/push → Phase 3 구현/검증/docs/commit/push 순서로 진행해줘.
인계의 이전 검증 기록을 현 HEAD 결과로 단정하지 말고, paid API 총 추가 $1 상한·copy world만 write·secret 비노출·서명/public release 별도 승인 경계를 지켜줘.
누락 기능/외부 검증이 있으면 완료라고 하지 말고 구체적인 remaining gate와 증거를 보고해줘.
```
