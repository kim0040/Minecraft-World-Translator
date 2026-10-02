# 실제 DeepSeek API 검증 — 2026-10-02

사용자가 유료 API 테스트를 승인했다. 대상 source는 `694a91a`, 모델은 저장된 `deepseek/deepseek-v4.1-flash`, reasoning은 `default`다. 제품 기본 모델을 변경하지 않고 격리된 설정과 합성 월드를 사용했다. 테스트 전용 출력 제한은 4096 tokens, 재시도는 0회, 생성 요청은 정확히 1회다.

## 확인된 결과

- 현재 Python JSONL/core의 scan → estimate → 실제 OpenRouter 번역 → write → reopen → backup restore를 통과했다. 합성 후보 3개 모두 번역, 실패·경고 0개, 변경 파일 1개.
- 표지판·JSON tellraw·SNBT title의 한국어 결과를 재조회했다. 명령 구조·색상·`%s`·번역 대상이 아닌 identifier가 보존됐다.
- restore 후 월드 전체 파일의 baseline SHA-256이 일치했다. 기존 사용자 설정·credential DB·master key의 hash도 그대로다. 비밀·월드·DB·출력은 Git에 추가하지 않았다.
- 실제 모델 catalog GET은 464개를 반환했고 모델의 가격·context·reasoning 정보를 받았다. 동일 scan에서 다른 catalog 모델 `deepseek/deepseek-v4-flash`로 설정 저장 후 비용이 해당 API 가격으로 자동 재계산됐으며 원래 모델로 되돌려 확인했다. 다른 모델로 생성 요청은 하지 않았다.
- 브라우저 fixture는 실제 catalog/기록된 estimate를 사용해 모델 목록 464개와 설정의 다른 모델 저장을 확인했다. 실제 native bridge·브라우저 비용 표시까지의 전체 E2E는 확인하지 않았다.
- desktop-entry mock 사전 검사 PASS. 최신 native bundle·게임 로드·모든 제공사 검증으로 확대하지 않는다.

## 남은 비용 정확도 문제

예상 비용은 $0.00005355–$0.00010710, 실제 응답의 보고 비용은 **$0.000219114**로 예상 상한의 약 2.05배였다. 실제 입력 398/output 289 tokens이며 output에는 reasoning 247 tokens가 포함됐다. 출력 추정은 78 tokens였다. 모델 catalog 단가와 실제 응답에서 역산한 단가도 달랐다. 따라서 자동 재계산 동작은 확인했지만 비용 범위의 정확성은 미완이다.

즉시 조회한 계정 usage delta는 0으로 나왔으므로 이를 무과금 근거로 사용하지 않는다. 위 비용은 생성 응답의 provider-reported cost이며 최종 청구서 확인은 아니다. reasoning 토큰과 실제 라우팅 가격·usage 비교를 반영하는 작업을 [추후 작업](../follow-up-work.md)에 남긴다.

비밀 없는 원시 검증 출력은 테스트 당시 `/private/tmp/pomi-deepseek-e2e-2nkmkql8/summary.json`에 저장했다. 임시 파일은 장기 보존을 보장하지 않으며 이 문서는 요약 증거다.
