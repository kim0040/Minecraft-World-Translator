# Phase 2 재개·검증 — 2026-10-01

이 기록은 [이전 중단 기록](phase2-pause-2026-10-01.md) 이후의 최신 상태다. 사용자 요청으로 재개했다. **Phase2 진행 중 / Phase3 미시작 / release-ready 아님.** 시작 HEAD는 `main` / `9817d54` checkpoint이며, 이번 수정은 미커밋이다. Phase 완료 commit/push는 하지 않았다.

## 최신 후속 상태

최신 소스·패키지·추론 UI/UX 검증과 남은 경계는 [설정·추론 UI/UX 개선](settings-ux-2026-10-01.md)을 따른다. 사용자가 직접 key/model 등록을 완료했고, 모델은 `deepseek/deepseek-v4.1-flash`다. 최신 관련 검사 frontend28 / browser30(29+1) / Rust24 PASS, Python provider 두 파일 PASS, build 0 errors/0 warnings, native 저장·재시작·기본값 복원 PASS. 전체 matrix는 UX 이후 재실행하지 않았다.

이하의 검사 수·hash·gpt-4o-mini 입력 대기는 **이전 재개 시점의 이력**이며 현재 상태가 아니다.

## 이전 재개 수정과 확인

- 검증 executor의 Rust fingerprint에 `src-tauri/build.rs`, root `.cargo/config(.toml)`, `rust-toolchain(.toml)`을 포함했다. 누락되던 build script 변경이 PASS를 무효화한다.
- 임시 합성 runner 18개 확인 PASS: 계획은 실행 없음, 최초 실행, PASS 재사용, source/command/toolchain/24시간 만료/force 무효화, 실패 비재사용, 실행 중 source 변경 거부, 동시 lock, SIGTERM143/lock 정리/RUNNING 비재사용, 소유 descendant 종료 및 무관한 프로세스 보존, Rust 초기 실행/build script 무효화. macOS 실행 증거이며 다른 OS의 process group 동작 검증은 아니다.
- result success/failure·대표 empty·1440px Settings 4개 targeted browser PASS(21.2초). 매핑된 4쌍 PNG가 동일 SHA-256이며 이번 실행의 PNG 복사다. 이후 전체 browser gate도 통과했다.
- 실제 외부 ZIP workflow에서 region/entity 3개와 ZIP 1개가 변경됐지만 Result에는 3개로 표시됐다. `refresh_report_counts`에 physical ZIP 수를 더했다. 같은 ZIP의 여러 language entry는 파일 1개로 센다. scan candidate file count도 동일 기준이다.
- external desktop 회귀에 동일 ZIP의 두 namespace를 넣어 candidate files2/changed files2(region1+ZIP1), 두 locale 출력 및 restore를 검사했다. targeted desktop workflow 및 resource-pack preflight 13개 PASS.

## 이전 재개 검사 — 소스 고정 후 한 번 실행

| 영역 | 결과 | 범위 |
| --- | --- | --- |
| Python | 전체 CI19 suites PASS, 10.41초 | ZIP 집계 수정과 usage/mock/safety/restore 포함 |
| Frontend | 9 files /49 PASS, 2.005초 | 최신 usage UI 포함 |
| Browser | 전체67 PASS, 87.76초 | 최적화된 화면/axe/100k/ZIP/usage fixture |
| Rust | 23 PASS | 최신 provider.usage routing/credential ownership 포함 |
| Check/production UI | 이전 최신 동일 UI PASS 재사용 | 이번 제품 UI source 변경 없음 |
| Sidecar | 최신 ZIP 집계 수정 incremental package PASS | PyInstaller 13.86초; 첫 sandbox 프로세스 지연은 소유 PID 확인 후 종료, sandbox 밖 재실행 |
| Tauri | 최신 unsigned debug Eval bundle PASS, 59.20MiB | macOS arm64; shared Cargo cache 사용, clean-machine 검증 아님 |
| Native | 외부 ZIP 선택→scan→manual run→verified backup→restore PASS | 합성 world/ZIP, provider requests0, 실제 변경4개/표시4개 |
| Actual API | NOT RUN /추가 비용$0 | 사용자 직접 key 입력·저장 대기 |

정확한 runtime cache는 Git 제외 `output/verification/evidence.json`이다. 각 fingerprint:

- frontend: `f06bee6e79fdba166ff6a0a3e29b222c2ed769bdf55693bd466222994764ed6a`
- python-final: `18f327646226c5a555ffa65172216623556dacba0874fa0052024864174d4927`
- browser-final: `35a49f59f6a66b26f33d953db17b15c6eca48235fd5c37069ac410a55fbb0581`

과거 PASS는 cache에 소급 등록하지 않았다. 위 UI/check와 Rust 수동 실행 증거는 별도로 기록한다. 검사 중 source 편집 없음.

