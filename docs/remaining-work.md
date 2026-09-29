# PomiTranslate 남은 작업과 완료 기준

기준일: 2026-09-29  
기준 브랜치: `feat/pomitranslate-desktop-app`  
구현 기준: `4c50a6e`까지

이 문서는 현재 코드에 들어 있는 기능과 실제로 검증한 범위를 구분하고, PomiTranslate를 배포 가능한 1.0으로 만들기 위해 남은 작업을 기록한다.

## 현재 도달한 상태

현재 빌드는 단순한 웹 UI가 아니라 Tauri 2 + Svelte 5 데스크톱 앱이다. 패키지된 Python JSONL sidecar가 기존 번역 코어를 실행하며 localhost 서버를 열지 않는다.

구현하고 현재 환경에서 확인한 항목:

- macOS Apple Silicon용 `PomiTranslate.app` 생성 및 실제 기동
- CLI와 데스크톱 앱이 같은 Python 번역 코어 사용
- 월드 선택, 최근 월드, DataVersion 참고 정보, 구조 기반 호환성 검사
- Scan Only, 후보 검색·필터·페이지 조회·제외·직접 번역
- 한국어·영어·일본어 UI
- OpenAI, Gemini, Anthropic, OpenRouter, Custom 제공사 설정
- API 키의 OS 키체인 저장·조회·삭제
- 온도, 배치 크기, RPM/TPM, timeout, retry, 스타일 프롬프트 설정
- 쓰기 전 검증 백업, 버전별 백업 기록, 복원 전 recovery 백업
- Minecraft/서버가 `session.lock`을 잡은 월드의 쓰기 차단
- 월드 내부 `resources.zip`의 선택적 번역과 리전 파일을 포함한 통합 복원
- 협력적 취소와 조건이 일치하는 취소 작업의 명시적 재개
- gzip, zlib, 무압축, `LZ4Block`, 외부 `.mcc` 청크 픽스처
- 실행 전 외부 전송 후보 수, 최소 번역 요청 수, 백업·비용 상태 표시

실제 앱에서 저장된 샘플 월드를 Scan Only로 검사한 결과는 후보 407개, 번역 API 요청 0회였다. 배치 크기 40에서 최소 번역 요청 11회를 표시했다. 이 값은 파일 경계와 재시도를 제외한 하한이다. 비용은 신뢰 가능한 제공사 가격을 확인하지 않았으므로 `확인 불가`로 표시한다. 실제 번역 시작은 실행하지 않았다.

## P0 — 배포 전에 반드시 끝낼 일

### 배포 서명과 업데이트

- Apple Developer ID 서명과 notarization
- Windows 코드 서명
- 서명된 updater manifest와 update bundle
- 업데이트 중 활성 번역 작업 보호와 실패 시 rollback
- 기존 사용자 데이터, 키체인 identifier, 설정 migration 검증

현재 앱의 ad hoc 서명은 로컬 무결성 검사 용도다. 배포 서명이나 notarization 완료를 뜻하지 않는다. 서명 자격 증명과 공개 릴리스는 별도 승인이 필요하다.

### clean-machine 설치 검증

다음 환경마다 CI 빌드 성공과 별도로 새 사용자 환경에서 설치·기동·기본 흐름을 확인해야 한다.

- macOS Apple Silicon
- macOS Intel
- Windows x64
- Linux x64

각 환경의 완료 기준:

1. Python, Node, Rust가 없는 환경에서 앱이 기동한다.
2. 패키지된 sidecar handshake가 성공한다.
3. 월드 선택과 Scan Only가 동작한다.
4. 키체인 또는 credential store 저장·조회·삭제가 동작한다.
5. 앱 종료 뒤 재시작해 설정과 최근 월드가 유지된다.
6. localhost TCP listener가 생기지 않는다.
7. 백업·복원 픽스처와 패키지 smoke가 통과한다.

### 공개 릴리스 게이트

