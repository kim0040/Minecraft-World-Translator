"""Launch the real desktop entry against a fixture world."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_release_fixtures import compound, nbt_bytes, string, write_region

PY = sys.executable


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        raw = b'{"data":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        payload = json.loads(body["messages"][1]["content"])
        translated = {key: ("Hola sign" if text == "Hello sign" else text) for key, text in payload.items()}
        raw = json.dumps({"choices": [{"message": {"content": json.dumps(translated)}}]}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def start_server() -> tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address[:2]
    return server, f"http://{host}:{port}/v1"


def hashes(world: Path) -> dict[str, str]:
    from mwt.safety import iter_data_files

    return {
        path.relative_to(world).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in iter_data_files(world)
    }


def listening(pid: int) -> str:
    completed = subprocess.run(
        ["lsof", "-nP", "-a", "-p", str(pid), "-iTCP", "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
    )
    return "\n".join(line for line in completed.stdout.splitlines() if str(pid) in line)


def exchange(proc: subprocess.Popen[str], message: dict | None = None) -> dict:
    if message is not None:
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()
    assert proc.stdout is not None
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError(proc.stderr.read() if proc.stderr else "desktop entry closed stdout")
    return json.loads(line)


def main() -> None:
    server, base_url = start_server()
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp = Path(temp_dir)
            world = tmp / "world"
            region = world / "region" / "r.0.0.mca"
            write_region(region, {0: (2, nbt_bytes(compound("sign", string("Text1", '{"text":"Hello sign"}'))), False)})
            original = hashes(world)
            env = os.environ.copy()
            env.update({"POMI_API_KEY": "desktop-test-key", "POMI_API_BASE": base_url, "POMI_MODEL": "fixture"})
            proc = subprocess.Popen(
                [
                    PY,
                    "-m",
                    "mwt.desktop_entry",
                    "--jsonl",
                    "--report-dir",
                    str(tmp / "reports"),
                    "--data-dir",
                    str(tmp / "userdata"),
                ],
                cwd=ROOT,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            try:
                hello = exchange(proc)
                assert hello["type"] == "system.hello"
                assert hello["payload"]["localhostServer"] is False
                assert hello["payload"]["productName"] == "PomiTranslate"
                assert listening(proc.pid) == ""
                scan = exchange(
                    proc,
                    {"v": 1, "id": "scan", "type": "scan.start", "payload": {"worldDir": str(world)}},
                )
                assert scan["payload"]["dryRun"] is True
                assert scan["payload"]["candidateCount"] > 0
                assert scan["payload"]["localhostServer"] is False
                assert "Back up your world" in scan["payload"]["preTranslate"]
                assert hashes(world) == original
                translated = exchange(
                    proc,
                    {
                        "v": 1,
                        "id": "translate",
                        "type": "translate.start",
                        "payload": {"worldDir": str(world), "fingerprint": scan["payload"]["fingerprint"]},
                    },
                )
                assert translated["payload"]["status"] == "completed"
                assert hashes(world) != original
                restored = exchange(
                    proc,
                    {"v": 1, "id": "restore", "type": "restore.start", "payload": {"worldDir": str(world)}},
                )
                assert restored["payload"]["status"] == "restored"
                assert hashes(world) == original
            finally:
                proc.kill()
                proc.wait(timeout=5)
        print("DESKTOP_ENTRY_PASSED")
        print("hello_protocol", hello["type"])
        print("scan_candidate_count", scan["payload"]["candidateCount"])
        print("localhost_server", False)
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
