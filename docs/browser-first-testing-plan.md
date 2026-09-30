# 웹 우선 검증과 유동적인 화면 대응 계획

기준일: 2026-09-30\
상태: 사용자 요청을 반영한 후속 실행 계약. 기존 fixture는 있지만 아래 전체 자동화·실측은 미완이다.\
연결: [전체 인계](agent-handoff-2026-09-30.md), [credential 계획](credential-storage-plan.md)

## 1. 결정

UI/UX와 브라우저에서 검증 가능한 기능은 **앱 bundle을 만들기 전에 웹에서 최대한 검사**한다. 반복적인 화면 수정마다 sidecar를 패키지하고 Tauri .app/installer를 만들지 않는다. 동일한 Svelte 화면·state·API 계약을 사용하는 브라우저 harness가 기본 개발/QA 경로다.

순서는 `정적·unit → 웹 fixture UI/기능 → 실제 Python 코어/JSONL 계약 → frontend production build → 마지막 Tauri/native/패키지 E2E`다. Python core와 Rust unit test는 중간 단계에서 필요한 만큼 실행할 수 있다. Rust test 컴파일과 .app/installer 패키징은 구분한다.

이 변경은 최종 실제 앱 검증을 생략하는 것이 아니다. 브라우저 PASS를 native file chooser, credential permission, sidecar bundling, 실제 world write/restore의 성공으로 간주하지 않는다. Phase 2/3 완료 gate와 검증→문서/review→commit→push 순서는 유지한다.

## 2. 현재 브라우저 검증 기반

- `pnpm dev`는 Vite를 `127.0.0.1`에 실행한다.
- 제품 UI는 `src/screens/`와 `src/lib/app.svelte.ts`를 그대로 사용한다.
- `src/lib/api.ts`의 invoke/listen은 Tauri에 연결돼 있다. 단순히 웹 URL을 열었다는 이유만으로 전체 기능이 동작한다고 판단하지 않는다.
- `tests/frontend/tauri-fixture-init.js`가 test-only `window.__TAURI_INTERNALS__`와 event/command 응답을 제공한다. 브라우저 시작 시 UI import/실행 전에 주입한다.
- `@playwright/test`, `@axe-core/playwright`가 dev dependency에 있다. `test:frontend`는 Vitest다. 유지되는 browser suite/script/config의 완성 여부는 후속 에이전트가 확인하고 필요하면 추가한다.
- 기존 `webui/`는 legacy parity 비교 대상이다. 새 UI를 검증할 때 legacy 화면을 대신 테스트하지 않는다.

후속 작업은 기존 fixture를 보존하고, adapter/fixture injection과 재현 가능한 Playwright 실행 명령을 명확하게 정리한다. package script를 추가하기 전 존재하지 않는 명령을 현재 실행 가능한 것으로 문서에 적지 않는다.

## 3. 앱 빌드 전에 실행할 검증

### A. 빠른 코드/계약 검사

- `pnpm check`, formatter/virtual range/status/progress/filter unit tests.
- Python scan/extract/NBT/provider/reliability/backup/resume fixture.
- credential vault/Rust boundary unit test는 OS credential과 실제 key 없이 temporary test data로 실행.
- backend schema·event·error 응답이 UI type/fixture와 일치하는지 확인.

### B. 같은 화면의 browser fixture 검증

- World/Scan/Review/Run/Result/Backups/Settings/About 전체를 실제 렌더링해서 검사.
- empty/loading/scan progress/result, large candidates, long paths/text, network/provider errors, partial/needs_retry/failed/cancelled/invalidated/unsupported.
- search/kind/included/excluded/manual/sort/paging/bulk/include toggle/editor save, 모델 변경 scan 유지·대상 언어 변경 invalidate, filter count/row count 일치.
- run summary/progress/cancel/retry, restore confirmation/busy/recovery 표시, restore 후 유효 workflow step.
- credential mode와 저장 상태/migration/오류 화면은 fake credential로 검사. 브라우저 fixture가 실제 키체인이나 운영 vault를 읽지 않음.
- 10k/100k generated candidates는 server paging을 흉내 내며 total/filter count를 정확히 계산. bounded DOM, offscreen keyboard 이동, 느린 응답·out-of-order·paging 실패·selection 보존 확인.
- keyboard only, focus visible/trap/restore, ESC, live/progress semantics, accessible names, reduced motion, axe.
- 14개 대표 screenshot을 재생성하고 눈으로 확인. diff 숫자나 axe 0만으로 가독성·layout 완료라고 하지 않음.

