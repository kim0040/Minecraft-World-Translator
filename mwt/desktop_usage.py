"""Read-only provider usage through the Rust credential boundary."""
from datetime import datetime, timezone
import json
import math
from urllib import request

from mwt.desktop_provider import resolve_desktop_provider


class UsageUnavailable(ValueError):
    """A redacted failure safe to send over the public desktop protocol."""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _number(value: object, *, required: bool = False) -> float | None:
    if value is None and not required:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UsageUnavailable("Provider usage response is invalid")
    try:
        number = float(value)
    except (OverflowError, ValueError):
        raise UsageUnavailable("Provider usage response is invalid") from None
    if not math.isfinite(number) or number < 0:
        raise UsageUnavailable("Provider usage response is invalid")
    return number


def fetch_openrouter_usage(body: dict, saved: dict) -> dict:
    if body.get("credentialOwner") != "rust":
        raise UsageUnavailable("Usage requires a Rust-owned credential")
    try:
        selected = resolve_desktop_provider(body, saved)
    except ValueError:
        raise UsageUnavailable("Provider usage configuration is invalid") from None
    if selected["provider"] != "openrouter":
        raise UsageUnavailable("Usage lookup is available for OpenRouter only")
    key = selected["api_key"].strip()
    if not key:
        raise UsageUnavailable("A stored OpenRouter API key is required")
    try:
        query = request.Request(
            "https://openrouter.ai/api/v1/key",
            headers={"Authorization": "Bearer " + key},
            method="GET",
        )
        with request.build_opener(NoRedirect()).open(query, timeout=20) as response:
            if response.status != 200:
                raise UsageUnavailable("Provider usage lookup failed")
            contents = response.read(65_537)
            if len(contents) > 65_536:
                raise UsageUnavailable("Provider usage response is invalid")
            data = json.loads(contents).get("data")
            if not isinstance(data, dict):
                raise UsageUnavailable("Provider usage response is invalid")
            # Never return label, hash, account identifiers or arbitrary provider fields.
            result = {
                "provider": "openrouter",
                "usage": _number(data.get("usage"), required=True),
                "byokUsage": _number(data.get("byok_usage")),
                "limit": _number(data.get("limit")),
                "limitRemaining": _number(data.get("limit_remaining")),
            }
    except UsageUnavailable:
        raise
    except Exception:
        # Transport errors may embed headers or the response body. Do not expose them.
        raise UsageUnavailable("Provider usage lookup failed") from None
    result["checkedAt"] = datetime.now(timezone.utc).isoformat()
    return result
