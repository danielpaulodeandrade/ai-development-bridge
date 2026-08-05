import os
import pytest
from unittest.mock import patch, MagicMock
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse
from src.provider_system.registry import ProviderRegistry
from src.provider_system.fallback_provider import FallbackProvider

class HealthyMockProvider(Provider):
    @property
    def provider_name(self) -> str:
        return "healthy_mock"
    def initialize(self) -> None:
        pass
    def send_prompt(self, messages, model=None, **kwargs) -> ProviderResponse:
        return ProviderResponse(content="Healthy", raw_response={}, model_used="mock")
    def health_check(self) -> bool:
        return True

class FailingMockProvider(Provider):
    @property
    def provider_name(self) -> str:
        return "failing_mock"
    def initialize(self) -> None:
        pass
    def send_prompt(self, messages, model=None, **kwargs) -> ProviderResponse:
        raise ConnectionError("Mock Connection Timeout")
    def health_check(self) -> bool:
        return False

@pytest.fixture(autouse=True)
def setup_registry():
    # Clear registry and register mocks
    ProviderRegistry.clear()
    ProviderRegistry.register(HealthyMockProvider)
    ProviderRegistry.register(FailingMockProvider)
    ProviderRegistry.register(FallbackProvider)
    yield
    ProviderRegistry.clear()

@pytest.fixture
def fallback_provider():
    return FallbackProvider()

def test_fallback_provider_name(fallback_provider):
    assert fallback_provider.provider_name == "fallback"

@patch.dict(os.environ, {"FALLBACK_ORDER": "failing_mock, healthy_mock"})
def test_fallback_routes_to_secondary_on_failure(fallback_provider):
    """Test that if the primary fails, it falls back to the secondary and returns its response."""
    msg = ProviderMessage(role="user", content="Hello")
    
    # 'failing_mock' will throw ConnectionError, so it should hit 'healthy_mock'
    response = fallback_provider.send_prompt([msg])
    
    assert response.content == "Healthy"

@patch.dict(os.environ, {"FALLBACK_ORDER": "failing_mock"})
def test_fallback_exhausts_and_raises(fallback_provider):
    """Test that if all providers fail, it propagates an error."""
    msg = ProviderMessage(role="user", content="Hello")
    
    with pytest.raises(RuntimeError, match="Fallback Manager exhausted all providers. Last error: Mock Connection Timeout"):
        fallback_provider.send_prompt([msg])

@patch.dict(os.environ, {"FALLBACK_ORDER": "failing_mock, healthy_mock"})
def test_fallback_health_check_healthy(fallback_provider):
    """If at least one provider is healthy, the fallback manager is healthy."""
    assert fallback_provider.health_check() is True

@patch.dict(os.environ, {"FALLBACK_ORDER": "failing_mock"})
def test_fallback_health_check_unhealthy(fallback_provider):
    """If all providers are unhealthy, the fallback manager is unhealthy."""
    assert fallback_provider.health_check() is False

@patch.dict(os.environ, {"FALLBACK_ORDER": ""})
def test_fallback_initialization_fails_if_empty(fallback_provider):
    with pytest.raises(ValueError, match="FALLBACK_ORDER is empty or invalid"):
        fallback_provider.initialize()