Mock backend의 scan/run/restore 성공은 UI 상태 전이의 증거다. 실제 월드 파일 수정이나 복원을 검증한 것으로 보고하지 않는다.

### C. 실제 backend 연결 검증

브라우저에서 실행 가능한 frontend 흐름과 별도로 기존 Python JSONL sidecar를 subprocess로 실행해 실제 scan/filter/manual/exclude/translate(mock provider)/backup/restore를 copy world에서 검증한다. 이것만으로도 PyInstaller/Tauri bundle 없이 대부분의 코어 회귀를 잡을 수 있다.

브라우저에서 실제 sidecar까지 연결하는 것이 반복 검증 시간을 충분히 줄이면 **개발/테스트 전용 transport bridge**를 좁게 추가할 수 있다. 현재 그런 bridge가 완성됐다고 가정하지 않는다.

bridge 필요 시 계약:

- production UI와 같은 typed backend adapter·JSONL schema를 사용한다. core나 UI를 별도 구현하지 않는다.
- loopback에만 bind, 세션 token/Origin 검사, 명시적인 request allowlist. arbitrary shell/file 접근 금지.
- 허용된 test-copy root·별도 temporary app-data만 접근. 원본 sample·사용자 vault·운영 설정·실제 키체인 접근 금지.
- 기본 local mock provider, paid network disabled. 실제 provider 호출은 마지막 허용된 최소 gate에 남긴다.
- cancel/progress/response id/filter count/backend error를 실제 프로토콜로 검증한다.
- test entry/config에서만 활성화하고 production build와 .app에는 bridge·mock hook을 포함하지 않는다. fallback 때문에 production이 localhost를 기다리면 안 된다.
- 정리 시 PID/command/cwd/listener를 확인하고 task 소유 서버만 종료한다.

bridge를 만들 필요가 없으면 browser fixture + subprocess contract tests 조합을 유지한다. 추가 server가 목적이 아니다.

### D. frontend production build

브라우저 문제를 해결한 뒤 `pnpm build`로 production compile을 검증한다. fixture/bridge 활성화 코드나 fake key가 production에 포함되지 않는지 확인한다. browser screenshot 수정만으로 `sidecar:build`/Tauri packaging을 반복하지 않는다.

## 4. 마지막 실제 앱 gate

위 검증이 통과하면 sidecar를 패키지하고 Tauri debug app을 빌드한다. 이때 다음 native/배포 차이를 검사한다.

- packaged startup, assets, sidecar handshake, 권한/경로/app-data/재시작 persistence.
- native folder chooser와 취소, window resize/min-size, OS zoom/scale/WebView 차이.
- local encrypted vault의 실제 file permission/DACL와 restart/read/update/delete/migration. opt-in keychain은 필요한 경우에만 접근.
- 실제 copy world의 전체 workflow와 최소 provider integration, actual usage/비용, translate→backup→restore hash/file list.
- native close/cancel, sidecar lifecycle/crash, OS-level world lock, write blocker.
- production localhost listener/test harness가 없음.
- clean-machine와 signing/updater/platform gate는 여전히 마지막 release 단계에 필요.

최종 앱 gate에서 결함이 나오면 해당 결함을 수정하고 영향을 받는 웹/코어 검증 및 앱 gate를 다시 수행한다. 원인 없이 전체 matrix나 installer를 반복하지 않는다. UI만 바뀌면 backend package를 재사용 가능한지 먼저 판단한다. Python/dependency/protocol/native 코드가 바뀌면 해당 sidecar/native build를 새로 만든다.

## 5. 화면 비율과 창 크기 대응 계약

한 가지 aspect ratio나 고정 screenshot 크기를 기준으로 화면을 설계하지 않는다. window width **그리고 height**에 따라 정보 배치를 바꾼다. 내용 접근·작업 완료를 유지하면서 desktop에서는 review 공간을 충분히 사용한다.

