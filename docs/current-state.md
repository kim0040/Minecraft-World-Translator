# 현재 상태

2026-09-30 문서 갱신 직전 제품 코드는 `main` / `e70d27a`였고 clean 상태였다. 로컬 `feat/pomitranslate-desktop-app`도 같은 commit이며 원격 ref는 fetch하지 않은 관측이다. 후속 시작 시 다시 확인한다. 보이는 이름은 PomiTranslate이고 저장소 이름은 그대로다.

최신 실행 계약은 [전체 에이전트 인계](agent-handoff-2026-09-30.md)다. **Phase 2 미완, Phase 3 미시작**이며 코드 존재를 완료 검증으로 취급하지 않는다. 이번 요청은 문서 갱신과 문서 전용 commit/push다. 테스트/API/제품 구현은 수행하지 않았으며 이 commit은 Phase 완료를 뜻하지 않는다.

## 들어 있는 것

- Tauri 2 + Svelte 5 데스크톱 앱. 패키지된 Python JSONL sidecar가 번역 코어를 실행하고 localhost 서버는 열지 않는다.
- CLI `mc_world_translator.py`, `python -m mwt.desktop_entry`, 데스크톱 앱이 같은 `WorldTranslator`를 쓴다.
- 텍스트 추출은 `mwt/extract.py`, NBT 읽기·쓰기는 `mwt/nbtio.py`다. NBT 리더는 원본 바이트를 보존하고 수정한 문자열만 그 자리에서 바꿔 쓴다. 수정하지 않은 청크는 바이트까지 같고, Java modified UTF-8(이모지, NUL)을 읽는다.
- 표지판(앞·뒤), 책 제목·페이지, 아이템 이름·설명(`extra`, `with`, `fallback`, hover/click 포함), 컨테이너 안 아이템, 블록·엔티티 이름, `text_display`, 명령 블록의 `tellraw`/`title`(`execute ... run` 포함)을 찾는다.
- 후보는 종류·위치(블록/엔티티 id, 좌표, 청크)·발생 횟수를 가진다. 이미 대상 언어로 된 문자열은 후보에서 뺀다(설정으로 끌 수 있다).
- scan plan은 월드 지문과 대상 언어·리소스팩 범위·이미 대상 언어인 문자열 건너뛰기·extractor version의 scope 지문에 묶인다. 모델·제공사·배치 크기를 바꿔도 검토한 스캔은 유지된다.
- 백업은 앱 데이터 디렉터리의 월드별 폴더에 둔다. 예전 릴리스가 월드 안 `.pomi-backups`에 만든 백업도 목록에 나오고 복원된다.
- 번역 요청은 기본 4개까지 동시에 보낸다(1–8). 한도 제한과 서킷 브레이커는 동시 요청에서도 그대로 적용된다.
- 번역은 세 단계다. 월드 전체에서 텍스트를 모으고, 고유 문자열을 전역 배치로 번역하고, 그 뒤에 월드에 쓴다. 번역이 끝나기 전에는 월드를 쓰지 않는다.
- 제공사 실패는 성공으로 보고하지 않는다. 한도 초과·연결 실패가 이어지면 요청을 멈추고, 인증·잔액·모델 오류는 즉시 멈춘다. stop 정책의 번역 실패는 쓰기 전에 중단되며 번역한 문자열은 체크포인트에 남아 재시도할 수 있다. skip 정책/파일 오류의 partial 결과와 구분해야 한다.
- 결과 상태는 `completed`, `partial`, `needs_retry`, `failed`, `cancelled`이다. 읽지 못한 청크와 쓸 수 없는 파일은 경고로 보고한다.
- `§` 서식 기호와 `%s`, `{name}` 자리표시자가 번역에서 사라지면 그 문자열은 원문을 유지하고 개수를 보고한다.
- 한 번의 번역은 검증된 백업 세트 하나를 만든다. 복원은 그 실행이 바꾼 파일을 되돌리고, 복원 직전 상태도 recovery 백업으로 남긴다.
- 리전 압축은 gzip, zlib, 무압축, Minecraft `LZ4Block`이다. `.mcc`는 압축된 바이트만 담는다.
- 공급자는 OpenAI, Gemini, Anthropic, OpenRouter, Custom이다. **현재 구현**은 Rust가 OS 키체인 서비스 `PomiTranslate`에 API 키를 보관한다.
- **새 합의·미구현**: [credential 저장 계획](credential-storage-plan.md)에 따라 로컬 암호화 DB + 별도 설치별 master key를 기본으로 하고 키체인/세션 모드를 선택 기능으로 둔다. DB와 키 파일 모두에 접근 가능한 같은 사용자 프로세스까지 차단하는 설계는 아니다.
- 일반 설정·최근 월드·scan plan은 JSON이다. 통합 SQLite data layer는 미구현이며 작은 SQLite public-settings helper만 있다.
- Phase 2 화면 분리, candidate virtual window/keyboard, System/Light/Dark, ko/en/ja UI와 frontend tests가 코드에 있다. 100k 실제 성능과 최종 integration은 별도 gate다.
- 지원 표는 `docs/support-matrix.md`이고, 픽스처를 통과한 형식만 지원이다.
- GitHub Actions는 테스트, 패키지, 릴리스를 정의한다. 서명 자격이 없으면 서명되지 않은 초안에서 멈춘다.

## 범위

- 스캔하는 곳: 각 차원의 `region`, `entities`, 켜 둔 경우 월드 안 `resources.zip`.
- 스캔하지 않는 곳: 데이터팩, `data/*.dat`(command storage, scoreboard), `level.dat`, 플레이어 데이터. 외부 리소스팩 선택/merge는 현재 desktop UI에서 제공하지 않는다. backend/CLI 기능과 desktop parity를 구분한다.

## 이전 검증 기록

이전 세션에서 frontend/Python/Rust/build, 대표 screenshot·responsive·dark·keyboard, 실제 Tauri local mock 번역/복원과 117파일 byte-identical 복원을 기록했다. 실제 provider라고 생각한 후속 실행은 stale localhost endpoint를 호출했으므로 mock 검증으로만 인정한다. endpoint 수정 코드는 있지만 최종 실제 provider gate는 남았다. 이번 문서 작업은 이 결과를 재실행하지 않았고 새 HEAD의 완료 증거로 단정하지 않는다. 상세 결과·한계·산출물은 인계 문서에 있다.

## 아직 아닌 것

- Bedrock, `.mcr`, `.linear`, 알 수 없는 압축은 발견만 하고 쓰지 않는다.
- macOS Intel, Windows x64, Linux x64는 clean-machine 검증 전이라 지원 플랫폼으로 적지 않는다.
- 배포 서명, notarization, 공개 릴리스는 하지 않았다.
- 나머지 작업은 `docs/remaining-work.md`에 있다.
