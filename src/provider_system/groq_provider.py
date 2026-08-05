import os
from typing import List, Optional
from groq import Groq
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class GroqProvider(Provider):
    """Implementation of the Groq AI Provider using the official SDK."""
    
    def __init__(self):
        self.client: Optional[Groq] = None
        self._default_model = "llama-3.3-70b-versatile"

    @property
    def provider_name(self) -> str:
        return "groq"

    def initialize(self) -> None:
        """Initializes the Groq client with the API key from the environment."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing.")
        
        self._default_model = os.getenv("GROQ_DEFAULT_MODEL", "llama-3.3-70b-versatile")
        self.client = Groq(api_key=api_key)

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to the Groq API and returns the standardized response."""
        if not self.client:
            self.initialize()
            
        # Convert ProviderMessage to Groq expected format
        groq_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        target_model = model or self._default_model
        
        completion_params = {
            "messages": groq_messages,
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
        """Performs a basic check to ensure the Groq client is authenticated."""
        try:
            if not self.client:
                self.initialize()
            # Calling models.list() is a lightweight way to check if the API key is valid
            self.client.models.list()
            return True
        except Exception:
            return False
