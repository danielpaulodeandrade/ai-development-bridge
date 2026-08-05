import os
import pytest
from unittest.mock import patch, MagicMock
from src.provider_system.base import ProviderMessage
from src.provider_system.ollama_provider import OllamaProvider

@pytest.fixture
def ollama_provider():
    return OllamaProvider()

def test_ollama_provider_name(ollama_provider):
    assert ollama_provider.provider_name == "ollama"

@patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://test-server:11434/v1", "OLLAMA_API_KEY": "fake_key", "OLLAMA_DEFAULT_MODEL": "llama-test"})
@patch("src.provider_system.ollama_provider.OpenAI")
def test_ollama_initialization(mock_openai_class, ollama_provider):
    ollama_provider.initialize()
    mock_openai_class.assert_called_once_with(
        base_url="http://test-server:11434/v1",
        api_key="fake_key"
    )
    assert ollama_provider._default_model == "llama-test"

@patch.dict(os.environ, {"OLLAMA_BASE_URL": "http://test-server:11434/v1", "OLLAMA_API_KEY": "fake_key"})
@patch("src.provider_system.ollama_provider.OpenAI")
def test_ollama_send_prompt(mock_openai_class, ollama_provider):
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked Ollama Reply"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model_dump.return_value = {"id": "chatcmpl-456"}
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    msg = ProviderMessage(role="user", content="Hello Ollama")
    response = ollama_provider.send_prompt([msg], model="deepseek-r1:14b")
    
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": "Hello Ollama"}],
        model="deepseek-r1:14b"
    )
    assert response.content == "Mocked Ollama Reply"
    assert response.model_used == "deepseek-r1:14b"
