import os
from typing import List, Optional
from openai import OpenAI
from src.provider_system.base import Provider, ProviderMessage, ProviderResponse

class NvidiaProvider(Provider):
    """Implementation of the NVidia NIM Provider using the OpenAI SDK."""
    
    def __init__(self):
        self.client: Optional[OpenAI] = None
        self._default_model = "nvidia/llama-3.1-nemotron-70b-instruct"

    @property
    def provider_name(self) -> str:
        return "nvidia"

    def initialize(self) -> None:
        """Initializes the NVidia client with the API key from the environment."""
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY environment variable is missing.")
            
        self._default_model = os.getenv("NVIDIA_DEFAULT_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )

    def send_prompt(self, messages: List[ProviderMessage], model: Optional[str] = None, **kwargs) -> ProviderResponse:
        """Sends the prompt to NVidia API and returns the standardized response."""
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
