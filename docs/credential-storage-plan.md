# API credential 저장 계획 — 로컬 암호화 저장

기준일: 2026-09-30\
상태: 사용자 합의에 따른 계획, **미구현**\
연결 문서: [전체 작업 인계](agent-handoff-2026-09-30.md)

## 결정과 이유

사용자는 반복되는 OS 키체인 접근 허용 요청을 줄이기 위해 앱의 DB에 API 키를 암호화해 저장하는 방향을 요청했다. 데스크톱 앱의 기본 credential 저장소를 로컬 암호화 저장으로 변경하고, OS 키체인은 선택 기능으로 유지한다. 세션 전용 저장도 선택할 수 있게 한다.

이는 “키체인과 같은 보안 수준”을 주장하는 변경이 아니다. 로컬 사용자 계정으로 DB와 암호화 키 파일을 모두 읽을 수 있는 프로세스는 API 키를 복호화할 수 있다. DB 파일만 노출되는 경우의 보호와 별도 권한 팝업 없는 사용을 목표로 한다. 최초 설정 화면에서 이 보호 범위를 짧게 설명한다.

API 키 평문을 DB·설정 JSON·로그·소스·환경설정 파일에 저장하지 않는 원칙은 유지한다. 서명 키나 updater 키를 이 저장소로 옮기지 않는다.

## 현재 구현과의 차이

- `mwt/userdata.py`: 설정·최근 월드는 `settings.json`에 저장한다.
- scan plan·checkpoint도 JSON이다. 통합 SQLite data layer는 아직 없다.
- `mwt/secrets.py::save_public_settings`: provider/model만 저장하는 작은 SQLite 함수이며, 운영 데이터 전체를 관리하는 DB가 아니다.
- `src-tauri/src/lib.rs`: Rust가 서비스 `PomiTranslate`의 provider별 키체인 항목을 읽고 저장·삭제한다.
- `credential_status`는 현재 실제 비밀번호를 읽어서 존재 여부를 판단한다. 설정 조회·저장 응답에서도 `read_key`를 호출한다.
- `src/lib/app.svelte.ts`와 `SettingsScreen.svelte`도 credential 상태를 조회한다.
- Python sidecar는 `credentialOwner: rust` 요청에서 키체인 fallback을 사용하지 않는다.

따라서 이 계획을 현재 구현 완료로 소개하면 안 된다.

## 저장 구조

Rust가 관리하는 작은 credential vault부터 구현한다. glossary/TM/candidate 전체의 DB 이전을 먼저 진행할 필요는 없다.

```text
<app-data>/credentials/credentials.sqlite  # 암호문과 비밀이 아닌 메타데이터
<app-data>/credential-key/master.key     # 설치별 무작위 256-bit 암호화 키
```

실제 경로는 Tauri app-data와 기존 Python user-data 경로를 조사한 뒤 확정한다. 개발·테스트·사용자 설치 데이터는 분리한다. 앱 설치 디렉터리, 현재 작업 디렉터리, world 폴더에 저장하지 않는다. 두 파일이 같은 사용자 디스크에 있다는 한계는 문서와 UX에 숨기지 않는다.

권장 schema:

- `vault_meta`: schema version, key id, 생성 시각.
- `credentials`: provider/account 식별자, cipher version, key id, nonce, ciphertext(인증 tag 포함), 생성·수정 시각.
- provider/account에 unique constraint. 원문 키·전체 키의 표시용 복사본·키 hash를 저장하지 않는다.
- 상태 확인은 메타데이터로 수행하며 키를 읽거나 복호화하지 않는다. “저장됨”과 “사용 가능/잠금 해제 실패”는 구분한다.

## 암호화와 파일 접근

- 검증된 라이브러리의 AES-256-GCM 사용. 자체 암호 알고리즘 구현 금지.
- 저장할 때 암호화하고, 실제 provider 요청에 필요할 때 복호화한다.
- 암호화 키와 nonce는 OS CSPRNG로 생성한다. nonce 재사용 금지.
- provider/account, schema/cipher version, key id를 AAD로 결합해 다른 항목으로 암호문을 옮겼을 때 인증이 실패하도록 한다.
- 앱 전체가 공유하는 고정 키, 소스/바이너리에 하드코딩한 키, 머신 id·경로에서 단순 파생한 키를 사용하지 않는다.
- macOS/Linux: 디렉터리 0700, DB·키·SQLite journal/WAL·임시 파일 0600. 생성 시점부터 제한된 권한 적용. symlink와 예상 밖 소유자를 거부한다.
- Windows: 현재 사용자 SID를 기준으로 파일과 디렉터리 DACL을 제한한다. Unix chmod가 Windows 보호를 대신한다고 가정하지 않는다. 구현 라이브러리와 상속 정책은 Windows 실기 검증으로 확정한다.
- 키 생성은 race-safe/atomic하게 수행한다. 이미 DB에 credential이 있는데 master key가 없으면 임의로 새 키를 만들어 정상 상태로 덮어쓰지 않는다.
- Rust만 master key를 다룬다. frontend에 암호화 키나 저장된 API 키를 반환하지 않는다.
- API 키는 기존 JSONL stdin 경로로 필요한 sidecar 요청에만 전달한다. argv·환경변수·로그로 우회 전달하지 않는다.
- 메모리 보유 범위와 수명은 필요한 요청/세션으로 제한하고, 가능한 zeroization을 사용한다. 메모리 복사나 swap까지 완전 제거했다고 주장하지 않는다.

