"""A request completed before cancellation must retain its usage without claiming writes."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import mc_world_translator as core
from tests.test_resource_pack_preflight import ProviderSpy, _config, _world


class UsageProvider(ProviderSpy):
    def translate_mapping(self, values: dict, **kwargs) -> dict[str, str]:
        result = super().translate_mapping(values, **kwargs)
        type(self).usage = {"prompt_tokens": 120, "completion_tokens": 20, "cost": 0.0, "cost_reported": False}
        return result


class CancelledUsageTests(unittest.TestCase):
    def test_finished_request_usage_survives_cancel_or_write_error(self) -> None:
        for outcome in ("cancel", "write_error"):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory(prefix="pomi-cancel-usage-") as directory:
                root = Path(directory)
                world = _world(root / "world")
                pack = world / "resources.zip"
                with zipfile.ZipFile(pack, "w") as archive:
                    archive.writestr("assets/demo/lang/en_us.json", json.dumps({"a": "Welcome traveler", "b": "Keep original", "c": "Shop"}))
                original = pack.read_bytes()
                cancelled = False

                def progress(event: dict) -> None:
                    nonlocal cancelled
                    if outcome == "cancel" and event.get("event") == "phase_start" and event.get("phase") == "write":
                        cancelled = True

                with patch.object(core, "LLMProviderClient", UsageProvider):
                    translator = core.WorldTranslator(_config(world, pack, root / "report.json"), progress_callback=progress, cancel_check=lambda: cancelled)
                    if outcome == "cancel":
                        report = translator.run()
                        self.assertEqual(report["status"], "cancelled")
                    else:
                        with patch.object(translator, "write_resource_packs", side_effect=OSError("synthetic write error")):
                            with self.assertRaises(OSError):
                                translator.run()
                        report = json.loads((root / "report.json").read_text())
                        self.assertEqual(report["status"], "failed")
                self.assertEqual(report["provider_requests"], 1)
                self.assertEqual(report["usage"]["prompt_tokens"], 120)
                self.assertEqual(report["usage"]["completion_tokens"], 20)
                self.assertEqual(report["translation"]["translated"], 3)
                self.assertEqual(report["changed_file_count"], 0)
                self.assertEqual(pack.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
