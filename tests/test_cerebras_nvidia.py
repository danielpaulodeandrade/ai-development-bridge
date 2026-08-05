import os
import pytest
from unittest.mock import patch, MagicMock
from src.provider_system.base import ProviderMessage
from src.provider_system.cerebras_provider import CerebrasProvider
from src.provider_system.nvidia_provider import NvidiaProvider

@pytest.fixture
def cerebras_provider():
    return CerebrasProvider()

@pytest.fixture
def nvidia_provider():
    return NvidiaProvider()

def test_cerebras_provider_name(cerebras_provider):
    assert cerebras_provider.provider_name == "cerebras"

def test_nvidia_provider_name(nvidia_provider):
    assert nvidia_provider.provider_name == "nvidia"

@patch.dict(os.environ, {"CEREBRAS_API_KEY": "fake_cerebras_key"})
@patch("src.provider_system.cerebras_provider.OpenAI")
def test_cerebras_initialization(mock_openai_class, cerebras_provider):
    cerebras_provider.initialize()
    mock_openai_class.assert_called_once_with(
        base_url="https://api.cerebras.ai/v1",
        api_key="fake_cerebras_key"
    )

@patch.dict(os.environ, {"NVIDIA_API_KEY": "fake_nvidia_key"})
@patch("src.provider_system.nvidia_provider.OpenAI")
def test_nvidia_initialization(mock_openai_class, nvidia_provider):
    nvidia_provider.initialize()
    mock_openai_class.assert_called_once_with(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="fake_nvidia_key"
    )
