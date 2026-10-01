# Phase2 완료 검증 — 2026-10-01

## 판정

**Phase2 데스크톱 기능·macOS arm64 개발 환경 gate 완료 / Phase3 미시작 / release-ready 아님.** 시작 HEAD는 `main` / `2d32ebe`이며 기존 샘플·startup WIP를 보존했다. 검증→문서·diff 검토→완료 commit→push 순서를 따른다. 실제 Git SHA와 원격 상태는 Git 기록을 기준으로 한다. 서명 배포·모든 플랫폼·모든 Minecraft 버전 완료를 뜻하지 않는다.

이 기록이 [샘플·시작 복구 기록](sample-startup-validation-2026-10-01.md)의 최종 계약 결정 대기·미커밋 상태를 대체한다. 그 기록의 샘플 provenance·과거 패키지 hash·실제 provider 비용은 당시 증거로 보존한다.

## Legacy 대체 범위

사용자의 계속 진행 요청에 따라 기존 구현과 안전 계약을 유지하는 기술 선택으로 정리했다. 새 옵션에 대한 별도 사용자 답변을 받았다고 주장하지 않는다.

- Desktop은 항상 검증된 자동 백업을 만들고 backup/checkpoint 저장 위치를 앱이 관리한다. Legacy의 off/suffix/임의 경로와 동등한 UI는 제공하지 않는다.
- Cancel/Resume, app data 백업, legacy `.pomi-backups` 발견·복원은 유지한다. 기존 데이터를 자동 이동·삭제하지 않는다.
- literal Python import는 BASE_URL/MODEL/SYSTEM_PROMPT 등 허용된 공개 설정의 읽기 전용 preview→draft→Save이며 백업·checkpoint·월드 경로·키는 import하지 않는다.
- 기존 경로·토글이 필요한 사용자는 CLI/Legacy를 사용할 수 있다. Legacy UI/launcher는 유지한다. 기능 비교는 [대체 범위 표](../legacy-ui-parity.md)를 따른다. 문자 그대로의 100% parity나 Legacy cleanup 완료로 표시하지 않는다.

## 최종 검사에서 수정한 결함

1. SourceOverrides의 오류가 해소되면 `<details open={invalid}>`가 입력창을 닫았다. 독립 expanded 상태로 사용자가 열어 둔 입력창을 유지하고 오류 시 펼친다. 기존 browser의 “저장된 값과 같은 빈 override도 Save enabled” 기대를 변경하고, 실제 새 번역문 입력의 저장 가능 여부를 확인했다.
2. 내부 청크가 번역 후 255-sector 한계를 넘어 처음 `.mcc`가 생기면 기존 백업은 원래 파일의 부재를 기록하지 않았다. 복원 후 orphan `.mcc`가 남아 원본 지문과 달라졌다. 새 파일 부재를 manifest에 기록하고 복원 직전 현재 `.mcc`를 recovery에 보존한 뒤 원본 header 복원→새 파일 제거 순으로 되돌린다.
3. `.mcc` payload를 먼저 atomic write하고 `.mca` header를 마지막에 기록한다. 각 성공 write를 즉시 표시해 중간 실패 뒤 복원이 가능하다. recovery 복원도 `.mcc`→`.mca` 순이다. 실제 프로세스 kill 전체 복구 UX는 Phase3에 남긴다.
4. 변경 파일 집계에 물리 `.mcc`를 포함했다. additive `written_files`를 보고서/checkpoint에 기록하고 unique region/.mcc/ZIP 경로를 센다. 기존 checkpoint는 필드가 없으면 region 기준을 유지한다.

새 파일 부재를 포함하는 백업만 schemaVersion3이며 일반 백업은2를 유지한다. 최신 reader는 기존2를 복원한다. 새 marker 백업은 이 버전 이상으로 복원해야 한다. marker는 좌표 `.mcc`·동일 폴더의 정상 region 백업·empty digest/size0에 제한하고 symlink/경로 이탈/알 수 없는 action은 쓰기 전에 거부한다.

## 자동 검사

| 검사 | 결과와 증거 경계 |
| --- | --- |
| Python 최종 | CI에 등록된20 suites PASS, 최종 집계 수정 후12.268초. `node scripts/verify.mjs python-final --run`; fingerprint `33ba674b772bafbbb0be46ec547a3fd3b76fceb65001e8841d2f1d3623163cf1` |
| 신규 external chunk | 255-sector 경계3 / write failure2 / validation4 / recovery roundtrip 및 물리 집계·이전 report fallback PASS. 생성 데이터만 사용, API0 |
| Frontend | 11files/58 PASS — SourceOverrides 수정 후 전체 실행 |
| Type/build | check0 errors/0 warnings, production build PASS |
| Browser 최종 | 전체87 시나리오 실행에서86 PASS/1 FAIL. 위 override 기대와 disclosure 결함 수정 후 영향7 PASS(9.3초). 영향 없는86 결과를 재사용. 한 번의 전체87 PASS 실행이라고 주장하지 않음 |
| Rust | startup4 포함28 PASS 재사용. Rust/dependencies는 이후 변경 없음 |
| Packaging | Python 수정 후 incremental sidecar와 unsigned debug Eval app 갱신 PASS. 최종 PyInstaller13.194초 / Rust14.15초; clean-machine/installer 서명 검증 아님 |

