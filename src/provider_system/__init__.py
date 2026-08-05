"""
Provider System - Init
"""
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse
from src.provider_system.registry import ProviderRegistry

# Import and auto-register providers
from src.provider_system.groq_provider import GroqProvider
from src.provider_system.openai_provider import OpenAIProvider
from src.provider_system.openrouter_provider import OpenRouterProvider

ProviderRegistry.register(GroqProvider)
ProviderRegistry.register(OpenAIProvider)
ProviderRegistry.register(OpenRouterProvider)

__all__ = ["Provider", "ProviderMessage", "ProviderResponse", "ProviderRegistry"]
