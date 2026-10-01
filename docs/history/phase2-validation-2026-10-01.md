# Phase 2 검증과 재개 기록 — 2026-10-01

> **재개 이후 최신 상태:** [2026-10-01 재개·검증](phase2-resume-2026-10-01.md). 아래 중단/검사 시점 기록은 이력이며 새 실행 결과는 재개 기록을 따른다.

> **2026-10-01 중단 갱신:** [최신 중단·인계](phase2-pause-2026-10-01.md)가 아래 진행 기록보다 우선한다. 외부 ZIP/사용량 조회 후속 구현과 검증 시점, 재개 순서는 해당 문서를 따른다. [테스트 지연 조사](test-efficiency-audit-2026-10-01.md)도 기록했다. Phase2 미완/Phase3 미시작, commit/push 없음.

이 문서가 9월 30일의 중단/진행 기록과 충돌할 때 우선한다. **Phase 2 진행 중, Phase 3 미시작. 완료 commit/push 없음.** 제품 저장소 `main` / `865b51d`, 기존 modified/untracked WIP를 보존했다. 원본 sample world는 변경하지 않았다.

## 구현·검증한 변경

### 실제 WebView 확대와 네이티브 dialog

- `src-tauri/src/zoom_menu.rs`: 기본 메뉴 유지, View 메뉴 75/100/125/150/175/200%, Cmd/Ctrl+0 100%, Cmd/Ctrl+2 200%. 메뉴 상태는 성공한 확대값만 반영하며 실패는 localized toast로 알린다.
- `Dialog.svelte`: fixed/inset 및 동적 viewport 최대 높이. Native에서는 AX tree에 대화상자가 있어도 backdrop만 보이는 결함을 발견했다. fixed 위치만 바꿔서는 해결되지 않았고, translate/opacity 등장 애니메이션 제거 후 정상 렌더링됐다.
- 실제 macOS Eval 앱, 1180×800 논리 창의 WebView 200%: 상세 editor에 한국어 입력, Tab→직접 번역 삭제→하단 닫기, Return, ESC, 복원 확인창 Cancel/Restore, Settings 하단 import/export/reset/delete/save 접근을 확인했다. 긴 화면은 내부/페이지 스크롤로 접근했다. CSS zoom 또는 retina DPR을 이 증거로 대체하지 않았다.
- 브라우저 회귀는 짧은 viewport에서 dialog 경계·footer scrollIntoView·editor focus·resize draft 보존을 검사한다. footer가 처음부터 보인다고 요구한 초기 assertion은 정상 내부 스크롤을 오해해 실패했으며, 실제 접근 가능성을 검사하도록 수정했다.

### 월드 입력 경계와 대형 파일 해시

- 수정 전 외부 `resources.zip` symlink를 검사해도 blocker가 없고, 외부 파일 변경이 월드 지문에 반영됨을 재현했다.
- `mwt/layout.py`, `mwt/safety.py`, translator/desktop entry: level/region/entities/관련 디렉터리·pack의 canonical 경계를 검사한다. 외부 파일은 읽기·API 호출 전에 차단한다. 내부를 가리키더라도 resources.zip symlink는 restore topology 보존을 위해 차단한다. 서버 루트의 관련 없는 plugin symlink는 차단 대상이 아니다.
- `tests/test_world_path_boundary.py` 6 회귀: pack on/off, 외부 region/entity/file/dir/level, server plugin 경계, streaming hash 동일성. 전체 Python suite에 포함됐다.
- file SHA-256과 world fingerprint는 스트리밍한다. 64 MiB 합성 파일의 tracemalloc peak: 기존 read_bytes 64.0 MiB, file hash 약0.26 MiB, fingerprint 약2.03 MiB. **Python allocation 측정이며 process RSS/전체 대형 월드 성능 결과가 아니다.**
- canonical check와 open은 별도이므로 악의적인 동시 symlink 교체까지 원자적으로 막았다고 주장하지 않는다. 일반 월드 지문은 유지했으나 과거 server-root의 plugin/cache까지 포함했던 checkpoint는 새 범위에서 invalidation될 수 있다.

### 재개 시 최신 검토 무시 결함 — RED/GREEN 및 실제 앱 확인

1. 실제 native Run은 직접 번역1/외부전송0/요청0을 표시했지만, Resume 결과는 이전 checkpoint 번역3/파일3을 적용했다. 격리 합성 월드에서만 발생했다. 완료 gate 실패로 기록했다.
2. 앱의 Backups→Restore로 즉시 복원했고, before.json의 대상4파일 해시 차이0을 확인했다. 당시 잘못된 번역 백업 `20260930T153151Z-e52abeb5c4d1-translation`, 복원 직전 recovery `20260930T153518Z-01f4365c11a6-recovery`.
3. 원인: `desktop_entry.handle(translate.resume)`이 새 요청의 excludedCandidateIds/candidateOverrides를 이전 checkpoint 값으로 덮어썼다. 이전 클라이언트가 생략한 필드만 기본값으로 보충하고, 명시적으로 보낸 새 값(빈 배열/객체 포함)을 우선하도록 수정했다. 코어의 검토 fingerprint/cache invalidation은 유지했다.
4. `tests/test_desktop_parity.py::test_resume_respects_latest_review`: 이전 manual2를 cache한 뒤 write 직전 취소→제외1/새 manual1→resume→복원. 수정 전 translated2 assertion 실패, 수정 후 translated1/request0/새 sample/파일1/제외 region byte-identical PASS. 생략한 옛 클라이언트와 명시적으로 비운 새 클라이언트도 구분한다.
5. 최신 sidecar 및 unsigned Eval app **59.17 MiB** 재빌드 후 실제 앱에서 재검증: 이전 manual3 checkpoint, Review에서 Keep original/Shop 제외, Welcome traveler→`여행자님, 환영합니다`, Resume. Result translated1/changed files1/API0/새 sample만 표시. 실제 변경은 `region/r.0.0.mca` 1개뿐이었다.
6. 실제 Backups→Restore: translation `20260930T160201Z-b2f254208bb5-translation`, recovery `20260930T160308Z-6e1f41a56c93-recovery`, 각1파일. 복원 후 원본 대상4파일 **hash differences0**.

