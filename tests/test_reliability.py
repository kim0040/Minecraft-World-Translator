"""A translation run must never report success it did not achieve.

Reproduces the failures found in the first end-to-end review: a provider outage that used to
finish as "completed" with half the world untouched, unreadable chunks skipped in silence,
and a translation that dropped Minecraft formatting codes.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import threading
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nbt import nbt  # noqa: E402

from mc_world_translator import DEFAULT_CONFIG, MAX_CONSECUTIVE_REQUEST_FAILURES, WorldTranslator, merge_nested  # noqa: E402
from mwt.region import RegionFile  # noqa: E402
from mwt.safety import world_fingerprint  # noqa: E402

RESULTS: list[str] = []


class Provider:
    """Scriptable OpenAI-compatible endpoint. ``script`` maps request number -> behaviour."""

    def __init__(self) -> None:
        self.requests = 0
        self.mode = "ok"
        self.fail_after = 10**9
        self.poison = ""
        self.drop_section_sign = False
        self.lock = threading.Lock()
        provider = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                self._send(200, {"data": []})

            def do_POST(self) -> None:  # noqa: N802
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                with provider.lock:
                    provider.requests += 1
                    number = provider.requests
                payload = json.loads(body["messages"][1]["content"])
                if provider.mode == "unauthorized":
                    return self._send(401, {"error": "bad key"})
                if provider.mode == "always429" or number > provider.fail_after:
                    return self._send(429, {"error": "rate limited"}, {"Retry-After": "0"})
                if provider.poison and any(provider.poison in text for text in payload.values()):
                    return self._send(400, {"error": "rejected"})
                out = {}
                for key, text in payload.items():
                    translated = "[번역] " + text
                    if provider.drop_section_sign:
                        translated = translated.replace("§", "")
                    out[key] = translated
                self._send(
                    200,
                    {
                        "choices": [{"message": {"content": json.dumps(out, ensure_ascii=False)}}],
                        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
                    },
                )

            def _send(self, status: int, payload: dict, headers: dict | None = None) -> None:
                raw = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                for name, value in (headers or {}).items():
                    self.send_header(name, value)
                self.end_headers()
                self.wfile.write(raw)

            def log_message(self, *args) -> None:
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        host, port = self.server.server_address[:2]
        self.base_url = f"http://{host}:{port}/v1"


def nbt_bytes(*texts: str) -> bytes:
    root = nbt.NBTFile()
    root.name = ""
    for index, text in enumerate(texts):
        sign = nbt.TAG_Compound(name=f"sign{index}")
        sign.tags.append(nbt.TAG_String(name="Text1", value=json.dumps({"text": text})))
        root.tags.append(sign)
    buffer = io.BytesIO()
    root.write_file(buffer=buffer)
    return buffer.getvalue()


def make_world(base: Path, name: str, files: dict[str, list[str]], *, corrupt_chunk: bool = False) -> Path:
    world = base / name
    for filename, texts in files.items():
        region = RegionFile.empty()
        region.put_nbt(0, nbt_bytes(*texts), compression=2)
        if corrupt_chunk:
            garbage = zlib.compress(b"\x0a\x00\x00not-valid-nbt")
            region.put_raw_record(1, (len(garbage) + 1).to_bytes(4, "big") + bytes([2]) + garbage)
        path = world / "region" / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        data, _ = region.build()
        path.write_bytes(data)
    (world / "level.dat").write_bytes(b"\x1f\x8b")
    return world


def hashes(world: Path) -> dict[str, str]:
    return {
        path.relative_to(world).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(world.rglob("*.mca"))
    }


def make_translator(world: Path, provider: Provider, report: Path, **runtime) -> WorldTranslator:
    config = merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": False,
            "report_path": str(report),
            "inherit_translate_py": False,
            "batch_size": runtime.pop("batch_size", 40),
            "api": {"provider": "openai", "api_key": "test-key", "model": "fixture", "base_url": provider.base_url},
            "runtime": {
                "checkpoint_enabled": True,
                "checkpoint_path": str(report.with_suffix(".checkpoint.json")),
                "scan_plan_id": "a" * 64,
                "expected_world_fingerprint": world_fingerprint(world),
                **runtime,
            },
        },
    )
    translator = WorldTranslator(config)
    translator.translator.sleep = lambda seconds: None
    return translator


def record(name: str) -> None:
    RESULTS.append(name)
    print(f"PASS {name}")


def test_outage_is_not_reported_as_completed(tmp: Path) -> None:
    provider = Provider()
    provider.mode = "always429"
    world = make_world(tmp, "outage", {f"r.{i}.0.mca": [f"Hello number {i}"] for i in range(4)})
    before = hashes(world)
    report = make_translator(world, provider, tmp / "outage.json").run()
    assert report["status"] == "needs_retry", report["status"]
    assert hashes(world) == before, "an outage must leave the world untouched"
    assert report["errors"][0]["code"] == "RATE_LIMITED"
    assert provider.requests <= MAX_CONSECUTIVE_REQUEST_FAILURES, provider.requests
    assert not (world / ".pomi-backups").exists(), "nothing was written, so nothing needs a backup"
    record("reliability.outage_needs_retry")


def test_bad_key_stops_at_once(tmp: Path) -> None:
    provider = Provider()
    provider.mode = "unauthorized"
    world = make_world(tmp, "badkey", {"r.0.0.mca": ["Hello there"], "r.1.0.mca": ["Another line"]})
    report = make_translator(world, provider, tmp / "badkey.json").run()
    assert report["status"] == "failed"
    assert report["errors"][0]["code"] == "AUTH_FAILED"
    assert provider.requests == 1, "a rejected key must not be retried"
    record("reliability.bad_key_fails_fast")


def test_single_bad_string_is_reported(tmp: Path) -> None:
    provider = Provider()
    provider.poison = "POISON"
    world = make_world(tmp, "poison", {"r.0.0.mca": ["Hello there", "POISON line", "Front line"]})
    before = hashes(world)
    report = make_translator(world, provider, tmp / "poison.json").run()
    assert report["status"] == "needs_retry"
    assert hashes(world) == before, "by default nothing is written while strings are missing"
    assert report["translation"]["failed"] == 1
    assert report["translation_failures"][0]["source"] == "POISON line"

    skipping = make_translator(world, provider, tmp / "poison-skip.json", on_translation_failure="skip").run()
    assert skipping["status"] == "partial"
    assert skipping["translation"] == {
        "unique": 3, "translated": 2, "failed": 1, "kept_original": 0, "unchanged": 0,
    }
    written = RegionFile.read(world / "region" / "r.0.0.mca").chunks[0].raw_nbt
    assert "[번역] Hello there".encode() in written and b"POISON line" in written
    record("reliability.failed_string_reported")


def test_retry_only_pays_for_what_is_missing(tmp: Path) -> None:
    provider = Provider()
    provider.fail_after = 1
    files = {f"r.{i}.0.mca": [f"Distinct line {i} a", f"Distinct line {i} b"] for i in range(3)}
    world = make_world(tmp, "resume", files)
    before = hashes(world)
    first = make_translator(world, provider, tmp / "resume.json", batch_size=2).run()
    assert first["status"] == "needs_retry"
    assert hashes(world) == before
    assert (tmp / "resume.checkpoint.json").is_file(), "translated batches must survive for the retry"
    requests_after_outage = provider.requests

    provider.fail_after = 10**9
    provider.requests = 0
    second = make_translator(world, provider, tmp / "resume.json", batch_size=2, resume_from_checkpoint=True).run()
    assert second["status"] == "completed", second
    assert provider.requests == 2, f"only the two untranslated batches should be requested, got {provider.requests}"
    assert requests_after_outage > 1
    assert second["translation"]["translated"] == 6
    assert not (tmp / "resume.checkpoint.json").exists()
    record("reliability.retry_reuses_paid_work")


def test_dropped_formatting_code_is_kept_original(tmp: Path) -> None:
    provider = Provider()
    provider.drop_section_sign = True
    world = make_world(tmp, "codes", {"r.0.0.mca": ["§6Golden door", "Plain door"]})
    report = make_translator(world, provider, tmp / "codes.json").run()
    assert report["status"] == "completed"
    assert report["translation"]["kept_original"] == 1
    assert report["kept_original_samples"] == ["§6Golden door"]
    written = RegionFile.read(world / "region" / "r.0.0.mca").chunks[0].raw_nbt
    assert "[번역] Plain door".encode() in written
    assert b"Golden door" in written and "[번역] ".encode() + b"\\u00a76" not in written
    assert "[번역] Golden".encode() not in written
    record("reliability.formatting_codes_protected")


def test_unreadable_chunk_is_reported(tmp: Path) -> None:
    provider = Provider()
    world = make_world(tmp, "corrupt", {"r.0.0.mca": ["Hello there"]}, corrupt_chunk=True)
    scan_config = merge_nested(
        DEFAULT_CONFIG,
        {
            "world_dir": str(world),
            "dry_run": True,
            "report_path": str(tmp / "corrupt-scan.json"),
            "inherit_translate_py": False,
            "api": {"provider": "openai", "api_key": "", "model": "fixture", "base_url": provider.base_url},
        },
    )
    scan = WorldTranslator(scan_config).run()
    assert scan["status"] == "completed" and scan["candidate_text_count"] == 1
    warning = next(item for item in scan["warnings"] if item["code"] == "chunk_unreadable")
    assert warning["count"] == 1 and warning["file"] == "region/r.0.0.mca"

    garbage = zlib.compress(b"\x0a\x00\x00not-valid-nbt")
    report = make_translator(world, provider, tmp / "corrupt.json").run()
    assert report["status"] == "completed"
    assert any(item["code"] == "chunk_unreadable" for item in report["warnings"])
    assert RegionFile.read(world / "region" / "r.0.0.mca").chunks[1].payload == garbage, "the bad chunk must be kept as it was"
    record("reliability.unreadable_chunk_reported")


def test_usage_is_counted(tmp: Path) -> None:
    provider = Provider()
    world = make_world(tmp, "usage", {"r.0.0.mca": ["Hello there"]})
    report = make_translator(world, provider, tmp / "usage.json").run()
    assert report["usage"]["prompt_tokens"] == 100 and report["usage"]["completion_tokens"] == 50
    record("reliability.usage_counted")


def main() -> None:
    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        for test in (
            test_outage_is_not_reported_as_completed,
            test_bad_key_stops_at_once,
            test_single_bad_string_is_reported,
            test_retry_only_pays_for_what_is_missing,
            test_dropped_formatting_code_is_kept_original,
            test_unreadable_chunk_is_reported,
            test_usage_is_counted,
        ):
            test(tmp)
    print("RELIABILITY_PASSED")


if __name__ == "__main__":
    main()
