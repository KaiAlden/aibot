import pytest

from app.services.llm_client import (
    MissingLLMConfigError,
    RemoteLLMClient,
    build_classic_translation_messages,
    extract_llm_text,
)


def test_build_classic_translation_messages_contains_safety_instruction() -> None:
    messages = build_classic_translation_messages("阳气不足")

    assert messages[0]["role"] == "system"
    assert "不得增加诊断、处方或用药建议" in messages[0]["content"]
    assert "阳气不足" in messages[1]["content"]


def test_remote_llm_client_requires_config() -> None:
    client = RemoteLLMClient(endpoint=None, api_key=None, model_name=None)

    with pytest.raises(MissingLLMConfigError):
        client.chat([{"role": "user", "content": "hi"}])


def test_extract_llm_text_supports_content_blocks() -> None:
    data = {"content": [{"type": "thinking", "thinking": "skip"}, {"type": "text", "text": "现代文"}]}

    assert extract_llm_text(data) == "现代文"
