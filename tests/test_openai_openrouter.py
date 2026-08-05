import os
import pytest
from unittest.mock import patch, MagicMock
from src.provider_system.base import ProviderMessage
from src.provider_system.openai_provider import OpenAIProvider
from src.provider_system.openrouter_provider import OpenRouterProvider

@pytest.fixture
def openai_provider():
    return OpenAIProvider()

@pytest.fixture
def openrouter_provider():
    return OpenRouterProvider()

def test_openai_provider_name(openai_provider):
    assert openai_provider.provider_name == "openai"

def test_openrouter_provider_name(openrouter_provider):
    assert openrouter_provider.provider_name == "openrouter"

@patch.dict(os.environ, clear=True)
def test_openai_initialization_fails_without_key(openai_provider):
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is missing"):
        openai_provider.initialize()

@patch.dict(os.environ, clear=True)
def test_openrouter_initialization_fails_without_key(openrouter_provider):
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable is missing"):
        openrouter_provider.initialize()

@patch.dict(os.environ, {"OPENAI_API_KEY": "fake_openai_key"})
@patch("src.provider_system.openai_provider.OpenAI")
def test_openai_initialization_success(mock_openai_class, openai_provider):
    openai_provider.initialize()
    mock_openai_class.assert_called_once_with(api_key="fake_openai_key")
    assert openai_provider.client is not None

@patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_openrouter_key"})
@patch("src.provider_system.openrouter_provider.OpenAI")
def test_openrouter_initialization_success(mock_openai_class, openrouter_provider):
    openrouter_provider.initialize()
    mock_openai_class.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1",
        api_key="fake_openrouter_key"
    )
    assert openrouter_provider.client is not None

@patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key"})
@patch("src.provider_system.openai_provider.OpenAI")
def test_openai_send_prompt(mock_openai_class, openai_provider):
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked OpenAI Reply"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model_dump.return_value = {"id": "chatcmpl-123"}
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    msg = ProviderMessage(role="user", content="Hello OpenAI")
    response = openai_provider.send_prompt([msg], model="gpt-4o-mini")
    
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": "Hello OpenAI"}],
        model="gpt-4o-mini"
    )
    assert response.content == "Mocked OpenAI Reply"
    assert response.model_used == "gpt-4o-mini"

@patch.dict(os.environ, {"OPENROUTER_API_KEY": "fake_key"})
@patch("src.provider_system.openrouter_provider.OpenAI")
def test_openrouter_send_prompt(mock_openai_class, openrouter_provider):
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked OpenRouter Reply"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model_dump.return_value = {"id": "chatcmpl-456"}
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    msg = ProviderMessage(role="user", content="Hello OpenRouter")
    response = openrouter_provider.send_prompt([msg], model="cerebras/llama3.1-70b")
    
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": "Hello OpenRouter"}],
        model="cerebras/llama3.1-70b"
    )
    assert response.content == "Mocked OpenRouter Reply"
    assert response.model_used == "cerebras/llama3.1-70b"