- 원격 GitHub Actions의 Linux/macOS/Windows 패키지 작업 통과
- 산출물별 SHA-256과 서명 상태 기록
- 설치·제거·업데이트 smoke 결과 기록
- 실제 지원 플랫폼만 README와 support matrix에 표기
- 공개 릴리스와 업로드는 사용자 확인 후 수행

## P1 — 1.0 핵심 기능에서 남은 일

### candidate occurrence 정규화

현재 scan plan은 고유 원문 문자열 중심이다. 후보의 `kind`는 일반값이고 실제 `location`과 occurrence 목록을 보존하지 않는다.

남은 구현:

- 후보별 실제 종류: 표지판 앞·뒤, 책 제목·페이지, lore, 명령 컴포넌트 등
- 월드, 차원, 리전, 청크, NBT 경로를 포함한 occurrence 위치
- 같은 원문의 occurrence 수와 occurrence 단위 포함·제외
- 양면 표지판을 한 개체로 묶되 앞·뒤 occurrence 구분
- scan plan과 체크포인트 schema revision 및 migration

완료 기준은 UI에 표시하는 종류·위치·횟수가 실제 fixture 경로와 일치하고, occurrence 하나만 제외해도 다른 발생 위치는 그대로 번역되는 것이다.

### 대규모 후보 UI

현재 API와 UI는 200개 단위 paging을 사용해 한 번에 10만 행을 만들지는 않는다. 계획서가 요구하는 진정한 virtualized table과 10만 occurrence 성능 검증은 남아 있다.

- 10만 occurrence 성능 fixture
- virtualized row rendering
- 검색·필터·직접 편집 중 스크롤 위치와 선택 상태 유지
- scan progress 이벤트 병합과 렌더 빈도 제한
- 메모리·응답 시간 측정값 기록

### 외부 리소스팩과 merge 정책

현재는 선택한 월드 폴더 안의 `resources.zip`만 처리한다.

- 사용자가 선택한 외부 리소스팩 ZIP
- 리소스팩 폴더와 modpack 리소스팩 폴더
- 기존 대상 locale 파일의 overwrite, skip, merge 정책
- namespace별 충돌 보고
- 월드 밖 입력은 읽기만 허용하고, 쓰기 대상과 백업 위치를 명확히 제한
- ZIP slip, symlink, path traversal 픽스처

### 강제 종료와 crash recovery

현재 재개는 협력적으로 취소되어 `cancelled` 상태가 기록된 작업만 지원한다.

- 프로세스 kill, 전원 중단, sidecar crash 뒤 `interrupted` 판정
- 부분 쓰기 파일과 백업 manifest의 일관성 검사
- 자동 재개 금지, 사용자에게 복원·재개·폐기 선택 제공
- 재시도 시 중복 API 과금 가능성 표시
- 강제 종료 fixture와 실제 패키지 smoke

### glossary와 translation memory

- 월드 범위 glossary와 전역 glossary
- 강제 번역, 번역 금지, 선호 번역, 고급 regex 규칙
- source + target language + 관련 profile fingerprint 기반 translation memory
- 기본값은 월드 범위로 격리
- 내보내기·가져오기와 삭제
- prompt, glossary, model, segmentation revision 변경 시 자동 무효화 또는 재처리

다른 월드의 문맥 또는 민감한 문자열이 자동으로 섞이지 않는 격리 테스트가 필요하다.

### 토큰·비용·시간 추정

현재 요청 수는 `외부 전송 고유 후보 ÷ 배치 크기`로 계산한 하한이다.

- 파일 경계와 실제 batch 분할을 반영한 요청 범위
- 모델 tokenizer가 확인된 경우에만 token 추정
- 신뢰 가능한 제공사 가격과 조회 시각이 있을 때만 비용 추정
- 실제 응답 usage와 예상값 비교
- 재개 작업은 전체가 아니라 남은 작업량만 계산
- 가격을 알 수 없을 때 `$0.00` 대신 `확인 불가` 유지

