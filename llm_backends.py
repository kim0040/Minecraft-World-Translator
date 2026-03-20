from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib import error, parse, request


PROVIDER_SPECS: dict[str, dict[str, str]] = {
    "comet": {
        "label": "Comet API",
        "base_url": "https://api.cometapi.com/v1",
        "env_var": "COMET_API_KEY",
        "base_url_env_var": "COMET_BASE_URL",
        "model_env_var": "COMET_MODEL",
        "family": "openai_compatible",
    },
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "env_var": "OPENAI_API_KEY",
        "base_url_env_var": "OPENAI_BASE_URL",
        "model_env_var": "OPENAI_MODEL",
        "family": "openai_compatible",
    },
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "env_var": "OPENROUTER_API_KEY",
        "base_url_env_var": "OPENROUTER_BASE_URL",
        "model_env_var": "OPENROUTER_MODEL",
        "family": "openai_compatible",
    },
    "gemini": {
        "label": "Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "env_var": "GEMINI_API_KEY",
        "base_url_env_var": "GEMINI_BASE_URL",
        "model_env_var": "GEMINI_MODEL",
        "family": "gemini",
    },
    "anthropic": {
        "label": "Anthropic",
        "base_url": "https://api.anthropic.com/v1",
        "env_var": "ANTHROPIC_API_KEY",
        "base_url_env_var": "ANTHROPIC_BASE_URL",
        "model_env_var": "ANTHROPIC_MODEL",
        "family": "anthropic",
    },
}


PROMPT_ENHANCER_SYSTEM_PROMPT = """
너는 마인크래프트 월드/맵 번역을 위한 스타일 프롬프트 설계자다.
사용자가 짧게 적은 스타일 요구사항을 실제 번역 시스템 프롬프트 뒤에 붙여도 되는 구체적인 추가 스타일 지시문으로 확장해라.

[작성 규칙]
1. 결과는 짧고 실전적인 지시문이어야 한다.
2. 사용자의 의도는 유지하되, 번역 품질에 도움이 되는 구체성만 보강한다.
3. 말투, 고유명사 처리, 퍼즐 힌트 명확성, 공포/코믹/중세 분위기 같은 항목을 필요할 때만 추가한다.
4. 특수기호, JSON 구조, 플레이 텍스트의 가독성을 망치지 말라는 지시는 포함해도 된다.
5. 설명, 인사, 머리말 없이 최종 지시문만 반환해라.
""".strip()


def provider_choices() -> list[str]:
    return sorted(PROVIDER_SPECS)


def provider_spec(provider: str) -> dict[str, str]:
    if provider not in PROVIDER_SPECS:
        raise ValueError(f"Unsupported provider: {provider}")
    return PROVIDER_SPECS[provider]


def infer_provider(provider: str | None, base_url: str) -> str:
    explicit = (provider or "").strip().lower()
    if explicit and explicit != "auto":
        return explicit

    lowered = base_url.strip().lower()
    if "openrouter.ai" in lowered:
        return "openrouter"
    if "generativelanguage.googleapis.com" in lowered or "googleapis.com" in lowered:
        return "gemini"
    if "anthropic.com" in lowered:
        return "anthropic"
    if "openai.com" in lowered:
        return "openai"
    if "cometapi.com" in lowered:
        return "comet"
    return "comet"


def resolve_api_key(provider: str, current: str) -> str:
    if current:
        return current

    env_name = provider_spec(provider)["env_var"]
    if os.getenv(env_name):
        return os.getenv(env_name, "")

    fallback_order = [
        "OPENAI_API_KEY",
        "COMET_API_KEY",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
        "OPENROUTER_API_KEY",
    ]
    for env_name in fallback_order:
        if os.getenv(env_name):
            return os.getenv(env_name, "")
    return ""


def default_base_url(provider: str) -> str:
    return provider_spec(provider)["base_url"]


