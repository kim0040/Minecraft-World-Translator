"""Public OpenRouter reasoning preferences and catalog-bound request validation."""
from typing import Any

EFFORTS = ("minimal", "low", "medium", "high", "xhigh", "max")
CHOICES = ("default", "enabled", "disabled", *EFFORTS)


def normalize_reasoning(value: Any = "default") -> str:
    if not isinstance(value, str) or value not in CHOICES:
        raise ValueError("openrouter_reasoning must be default, enabled, disabled, or a supported effort")
    return value


def model_reasoning(value: Any) -> dict | None:
    if not isinstance(value, dict):
        return None
    result = {key: value[key] for key in ("mandatory", "default_enabled", "supports_max_tokens") if type(value.get(key)) is bool}
    if value.get("default_effort") in (*EFFORTS, "none"):
        result["default_effort"] = value["default_effort"]
    if "supported_efforts" in value:
        efforts = value["supported_efforts"]
        if efforts is None:
            result["supported_efforts"] = None
        elif isinstance(efforts, list):
            result["supported_efforts"] = list(dict.fromkeys(x for x in efforts if isinstance(x, str) and x in EFFORTS))
    return result


def reasoning_payload(choice: str, info: dict | None) -> dict | None:
    choice = normalize_reasoning(choice)
    if choice == "default":
        return None  # Preserve provider defaults and the old request shape.
    if not info or not (isinstance(info.get("reasoning"), dict) or "reasoning" in info.get("supported_parameters", [])):
        raise ValueError("Refresh the model list: this model has no verified reasoning support")
    meta = info.get("reasoning") or {}
    if choice == "disabled":
        if meta.get("mandatory"):
            raise ValueError("Reasoning is mandatory for this model")
        return {"enabled": False, "exclude": True}
    if choice == "enabled":
        return {"enabled": True, "exclude": True}
    if "supported_efforts" not in meta or (meta["supported_efforts"] is not None and choice not in meta["supported_efforts"]):
        raise ValueError("This reasoning effort is not supported by the selected model")
    # Translation consumes only final message content; reasoning text is not stored.
    return {"effort": choice, "exclude": True}
