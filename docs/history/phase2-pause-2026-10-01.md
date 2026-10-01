# PomiTranslate 중단·인계 — 2026-10-01 02:11 KST

> **재개 이후 최신 상태:** [2026-10-01 재개·검증](phase2-resume-2026-10-01.md). 아래 중단/검사 시점 기록은 이력이며 새 실행 결과는 재개 기록을 따른다.

> **최신 결정 — 검증 최적화 후 중간 저장/중단:** 사용자 요청으로 실행 정책·명령을 반영하고 현재 WIP를 checkpoint commit/push한다. Phase2 완료 commit이 아니며 Phase3 미시작이다. [검증 실행 정책](../verification-policy.md)과 아래 최적화 후속 기록을 우선한다. 테스트·개발 서버·Eval 앱은 종료됐으며 내일 재개 전 새 검사/빌드를 실행하지 않는다.

사용자 요청: **하던 것까지만 정리 후 중단하고, 작업 지연과 테스트 과잉 여부를 조사해 브리핑**. 추가 기능, 새 전체 회귀, Tauri 재빌드/실행, 유료 호출을 시작하지 않았다. 이 문서가 앞선 진행 기록과 충돌할 때 우선한다.


## 검증 최적화 후속 — 사용자 추가 요청

- 일반 중간 저장을 명시 승인받아 기존 Phase2 WIP와 이번 optimization/policy를 함께 checkpoint commit/push한다. Phase2 미완, Phase3 미시작. 이 snapshot 이전 HEAD865b51d; 저장 hash는 `git log -1`로 확인한다.
- `scripts/verify.mjs`, plan/ui/final 명령, exact source/command/toolchain 및24시간 PASS reuse, RUNNING/실패/중단 비재사용, 실행 중 소스 변경 감지, concurrent lock과 자신이 시작한 group만 cancel을 구현했다.
- 기존 증거는 새 cache에 소급 등록하지 않았다. 이번에는 **node --check 2 scripts + plan-only 출력 + docs link/diff 검토**만 수행했다. 실제 테스트·앱 빌드는 재실행하지 않았다.
- 기본 sidecar에서 --clean을 opt-in으로 변경했다. explicit clean/최종 desktop build는 유지한다. UI-only native dev 명령을 분리했다.
- result-failed 두 번 boot/run을 하나로 통합하고 assertions/axe/PNG는 유지했다. 기존 numbered/generic screenshot 두 번 캡처를 이번 run PNG 복사로 바꿨다. 최적화 후 현재 전체 browser case67의 runtime는 아직 NOT RUN이며 이전67PASS와 같은 source라고 주장하지 않는다.
- tracking 되는 제품 `AGENTS.md` 및 verification-policy를 새로 추가했고 상위 AGENTS.md·root plan/current state도 연결했다. DB/key/env/backup/evidence ignore를 강화했다. 실제 secrets/world/artifacts는 staging하지 않는다.
- Eval 앱을 CUA Cmd+Q로 종료한 뒤 PID88558 소멸을 확인했다. localhost5173/5197/5198 listener 없음, test/build runner 없음. 공용 Playwright MCP는 보존했다. 기존 문서의 Settings handoff가 열려 있다는 문구는 이 시점 이후 유효하지 않다.

### 내일 잔여 — 최적화 도구 먼저, 영향 검사만

1. 새 executor의 cache reuse/invalidation/실패·취소·lock을 합성 작은 runner로 targeted 확인. 현재 syntax/plan PASS이지 실행 동작 완료 검증이 아님.
2. screenshot 통합/result-failed 관련 browser case만 targeted 확인. 이 작업 때문에 전체Python/Rust/100k를 재실행하지 않는다.
3. 이후 원래 남은 latest provider.usage Rust routing/외부ZIP native/APIusage-cost-restore/startup/legacy parity/최종 gate를 이어간다. 기존Phase3 backlog는 전부 remaining-work에 보존한다.
4. 동일소스의 유효PASS는재사용하며, 변경된레이어만무효화한다. Phase2검증완료→완료commit/push후에만Phase3.

## Git 및 안전