전체 browser에는 layout/locale/dark/axe/virtualization/workflow가 포함된다. latest native gate는 아래 실제 packaged 경로로 확인했다. Git 제외 cache는 `output/verification/evidence.json`이며 FAIL 기록을 수동 PASS로 바꾸지 않았다.

## 최종 native `.mcc` gate

- Eval identifier `app.pomitranslate.eval20260930r1`; production 데이터·credential은 접근/수정하지 않았다. 기존 Eval provider/model/reasoning/팩 설정을 유지했고 recent world만 변경했다.
- 합성 `/private/tmp/pomi-eval/final-mcc-20261001/world`: level.dat + region2파일. 유효 NBT Byte_Array로 uncompressed 청크를 내부 한계32bytes 아래에 배치했다. 원본 region1,052,672bytes이며 최초 `.mcc` 없음.
- 기존 명시 선택 외부ZIP 후보는 제외했다. Hello sign에 `대형 청크 검증 `과 `검증`50회만 수동 입력했다. 사전 점검의 전송0/직접1/예상 요청0, 결과 completed/변경2/API0를 실제 UI에서 확인했다.
- 저장된 region을 다시 읽고 NBT 재파싱·번역문·external flag와 payload를 확인했다. level.dat는 그대로, 이전 합성 world4+ZIP1도 baseline hash 차이0이다.
- 자동 백업 `20261001T061350Z-93813be1f053-translation`의 schema3·region 복사본·new `.mcc` 부재 marker 확인. native 복원 후 recovery `20261001T061453Z-a4f121258d99-recovery`와 Ready를 확인했다. 최종 원래2파일 hash 차이0 / 새 `.mcc` 없음.
- 앞선 집계 수정 전 native도 write/reopen/restore PASS였지만 결과 표시1은 결함이었다. 수정 후 위 최종 native로 변경2를 확인했다. 검사 helper의 잘못된 메서드 호출1회는 실패로 구분하고 실제 payload assertion을 수정해 재확인했다.
- 최종 정상 종료 후 소유 Pomi app/sidecar 잔여 프로세스0, cancel 파일0. raw report/해시/복원 요약은 Git 제외 `output/startup-native-20261001/final-mcc/`다.

최종 bundle: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app` (59.21 MiB).

- Executable SHA-256: `476052d71076ed8f0a5942180b366028c88561973dbcf61fdb6ad70e043ccd70`.
- Embedded sidecar SHA-256: `6fcae7b4d1b303e180dda5edca73f7c6b34479ab12b4aa2d92f871fd655d9ad4`; prepared와 동일.

## 재사용한 샘플·실제 provider 증거

[이전 상세 기록](sample-startup-validation-2026-10-01.md)의 공개5 region+Roguefire 복사본9435청크 읽기·원문 NBT byte-identical, Roguefire12후보 write/reopen/117파일 restore와 원본 hash 차이0를 재사용한다. 공개5는 후보0으로 쓰기 검증 아님. 원본과 다운로드는 Git/배포물에 포함하지 않는다.

실제 OpenRouter 합성3문장/1요청, 입력391/출력108, provider-reported $0.0001484, world4+ZIP1 native restore를 재사용한다. 이번 최종 `.mcc` gate는 API0/추가 비용0이며 유료 요청을 반복하지 않았다. 단일 요청을 모든 제공사·번역 품질·최종 청구서 검증으로 확대하지 않는다.

## 남은 작업

최종32개 변경·신규 파일의 `git diff --check` PASS, Markdown 로컬 링크 누락0, credential/private-key 패턴 검출0, Git 변경 목록의 world/DB/key/ZIP/app 등 runtime 생성물0을 확인했다. 패턴 검사는 완전한 비밀 검출 보장이 아니다. 공개5 원본 SHA-256·mode0444·Git 제외를 다시 확인했다. 완료 저장 전 원격 main은 시작 HEAD `2d32ebe`와 같았다. 이 변경은 CI의 core 자동 검사 대상이며 installer/release dispatch는 하지 않는다.

Phase3의 우선순위는 [호환성 계획](../compatibility-roadmap-2026-10-01.md)의 SNBT command→최신 component→청크별 DataVersion/coverage다. 신규 `.mcc` 합성 경계와 실패 복원은 완료했으나 실제 LZ4/대형 외부 청크 게임 월드, 1.20.5/1.21.5/26.x의 텍스트 포함 실제 생성 샘플과 게임 로드는 미검증이다. 모든 버전 지원을 선언하지 않는다.

clean-machine/다른 OS/keychain opt-in/native permission, signing/notarization/updater, target별 binary license/NOTICE는 [잔여 gate](../follow-up-work.md)에 남긴다. 공개 release·원본 world 쓰기·사용자 world 업로드는 수행하지 않았다.
