#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
STAMP_FILE="$VENV_DIR/.requirements_installed"

pause_on_error() {
  echo
  read -r -p "문제가 발생했습니다. Enter를 누르면 종료합니다. " _
}

trap 'pause_on_error' ERR

echo "[Minecraft World Translator] 준비 중..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3를 찾을 수 없습니다. Python 3.11+를 먼저 설치하세요."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[1/4] 가상환경 생성"
  python3 -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

if [ ! -f "$STAMP_FILE" ] || [ "$SCRIPT_DIR/requirements.txt" -nt "$STAMP_FILE" ]; then
  echo "[2/4] 의존성 설치"
  python3 -m pip install --upgrade pip
  python3 -m pip install -r "$SCRIPT_DIR/requirements.txt"
  touch "$STAMP_FILE"
else
  echo "[2/4] 의존성 확인 완료"
fi

echo "[3/4] 웹 UI 실행 준비"
ARGS=()
if [ "${MWT_SKIP_OPEN:-0}" != "1" ]; then
  ARGS+=(--open-browser)
fi

echo "[4/4] 웹 UI 시작"
cd "$SCRIPT_DIR"
exec python3 "$SCRIPT_DIR/webui_server.py" "${ARGS[@]}"
