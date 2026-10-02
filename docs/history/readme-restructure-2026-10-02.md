# README 재구성 — 2026-10-02

사용자가 README 상단을 서비스 소개와 할 수 있는 일 중심으로 재구성하고, "대학생 김현민" 개인 프로젝트 배경 안내를 상단에서 기여자 절로 옮겨 읽는 입장에서 거부감 없게 다듬으며, 메인 README를 영어로 전환하고 한국어 바로가기를 제공하고, 기타 문서의 같은 문구를 정리하고, Git 추적 민감정보를 점검한 뒤 commit/push를 요청했다. 코드 수정이 아닌 문서 수정이다.

- root README를 영어 메인으로 전환하고 상단에 서비스 소개와 할 수 있는 일 요약(스캔·검토·AI 번역·백업/복원)을 배치했다. 한국어판은 docs/README.ko.md로 옮기고 기존 한국어 링크를 유지했다.
- docs/README.en.md는 기존 영어 링크용 진입점으로 정리하고, ja/zh README의 언어 링크와 상단 요약을 새 구조로 맞췄다. docs/README.md 언어별 소개 링크도 갱신했다.
- 개인 프로젝트 배경 안내를 README 상단에서 기여자·문의 절로 옮기고, 개발 중이라 미완성·예상치 못한 문제가 있을 수 있으니 지원 범위 확인과 백업을 권하는 문장으로 다듬었다. disclaimer·CONTRIBUTING의 같은 배경 문구도 같은 어조로 조정했다.
- README의 Phase 문구를 current-state 기준(Phase2 개발 환경 gate 완료 / Phase3 진행 중 / release-ready 아님)으로 맞췄다.
- Git 추적 파일277개와 전체 이력을 credential/private-key 패턴으로 점검했고 실제 비밀 검출은 없었다. .env.example은 빈 placeholder, 테스트 값은 synthetic fixture, 소개 screenshot3장은 문서화된 SHA-256과 일치하며 키·개인 경로가 없음을 직접 확인했다. 제거할 추적 파일은 없었다.
- 문서 전용 변경이라 Python/frontend/browser/Rust/native/API 검사를 실행하지 않았다. 추가 API 비용$0.
- 이번 commit/push는 checkpoint이며 Phase 완료가 아니다. Phase2 개발 환경 gate 완료/Phase3 진행 중/release-ready 아님. 불필요한 CI를 막는 [skip ci]를 사용한다. 태그·공개 release·서명·사용자 world upload는 수행하지 않는다.