## UX와 설정

저장 모드:

1. 로컬 암호화 저장 — 새 설정의 기본값, 재시작 후 자동 사용.
2. 이번 실행에서만 사용 — 영속 저장 없음.
3. OS 키체인 — 사용자가 선택할 때만 접근.

Settings는 저장 방식·저장 여부·변경·삭제를 표시한다. 저장된 키 전체 값을 다시 보여 주지 않는다. 삭제에는 현재 UX의 확인 dialog를 유지한다. World/Scan/Review에 API 키를 요구하지 않는다.

키체인 모드를 선택하지 않은 시작·화면 이동·상태 확인에서는 키체인 API를 호출하지 않는다. 로컬 vault 오류를 키체인 접근으로 자동 우회하지 않는다. macOS 파일 권한 요청이나 개발 도구 승인까지 모두 없어지는 변경이라고 설명하지 않는다.

## 기존 키체인 사용자 migration

- 자동으로 기존 키를 읽어서 startup 권한 팝업을 띄우지 않는다.
- 기존 설정은 보존하고, Settings에서 `기존 키 가져오기` 또는 `새 키 입력` 선택을 제공한다. 가져오기는 사용자가 누른 경우에만 키체인에 접근한다.
- 암호화 저장 transaction 및 저장 후 복호화 검증이 끝난 뒤 사용 모드를 전환한다.
- 실패하면 기존 credential과 모드를 보존한다. 중간 상태를 성공으로 보고하지 않는다.
- 기존 키체인 항목은 자동 삭제하지 않는다. 사용자가 삭제를 선택해야 한다.
- `openrouter`, `custom` 등 provider/account 매핑 유지. Custom endpoint와 공개 provider credential을 혼용하지 않는다.
- CLI/legacy Web UI의 기존 keyring 계약은 별도 호환 계층으로 유지한다. 데스크톱 변경 때문에 CLI에서 갑자기 키가 없어지거나 새 저장소로 조용히 옮겨지면 안 된다.

## 실패·백업·업데이트

- master key 누락, 암호문 변조, schema 불일치, permission 오류는 credential 사용 실패로 명확히 보고한다. 해당 요청을 provider로 보내지 않는다.
- 복호화 실패를 “키 없음”으로 바꾸거나 DB를 재생성해 정보를 숨기지 않는다.
- 키 파일을 잃으면 재입력해야 한다는 안내를 제공한다. 이동·재설치·업데이트·이전 사용자 데이터 경로 migration을 테스트한다.
- world backup에는 credential DB·키 파일을 넣지 않는다.
- 일반 진단 export와 앱 설정 export도 credential DB·키·평문을 포함하지 않는다. 앱 데이터 export가 있다면 포함 정책을 명시한다.
- credential DB와 key 파일을 자동 클라우드 동기화하거나 임의 backup 위치에 복사하지 않는다.
- master key rotation과 비밀번호로 잠그는 portable export는 후속 기능이다. 미구현이면 제공한다고 표시하지 않는다.

## 구현 범위와 검증 계약

주요 변경 예상 파일:

- `src-tauri/src/credentials/` (또는 동등한 작은 Rust 모듈): vault, crypto, permission, migration.
- `src-tauri/src/lib.rs`: credential command routing 및 sidecar 주입.
- `src-tauri/Cargo.toml`/lock: SQLite·crypto·permission 관련 의존성.
- `src/lib/api.ts`, `app.svelte.ts`, `SettingsScreen.svelte`: 모드·상태·migration UI.
- i18n ko/en/ja 및 privacy/About 문구. 중국어 지원을 선언하려면 실제 locale도 구현.
- `mwt/secrets.py`, brand/secret/provider tests: 데스크톱과 CLI 계약 구분.

필수 테스트:

- 저장·읽기·변경·삭제·재시작, provider 격리, 세션 모드 비영속성.
- DB/WAL/임시 파일/로그/frontend 응답에 fixture 평문이 없는지 확인.
- nonce·AAD·tag 변조, provider 바꿔치기, master key 누락, migration 실패, concurrent 생성/저장.
- 플랫폼별 permission, 권한 실패 시 fail closed, symlink 거부.
- startup·Settings 조회·일반 저장·scan에서 키체인 호출 0회. opt-in migration/keychain 모드만 접근.
- 공개 provider에 숨은 Custom endpoint나 POMI_* 환경변수가 있어도 UI가 선택한 credential을 잘못된 host로 전송하지 않음. CLI의 의도된 환경변수 override 계약과 구분.
- Rust vault unit tests → browser fixture의 mode/migration/error UX → frontend/Python contract → 마지막 Tauri 재시작·permission·모드 전환 E2E. 실제 credential 보호를 browser mock PASS로 대신하지 않으며, UX 수정마다 app bundle을 만들지 않는다. [웹 우선 절차](browser-first-testing-plan.md)를 따른다.
- paid API는 모든 로컬 검증 후 최소 1건. 남은 전체 예산 상한 $1 유지.

새 저장 모드를 구현했다고 Phase 2 전체를 자동 완료 처리하지 않는다. 전체 gate는 인계 문서를 따른다.

## 참고

[OWASP Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)는 암호화 키를 데이터와 분리해 저장하도록 권고한다. 별도 로컬 파일을 사용한다는 사실만으로 OS credential store와 동등한 보호를 얻는 것은 아니다.
