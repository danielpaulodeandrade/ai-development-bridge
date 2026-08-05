import os
from typing import List, Optional
from openai import OpenAI
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class OllamaProvider(Provider):
    """Implementation of the Ollama Provider using the OpenAI SDK."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._default_model = "llama3.1:8b-instruct-q8_0"

    @property
    def provider_name(self) -> str:
        return "ollama"

    def initialize(self) -> None:
        """Initializes the Ollama client with the Base URL from the environment."""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        # Ollama local doesn't strictly need a real API key, but the OpenAI SDK requires a non-empty string.
        api_key = os.getenv("OLLAMA_API_KEY", "ollama")
        
        self._default_model = os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.1:8b-instruct-q8_0")
        
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to Ollama and returns the standardized response."""
        if not self.client:
            self.initialize()
            
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        target_model = model or self._default_model
        
        completion_params = {
            "messages": ollama_messages,
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
        """Performs a basic check to ensure the Ollama server is reachable."""
        try:
            if not self.client:
                self.initialize()
            # Note: models.list() hits the /v1/models endpoint natively supported by Ollama
            self.client.models.list()
            return True
        except Exception:
            return False