- CSS grid/flex, `minmax(0, 1fr)`, `min-width: 0`, 유동 폭, content 기반 breakpoint를 우선한다.
- 긴 path/source/한국어/영어/일본어가 전체 layout을 넓히거나 글자를 한 글자씩 세로로 떨어뜨리지 않음. 필요한 곳은 wrap/ellipsis + 전체 보기 제공.
- input/editor 최소 사용 폭과 버튼 touch/click target 유지. 여유가 없으면 열을 재배치/숨김 disclosure하고 핵심 action은 접근 가능하게 한다.
- 넓고 낮은 화면은 vertical 공간 낭비를 줄인다. toolbar/footer/dialog 때문에 editor/table이 사라지면 안 된다.
- 세로형/좁은 화면에서는 sidebar 축소·drawer/상단 navigation, table의 부가 열 disclosure, detail 별도 panel/dialog 등의 방식으로 대응한다. 숨긴 내용은 keyboard로도 열 수 있어야 한다.
- wide/ultrawide에서는 모든 페이지를 작은 중앙 카드에 가두지 않는다. review table/detail은 가용 폭을 사용하고 읽기용 긴 문장은 적절한 최대 폭을 둔다.
- dialog는 viewport 안에서 동작하고 body scroll/액션 접근을 제공한다. content 높이만큼 창 밖으로 늘어나지 않음.
- resize/zoom/orientation 중 검색·선택·manual draft·include/exclude·job state를 잃지 않는다. panel 변경 때 focus를 잃거나 보이지 않는 요소에 가두지 않음.
- 작은 높이에서 필요한 page scroll을 허용하고, candidate table 핵심 영역을 작은 nested scroll box에 가두지 않음.
- 실제 native min-size(현재 840×620)가 browser reflow/200% 검증을 대신하지 않는다. 최소 창 크기의 정책은 실제 UX 확인 후 결정한다. min-size를 낮추면 native resize도 재검증.

## 6. 실측 matrix와 성공 기준

기존 필수 viewport 유지:

- 1440×900, 1180×800, 1024×768, 840×620.
- 최소 320 CSS px에서 내용과 action 접근 가능. 모바일 최적화를 release promise로 추가하지 않음.

대표 비율/높이 추가:

- 1280×720 및 1920×1080 — 16:9.
- 2560×1080 — ultrawide.
- 800×1000 — 세로형.
- 1180×500 및 840×480 — 짧은 높이/reflow 스트레스.
- 320×568 — 좁은 폭.
- breakpoint 전후 ±1px, 창을 연속 드래그해서 크기 변경, 200% 실제 zoom와 시스템 scale.

모든 화면을 핵심 desktop/좁은 viewport에서 확인하고, 추가 matrix는 위험이 있는 review/detail/settings/dialog/run/footer 중심으로 검사한다. 모든 언어×theme×viewport 조합을 매 수정마다 전수 실행하지 않는다. 최종 대표 matrix와 검증한 조합/누락 조합은 기록한다.

성공 기준:

- page horizontal overflow 없음(필요한 데이터 table 내부 scroll은 명시적으로 허용).
- 글자/label/button/input overlap·clipping·20px input·수직 한 글자 줄바꿈 없음.
- 주요 action/dialog/footer/detail/editor를 mouse와 keyboard로 접근할 수 있음.
- 가상화는 container resize 뒤 visible range/height/focus를 올바르게 계산하며 DOM이 전체 total에 비례하지 않음.
- 200% zoom에서 내용 접근과 workflow 유지. 단순히 CSS viewport만 줄인 검증은 실제 zoom과 구분해 보고.
- screenshot inspection·DOM 측정·keyboard 동작을 함께 기록. 현재 검사하지 않은 조합을 PASS라고 하지 않음.

## 7. 증거와 완료 보고

보고서를 `웹 fixture`, `실제 Python/JSONL`, `Tauri native/패키지`, `실제 provider`로 구분한다. 실행 명령·commit·fixture/viewport·검사 결과·실제 side effect 유무를 적는다. browser mock result를 paid/restore/credential gate와 섞지 않는다.

이 문서는 새 검사 절차와 반응형 요구를 추가한 것이다. 새로운 browser bridge, Playwright suite, viewport matrix, native gate를 이번 문서 변경에서 실행하거나 완료했다고 주장하지 않는다.