## P2 — 안전성과 데이터 계층

### 영속 schema와 migration

현재 공개 설정과 scan plan은 사용자 데이터 디렉터리의 JSON 파일을 쓴다. 계획서의 SQLite 범위는 구현하지 않았다.

- schema version과 migration runner
- candidate occurrence, job, glossary, translation memory 테이블
- migration 실패 시 원본 보존과 rollback
- 앱 업데이트 전후 데이터 호환성 fixture

SQLite 도입은 위 데이터가 실제로 필요해지는 시점에 수행하며, 현재 동작하는 JSON 설정을 근거 없이 교체하지 않는다.

### 지원 범위 확장

- Java DataVersion별 검증 표
- 큰 modpack/server world 성능 fixture
- 더 많은 현대 텍스트 컴포넌트와 명령 구조 fixture
- custom dimension과 Paper 분리 월드의 실제 표본 검증 확대

Bedrock, pre-Anvil `.mcr`, `.linear`, 알 수 없는 압축은 adapter와 무기록 fixture가 생기기 전까지 쓰지 않는다.

## P3 — UX, 접근성, 제품 문서

### 접근성 실기 검증

현재 native dialog, skip link, focus 표시, live region, reduced motion, 반응형 reflow를 구현했고 접근성 트리에서 주요 화면과 언어 전환을 확인했다.

남은 검증:

- 키보드만으로 전체 작업 흐름 수행
- dialog focus trap과 닫힌 뒤 focus 복원
- VoiceOver, NVDA 또는 동등한 화면 읽기 프로그램 발화
- 200% 확대
- 320px 상당 폭 reflow
- 고대비·색각·오류 상태 검토
- 긴 영어·일본어 문구와 시스템 글꼴 확대에서 잘림 확인

### 일반 설정

- theme system/light/dark
- font size
- density
- 로그·캐시·translation memory 삭제 UI
- 진단 정보 내보내기 시 비밀과 개인 경로 redaction

### About와 고지

- Minecraft EULA와 Usage Guidelines 링크
- MIT 및 third-party notices 화면
- 빌드 버전·commit·지원 플랫폼 표시
- 영어·한국어 법적 고지 원문 누락 검사

## 아직 실행하지 않은 실제 부작용 검증

- 유료 제공사에 대한 실제 번역 요청
- 사용자 월드에 대한 실제 번역 쓰기
- 배포 서명 키 사용
- notarization
- 공개 릴리스, release upload, updater 배포

이 항목들은 비용, 자격 증명, 사용자 데이터 변경 또는 공개 배포가 수반되므로 각각 실행 직전에 별도 확인한다.

## 권장 작업 순서

1. 원격 CI 패키지 결과와 clean-machine smoke를 확보한다.
2. candidate occurrence schema와 실제 위치 데이터를 구현한다.
3. 10만 occurrence 성능 fixture와 virtualized table을 구현한다.
4. 외부 리소스팩 및 merge 정책을 추가한다.
5. 강제 종료 recovery를 구현한다.
6. glossary와 월드 범위 translation memory를 추가한다.
7. 토큰·비용·시간 추정을 검증 가능한 제공사부터 추가한다.
8. 접근성 실기와 배포 서명·updater gate를 통과한다.

## 완료 판정 원칙

- 정적 검사나 빌드 성공만으로 기능 완료라고 하지 않는다.
- scan, 백업, 번역, 복원은 동일 fixture 또는 실제 허가된 월드에서 end-to-end로 확인한다.
- 플랫폼 지원은 그 플랫폼의 clean-machine 설치·기동·기본 흐름을 확인한 뒤에만 표기한다.
- 가격, 버전, 형식 지원은 확인한 근거와 확인 시각을 함께 기록한다.
- 알 수 없는 데이터는 `unknown` 또는 `확인 불가`로 유지한다.
- 공개 릴리스와 사용자 월드 쓰기는 명시적 승인 없이 실행하지 않는다.
