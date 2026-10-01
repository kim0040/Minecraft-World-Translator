# Phase 2 최신 검증 재개 — 2026-09-30

> 최신 상태는 [2026-10-01 검증·재개 기록](phase2-validation-2026-10-01.md)을 따른다. 이 문서는 9월30일 실행 이력이다.

상태: 사용자 “이어서 해줘” 요청으로 재개. **Phase 2 진행 중 / Phase 3 미시작**, main/865b51d의 모든 WIP 보존, 이번 commit/push 없음. 이 문서는 이전 중단 기록보다 우선한다.

## 최신 후속 검토 — credential 모드 전환

현재 최종 후속 결과: **browser 전체64 PASS/1.7m, frontend48 PASS, Rust23 PASS, check0 errors/0 warnings, production build PASS**. 설정 저장 중 busy/입력·중복 저장·이동 차단을 추가했고, 지연 fixture에서 저장 완료 후 편집·navigation 복귀 및 저장된 model 유지도 검증했다. fieldset 추가로 발생한 Svelte CSS selector 경고6개는 wide-layout selector를 맞춰 모두 해소했다. 최신14 screenshot을 다시 생성했으며 변경된 Settings 및320px endpoint screenshot을 직접 확인했다. 저장 busy까지 포함한 r1 unsigned debug bundle59.08MiB도 앱 종료 후 재빌드했다. 아래 전체63 미실행/targeted 숫자는 그 이전 실행 단계의 기록이다.

최신 r1 native 재확인: bootstrap/scan3 보존, Settings Save에서 실제 `저장 중…`·Sidebar `작업 중`·필드/키/메뉴 disabled를 직접 관측했고 완료 후 준비/편집 복귀 및 빈 stored-key 입력을 확인했다. API/월드 쓰기 없는 public 설정 저장이다. 새 mock 탭은 `299115974`, 수동 preview 서버5198(session6107)을 사용자 직접200% 확인용으로 유지한다(이전 listener 종료 기록보다 우선). r2 앱은 정상 종료했다. r1은 기존 Custom/mock 설정 화면으로 복귀해 유지한다. OpenRouter 선택 준비 과정에서 AX 선택·Return이 폼 submit과 섞여 초안이 원래 값으로 돌아왔으므로 provider 변경 성공으로 기록하지 않는다. 사용자가 직접 OpenRouter/모델을 선택하고 키를 입력·저장해야 한다. 실제 OpenRouter 키 없음, fake Custom credential은 별도 계정에 남아 있다. OS keychain 버튼은 누르지 않았다. 합성 원본4파일 해시 차이0, r2 앱 데이터에서 합성 키 평문 미검출도 재확인했다.

