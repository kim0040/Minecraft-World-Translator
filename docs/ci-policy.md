# CI 실행 정책

일상적인 검증은 로컬에서 수행한다. GitHub Actions는 아래 조건에서만 실행한다.

| 변경 / 이벤트 | Python CI | Desktop installer | Release gate |
| --- | --- | --- | --- |
| 일반 feature branch push | 실행 안 함 | 실행 안 함 | 실행 안 함 |
| main push 또는 main 대상 PR: Python 파일 / requirements.txt | 실행 | 실행 안 함 | 실행 안 함 |
| main push 또는 main 대상 PR: ci.yml | 실행 | 실행 안 함 | 실행 안 함 |
| 문서 / 이미지 / Svelte / TypeScript / frontend·browser 테스트만 변경 | 실행 안 함 | 실행 안 함 | 실행 안 함 |
| 수동 실행 | 선택한 workflow만 실행 | 기본 Linux, all 선택 시 3 OS | 명시적 실행 |
| v* 태그 push | 실행 안 함 | 3 OS 빌드 | 실행 |

Python 코드가 섞인 변경은 Python CI가 실행된다. `tests/frontend/**`와 `tests/browser/**`는 Python CI 실행 조건에 포함하지 않는다. 새 Python 테스트는 `**/*.py` 조건으로 포함된다. 동시에 실행되는 동일 ref의 오래된 검증은 취소한다.

## 로컬 검증

- UI: `pnpm check`, `pnpm test:frontend`, `pnpm test:browser`, 필요한 screenshot 검사.
- Python: 변경 범위에 해당하는 `.venv/bin/python` 회귀 테스트.
- Rust: `cargo test --locked --manifest-path src-tauri/Cargo.toml`.
- 앱 패키징은 웹/코어 검증 후 마지막 native gate에서 수행한다.

PR에 필수 status check를 설정한다면 paths 때문에 실행되지 않는 workflow를 모든 PR에 무조건 요구하지 않는다. branch protection의 실제 설정은 별도 확인 대상이다.

## 최종 gate

릴리스 후보에서 `desktop-build`를 수동 `all`로 실행하여 Linux/macOS/Windows 패키지를 검증한다. 서명·clean-machine·실제 앱 workflow 검증은 별도로 남아 있다. 현재 release workflow는 공개 배포를 수행하지 않는 서명 준비 gate다. 태그 push나 공개 release는 사용자 승인 없이 수행하지 않는다.

일반 CI 정책 수정 확인을 위해 유료 runner를 새로 실행하지 않는다. 조건 검사는 로컬에서 수행하며, 원격 실행 성공과 구분해 기록한다.
