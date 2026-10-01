# 소개용 화면 정보

2026-10-01 네이티브 UX 개편 후 현재 Svelte 제품 UI를 Playwright/Chromium(Linux)으로 다시 캡처했다. 브라우저의 합성 backend entry를 사용했으며 actual provider·native 설치·유료 번역 검증을 대체하지 않는다. UI를 다시 그린 목업이 아니다.

- Viewport: 1440×980, 한국어, light theme. 내용 영역만 스크롤하는 셸이므로 세 이미지 모두 창 크기 그대로다.
- Entry: `/tests/frontend/preview.html?scenario=review&model=deepseek/deepseek-v4.1-flash` (개발 전용 fixture).
- 후보·월드 경로·모델 정보·추정 비용·키 저장 배지는 합성 데이터다. 실제 키를 입력·조회하지 않았다.
- `review.png`: 후보 검토와 직접 번역 편집.
- `settings.png`: 모델·직접 추론 설정·저장되지 않은 변경 상태.
- `run.png`: 추론·요청 수·비용의 실행 전 요약. 번역 시작 버튼은 누르지 않았다.

## 파일

| 이미지 | 크기 | SHA-256 |
| --- | --- | --- |
| review.png | 1440×980, 140,144 bytes | `053e732c63d336b150b20af6a8ba2e404e23c52fa498c3dd0f1b70494c8da96e` |
| settings.png | 1440×980, 113,694 bytes | `9bcaee9d3a0f7963bf23c7b99f3fd7338f3e45ef361f5eaa16932ed9d189cb6e` |
| run.png | 1440×980, 129,205 bytes | `57a755adc271864581154dcdc631e6b7dbcb5f5aff3865a3f8f18e6cee84a597` |

현재 저장소의 서비스 소개용으로 이 세 이미지와 이 문서만 추적한다. 일반 screenshot·trace·검증 cache는 `output/`에서 Git 제외한다. 버전이나 화면이 바뀌면 최신 UI를 합성 데이터로 다시 캡처하고, 원문/키/개인 경로가 없는지 직접 확인한다.
