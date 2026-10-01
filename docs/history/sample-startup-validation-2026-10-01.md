# 실제 샘플·시작 복구·최소 provider 검증 — 2026-10-01

## 판정과 변경 범위

사용자 요청에 따라 공개 샘플을 내려받아 복사본으로 검사하고, Phase2 시작 복구를 구현했다. 시작 HEAD는 `main` / `2d32ebe`, 기존 호환성 계획 WIP를 보존했다. 이 기록의 변경은 미커밋이다. **Phase2 진행 중 / Phase3 미시작 / release-ready 아님.**

이번에 확인한 것은 샘플의 읽기·바이트 보존, 실제 월드 복사본의 결정적 쓰기·복원, macOS arm64 개발 앱의 시작 실패 복구와 OpenRouter 최소 E2E다. 특정 Java 버전 전체의 지원, 게임 내 표시·동작, 번역 품질 전체를 검증한 결과는 아니다.

## 공개 샘플 출처와 보존

[VilleOlof/mca의 고정 data 디렉터리](https://github.com/VilleOlof/mca/tree/b8454dd93355c211d2343e3bb87f80ff62f5a73d/data)에서 `.mca` 다섯 개를 받았다. Commit은 `b8454dd93355c211d2343e3bb87f80ff62f5a73d`, 총 34,934,784 bytes다. 저장 위치는 Git 제외 `output/compatibility-samples/upstream/`, 원본 mode는 0444다. 획득 시점의 출처·크기·해시는 `manifest.json`과 `manifest-addendum-nearby-versions.json`에 보존했다.

저장소 라이선스는 MIT지만 개별 binary fixture의 별도 고지는 확인하지 못했다. 로컬 검사에만 사용하며 저장소·배포물에 동봉하지 않는다. 파일명은 upstream의 버전 표기다. `level.dat` 없는 단일 region이므로 완전한 게임 save나 공식 버전 생성 증거로 취급하지 않는다.

| Upstream 파일명 | 관측 DataVersion | 청크 | 원본 SHA-256 |
| --- | --- | --- | --- |
| 1.2.1.mca | 없음 / unknown | 1,024 | `c9897904eca3a6440f8fe28b1a4183b6ddf46064b355fbe89d6536ffc150aeb2` |
| 1.12.2.mca | 1343 | 1,024 | `921187fda51c65a4b97a6b5b36839c18134e21a9a30a78f715ab17f87d6e3ca7` |
| 1.19.mca | 3105 | 1,024 | `d16662ea237e9219fb11cbda1279c8e91b20a75c264ed070ef97c606a5134022` |
| 1.20.2.mca | 3578 | 1,024 | `0bd43148d3bcce5442047cfe9f86edcee2a96f44cfb29fc88eb9282aff9d8223` |
| 1.21.11.mca | 4671 | 1,024 | `fcc4ced13a8c27fffa8a6f0547c8dfb6621ff56c18eb79e38ff78c88c6d36941` |

총5,120 청크에서 zlib(2), NBT parse→원문 그대로 dump의 byte-identical, Scan Only 완료·API 요청0·원본 hash 차이0을 확인했다. 고유 후보는 각0개다. 따라서 **쓰기·복원은 NOT_APPLICABLE_NO_CANDIDATES**이며 후보0을 모든 표시 텍스트가 없다는 의미로 해석하지 않는다. 보고서는 `output/compatibility-samples/run-20261001-a/sample-00`부터 `sample-04`에 있다.

정확한 1.20.5/1.21.5 샘플은 고정 upstream 디렉터리에 없었다. 인접 버전의 파일로 해당 경계 버전 검증을 대신하지 않는다. 26.x, 최신 SNBT command, LZ4 실월드, 신규 `.mcc` 생성 경계와 실제 게임 로드는 남아 있다.

## 실제 월드 복사본의 쓰기·복원

기존 `sample/[1.21.10] Roguefire v1.1` 원본 117파일 / 23,003,499 bytes를 별도 `output/` world로 복사했다. 원본에는 쓰지 않았다.

| 항목 | 결과 |
| --- | --- |
| 읽은 청크 / 원문 NBT byte-identical | 4,315 / 4,315 |
| DataVersion 분포 | 4556: 3,635 / 4440: 680 — 실제 혼합 버전 |
| 압축 | 전부 zlib(2) |
| 스캔 | completed, 고유 후보477 / 발생 위치6,308, API0·파일 변경0 |
| 결정적 쓰기 | 후보12개에 `검증 ` 접두사를 적용, 나머지 exact-source 원문 유지 override; provider 호출 시 즉시 오류로 막음 |
| 실제 변경 / reopen | 2파일 변경, 재파싱 후 선택한 번역12개 수집·DataVersion 분포 동일 |
| 백업 / 복원 | `20261001T051749Z-4f925ece7850-translation`, 전체 baseline hash 차이0 |
| 원본 / 게임 로드 | 원본117파일 hash 차이0 / NOT_RUN |

원본의 10개 entities region은 **0-byte 파일**이다. 검사 도구가 header 부족으로 기록했고 코어는 small file로 건너뛰었다. 모두 그대로 보존됐다. 이 파일들을 손상 청크나 성공적으로 파싱한 청크로 세지 않는다. 다른 parser 오류·unsupported 청크는0이었다.

최종 PASS 보고서는 `output/compatibility-samples/roguefire-20261001-c/sample-00/summary.json`이다. 앞선 a의 월드 검사와 b의 reopen assertion은 검사 도구의 empty-header 처리 및 오래된 write fingerprint 때문에 실패했다. 실패 기록을 PASS로 승격하지 않는다. 도구를 수정한 후 해당 월드만 재검사했고, 영향 없는 공개5개의 유효 결과는 재사용했다. 복사본 중 실패 잔여물은 원본·최종 PASS와 구분한다.

### 재현 도구

[`scripts/verify-world-samples.py`](../../scripts/verify-world-samples.py)는 원본/출력 경로 분리, Git 제외 출력, 원본 hash, scan→결정적 write→reopen→restore를 수행한다. 출력 디렉터리는 새 이름을 써야 한다. API·게임 실행은 하지 않는다.

```sh
.venv/bin/python scripts/verify-world-samples.py \
  --sample output/compatibility-samples/upstream/1.12.2.mca \
  --sample output/compatibility-samples/upstream/1.21.11.mca \
  --output output/compatibility-samples/new-region-check

.venv/bin/python scripts/verify-world-samples.py \
  --sample '../../sample/[1.21.10] Roguefire v1.1' \
  --output output/compatibility-samples/new-world-check
```

## Phase2 시작 복구 구현과 증거

- Rust `startup.rs`: 요청 시작 기준 hello30초, `app.bootstrap` 전체60초의 절대 deadline. 반복 hello/event가 제한을 연장하지 않는다. hello 이후 scan/translate/restore 작업에 일괄 timeout을 적용하지 않는다.
- deadline 도달 시 기존 소유 sidecar 종료·cancel 파일 정리 경로를 따른다. 정확한 `CORE_HANDSHAKE_TIMEOUT` / `BOOTSTRAP_TIMEOUT`을 frontend로 전달한다.
- frontend: 시작 오류 안내·다시 시도, 실패 시 navigation 차단, 중복 boot 방지, 지연 event 등록이 bootstrap을 막지 않도록 분리, destroy 후 늦은 listener cleanup. ko/en/ja 오류 문구를 추가했다.

| 검사 | 이번 source 결과 |
| --- | --- |
| `pnpm build` | check 0 errors / 0 warnings, Vite build PASS |
| Frontend | `vitest run tests/frontend`: 11files /58 PASS, 신규 startup4 포함 |
| Browser | `playwright test tests/browser/startup.spec.ts`: 5 PASS — timeout/stopped/retry/delay/stalled listener |
| Rust | `cargo test --offline --manifest-path src-tauri/Cargo.toml --lib`: 28 PASS, 신규 deadline4 포함 |
| Python 영향 검사 | `tests/test_extraction.py`: 10 PASS / `tests/test_desktop_entry.py`: PASS |
| Native | hello 무응답30초·hello 이후 bootstrap 무응답60초 → 각각 한국어 오류·navigation 차단·소유 프로세스 종료 → 실 sidecar 복구 후 재시도 Ready; 마지막 실 app cold start Ready |

네이티브 fault는 Git 제외 `output/startup-native-20261001/handshake.app`, `bootstrap.app`에 최신 앱을 복사해 sidecar만 `sleep120` stub으로 교체했다. 두 앱은 동일 Eval identifier의 격리 데이터만 사용했고 한 번에 하나씩 실행했다. handshake 자식 PID39944, bootstrap 자식 PID41888의 timeout 후 소멸을 `ps`로 확인했다. 각 복사본의 원래 sidecar를 복구한 뒤 재시도 성공을 실제 AX/screenshot으로 확인하고 정상 종료했다. 최종 cancel 파일 없음도 확인했다.

과거 지속 blank의 원인을 이 결과만으로 확정하지 않는다. event 등록 지연·sidecar 무응답의 재현 가능한 회귀를 처리한 것이다. 각 다른 OS·clean-machine·물리 저장 장치 장애는 미검증이다.

샌드박스의 pnpm 정지·Cargo 캐시 접근 제한·mock 로컬 socket PermissionError는 완료 결과와 분리했다. 소유한 정지 pnpm만 확인 후 종료했고, 같은 좁은 명령을 승인된 실행 환경에서 수행했다. 중단/오류 실행을 PASS에 포함하지 않는다. Python 코어·sidecar 소스는 바뀌지 않아 기존 sidecar를 재사용했고 native 앱은 마지막에 1회 만들었다.

### 최신 unsigned Eval 앱

- Identifier: `app.pomitranslate.eval20260930r1`, macOS arm64, 59.21 MiB.
- Bundle: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app`.
- Executable SHA-256: `10518b56c22be47e875d5a0c211a113e785cd6f9f1f77c8205f0fc9ea8ab385e`.
- Embedded sidecar SHA-256: `b2f35d90780458bdaf8b516d73f0257fd9ec7fbba24c9ea33013e3216e1d10ce`, prepared와 일치.

## 실제 provider 최소 E2E — PASS

기존 허용 추가 예산 총$1 이하에서 사용자가 이미 등록한 Local credential을 앱이 사용했다. 키를 읽어 채팅·파일·로그에 복사하거나 재등록하지 않았다. 원격으로 보낸 것은 합성 문장3개이며 다운로드한 실제 맵 텍스트는 전송하지 않았다.

- 제공사 OpenRouter / 고정 endpoint `https://openrouter.ai/api/v1/chat/completions`, 모델 `deepseek/deepseek-v4.1-flash`, 추론 `모델 기본값`.
- 합성 `External ZIP workflow world` 4파일 + 명시 선택 외부ZIP1파일의 사전 baseline SHA-256 차이0. native scan 후에도0.
- 후보4 중 `Keep original` 제외, 직접 번역0. `Hello external pack`, `Welcome traveler`, `Shop`만 실제 API 전송.
- 결과 completed, API1요청, 입력391 / 출력108 tokens, 실패0 / 경고0. 제공사 응답의 비용 **$0.0001484**, `cost_reported: true`. 이 단일 요청의 provider-reported cost이며 최종 청구서 전체를 감사한 수치가 아니다.
- UI 누적 usage: 14:30:57의0.796399 → 14:33:39의0.796547, BYOK 둘 다0. 표시값 차이0.000148은 응답 비용과 반올림 수준에서 일치한다. 같은 키의 다른 작업·집계 지연 가능성 때문에 usage 차이를 독립적인 정확한 청구 금액으로 단정하지 않는다.
- 변경3파일: region/r.0.0.mca, entities/r.0.0.mca, 외부ZIP. 저장된 파일을 재파싱하여 각각 `여행자여, 환영합니다`, `상점`, `외부 팩 안녕하세요`를 확인했다. 제외된 r.1.0.mca와 level.dat는 byte-identical. 이는 적용 검증이며 전체 번역 품질 검증이 아니다.
- 앱 백업 화면의 `20261001T053234Z-0dd07e8683b3-translation`: 파일3/외부ZIP1/무결성 확인. 실제 복원 실행 후 recovery snapshot `20261001T053438Z-3afbf6bc00b7-recovery` 생성·Ready 확인. **world4+ZIP1 baseline hash 차이0**.
- model/provider/reasoning/override/pack public 설정은 모두 유지됐다. `recent_worlds`만 갱신돼 settings 파일 전체의 byte-identical 복원을 주장하지 않는다. credential 저장 상태도 native 화면에서 확인했다.
- raw report와 공개 설정 baseline은 Git 제외 `output/startup-native-20261001/`. 실제 게임 로드는 NOT_RUN. 검증 앱들은 모두 정상 종료했다.

## 다음 작업과 남은 경계

최종 변경23파일의 `git diff --check` PASS, 갱신한 Markdown의 로컬 링크 누락0, credential/private-key 패턴 검출0, Git 변경 목록의 world/DB/key/ZIP/app 생성물0을 확인했다. 이 패턴 검사는 완전한 비밀 검출 보장이 아니다. 공개5개 원본 SHA-256과 mode0444 및 최종 bundle/sidecar hash를 다시 확인했다. 정상 종료 후 Pomi 앱/sidecar 실행 경로의 잔여 프로세스도 없었다. 문서 변경 때문에 같은 검사·패키지를 다시 실행하지 않았다.

P2-START의 이번 개발 환경 회귀와 P2-API 최소 E2E는 확인됐다. P2-PARITY의 always-backup/app-managed checkpoint 최종 범위 결정 및 P2-FINAL 검토는 남아 있다. 해당 결정을 묻는 사용자 질문은 아직 답을 기다리는 상태다. 결정 없이 parity 완료·Legacy 제거·Phase2 완료로 표시하지 않는다.

Phase2 완료 후 호환성 구현은 [계획](../compatibility-roadmap-2026-10-01.md)의 SNBT command → 최신 component → chunk별 coverage/혼합 형식 순서다. 실제 게임 로드, 경계 버전 텍스트가 있는 샘플, 신규 `.mcc` 생성/복구, clean-machine/다른 OS/keychain/signing/updater/license는 남아 있다. 공개 release·원본 world 쓰기·world 업로드·commit/push는 수행하지 않았다.
