# Documentation screenshots / 소개용 화면

2026-10-02 현재 Svelte 제품 UI를 macOS의 Playwright/Chromium으로 한국어·영어·일본어에서 새로 캡처했습니다. 세 언어 모두 동일한 합성 fixture와 1440×980 viewport, light theme을 사용했습니다. 화면을 다시 그린 목업이 아닙니다. UI의 번역된 버튼·제목·입력 안내와 언어별 수동 번역 예시를 확인했습니다.

Captured from the current Svelte UI with synthetic data. These are browser screenshots, not evidence of native installation, actual provider usage or support for a specific model. Chinese documentation uses the English UI images because Chinese UI is not implemented.

- Entry: `/tests/frontend/preview.html?scenario=review&model=deepseek/deepseek-v4.1-flash&locale={ko|en|ja}&theme=light`.
- `review.png`: candidate review / 후보 검색·직접 번역 편집.
- `settings.png`: provider, model and custom reasoning / 제공사·모델·직접 추론·저장되지 않은 변경.
- `run.png`: pre-run confirmation / 추론·요청 수·추정 비용·외부 전송 안내. 번역 시작은 누르지 않았습니다.
- Source world names, paths, models, prices and saved-key badges are synthetic. No real keys or private worlds were read. Foreign source strings and technical IDs remain original.
- Capture waited for fonts, page transitions and save notifications. External requests0, paid requests0, scan/translation/restore jobs0; viewport overflow0. Three earlier Korean URLs are refreshed aliases of this capture.

## Language gallery / 언어별 화면

| UI language | Review / 검토 | Settings / 설정 | Run / 실행 |
| --- | --- | --- | --- |
| 한국어 | [화면](locales/ko/review.png) | [화면](locales/ko/settings.png) | [화면](locales/ko/run.png) |
| English | [Screen](locales/en/review.png) | [Screen](locales/en/settings.png) | [Screen](locales/en/run.png) |
| 日本語 | [画面](locales/ja/review.png) | [画面](locales/ja/settings.png) | [画面](locales/ja/run.png) |
| 简体中文文档 | [English UI](locales/en/review.png) | [English UI](locales/en/settings.png) | [English UI](locales/en/run.png) |

## Capture manifest / 파일 정보

All screenshots are 1440×980. Source-input hash, aliases and PNG hashes are recorded in [manifest.json](manifest.json). Regeneration commands and scope are in [localization.md](../localization.md).

| File | UI locale | Bytes | SHA-256 |
| --- | --- | --- | --- |
| locales/ko/review.png | ko | 150451 | `308f0bcef32db1ebc18c2e14b4fa003c3d344705fad58f55d015b14c521ff549` |
| locales/ko/settings.png | ko | 119191 | `d731f7cc734739c305695f662b26c6062d731003185e9f3e90b0722e0b733d6e` |
| locales/ko/run.png | ko | 138426 | `d00d4a60f8e2c00ed056df41ca62c985e2335050f3b5d75723c6dcc9033f825d` |
| locales/en/review.png | en | 155867 | `4ca560e6d1261acf8f8490118f656e34cd462a8e0a2776c299f8b36c53a00a3e` |
| locales/en/settings.png | en | 121308 | `bf45a6ca623afe376f977432760474e887f768074d3bbc44637b12d9f7c42948` |
| locales/en/run.png | en | 140993 | `e1e6019b0ee68e6622a7ab08ea6e5ef18bb30720d2e3274c3d7ef46d6c5b53bd` |
| locales/ja/review.png | ja | 172428 | `58702a39079cb9148ec433ba10de4af7f76a5b08316b1f44898d288bae7c0dee` |
| locales/ja/settings.png | ja | 132261 | `74b4d411dd5c9325d7ae11f59458381ff0ba80b0ddd0c63e7d5e7b3322712f66` |
| locales/ja/run.png | ja | 161276 | `3c82f56913adb24f1bb3d233e15d149a58b4c2d72c96d9410c6ac9cdb399bba6` |

`review.png`, `settings.png`, `run.png` at this directory's root are byte-identical aliases of `locales/ko/` for existing links. General screenshots, traces, reports, worlds, credentials and caches stay ignored under `output/`. Only these curated synthetic documentation screenshots are intentionally tracked.
