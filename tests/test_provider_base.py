import pytest
from typing import List, Optional
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse
from src.provider_system.registry import ProviderRegistry

class MockProvider(Provider):
    @property
    def provider_name(self) -> str:
        return "mock_llm"
        
    def initialize(self) -> None:
        self.is_initialized = True
        
    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        content = " ".join([m.content for m in messages])
        return ProviderResponse(
            content=f"Mocked: {content}",
            raw_response={"status": "success"},
            model_used=model or "mock-default-model"
        )
        
    def health_check(self) -> bool:
        return getattr(self, "is_initialized", False)


def test_provider_registry_lifecycle():
    # Clear any previous state
    ProviderRegistry.clear()
    
    # Test registration
    ProviderRegistry.register(MockProvider)
    assert "mock_llm" in ProviderRegistry.list_providers()
    
    # Test retrieval and automatic initialization
    provider = ProviderRegistry.get_provider("mock_llm")
    assert isinstance(provider, MockProvider)
    assert provider.health_check() is True  # Should be initialized
    
    # Test singleton behavior
    provider2 = ProviderRegistry.get_provider("mock_llm")
    assert provider is provider2  # Exact same instance
    
    # Test unknown provider
    with pytest.raises(ValueError):
        ProviderRegistry.get_provider("unknown_llm")

def test_provider_message_and_response():
    # Test data models
    msg = ProviderMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
    
    # Test mock interaction
    provider = MockProvider()
    response = provider.send_prompt([msg], model="test-model")
    
    assert response.content == "Mocked: Hello"
    assert response.raw_response == {"status": "success"}
    assert response.model_used == "test-model"
