from typing import Any, Protocol

import httpx

from app.config.settings import settings


class LLMError(Exception):
    pass


class MissingLLMConfigError(LLMError):
    pass


class LLMClient(Protocol):
    def chat(self, messages: list[dict[str, str]], temperature: float | None = None) -> str:
        ...


class RemoteLLMClient:
    """OpenAI-compatible non-streaming chat client for backend batch jobs."""

    def __init__(
        self,
        endpoint: str | None = settings.llm_api_endpoint,
        api_key: str | None = settings.llm_api_key,
        model_name: str | None = settings.llm_model_name,
        timeout_seconds: float = 60,
    ) -> None:
        self.endpoint = endpoint
        self.api_key = api_key
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def _validate_config(self) -> None:
        if not self.endpoint or not self.api_key or not self.model_name:
            raise MissingLLMConfigError(
                "LLM_API_ENDPOINT, LLM_API_KEY and LLM_MODEL_NAME must be configured before translation."
            )

    def chat(self, messages: list[dict[str, str]], temperature: float | None = None) -> str:
        self._validate_config()
        payload: dict[str, Any] = {
            "model": self.model_name,
            "messages": messages,
            "temperature": settings.llm_temperature if temperature is None else temperature,
            "max_tokens": settings.llm_max_tokens,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = extract_llm_text(data)
        if content:
            return content
        raise LLMError(f"Unexpected LLM response format, top-level keys: {sorted(data.keys())}")


def extract_llm_text(data: dict[str, Any]) -> str | None:
    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError):
        pass

    content = data.get("content")
    if isinstance(content, list):
        texts = [
            str(item.get("text", "")).strip()
            for item in content
            if isinstance(item, dict) and item.get("type") == "text" and item.get("text")
        ]
        return "\n".join(texts).strip() or None

    if isinstance(content, str):
        return content.strip()
    return None


def build_classic_translation_messages(text: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是中医古籍整理助手。请将古文整理为现代中文释义，保留原意和中医术语，"
                "不得增加诊断、处方或用药建议。只输出现代文释义。"
            ),
        },
        {
            "role": "user",
            "content": f"请翻译以下中医古籍片段：\n\n{text}",
        },
    ]
