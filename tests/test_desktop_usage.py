"""OpenRouter key-usage reads stay scoped, redacted, and schema-checked."""

from __future__ import annotations

from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mwt.desktop_usage import UsageUnavailable, fetch_openrouter_usage  # noqa: E402


FAKE_KEY = "synthetic-openrouter-key-do-not-use"
BASE_BODY = {
    "credentialOwner": "rust",
    "provider": "openrouter",
    "apiKey": FAKE_KEY,
}
SAVED = {"provider": "openrouter", "base_url": "https://openrouter.ai/api/v1"}


class FakeResponse:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self.body = body
        self.read_sizes: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.read_sizes.append(size)
        return self.body if size < 0 else self.body[:size]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def _response(status: int = 200, payload=None) -> FakeResponse:
    return FakeResponse(status, json.dumps(payload).encode("utf-8"))


def _install_opener(response=None, *, error: Exception | None = None):
    opener = Mock()
    if error is not None:
        opener.open.side_effect = error
    else:
        opener.open.return_value = response
    build_opener = patch("mwt.desktop_usage.request.build_opener", return_value=opener)
    return build_opener, opener


class DesktopUsageTests(unittest.TestCase):
    def test_uses_fixed_endpoint_bearer_key_timeout_and_no_redirect(self) -> None:
        response = _response(
            payload={
                "data": {
                    "usage": 12.5,
                    "byok_usage": 1.25,
                    "limit": 50.0,
                    "limit_remaining": 36.25,
                    "label": "private key label",
                    "hash": "private key hash",
                    "unexpected": "private provider response field",
                }
            }
        )
        build_opener, opener = _install_opener(response)
        with build_opener as build:
            result = fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))

        request = opener.open.call_args.args[0]
        self.assertIsInstance(request, Request)
        self.assertEqual(request.full_url, "https://openrouter.ai/api/v1/key")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {FAKE_KEY}")
        self.assertEqual(opener.open.call_args.kwargs, {"timeout": 20})
        build.assert_called_once()
        handlers = build.call_args.args
        redirect_handler = next((item for item in handlers if isinstance(item, HTTPRedirectHandler)), None)
        self.assertIsNotNone(redirect_handler, "redirects must be explicitly disabled")
        self.assertIsNone(
            redirect_handler.redirect_request(request, None, 302, "Found", {}, "https://attacker.invalid/"),
            "the redirect handler must refuse redirect targets",
        )
        self.assertEqual(response.read_sizes, [65537])

        self.assertEqual(
            set(result),
            {"provider", "checkedAt", "usage", "byokUsage", "limit", "limitRemaining"},
        )
        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(result["usage"], 12.5)
        self.assertEqual(result["byokUsage"], 1.25)
        self.assertEqual(result["limit"], 50.0)
        self.assertEqual(result["limitRemaining"], 36.25)
        checked_at = datetime.fromisoformat(result["checkedAt"].replace("Z", "+00:00"))
        self.assertIsNotNone(checked_at.tzinfo)
        self.assertEqual(checked_at.utcoffset(), timedelta(0))
        serialized = json.dumps(result)
        for private_value in (FAKE_KEY, "private key label", "private key hash", "private provider response field"):
            self.assertNotIn(private_value, serialized)

    def test_optional_accounting_fields_default_to_null(self) -> None:
        response = _response(payload={"data": {"usage": 0}})
        build_opener, _opener = _install_opener(response)
        with build_opener:
            result = fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))

        self.assertIsNone(result["byokUsage"])
        self.assertIsNone(result["limit"])
        self.assertIsNone(result["limitRemaining"])

    def test_rejects_wrong_owner_provider_endpoint_or_missing_key_before_network(self) -> None:
        invalid_inputs = [
            ({**BASE_BODY, "credentialOwner": "python"}, dict(SAVED)),
            ({**BASE_BODY, "provider": "custom", "baseUrl": "https://attacker.invalid"}, dict(SAVED)),
            ({**BASE_BODY, "provider": "openai"}, dict(SAVED)),
            ({**BASE_BODY, "baseUrl": "https://attacker.invalid/api/v1"}, dict(SAVED)),
            ({**BASE_BODY, "apiKey": ""}, dict(SAVED)),
            ({key: value for key, value in BASE_BODY.items() if key != "apiKey"}, dict(SAVED)),
        ]
        for body, saved in invalid_inputs:
            with self.subTest(body=body):
                build_opener, _opener = _install_opener(_response(payload={"data": {"usage": 0}}))
                with build_opener as build:
                    with self.assertRaises(UsageUnavailable):
                        fetch_openrouter_usage(body, saved)
                build.assert_not_called()

    def test_rejects_non_200_malformed_json_or_invalid_response_shape(self) -> None:
        cases = [
            _response(401, {"error": {"message": f"Bearer {FAKE_KEY}"}}),
            FakeResponse(200, f"Bearer {FAKE_KEY} is not JSON".encode("utf-8")),
            _response(payload={"data": []}),
            _response(payload={"unexpected": {"usage": 1}}),
        ]
        for response in cases:
            with self.subTest(status=response.status, body=response.body[:80]):
                build_opener, _opener = _install_opener(response)
                with build_opener:
                    with self.assertRaises(UsageUnavailable) as raised:
                        fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))
                self.assertNotIn(FAKE_KEY, str(raised.exception))

    def test_rejects_oversized_response(self) -> None:
        response = FakeResponse(200, b" " * 65537)
        build_opener, _opener = _install_opener(response)
        with build_opener:
            with self.assertRaises(UsageUnavailable):
                fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))
        self.assertEqual(response.read_sizes, [65537])

    def test_rejects_invalid_usage_counters(self) -> None:
        invalid_values = (None, True, "12.5", -0.01, float("nan"), float("inf"), -float("inf"), {})
        for value in invalid_values:
            with self.subTest(usage=value):
                response = _response(payload={"data": {"usage": value}})
                build_opener, _opener = _install_opener(response)
                with build_opener:
                    with self.assertRaises(UsageUnavailable):
                        fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))

        response = _response(payload={"data": {}})
        build_opener, _opener = _install_opener(response)
        with build_opener:
            with self.assertRaises(UsageUnavailable):
                fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))

    def test_rejects_invalid_optional_numeric_fields(self) -> None:
        for field in ("byok_usage", "limit", "limit_remaining"):
            for value in (True, -1, float("nan"), float("inf"), "5"):
                with self.subTest(field=field, value=value):
                    response = _response(payload={"data": {"usage": 0, field: value}})
                    build_opener, _opener = _install_opener(response)
                    with build_opener:
                        with self.assertRaises(UsageUnavailable):
                            fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))

    def test_redacts_http_and_transport_exception_text(self) -> None:
        errors = [
            HTTPError(
                "https://openrouter.ai/api/v1/key",
                302,
                f"redirect included Bearer {FAKE_KEY}",
                {},
                None,
            ),
            OSError(f"transport failed for Bearer {FAKE_KEY}"),
        ]
        for error in errors:
            with self.subTest(error_type=type(error).__name__):
                build_opener, _opener = _install_opener(error=error)
                with build_opener:
                    with self.assertRaises(UsageUnavailable) as raised:
                        fetch_openrouter_usage(dict(BASE_BODY), dict(SAVED))
                self.assertNotIn(FAKE_KEY, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
