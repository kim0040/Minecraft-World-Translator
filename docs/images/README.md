# 소개용 화면 정보

2026-10-01에 현재 Svelte 제품 UI를 Playwright/Chrome으로 캡처했다. 브라우저의 합성 backend entry를 사용했으며 actual provider·native 설치·유료 번역 검증을 대체하지 않는다. UI를 다시 그린 목업이 아니다.

- Viewport: 1440×980, 한국어, light theme. Run은 전체 페이지를 캡처했다.
- Entry: `/tests/frontend/preview.html?scenario=review&model=deepseek/deepseek-v4.1-flash` (개발 전용 fixture).
- 후보·월드 경로·모델 정보·추정 비용·키 저장 배지는 합성 데이터다. 실제 키를 입력·조회하지 않았다.
- `review.png`: 후보 검토와 직접 번역 편집.
- `settings.png`: 모델·직접 추론 설정·저장되지 않은 변경 상태.
- `run.png`: 추론·요청 수·비용의 실행 전 요약. 번역 시작 버튼은 누르지 않았다.

## 파일

| 이미지 | 크기 | SHA-256 |
| --- | --- | --- |
| review.png | 1440×980, 166,505 bytes | `213927be9531d98ff76909c8f87ff9635af5448cf667540f4a4b2247d140e7d8` |
| settings.png | 1440×980, 118,485 bytes | `dde19d4200a89fb3f61106d8b76a016afdc8fec06c3351e377104a5928ce242c` |
| run.png | 1440×1179, 148,613 bytes | `4da9e5f73236c438bffae2ff9a83c48a837ad0088c02d0951b89ec556d0c9079` |

현재 저장소의 서비스 소개용으로 이 세 이미지와 이 문서만 추적한다. 일반 screenshot·trace·검증 cache는 `output/`에서 Git 제외한다. 버전이나 화면이 바뀌면 최신 UI를 합성 데이터로 다시 캡처하고, 원문/키/개인 경로가 없는지 직접 확인한다.
