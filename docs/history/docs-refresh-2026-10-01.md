# 문서·라이선스·진행 저장 — 2026-10-01

## 요청과 변경

사용자가 미완 작업 기록, 서비스 README·스크린샷·사용법·기여자·MIT 검토, 문서 최신화·파일 정리·Git 제외·commit/push를 요청했다. 이어 개인 사용을 위해 대학생이 만든 프로젝트라는 배경과 면책·타 라이선스 조건 고려를 요청했다.

- 한국어 root README를 서비스 소개·사용법·현재 지원 범위 중심으로 다시 작성했다. 영문·일문·중문 소개를 같은 범위로 갱신하고 기존 한국어 문서는 단일 README로 안내한다.
- contributor/문의는 김현민, mini0227kim@gmail.com이다. 개인 시간·제한된 예산의 프로젝트라는 배경을 기록하고 유료 지원/복구/보상 약정과 구분했다.
- docs/user-guide, development, privacy, disclaimer, CONTRIBUTING과 문서 목차를 추가했다. 적용 법률이 허용하는 범위의 보증 부인·책임 제한이며 MIT에 새 사용 제한을 추가하지 않는다.
- 기존 MIT를 유지하고 기존 copyright 식별자를 보존했다. 원래 허락·보증/책임 본문은 변경하지 않았다. THIRD_PARTY_NOTICES와 legal 목록/검토에 MPL·Unicode·PyInstaller 예외·Python/native·플랫폼 미확인·API 비용·Minecraft/맵 권리를 기록했다.
- 날짜별10개 기록을 docs/history로 모았고 과거 증거를 삭제하지 않았다. 최신 상태와 미완 작업의 기준 문서는 current-state와 follow-up-work다. 기존 remaining-work 링크는 짧은 안내로 유지한다.
- 현재 실제 제품 UI를 합성 backend로 캡처한 review/settings/run 이미지3장을 docs/images에 추적한다. 실제 key/world/유료 호출은 사용하지 않았고 이미지의 합성 데이터·제한을 설명한다.
- output·trace·report·world·DB·key는 Git 제외다. 일반 source/lockfile/합성 fixture 코드는 유지한다. runtime 모듈·CLI entry/legacy launcher는 이동하지 않았다.
- 지원 표의 문서 문구와 mwt/support_matrix.py renderer를 함께 맞췄다. fixture PASS를 새로 만든 것이 아니며 지원 판정 row는 바꾸지 않았다.

## 이번 확인

- git diff --check PASS.
- 저장소 사용자/개발/상태/이력 문서의 로컬 링크 누락0.
- README의 제품명·부제·비공식 관계·백업·API 비용·자체 결제 없음 필수 원문 모두 존재.
- 기록된 support row를 다시 렌더링했을 때 support-matrix 문서와 동일; 새로운 Minecraft fixture 실행이 아님.
- MIT 본문은 copyright 이름 병기 외에 기존 파일과 동일.
- README를 Pandoc GFM→HTML로 렌더하고 실제 Chrome에서 확인. 워드마크+서비스 이미지3개 모두 load 완료, 세 원본 화면도 직접 점검.
- 변경 파일 credential/private-key 패턴 검출0, runtime artifact 후보0. 합성 소개용 PNG3개만 의도적으로 포함. 패턴 검사가 완전한 비밀 검출 보장은 아니다.
- .pomi-reports/output/test-results/worlds/SQLite/region/master.key ignore 규칙을 확인.
- 원격 fetch 후 커밋 전 HEAD...origin/main의 ahead/behind 0/0. 사용자가 승인한 기존 추론/사이드바/provider/ZIP WIP를 보존해 이번 진행 저장에 함께 포함한다.

## 미완과 배포 경계

관련 제품 검증은 [직전 UI/UX 증거](settings-ux-2026-10-01.md)를 따른다. 이번 문서 작업 때문에 전체 앱 검사·sidecar/native 재빌드·실제 유료 API를 반복하지 않았다. 이미지 capture는 installer/actual provider 검증을 대체하지 않는다. 추가 API 비용$0.

Cargo 외부525개 중333 metadata 확인·192 미확인, npm 설치72·Python 설치14 metadata를 기록했다. metadata는 최종 SBOM/원문 notice 동봉 검증이 아니다. 소스 MIT 유지의 알려진 충돌은 발견하지 못했으며 **정식 바이너리 배포의 license 완료 판정은 보류**한다. [LEGAL-01과 기타 gate](../follow-up-work.md)를 따른다.

사용자 요청의 이번 commit/push는 **checkpoint**이고 Phase2 완료 commit이 아니다. Phase2 진행 중/Phase3 미시작/release-ready 아님. 불필요한 CI를 막는 [skip ci]를 사용한다. 태그·공개 release·서명·사용자 world upload는 수행하지 않는다.