- 제품 저장소 `reference/Minecraft-World-Translator`, 실제 branch `main`, HEAD `865b51d`.
- 기존/이번 modified·untracked WIP 모두 보존. reset/clean/restore/stage/commit/push 없음. `git diff --check` PASS.
- **Phase 2 미완, Phase 3 미시작**. 이전 committed UI를 Phase 완료로 소급하지 않는다.
- 원본 sample 미변경. 모든 write 테스트는 합성/임시 복사본. 추가 실제 API 사용 $0.
- 마지막 실행 중이던 sidecar packaging은 정상 종료(약22초)했고 새 테스트/빌드 프로세스는 남아 있지 않다. 기존 Eval 앱은 idle CPU 0.0% 관측, Settings 상태로 유지했다. 공용 Playwright MCP 프로세스는 테스트 runner가 아니며 종료하지 않았다.

## 이번에 구현한 것

1. 기존 UI·vault·native 검증과 resume/dialog 수정은 [상세 실행 기록](phase2-validation-2026-10-01.md)을 따른다. 특히 native resume이 새 exclude/manual을 무시하던 결함은 수정 후 translated1/request0/changed1과 원본4파일 byte-identical restore로 재검증했다.
2. **명시적으로 선택한 외부 ZIP**을 Settings→Scan→Review→Run→Backup/Restore에 연결했다. Legacy가 받던 임의 ZIP은 Phase2 parity다. 폴더형 팩과 merge는 Phase3 확장이며 아직 미지원이다.
3. 외부 ZIP 설정은 절대 경로·ZIP·최대16개를 검증한다. raw 경로는 private preferences에만 저장하고 public export/import에는 싣지 않는다. 저장/선택 변경은 scan을 invalidation한다. 긴 경로의 1440/840/320px browser 검증 및 1440/320 screenshot 직접 inspection을 수행했다.
4. 외부 ZIP은 선택 whitelist와 parent identity, scan 당시 streaming SHA-256으로 검증한다. 변경 중/scan 이후/쓰기 직전 달라지면 invalidated 처리한다. Scan 도중 변경은 plan을 만들지 않고 저장 report도 invalidated로 수정했다.
5. backup manifest v2는 외부 ZIP canonical 대상/parent identity/별도 archive alias를 저장한다. 기존 world-only/legacy backup 호환 유지. Manifest 자체가 임의 외부 쓰기 권한을 부여하지 않는다. Restore는 필요한 대상만 현재 설정의 선택과 교차 검증하고, unselected/missing/symlink/parent-changed 대상이면 recovery 및 쓰기 전에 거부한다. recovery snapshot도 외부 ZIP을 포함한다.
6. OpenRouter **읽기 전용 누적 사용 크레딧 조회**를 추가했다. `provider.usage`는 Rust 저장소에서 키를 주입하고 고정 공식 `/api/v1/key`만 GET, redirect 거부·20초 timeout·64KiB 응답 제한·finite/nonnegative numeric allowlist를 적용한다. key label/hash/account ID/raw response/error/키 자체는 UI에 반환하지 않는다. 새 key draft가 있으면 버튼 비활성, 조회는 draft를 저장하거나 번역하지 않는다. 전후 차이에 다른 작업/집계 지연이 섞일 수 있다는 안내를 표시한다. **실제 authenticated 조회는 NOT RUN**.

## 검증 — 시점과 범위를 구분

| 항목 | 마지막 증거 | 이후 변경/미검증 경계 |
| --- | --- | --- |
| Python 전체 | CI 목록의 18 suites PASS | 이후 usage8 unit PASS, scan 도중 외부 ZIP 변경/저장 report invalidation targeted PASS. 현재 CI19 suites 전체 재실행은 NOT RUN |
| Frontend unit | 9 files /49 PASS | usage UI 추가 후 전체 unit 재실행 NOT RUN; check/build와 관련 browser로 검사 |
| Browser 전체 | 67 PASS /3.5분 | 이후 usage1 + 외부ZIP3 targeted=4 PASS /7.5초. 현재68 전체를 한 실행으로 확인하지 않음 |
| Check/build | 0 errors/0 warnings, Vite production build PASS | usage UI/i18n 포함. 첫 i18n 삽입 실수를 발견해 수정 후 PASS |
| Usage unit | 8 PASS /0.008초 | 처음7/8에서 resolver 예외 타입 실패→generic UsageUnavailable 수정→8/8 PASS. 모든 HTTP mocked |
| External core | preflight/backup/translate 13 tests 및 desktop workflow PASS | 합성 manual/mock provider, 미선택 복원 거부·다중 ZIP·쓰기 전 변경 차단·byte-identical restore/recovery |
| Rust | 이전23 PASS | `provider.usage` allowlist/ownership/injection 추가 뒤 Rust 재실행 NOT RUN |
| Sidecar | 최신 외부 ZIP/usage/scan report 코드를 포함한 packaging PASS | PyInstaller 약22초; frontend/백엔드와 별개 native 실행 gate 필요 |
| Tauri/native | 이전59.17MiB Eval build, native mock/cancel/restore/resume/200%/cold restart PASS | 최신 외부ZIP/usage/scan report 코드의 Tauri 재빌드·native E2E는 NOT RUN |
| 실제 API | NOT RUN /추가비용$0 | 실제 OpenRouter key 미등록, usage 전후·실제 cost·최종 API E2E 남음 |

