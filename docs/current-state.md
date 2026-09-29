# 현재 상태

제품 코드는 `kim0040/Minecraft-World-Translator`의 `feat/pomitranslate-desktop-app` 브랜치에 있다. 보이는 이름은 PomiTranslate이고 저장소 이름은 그대로다.

## 들어 있는 것

- Tauri 2 + Svelte 5 데스크톱 앱. 패키지된 Python JSONL sidecar가 번역 코어를 실행하고 localhost 서버는 열지 않는다.
- CLI `mc_world_translator.py`, `python -m mwt.desktop_entry`, 데스크톱 앱이 같은 `WorldTranslator`를 쓴다.
- 번역은 세 단계다. 월드 전체에서 텍스트를 모으고, 고유 문자열을 전역 배치로 번역하고, 그 뒤에 월드에 쓴다. 번역이 끝나기 전에는 월드를 쓰지 않는다.
- 제공사 실패는 성공으로 보고하지 않는다. 한도 초과·연결 실패가 이어지면 요청을 멈추고, 인증·잔액·모델 오류는 즉시 멈춘다. 이때 월드는 그대로이고 번역한 문자열은 체크포인트에 남아 이어서 실행할 수 있다.
- 결과 상태는 `completed`, `partial`, `needs_retry`, `failed`, `cancelled`이다. 읽지 못한 청크와 쓸 수 없는 파일은 경고로 보고한다.
- `§` 서식 기호와 `%s`, `{name}` 자리표시자가 번역에서 사라지면 그 문자열은 원문을 유지하고 개수를 보고한다.
- 한 번의 번역은 검증된 백업 세트 하나를 만든다. 복원은 그 실행이 바꾼 파일을 되돌리고, 복원 직전 상태도 recovery 백업으로 남긴다.
- 리전 압축은 gzip, zlib, 무압축, Minecraft `LZ4Block`이다. `.mcc`는 압축된 바이트만 담는다.
- 공급자는 OpenAI, Gemini, Anthropic, OpenRouter, Custom이다. API 키는 OS 키체인 서비스 `PomiTranslate`에만 둔다.
- 지원 표는 `docs/support-matrix.md`이고, 픽스처를 통과한 형식만 지원이다.
- GitHub Actions는 테스트, 패키지, 릴리스를 정의한다. 서명 자격이 없으면 서명되지 않은 초안에서 멈춘다.

## 범위

- 스캔하는 곳: 각 차원의 `region`, `entities`, 켜 둔 경우 월드 안 `resources.zip`.
- 스캔하지 않는 곳: 데이터팩, `data/*.dat`(command storage, scoreboard), `level.dat`, 플레이어 데이터.

## 아직 아닌 것

- Bedrock, `.mcr`, `.linear`, 알 수 없는 압축은 발견만 하고 쓰지 않는다.
- macOS Intel, Windows x64, Linux x64는 clean-machine 검증 전이라 지원 플랫폼으로 적지 않는다.
- 배포 서명, notarization, 공개 릴리스는 하지 않았다.
- 나머지 작업은 `docs/remaining-work.md`에 있다.
