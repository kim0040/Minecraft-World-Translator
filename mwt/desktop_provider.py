"""Provider selection for Rust-owned desktop requests; CLI overrides remain separate."""
from urllib.parse import urlsplit

PUBLIC_ENDPOINTS = {
    "openai": ("https://api.openai.com/v1", "openai"),
    "openrouter": ("https://openrouter.ai/api/v1", "openai"),
    "comet": ("https://api.cometapi.com/v1", "openai"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta", "gemini"),
    "anthropic": ("https://api.anthropic.com/v1", "anthropic"),
}


def resolve_desktop_provider(body: dict, saved: dict) -> dict:
    provider = str(body.get("provider") or saved.get("provider") or "openai")
    model = str(body.get("model") or saved.get("model") or "")
    if provider in PUBLIC_ENDPOINTS:
        endpoint, wire = PUBLIC_ENDPOINTS[provider]
        supplied = str(body.get("baseUrl") or "")
        if supplied and supplied.rstrip("/") != endpoint:
            raise ValueError("Public provider endpoint does not match the selected provider")
    elif provider == "custom":
        endpoint = str(body.get("baseUrl") or saved.get("base_url") or "")
        parsed = urlsplit(endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("Custom provider requires an explicit HTTP(S) endpoint without credentials")
        wire = str(body.get("wireFormat") or saved.get("wire_format") or "openai")
        if wire not in {"openai", "anthropic"}:
            raise ValueError("Unsupported Custom wire format")
    else:
        raise ValueError("Unsupported desktop provider")
    return {"provider": provider, "model": model, "base_url": endpoint, "wire_format": wire, "api_key": str(body.get("apiKey") or "")}
