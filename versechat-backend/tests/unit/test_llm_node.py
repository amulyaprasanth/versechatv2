from unittest.mock import patch

import pytest

from versechat_backend.rag.nodes.llm_node import LLMNode


@patch.dict("os.environ", {"GROQ_API_KEY": ""}, clear=True)
def test_groq_key_missing():
    with pytest.raises(
        ValueError, match="Groq API key is missing from environment variables"
    ):
        LLMNode()


def invalid_model_name():
    with pytest.raises(
        ValueError,
        match="Invalid model name. Please check [https://console.groq.com/docs/models](https://console.groq.com/docs/models) for a list of supported models.",
    ):
        LLMNode(model="some-random-model")
