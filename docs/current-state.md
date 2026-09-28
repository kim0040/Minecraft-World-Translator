# 현재 상태

2026-09-28. 제품 코드는 `kim0040/Minecraft-World-Translator`의 `main`이다. 저장소 이름은 그대로 두고, 보이는 이름은 PomiTranslate다.

## 들어 있는 것

- CLI `mc_world_translator.py`와 데스크톱 진입점 `python -m mwt.desktop_entry`가 같은 `WorldTranslator`를 쓴다.
- 한 번의 번역은 백업 목록을 하나만 만든다. 복구는 그 실행이 고친 리전 파일을 모두 되돌린다.
- 리전 압축은 gzip, zlib, 무압축, Minecraft `LZ4Block`이다. `.mcc`는 압축된 바이트만 담는다.
- 공급자는 OpenAI, Gemini, Anthropic, OpenRouter, Custom이다. 예전 Comet 설정도 읽는다.
- 텍스트 모델 목록을 받아 그 id를 쓴다. 목록에 없는 모델은 월드를 쓰기 전에 멈춘다.
- API 키는 OS 키체인 서비스 `PomiTranslate`에만 둔다. 공개 설정은 설치 폴더 밖의 사용자 데이터 디렉터리에 남는다.
- 지원 표는 `docs/support-matrix.md`이고, 픽스처를 통과한 형식만 지원이다.
- GitHub Actions는 테스트, 패키지, 릴리스를 돌린다. 서명 자격이 없으면 서명되지 않은 초안에서 멈추고 서명 검증은 켜 둔다.

## 아직 아닌 것

- Tauri와 Svelte 화면은 없다. 패키지된 진입점은 PyInstaller JSONL 프로그램이다.
- Bedrock, `.mcr`, `.linear`, 알 수 없는 압축은 발견만 하고 쓰지 않는다.
- macOS Intel, Windows x64, Linux x64는 지원 플랫폼으로 적지 않는다.
- 로컬 웹 UI는 Python이 있는 환경의 선택 항목이다. 패키지된 앱은 그 서버가 없어도 된다.
