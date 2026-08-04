from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class BrowserSession(BaseModel):
    session_id: str
    status: str
    metadata: Dict[str, Any] = {}

class BrowserDriver(ABC):
    """
    Fundação para a comunicação com navegadores e plataformas de IA baseadas em Web.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome do provedor (ex: chatgpt, claude, etc)."""
        pass

    @abstractmethod
    async def start_session(self) -> BrowserSession:
        """Inicia e retorna uma nova sessão de navegação."""
        pass

    @abstractmethod
    async def execute_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """Executa uma ação genérica na página atual."""
        pass

    @abstractmethod
    async def close_session(self, session_id: str) -> None:
        """Encerra a sessão específica."""
        pass