## 최신 검사

| 검사 | 결과 | 근거 범위 |
| --- | --- | --- |
| pnpm check / production build | PASS, 0 errors/0 warnings | 최신 UI 및 dialog 수정 |
| frontend | 9 files / 48 PASS | utility/state/settings/virtualization |
| browser | 64 PASS / 56.7초 | 동일 제품 UI synthetic fixture |
| Python | 17 suites PASS | 최신 resume 수정 포함, ci.yml에 나열된 전체 suite |
| Rust | 23 PASS | vault/transaction/provider/export/data root/zoom 코드 |
| sidecar / Tauri debug app | PASS | 최신 resume fix 패키지, macOS arm64 |
| native | mock workflow/cancel/restore, credential transition/restart, literal chooser, 실제200%, 최신 검토 resume PASS | 실제 provider 호출과 구분 |
| 실제 API | NOT RUN, 추가 비용 $0 | real key 미등록 |

Python 전체 재실행 첫 시도는 sandbox의 localhost bind 금지로 release fixture에서 PermissionError가 났다. 네트워크 샌드박스 밖에서 합성 localhost responder로 동일17 suite를 재실행했고 모두 통과했다. 유료 provider를 호출하지 않았다.

대표14 screenshot 직접 inspection 및 browser viewport: 1440×900,1180×800,1024×768,840×620,320px, ultrawide/세로형/짧은 높이/연속 resize/dark/keyboard. 100k fixture는 bounded DOM/page cache와 paging/filter count를 확인했으며 실제100k 월드 처리 성능은 별도다. 과거 테스트 상세는 [9월30일 검증](phase2-validation-2026-09-30.md)을 따른다.

## 재현 환경과 명령

- 월드: `/private/tmp/pomi-eval/resume-20260930/Native workflow world`
- 원본 대상4파일 snapshot: `/private/tmp/pomi-eval/resume-20260930/before.json`
- app identifier: `app.pomitranslate.eval20260930r1`
- native app data: `~/Library/Application Support/app.pomitranslate.eval20260930r1`; Python root는 그 아래 `core`. Rust는 명시적 `--data-dir`로 전달한다. Production 앱 데이터는 사용하지 않는다.
- Eval config: `/private/tmp/pomi-eval/resume-20260930/tauri-eval.json`, beforeBuildCommand는 빈 값(앞서 production build 완료).
- 앱: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app`
- 테스트 script/artifacts/DB/key/world/build outputs는 Git에 추가하지 않는다.

```bash
pnpm check
pnpm test:frontend
pnpm test:browser
pnpm build
# Python 전체 목록: .github/workflows/ci.yml의 17개 명령, .venv/bin/python으로 실행
pnpm sidecar:build
pnpm tauri build --debug --bundles app --config /private/tmp/pomi-eval/resume-20260930/tauri-eval.json
```

native 입력·화면은 CUA만 사용했다. 이전 cold launch 한 번은 blank가 지속됐고 종료/재빌드 뒤 준비 상태를 확인했다. 최신 앱은 정상 Cmd+Q 종료(isRunning=false)→cold launch→Loading→Ready 및 최근 월드 경로 유지까지 재검증했다. 정확한 startup 성능과 원래 blank 원인은 미확정이며, 이 검사를 모든 플랫폼 startup gate로 확대하지 않는다. 현재 Eval은 Settings를 열어 실제 키 직접 등록을 기다린다.

## 완료 전 남은 사항

1. 사용자가 실제 OpenRouter provider/model/key를 **Eval 앱에서 직접 입력하고 로컬 저장**해야 한다. computer-use skill의 새 credential 입력·제출 handoff 규칙 때문에 agent가 대신 입력하지 않는다. 채팅/파일/로그로 키를 보내지 않는다. 이전 OS keychain을 자동 읽거나 가져오지 않는다.
2. 등록 뒤 mock 없이 공식 endpoint/usage 전후를 확인하고 소량 합성 텍스트로 최종 실제 API E2E, 사용량/비용, 백업·복원 해시 비교. 허용 추가 총≤$1, 목표$0.01–$0.10. 현재 추가비용$0.
3. [Legacy parity](../legacy-ui-parity.md): external ZIP/folder/merge 및 app-managed backup/checkpoint 계약 잔여. 현재 in-world pack/항상 안전 백업만으로 전체 parity 완료라고 하지 않는다. 외부 scope 확장과 Phase2 gate 경계에 대한 질문은 답변 미수신이며 축소 승인으로 간주하지 않는다.
4. startup 안정성, 최종 docs/diff/secret-artifact review→Phase2 완료 commit→push. 그 뒤에만 [Phase3 전체 backlog](../follow-up-work.md)를 구현한다.
5. Windows/Linux clean-machine, signing/notarization/updater/cross-platform installer는 NOT RUN. 현재 artifact는 **unsigned development build**이며 release-ready가 아니다.

CI 정책은 관련 Python main push/PR만 core 실행, installer manual/tag, 수동 기본Linux다. 이번 변경은 CI dispatch하지 않았다. Legacy UI/launcher를 제거하지 않았다.