## 이전 재개 native 실측

- identifier: `app.pomitranslate.eval20260930r1`. production app data와 격리.
- bundle: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app`
- app executable SHA-256: `931cf2961d9a0bfcf85f158fc39a4b4635d1e96f531d8cdb279404dc7b0b9f97`
- embedded sidecar SHA-256: `58a23336866682c486355063609302c003ddb3d01dd8af37fc8caa4c0f239c37`. prepared sidecar와 일치.
- world: `/private/tmp/pomi-eval/external-20261001/External ZIP workflow world`
- external ZIP: `/private/tmp/pomi-eval/external-20261001/outside-world/selected external pack.zip`
- baseline: `/private/tmp/pomi-eval/external-20261001/before.json`(world4+ZIP1). scan 후 차이0, run 후 차이4, restore 후 차이0.
- 최신 Result: translated4/changed files4/API requests0. ZIP의 `assets/eval/lang/ko_kr.json`에서 기대 직접 번역 확인.
- verified translation backup: `20261001T003240Z-515b9b7f937e-translation`, 4files/external1.
- restore 직전 recovery: `20261001T003331Z-02a15057bcd0-recovery`, 4files/external1. 앱 성공 알림과 대상5파일 byte-identical 복원 확인.
- 앞선59.19MiB bundle에서도 같은 workflow/restore를 확인했고, 최종 gate는 위 집계 수정 후 bundle 결과다.
- 정상 종료→최신 bundle cold launch→Loading→Ready/최근 world 유지를 확인했다. 과거1회 지속 blank는 이번에 재현되지 않았으며, 원인 확정·clean-machine startup 안정성 증거는 아니다.

## startup 잔여 위험 조사

`src/lib/app.svelte.ts::boot`는 bootstrap 오류가 반환되면 finally에서 Ready와 오류 안내로 전환한다. 다만 `src-tauri/src/lib.rs::exchange_sidecar`의 event receive에는 handshake/bootstrap 응답 deadline이 없다. `mwt/desktop_entry.py::_bootstrap_payload`는 최근 world inspection·backup listing·resume 정보를 동기적으로 모은다. 따라서 미응답 sidecar 또는 오래 걸리는 저장소 작업에서 Loading이 지속될 가능성은 남는다. 과거 blank의 프로세스/로그가 보존되지 않아 이 경로를 당시 원인으로 확정하지 않는다.

다음 검증은 startup 전용 무응답/지연 fixture와 cleanup·오류 복구를 재현하는 targeted 검사다. write operation의 장시간 작업에 일괄 timeout을 추가하지 않는다. 현재 native Ready 성공을 과거 blank 수정 완료라고 기록하지 않는다.

## 이전 사용자 인계

Eval Settings에 OpenRouter / `openai/gpt-4o-mini`, global manual override `{}` **미저장 draft**를 준비했다. 새 API 키는 사용자가 앱에서 직접 입력하고 저장해야 한다. computer-use의 새 credential 입력/확인/제출은 사용자 handoff 규칙을 따른다. 키를 채팅/평문파일/로그로 받지 않는다. 기존 keychain 자동 접근 없음.

저장 후 순서: Settings의 공식 누적 usage GET→합성4문 scan/review/preflight→최소 실제 API run→Result의 requests/tokens/실제 cost와 usage 재조회→verified backup/restore→baseline5 hash 차이0. 기존 허용 추가 총액≤$1, 목표$0.01–$0.10. 키가 없는 상태로 유료 호출을 시작하지 않았다. 누적 usage 차이에 다른 작업/집계 지연이 섞일 수 있다.

## 남은 판정

1. actual provider/usage/cost/restore.
2. legacy backup off/suffix/path, checkpoint off/path의 app-managed 항상 안전 보관과의 차이. 차이를 검증된 parity라고 하지 않으며 legacy UI/launcher를 유지한다. folder/merge는 Phase3 확장.
3. 과거 blank 원인·clean-machine startup, OS keychain opt-in 실제 OS 검증, Windows/Linux installer·signing/notarization/updater는 미검증.
4. 현재 docs link/diff/secret-pattern/artifact 검토 PASS. 사용자 등록·최종 API 결과 반영 후 검토를 갱신하고, 전체 Phase2 gate를 충족했을 때만 Phase2 완료 commit/push. 이후 Phase3.

생성물/world/DB/key/cache/bundle은 Git 제외. 변경 파일의 credential/private-key 패턴 검사 검출0, `git diff --check` PASS. 공개 release/서명/사용자 world upload 없음. 전체 gate의 유효 PASS를 재사용하며 키 대기나 docs 갱신을 이유로 같은 검사를 반복하지 않는다.
