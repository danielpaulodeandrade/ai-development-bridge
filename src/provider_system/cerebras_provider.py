import os
from typing import List, Optional
from openai import OpenAI
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class CerebrasProvider(Provider):
    """Implementation of the Cerebras Provider using the OpenAI SDK."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._default_model = "llama3.1-70b"

    @property
    def provider_name(self) -> str:
        return "cerebras"

    def initialize(self) -> None:
        """Initializes the Cerebras client with the API key from the environment."""
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable is missing.")
            
        self._default_model = os.getenv("CEREBRAS_DEFAULT_MODEL", "llama3.1-70b")
        
        self.client = OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=api_key
        )

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to Cerebras API and returns the standardized response."""
        if not self.client:
            self.initialize()
            
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        target_model = model or self._default_model
        
        completion_params = {
            "messages": formatted_messages,
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
        try:
            if not self.client:
                self.initialize()
            self.client.models.list()
            return True
        except Exception:
            return False
