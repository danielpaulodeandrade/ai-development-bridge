import os
import logging
from typing import List, Optional
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse
from src.provider_system.registry import ProviderRegistry

logger = logging.getLogger(__name__)

class FallbackProvider(Provider):
    """
    A resilience manager that attempts to route prompts to a primary provider,
    and falls back to secondary providers seamlessly in case of failure.
    """
    
    def __init__(self):
        self._fallback_order: List[str] = []
        
    @property
    def provider_name(self) -> str:
        return "fallback"

    def initialize(self) -> None:
        """Loads the fallback order from the environment and ensures they are valid."""
        order_str = os.getenv("FALLBACK_ORDER", "groq,openrouter,cerebras,ollama,nvidia,openai")
        self._fallback_order = [p.strip() for p in order_str.split(",") if p.strip()]
        
        if not self._fallback_order:
            raise ValueError("FALLBACK_ORDER is empty or invalid.")

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Attempts to send the prompt using the configured fallback order."""
        if not self._fallback_order:
            self.initialize()
            
        last_exception = None
        
        for provider_name in self._fallback_order:
            try:
                # Get and initialize the provider on the fly
                provider = ProviderRegistry.get_provider(provider_name)
                
                # Attempt to send the prompt
                return provider.send_prompt(messages=messages, model=model, **kwargs)
                
            except Exception as e:
                # Catch any error (timeout, rate limit, auth failure, ValueError from missing keys)
                last_exception = e
                logger.warning(f"Fallback Manager: Provider '{provider_name}' failed with error: {e}. Trying next...")
                continue
                
        # If we exhausted all providers, raise the last exception
        raise RuntimeError(f"Fallback Manager exhausted all providers. Last error: {last_exception}") from last_exception

    def health_check(self) -> bool:
        """
        The fallback manager is healthy if AT LEAST ONE provider in the chain is healthy.
        """
        if not self._fallback_order:
            try:
                self.initialize()
            except Exception:
                return False
                
        for provider_name in self._fallback_order:
            try:
                provider = ProviderRegistry.get_provider(provider_name)
                if provider.health_check():
                    return True
            except Exception:
                continue
                
        return False