def resolve_base_url(provider: str, current: str) -> str:
    if current:
        return current
    spec = provider_spec(provider)
    return os.getenv(spec["base_url_env_var"], spec["base_url"])


def resolve_model(provider: str, current: str) -> str:
    if current:
        return current
    spec = provider_spec(provider)
    return os.getenv(spec["model_env_var"], "")


def normalize_model_name(provider: str, model: str) -> str:
    cleaned = model.strip()
    if provider == "gemini" and cleaned and not cleaned.startswith("models/"):
        return cleaned
    return cleaned


def extract_json_object(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def flatten_text_payload(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif item.get("type") == "output_text" and isinstance(item.get("text"), str):
                    parts.append(item["text"])
        return "\n".join(parts).strip()
    if isinstance(content, dict):
        if isinstance(content.get("text"), str):
            return content["text"]
    return ""


class LLMProviderClient:
    def __init__(self, config: dict[str, Any]) -> None:
        api_config = config["api"]
        self.provider = api_config["provider"]
        self.base_url = api_config["base_url"].rstrip("/")
        self.api_key = api_config["api_key"]
        self.model = api_config["model"]
        self.timeout = int(api_config.get("request_timeout", 120))
        self.family = provider_spec(self.provider)["family"]

    def ensure_ready(self, require_model: bool = True) -> None:
        if not self.api_key:
            raise RuntimeError(f"{provider_spec(self.provider)['label']} API key is missing.")
        if require_model and not self.model:
            raise RuntimeError(f"{provider_spec(self.provider)['label']} model is missing.")

    def list_models(self) -> list[dict[str, Any]]:
        self.ensure_ready(require_model=False)
        if self.family == "openai_compatible":
            return self._list_models_openai_compatible()
        if self.family == "gemini":
            return self._list_models_gemini()
        if self.family == "anthropic":
            return self._list_models_anthropic()
        raise RuntimeError(f"Unsupported provider family: {self.family}")

    def complete_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        expect_json: bool = False,
        max_output_tokens: int = 4096,
    ) -> str:
        self.ensure_ready(require_model=True)
        if self.family == "openai_compatible":
            return self._complete_openai_compatible(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                expect_json=expect_json,
            )
        if self.family == "gemini":
            return self._complete_gemini(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                expect_json=expect_json,
                max_output_tokens=max_output_tokens,
            )
        if self.family == "anthropic":
            return self._complete_anthropic(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
        raise RuntimeError(f"Unsupported provider family: {self.family}")

    def translate_mapping(self, payload: dict[str, str], *, system_prompt: str, temperature: float) -> dict[str, str]:
        raw = self.complete_text(
            system_prompt=system_prompt,
            user_prompt=json.dumps(payload, ensure_ascii=False, indent=2),
            temperature=temperature,
            expect_json=True,
        )
        parsed = extract_json_object(raw)
        return {
            key: parsed.get(key, value) if isinstance(parsed.get(key, value), str) else value
            for key, value in payload.items()
        }

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str],
        payload: dict[str, Any] | None = None,
    ) -> Any:
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(url=url, data=body, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"{provider_spec(self.provider)['label']} request failed with HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(f"{provider_spec(self.provider)['label']} request failed: {exc.reason}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"{provider_spec(self.provider)['label']} returned invalid JSON.") from exc

    def _openai_headers(self) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "http://localhost"
            headers["X-Title"] = "Minecraft World Translator"
        return headers

    def _complete_openai_compatible(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        expect_json: bool,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        if expect_json:
            payload["response_format"] = {"type": "json_object"}

        response = self._request_json(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._openai_headers(),
            payload=payload,
        )
        choices = response.get("choices") or []
        if not choices:
            raise RuntimeError(f"{provider_spec(self.provider)['label']} returned no choices.")
        message = choices[0].get("message", {})
        return flatten_text_payload(message.get("content"))

    def _list_models_openai_compatible(self) -> list[dict[str, Any]]:
        response = self._request_json("GET", f"{self.base_url}/models", headers=self._openai_headers())
        data = response.get("data") or []
        models: list[dict[str, Any]] = []
        for item in data:
            model_id = str(item.get("id", "")).strip()
            if not model_id:
                continue
            models.append(
                {
                    "id": model_id,
                    "display_name": model_id,
                    "description": item.get("owned_by", ""),
                    "raw": item,
                }
            )
        return models

    def _complete_gemini(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        expect_json: bool,
        max_output_tokens: int,
    ) -> str:
        model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
        query = parse.urlencode({"key": self.api_key})
        payload: dict[str, Any] = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }
        if expect_json:
            payload["generationConfig"]["responseMimeType"] = "application/json"
        response = self._request_json(
            "POST",
            f"{self.base_url}/{model_name}:generateContent?{query}",
            headers={"Content-Type": "application/json"},
            payload=payload,
        )
        candidates = response.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini returned no candidates.")
        content = candidates[0].get("content", {})
        parts = content.get("parts") or []
        return "\n".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and isinstance(part.get("text"), str)
        ).strip()

    def _list_models_gemini(self) -> list[dict[str, Any]]:
        query = parse.urlencode({"key": self.api_key, "pageSize": 1000})
        response = self._request_json(
            "GET",
            f"{self.base_url}/models?{query}",
            headers={"Content-Type": "application/json"},
        )
        data = response.get("models") or []
        models: list[dict[str, Any]] = []
        for item in data:
            methods = item.get("supportedGenerationMethods") or []
            if "generateContent" not in methods:
                continue
            model_id = str(item.get("baseModelId") or item.get("name", "")).strip()
            if model_id.startswith("models/"):
                model_id = model_id.split("/", 1)[1]
            if not model_id:
                continue
            description_parts = [item.get("displayName", "")]
            if item.get("description"):
                description_parts.append(str(item["description"]))
            models.append(
                {
                    "id": model_id,
                    "display_name": item.get("displayName", model_id),
                    "description": " | ".join(part for part in description_parts if part),
                    "raw": item,
                }
            )
        return models

    def _anthropic_headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _complete_anthropic(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_output_tokens: int,
    ) -> str:
        payload = {
            "model": self.model,
            "system": system_prompt,
            "max_tokens": max_output_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        response = self._request_json(
            "POST",
            f"{self.base_url}/messages",
            headers=self._anthropic_headers(),
            payload=payload,
        )
        parts = response.get("content") or []
        return "\n".join(
            part.get("text", "")
            for part in parts
            if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str)
        ).strip()

    def _list_models_anthropic(self) -> list[dict[str, Any]]:
        response = self._request_json("GET", f"{self.base_url}/models?limit=1000", headers=self._anthropic_headers())
        data = response.get("data") or []
        models: list[dict[str, Any]] = []
        for item in data:
            model_id = str(item.get("id", "")).strip()
            if not model_id:
                continue
            models.append(
                {
                    "id": model_id,
                    "display_name": item.get("display_name", model_id),
                    "description": item.get("created_at", ""),
                    "raw": item,
                }
            )
        return models


def enhance_style_prompt(config: dict[str, Any], brief: str) -> str:
    cleaned = brief.strip()
    if not cleaned:
        raise ValueError("Style brief is empty.")

    prompt_config = config["prompt"]
    user_prompt = (
        f"대상 언어: {prompt_config['target_language']}\n"
        f"기본 스타일 프리셋: {prompt_config['style_preset']}\n"
        f"현재 추가 스타일 지시: {prompt_config['style_prompt'] or '(없음)'}\n"
        f"사용자 메모: {cleaned}\n\n"
        "위 메모를 바탕으로 실제 게임 번역 품질에 도움이 되는 추가 스타일 지시문을 4~8줄 정도로 정리해라."
    )
    client = LLMProviderClient(config)
    return client.complete_text(
        system_prompt=PROMPT_ENHANCER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
        max_output_tokens=700,
    ).strip()
