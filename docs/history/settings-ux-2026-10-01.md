# 설정·추론 UI/UX 개선 — 2026-10-01

## 현재 판정

사용자가 승인한 여섯 개선을 반영했다. `main` / 시작 HEAD `9817d54`, 기존 WIP 보존, 이번 수정은 미커밋이다. **Phase2 진행 중 / Phase3 미시작 / release-ready 아님.** 실제 번역 API 추가 비용 $0. 최신 앱은 격리된 PomiTranslate Eval이며 production 데이터와 분리한다.

## 반영한 개선

1. 모델 지원 정보 조회와 설정 저장을 분리했다. 조회는 draft/scan을 저장·무효화하지 않는다.
2. 추론을 `모델 기본값 / 추론 끄기 / 직접 설정`으로 나누고, 직접 설정에만 지원 강도를 표시한다. 모델 기본값의 켜짐·강도와 미확인 상태를 구분한다. 필수 추론 모델의 끄기와 지원하지 않는 강도는 저장을 차단한다.
3. OpenRouter 공개 모델 정보는 입력 후 자동 조회하고 수동 새로고침을 제공한다. 조회 실패·재시도·캐시·모델 미발견을 구분한다. 공개 조회는 고정 OpenRouter endpoint의 models.list에만 credential 접근을 생략하며 번역/usage에는 적용하지 않는다.
4. 고정 하단 저장 영역에 저장됨·변경 있음, 취소·저장을 표시한다. 변화가 없으면 버튼을 비활성화한다. 작은 화면에서 포커스 입력이 저장 영역 뒤로 숨지 않도록 스크롤 여백을 둔다.
5. 제공사·모델을 첫 그룹에 배치하고 저장된 키는 배지·저장 방식·변경/삭제로 간결하게 표시한다. 키 관리·보안과 설정 가져오기·내보내기는 별도 펼침 영역이다.
6. 실행 전 화면에 추론 요약·수정 경로와 추론 토큰/재시도 비용 추정 제외 안내를 추가했다. ko/en/ja 문구를 적용하고 기존 고정 사이드바를 유지했다.

## 이번 소스의 검증

| 영역 | 결과 | 범위 |
| --- | --- | --- |
| Type/UI build | PASS, 0 errors / 0 warnings | 최종 pnpm build |
| Frontend | 관련 4 files / 28 PASS | reasoning/i18n/settings/settings-import |
| Python | test_desktop_provider.py, test_providers.py PASS | 공개 조회의 keyless·설정 불변·캐시와 provider request mock |
| Rust | 24 PASS | tests:: 범위, public catalog bypass 제한 포함 |
| Browser | 관련 30개 시나리오 PASS | 최종 제품 소스에서 29개 PASS + 키보드 테스트 수정 후 해당 1개 PASS; 30개 단일 일괄 실행 결과는 아님 |
| Responsive/a11y | PASS | 320/840/1440px 저장 영역·포커스·가로 overflow·axe 및 화면 직접 점검 |
| Sidecar/Tauri | PASS | Python/Rust 변경 후 마지막 incremental sidecar와 unsigned macOS arm64 Eval app 1회 패키징 |
| Native | PASS | 실제 추론 강도 선택·저장·정상 종료/재시작 유지·실행 전 요약·최종 기본값 복원·사이드바/저장 영역 |

전체 frontend/Python/browser matrix는 이번 UX 소스에서 다시 실행하지 않았다. UX 이전 추론/사이드바 소스의 전체 19 Python suites / frontend50 / browser71 PASS는 과거 증거다. 최신 targeted 결과를 전체 matrix나 release gate 완료로 확대하지 않는다.

### 실제 모델 조회와 native 상태

- 실제 인증 없는 OpenRouter 모델 GET은 HTTP200, Authorization 미전송으로 확인했다. 이는 현재 endpoint의 실측이며 미래의 무인증 지원을 보장하지 않는다.
- 사용자가 직접 저장한 제공사 OpenRouter / 모델 `deepseek/deepseek-v4.1-flash` / 저장된 Local credential 상태를 유지했다. 키 자체를 읽거나 로그·파일에 복사하지 않았다.
- 조회된 모델은 추론 기본 켜짐/high, 지원 강도 low/high/max였다. 공개 조회 전후 public settings 파일 SHA-256 동일을 확인했다.
- 검증에서 max 저장 후 재시작 유지와 Run 요약을 확인했다. 마지막에 원래 `모델 기본값`으로 저장했고, 모델과 키 저장 상태·변경 없는 저장 버튼 비활성화를 실제 화면에서 재확인했다. 이 수동 저장/scan 후 public settings 전체 hash는 시작 시점과 같지 않으므로 전체 설정 파일의 byte-identical 복원을 주장하지 않는다.
- 합성 world4+외부ZIP1 기준 파일의 hash 차이0을 마지막 scan 후 확인했다. 실제 유료 번역 시작 버튼은 누르지 않았다.

### 최신 패키지

- Identifier: `app.pomitranslate.eval20260930r1`
- Bundle: `/Volumes/DevSSD/Developer/BuildCache/cargo-target/debug/bundle/macos/PomiTranslate Eval.app` (59.20 MiB)
- App executable SHA-256: `0bfdb29f322f7f1c991840543dd836b6996c2cd0a763b003c7aa210a883bbbcc`
- Embedded sidecar SHA-256: `b2f35d90780458bdaf8b516d73f0257fd9ec7fbba24c9ea33013e3216e1d10ce` (prepared와 일치)
- 화면 증거: Git 제외 `output/playwright/reasoning-settings-custom.png`, `reasoning-preflight.png`, `settings-ux-1440.png`, `settings-ux-320.png`.

## 남은 경계

- 사용자의 실제 key/model 등록은 완료됐다. 최소 실제 provider 번역의 usage 전후·cost·verified backup/restore는 아직 미실행이다. 공개 모델 조회는 credential 유효성 검증을 대체하지 않는다.
- Legacy backup/checkpoint off/suffix/path 대체 계약, 과거 지속 blank 원인·startup 지연/무응답 복구, clean-machine·다른 OS·keychain opt-in·서명/updater와 Phase3는 남아 있다.
- Phase2 전체 완료 commit/push, 공개 release와 사용자 world upload는 하지 않았다. 생성물/world/DB/key/cache는 Git 제외한다.

최종 변경 검토: `git diff --check` PASS, 변경·신규40파일 credential/private-key 패턴 검출0, 생성물 확장자/경로 포함0, 갱신한 상태 문서의 로컬 링크 누락0. 최신 bundle executable/sidecar hash를 재조회해 위 기록과 일치함을 확인했다. 키 패턴 검사는 완전한 비밀 검출 보장이 아니다.