- 최종 diff 검토에서 Local → Session 전환이 기존 ciphertext row를 남겨, 재시작 뒤 Local로 돌아가면 옛 키가 재활성화되는 결함을 발견했다. 회귀 test에서 row 1 != 0 실패를 먼저 재현한 뒤 수정했다. 비로컬 모드에서는 local row를 제거하며, 만료된 session에서 키 없이 Local로 전환할 때 과거 버전의 stale row도 제거한다. 이 제거는 mode metadata와 같은 SQLite transaction이다. keychain 모드 삭제도 앱의 local 복사본을 함께 제거한다. 명시적으로 가져온 기존 OS keychain 원본은 자동 삭제하지 않는다.
- Rust 전체 **23 PASS**, frontend 전체 **48/9 files PASS**, check/build 및 cargo fmt/diff check PASS. 기존 metadata 실패 rollback test도 PASS. 실제 OS keychain 전환·삭제는 실행하지 않았으며 이를 native 성공으로 주장하지 않는다.
- Custom endpoint 수동 입력이 user info/query/fragment/공백/잘못된 port를 허용하던 inline validation을 import와 같은 규칙으로 통일했다. ko/en/ja 오류 이유와 Save disabled를 추가했다. browser targeted **4 PASS**(1440/840/320 endpoint 3 + 기존 credential UX 1), 3개 새 screenshot 직접 inspection PASS. 앞선 전체59 및 screenshot28/수동preview1 기록은 별도이며, 현재 전체63 일괄 실행은 하지 않았다.
- 최신 Rust/frontend의 **unsigned debug Tauri build PASS(59.08 MiB)**. 새 `app.pomitranslate.eval20260930r2` / `PomiTranslate Credential Eval.app`로 기존 r1 데이터와 분리했다. 같은 packaged sidecar는 Python 변경이 없어 재사용했다. 네이티브에서 합성 키 Local 저장(row1) → 빈 새 키로 Session 전환(row0, 사용 가능) → 정상 종료 → 재시작(세션 선택 유지, 키 없음) → 빈 키로 Local 저장(row0, 키 없음)을 확인했다. API 요청/키체인 접근/월드 쓰기 없음. metadata 결과는 temp `credential-transition-result.json`에만 남긴다.
- 첫 r2 `getApp` UI 도구 호출은 약260초 지연됐다. 이후 프로세스 CPU0.0%, 화면 준비를 확인했고 정상 재시작은 첫 관측약1.4초에 loading 화면이 보였다. 도구 호출 시간과 실제 startup 시간을 동일시하지 않으며 초기 지연 원인은 미확정이다. 첫 AX secure-field setValue 뒤 저장은 credential row0이었고, 실제 키보드 입력 후 row1/빈 입력 UI를 확인해 그 이후 전환만 PASS로 기록한다.
- 브라우저 정책은 이번 같은 연결에서 탭 생성이 정상화됐다. 그러나 탭 단축키가 실제 확대를 바꾸지 않았다(2550×1320 CSS px, DPR2, visualViewport.scale1, overflow0). native Chrome 창은 검증 탭과 일치하지 않았으며 Comet 창 binding은 자동 승인 검토가 로그인 콘텐츠 노출 가능성을 이유로 거부했다. 우회하지 않았다. **최신 실제200%는 여전히 미완**이며 사용자가 fixture 탭을 직접200%로 바꾸도록 요청했다. viewport/DPR을 실제200% 증거로 취급하지 않는다.
- 실제 키 입력·저장은 computer-use credential handoff 규칙 때문에 사용자에게 요청했다. 실키 등록 또는 확대 변경 답변은 아직 없으며 실제 API 비용은 계속 **$0**. Phase2 완료 commit/push 및 Phase3는 미실행이다.

다음: 사용자 실제 키/확대 응답 → 최신 실제200% inspection → 현재 최신 r1 bundle에서 최소 actual provider/usage/byte-identical restore → legacy parity/scope 계약 및 남은 diff 최종 review → Phase2 commit/push. 코드가 추가 변경되면 실행 앱을 먼저 종료하고 다시 빌드한다. 이전 r1 mock E2E 증거는 아래에 보존하며 r2는 credential 전환 회귀 증거다.

## 구현

- `settings.import_legacy` preview: 사용자 선택 .py 텍스트를 bounded AST로 읽으며 실행/import하지 않는다. BASE_URL/MODEL/SYSTEM_PROMPT 문자열 상수만 draft로 가져온다. API_KEY/경로/다른 이름은 제외, 동적 값과 잘못된 endpoint는 generic error. preview는 설정·키체인·월드를 변경하지 않는다. 사용자 Save가 필요하다. CLI legacy loader는 유지한다.
- Comet API 직접 선택: 기존 CLI provider를 desktop에 복구했다. Rust credential/provider boundary 및 Python routing에 기존 builtin endpoint를 고정한다. Custom endpoint와 credential account는 분리한다. 기존 Comet JSON의 별도 endpoint는 Custom으로 유지한다.
- Gemini public settings export/import roundtrip 오류를 수정했다. Gemini wire는 public provider에서 지원하며 Custom의 지원 규격은 OpenAI/Anthropic으로 유지한다.
- native에서 Sidebar elapsed가 0초로 고정되는 문제를 발견해 ticking state를 추가했다. browser targeted 6 PASS 후 최신 bundle을 재빌드했다. native 스캔 중 sidebar 8초/main 9초를 직접 확인해 증가 동작을 검증했다.

## 검증

