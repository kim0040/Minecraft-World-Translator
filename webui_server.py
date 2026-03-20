from __future__ import annotations

import argparse
import json
import mimetypes
import threading
import uuid
import webbrowser
from copy import deepcopy
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from llm_backends import PROVIDER_SPECS, default_base_url
from mc_world_translator import (
    DEFAULT_CONFIG,
    STYLE_PRESETS,
    WorldTranslator,
    enhance_style_prompt_for_config,
    list_models_for_config,
    merge_nested,
    normalize_config,
)


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "webui"
CONFIG_BASE_PATH = BASE_DIR / "config.example.toml"
MAX_EVENTS = 400


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def ensure_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return default


def ensure_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ensure_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ensure_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = str(value).replace(",", "\n").splitlines()
    result: list[str] = []
    for item in items:
        text = ensure_str(item)
        if text:
            result.append(text)
    return result


def ensure_dict(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            ensure_str(key): ensure_str(item)
            for key, item in value.items()
            if ensure_str(key)
        }
    if value is None:
        return {}

    result: dict[str, str] = {}
    for line in str(value).splitlines():
        if "=" not in line:
            continue
        key, item = line.split("=", 1)
        key = key.strip()
        item = item.strip()
        if key:
            result[key] = item
    return result


def build_payload_config(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("config", payload)
    if not isinstance(raw, dict):
        raise ValueError("Invalid payload: `config` must be an object.")

    config = deepcopy(DEFAULT_CONFIG)

    api = raw.get("api", {})
    prompt = raw.get("prompt", {})
    scan = raw.get("scan", {})
    resource_pack = raw.get("resource_pack", {})
    runtime = raw.get("runtime", {})

    config["world_dir"] = ensure_str(raw.get("world_dir"))
    config["report_path"] = ensure_str(raw.get("report_path"))
    config["dry_run"] = ensure_bool(raw.get("dry_run"), False)
    config["backup"] = ensure_bool(raw.get("backup"), True)
    config["backup_suffix"] = ensure_str(raw.get("backup_suffix"), ".bak_translate") or ".bak_translate"
    config["batch_size"] = max(1, ensure_int(raw.get("batch_size"), 40))
    config["temperature"] = ensure_float(raw.get("temperature"), 0.3)
    config["inherit_translate_py"] = ensure_bool(raw.get("inherit_translate_py"), True)
    config["translate_py_path"] = ensure_str(raw.get("translate_py_path"), "./translate.py") or "./translate.py"

    provider = ensure_str(api.get("provider"), "comet").lower() or "comet"
    config["api"]["provider"] = provider
    config["api"]["api_key"] = ensure_str(api.get("api_key"))
    config["api"]["base_url"] = ensure_str(api.get("base_url"), default_base_url(provider))
    config["api"]["model"] = ensure_str(api.get("model"))
    config["api"]["request_timeout"] = max(10, ensure_int(api.get("request_timeout"), 120))

    config["prompt"]["target_language"] = ensure_str(prompt.get("target_language"), "한국어") or "한국어"
    style_preset = ensure_str(prompt.get("style_preset"), "neutral") or "neutral"
    config["prompt"]["style_preset"] = style_preset if style_preset in STYLE_PRESETS else "neutral"
    config["prompt"]["style_prompt"] = ensure_str(prompt.get("style_prompt"))
    config["prompt"]["custom_system_prompt"] = ensure_str(prompt.get("custom_system_prompt"))

    config["scan"]["region_dirs"] = ensure_list(scan.get("region_dirs")) or deepcopy(DEFAULT_CONFIG["scan"]["region_dirs"])
    config["scan"]["skip_patterns"] = ensure_list(scan.get("skip_patterns")) or deepcopy(
        DEFAULT_CONFIG["scan"]["skip_patterns"]
    )
    config["scan"]["translate_signs"] = ensure_bool(scan.get("translate_signs"), True)
    config["scan"]["translate_books"] = ensure_bool(scan.get("translate_books"), True)
    config["scan"]["translate_custom_names"] = ensure_bool(scan.get("translate_custom_names"), True)
    config["scan"]["translate_item_names"] = ensure_bool(scan.get("translate_item_names"), True)
    config["scan"]["translate_lore"] = ensure_bool(scan.get("translate_lore"), True)
    config["scan"]["translate_titles"] = ensure_bool(scan.get("translate_titles"), True)
    config["scan"]["translate_filtered_titles"] = ensure_bool(scan.get("translate_filtered_titles"), True)
    config["scan"]["translate_command_output"] = ensure_bool(scan.get("translate_command_output"), True)
    config["scan"]["skip_command_like_text"] = ensure_bool(scan.get("skip_command_like_text"), True)
    config["scan"]["component_translate_key_prefixes"] = ensure_list(scan.get("component_translate_key_prefixes"))
    config["scan"]["overrides"] = ensure_dict(scan.get("overrides"))

    config["resource_pack"]["enabled"] = ensure_bool(resource_pack.get("enabled"), False)
    config["resource_pack"]["zip_paths"] = ensure_list(resource_pack.get("zip_paths"))
    config["resource_pack"]["source_lang_files"] = ensure_list(resource_pack.get("source_lang_files")) or [
        "en_us.json",
        "zh_cn.json",
    ]
    config["resource_pack"]["target_lang_file"] = (
        ensure_str(resource_pack.get("target_lang_file"), "ko_kr.json") or "ko_kr.json"
    )
    config["resource_pack"]["skip_if_target_exists"] = ensure_bool(
        resource_pack.get("skip_if_target_exists"), False
    )

    config["runtime"]["checkpoint_enabled"] = ensure_bool(runtime.get("checkpoint_enabled"), True)
    config["runtime"]["checkpoint_path"] = ensure_str(runtime.get("checkpoint_path"))
    config["runtime"]["resume_from_checkpoint"] = ensure_bool(runtime.get("resume_from_checkpoint"), False)
    config["runtime"]["continue_on_file_error"] = ensure_bool(runtime.get("continue_on_file_error"), True)
    config["runtime"]["max_batch_retries"] = max(1, ensure_int(runtime.get("max_batch_retries"), 3))
    config["runtime"]["max_file_write_retries"] = max(1, ensure_int(runtime.get("max_file_write_retries"), 2))
    if config["runtime"]["resume_from_checkpoint"]:
        config["runtime"]["checkpoint_enabled"] = True

    return normalize_config(merge_nested(DEFAULT_CONFIG, config), CONFIG_BASE_PATH)


def summarize_config(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "provider": config["api"]["provider"],
        "world_dir": config["world_dir"],
        "report_path": config["report_path"],
        "backup": config["backup"],
        "dry_run": config["dry_run"],
        "inherit_translate_py": config["inherit_translate_py"],
        "translate_py_path": config["translate_py_path"],
        "model": config["api"]["model"],
        "base_url": config["api"]["base_url"],
        "request_timeout": config["api"]["request_timeout"],
        "api_key_present": bool(config["api"]["api_key"]),
        "target_language": config["prompt"]["target_language"],
        "style_preset": config["prompt"]["style_preset"],
        "resource_pack_enabled": config["resource_pack"]["enabled"],
        "resource_pack_zip_paths": config["resource_pack"]["zip_paths"],
        "resume_from_checkpoint": config["runtime"]["resume_from_checkpoint"],
        "checkpoint_path": config["runtime"]["checkpoint_path"],
    }


def discover_example_paths() -> dict[str, str]:
    translate_py_path = BASE_DIR.parent / "translate.py"
    sample_world_dir = BASE_DIR.parent / "Trip to BrennenBurg REMAKE"
    return {
        "translate_py_path": str(translate_py_path.resolve()) if translate_py_path.exists() else "",
        "world_dir": str(sample_world_dir.resolve()) if sample_world_dir.exists() else "",
    }


def provider_meta() -> list[dict[str, str]]:
    return [
        {
            "id": provider_id,
            "label": spec["label"],
            "default_base_url": spec["base_url"],
            "env_var": spec["env_var"],
        }
        for provider_id, spec in PROVIDER_SPECS.items()
    ]


class JobManager:
    def __init__(self) -> None:
        self.jobs: dict[str, dict[str, Any]] = {}
        self.lock = threading.Lock()

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        config = build_payload_config(payload)
        if not config["world_dir"]:
            raise ValueError("`world_dir` is required.")
        if not Path(config["world_dir"]).is_dir():
            raise ValueError(f"World directory does not exist or is not a directory: {config['world_dir']}")
        if not config["dry_run"]:
            if not config["api"]["api_key"]:
                raise ValueError("API key is missing. Set it in the UI, .env, environment, or translate.py defaults.")
            if not config["api"]["model"]:
                raise ValueError("Model is missing. Set it in the UI or your defaults.")

        job_id = uuid.uuid4().hex[:10]
        job = {
            "id": job_id,
            "status": "queued",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "started_at": None,
            "finished_at": None,
            "error": "",
            "progress": {
                "phase": "queued",
                "percent": 0,
                "processed_files": 0,
                "total_files": 0,
                "processed_batches": 0,
                "processed_texts": 0,
                "current_file": "",
                "current_activity": "",
                "changed_file_count": 0,
                "candidate_file_count": 0,
                "last_event_at": "",
            },
            "summary": summarize_config(config),
            "events": [],
            "result": None,
            "can_resume": False,
            "_config": config,
            "_cancel_event": threading.Event(),
        }

        with self.lock:
            self.jobs[job_id] = job

        thread = threading.Thread(target=self._run_job, args=(job_id,), daemon=True)
        thread.start()
        return self.public_job(job_id)

    def public_job(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            if job_id not in self.jobs:
                raise KeyError(job_id)
            return self._public_view(self.jobs[job_id])

    def cancel_job(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            if job_id not in self.jobs:
                raise KeyError(job_id)
            job = self.jobs[job_id]
            if job["status"] in {"completed", "failed", "cancelled"}:
                return self._public_view(job)
            job["_cancel_event"].set()
            self._append_event(job, {"event": "job_cancel_requested"})
            job["progress"]["current_activity"] = "cancel_requested"
            return self._public_view(job)

    def list_jobs(self) -> list[dict[str, Any]]:
        with self.lock:
            jobs = [self._public_view(job) for job in self.jobs.values()]
        jobs.sort(key=lambda item: item["created_at"], reverse=True)
        return jobs

    def _public_view(self, job: dict[str, Any]) -> dict[str, Any]:
        view = {key: value for key, value in job.items() if not key.startswith("_")}
        view["progress"] = dict(job["progress"])
        view["events"] = list(job["events"])
        return view

    def _append_event(self, job: dict[str, Any], event: dict[str, Any]) -> None:
        entry = {"timestamp": now_iso(), **event}
        job["updated_at"] = entry["timestamp"]
        job["progress"]["last_event_at"] = entry["timestamp"]
        job["events"].append(entry)
        if len(job["events"]) > MAX_EVENTS:
            job["events"] = job["events"][-MAX_EVENTS:]

    def _update_progress(self, job: dict[str, Any], event: dict[str, Any]) -> None:
        progress = job["progress"]
        name = event["event"]

        if name == "resource_pack_start":
            progress["phase"] = "resource_pack"
            progress["current_activity"] = "resource_pack"
            progress["percent"] = max(progress["percent"], 5)
        elif name == "resource_pack_done":
            progress["phase"] = "scan_pending"
            progress["current_activity"] = "resource_pack_done"
            progress["percent"] = max(progress["percent"], 12)
        elif name == "scan_start":
            progress["phase"] = "scan"
            progress["current_activity"] = "scan_start"
            progress["total_files"] = int(event.get("total_files", 0))
            if progress["total_files"] == 0:
                progress["percent"] = max(progress["percent"], 90)
        elif name == "file_start":
            progress["phase"] = "scan"
            progress["current_activity"] = "file_start"
            progress["current_file"] = ensure_str(event.get("file"))
            progress["total_files"] = int(event.get("total", progress["total_files"]))
            index = max(0, int(event.get("index", 0)) - 1)
            total = max(1, int(event.get("total", 0)))
            progress["processed_files"] = index
            progress["percent"] = max(progress["percent"], 12 + int(index / total * 80))
        elif name == "file_done":
            progress["phase"] = "scan"
            progress["current_activity"] = "file_done"
            progress["current_file"] = ensure_str(event.get("file"))
            total = max(1, int(event.get("total", 0)))
            index = int(event.get("index", 0))
            progress["processed_files"] = index
            progress["total_files"] = total
            progress["percent"] = max(progress["percent"], 12 + int(index / total * 80))
        elif name == "translation_batch_start":
            progress["phase"] = "translate"
            progress["current_activity"] = "translation_batch_start"
        elif name == "translation_batch_done":
            progress["phase"] = "translate"
            progress["current_activity"] = "translation_batch_done"
            progress["processed_batches"] += 1
            progress["processed_texts"] += int(event.get("batch_size", 0))
        elif name == "translation_batch_error":
            progress["phase"] = "translate"
            progress["current_activity"] = "translation_batch_error"
        elif name == "resource_pack_skipped":
            progress["current_activity"] = "resource_pack_skipped"
        elif name == "checkpoint_loaded":
            progress["current_activity"] = "checkpoint_loaded"
        elif name == "file_error":
            progress["current_activity"] = "file_error"
        elif name == "file_write_retry":
            progress["current_activity"] = "file_write_retry"
        elif name == "job_cancel_requested":
            progress["current_activity"] = "cancel_requested"
        elif name == "cancelled":
            progress["phase"] = "cancelled"
            progress["current_activity"] = "cancelled"
        elif name == "fatal_error":
            progress["phase"] = "failed"
            progress["current_activity"] = "failed"
        elif name == "done":
            progress["phase"] = "done"
            progress["current_activity"] = "done"
            progress["percent"] = 100
            progress["changed_file_count"] = int(event.get("changed_file_count", 0))
            progress["candidate_file_count"] = int(event.get("candidate_file_count", 0))

    def _run_job(self, job_id: str) -> None:
        with self.lock:
            job = self.jobs[job_id]
            job["status"] = "running"
            job["started_at"] = now_iso()
            job["progress"]["phase"] = "preparing"
            job["progress"]["current_activity"] = "preparing"
            self._append_event(job, {"event": "job_started"})
            config = job["_config"]
            cancel_event = job["_cancel_event"]

        try:
            translator = WorldTranslator(
                config,
                progress_callback=lambda event: self._handle_progress(job_id, event),
                cancel_check=cancel_event.is_set,
            )
            report = translator.run()
            with self.lock:
                job = self.jobs[job_id]
                final_status = report.get("status", "completed")
                job["status"] = final_status
                job["finished_at"] = now_iso()
                job["result"] = report
                job["can_resume"] = final_status == "cancelled"
                if final_status == "cancelled":
                    job["progress"]["phase"] = "cancelled"
                    job["progress"]["current_activity"] = "cancelled"
                else:
                    job["progress"]["phase"] = "done"
                    job["progress"]["current_activity"] = "done"
                    job["progress"]["percent"] = 100
                job["progress"]["changed_file_count"] = int(report.get("changed_file_count", 0))
                job["progress"]["candidate_file_count"] = int(report.get("candidate_file_count", 0))
                self._append_event(job, {
                    "event": "job_cancelled" if final_status == "cancelled" else "job_completed",
                    "changed_file_count": report.get("changed_file_count", 0),
                    "candidate_file_count": report.get("candidate_file_count", 0),
                })
        except SystemExit as exc:
            self._fail_job(job_id, str(exc) or "Translator exited early.")
        except Exception as exc:
            self._fail_job(job_id, str(exc) or exc.__class__.__name__)

    def _fail_job(self, job_id: str, message: str) -> None:
        with self.lock:
            job = self.jobs[job_id]
            job["status"] = "failed"
            job["finished_at"] = now_iso()
            job["error"] = message
            job["progress"]["phase"] = "failed"
            job["progress"]["current_activity"] = "failed"
            job["can_resume"] = True
            self._append_event(job, {"event": "job_failed", "message": message})

    def _handle_progress(self, job_id: str, event: dict[str, Any]) -> None:
        with self.lock:
            if job_id not in self.jobs:
                return
            job = self.jobs[job_id]
            self._append_event(job, event)
            self._update_progress(job, event)


JOB_MANAGER = JobManager()


class AppHandler(BaseHTTPRequestHandler):
    server_version = "MinecraftWorldTranslatorUI/1.0"

    def do_GET(self) -> None:  # noqa: N802
        self.handle_request(send_body=True)

    def do_HEAD(self) -> None:  # noqa: N802
        self.handle_request(send_body=False)

    def handle_request(self, send_body: bool) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/meta":
            self.send_json(
                {
                    "providers": provider_meta(),
                    "style_presets": sorted(STYLE_PRESETS),
                    "example_paths": discover_example_paths(),
                    "defaults": {
                        "batch_size": DEFAULT_CONFIG["batch_size"],
                        "temperature": DEFAULT_CONFIG["temperature"],
                        "backup_suffix": DEFAULT_CONFIG["backup_suffix"],
                        "provider": DEFAULT_CONFIG["api"]["provider"],
                        "request_timeout": DEFAULT_CONFIG["api"]["request_timeout"],
                        "checkpoint_enabled": DEFAULT_CONFIG["runtime"]["checkpoint_enabled"],
                        "continue_on_file_error": DEFAULT_CONFIG["runtime"]["continue_on_file_error"],
                        "max_batch_retries": DEFAULT_CONFIG["runtime"]["max_batch_retries"],
                        "max_file_write_retries": DEFAULT_CONFIG["runtime"]["max_file_write_retries"],
                        "region_dirs": DEFAULT_CONFIG["scan"]["region_dirs"],
                        "skip_patterns": DEFAULT_CONFIG["scan"]["skip_patterns"],
                        "resource_pack_source_lang_files": DEFAULT_CONFIG["resource_pack"]["source_lang_files"],
                    },
                },
                send_body=send_body,
            )
            return

        if parsed.path == "/api/jobs":
            self.send_json({"jobs": JOB_MANAGER.list_jobs()}, send_body=send_body)
            return

        if parsed.path.startswith("/api/jobs/"):
            job_id = parsed.path.rsplit("/", 1)[-1]
            try:
                job = JOB_MANAGER.public_job(job_id)
            except KeyError:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Job not found.")
                return
            self.send_json(job, send_body=send_body)
            return

        self.serve_static(parsed.path, send_body=send_body)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"

        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self.send_error_json(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON.")
            return

        if parsed.path == "/api/jobs":
            try:
                job = JOB_MANAGER.create_job(payload)
            except Exception as exc:
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self.send_json(job, status=HTTPStatus.CREATED)
            return

        if parsed.path.startswith("/api/jobs/") and parsed.path.endswith("/cancel"):
            job_id = parsed.path.split("/")[-2]
            try:
                job = JOB_MANAGER.cancel_job(job_id)
            except KeyError:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Job not found.")
                return
            self.send_json(job)
            return

        if parsed.path == "/api/models":
            try:
                config = build_payload_config(payload)
                models = list_models_for_config(config)
            except Exception as exc:
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self.send_json(
                {
                    "provider": config["api"]["provider"],
                    "model_count": len(models),
                    "models": models,
                }
            )
            return

        if parsed.path == "/api/prompt-assist":
            try:
                config = build_payload_config(payload)
                brief = ensure_str(payload.get("brief"))
                enhanced = enhance_style_prompt_for_config(config, brief)
            except Exception as exc:
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(exc))
                return
            self.send_json({"enhanced_prompt": enhanced})
            return

        self.send_error_json(HTTPStatus.NOT_FOUND, "Unknown endpoint.")

    def send_json(
        self,
        payload: Any,
        status: HTTPStatus = HTTPStatus.OK,
        *,
        send_body: bool = True,
    ) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"error": message, "status": status}, status=status)

    def serve_static(self, request_path: str, *, send_body: bool = True) -> None:
        relative = "index.html" if request_path in {"", "/"} else request_path.lstrip("/")
        target = (WEB_DIR / relative).resolve()
        if WEB_DIR.resolve() not in target.parents and target != WEB_DIR.resolve():
            self.send_error_json(HTTPStatus.FORBIDDEN, "Invalid path.")
            return

        if target.is_dir():
            target = target / "index.html"
        if not target.exists() or not target.is_file():
            self.send_error_json(HTTPStatus.NOT_FOUND, "Static file not found.")
            return

        mime_type, _ = mimetypes.guess_type(str(target))
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if send_body:
            self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Minecraft World Translator web UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=8765, help="Bind port. Default: 8765")
    parser.add_argument("--open-browser", action="store_true", help="Open the browser automatically.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    server = ThreadingHTTPServer((args.host, args.port), AppHandler)
    bound_host, bound_port = server.server_address[:2]
    display_host = args.host
    if bound_host in {"0.0.0.0", "::"}:
        display_host = "127.0.0.1"
    url = f"http://{display_host}:{bound_port}"
    print(f"Minecraft World Translator UI running at {url}")
    print("Press Ctrl+C to stop.")

    if args.open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
