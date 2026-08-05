import os
from typing import List, Optional
from openai import OpenAI
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class OpenRouterProvider(Provider):
    """Implementation of the OpenRouter Provider using the OpenAI SDK."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._default_model = "anthropic/claude-3.5-sonnet"

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def initialize(self) -> None:
        """Initializes the OpenRouter client with the API key and Base URL."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is missing.")
            
        self._default_model = os.getenv("OPENROUTER_DEFAULT_MODEL", "anthropic/claude-3.5-sonnet")
        
        # OpenRouter uses the OpenAI API standard, so we just override the base_url
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to OpenRouter and returns the standardized response."""
        if not self.client:
            self.initialize()
            
        router_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        target_model = model or self._default_model
        
        completion_params = {
            "messages": router_messages,
            "model": target_model,
        }
        completion_params.update(kwargs)
        
        response = self.client.chat.completions.create(**completion_params)
        
        content = response.choices[0].message.content
        
        return ProviderResponse(
            content=content,
            raw_response=response.model_dump(),
            model_used=target_model
        )

    def health_check(self) -> bool:
        """Performs a basic check to ensure the OpenRouter client is authenticated."""
        try:
            if not self.client:
                self.initialize()
            # Note: OpenRouter models endpoint works the same way
            self.client.models.list()
            return True
        except Exception:
            return False