- pnpm check 0 errors/0 warnings, frontend 47/9 files PASS.
- Python 전체 최신 16/16 suite PASS(legacy parser 11 cases 포함). 처음 4개 mock server suite는 sandbox bind 권한 부족으로 실패; 필요한 local-server 실행권한으로 재실행 성공. 실제 API/키체인 무접근.
- Browser 전체 59 PASS/1.7m. 이후 screenshot 경로만 정리한 screens suite 28 PASS/1.3m, 새 수동 preview 1 PASS/6.6s. 새 test를 포함한 전체60 일괄 실행은 하지 않았다. 새 import/Comet/pack 1440·840·320 controls 포함. 중간 영어 문구 수정 오류로 첫 test 부팅이 실패한 54/55 실행은 PASS로 취급하지 않으며, 수정 후 최신 58 전체 PASS를 확보했다.
- Rust 21 PASS. pnpm build PASS. sidecar package PASS 및 실제 packaged JSONL legacy preview PASS. 최초 smoke 명령의 --jsonl 누락을 고쳐 확인했다.
- 최신 취소/locale/import/Comet를 포함한 isolated unsigned debug Tauri build PASS (59.08 MiB). Sidebar tick까지 포함한 후속 unsigned bundle도 PASS(59.08 MiB), 실행 상태 확인.
- 최신 native 설정: invalid target ../bad.json의 Save disabled, ja_jp.json+skip-existing=true 저장, reviewed scan invalidate 확인. fresh startup/local credential stored/blank input 확인. synthetic world scan3 및 mock 번역3/request1/token120/20 완료 후 native restore를 수행했고 원본 4파일 해시 차이0 확인. 최신 native 취소 회귀 PASS: 3 번역문 준비/changed0/request1/input120/output20, 최신 JSON 보고서와 UI 일치, 원본4파일 해시 차이0. 뒤의 재시작 및 probe에서 resource pack options 유지 확인.
- 추가 실제 API 비용 $0. 원본 sample 미변경. real API는 사용자 직접 local key 등록 또는 후속 지시가 필요해 async 질문했으며 응답을 기다린다. 키를 채팅/로그/파일에 평문 전달하지 않는다.

## 다음 gate

최신 실제 200% zoom final gate(브라우저 정책 차단 해소 필요) → legacy external pack 범위 계약 정리 → 최소 actual API/usage → docs/diff → Phase2 commit/push → Phase3.

External ZIP/folder scope는 아직 지원하지 않으며 in-world resources.zip만 지원한다. raw file merge도 미지원. safe import/Comet가 구현됐으므로 이를 다시 미착수로 표시하지 않는다. Legacy UI/launcher는 아직 보존했다. clean machine/cross-platform/signing/release gate 미실행.

## 환경

/tmp/pomi-eval/resume-20260930 synthetic 월드와 snapshot/exports/mock/config를 유지한다. Native eval identifier app.pomitranslate.eval20260930r1이며 production root와 분리된다. mock localhost52973은 취소 gate 후 정확한 소유 PID를 확인해 종료했다. 브라우저 test 서버5197 및 수동 검증 서버5198도 종료했으며 listener 없음 확인. 이전 export 테스트가 synthetic 월드에 pomi-settings.json을 생성했으므로 폴더 파일 수는5지만 translation 대상 원본4개는 byte-identical이며 해당 JSON은 번역 파일이 아니다. Git에 temp artifacts/월드/DB/키를 추가하지 않는다.


## 후속 native 증거와 미완 경계

