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


# Gemini reports only a boolean "thinking" flag. Generation 3+ takes a thinking level; 2.5 takes a
# token budget. Measured 2026-10-01: "minimal" (3.x flash/lite) and budget 0 (2.5 flash) return no
# thought tokens; flash-lite 3.x rejects budget 0, so it is never sent to generation 3+.
_GEMINI_LEVELS = ("minimal", "low", "medium", "high")
_GEMINI_BUDGETS = {"minimal": 512, "low": 1024, "medium": 8192, "high": 24576}


def _gemini_generation(model_id: str) -> tuple[float, bool, bool]:
    import re

    lowered = model_id.lower().removeprefix("models/")
    match = re.match(r"gemini-(\d+(?:\.\d+)?)", lowered)
    generation = float(match.group(1)) if match else 0.0
    return generation, "pro" in lowered, "lite" in lowered


def gemini_reasoning(model_id: str, thinking: Any) -> dict | None:
    """Catalog reasoning metadata for a Gemini model, in the shape `model_reasoning` returns."""
    if thinking is not True:
        return None
    generation, pro, lite = _gemini_generation(model_id)
    if generation >= 3:
        efforts = ["low", "high"] if pro else list(_GEMINI_LEVELS)
        meta: dict = {"mandatory": pro, "supported_efforts": efforts}
        if not lite:
            meta.update(default_enabled=True, default_effort="high")
        return meta
    if generation >= 2.5:
        meta = {"mandatory": pro, "supported_efforts": ["low", "medium", "high"]}
        if not lite:
            meta.update(default_enabled=True)
        return meta
    return None


def gemini_thinking_config(choice: str, model_id: str, info: dict | None) -> dict | None:
    """`generationConfig.thinkingConfig` for a validated choice; None keeps the model default."""
    reasoning_payload(choice, info)  # Same catalog-bound validation as OpenRouter.
    if choice == "default":
        return None
    generation, _pro, _lite = _gemini_generation(model_id)
    if generation >= 3:
        if choice == "disabled":
            return {"thinkingLevel": "minimal"}
        if choice == "enabled":
            return None
        return {"thinkingLevel": choice if choice in _GEMINI_LEVELS else "high"}
    if choice == "disabled":
        return {"thinkingBudget": 0}
    if choice == "enabled":
        return {"thinkingBudget": -1}
    return {"thinkingBudget": _GEMINI_BUDGETS.get(choice, _GEMINI_BUDGETS["high"])}
