from abc import ABC, abstractmethod
from src.provider_system.models import ProviderRequest, ProviderResponse

class BaseProvider(ABC):
    """
    Interface base obrigatória para todos os provedores de IA 
    (Browser, API, Local, etc).
    """
    
    @abstractmethod
    async def send_request(self, request: ProviderRequest) -> ProviderResponse:
        """
        Envia um request estruturado para o provedor e retorna a resposta de forma assíncrona.
        """
        pass
