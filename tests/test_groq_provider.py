import os
import pytest
from unittest.mock import patch, MagicMock
from src.provider_system.base import ProviderMessage
from src.provider_system.registry import ProviderRegistry
from src.provider_system.groq_provider import GroqProvider

@pytest.fixture
def groq_provider():
    """Returns an uninitialized GroqProvider instance."""
    return GroqProvider()

def test_groq_provider_name(groq_provider):
    assert groq_provider.provider_name == "groq"

@patch.dict(os.environ, clear=True)
def test_groq_initialization_fails_without_key(groq_provider):
    """Ensure it raises ValueError if GROQ_API_KEY is not in the environment."""
    groq_provider.client = None
    with pytest.raises(ValueError, match="GROQ_API_KEY environment variable is missing"):
        groq_provider.initialize()

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"})
@patch("src.provider_system.groq_provider.Groq")
def test_groq_initialization_success(mock_groq_class, groq_provider):
    """Ensure it initializes the client successfully when key is present."""
    groq_provider.client = None
    groq_provider.initialize()
    
    mock_groq_class.assert_called_once_with(api_key="fake_key")
    assert groq_provider.client is not None

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"})
@patch("src.provider_system.groq_provider.Groq")
def test_groq_send_prompt(mock_groq_class, groq_provider):
    """Ensure the provider translates messages correctly and returns ProviderResponse."""
    # Setup mock response
    mock_client = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Mocked Groq Reply"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.model_dump.return_value = {"id": "chatcmpl-123", "model": "llama-test"}
    mock_client.chat.completions.create.return_value = mock_response
    
    mock_groq_class.return_value = mock_client
    
    # Ensure client is clear before test
    groq_provider.client = None
    
    # Send a prompt
    msg = ProviderMessage(role="user", content="Hello Groq")
    response = groq_provider.send_prompt([msg], model="llama-test-model")
    
    # Verify the mock was called correctly
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": "Hello Groq"}],
        model="llama-test-model"
    )
    
    # Verify the standard response mapping
    assert response.content == "Mocked Groq Reply"
    assert response.model_used == "llama-test-model"
    assert response.raw_response == {"id": "chatcmpl-123", "model": "llama-test"}

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"})
@patch("src.provider_system.groq_provider.Groq")
def test_groq_health_check_success(mock_groq_class, groq_provider):
    mock_client = MagicMock()
    mock_client.models.list.return_value = {"data": []}
    mock_groq_class.return_value = mock_client
    
    groq_provider.client = None
    assert groq_provider.health_check() is True

@patch.dict(os.environ, {"GROQ_API_KEY": "fake_key"})
@patch("src.provider_system.groq_provider.Groq")
def test_groq_health_check_failure(mock_groq_class, groq_provider):
    mock_client = MagicMock()
    mock_client.models.list.side_effect = Exception("API Error")
    mock_groq_class.return_value = mock_client
    
    groq_provider.client = None
    assert groq_provider.health_check() is False
