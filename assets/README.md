# PomiTranslate 에셋

제품명은 PomiTranslate, 부제는 World Translator for Minecraft, 마스코트는 Pomi다. 현재 제품·legacy UI·문서에 사용하는 작은 브랜드/기능 안내 에셋을 보관한다. 큰 생성 원본·다른 크기·시즌별 실험은 개발 workspace에 보존하며 제품 Git에 추가하지 않는다.

- `icons/app/`: 방향 A와 앱 아이콘 master. 실제 Tauri 입력은 `src-tauri/icons/`에 있다.
- `brand/`: 워드마크·심볼·공유 이미지.
- `mascot/`: Pomi 이미지. 실제 UI용 파일은 `public/images/`에 있다.
- `icons/feature/`: 기존 기능 SVG.
- `illustrations/docs/`: 한국어·영어·일본어·중국어 간체 스캔/백업/API/미지원 안내 카드. 서비스 소개 screenshot은 `docs/images/`에서 관리한다.

## 언어별 문자 에셋

공유 이미지 4개와 안전 안내 카드 16개는 같은 문구 원본 [`localization.json`](localization.json)에서 SVG로 생성하고 PNG로 렌더합니다. 제품명·Pomi·공식 부제는 공통으로 유지하며, 설명과 안전 안내는 각 문서 언어로 제공합니다. 중국어 간체는 문서 언어이고 현재 UI는 ko/en/ja입니다.

| 언어 | 공유 이미지 | 스캔 | 백업 | API 전송·비용 | 미지원 압축 |
| --- | --- | --- | --- | --- | --- |
| 한국어 | [공유](brand/social/og_default_ko_v1.png) | [스캔](illustrations/docs/doc_scan_first_ko_v1.png) | [백업](illustrations/docs/doc_backup_first_ko_v1.png) | [API](illustrations/docs/doc_api_notice_ko_v1.png) | [미지원](illustrations/docs/doc_unsupported_ko_v1.png) |
| English | [Share](brand/social/og_default_en_v1.png) | [Scan](illustrations/docs/doc_scan_first_en_v1.png) | [Backup](illustrations/docs/doc_backup_first_en_v1.png) | [API](illustrations/docs/doc_api_notice_en_v1.png) | [Unsupported](illustrations/docs/doc_unsupported_en_v1.png) |
| 日本語 | [共有](brand/social/og_default_ja_v1.png) | [スキャン](illustrations/docs/doc_scan_first_ja_v1.png) | [バックアップ](illustrations/docs/doc_backup_first_ja_v1.png) | [API](illustrations/docs/doc_api_notice_ja_v1.png) | [未対応](illustrations/docs/doc_unsupported_ja_v1.png) |
| 简体中文 | [分享](brand/social/og_default_zh_v1.png) | [扫描](illustrations/docs/doc_scan_first_zh_v1.png) | [备份](illustrations/docs/doc_backup_first_zh_v1.png) | [API](illustrations/docs/doc_api_notice_zh_v1.png) | [不支持](illustrations/docs/doc_unsupported_zh_v1.png) |

각 PNG 옆에 같은 이름의 SVG 원본이 있습니다. 언어 없는 기존 안내 카드 4개는 이번 한국어 출력과 동일한 호환 별칭입니다. API 안내는 **선택한 원문과 번역 지시**가 제공사로 전송된다는 뜻이며 번역 완료 후 텍스트를 보내는 기능으로 설명하지 않습니다. 워드마크의 고유 브랜드명·공식 부제와 글자 없는 아이콘/마스코트는 공통입니다.

재생성·문구 규칙은 [현지화 관리](../docs/localization.md), 파일 hash는 [manifest](localization-manifest.json)를 따릅니다.

Pomi 래스터 그림은 프로젝트를 위해 생성·편집한 에셋이며 AI 생성 이미지의 독점적 저작권을 보장한다고 주장하지 않는다. SVG 워드마크는 Avenir Next/Nunito/system font 이름을 참조하지만 글꼴 binary를 배포하지 않는다. 제3자 글꼴을 새로 포함할 때는 그 별도 라이선스를 확인한다.

Minecraft 게임 파일·공식 로고·맵·리소스팩을 프로젝트 브랜드 에셋으로 제공하지 않는다. 실제 provenance/상표/글꼴·생성 조건은 정식 배포 전 [라이선스 검토](../docs/legal/license-review.md)의 gate에서 확인한다. 외부 에셋을 추가하면 출처·원래 라이선스를 보존한다.
