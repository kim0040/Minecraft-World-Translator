# Legacy Web UI와 desktop 기능 비교 — 2026-10-01

> **2026-10-01 중단 갱신:** [최신 중단·인계](phase2-pause-2026-10-01.md)가 아래 진행 기록보다 우선한다. 외부 ZIP/사용량 조회 후속 구현과 검증 시점, 재개 순서는 해당 문서를 따른다. [테스트 지연 조사](test-efficiency-audit-2026-10-01.md)도 기록했다. Phase2 미완/Phase3 미시작, commit/push 없음.

대상: `webui/index.html`, `webui/app.js`, `webui_server.py`와 현재 Svelte/Rust/JSONL 경로. **Phase 2 미완**, legacy UI와 launcher는 보존한다. 최신 실행 증거는 [검증·인계](phase2-validation-2026-10-01.md)이다. Source 구현과 browser fixture/native/actual provider 검증을 구분한다.

## 현재 비교

| Legacy 기능 | Desktop 대체와 주요 파일 | 현재 판정 |
| --- | --- | --- |
| 월드 선택/최근 경로 | WorldScreen, app.selectWorld, desktop inspection | native chooser와 합성 world workflow 검증 |
| Provider/Comet/Custom/model/모델 목록/키 | SettingsScreen, desktop_provider, provider_boundary, credentials | Comet 직접 선택 구현; mock 및 vault native 회귀 PASS, 실제 provider/OS keychain gate 남음 |
| 언어/style/brief 개선/system prompt | SettingsScreen, desktop_prompt.py | editable prompt와 명시적 확인 후 helper; browser/Python mock PASS, 실제 유료 helper NOT RUN |
| 종류/Recommended·Story·All preset, 파일/key 규칙 | ScanScopeSettings, settings/desktop_settings | curated preset과 옵션 roundtrip/browser 회귀 PASS |
| persistent source→target replacement | SourceOverrides, desktop_settings | global exact-source override와 candidate별 manual 적용; Python/browser 회귀 PASS |
| scan/review/filter/include/exclude/manual | ReviewScreen, CandidateTable/Detail, candidates state | server paging·virtualization·keyboard·100k bounded fixture; 최신 native resume에도 새 검토 반영 PASS |
| batch/temperature/RPM/TPM/retry/file error 정책 | SettingsScreen, desktop_settings, translator | performance 및 continue-on-file-error/file write retries 구현/회귀 PASS |
| checkpoint/Resume/Cancel | 앱 관리 checkpoint, RunScreen, desktop_entry | native cancel와 최신 검토 resume PASS; legacy checkpoint enable/path는 사용자 노출하지 않음 |
| resource pack/source·target locale/skip target | ResourcePackSettings, resource-pack, desktop_entry | 월드 내부 일반 resources.zip, locale·skip 정책 구현 및 synthetic pack 회귀 PASS |
| 임의 external ZIP | ExternalResourcePacks, desktop_resource_packs, explicit backup whitelist | 구현/Python·browser PASS, 최신 native gate 남음 |
| folder/merge | Legacy ZIP-only와 별개의 Phase3 확장 | 미지원 |
| backup opt-out/suffix/path | 항상 자동 백업, app data 경로, BackupsScreen | 검증/recovery/legacy .pomi-backups restore 개선. 임의 경로·retention·off toggle의 동등 기능은 없음 |
| report path/event/raw JSON | Scan/Result structured summary, native JSON report export | native export 검증, 저장 위치 직접 선택. persistent report path/raw timeline은 다른 UX로 대체 |
| translate.py 상속/경로 | settings.import_legacy, desktop_legacy_import | 선택한 Python을 실행하지 않고 literal AST 읽기 전용 preview→draft→명시적 Save. native chooser/discard PASS. 동적 Python 상속은 미지원 |
| settings export/reset/import | public schema JSON, SettingsScreen/settings-import | 공개 allowlist만 export; preview/import/reset draft/save 및 validation/busy 회귀 PASS |
| locale/theme/contact/About | ko/en/ja, System/Light/Dark, AboutScreen | browser 화면/keyboard/dark 확인, contact mailto 구현. 중국어는 기존 지원 언어에 없음 |

## 남은 계약과 실제 gate

- Legacy 임의 ZIP은 Phase2 parity로 구현했다. folder/merge는 Legacy 기능이 아니므로 Phase3 확장에 남긴다. 최신 ZIP native gate와 app-managed backup/checkpoint 대체 차이를 확인하기 전 parity 완료 선언/legacy 제거를 하지 않는다.
- backup/checkpoint 항상 켜짐은 안전 원칙에 맞지만, 사용자가 제어하던 경로/토글을 코드 없이 parity로 표기할 수 없다. 임의 외부 입력은 안전 preflight로 쓰기 전에 실패한다.
- report export와 literal import는 실제 구현된 대체 경로다. report path/동적 Python 실행이 그대로 존재한다고 주장하지 않는다.
- credential Local delete는 앱의 암호문/Session을 제거한다. 명시적으로 가져온 OS 원본은 자동 삭제하지 않는 계약이다. OS 저장 모드의 삭제/권한 UI는 실제 OS gate가 남아 있다.
- 실제 provider 최종 gate와 startup 안정성/최종 diff review가 남아 있다. 기능별 mock 성공은 실제 provider 성공을 뜻하지 않는다.

Phase2 검증→문서/review→commit→push 뒤 Phase3을 진행한다. 외부 scope가 어느 Phase에서 끝나든 안전성·백업·복원·실제 검증 없이 supported로 올리지 않는다.