- 지연 mock이 취소 요청 전에 두 차례 완료된 실행은 취소 PASS로 취급하지 않는다. 매번 native backup restore 후 원본 해시를 확인했다. 마지막 실행은 실제 translate phase(0/3)에서 취소했고 cleanup 후 cancelled/changed0/request1/usage120·20을 확인했다. `/private/tmp/pomi-eval/resume-20260930/native-cancelled-report-fixed.json`은 새 수정 후 보고서다. 이전 `native-cancelled-report.json`은 결함 재현 파일이므로 구분한다.
- 최신 clock bundle 재시작에서 CUA timeout 두 차례와 평가 앱/sidecar 높은 CPU 관측. 현재 실행 앱과 동일 bundle 경로를 재빌드한 상황과 연관 가능성이 있으나 원인은 확정하지 않는다. 정확한 이번 평가 PID만 종료했고 응답하지 않던 sidecar는 KILL 후 재실행했다. 이후 bootstrap/Settings UI 정상, 별도 bundled JSONL bootstrap response.ok, 옵션 유지 확인. **다음 build는 평가 앱을 먼저 종료하고 진행한다.** 반복 cold startup latency/CPU는 남은 성능 gate에서 확인한다.
- native Settings import 파일 chooser는 열리고 .py fixture도 목록에 보였으나, CUA AX 선택이 다른 항목을 선택하고 Go-to-folder clipboard 동작이 timeout이었다. 취소 후 화면을 복구했다. **native 파일 선택·preview 완료 PASS가 아니다.** AST parser11/Python dispatch/packaged JSONL/browser preview는 PASS이며 이 부분을 native chooser 성공으로 대체하지 않는다.
- 최신 native 재스캔 중 sidebar 경과 시간 8초 및 main9초 증가를 스크린샷/AX로 확인했다. system dark mode가 반영된 새 화면도 확인했다. 200% zoom은 이전 검증 증거이며 최신 전체 final inspection은 아직 남았다.
- 상위 AGENTS 선택적 delegation에 따라 Luna Max 1개 worker가 bounded legacy parser 조사/2파일 구현을 수행했고 Main이 결정·bridge·회귀/패키지 검증을 완료했다. gpt-5.6-luna는 callable 목록에 없어 available gpt-6-luna Max를 사용했다.

## 마지막 재검증

- Native Python chooser **PASS로 갱신**: `super+shift+g`와 PathTextField.setValue로 합성 translate.py를 선택하고 Open AX action으로 열었다. 모델 `native-import-preview`가 draft에 들어왔고 stored-key 상태/빈 입력칸 유지. 저장하지 않고 workspace로 이동한 뒤 Settings에 돌아오면 원래 `native-fixture`로 복귀했고 scan3도 유지됐다. 이전 AX 선택/clipboard 실패는 도구 이력으로 보존한다. 화면의 Open 활성 여부와 AX disabled 표기가 불일치했으나 실제 Open 동작은 성공했다.
- 최신 14개 고정 screenshot(01–14)을 screens suite에서 다시 생성하고 Main이 모두 직접 열어 확인했다. stale numbered artifacts가 있었으므로 기존 번호 파일을 최신으로 오인하지 않도록 regression harness에 고정 매핑을 추가했다. Review/editor/dark/long path/run/result/backup/settings/about에 겹침·세로 한 글자·입력 폭 붕괴가 보이지 않았다. 320px pack 화면도 확인했다. 840/1024/1180/세로/짧은 창/resize/100k/keyboard/axe는 전체59 결과에 포함된다.
- 개발 전용 `tests/frontend/preview.html` 추가. `pnpm dev` 후 `/tests/frontend/preview.html?scenario=review`에서 synthetic backend로 같은 Svelte UI를 수동 점검할 수 있다. 실제 sidecar/API/월드 write 증거가 아니며 production Vite entry는 기존 index.html이다. 새 targeted browser test는 synthetic 후보/editor 및 외부 HTTP request 없음 확인 PASS.
- 최신 Chrome 수동200%는 **BLOCKED**: CUA가 localhost5198 접근 전 admin-enforced policy를 검증할 수 없어 access를 거부했다. 다른 도구/브라우저/우회로 접근하지 않았고 서버를 종료했다. 이전 실제200% 증거를 최신 소스 final PASS로 대체하지 않는다. Tauri 기본 View 메뉴는 Full Screen만 제공한다.
- bundle 수정 없이 평가 앱 정상 Quit 후 cold relaunch 성공. 첫 observation은 아직 빈 창, 후속 observation(launch 호출 후 약31초 이내)은 ready/scan3. 이는 확인 상한이고 정확한 startup 소요시간 측정이 아니다. 이후 평가 PID89753 CPU0.3% 관측. 이전 고CPU가 재현되지 않았으나 원인을 확정하지 않는다. Windows/Linux/clean-machine performance gate는 미실행.
- 이번 paid API 추가 비용 **$0**, 실키 직접 등록 async 질문은 미응답이다. Phase2 완료/commit/push하지 않았다. 다음 핵심 의존성은 실제 provider credential과 browser policy 회복이며 Phase3는 시작하지 않는다.
