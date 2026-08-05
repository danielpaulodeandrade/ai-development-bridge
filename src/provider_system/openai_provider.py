import os
from typing import List, Optional
from openai import OpenAI
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class OpenAIProvider(Provider):
    """Implementation of the OpenAI Provider using the official SDK."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._default_model = "gpt-4o"

    @property
    def provider_name(self) -> str:
        return "openai"

    def initialize(self) -> None:
        """Initializes the OpenAI client with the API key from the environment."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is missing.")
            
        self._default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o")
        self.client = OpenAI(api_key=api_key)

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to the OpenAI API and returns the standardized response."""
        if not self.client:
            self.initialize()
            
        openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        target_model = model or self._default_model
        
        completion_params = {
            "messages": openai_messages,
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
        """Performs a basic check to ensure the OpenAI client is authenticated."""
        try:
            if not self.client:
                self.initialize()
            self.client.models.list()
            return True
        except Exception:
            return False