위 표의 개수는 서로 다른 레이어/시점이다. Python suite18은 개별 assertion18이라는 뜻이 아니며, 전체67과 targeted4를 합쳐71개 독립 테스트라고 세지 않는다.

## 재개 시 다음 순서

1. 이 기록/AGENTS/구현 계획을 읽고 git 상태와 diff 확인. 기존 WIP를 삭제하지 않는다.
2. [테스트 지연 조사](test-efficiency-audit-2026-10-01.md)와 개정 [웹 우선 계획](../browser-first-testing-plan.md)을 적용한다. 소스를 먼저 안정화하고 **변경 관련 검사만** 실행한다. 이전 PASS 증거를 날짜/소스 범위와 함께 재사용한다.
3. 최신 `provider.usage` Rust routing 검증 및 영향받은 backend 계약을 확인한다. 정확한 기준점이 필요할 때 소스 고정 후 마지막 full gate를 한 번 수행한다. 테스트 실행 중 소스를 수정하지 않는다.
4. Eval 앱을 정상 종료한 뒤 최신 frontend/sidecar를 Tauri에 묶는다. UI-only 수정이면 sidecar 재패키징하지 않는다. 외부 ZIP native select→scan→manual run(API0)→backup/restore→5 target hashes difference0을 확인한다.
5. Native 시험 준비 경로: `/private/tmp/pomi-eval/external-20261001/External ZIP workflow world`, external ZIP `/private/tmp/pomi-eval/external-20261001/outside-world/selected external pack.zip`, baseline `/private/tmp/pomi-eval/external-20261001/before.json`(world4+ZIP1). 아직 native write하지 않았다.
6. 기존 Eval identifier `app.pomitranslate.eval20260930r1`, app data `~/Library/Application Support/app.pomitranslate.eval20260930r1`, core root `core`. 기존 production 앱 데이터는 건드리지 않는다. 새 bundle 빌드 시 실행 앱을 먼저 종료한다.
7. 실제 API gate는 사용자가 Eval Settings에서 OpenRouter/model/새 키 입력·로컬 저장을 직접 완료해야 한다. computer-use skill credential handoff 규칙 때문이며 키를 채팅/로그/평문파일로 받지 않는다. 이전 keychain 자동 읽기 없음. 기존 예산 추가 총≤$1, 목표$0.01–$0.10. 현재 등록 미완이므로 비용/실제 provider 성공을 주장하지 않는다.
8. Legacy arbitrary ZIP native parity와 app-managed backup/checkpoint 대체 범위, startup 안정성, docs/diff/artifact/secret review를 마무리한다. 항상 안전 백업 정책과 legacy off/suffix/path 토글 차이를 숨기지 않는다. **legacy UI/launcher는 보존한다.**
9. Phase2 모든 gate 후 문서/review→commit→push. 그 뒤에만 [Phase3 전체 backlog](../follow-up-work.md) 구현. Windows/Linux clean-machine/signing/updater/release도 아직 미완이다.

## 마지막 빌드의 주의점

소스가 안정화되기 전에 첫 sidecar packaging(약56초)을 시작했고, usage 예외·scan report 오류를 수정한 뒤 다시 packaging(약22초)했다. 이는 개발 순서의 비효율이며 이후에는 affected tests→소스 고정→필요 시 packaging 한 번을 따른다. 최신 sidecar PASS를 기존 실행 중인 Eval 앱의 최신 소스 성공으로 해석하지 않는다.
