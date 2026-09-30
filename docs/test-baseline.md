# 기준 테스트

> 최신 검사 순서: [웹 우선 UI/기능 검증·화면 비율 대응](browser-first-testing-plan.md). 앱 packaging은 웹/코어 검사 후 마지막 native gate에서 수행한다.

> 원격 인계용 사본: 프로젝트 루트 계획/기록을 제품 저장소에도 포함했다. 본문의 프로젝트 루트 경로는 기존 로컬 배치를 설명하며, 이 저장소만 clone한 경우 실행 명령은 clone 루트에서 수행한다.

> 2026-09-30: 아래는 과거 baseline 기록이다. 현재 테스트 명령, Phase 2/3 완료 gate, 결과의 재검증 범위는 [전체 인계](agent-handoff-2026-09-30.md)를 따른다. 당시의 407후보/번역 미실행/접근성 미검증 기록을 최신 상태로 사용하지 않는다. 이번 문서 작업에서는 테스트를 재실행하지 않았다.

처음 기록한 기준 커밋은 `cf91bb5d7453202932bff548266a0cb6756be0c9`이다. 그 시점의 `test_core.py`는 19개였다.

현재 제품 테스트는 같은 가상환경에서 다음을 실행한다.

```bash
.venv/bin/python test_core.py
.venv/bin/python tests/test_release_fixtures.py
.venv/bin/python tests/test_providers.py
.venv/bin/python tests/test_brand_secrets.py
.venv/bin/python tests/test_desktop_entry.py
```

실행 환경은 Python 3.12.14와 `NBT==1.5.1`이다. 시스템 기본 `python3`는 이 기준 실행에 쓰지 않는다.

릴리스 픽스처가 Scan Only, 복구, 체크포인트, 압축, 텍스트 모양, 미지원 형식의 무기록을 담당한다. 지원 표는 그 결과로 생성한다.

2026-09-29 데스크톱 작업에서는 다음도 확인했다.

- Svelte/TypeScript 검사 0 error, 0 warning
- Rust/Tauri `cargo check` 통과
- macOS arm64 `.app` 번들 생성, ad hoc 서명 무결성 통과
- 실제 앱 프로세스 기동 및 TCP listener 없음
- 실제 앱 접근성 트리·렌더링에서 준비 상태, 한국어·영어·일본어 전환, 키체인 상태 비동기 반영 확인
- 시작 bootstrap 단일화, 전체 형식 검사를 Scan Only에 유지, 패키지 sidecar bootstrap 0.177초
- 저장된 샘플 월드 실제 Scan Only: 후보 407개, API 요청 0회, 배치 40 기준 최소 요청 11회 표시. 번역 실행은 취소함
- scan plan paging, 설정 변경 invalidation, 후보 제외, 수동 번역 API 0회
- 버전 백업, 복원 전 recovery snapshot, 매니페스트 경로 탈출 거부
- 동일 월드 동시 write lock
- Minecraft/서버 `session.lock` 충돌 시 실제 쓰기 중단
- 월드 내부 `resources.zip`과 리전을 한 백업 세트로 번역·복원
- `resources.zip` 변경 뒤 기존 scan plan 무효화
- DataVersion 읽기와 구조 기반 호환성 입력
- 고급 번역 설정 저장과 공개 설정에서 비밀 제외
- 한국어·영어·일본어 UI 카탈로그의 화면 키 완전성, UI 언어 저장, 번역 설정 지문과 UI 언어 분리
- 제외·직접 번역 후보와 배치 크기를 반영한 번역 전 최소 요청 수 표시. 파일 경계·재시도 제외 및 재개 작업 확인 불가 문구 포함
- 협력적 취소 체크포인트 감지와 명시적 재개
- 한 파일 기록 후 같은 백업 세트로 나머지 파일 재개·전체 복원

GUI에서 주요 화면과 언어 전환은 확인했다. 전체 키보드 순회, 화면 읽기 프로그램 발화, 200% 확대, 320px 상당 폭은 아직 확인하지 않았다. macOS Intel/Windows/Linux clean-machine 설치와 실제 유료 provider 호출도 아직 실행하지 않았다.

## `test_core.py`

명령:

```bash
.venv/bin/python test_core.py
```

결과: 19개 전부 통과.

- 문자열 필터, 설정 병합, JSON 텍스트, 명령 컴포넌트
- 리전 경로 범위와 백업 파일 건너뛰기
- 리소스팩 dry-run이 파일을 쓰지 않음
- 체크포인트 설정 불일치 거부
- LLM 응답 키 누락 거부
- 원자적 쓰기 권한 유지
- 깨진 `translate.py`는 무시

이 테스트는 실제 `.mca` 라운드트립, LZ4, `.mcc`, 양면 표지판, item component를 검사하지 않는다.

## CLI

`--help`는 정상 종료했다.

빈 월드 디렉터리에 `--dry-run`을 실행한 결과:

- `status`: `completed`
- `dry_run`: `true`
- `candidate_file_count`: 0
- `candidate_text_count`: 0
- `changed_file_count`: 0
- `errors`: 없음
- API 키 없이 완료했다. 실제 번역 경로는 키가 없으면 실행 전에 중단한다.

## Web UI

`webui_server.py --host 127.0.0.1 --port 8766`

- `GET /` 200, 제목 `Minecraft World Translator UI`
- `GET /api/meta` 200
- 제공자: openai, gemini, anthropic, openrouter, comet, custom_openai, custom_anthropic
- 기본 스캔 경로: `region`, `entities`, `DIM-1/region`, `DIM-1/entities`, `DIM1/region`, `DIM1/entities`
- `GET /api/jobs` 200, 작업 없음

브라우저에서 버튼을 눌러 번역을 실행하는 확인은 하지 않았다.
